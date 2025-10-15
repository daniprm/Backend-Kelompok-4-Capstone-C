"""
Class untuk representasi kromosom dalam Genetic Algorithm
"""
from typing import List, Tuple
import random
from models.destination import Destination
from models.route import Route

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
    """
    
    def __init__(
            self,
            genes: List[Destination],
            start_point: Tuple[float, float],
            # end_point: Tuple[float, float] = None
        ):
        """
        Inisialisasi kromosom
        
        Args:
            genes: List destinasi dalam urutan tertentu
            start_point: Koordinat titik awal
            end_point: Koordinat titik akhir (default sama dengan start_point)
        """
        self.genes = genes
        self.start_point = start_point
        # self.end_point = end_point if end_point else start_point
        self.fitness_value = None
    
    def calculate_fitness(self) -> float:
        """
        Menghitung nilai fitness kromosom
        Fitness = 1 / total_distance (semakin kecil jarak, semakin tinggi fitness)
        
        Returns:
            Nilai fitness
        """
        route = Route(
            self.start_point, 
            self.genes, 
            # self.end_point
          )
        total_distance = route.calculate_total_distance()
        
        # Menghindari division by zero
        if total_distance == 0:
            self.fitness_value = float('inf')
        else:
            # Fitness berbanding terbalik dengan jarak (jarak pendek = fitness tinggi)
            self.fitness_value = 1.0 / total_distance
        
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
        route = Route(
            self.start_point, 
            self.genes, 
            # self.end_point
            )
        return route.calculate_total_distance()
    
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
        return Chromosome(
            genes=self.genes.copy(),
            start_point=self.start_point,
            # end_point=self.end_point
        )
    
    def __repr__(self) -> str:
        return f"Chromosome(genes={len(self.genes)}, fitness={self.get_fitness():.6f}, distance={self.get_total_distance():.2f}km)"
    
    def __lt__(self, other: 'Chromosome') -> bool:
        """
        Perbandingan untuk sorting (fitness lebih tinggi = lebih baik)
        """
        return self.get_fitness() < other.get_fitness()
