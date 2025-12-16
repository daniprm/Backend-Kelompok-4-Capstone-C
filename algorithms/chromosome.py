"""
Class untuk representasi kromosom dalam Genetic Algorithm
"""
from typing import List, Tuple
import random
from models.destination import Destination
from models.route import Route
from utils.penalty import calculate_total_penalty, apply_penalty_to_fitness, get_constraint_violation_info

class Chromosome:
    """
    Class untuk merepresentasikan satu kromosom (solusi rute)
    
    Setiap kromosom merepresentasikan satu rute wisata dengan urutan destinasi tertentu
    Gen dalam kromosom adalah destinasi wisata individual
    
    Attributes:
        genes: List destinasi yang merepresentasikan urutan kunjungan
        start_point: Titik awal rute
        end_point: Titik akhir rute
        fitness_value: Nilai fitness (akan dihitung)
        penalty_value: Nilai penalty dari constraint violations
    """
    
    def __init__(
            self,
            genes: List[Destination],
            start_point: Tuple[float, float],
        ):
        self.genes = genes
        self.start_point = start_point
        self.fitness_value = None
        self.penalty_value = None
        self._total_distance = None
        self._total_time = None
    
    def calculate_fitness(self) -> float:
        """
        Menghitung nilai fitness kromosom dengan mekanisme penalty
        
        Fitness = (1 / total_distance) dengan penalty jika melanggar constraint
        Constraint:
        - Jarak maksimal: 20 km
        - Waktu tempuh maksimal: 5 jam (300 menit)
        
        Returns:
            Nilai fitness (dengan penalty jika ada pelanggaran constraint)
        """
        route = Route(
            self.start_point, 
            self.genes, 
          )
        
        # Hitung total distance dan time
        self._total_distance = route.calculate_total_distance()
        self._total_time = route.calculate_total_travel_time()
        
        # Hitung base fitness (tanpa penalty)
        if self._total_distance == 0:
            base_fitness = float('inf')
        else:
            # Fitness berbanding terbalik dengan jarak (jarak pendek = fitness tinggi)
            base_fitness = 1.0 / self._total_distance
        
        # Hitung penalty dari constraint violations
        self.penalty_value = calculate_total_penalty(self._total_distance, self._total_time)
        
        # Terapkan penalty pada fitness
        self.fitness_value = apply_penalty_to_fitness(base_fitness, self.penalty_value)
        
        return self.fitness_value
    
    def get_fitness(self) -> float:
        """
        Mendapatkan nilai fitness (hitung jika belum ada)
        Returns:
            Nilai fitness
        """
        if self.fitness_value is None:
            return self.calculate_fitness()
        return self.fitness_value
    
    def get_total_distance(self) -> float:
        """
        Mendapatkan total jarak rute
        
        Returns:
            Total jarak dalam km
        """
        if self._total_distance is not None:
            return self._total_distance
            
        route = Route(
            self.start_point, 
            self.genes, 
            )
        return route.calculate_total_distance()
    
    def get_total_travel_time(self) -> float:
        """
        Mendapatkan total waktu tempuh rute
        
        Returns:
            Total waktu tempuh dalam menit
        """
        if self._total_time is not None:
            return self._total_time
            
        route = Route(
            self.start_point, 
            self.genes, 
            )
        return route.calculate_total_travel_time()
    
    def get_penalty(self) -> float:
        """
        Mendapatkan nilai penalty (hitung jika belum ada)
        
        Returns:
            Nilai penalty dari constraint violations
        """
        if self.penalty_value is None:
            self.calculate_fitness()
        return self.penalty_value
    
    def get_constraint_info(self) -> dict:
        """
        Mendapatkan informasi detail tentang constraint violations
        
        Returns:
            Dictionary berisi informasi pelanggaran constraint
        """
        # Pastikan nilai sudah dihitung
        if self._total_distance is None or self._total_time is None:
            self.calculate_fitness()
            
        return get_constraint_violation_info(self._total_distance, self._total_time)
    
    def is_feasible(self) -> bool:
        """
        Mengecek apakah kromosom memenuhi semua constraint (feasible solution)
        
        Returns:
            True jika tidak ada constraint yang dilanggar
        """
        constraint_info = self.get_constraint_info()
        return constraint_info['is_feasible']
    
    def is_valid(self) -> bool:
        """
        Memvalidasi apakah kromosom memenuhi constraint
        
        Returns:
            True jika valid
        """
        route = Route(
            self.start_point,
            self.genes,
            # self.end_point
          )
        return route.is_valid_route_order()
    
    def copy(self) -> 'Chromosome':
        """
        Membuat salinan kromosom
        
        Returns:
            Kromosom baru yang merupakan salinan
        """
        new_chromosome = Chromosome(
            genes=self.genes.copy(),
            start_point=self.start_point,
        )
        # Copy cached values untuk menghindari recomputation
        new_chromosome.fitness_value = self.fitness_value
        new_chromosome.penalty_value = self.penalty_value
        new_chromosome._total_distance = self._total_distance
        new_chromosome._total_time = self._total_time
        return new_chromosome
    
    def __repr__(self) -> str:
        penalty_str = f", penalty={self.get_penalty():.6f}" if self.penalty_value and self.penalty_value > 0 else ""
        time_str = f", time={self.get_total_travel_time():.1f}min"
        feasible_str = " [FEASIBLE]" if self.is_feasible() else " [INFEASIBLE]"
        return f"Chromosome(genes={len(self.genes)}, fitness={self.get_fitness():.6f}, distance={self.get_total_distance():.2f}km{time_str}{penalty_str}){feasible_str}"
    
    def __lt__(self, other: 'Chromosome') -> bool:
        """
        Perbandingan untuk sorting (fitness lebih tinggi = lebih baik)
        """
        return self.get_fitness() < other.get_fitness()
