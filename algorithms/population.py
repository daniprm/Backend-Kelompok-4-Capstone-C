"""
Class untuk manajemen populasi dalam Genetic Algorithm
"""
from typing import List, Tuple
import random
from algorithms.chromosome import Chromosome
from models.destination import Destination
from utils.data_loader import group_destinations_by_category

class Population:
    """
    Class untuk merepresentasikan populasi (kumpulan kromosom)
    
    Attributes:
        chromosomes: List kromosom dalam populasi
        population_size: Ukuran populasi
    """
    
    def __init__(self, chromosomes: List[Chromosome] = None, population_size: int = 50):
        """
        Inisialisasi populasi
        
        Args:
            chromosomes: List kromosom (opsional)
            population_size: Ukuran populasi target
        """
        self.chromosomes = chromosomes if chromosomes else []
        self.population_size = population_size
    
    def initialize_random_population(
            self, 
            all_destinations: List[Destination],
            start_point: Tuple[float, float],
        ):
        """
        Inisialisasi populasi awal dengan kromosom random yang valid
        
        Setiap kromosom harus mengikuti pola: K1, C1, W1, K2, W2, C2, K3, O
        
        Args:
            all_destinations: List semua destinasi yang tersedia
            start_point: Koordinat titik awal
            end_point: Koordinat titik akhir
        """
        # Kelompokkan destinasi berdasarkan kategori
        grouped = group_destinations_by_category(all_destinations)
        
        # Validasi apakah ada cukup destinasi untuk setiap kategori
        required_counts = {
            'makanan_berat': 3,
            'makanan_ringan': 2,
            'non_kuliner': 3,
            'oleh_oleh': 1
        }
        
        for category, required_count in required_counts.items():
            if len(grouped[category]) < required_count:
                raise ValueError(f"Tidak cukup destinasi kategori {category}. "
                               f"Dibutuhkan {required_count}, tersedia {len(grouped[category])}")
        
        # Generate populasi
        for _ in range(self.population_size):
            chromosome = self._create_random_valid_chromosome(
                grouped,
                start_point,
            )
            self.chromosomes.append(chromosome)
    
    def _create_random_valid_chromosome(
            self,
            grouped_destinations: dict,
            start_point: Tuple[float, float],
        ) -> Chromosome:
        """
        Membuat satu kromosom random yang valid dengan pola K1, C1, W1, K2, W2, C2, K3, O
        
        Args:
            grouped_destinations: Dictionary destinasi yang sudah dikelompokkan
            start_point: Titik awal
            
        Returns:
            Kromosom valid
        """
        genes = []
        
        # K1 - Makanan berat pertama
        genes.append(random.choice(grouped_destinations['makanan_berat']))
        
        # C1 - Makanan ringan pertama
        genes.append(random.choice(grouped_destinations['makanan_ringan']))
        
        # W1 - Non kuliner pertama
        genes.append(random.choice(grouped_destinations['non_kuliner'] + grouped_destinations['all']))
        
        # K2 - Makanan berat kedua (tidak sama dengan K1)
        available_k2 = [d for d in grouped_destinations['makanan_berat'] if d != genes[0]]
        genes.append(random.choice(available_k2))
        
        # W2 - Non kuliner kedua (tidak sama dengan W1)
        available_w2 = [d for d in grouped_destinations['non_kuliner'] if d != genes[2]]
        available_w2.extend(d for d in grouped_destinations['all'] if d not in genes)
        genes.append(random.choice(available_w2))
        
        # C2 - Makanan ringan kedua (tidak sama dengan C1)
        available_c2 = [d for d in grouped_destinations['makanan_ringan'] if d != genes[1]]
        genes.append(random.choice(available_c2))
        
        # K3 - Makanan berat ketiga (tidak sama dengan K1 dan K2)
        available_k3 = [d for d in grouped_destinations['makanan_berat'] 
                       if d not in [genes[0], genes[3]]]
        genes.append(random.choice(available_k3))
        
        # O - Oleh-oleh
        available_o = [d for d in grouped_destinations['all'] if d not in genes]
        genes.append(random.choice(grouped_destinations['oleh_oleh'] + available_o))
        
        return Chromosome(
                genes, 
                start_point, 
            )
    
    def evaluate_fitness(self):
        for chromosome in self.chromosomes:
            chromosome.calculate_fitness()
    
    def sort_by_fitness(self):
        self.chromosomes.sort(reverse=True, key=lambda x: x.get_fitness())
    
    def get_best_chromosome(self) -> Chromosome:
        if not self.chromosomes:
            return None
        return max(self.chromosomes, key=lambda x: x.get_fitness())
    
    def get_best_n_chromosomes(self, n: int) -> List[Chromosome]:
        self.sort_by_fitness()
        return self.chromosomes[:n]
    
    def add_chromosome(self, chromosome: Chromosome):
        self.chromosomes.append(chromosome)
    
    def replace_population(self, new_chromosomes: List[Chromosome]):
        self.chromosomes = new_chromosomes
    
    def get_average_fitness(self) -> float:
        if not self.chromosomes:
            return 0.0
        return sum(c.get_fitness() for c in self.chromosomes) / len(self.chromosomes)
    
    def __len__(self) -> int:
        return len(self.chromosomes)
    
    def __repr__(self) -> str:
        best = self.get_best_chromosome()
        avg = self.get_average_fitness()
        return f"Population(size={len(self)}, best_fitness={best.get_fitness():.6f}, avg_fitness={avg:.6f})"
