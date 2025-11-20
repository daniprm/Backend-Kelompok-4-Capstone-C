"""
Algoritma 2-Opt untuk local search optimization
"""
from typing import List
from algorithms.chromosome import Chromosome
from models.destination import Destination
from utils.distance import calculate_distance

class TwoOptOptimizer:
    """
    Class untuk mengimplementasikan algoritma 2-Opt
    
    2-Opt adalah algoritma local search yang mencoba memperbaiki rute dengan
    menghilangkan crossing edges (edge yang bersilangan)
    """
    
    def __init__(self, max_iterations: int = 500):
        """
        Inisialisasi 2-Opt optimizer
        
        Args:
            max_iterations: Maksimal iterasi untuk mencari improvement
        """
        self.max_iterations = max_iterations
    
    def optimize(self, chromosome: Chromosome) -> Chromosome:
        """
        Mengoptimasi kromosom menggunakan algoritma 2-Opt
        
        Args:
            chromosome: Kromosom yang akan dioptimasi
            
        Returns:
            Kromosom yang telah dioptimasi
        """
        # Copy kromosom untuk tidak memodifikasi yang asli
        current_genes = chromosome.genes.copy()
        current_distance = self._calculate_route_distance(
            current_genes, 
            chromosome.start_point, 
            # chromosome.end_point
        )
        
        improved = True
        iteration = 0
        
        while improved and iteration < self.max_iterations:
            improved = False
            iteration += 1
            
            # Coba semua kemungkinan 2-opt swap
            for i in range(len(current_genes) - 1):
                for j in range(i + 2, len(current_genes)):
                    # Buat rute baru dengan reverse segment antara i dan j
                    new_genes = self._two_opt_swap(current_genes, i, j)
                    new_distance = self._calculate_route_distance(
                        new_genes,
                        chromosome.start_point,
                        # chromosome.end_point
                    )
                    
                    # Jika lebih baik, gunakan rute baru
                    if new_distance < current_distance:
                        current_genes = new_genes
                        current_distance = new_distance
                        improved = True
                        break
                
                if improved:
                    break
        
        # Return kromosom yang telah dioptimasi
        return Chromosome(
            current_genes, 
            chromosome.start_point, 
            # chromosome.end_point
          )
    
    def _two_opt_swap(self, genes: List[Destination], i: int, j: int) -> List[Destination]:
        """
        Melakukan 2-opt swap dengan membalik segment antara index i dan j
        
        Args:
            genes: List destinasi
            i: Index awal segment
            j: Index akhir segment
            
        Returns:
            List destinasi dengan segment yang dibalik
        """
        new_genes = genes.copy()
        # Reverse segment antara i dan j
        new_genes[i:j+1] = reversed(new_genes[i:j+1])
        return new_genes
    
    def _calculate_route_distance(
            self, 
            genes: List[Destination],
            start_point: tuple,
            # end_point: tuple
        ) -> float:
        """
        Menghitung total jarak rute
        
        Args:
            genes: List destinasi
            start_point: Koordinat awal
            end_point: Koordinat akhir
            
        Returns:
            Total jarak dalam km
        """
        if not genes:
            return 0.0
        
        total_distance = 0.0
        
        # Jarak dari start ke destinasi pertama
        total_distance += calculate_distance(
            start_point[0], start_point[1],
            genes[0].latitude, genes[0].longitude
        )
        
        # Jarak antar destinasi
        for i in range(len(genes) - 1):
            total_distance += calculate_distance(
                genes[i].latitude, genes[i].longitude,
                genes[i + 1].latitude, genes[i + 1].longitude
            )
        
        # # Jarak dari destinasi terakhir ke end
        # total_distance += calculate_distance(
        #     genes[-1].latitude, genes[-1].longitude,
        #     end_point[0], end_point[1]
        # )
        
        return total_distance
    
    def optimize_with_constraints(self, chromosome: Chromosome) -> Chromosome:
        """
        Mengoptimasi kromosom dengan mempertahankan constraint urutan kategori
        
        Hanya menukar destinasi dalam kategori yang sama untuk mempertahankan pola
        K1, C1, W1, K2, W2, C2, K3, O
        
        Args:
            chromosome: Kromosom yang akan dioptimasi
            
        Returns:
            Kromosom yang telah dioptimasi dengan constraint terpenuhi
        """
        # Untuk constraint-based optimization, kita hanya bisa menukar
        # destinasi dalam posisi yang memiliki kategori yang sama
        
        # Mapping kategori ke posisi dalam rute
        category_positions = {
            'makanan_berat': [0, 3, 6],  # K1, K2, K3
            'makanan_ringan': [1, 5],     # C1, C2
            'non_kuliner': [2, 4],        # W1, W2
            'oleh_oleh': [7]              # O
        }
        
        current_genes = chromosome.genes.copy()
        current_distance = self._calculate_route_distance(
            current_genes,
            chromosome.start_point,
        )
        
        improved = True
        iteration = 0
        
        while improved and iteration < self.max_iterations:
            improved = False
            iteration += 1
            
            # Coba swap dalam kategori yang sama
            for category, positions in category_positions.items():
                if len(positions) < 2:
                    continue
                
                # Coba semua kombinasi swap dalam kategori
                for i in range(len(positions)):
                    for j in range(i + 1, len(positions)):
                        pos_i = positions[i]
                        pos_j = positions[j]
                        
                        # Swap
                        new_genes = current_genes.copy()
                        new_genes[pos_i], new_genes[pos_j] = new_genes[pos_j], new_genes[pos_i]
                        
                        new_distance = self._calculate_route_distance(
                            new_genes,
                            chromosome.start_point,
                            # chromosome.end_point
                        )
                        
                        if new_distance < current_distance:
                            current_genes = new_genes
                            current_distance = new_distance
                            improved = True
                            break
                    
                    if improved:
                        break
                
                if improved:
                    break
        
        return Chromosome(
            current_genes, 
            chromosome.start_point, 
            # chromosome.end_point
          )