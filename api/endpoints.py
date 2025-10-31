import os
import uuid
from fastapi import APIRouter, HTTPException, Request
from system import TourismRouteRecommendationSystem
# Import visualisasi di-comment karena tidak digunakan
# from visualization.map_plotter import RouteMapPlotter
# from visualization.convergence_plotter import ConvergencePlotter
from api.schemas import RouteRequest, RecommendationResponse
from api.config import (
    DEFAULT_POPULATION_SIZE,
    DEFAULT_GENERATIONS,
    DEFAULT_CROSSOVER_RATE,
    DEFAULT_MUTATION_RATE,
    DEFAULT_NUM_ROUTES
)
# from api.config import OUTPUT_DIR # Tidak diperlukan jika visualisasi dinonaktifkan
# from datetime import datetime # Tidak diperlukan jika visualisasi dinonaktifkan

router = APIRouter()
@router.post("/generate-routes", response_model=RecommendationResponse)
async def generate_routes(request_data: RouteRequest, http_request: Request):
    """
    Menghasilkan rekomendasi rute wisata berdasarkan lokasi pengguna.
    
    Request body hanya memerlukan:
    - latitude: Latitude lokasi pengguna
    - longitude: Longitude lokasi pengguna
    
    Parameter HGA dan jumlah rute dikonfigurasi secara otomatis di API:
    - population_size: 100
    - generations: 5000
    - crossover_rate: 0.8
    - mutation_rate: 0.1
    - num_routes: 3
    """
    
    # 1. Dapatkan sistem
    system: TourismRouteRecommendationSystem = http_request.app.state.recommendation_system
    if not system:
        raise HTTPException(status_code=503, detail="Sistem belum siap.")
    
    # 2. Inisialisasi HGA dengan konfigurasi default
    try:
        system.initialize_hga(
            population_size=DEFAULT_POPULATION_SIZE,
            generations=DEFAULT_GENERATIONS,
            crossover_rate=DEFAULT_CROSSOVER_RATE,
            mutation_rate=DEFAULT_MUTATION_RATE
        )
        print(f"HGA diinisialisasi dengan: population={DEFAULT_POPULATION_SIZE}, generations={DEFAULT_GENERATIONS}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    user_location = (request_data.latitude, request_data.longitude)
    
    # 3. Jalankan HGA
    print(f"Menjalankan HGA untuk user di {user_location}...")
    try:
        recommendations = system.get_route_recommendations(
            user_location=user_location,
            num_routes=DEFAULT_NUM_ROUTES
        )
    except Exception as e:
        print(f"Error saat menjalankan HGA: {e}")
        raise HTTPException(status_code=500, detail=f"Terjadi error saat kalkulasi: {e}")

    print("HGA selesai.")
    
    # Visualisasi dinonaktifkan - tidak diperlukan di output
    # Jika diperlukan visualisasi, uncomment kode di bawah ini
    
    """
    # 4. Dapatkan statistik
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
    """
    
    # 6. Kembalikan respons (tanpa statistics dan visualization_urls)
    return RecommendationResponse(
        message="Rekomendasi rute berhasil dibuat.",
        user_location=user_location,
        recommendations=recommendations
    )