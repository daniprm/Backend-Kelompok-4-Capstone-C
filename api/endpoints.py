import os
import uuid
from fastapi import APIRouter, HTTPException, Request
from ..system import TourismRouteRecommendationSystem
from visualization.map_plotter import RouteMapPlotter
from visualization.convergence_plotter import ConvergencePlotter
from schemas import RouteRequest, RecommendationResponse
from config import OUTPUT_DIR # Ambil path dari config

router = APIRouter()

@router.post("/generate-routes", response_model=RecommendationResponse)
async def generate_routes(request_data: RouteRequest, http_request: Request):
    """
    Menghasilkan rekomendasi rute wisata berdasarkan lokasi pengguna dan parameter HGA.
    """
    
    # 1. Dapatkan sistem rekomendasi dari state aplikasi
    # 'http_request.app.state.recommendation_system' di-set saat startup
    system: TourismRouteRecommendationSystem = http_request.app.state.recommendation_system
    if not system:
        raise HTTPException(status_code=503, detail="Sistem belum siap. Coba beberapa saat lagi.")
    
    # 2. Inisialisasi HGA dengan parameter dari request
    try:
        system.initialize_hga(
            population_size=request_data.population_size,
            generations=request_data.generations,
            crossover_rate=request_data.crossover_rate,
            mutation_rate=request_data.mutation_rate
        )
    except ValueError as e:
        # Tangkap error jika data destinasi tidak cukup
        raise HTTPException(status_code=400, detail=str(e))
    
    user_location = (request_data.latitude, request_data.longitude)
    
    # 3. Jalankan HGA (Proses intensif)
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
    stats = system.hga.get_evolution_statistics()
    
    # 5. Buat visualisasi
    run_id = str(uuid.uuid4())[:8]  # ID unik untuk nama file
    base_url = str(http_request.base_url)
    vis_urls = {}

    # --- 5a. Buat Peta Rute Terbaik ---
    if recommendations and system.hga.best_solution:
        try:
            print("Membuat peta rute terbaik...")
            map_plotter = RouteMapPlotter(center_location=user_location, use_real_routes=True)
            best_route_genes = system.hga.best_solution.genes
            
            map_filename = f"map_rute_terbaik_{run_id}.html"
            map_filepath = os.path.join(OUTPUT_DIR, map_filename)
            
            map_plotter.create_route_map(
                start_point=user_location,
                destinations=best_route_genes
            )
            map_plotter.save_map(map_filepath)
            
            # URL statis: {base_url}/static/{nama_file}
            vis_urls["best_route_map"] = f"{base_url}static/{map_filename}"
            print(f"Peta disimpan: {map_filepath}")

        except Exception as e:
            print(f"Error saat membuat peta: {e}")
            vis_urls["best_route_map"] = f"Error: {e}"

    # --- 5b. Buat Plot Konvergensi ---
    try:
        print("Membuat plot konvergensi...")
        plotter = ConvergencePlotter(output_dir=OUTPUT_DIR)
        plot_filename = f"plot_konvergensi_{run_id}.png"
        
        plot_path = plotter.plot_fitness_evolution(
            stats['best_fitness_history'], 
            stats['average_fitness_history'],
            filename=plot_filename
        )
        
        if plot_path:
            vis_urls["convergence_plot"] = f"{base_url}static/{plot_filename}"
            print(f"Plot disimpan: {plot_path}")
        else:
            vis_urls["convergence_plot"] = "Tidak ada data untuk di-plot."
            
    except Exception as e:
        print(f"Error saat membuat plot: {e}")
        vis_urls["convergence_plot"] = f"Error: {e}"

    # 6. Bersihkan statistik (hapus objek yg tidak serializable)
    stats.pop('best_solution', None)
    
    # 7. Kembalikan respons
    return RecommendationResponse(
        message="Rekomendasi rute berhasil dibuat.",
        user_location=user_location,
        recommendations=recommendations,
        statistics=stats,
        visualization_urls=vis_urls
    )