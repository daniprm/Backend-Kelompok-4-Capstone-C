"""
Main application untuk sistem rekomendasi rute wisata Surabaya
menggunakan Hybrid Genetic Algorithm (HGA)
"""
import os
import json
from typing import Tuple, List
from algorithms.hga import HybridGeneticAlgorithm
from utils.data_loader import load_destinations_from_csv
from models.route import Route
from visualization.map_plotter import RouteMapPlotter
from visualization.convergence_plotter import ConvergencePlotter
from system import TourismRouteRecommendationSystem


def main():
    """
    Fungsi utama untuk menjalankan sistem rekomendasi
    """
    print("="*70)
    print(" SISTEM REKOMENDASI RUTE WISATA SURABAYA")
    print(" Menggunakan Hybrid Genetic Algorithm (HGA)")
    print("="*70)
    print()
    
    # Inisialisasi sistem
    system = TourismRouteRecommendationSystem("./data/data_wisata_sby.csv")
    
    # Load data
    system.load_data()
    
    # Input koordinat user
    print("Masukkan koordinat lokasi Anda:")
    print("(Contoh: Surabaya Pusat sekitar -7.2575, 112.7521)")
    
    try:
        latitude = float(input("Latitude: ").strip())
        longitude = float(input("Longitude: ").strip())
        user_location = (latitude, longitude)
    except ValueError:
        print("Input tidak valid. Menggunakan lokasi default (Surabaya Pusat)")
        user_location = (-7.2575, 112.7521)
    
    print(f"\nLokasi Anda: {user_location}")
    print()
    
    # Konfigurasi HGA
    print("Konfigurasi HGA:")
    system.initialize_hga(
        population_size=70,
        generations=10000,
        crossover_rate=0.8,
        mutation_rate=0.1
    )
    
    # Dapatkan rekomendasi
    print("\nMencari 3 rute wisata optimal...\n")
    recommendations = system.get_route_recommendations(
        user_location=user_location,
        num_routes=3
    )
    
    # Tampilkan hasil
    print("\n" + "="*70)
    print(" HASIL REKOMENDASI RUTE WISATA")
    print("="*70)
    
    for route_info in recommendations:
        system.print_route_details(route_info)
    
    # Simpan hasil ke file JSON
    output_file = "route_recommendations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'user_location': user_location,
            'recommendations': recommendations
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print(f"Hasil JSON disimpan di: {output_file}")
    print(f"{'='*70}")
    
    # VISUALISASI - Buat grafik konvergensi
    print(f"\n{'='*70}")
    print(" MEMBUAT VISUALISASI")
    print(f"{'='*70}")
    
    # Buat directory untuk output
    os.makedirs('visualization/outputs', exist_ok=True)
    
    # Ambil statistik dari HGA
    stats = system.hga.get_evolution_statistics()
    
    # Plot grafik konvergensi
    print("\n1. Membuat grafik konvergensi...")
    plotter = ConvergencePlotter(output_dir='visualization/outputs')
    graph_files = plotter.create_all_plots(stats)
    
    # Buat peta rute
    print("\n2. Membuat peta rute interaktif dengan routing API...")
    map_plotter = RouteMapPlotter(center_location=user_location, use_real_routes=True)
    
    # Peta rute terbaik
    best_route_dest = system.hga.best_solution.genes
    best_distance = system.hga.best_solution.get_total_distance()
    
    route_map = map_plotter.create_route_map(
        start_point=user_location,
        destinations=best_route_dest,
        route_name=f"Rute Terbaik - {best_distance:.2f} km"
    )
    map_plotter.save_map('visualization/outputs/best_route_map.html')
    
    # Peta semua rute
    routes_data = []
    colors = ['blue', 'red', 'green']
    best_chromosomes = system.hga.get_evolution_statistics()['best_solution']
    
    # Get top 3 solutions from final population
    from algorithms.population import Population
    if hasattr(system.hga, 'final_population'):
        top_solutions = system.hga.final_population.get_best_n_chromosomes(3)
    else:
        top_solutions = [system.hga.best_solution] * 3
    
    for i, sol in enumerate(top_solutions[:3]):
        routes_data.append({
            'destinations': sol.genes,
            'name': f'Rute #{i+1} ({sol.get_total_distance():.2f} km)',
            'color': colors[i]
        })
    
    multi_map = map_plotter.create_multiple_routes_map(
        start_point=user_location,
        routes_data=routes_data
    )
    multi_map = map_plotter.add_legend(multi_map)
    multi_map.save('visualization/outputs/all_routes_map.html')
    print("   [OK] Peta semua rute: visualization/outputs/all_routes_map.html")
    
    # Summary
    print(f"\n{'='*70}")
    print(" VISUALISASI SELESAI")
    print(f"{'='*70}")
    print("\nOutput yang dihasilkan:")
    print(f"  [JSON] Data        : {output_file}")
    print(f"  [MAP]  Peta Terbaik: visualization/outputs/best_route_map.html")
    print(f"  [MAP]  Peta Semua  : visualization/outputs/all_routes_map.html")
    print(f"  [GRAF] Grafik (4)  : visualization/outputs/*.png")
    print(f"{'='*70}")
    print("\n[INFO] Buka file HTML untuk melihat peta interaktif di browser!")
    print(f"{'='*70}")
    
import uvicorn
def run_api():
    print("Menjalankan server Uvicorn di http://127.0.0.1:8000")
    print("Folder data: ", os.path.abspath("data"))
    print("Folder output: ", os.path.abspath("api_outputs"))
    print("Cek dokumentasi interaktif di http://127.0.0.1:8000/docs")
    
    # Menjalankan aplikasi dari dalam paket
    # "halal_route_optimizer.api.main:app" menunjuk ke file main.py di dalam api,
    # dan variabel 'app' di dalamnya.
    uvicorn.run(
        "api.run:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        # reload_dirs=["halal_route_optimizer"] # Aktifkan jika Anda ingin auto-reload
    )
    

if __name__ == "__main__":
    # main()
    run_api()
