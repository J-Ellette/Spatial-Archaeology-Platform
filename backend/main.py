from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shapely.geometry import shape, mapping
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Example: Sentinel connector using sentinelsat
# pip install sentinelsat
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

app = FastAPI(title="Archaeological Discovery Backend (prototype)")

SENTINEL_USER = os.getenv("SENTINEL_USER", "")
SENTINEL_PASSWORD = os.getenv("SENTINEL_PASSWORD", "")
SENTINEL_API_URL = os.getenv("SENTINEL_API_URL", "https://scihub.copernicus.eu/dhus")

if not SENTINEL_USER or not SENTINEL_PASSWORD:
    # For prototyping we allow empty credentials (won't download), but warn in logs.
    print("WARNING: SENTINEL_USER/SENTINEL_PASSWORD not set. Sentinel searches may be limited.")


class AOIRequest(BaseModel):
    geojson: Dict[str, Any]
    start_date: Optional[str] = None  # YYYY-MM-DD
    end_date: Optional[str] = None    # YYYY-MM-DD
    max_results: Optional[int] = 10


@app.post("/search/sentinel")
def search_sentinel(req: AOIRequest):
    """
    Search Sentinel products overlapping the provided AOI GeoJSON polygon.
    Returns product metadata (id, title, date, footprint).
    Requires SENTINEL_USER and SENTINEL_PASSWORD for full access/download.
    """
    # Validate geometry
    try:
        geom = req.geojson
        # Convert geojson to WKT for sentinelsat
        wkt = geojson_to_wkt(geom)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid geojson: {e}")

    # Build query kwargs
    query_kwargs = {
        "platformname": "Sentinel-2",
        "area": wkt,
        "limit": req.max_results or 10,
        "cloudcoverpercentage": (0, 80),
    }
    if req.start_date:
        try:
            datetime.fromisoformat(req.start_date)
            query_kwargs["date"] = (req.start_date, req.end_date or datetime.utcnow().date().isoformat())
        except Exception:
            raise HTTPException(status_code=400, detail="start_date/end_date must be YYYY-MM-DD")

    api = SentinelAPI(SENTINEL_USER, SENTINEL_PASSWORD, SENTINEL_API_URL)
    try:
        products = api.query(**query_kwargs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentinel API error: {e}")

    results = []
    for prod_id, props in products.items():
        results.append({
            "id": prod_id,
            "title": props.get("title"),
            "size": props.get("size"),
            "beginposition": props.get("beginposition").isoformat() if props.get("beginposition") else None,
            "endposition": props.get("endposition").isoformat() if props.get("endposition") else None,
            "cloudcoverpercentage": props.get("cloudcoverpercentage"),
            "footprint": props.get("footprint"),
            "download_url": None  # we can populate if credentials & download is requested
        })

    return {"count": len(results), "products": results}


# Additional endpoints to implement (placeholders)
@app.post("/download/sentinel/{product_id}")
def download_sentinel(product_id: str):
    """
    Download a Sentinel product by id into the backend cache and return a path or URL.
    Implemented as TODO. Use SentinelAPI.download() or download_all().
    """
    raise HTTPException(status_code=501, detail="Download endpoint not implemented in prototype. See README for guidance.")


# Add similar endpoints for USGS, NOAA, NASA, and The National Map
# Typical connectors:
# - USGS: use USGS APIs or `landsatxplore` for Landsat searches, or USGS bulk download APIs for Landsat/ASTER
# - NOAA: the Digital Coast APIs or data.gov endpoints for coastal LiDAR
# - NASA: Earthdata requires credentials and token-based downloads for GEDI
# - The National Map: direct HTTP downloads for DEM/LiDAR tiles
