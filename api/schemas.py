from pydantic import BaseModel, Field
from typing import List, Tuple, Dict

# --- Request Models ---

class RouteRequest(BaseModel):
    latitude: float = Field(..., example=-7.2575, description="Latitude lokasi pengguna")
    longitude: float = Field(..., example=112.7521, description="Longitude lokasi pengguna")

# --- Response Models ---

class DestinationDetail(BaseModel):
    order: int
    nama: str
    kategori: List[str]
    coordinates: Tuple[float, float]

class RouteResponse(BaseModel):
    rank: int
    start_point: Tuple[float, float]
    total_destinations: int
    total_distance_km: float
    destinations: List[DestinationDetail]
    is_valid_order: bool

class RecommendationResponse(BaseModel):
    message: str
    user_location: Tuple[float, float]
    recommendations: List[RouteResponse]