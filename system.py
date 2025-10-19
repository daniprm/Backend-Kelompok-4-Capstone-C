import os
import json
from typing import Tuple, List
from algorithms.hga import HybridGeneticAlgorithm
from utils.data_loader import load_destinations_from_csv
from models.route import Route
from visualization.map_plotter import RouteMapPlotter
from visualization.convergence_plotter import ConvergencePlotter
class TourismRouteRecommendationSystem:
    """
    Sistem Rekomendasi Rute Wisata menggunakan HGA
    """
    
    def __init__(self, data_file: str = "./data/data_wisata_sby.csv"):
        """
        Inisialisasi sistem
        
        Args:
            data_file: Path ke file CSV data destinasi
        """
        self.data_file = data_file
        self.destinations = None
        self.hga = None
        
    def load_data(self):
        """
        Memuat data destinasi dari CSV
        """
        print("Memuat data destinasi wisata...")
        self.destinations = load_destinations_from_csv(self.data_file)
        print(f"Berhasil memuat {len(self.destinations)} destinasi\n")
        print(self.destinations[0])
        
    def initialize_hga(self, 
                      population_size: int = 70,
                      generations: int = 10000,
                      crossover_rate: float = 0.8,
                      mutation_rate: float = 0.1):
        """
        Inisialisasi Hybrid Genetic Algorithm
        
        Args:
            population_size: Ukuran populasi
            generations: Jumlah generasi
            crossover_rate: Probabilitas crossover
            mutation_rate: Probabilitas mutasi
        """
        self.hga = HybridGeneticAlgorithm(
            population_size=population_size,
            generations=generations,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            elitism_count=2,
            tournament_size=5,
            use_2opt=True,
            two_opt_iterations=500
        )
        
    def get_route_recommendations(self,
                                 user_location: Tuple[float, float],
                                 num_routes: int = 3) -> List[dict]:
        """
        Mendapatkan rekomendasi rute wisata optimal
        
        Args:
            user_location: Koordinat user (latitude, longitude)
            num_routes: Jumlah rute yang diinginkan
            
        Returns:
            List dictionary berisi detail rute
        """
        if self.destinations is None:
            raise ValueError("Data belum dimuat. Panggil load_data() terlebih dahulu")
        
        if self.hga is None:
            self.initialize_hga()
        
        # Jalankan HGA
        best_chromosomes = self.hga.run(
            destinations=self.destinations,
            start_point=user_location,
            # TODO: End point adalah destinasi terakhir, bukan lokasi user
            # end_point=user_location,
            num_solutions=num_routes
        )
        
        # Format hasil
        recommendations = []
        for i, chromosome in enumerate(best_chromosomes):
            route = Route(user_location, chromosome.genes)
            route_info = route.get_route_summary()
            route_info['rank'] = i + 1
            recommendations.append(route_info)
        
        return recommendations
    
    def print_route_details(self, route_info: dict):
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