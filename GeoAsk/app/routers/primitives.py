"""FastAPI routes — one endpoint per spatial primitive.

Each route is a thin adapter: validate the request (Pydantic), call the pure
primitive, translate a ``ValueError`` from the primitive into a 422 so the
orchestration layer sees a clean, machine-readable rejection instead of a 500.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import spatial
from ..schemas import (
    BufferRequest,
    DemographicOverlayRequest,
    FeatureCollectionResponse,
    FilterRequest,
    IsochroneRequest,
    NearestRequest,
    SpatialJoinRequest,
)

router = APIRouter(prefix="/tools", tags=["primitives"])


def _guard(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/buffer", response_model=FeatureCollectionResponse)
def buffer(req: BufferRequest):
    return _guard(spatial.buffer, req.features, req.distance_m)


@router.post("/isochrone", response_model=FeatureCollectionResponse)
def isochrone(req: IsochroneRequest):
    return _guard(spatial.isochrone, req.features, req.minutes, req.mode)


@router.post("/filter_by_attribute", response_model=FeatureCollectionResponse)
def filter_by_attribute(req: FilterRequest):
    return _guard(spatial.filter_by_attribute, req.features, req.attribute, req.op, req.value)


@router.post("/spatial_join", response_model=FeatureCollectionResponse)
def spatial_join(req: SpatialJoinRequest):
    return _guard(spatial.spatial_join, req.target, req.join, req.predicate, req.keep)


@router.post("/nearest", response_model=FeatureCollectionResponse)
def nearest(req: NearestRequest):
    return _guard(spatial.nearest, req.source, req.destinations)


@router.post("/demographic_overlay", response_model=FeatureCollectionResponse)
def demographic_overlay(req: DemographicOverlayRequest):
    return _guard(
        spatial.demographic_overlay,
        req.areas,
        req.tracts,
        req.value_field,
        req.kind,
        req.out_field,
    )
