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
import time
from datetime import datetime

from algorithms.hga import HybridGeneticAlgorithm
from utils.data_loader import load_destinations_from_csv
from utils.distance import get_osrm_cache_stats, clear_osrm_cache, set_use_osrm, set_osrm_profile, recalculate_route_with_osrm
from models.route import Route

# Default HGA Configuration (sesuai dengan Main.py)
DEFAULT_HGA_CONFIG = {
    "population_size": 100,
    "generations": 500,
    "crossover_rate": 0.9,
    "mutation_rate": 0.2,
    "elitism_count": 10,
    "tournament_size": 8,
    "use_2opt": True,
    "two_opt_iterations": 500
}

# Global variables untuk cache
destinations = None

# System initialization
def initialize_system():
    """Load destinations data on startup"""
    global destinations
    if destinations is None:
        print("Loading destinations data...")
        destinations = load_destinations_from_csv("./data/data_wisata.jsonl")
        print(f"Successfully loaded {len(destinations)} destinations")

def generate_google_maps_url(start_point, destinations_list):
    """
    Generate Google Maps URL untuk navigasi rute
    
    Args:
        start_point: Tuple (latitude, longitude) titik awal
        destinations_list: List of Destination objects
    
    Returns:
        String URL Google Maps untuk navigasi
    
    Format URL: https://www.google.com/maps/dir/start/dest1/dest2/.../destN
    """
    base_url = "https://www.google.com/maps/dir"
    
    # Build waypoints list
    waypoints = []
    
    # Add start point
    waypoints.append(f"'{start_point[0]},{start_point[1]}'")
    
    # Add all destinations
    for dest in destinations_list:
        waypoints.append(f"{dest.latitude},+{dest.longitude}")
    
    # Join waypoints with /
    waypoints_str = "/".join(waypoints)
    
    # Add travel mode parameter (9 = motorcycle/driving)
    # Reference: https://developers.google.com/maps/documentation/urls/get-started
    url = f"{base_url}/{waypoints_str}?entry=ttu&travelmode=two-wheeler"
    
    return url

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
    place_id: Optional[int] = None
    nama_destinasi: str
    kategori: List[str]
    latitude: float
    longitude: float
    alamat: Optional[str] = None
    image_url: Optional[str] = None
    deskripsi: Optional[str] = None

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
        "description": "API untuk rekomendasi rute wisata Surabaya menggunakan Hybrid Genetic Algorithm",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "recommend": "/generate-routes (POST)",
            "destinations": "/api/destinations (GET)",
            "default_config": "/api/config/default (GET)",
            "osrm_status": "/api/osrm/status (GET)"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    osrm_stats = get_osrm_cache_stats()
    return {
        "status": "healthy",
        "destinations_loaded": destinations is not None,
        "total_destinations": len(destinations) if destinations else 0,
        "osrm_enabled": osrm_stats['osrm_enabled'],
        "osrm_cache_size": osrm_stats['cache_size'],
        "timestamp": datetime.now().isoformat()
    }

# Konstanta untuk validasi rute
MAX_ROUTE_DISTANCE_KM = 25.0  # Maksimal jarak rute yang valid
MAX_HGA_RETRY_ATTEMPTS = 10   # Maksimal percobaan ulang HGA
ROUTE_SEARCH_TIMEOUT_SECONDS = 60  # Timeout untuk pencarian rute (detik)

