"""
Hybrid Genetic Algorithm (HGA) untuk optimasi rute wisata
Menggabungkan Genetic Algorithm dengan 2-Opt local search
"""
from typing import List, Tuple, Dict
import random
from algorithms.chromosome import Chromosome
from algorithms.population import Population
from algorithms.operators import GAOperators
from algorithms.two_opt import TwoOptOptimizer
from models.destination import Destination

class HybridGeneticAlgorithm:
    
    def __init__(self,
                 population_size: int = 100,
                 generations: int = 200,
                 crossover_rate: float = 0.8,
                 mutation_rate: float = 0.1,
                 elitism_count: int = 2,
                 tournament_size: int = 3,
                 use_2opt: bool = True,
                 two_opt_iterations: int = 500):
        
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.tournament_size = tournament_size
        self.use_2opt = use_2opt
        
        # Inisialisasi operator dan optimizer
        self.operators = GAOperators()
        self.two_opt = TwoOptOptimizer(max_iterations=two_opt_iterations)
        
        # Tracking evolusi
        self.best_fitness_history = []
        self.average_fitness_history = []
        self.best_solution = None
    
    def run(self, 
            destinations: List[Destination],
            start_point: Tuple[float, float],
            num_solutions: int = 3) -> List[Chromosome]:
        """
        Menjalankan HGA untuk menemukan solusi rute optimal
        
        Args:
            destinations: List semua destinasi yang tersedia
            start_point: Koordinat titik awal
            end_point: Koordinat titik akhir
            num_solutions: Jumlah solusi terbaik yang dikembalikan
            
        Returns:
            List kromosom (solusi) terbaik
        """
        print("=== Memulai Hybrid Genetic Algorithm ===")
        print(f"Populasi: {self.population_size}, Generasi: {self.generations}")
        print(f"Crossover Rate: {self.crossover_rate}, Mutation Rate: {self.mutation_rate}")
        print(f"Elitism: {self.elitism_count}, 2-Opt: {self.use_2opt}\n")
        
        # 1. Inisialisasi populasi awal
        print("Tahap 1: Inisialisasi populasi...")
        population = Population(population_size=self.population_size)
        population.initialize_random_population(
            destinations,
            start_point,
          )
        population.evaluate_fitness()
        
        best_initial = population.get_best_chromosome()
        print(f"Populasi awal - Best distance: {best_initial.get_total_distance():.2f} km\n")
        
        # 2. Evolusi melalui generasi
        print("Tahap 2: Evolusi melalui generasi...")
        for generation in range(self.generations):
            # 3. Evaluasi fitness
            population.evaluate_fitness()
            population.sort_by_fitness()
            
            # Track best solution
            current_best = population.get_best_chromosome()
            self.best_fitness_history.append(current_best.get_fitness())
            self.average_fitness_history.append(population.get_average_fitness())
            
            if self.best_solution is None or current_best.get_fitness() > self.best_solution.get_fitness():
                self.best_solution = current_best.copy()
            
            # Print progress setiap 20 generasi
            if generation % 20 == 0:
                print(f"Gen {generation:3d} - Best: {current_best.get_total_distance():.2f} km, "
                      f"Avg: {1/population.get_average_fitness():.2f} km")
            
            # 9. Cek konvergensi
            if self._check_convergence(generation):
                print(f"\nKonvergensi tercapai pada generasi {generation}")
                break
            
            # 8. Generasi populasi baru
            # new_population = self._create_new_generation(population)
            new_population = self._create_new_generation_modified(population, destinations, start_point)
            population = new_population
        
        print(f"\n=== HGA Selesai ===")
        print(f"Solusi terbaik: {self.best_solution.get_total_distance():.2f} km\n")
        
        # Simpan final population untuk visualisasi
        population.evaluate_fitness()
        population.sort_by_fitness()
        self.final_population = population
        
        # Return n solusi terbaik yang unik
        return population.get_best_n_chromosomes(num_solutions)
    
    def _create_new_generation(self, population: Population) -> Population:
        """
        Membuat generasi baru menggunakan seleksi, crossover, mutasi, dan 2-opt
        
        Args:
            population: Populasi saat ini
            
        Returns:
            Populasi generasi baru
        """
        new_chromosomes = []
        
        # Elitism: Pertahankan individu terbaik
        elite_chromosomes = population.get_best_n_chromosomes(self.elitism_count)
        new_chromosomes.extend([c.copy() for c in elite_chromosomes])
        
        # Generate offspring hingga populasi penuh
        while len(new_chromosomes) < self.population_size:
            # 4. Seleksi
            parent1 = self.operators.tournament_selection(
                population.chromosomes, 
                self.tournament_size
            )
            parent2 = self.operators.tournament_selection(
                population.chromosomes,
                self.tournament_size
            )
            parent3 = self.operators.tournament_selection(
                population.chromosomes,
                self.tournament_size
            )
            parent4 = self.operators.tournament_selection(
                population.chromosomes,
                self.tournament_size
            )

            # 5. Crossover
            if random.random() < self.crossover_rate:
                offspring1, offspring2 = self.operators.order_crossover_modified(parent1, parent2, parent3, parent4)
            else:
                offspring1, offspring2 = parent1.copy(), parent2.copy()
            
            
            # 6. Mutasi
            offspring1 = self.operators.swap_mutation(offspring1, self.mutation_rate)
            offspring2 = self.operators.swap_mutation(offspring2, self.mutation_rate)
            
            # 7. Local search dengan 2-Opt
            if self.use_2opt:
                offspring1 = self.two_opt.optimize_with_constraints(offspring1)
                offspring2 = self.two_opt.optimize_with_constraints(offspring2)
            
            new_chromosomes.append(offspring1)
            if len(new_chromosomes) < self.population_size:
                new_chromosomes.append(offspring2)
        
        # Batasi ukuran populasi
        new_chromosomes = new_chromosomes[:self.population_size]
        
        return Population(chromosomes=new_chromosomes, population_size=self.population_size)

    def _create_new_generation_modified(self, population: Population, destinations: List[Destination], start_point: Tuple[float, float]) -> Population:
        """
        Membuat generasi baru dengan satu offspring hasil evolusi, sisanya random population.
        
        Args:
            population: Populasi saat ini
            
        Returns:
            Populasi generasi baru
        """
        new_chromosomes = []

        # Elitism: Pertahankan individu terbaik
        elite_chromosomes = population.get_best_n_chromosomes(self.elitism_count)
        new_chromosomes.extend([c.copy() for c in elite_chromosomes])

        # Hanya satu offspring hasil evolusi
        parent1 = self.operators.tournament_selection(
            population.chromosomes, self.tournament_size
        )
        parent2 = self.operators.tournament_selection(
            population.chromosomes, self.tournament_size
        )
        parent3 = self.operators.tournament_selection(
            population.chromosomes, self.tournament_size
        )
        parent4 = self.operators.tournament_selection(
            population.chromosomes, self.tournament_size
        )

        if random.random() < self.crossover_rate:
            offspring, _ = self.operators.order_crossover_modified(parent1, parent2, parent3, parent4)
        else:
            offspring = parent1.copy()

        offspring = self.operators.swap_mutation(offspring, self.mutation_rate)
        if self.use_2opt:
            offspring = self.two_opt.optimize_with_constraints(offspring)

        new_chromosomes.append(offspring)

        # Sisanya random population seperti inisialisasi awal
        remaining = self.population_size - len(new_chromosomes)
        if remaining > 0:
            # Ambil data dari populasi awal (destinations dan start_point)
            destinations = destinations
            start_point = start_point

            temp_population = Population(population_size=remaining)
            temp_population.initialize_random_population(destinations, start_point)
            temp_population.evaluate_fitness()
            new_chromosomes.extend(temp_population.chromosomes)

        # Batasi ukuran populasi
        new_chromosomes = new_chromosomes[:self.population_size]

        return Population(chromosomes=new_chromosomes, population_size=self.population_size)
    
    # TODO: Pengatur konvergensi
    def _check_convergence(self, generation: int, patience: int = 2500) -> bool:
        """
        Mengecek apakah algoritma sudah konvergen
        
        Konvergensi tercapai jika tidak ada improvement signifikan dalam beberapa generasi
        
        Args:
            generation: Generasi saat ini
            patience: Jumlah generasi tanpa improvement untuk dianggap konvergen
            
        Returns:
            True jika konvergen
        """
        if generation < patience:
            return False
        
        # Cek apakah fitness tidak berubah dalam 'patience' generasi terakhir
        recent_fitness = self.best_fitness_history[-patience:]
        
        if len(set(recent_fitness)) == 1:  # Semua nilai sama
            return True
        
        # Cek improvement rate
        improvement_rate = (recent_fitness[-1] - recent_fitness[0]) / recent_fitness[0]
        
        if abs(improvement_rate) < 0.001:  # Improvement < 0.1%
            return True
        
        return False
    
    def get_evolution_statistics(self) -> Dict:
        """
        Mendapatkan statistik evolusi algoritma
        
        Returns:
            Dictionary berisi statistik
        """
        return {
            'total_generations': len(self.best_fitness_history),
            'best_fitness_history': self.best_fitness_history,
            'average_fitness_history': self.average_fitness_history,
            'best_distance': self.best_solution.get_total_distance() if self.best_solution else None,
            'best_solution': self.best_solution
        }
    
    def get_best_routes(self, num_routes: int = 3) -> List[Dict]:
        """
        Mendapatkan deskripsi detail dari rute-rute terbaik
        
        Args:
            num_routes: Jumlah rute yang diinginkan
            
        Returns:
            List dictionary berisi detail rute
        """
        if not hasattr(self, 'final_solutions'):
            return []
        
        routes = []
        for i, chromosome in enumerate(self.final_solutions[:num_routes]):
            route_info = {
                'rank': i + 1,
                'total_distance_km': round(chromosome.get_total_distance(), 2),
                'fitness': round(chromosome.get_fitness(), 6),
                'destinations': [
                    {
                        'order': j + 1,
                        'name': dest.nama,
                        'category': dest.kategori,
                        'latitude': dest.latitude,
                        'longitude': dest.longitude
                    }
                    for j, dest in enumerate(chromosome.genes)
                ]
            }
            routes.append(route_info)
        
        return routes
