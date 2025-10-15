"""
Script contoh penggunaan sistem rekomendasi rute wisata
Untuk testing dan demonstrasi tanpa input interaktif
"""
from algorithms.hga import HybridGeneticAlgorithm
from utils.data_loader import load_destinations_from_csv
from models.route import Route
from visualization.map_plotter import RouteMapPlotter
from visualization.convergence_plotter import ConvergencePlotter
import json
import os

def run_example():
    """
    Contoh penggunaan sistem dengan lokasi default
    """
    print("="*70)
    print(" CONTOH PENGGUNAAN SISTEM REKOMENDASI RUTE WISATA")
    print("="*70)
    print()
    
    # 1. Load data destinasi
    print("1. Memuat data destinasi wisata...")
    destinations = load_destinations_from_csv("./data/data_wisata_sby.csv")
    print(f"   [OK] Berhasil memuat {len(destinations)} destinasi\n")
    
    # 2. Setup lokasi user (contoh: Tugu Pahlawan Surabaya)
    user_location = (-7.2792995174612924, 112.79426806984044)  # ITS
    print(f"2. Lokasi user: {user_location}")
    print(f"   (ITS, Surabaya)\n")
    
    # 3. Inisialisasi HGA dengan parameter optimal
    print("3. Inisialisasi Hybrid Genetic Algorithm...")
    hga = HybridGeneticAlgorithm(
        population_size=40,      # Populasi lebih kecil untuk testing cepat
        generations=2000,         # Generasi lebih sedikit untuk testing
        crossover_rate=0.8,
        mutation_rate=0.1,
        elitism_count=1,
        tournament_size=5,
        use_2opt=True,
        two_opt_iterations=1000
    )
    print("   [OK] HGA berhasil diinisialisasi\n")
    
    # 4. Jalankan algoritma
    print("4. Menjalankan HGA untuk menemukan rute optimal...")
    print("-"*70)
    
    best_solutions = hga.run(
        destinations=destinations,
        start_point=user_location,
        num_solutions=3
    )
    
    print("-"*70)
    print()
    
    # 5. Tampilkan hasil
    print("5. HASIL REKOMENDASI RUTE WISATA")
    print("="*70)
    
    for i, chromosome in enumerate(best_solutions):
        route = Route(
            user_location, 
            chromosome.genes, 
            # user_location
          )
        route_info = route.get_route_summary()
        
        print(f"\n{'='*70}")
        print(f"RUTE #{i+1}")
        print(f"{'='*70}")
        print(f"Total Jarak      : {route_info['total_distance_km']} km")
        print(f"Fitness          : {chromosome.get_fitness():.6f}")
        print(f"Valid Order      : {'Ya' if route_info['is_valid_order'] else 'Tidak'}")
        print(f"\nUrutan Destinasi:")
        print(f"{'-'*70}")
        
        labels = ['K1', 'C1', 'W1', 'K2', 'W2', 'C2', 'K3', 'O']
        
        for dest in route_info['destinations']:
            idx = dest['order'] - 1
            label = labels[idx] if idx < len(labels) else '?'
            kategori_str = ', '.join(dest['kategori'])
            print(f"{dest['order']}. [{label:3s}] {dest['nama']}")
            print(f"        Kategori  : {kategori_str}")
            print(f"        Koordinat : ({dest['coordinates'][0]:.6f}, {dest['coordinates'][1]:.6f})")
    
    # 6. Simpan hasil ke file
    print(f"\n{'='*70}")
    print("6. Menyimpan hasil ke file...")
    
    output_data = {
        'user_location': user_location,
        'hga_config': {
            'population_size': 50,
            'generations': 100,
            'crossover_rate': 0.8,
            'mutation_rate': 0.1,
            'use_2opt': True
        },
        'solutions': []
    }
    
    for i, chromosome in enumerate(best_solutions):
        route = Route(user_location, chromosome.genes)
        route_info = route.get_route_summary()
        route_info['rank'] = i + 1
        route_info['fitness'] = chromosome.get_fitness()
        output_data['solutions'].append(route_info)
    
    # Simpan ke JSON
    with open('example_output.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("   [OK] Hasil disimpan ke: example_output.json")
    
    # 7. Statistik evolusi
    stats = hga.get_evolution_statistics()
    print(f"\n7. Statistik Evolusi:")
    print(f"   Total Generasi      : {stats['total_generations']}")
    print(f"   Jarak Terbaik       : {stats['best_distance']:.2f} km")
    print(f"   Fitness Awal        : {stats['best_fitness_history'][0]:.6f}")
    print(f"   Fitness Akhir       : {stats['best_fitness_history'][-1]:.6f}")
    
    improvement = ((stats['best_fitness_history'][-1] - stats['best_fitness_history'][0]) 
                   / stats['best_fitness_history'][0] * 100)
    print(f"   Improvement         : {improvement:.2f}%")
    
    # 8. VISUALISASI - Buat grafik konvergensi
    print(f"\n8. Membuat Visualisasi Grafik Konvergensi...")
    print(f"{'-'*70}")
    
    # Buat directory untuk output visualisasi
    os.makedirs('visualization/outputs', exist_ok=True)
    
    # Plot grafik konvergensi
    plotter = ConvergencePlotter(output_dir='visualization/outputs')
    graph_files = plotter.create_all_plots(stats)
    
    # 9. VISUALISASI - Buat peta rute
    print(f"\n9. Membuat Visualisasi Peta Rute...")
    print(f"{'-'*70}")
    
    # Inisialisasi map plotter dengan real routes enabled
    map_plotter = RouteMapPlotter(center_location=user_location, use_real_routes=True)
    
    # Buat peta untuk rute terbaik
    print(f"\n  Membuat peta rute terbaik dengan routing API...")
    best_route = best_solutions[0]
    route_map = map_plotter.create_route_map(
        start_point=user_location,
        destinations=best_route.genes,
        route_name=f"Rute Terbaik - {best_route.get_total_distance():.2f} km"
    )
    map_plotter.save_map('visualization/outputs/best_route_map.html')
    
    # Buat peta dengan semua 3 rute
    print(f"\n  Membuat peta semua rute dengan routing API...")
    routes_data = []
    colors = ['blue', 'red', 'green']
    for i, sol in enumerate(best_solutions[:3]):
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
    print(f"\n   [OK] Peta semua rute disimpan ke: visualization/outputs/all_routes_map.html")
    
    print(f"\n{'='*70}")
    print(" SELESAI - Sistem berhasil menemukan rute optimal!")
    print("="*70)
    print(f"\nOutput yang dihasilkan:")
    print(f"  1. JSON          : example_output.json")
    print(f"  2. Peta Terbaik  : visualization/outputs/best_route_map.html")
    print(f"  3. Peta Semua    : visualization/outputs/all_routes_map.html")
    print(f"  4. Grafik        : visualization/outputs/*.png (4 file)")
    print(f"{'='*70}")



if __name__ == "__main__":
    run_example()