@app.post("/generate-routes", response_model=RouteRecommendationResponse, tags=["Recommendations"])
async def get_route_recommendations(request: RouteRecommendationRequest):
    """
    Mendapatkan rekomendasi rute wisata optimal berdasarkan lokasi user
    
    - **latitude**: Latitude lokasi user (-90 sampai 90)
    - **longitude**: Longitude lokasi user (-180 sampai 180)
    - **num_routes**: Jumlah rute yang diinginkan (1-5, default: 3)
    - **hga_config**: Konfigurasi HGA (opsional)
    
    Mekanisme validasi:
    - Setelah rute dihasilkan, dilakukan pengecekan ulang dengan OSRM
    - Jika jarak > 25 km, rute ditolak dan HGA dijalankan ulang
    - Proses berlanjut hingga mendapatkan sejumlah rute yang diminta
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
        
        print(f"\nProcessing request for location: {user_location}")
        print(f"HGA Config - Pop: {hga_config.population_size}, Gen: {hga_config.generations}, "
              f"2-Opt: {hga_config.use_2opt} ({hga_config.two_opt_iterations} iter)")
        print(f"Target: {num_routes} routes with max distance {MAX_ROUTE_DISTANCE_KM} km")
        
        # List untuk menyimpan rute yang valid
        valid_routes = []
        # Set untuk menyimpan route signature (untuk menghindari duplikat)
        seen_route_signatures = set()
        # Counter untuk retry attempts
        total_attempts = 0
        # Statistik untuk response
        all_stats = []
        rejected_routes_count = 0
        # Track waktu mulai untuk timeout
        start_time = time.time()
        timeout_reached = False
        
        # Loop hingga mendapatkan jumlah rute yang diminta atau mencapai batas retry atau timeout
        while len(valid_routes) < num_routes and total_attempts < MAX_HGA_RETRY_ATTEMPTS:
            # Check timeout
            elapsed_time = time.time() - start_time
            if elapsed_time >= ROUTE_SEARCH_TIMEOUT_SECONDS:
                timeout_reached = True
                print(f"\n⏱ Timeout reached: {elapsed_time:.2f}s >= {ROUTE_SEARCH_TIMEOUT_SECONDS}s")
                break
            total_attempts += 1
            print(f"\n--- HGA Attempt {total_attempts} (Valid routes: {len(valid_routes)}/{num_routes}) ---")
            
            # Inisialisasi HGA baru untuk setiap attempt
            hga = HybridGeneticAlgorithm(
                population_size=hga_config.population_size,
                generations=hga_config.generations,
                crossover_rate=hga_config.crossover_rate,
                mutation_rate=hga_config.mutation_rate,
                elitism_count=hga_config.elitism_count,
                tournament_size=hga_config.tournament_size,
                use_2opt=hga_config.use_2opt,
                two_opt_iterations=hga_config.two_opt_iterations
            )
            
            # Jalankan HGA - minta lebih banyak solusi untuk meningkatkan peluang mendapat rute valid
            candidates_needed = num_routes - len(valid_routes)
            solutions_to_request = min(candidates_needed + 2, 5)  # Minta sedikit lebih banyak
            
            best_chromosomes = hga.run(
                destinations=destinations,
                start_point=user_location,
                num_solutions=solutions_to_request
            )
            
            # Simpan statistik
            stats = hga.get_evolution_statistics()
            all_stats.append(stats)
            
            # Proses setiap chromosome hasil HGA
            for chromosome in best_chromosomes:
                if len(valid_routes) >= num_routes:
                    break
                
                # Buat route signature untuk cek duplikat (berdasarkan urutan place_id)
                route_signature = tuple(dest.place_id for dest in chromosome.genes)
                if route_signature in seen_route_signatures:
                    print(f"  Skipping duplicate route")
                    continue
                
                # Rekalkulasi dengan OSRM untuk mendapatkan jarak real
                osrm_data = recalculate_route_with_osrm(user_location, chromosome.genes)
                
                if osrm_data['success']:
                    osrm_distance = osrm_data['total_distance_km']
                    
                    # Validasi jarak <= 25 km
                    if osrm_distance <= MAX_ROUTE_DISTANCE_KM:
                        print(f"  ✓ Valid route found: {osrm_distance:.2f} km")
                        
                        # Tandai route sebagai sudah dilihat
                        seen_route_signatures.add(route_signature)
                        
                        # Buat route info
                        route = Route(user_location, chromosome.genes)
                        route_info = route.get_route_summary()
                        route_info['fitness'] = chromosome.get_fitness()
                        
                        # Generate Google Maps URL untuk navigasi
                        google_maps_url = generate_google_maps_url(user_location, chromosome.genes)
                        route_info['google_maps_url'] = google_maps_url
                        
                        # Update dengan data OSRM yang lebih akurat
                        route_info['total_distance_km'] = osrm_data['total_distance_km']
                        route_info['total_travel_time_minutes'] = osrm_data['total_duration_minutes']
                        route_info['total_travel_time_hours'] = osrm_data['total_duration_hours']
                        route_info['osrm_recalculated'] = True
                        route_info['osrm_route_geometry'] = osrm_data.get('geometry')
                        
                        # Update constraint info dengan data OSRM
                        if 'constraint_info' in route_info:
                            from utils.penalty import calculate_distance_penalty, calculate_time_penalty, calculate_total_penalty
                            
                            distance_km = osrm_data['total_distance_km']
                            time_minutes = osrm_data['total_duration_minutes']
                            distance_violated = distance_km > 20.0
                            time_violated = time_minutes > 300.0
                            
                            route_info['constraint_info']['distance']['value'] = round(distance_km, 2)
                            route_info['constraint_info']['distance']['violated'] = distance_violated
                            route_info['constraint_info']['distance']['excess'] = round(max(0, distance_km - 20.0), 2)
                            route_info['constraint_info']['distance']['penalty'] = round(calculate_distance_penalty(distance_km), 6)
                            
                            route_info['constraint_info']['time']['value_minutes'] = round(time_minutes, 2)
                            route_info['constraint_info']['time']['value_hours'] = round(time_minutes / 60, 2)
                            route_info['constraint_info']['time']['violated'] = time_violated
                            route_info['constraint_info']['time']['excess_minutes'] = round(max(0, time_minutes - 300.0), 2)
                            route_info['constraint_info']['time']['penalty'] = round(calculate_time_penalty(time_minutes), 6)
                            
                            route_info['constraint_info']['total_penalty'] = round(calculate_total_penalty(distance_km, time_minutes), 6)
                            route_info['constraint_info']['is_feasible'] = not distance_violated and not time_violated
                        
                        valid_routes.append(route_info)
                    else:
                        print(f"  ✗ Route rejected: {osrm_distance:.2f} km > {MAX_ROUTE_DISTANCE_KM} km limit")
                        rejected_routes_count += 1
                else:
                    # Jika OSRM gagal, tetap terima rute tapi tandai
                    print(f"  ⚠ OSRM failed, accepting route with estimated distance")
                    seen_route_signatures.add(route_signature)
                    
                    route = Route(user_location, chromosome.genes)
                    route_info = route.get_route_summary()
                    route_info['fitness'] = chromosome.get_fitness()
                    
                    google_maps_url = generate_google_maps_url(user_location, chromosome.genes)
                    route_info['google_maps_url'] = google_maps_url
                    route_info['osrm_recalculated'] = False
                    route_info['osrm_error'] = osrm_data.get('error', 'Unknown error')
                    
                    valid_routes.append(route_info)
        
        # Cek apakah berhasil mendapatkan cukup rute
        elapsed_time = time.time() - start_time
        
        if len(valid_routes) == 0:
            if timeout_reached:
                raise HTTPException(
                    status_code=408,  # Request Timeout
                    detail=f"Timeout: Failed to find any valid routes within {MAX_ROUTE_DISTANCE_KM} km after {elapsed_time:.2f} seconds (timeout: {ROUTE_SEARCH_TIMEOUT_SECONDS}s)"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to find any valid routes within {MAX_ROUTE_DISTANCE_KM} km after {total_attempts} attempts"
                )
        
        recommendations = valid_routes
        
        # Sorting routes berdasarkan jarak OSRM (terpendek ke terpanjang)
        recommendations.sort(key=lambda x: x.get('total_distance_km', float('inf')))
        
        # Update rank setelah sorting
        for i, route in enumerate(recommendations):
            route['rank'] = i + 1
        
        # Aggregate statistics dari semua HGA runs
        final_stats = all_stats[-1] if all_stats else None
        
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
                "mutation_rate": hga_config.mutation_rate,
                "elitism_count": hga_config.elitism_count,
                "tournament_size": hga_config.tournament_size,
                "use_2opt": hga_config.use_2opt,
                "two_opt_iterations": hga_config.two_opt_iterations
            },
            "route_validation": {
                "max_distance_km": MAX_ROUTE_DISTANCE_KM,
                "total_hga_attempts": total_attempts,
                "rejected_routes_count": rejected_routes_count,
                "valid_routes_found": len(recommendations),
                "search_time_seconds": round(elapsed_time, 2),
                "timeout_seconds": ROUTE_SEARCH_TIMEOUT_SECONDS,
                "timeout_reached": timeout_reached
            },
            "statistics": {
                "total_generations": final_stats['total_generations'] if final_stats else 0,
                "best_distance_km": final_stats['best_distance'] if final_stats else 0,
                "initial_fitness": final_stats['best_fitness_history'][0] if final_stats else 0,
                "final_fitness": final_stats['best_fitness_history'][-1] if final_stats else 0,
                "improvement_percentage": (
                    (final_stats['best_fitness_history'][-1] - final_stats['best_fitness_history'][0]) 
                    / final_stats['best_fitness_history'][0] * 100
                ) if final_stats and final_stats['best_fitness_history'][0] != 0 else 0
            },
            "routes": recommendations
        }
        
        print(f"\n=== Route Generation Summary ===")
        print(f"Successfully generated {len(recommendations)} valid routes")
        print(f"Total HGA attempts: {total_attempts}")
        print(f"Search time: {elapsed_time:.2f}s / {ROUTE_SEARCH_TIMEOUT_SECONDS}s")
        print(f"Rejected routes (>{MAX_ROUTE_DISTANCE_KM} km): {rejected_routes_count}")
        if recommendations:
            print(f"Best route distance: {recommendations[0].get('total_distance_km', 'N/A'):.2f} km\n")
        
        # Tentukan message berdasarkan apakah timeout tercapai
        if timeout_reached and len(recommendations) < num_routes:
            message = f"Timeout reached. Generated {len(recommendations)}/{num_routes} route recommendations in {elapsed_time:.2f}s"
        else:
            message = f"Successfully generated {len(recommendations)} route recommendations"
        
        return RouteRecommendationResponse(
            success=True,
            message=message,
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
            "place_id": dest.place_id,
            "nama_destinasi": dest.nama,
            "kategori": dest.kategori,
            "latitude": dest.latitude,
            "longitude": dest.longitude,
            "alamat": dest.alamat,
            "image_url": dest.image_url,
            "deskripsi": dest.deskripsi
        })
    
    return {
        "success": True,
        "total": len(destinations_list),
        "data": destinations_list
    }

@app.get("/api/config/default", tags=["Configuration"])
async def get_default_config():
    """Get default HGA configuration (sesuai dengan Main.py)"""
    return {
        "success": True,
        "data": {
            "hga_config": DEFAULT_HGA_CONFIG,
            "description": "Default configuration used in Main.py",
            "note": "You can override these values in your request to /generate-routes"
        }
    }

@app.get("/api/osrm/status", tags=["OSRM"])
async def get_osrm_status():
    """Get OSRM status and cache statistics"""
    stats = get_osrm_cache_stats()
    
    profile_description = {
        'driving': 'Motor/Mobil (paling cocok untuk motor di Indonesia)',
        'bike': 'Sepeda',
        'foot': 'Jalan kaki'
    }
    
    return {
        "success": True,
        "data": {
            "osrm_enabled": stats['osrm_enabled'],
            "osrm_base_url": stats['osrm_base_url'],
            "osrm_profile": stats['osrm_profile'],
            "profile_description": profile_description.get(stats['osrm_profile'], 'Unknown'),
            "cache_size": stats['cache_size'],
            "available_profiles": list(profile_description.keys()),
            "description": "OSRM is used to calculate real route distances on roads. Falls back to Haversine (straight-line distance) if OSRM fails."
        }
    }

@app.post("/api/osrm/clear-cache", tags=["OSRM"])
async def clear_cache():
    """Clear OSRM distance cache"""
    clear_osrm_cache()
    return {
        "success": True,
        "message": "OSRM cache cleared successfully"
    }

@app.post("/api/osrm/toggle", tags=["OSRM"])
async def toggle_osrm(enable: bool = True):
    """
    Enable or disable OSRM usage
    
    - **enable**: True to use OSRM, False to use Haversine only
    """
    set_use_osrm(enable)
    status = "enabled" if enable else "disabled"
    return {
        "success": True,
        "message": f"OSRM has been {status}",
        "osrm_enabled": enable
    }

@app.post("/api/osrm/set-profile", tags=["OSRM"])
async def set_profile(profile: str = "bike"):
    """
    Set OSRM transportation profile
    
    - **profile**: Transportation mode
      - 'driving': Motor/Mobil (default, paling cocok untuk motor)
      - 'bike': Sepeda
      - 'foot': Jalan kaki
    
    Note: Public OSRM server tidak memiliki profil 'motorcycle' terpisah.
    Gunakan 'driving' untuk motor di Indonesia.
    """
    try:
        set_osrm_profile(profile)
        
        profile_description = {
            'driving': 'Motor/Mobil',
            'bike': 'Sepeda',
            'foot': 'Jalan kaki'
        }
        
        return {
            "success": True,
            "message": f"OSRM profile changed to '{profile}'",
            "profile": profile,
            "description": profile_description.get(profile, 'Unknown'),
            "note": "Cache has been cleared due to profile change"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
