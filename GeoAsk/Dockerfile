FROM python:3.11-slim

# GEOS/PROJ come in via the shapely/pyproj wheels, so no system GDAL is needed
# for the primitives layer. geopandas in the data pipeline pulls its own wheels.
WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
