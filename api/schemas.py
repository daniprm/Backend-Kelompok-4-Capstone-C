from pydantic import BaseModel, Field
from typing import List, Tuple, Dict, Optional

class WisataDestination(BaseModel):
    restaurant_id: int
    nama_destinasi: str
    kategori: str
    latitude: str
    longitude: str
    alamat: Optional[str] = None
    image_url: Optional[str] = None
    deskripsi: Optional[str] = None

class WisataListResponse(BaseModel):
    message: str
    total: int
    data: List[WisataDestination]

class WisataStatsResponse(BaseModel):
    message: str
    total_destinations: int
    kategori_count: Dict[str, int]

DEFAULT_HGA_CONFIG = {
    "population_size": 150,
    "generations": 100,
    "crossover_rate": 0.8,
    "mutation_rate": 0.05,
    "elitism_count": 2,
    "tournament_size": 8,
    "use_2opt": True,
    "two_opt_iterations": 100
}

# Pydantic Models untuk Request/Response
class LocationRequest(BaseModel):
    latitude: float = Field(..., description="Latitude lokasi user", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude lokasi user", ge=-180, le=180)
    num_routes: Optional[int] = Field(3, description="Jumlah rute yang diinginkan", ge=1, le=5)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": -7.2575,
                "longitude": 112.7521,
                "num_routes": 3
            }
        }
    }

class HGAConfig(BaseModel):
    population_size: Optional[int] = Field(
        DEFAULT_HGA_CONFIG["population_size"], 
        description="Ukuran populasi", 
        ge=10, 
        le=200
    )
    generations: Optional[int] = Field(
        DEFAULT_HGA_CONFIG["generations"], 
        description="Jumlah generasi", 
        ge=100, 
        le=20000
    )
    crossover_rate: Optional[float] = Field(
        DEFAULT_HGA_CONFIG["crossover_rate"], 
        description="Probabilitas crossover", 
        ge=0.0, 
        le=1.0
    )
    mutation_rate: Optional[float] = Field(
        DEFAULT_HGA_CONFIG["mutation_rate"], 
        description="Probabilitas mutasi", 
        ge=0.0, 
        le=1.0
    )
    elitism_count: Optional[int] = Field(
        DEFAULT_HGA_CONFIG["elitism_count"], 
        description="Jumlah solusi terbaik yang dipertahankan", 
        ge=1, 
        le=10
    )
    tournament_size: Optional[int] = Field(
        DEFAULT_HGA_CONFIG["tournament_size"], 
        description="Ukuran tournament selection", 
        ge=2, 
        le=20
    )
    use_2opt: Optional[bool] = Field(
        DEFAULT_HGA_CONFIG["use_2opt"], 
        description="Menggunakan 2-Opt local search optimization"
    )
    two_opt_iterations: Optional[int] = Field(
        DEFAULT_HGA_CONFIG["two_opt_iterations"], 
        description="Jumlah iterasi 2-Opt", 
        ge=10, 
        le=2000
    )

class RouteRecommendationRequest(BaseModel):
    latitude: float = Field(..., description="Latitude lokasi user", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude lokasi user", ge=-180, le=180)
    num_routes: Optional[int] = Field(3, description="Jumlah rute yang diinginkan", ge=1, le=5)
    hga_config: Optional[HGAConfig] = Field(None, description="Konfigurasi HGA (opsional)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": -7.2575,
                "longitude": 112.7521,
                "num_routes": 3,
                "hga_config": {
                    "population_size": DEFAULT_HGA_CONFIG["population_size"],
                    "generations": DEFAULT_HGA_CONFIG["generations"],
                    "crossover_rate": DEFAULT_HGA_CONFIG["crossover_rate"],
                    "mutation_rate": DEFAULT_HGA_CONFIG["mutation_rate"],
                    "elitism_count": DEFAULT_HGA_CONFIG["elitism_count"],
                    "tournament_size": DEFAULT_HGA_CONFIG["tournament_size"],
                    "use_2opt": DEFAULT_HGA_CONFIG["use_2opt"],
                    "two_opt_iterations": DEFAULT_HGA_CONFIG["two_opt_iterations"]
                }
            }
        }
    }

class DestinationInfo(BaseModel):
    order: int
    nama: str
    kategori: List[str]
    coordinates: List[float]

class RouteInfo(BaseModel):
    rank: int
    total_distance_km: float
    is_valid_order: bool
    destinations: List[DestinationInfo]

class RouteRecommendationResponse(BaseModel):
    success: bool
    message: str
    data: dict
    timestamp: str
