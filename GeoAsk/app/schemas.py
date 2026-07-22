"""Request/response schemas for the primitive endpoints.

Geometry payloads are typed loosely as ``dict`` GeoJSON rather than fully
modelled GeoJSON classes: the primitives validate structure themselves and
full GeoJSON modelling in Pydantic buys little here while making the schemas
hard to read. The scalar parameters (distances, operators, modes) *are* typed
and constrained, because those are what the LLM tool layer gets wrong.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

GeoJSON = dict[str, Any]


class BufferRequest(BaseModel):
    features: GeoJSON = Field(..., description="GeoJSON FeatureCollection to buffer")
    distance_m: float = Field(..., gt=0, description="Buffer radius in metres")


class IsochroneRequest(BaseModel):
    features: GeoJSON = Field(..., description="Origin points")
    minutes: float = Field(..., gt=0, description="Travel-time budget in minutes")
    mode: Literal["walk", "bike", "drive"] = "drive"


class FilterRequest(BaseModel):
    features: GeoJSON
    attribute: str
    op: Literal["==", "!=", ">", ">=", "<", "<="]
    value: Any


class SpatialJoinRequest(BaseModel):
    target: GeoJSON
    join: GeoJSON
    predicate: Literal["intersects", "within", "contains"] = "intersects"
    keep: Literal["matching", "non_matching"] = "matching"


class NearestRequest(BaseModel):
    source: GeoJSON
    destinations: GeoJSON


class DemographicOverlayRequest(BaseModel):
    areas: GeoJSON
    tracts: GeoJSON
    value_field: str
    kind: Literal["extensive", "intensive"] = "extensive"
    out_field: str | None = None


class FeatureCollectionResponse(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[dict[str, Any]]
