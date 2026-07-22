"""Geometry helpers shared by every spatial primitive.

The primitives all speak GeoJSON (WGS84 / EPSG:4326) at their edges because that
is what the frontend and the LLM tool layer exchange. But distance, area and
buffer math is wrong in degrees, so any metric operation is done in a local
azimuthal-equidistant projection centred on the working data. Centre-based AEQD
keeps distances near the centre accurate to well within a percent over a metro
sized area, which is the scale GeoAsk operates at.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from pyproj import CRS, Transformer
from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform as shapely_transform

WGS84 = CRS.from_epsg(4326)

Projector = Callable[[BaseGeometry], BaseGeometry]


def _local_metric_crs(lon: float, lat: float) -> CRS:
    """A metre-based CRS centred on (lon, lat)."""
    return CRS.from_proj4(
        f"+proj=aeqd +lat_0={lat} +lon_0={lon} "
        "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
    )


def make_projectors(lon: float, lat: float) -> tuple[Projector, Projector]:
    """Return (to_metric, to_wgs84) geometry transformers centred on a point."""
    metric = _local_metric_crs(lon, lat)
    fwd = Transformer.from_crs(WGS84, metric, always_xy=True).transform
    inv = Transformer.from_crs(metric, WGS84, always_xy=True).transform
    return (
        lambda geom: shapely_transform(fwd, geom),
        lambda geom: shapely_transform(inv, geom),
    )


def features_of(fc: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the feature list from a FeatureCollection (or a single Feature)."""
    if fc.get("type") == "FeatureCollection":
        return list(fc.get("features", []))
    if fc.get("type") == "Feature":
        return [fc]
    raise ValueError("expected a GeoJSON Feature or FeatureCollection")


def geometries_of(fc: dict[str, Any]) -> list[BaseGeometry]:
    return [shape(f["geometry"]) for f in features_of(fc) if f.get("geometry")]


def centroid_lonlat(fc: dict[str, Any]) -> tuple[float, float]:
    """Centroid (lon, lat) of every geometry in the collection, for centring the
    metric projection. Raises if the collection has no geometry."""
    geoms = geometries_of(fc)
    if not geoms:
        raise ValueError("collection has no geometry to project")
    xs = [g.centroid.x for g in geoms]
    ys = [g.centroid.y for g in geoms]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def feature(geom: BaseGeometry, properties: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "type": "Feature",
        "geometry": mapping(geom),
        "properties": dict(properties or {}),
    }


def feature_collection(features: Iterable[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "FeatureCollection", "features": list(features)}
