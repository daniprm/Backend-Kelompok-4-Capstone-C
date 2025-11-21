import os
import uuid
import json
from fastapi import APIRouter, HTTPException, Request, Query, FastAPI
from visualization.map_plotter import RouteMapPlotter
from visualization.convergence_plotter import ConvergencePlotter
from api.schemas import *
from api.config import OUTPUT_DIR # Ambil path dari config
from utils.database import get_all_wisata, get_wisata_by_id, search_wisata, get_wisata_statistics
from utils.data_loader import load_destinations_from_sqlite
from datetime import datetime
from utils.distance_matrix import *
from utils.distance import *
from algorithms.hga import *
from models.route import *
from contextlib import asynccontextmanager


router = APIRouter()
destinations = None

def initialize_system():
    """Load destinations data on startup"""
    global destinations
    if destinations is None:
        print("Loading destinations data from SQLite...")
        try:
            destinations = load_destinations_from_sqlite()
            print(f"Successfully loaded {len(destinations)} destinations")
        except Exception as e:
            print(f"ERROR loading destinations: {e}")
            raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_system()
    print("API Server started successfully!")
    yield
    # Shutdown (jika diperlukan cleanup)
    print("API Server shutting down...")

@router.get("/api/config/default", tags=["Configuration"])
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

@router.get("/api/osrm/status", tags=["OSRM"])
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
            "cache_size": stats['osrm_runtime_cache_size'],
            "available_profiles": list(profile_description.keys()),
            "description": "OSRM is used to calculate real route distances on roads. Falls back to Haversine (straight-line distance) if OSRM fails."
        }
    }

@router.post("/api/osrm/clear-cache", tags=["OSRM"])
async def clear_cache():
    """Clear OSRM distance cache"""
    clear_osrm_cache()
    return {
        "success": True,
        "message": "OSRM cache cleared successfully"
    }

@router.post("/api/osrm/toggle", tags=["OSRM"])
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

@router.post("/api/osrm/set-profile", tags=["OSRM"])
async def set_profile(profile: str = "driving"):
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
        
@router.get("/api/destinations", tags=["Destinations"])
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
    
@router.get("/", tags=["Root"])
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

@router.get("/wisata", response_model=WisataListResponse)
async def get_wisata_data(
    kategori: str = Query(None, description="Filter berdasarkan kategori (mall, oleh_oleh, non_kuliner, makanan_ringan, makanan_berat, all)"),
    limit: int = Query(None, gt=0, description="Batas jumlah data yang dikembalikan"),
    offset: int = Query(0, ge=0, description="Offset untuk pagination"),
    search: str = Query(None, description="Cari berdasarkan nama atau alamat")
):
    """
    Mengambil data wisata dari database SQLite
    
    Query Parameters:
    - kategori: Filter berdasarkan kategori destinasi
    - limit: Jumlah maksimal data yang dikembalikan
    - offset: Posisi awal data untuk pagination
    - search: Kata kunci pencarian untuk nama atau alamat
    """
    
    try:
        # Jika ada pencarian, gunakan search_wisata
        if search:
            all_data = search_wisata(search, limit)
            total = len(all_data)
        else:
            # Ambil data dari database dengan filtering dan pagination
            all_data, total = get_all_wisata(kategori=kategori, limit=limit, offset=offset)
        
        if not all_data:
            return WisataListResponse(
                message="Data wisata tidak ditemukan",
                total=0,
                data=[]
            )
        
        # Convert ke Pydantic models
        wisata_list = [WisataDestination(**item) for item in all_data]
        
        return WisataListResponse(
            message="Data wisata berhasil diambil",
            total=total,
            data=wisata_list
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mengambil data: {str(e)}")

@router.get("/wisata/{restaurant_id}", response_model=WisataDestination)
async def get_wisata_by_id_endpoint(restaurant_id: int):
    """
    Mengambil data wisata berdasarkan restaurant_id dari database SQLite
    
    Path Parameters:
    - restaurant_id: ID unik dari destinasi wisata
    """
    
    try:
        # Ambil data dari database
        wisata_data = get_wisata_by_id(restaurant_id)
        
        if not wisata_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Destinasi wisata dengan ID {restaurant_id} tidak ditemukan"
            )
        
        return WisataDestination(**wisata_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mengambil data: {str(e)}")

@router.get("/wisata/stats/overview", response_model=WisataStatsResponse)
async def get_wisata_stats():
    """
    Mengambil statistik data wisata
    
    Returns:
    - Total jumlah destinasi
    - Jumlah destinasi per kategori
    """
    
    try:
        stats = get_wisata_statistics()
        
        return WisataStatsResponse(
            message="Statistik data wisata berhasil diambil",
            total_destinations=stats['total_destinations'],
            kategori_count=stats['kategori_count']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mengambil statistik: {str(e)}")

@router.post("/generate-routes", response_model=RouteRecommendationResponse, tags=["Recommendations"])
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
            elitism_count=hga_config.elitism_count,
            tournament_size=hga_config.tournament_size,
            use_2opt=hga_config.use_2opt,
            two_opt_iterations=hga_config.two_opt_iterations
        )
        
        print(f"\nProcessing request for location: {user_location}")
        print(f"HGA Config - Pop: {hga_config.population_size}, Gen: {hga_config.generations}, "
              f"2-Opt: {hga_config.use_2opt} ({hga_config.two_opt_iterations} iter)")
        
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
                "mutation_rate": hga_config.mutation_rate,
                "elitism_count": hga_config.elitism_count,
                "tournament_size": hga_config.tournament_size,
                "use_2opt": hga_config.use_2opt,
                "two_opt_iterations": hga_config.two_opt_iterations
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
@router.get("/health", tags=["Health"])
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