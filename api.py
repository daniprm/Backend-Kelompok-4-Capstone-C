"""
FastAPI application untuk sistem rekomendasi rute wisata Surabaya
menggunakan Hybrid Genetic Algorithm (HGA)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from contextlib import asynccontextmanager
import json
from datetime import datetime

from algorithms.hga import HybridGeneticAlgorithm
from utils.data_loader import load_destinations_from_csv
from models.route import Route

# Global variables untuk cache
destinations = None

# System initialization
def initialize_system():
    """Load destinations data on startup"""
    global destinations
    if destinations is None:
        print("Loading destinations data...")
        destinations = load_destinations_from_csv("./data/data_wisata_sby.csv")
        print(f"Successfully loaded {len(destinations)} destinations")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_system()
    print("API Server started successfully!")
    yield
    # Shutdown (jika diperlukan cleanup)
    print("API Server shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Tourism Route Recommendation API",
    description="API untuk rekomendasi rute wisata Surabaya menggunakan Hybrid Genetic Algorithm",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware - Allow all origins (sesuaikan dengan kebutuhan production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain frontend Anda di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    population_size: Optional[int] = Field(70, description="Ukuran populasi", ge=10, le=200)
    generations: Optional[int] = Field(5000, description="Jumlah generasi", ge=100, le=20000)
    crossover_rate: Optional[float] = Field(0.8, description="Probabilitas crossover", ge=0.0, le=1.0)
    mutation_rate: Optional[float] = Field(0.1, description="Probabilitas mutasi", ge=0.0, le=1.0)

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
                    "population_size": 70,
                    "generations": 5000,
                    "crossover_rate": 0.8,
                    "mutation_rate": 0.1
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

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Tourism Route Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "recommend": "/generate-routes (POST)"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "destinations_loaded": destinations is not None,
        "total_destinations": len(destinations) if destinations else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/generate-routes", response_model=RouteRecommendationResponse, tags=["Recommendations"])
async def get_route_recommendations(request: RouteRecommendationRequest):
    """
    Mendapatkan rekomendasi rute wisata optimal berdasarkan lokasi user
    
    - **latitude**: Latitude lokasi user (-90 sampai 90)
    - **longitude**: Longitude lokasi user (-180 sampai 180)
    - **num_routes**: Jumlah rute yang diinginkan (1-5, default: 3)
    - **hga_config**: Konfigurasi HGA (opsional)
    """
    try:
        # Validasi destinations sudah dimuat
        if destinations is None:
            raise HTTPException(
                status_code=500, 
                detail="Destinations data not loaded. Please restart the server."
            )
        
        # Extract data dari request
        user_location = (request.latitude, request.longitude)
        num_routes = request.num_routes
        
        # Inisialisasi HGA dengan konfigurasi dari request atau default
        hga_config = request.hga_config or HGAConfig()
        
        hga = HybridGeneticAlgorithm(
            population_size=hga_config.population_size,
            generations=hga_config.generations,
            crossover_rate=hga_config.crossover_rate,
            mutation_rate=hga_config.mutation_rate,
            elitism_count=2,
            tournament_size=5,
            use_2opt=True,
            two_opt_iterations=500
        )
        
        print(f"\nProcessing request for location: {user_location}")
        print(f"HGA Config - Pop: {hga_config.population_size}, Gen: {hga_config.generations}")
        
        # Jalankan HGA
        best_chromosomes = hga.run(
            destinations=destinations,
            start_point=user_location,
            num_solutions=num_routes
        )
        
        # Format hasil
        recommendations = []
        for i, chromosome in enumerate(best_chromosomes):
            route = Route(user_location, chromosome.genes)
            route_info = route.get_route_summary()
            route_info['rank'] = i + 1
            route_info['fitness'] = chromosome.get_fitness()
            recommendations.append(route_info)
        
        # Get statistics
        stats = hga.get_evolution_statistics()
        
        # Response
        response_data = {
            "user_location": {
                "latitude": user_location[0],
                "longitude": user_location[1]
            },
            "hga_config": {
                "population_size": hga_config.population_size,
                "generations": hga_config.generations,
                "crossover_rate": hga_config.crossover_rate,
                "mutation_rate": hga_config.mutation_rate
            },
            "statistics": {
                "total_generations": stats['total_generations'],
                "best_distance_km": stats['best_distance'],
                "initial_fitness": stats['best_fitness_history'][0],
                "final_fitness": stats['best_fitness_history'][-1],
                "improvement_percentage": (
                    (stats['best_fitness_history'][-1] - stats['best_fitness_history'][0]) 
                    / stats['best_fitness_history'][0] * 100
                )
            },
            "routes": recommendations
        }
        
        print(f"Successfully generated {len(recommendations)} routes")
        print(f"Best route distance: {stats['best_distance']:.2f} km\n")
        
        return RouteRecommendationResponse(
            success=True,
            message=f"Successfully generated {len(recommendations)} route recommendations",
            data=response_data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating route recommendations: {str(e)}"
        )

@app.get("/api/destinations", tags=["Destinations"])
async def get_destinations():
    """Get all available destinations"""
    if destinations is None:
        raise HTTPException(
            status_code=500,
            detail="Destinations data not loaded"
        )
    
    destinations_list = []
    for dest in destinations:
        destinations_list.append({
            "nama": dest.nama,
            "kategori": dest.kategori,
            "coordinates": {
                "latitude": dest.latitude,
                "longitude": dest.longitude
            }
        })
    
    return {
        "success": True,
        "total": len(destinations_list),
        "data": destinations_list
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
