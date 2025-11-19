import os
import uuid
import json
from fastapi import APIRouter, HTTPException, Request, Query
from system import TourismRouteRecommendationSystem
from visualization.map_plotter import RouteMapPlotter
from visualization.convergence_plotter import ConvergencePlotter
from api.schemas import RouteRequest, RecommendationResponse, WisataListResponse, WisataDestination, WisataStatsResponse
from api.config import OUTPUT_DIR # Ambil path dari config
from utils.database import get_all_wisata, get_wisata_by_id, search_wisata, get_wisata_statistics
from datetime import datetime

router = APIRouter()

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

@router.post("/generate-routes", response_model=RecommendationResponse)
async def generate_routes(request_data: RouteRequest, http_request: Request):
    """
    Menghasilkan rekomendasi rute wisata berdasarkan lokasi pengguna dan parameter HGA.
    """
    
    # 1. Dapatkan sistem
    system: TourismRouteRecommendationSystem = http_request.app.state.recommendation_system
    if not system:
        raise HTTPException(status_code=503, detail="Sistem belum siap.")
    
    # 2. Inisialisasi HGA
    try:
        system.initialize_hga(
            population_size=request_data.population_size,
            generations=request_data.generations,
            crossover_rate=request_data.crossover_rate,
            mutation_rate=request_data.mutation_rate
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    user_location = (request_data.latitude, request_data.longitude)
    
    # 3. Jalankan HGA
    print(f"Menjalankan HGA untuk user di {user_location}...")
    try:
        recommendations = system.get_route_recommendations(
            user_location=user_location,
            num_routes=request_data.num_routes
        )
    except Exception as e:
        print(f"Error saat menjalankan HGA: {e}")
        raise HTTPException(status_code=500, detail=f"Terjadi error saat kalkulasi: {e}")

    print("HGA selesai.")
    
    # 4. Dapatkan statistik
    # stats_raw berisi 'best_solution' yang tidak serializable
    stats_raw = system.hga.get_evolution_statistics()
    
    # 5. Buat visualisasi
    run_id = str(uuid.uuid4())[:8]
    base_url = str(http_request.base_url)
    vis_urls = {}
    
    map_plotter = RouteMapPlotter(center_location=user_location, use_real_routes=True)
    
    # --- 5a. Peta Rute Terbaik ---
    if recommendations and system.hga.best_solution:
        try:
            print("Membuat peta rute terbaik...")
            best_route_genes = system.hga.best_solution.genes
            map_filename = f"best_route_{datetime.now().isoformat()}.html"
            map_filepath = os.path.join(OUTPUT_DIR, map_filename)
            best_map = map_plotter.create_route_map(
                start_point=user_location,
                destinations=best_route_genes
            )
            map_plotter.save_map(map_filepath) 
            vis_urls["best_route_map"] = f"{base_url}static/{map_filename}"
        except Exception as e:
            print(f"Error saat membuat peta terbaik: {e}")
            vis_urls["best_route_map"] = f"Error: {e}"

    # --- 5b. Peta Semua Rute ---
    if recommendations and hasattr(system.hga, 'final_population'):
        try:
            print(f"Membuat peta {request_data.num_routes} rute terbaik...")
            top_solutions = system.hga.final_population.get_best_n_chromosomes(request_data.num_routes)
            routes_data = []
            colors = ['blue', 'red', 'green', 'purple', 'orange']
            for i, sol in enumerate(top_solutions):
                routes_data.append({
                    'destinations': sol.genes,
                    'name': f'Rute #{i+1} ({sol.get_total_distance():.2f} km)',
                    'color': colors[i % len(colors)]
                })
            
            multi_map = map_plotter.create_multiple_routes_map(
                start_point=user_location,
                routes_data=routes_data
            )
            multi_map = map_plotter.add_legend(multi_map)
            all_map_filename = f"all_routes_{datetime.now().isoformat()}.html"
            all_map_filepath = os.path.join(OUTPUT_DIR, all_map_filename)
            multi_map.save(all_map_filepath)
            vis_urls["all_routes_map"] = f"{base_url}static/{all_map_filename}"
        except Exception as e:
            print(f"Error saat membuat peta semua rute: {e}")
            vis_urls["all_routes_map"] = f"Error: {e}"

    # --- 5c. Buat SEMUA Plot Konvergensi ---
    try:
        print("Membuat semua plot statistik...")
        plotter = ConvergencePlotter(output_dir=OUTPUT_DIR)
        
        # Plot 1: Fitness Evolution
        plot_fitness_filename = f"fitness_evolution_{datetime.now().isoformat()}.png"
        plot_fitness_path = plotter.plot_fitness_evolution(
            stats_raw['best_fitness_history'], 
            stats_raw['average_fitness_history'],
            filename=plot_fitness_filename
        )
        if plot_fitness_path:
            vis_urls["fitness_evolution_plot"] = f"{base_url}static/{plot_fitness_filename}"
        
        # Plot 2: Distance Evolution
        plot_distance_filename = f"distance_evolution_{datetime.now().isoformat()}.png"
        plot_distance_path = plotter.plot_distance_evolution(
            stats_raw['best_fitness_history'], 
            stats_raw['average_fitness_history'],
            filename=plot_distance_filename
        )
        if plot_distance_path:
            vis_urls["distance_evolution_plot"] = f"{base_url}static/{plot_distance_filename}"

        # Plot 3: Statistics Summary
        plot_stats_filename = f"statistics_summary_{datetime.now().isoformat()}.png"
        plot_stats_path = plotter.plot_statistics_summary(
            stats_raw, # Kirim semua statistik mentah
            filename=plot_stats_filename
        )
        if plot_stats_path:
            vis_urls["statistics_summary_plot"] = f"{base_url}static/{plot_stats_filename}"

        # Plot 4: Convergence Analysis (Improvement Rate)
        plot_analysis_filename = f"convergence_analysis_{datetime.now().isoformat()}.png"
        plot_analysis_path = plotter.plot_convergence_analysis(
            stats_raw['best_fitness_history'],
            filename=plot_analysis_filename
        )
        if plot_analysis_path:
            vis_urls["convergence_analysis_plot"] = f"{base_url}static/{plot_analysis_filename}"
        # --- SELESAI TAMBAHAN ---

    except Exception as e:
        print(f"Error saat membuat plot: {e}")
        vis_urls["plots_error"] = f"Error: {e}"

    # 6. Bersihkan statistik
    stats_clean = stats_raw.copy()
    stats_clean.pop('best_solution', None)
    
    # 7. Kembalikan respons
    return RecommendationResponse(
        message="Rekomendasi rute berhasil dibuat.",
        user_location=user_location,
        recommendations=recommendations,
        statistics=stats_clean, 
        visualization_urls=vis_urls
    )