"""
Operator-operator Genetic Algorithm: Selection, Crossover, Mutation
"""
import random
from typing import List, Tuple
from algorithms.chromosome import Chromosome

class GAOperators:
    """
    Class yang berisi operator-operator Genetic Algorithm
    """
    
    @staticmethod
    def tournament_selection(population: List[Chromosome], 
                            tournament_size: int = 3) -> Chromosome:
        """
        Seleksi menggunakan metode tournament
        
        Memilih beberapa kromosom secara random dan mengambil yang terbaik
        
        Args:
            population: List kromosom dalam populasi
            tournament_size: Jumlah kromosom yang ikut tournament
            
        Returns:
            Kromosom pemenang tournament
        """
        tournament = random.sample(population, min(tournament_size, len(population))) # min() memastikan bahwa ukuran tournament tidak melebihi populasi
        return max(tournament, key=lambda x: x.get_fitness())
    
    @staticmethod
    def roulette_wheel_selection(population: List[Chromosome]) -> Chromosome:
        """
        Seleksi menggunakan metode roulette wheel
        
        Probabilitas terpilih sebanding dengan nilai fitness
        
        Args:
            population: List kromosom dalam populasi
            
        Returns:
            Kromosom yang terpilih
        """
        total_fitness = sum(c.get_fitness() for c in population)
        
        if total_fitness == 0:
            return random.choice(population)
        
        # Generate random number
        pick = random.uniform(0, total_fitness)
        current = 0
        
        for chromosome in population:
            current += chromosome.get_fitness()
            if current > pick:
                return chromosome
        
        return population[-1]
    
    @staticmethod
    def order_crossover(parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Order Crossover (OX) - Cocok untuk masalah rute/permutasi
        
        Mempertahankan urutan relatif gen dari parent dengan mengambil subset dari satu parent
        dan mengisi sisanya dengan urutan dari parent lain
        
        Args:
            parent1: Kromosom parent pertama
            parent2: Kromosom parent kedua
            
        Returns:
            Tuple dua kromosom offspring
        """
        size = len(parent1.genes)
        
        # Pilih dua titik crossover random
        point1 = random.randint(0, size - 1)
        point2 = random.randint(0, size - 1)
        
        # Pastikan point1 < point2
        if point1 > point2:
            point1, point2 = point2, point1
        
        # Buat offspring 1
        offspring1_genes = [None] * size
        offspring1_genes[point1:point2] = parent1.genes[point1:point2]
        
        # Fill remaining positions dari parent2 dengan order yang sama
        # Gunakan ID destinasi untuk perbandingan unik
        selected_genes = offspring1_genes[point1:point2]
        selected_ids = {id(gene) for gene in selected_genes}
        
        parent2_filtered = [gene for gene in parent2.genes 
                           if id(gene) not in selected_ids]
        
        idx = 0
        for i in range(size):
            if offspring1_genes[i] is None:
                if idx < len(parent2_filtered):
                    offspring1_genes[i] = parent2_filtered[idx]
                    idx += 1
                else:
                    # Fallback: gunakan gen dari parent1 jika parent2_filtered habis
                    offspring1_genes[i] = parent1.genes[i]
        
        # Buat offspring 2 dengan cara yang sama
        offspring2_genes = [None] * size
        offspring2_genes[point1:point2] = parent2.genes[point1:point2]
        
        selected_genes2 = offspring2_genes[point1:point2]
        selected_ids2 = {id(gene) for gene in selected_genes2}
        
        parent1_filtered = [gene for gene in parent1.genes 
                           if id(gene) not in selected_ids2]
        
        idx = 0
        for i in range(size):
            if offspring2_genes[i] is None:
                if idx < len(parent1_filtered):
                    offspring2_genes[i] = parent1_filtered[idx]
                    idx += 1
                else:
                    # Fallback: gunakan gen dari parent2 jika parent1_filtered habis
                    offspring2_genes[i] = parent2.genes[i]
        
        offspring1 = Chromosome(
            offspring1_genes, 
            parent1.start_point, 
            # parent1.end_point
          )
        offspring2 = Chromosome(
            offspring2_genes, 
            parent2.start_point, 
            # parent2.end_point
          )
        
        return offspring1, offspring2
    
    @staticmethod
    def order_crossover_modified(parent1: Chromosome, parent2: Chromosome, parent3: Chromosome, parent4: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Order Crossover (OX) - Cocok untuk masalah rute/permutasi
        
        Mempertahankan urutan relatif gen dari parent dengan mengambil subset dari satu parent
        dan mengisi sisanya dengan urutan dari parent lain
        
        Args:
            parent1: Kromosom parent pertama
            parent2: Kromosom parent kedua
            
        Returns:
            Tuple dua kromosom offspring
        """
        size = len(parent1.genes)
        
        # Pilih dua titik crossover random
        point1 = random.randint(0, size - 1)
        point2 = random.randint(0, size - 1)
        
        # Pastikan point1 < point2
        if point1 > point2:
            point1, point2 = point2, point1
        
        # Buat offspring 1
        offspring1_genes = [None] * size
        offspring1_genes[point1:point2] = parent1.genes[point1:point2]
        
        # Fill remaining positions dari parent2 dengan order yang sama
        # Gunakan ID destinasi untuk perbandingan unik
        selected_genes = offspring1_genes[point1:point2]
        selected_ids = {id(gene) for gene in selected_genes}
        
        parent2_filtered = [
            gene if id(gene) not in selected_ids else None
            for gene in parent2.genes
        ]
        parent3_filtered = [
            gene if id(gene) not in selected_ids else None
            for gene in parent3.genes
        ]
        
        parent4_filtered = [
            gene if id(gene) not in selected_ids else None
            for gene in parent4.genes
        ]
        
        # idx = 0
        for i in range(size):
            # if offspring1_genes[i] is None:
            #     if idx < len(parent2_filtered):
            #         offspring1_genes[i] = parent2_filtered[idx]
            #         idx += 1
            #     else:
            #         # Fallback: gunakan gen dari parent1 jika parent2_filtered habis
            #         offspring1_genes[i] = parent1.genes[i]
            if offspring1_genes[i] is None and parent2_filtered[i] is not None:
                offspring1_genes[i] = parent2_filtered[i]
            elif offspring1_genes[i] is None and parent3_filtered[i] is not None:
                offspring1_genes[i] = parent3_filtered[i]
            elif offspring1_genes[i] is None and parent4_filtered[i] is not None:
                offspring1_genes[i] = parent4_filtered[i]
            else:
                # Fallback: gunakan gen dari parent1 jika parent2_filtered habis
                offspring1_genes[i] = parent1.genes[i]

        
        # Buat offspring 2 dengan cara yang sama
        offspring2_genes = [None] * size
        offspring2_genes[point1:point2] = parent2.genes[point1:point2]
        
        selected_genes2 = offspring2_genes[point1:point2]
        selected_ids2 = {id(gene) for gene in selected_genes2}
        
        parent1_filtered = [
            gene if id(gene) not in selected_ids2 else None
            for gene in parent1.genes
        ]
        parent3_filtered = [
            gene if id(gene) not in selected_ids2 else None
            for gene in parent3.genes
        ]
        parent4_filtered = [
            gene if id(gene) not in selected_ids2 else None
            for gene in parent4.genes
        ]
        
        
        # idx = 0
        # for i in range(size):
        #     if offspring2_genes[i] is None:
        #         if idx < len(parent1_filtered):
        #             offspring2_genes[i] = parent1_filtered[idx]
        #             idx += 1
        #         else:
        #             # Fallback: gunakan gen dari parent2 jika parent1_filtered habis
        #             offspring2_genes[i] = parent2.genes[i]
        for i in range(size):
            if offspring2_genes[i] is None and parent1_filtered[i] is not None:
                offspring2_genes[i] = parent1_filtered[i]
            elif offspring2_genes[i] is None and parent3_filtered[i] is not None:
                offspring2_genes[i] = parent3_filtered[i]
            elif offspring2_genes[i] is None and parent4_filtered[i] is not None:
                offspring2_genes[i] = parent4_filtered[i]
            else:
                # Fallback: gunakan gen dari parent2 jika parent1_filtered habis
                offspring2_genes[i] = parent2.genes[i]
        
        offspring1 = Chromosome(
            offspring1_genes, 
            parent1.start_point, 
            # parent1.end_point
          )
        offspring2 = Chromosome(
            offspring2_genes, 
            parent2.start_point, 
            # parent2.end_point
          )
        
        return offspring1, offspring2
    
    @staticmethod
    def position_based_crossover(parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Position Based Crossover - Alternatif untuk OX
        
        Memilih beberapa posisi random dari parent1, sisanya diisi dengan urutan dari parent2
        
        Args:
            parent1: Kromosom parent pertama
            parent2: Kromosom parent kedua
            
        Returns:
            Tuple dua kromosom offspring
        """
        size = len(parent1.genes)
        
        # Pilih beberapa posisi random (sekitar 40% dari total)
        # Untuk 8 gen, 40% adalah sekitar 3 posisi
        num_positions = max(1, int(0.4 * size))
        selected_positions = random.sample(range(size), num_positions)
        
        # Buat offspring 1
        offspring1_genes = [None] * size
        for pos in selected_positions:
            offspring1_genes[pos] = parent1.genes[pos]
        
        # Isi sisanya dengan urutan dari parent2
        # Gunakan ID untuk perbandingan unik
        selected_genes = [g for g in offspring1_genes if g is not None]
        selected_ids = {id(gene) for gene in selected_genes}
        
        parent2_filtered = [gene for gene in parent2.genes if id(gene) not in selected_ids]
        
        idx = 0
        for i in range(size):
            if offspring1_genes[i] is None:
                if idx < len(parent2_filtered):
                    offspring1_genes[i] = parent2_filtered[idx]
                    idx += 1
                else:
                    # Fallback
                    offspring1_genes[i] = parent1.genes[i]
        
        # Buat offspring 2
        offspring2_genes = [None] * size
        for pos in selected_positions:
            offspring2_genes[pos] = parent2.genes[pos]
        
        selected_genes2 = [g for g in offspring2_genes if g is not None]
        selected_ids2 = {id(gene) for gene in selected_genes2}
        
        parent1_filtered = [gene for gene in parent1.genes if id(gene) not in selected_ids2]
        
        idx = 0
        for i in range(size):
            if offspring2_genes[i] is None:
                if idx < len(parent1_filtered):
                    offspring2_genes[i] = parent1_filtered[idx]
                    idx += 1
                else:
                    # Fallback
                    offspring2_genes[i] = parent2.genes[i]
        
        offspring1 = Chromosome(
            offspring1_genes, 
            parent1.start_point, 
          )
        offspring2 = Chromosome(
            offspring2_genes, 
            parent2.start_point, 
          )
        
        return offspring1, offspring2
    
    @staticmethod
    def swap_mutation(chromosome: Chromosome, mutation_rate: float = 0.01) -> Chromosome:
        """
        Swap Mutation - Menukar posisi dua gen
        
        Args:
            chromosome: Kromosom yang akan dimutasi
            mutation_rate: Probabilitas mutasi terjadi
            
        Returns:
            Kromosom hasil mutasi (bisa sama jika tidak terjadi mutasi)
        """
        if random.random() > mutation_rate:
            return chromosome
        
        # Copy genes
        mutated_genes = chromosome.genes.copy()
        size = len(mutated_genes)
        
        # Pilih dua posisi random dan tukar
        pos1 = random.randint(0, size - 1)
        pos2 = random.randint(0, size - 1)
        
        mutated_genes[pos1], mutated_genes[pos2] = mutated_genes[pos2], mutated_genes[pos1]
        
        return Chromosome(
            mutated_genes, 
            chromosome.start_point, 
            # chromosome.end_point
          )
    
    @staticmethod
    def inversion_mutation(chromosome: Chromosome, mutation_rate: float = 0.01) -> Chromosome:
        """
        Inversion Mutation - Membalik urutan subset gen
        
        Args:
            chromosome: Kromosom yang akan dimutasi
            mutation_rate: Probabilitas mutasi terjadi
            
        Returns:
            Kromosom hasil mutasi
        """
        if random.random() > mutation_rate:
            return chromosome
        
        mutated_genes = chromosome.genes.copy()
        size = len(mutated_genes)
        
        # Pilih dua posisi dan balik urutan di antaranya
        point1 = random.randint(0, size - 1)
        point2 = random.randint(0, size - 1)
        
        if point1 > point2:
            point1, point2 = point2, point1
        
        mutated_genes[point1:point2+1] = reversed(mutated_genes[point1:point2+1])
        
        return Chromosome(
            mutated_genes, 
            chromosome.start_point, 
            # chromosome.end_point
          )
    
    @staticmethod
    def scramble_mutation(chromosome: Chromosome, mutation_rate: float = 0.01) -> Chromosome:
        """
        Scramble Mutation - Mengacak urutan subset gen
        
        Args:
            chromosome: Kromosom yang akan dimutasi
            mutation_rate: Probabilitas mutasi terjadi
            
        Returns:
            Kromosom hasil mutasi
        """
        if random.random() > mutation_rate:
            return chromosome
        
        mutated_genes = chromosome.genes.copy()
        size = len(mutated_genes)
        
        # Pilih subset dan acak urutannya
        point1 = random.randint(0, size - 2)
        point2 = random.randint(point1 + 1, size - 1)
        
        subset = mutated_genes[point1:point2+1]
        random.shuffle(subset)
        mutated_genes[point1:point2+1] = subset
        
        return Chromosome(
            mutated_genes, 
            chromosome.start_point, 
            # chromosome.end_point
          )
