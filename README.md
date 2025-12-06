# Archaeological Discovery Explorer — Prototype

This project is a minimal prototype for an archaeological discovery app that uses free Earth observation and elevation data sources (Sentinel, Landsat, USGS DEM/LiDAR, NOAA coastal LiDAR, NASA GEDI, etc.). It demonstrates a GUI to draw an AOI and a backend endpoint that searches for Sentinel products (as an example). Use this as a basis to add additional connectors and processing.

Architecture
- Frontend: Leaflet map with drawing controls to select AOI and request data.
- Backend: FastAPI service that talks to satellite/LiDAR data providers, downloads data to a local cache, and runs preprocessing (raster reprojection, cropping, hillshading).
- Processing: rasterio/GDAL for raster ops; PDAL/laspy for LiDAR; scikit-image and PyTorch/TensorFlow for ML detection.
- Visualization: overlay served tiles or Potree for point clouds.

Important data sources to integrate
- USGS EarthExplorer / The National Map (Landsat, aerial imagery, DEM/LiDAR)
- NOAA Data Access Viewer (coastal LiDAR, aerial)
- NASA Earthdata Search (GEDI, other mission data)
- Copernicus / Sentinel Hub / Open Access Hub (Sentinel-1 & Sentinel-2)
- Sentinel Hub / EO Browser for previews and easy downloads

Prototype features
- Draw AOI in web GUI
- POST AOI to backend to search Sentinel (example)
- Backend returns product metadata and download status

Quick start (local)
1. Copy .env.example to `.env` and fill in credentials:
   - SENTINEL_USER and SENTINEL_PASSWORD (or use token), and other provider credentials when you add connectors.
2. Create a virtualenv and install:
   - `python -m venv venv && source venv/bin/activate`
   - `pip install -r backend/requirements.txt`
3. Run the backend:
   - `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
4. Serve the frontend statically (open `frontend/index.html` in a browser) or use a tiny webserver:
   - `python -m http.server --directory frontend 8080` then open http://localhost:8080

Notes about API credentials and accounts
- NASA Earthdata requires registration — you'll receive a username/password for programmatic downloads (use requests with HTTP basic auth or oauth when required).
- Copernicus Open Access Hub / Sentinel Hub require registration (Sentinel Hub provides APIs and tokens; alternatively, public Sentinel data is available via AWS Open Data).
- USGS has APIs and login flows for some services (register and obtain an API key if needed).
- NOAA Datasets are often open but some APIs require token or request limits.

Processing pipeline ideas (archaeology-focused)
- DEM processing:
  - Create multiple hillshades (at different azimuths), slope and curvature rasters.
  - Calculate Local Relief Model (LRM) and Topographic Position Index (TPI) to reveal subtle features.
  - Use high-pass filters and adaptive contrast to highlight micro-relief.
- LiDAR point clouds:
  - Use PDAL to filter ground points and create high-resolution DEMs, Canopy Height Models, and intensity rasters.
  - Visualize point clouds with Potree (web) or Open3D (desktop).
- Detection:
  - Classical: edge detection, local statistical anomaly detection, PCA on multispectral bands.
  - ML: segmentation (U-Net), anomaly detection, train on labeled archaeological features if available.
- Export: GeoTIFFs, LAS/LAZ, GeoJSON vector candidates, shapefiles.

Scaling & production recommendations
- Use a caching layer (S3 / local cache) for downloaded products.
- Respect provider usage policies and rate limits.
- Use a job queue (Celery, RQ) for long-running downloads and processing.
- Containerize with Docker and orchestrate with Kubernetes for scaling.

Next steps
- Implement additional connectors (USGS, NOAA, NASA) — I included guidance in the code comments.
- Add DEM/LiDAR ingestion examples (PDAL pipelines).
- Add feature-detection modules and a results review UI.

License: MIT
