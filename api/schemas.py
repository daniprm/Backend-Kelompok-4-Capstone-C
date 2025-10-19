from pydantic import BaseModel, Field
from typing import List, Tuple, Dict

# --- Request Models ---

class RouteRequest(BaseModel):
    latitude: float = Field(..., example=-7.2575, description="Latitude lokasi pengguna")
    longitude: float = Field(..., example=112.7521, description="Longitude lokasi pengguna")
    num_routes: int = Field(3, gt=0, le=10, description="Jumlah rute alternatif yang diinginkan")
    generations: int = Field(1000, gt=10, le=10000, description="Jumlah generasi HGA (Mempengaruhi waktu proses)")
    population_size: int = Field(50, gt=10, le=200, description="Ukuran populasi HGA")
    crossover_rate: float = Field(0.8, ge=0.0, le=1.0)
    mutation_rate: float = Field(0.1, ge=0.0, le=1.0)

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
    statistics: Dict
    visualization_urls: Dict[str, str]