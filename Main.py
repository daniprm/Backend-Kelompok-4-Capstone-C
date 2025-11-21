"""
Main application untuk sistem rekomendasi rute wisata Surabaya
menggunakan Hybrid Genetic Algorithm (HGA)
"""
import os
import json
from typing import Tuple, List
from algorithms.hga import HybridGeneticAlgorithm
from utils.data_loader import load_destinations_from_csv, load_destinations_from_sqlite
from models.route import Route
from visualization.map_plotter import RouteMapPlotter
from visualization.convergence_plotter import ConvergencePlotter


def print_route_details(route_info: dict):
    """
    Mencetak detail rute dengan format yang mudah dibaca
    
    Args:
        route_info: Dictionary informasi rute
    """
    print(f"\n{'='*70}")
    print(f"RUTE #{route_info['rank']}")
    print(f"{'='*70}")
    print(f"Total Jarak: {route_info['total_distance_km']} km")
    print(f"Valid Order: {'Ya' if route_info['is_valid_order'] else 'Tidak'}")
    print(f"\nUrutan Destinasi:")
    print(f"{'-'*70}")
    
    # Label untuk setiap posisi sesuai pola K1,C1,W1,K2,W2,C2,K3,O
    labels = ['K1', 'C1', 'W1', 'K2', 'W2', 'C2', 'K3', 'O']
    
    for dest in route_info['destinations']:
        idx = dest['order'] - 1
        label = labels[idx] if idx < len(labels) else '?'
        print(f"{dest['order']}. [{label}] {dest['nama']}")
        print(f"   Kategori: {', '.join(dest['kategori'])}")
        print(f"   Koordinat: ({dest['coordinates'][0]}, {dest['coordinates'][1]})")
        print()


def main():
    """
    Fungsi utama untuk menjalankan sistem rekomendasi
    """
    print("="*70)
    print(" SISTEM REKOMENDASI RUTE WISATA SURABAYA")
    print(" Menggunakan Hybrid Genetic Algorithm (HGA)")
    print("="*70)
    print()
    
    # Load data destinasi
    print("Memuat data destinasi wisata...")
    use_sqlite = True  # Set ke False jika ingin pakai CSV
    
    if use_sqlite:
        print("Loading from SQLite database...")
        destinations = load_destinations_from_sqlite("./data/data_wisata_surabaya.db")
    else:
        print("Loading from CSV file...")
        destinations = load_destinations_from_csv("./data/data_wisata_sby.csv")
    
    print(f"Berhasil memuat {len(destinations)} destinasi\n")
    if destinations:
        print(f"Contoh destinasi: {destinations[0]}\n")
    
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
    
    # Konfigurasi dan inisialisasi HGA
    print("Konfigurasi HGA:")
    hga = HybridGeneticAlgorithm(
        population_size=70,
        generations=10000,
        crossover_rate=0.8,
        mutation_rate=0.1,
        elitism_count=2,
        tournament_size=5,
        use_2opt=True,
        two_opt_iterations=500
    )
    print(f"  Population Size: 70")
    print(f"  Generations: 10000")
    print(f"  Crossover Rate: 0.8")
    print(f"  Mutation Rate: 0.1")
    
    # Dapatkan rekomendasi
    print("\nMencari 3 rute wisata optimal...\n")
    num_routes = 3
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
        recommendations.append(route_info)
    
    # Tampilkan hasil
    print("\n" + "="*70)
    print(" HASIL REKOMENDASI RUTE WISATA")
    print("="*70)
    
    for route_info in recommendations:
        print_route_details(route_info)
    
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
    stats = hga.get_evolution_statistics()
    
    # Plot grafik konvergensi
    print("\n1. Membuat grafik konvergensi...")
    plotter = ConvergencePlotter(output_dir='visualization/outputs')
    graph_files = plotter.create_all_plots(stats)
    
    # Buat peta rute
    print("\n2. Membuat peta rute interaktif dengan routing API...")
    map_plotter = RouteMapPlotter(center_location=user_location, use_real_routes=True)
    
    # Peta rute terbaik
    best_route_dest = hga.best_solution.genes
    best_distance = hga.best_solution.get_total_distance()
    
    route_map = map_plotter.create_route_map(
        start_point=user_location,
        destinations=best_route_dest,
        route_name=f"Rute Terbaik - {best_distance:.2f} km"
    )
    map_plotter.save_map('visualization/outputs/best_route_map.html')
    
    # Peta semua rute
    routes_data = []
    colors = ['blue', 'red', 'green']
    
    # Get top 3 solutions from final population
    if hasattr(hga, 'final_population'):
        top_solutions = hga.final_population.get_best_n_chromosomes(3)
    else:
        top_solutions = [hga.best_solution] * 3
    
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
