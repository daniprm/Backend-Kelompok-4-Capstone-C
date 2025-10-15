# Dokumentasi Teknis - Sistem Rekomendasi Rute Wisata dengan HGA

## 📖 Daftar Isi

1. [Arsitektur Sistem](#arsitektur-sistem)
2. [Penjelasan Modul](#penjelasan-modul)
3. [Alur Algoritma HGA](#alur-algoritma-hga)
4. [Detail Implementasi](#detail-implementasi)
5. [Parameter Tuning](#parameter-tuning)
6. [Testing dan Validasi](#testing-dan-validasi)

---

## 🏛️ Arsitektur Sistem

### Struktur Package

```
dev/
│
├── models/                 # Data models
│   ├── destination.py     # Model destinasi wisata
│   └── route.py           # Model rute wisata
│
├── utils/                 # Utility functions
│   ├── distance.py        # Perhitungan jarak
│   └── data_loader.py     # Loading dan preprocessing data
│
├── algorithms/            # Algoritma HGA
│   ├── chromosome.py      # Representasi solusi
│   ├── population.py      # Manajemen populasi
│   ├── operators.py       # Operator GA
│   ├── two_opt.py        # Local search
│   └── hga.py            # Main HGA algorithm
│
├── config.py             # Konfigurasi parameter
├── main.py               # Aplikasi utama
├── example.py            # Contoh penggunaan
└── data_wisata_sby.csv  # Data destinasi
```

---

## 📦 Penjelasan Modul

### 1. Models Package

#### `destination.py`

**Class: Destination**

- **Purpose**: Merepresentasikan satu destinasi wisata
- **Attributes**:
  - `nama`: Nama destinasi
  - `kategori`: List kategori (bisa multi-kategori)
  - `latitude`: Koordinat latitude
  - `longitude`: Koordinat longitude
- **Methods**:
  - `has_category()`: Mengecek apakah destinasi memiliki kategori tertentu

#### `route.py`

**Class: Route**

- **Purpose**: Merepresentasikan satu rute wisata lengkap
- **Attributes**:
  - `start_point`: Koordinat awal
  - `destinations`: List destinasi yang dikunjungi
  - `end_point`: Koordinat akhir
- **Methods**:
  - `calculate_total_distance()`: Hitung total jarak rute
  - `is_valid_route_order()`: Validasi urutan rute sesuai pola
  - `get_route_summary()`: Ringkasan rute dalam format dict

### 2. Utils Package

#### `distance.py`

**Function: calculate_distance()**

- **Purpose**: Menghitung jarak geodesik menggunakan Haversine formula
- **Formula**:
  ```
  a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
  c = 2 × atan2(√a, √(1-a))
  distance = R × c
  ```
  dimana R = 6371 km (radius bumi)

**Function: calculate_route_distance()**

- **Purpose**: Hitung total jarak untuk serangkaian titik

#### `data_loader.py`

**Function: load_destinations_from_csv()**

- **Purpose**: Load data dari CSV dan convert ke objek Destination
- **Handle**: Format koordinat dengan koma sebagai separator desimal
- **Error Handling**: Skip row yang invalid dengan logging

**Function: group_destinations_by_category()**

- **Purpose**: Mengelompokkan destinasi berdasarkan kategori
- **Return**: Dictionary dengan key kategori

### 3. Algorithms Package

#### `chromosome.py`

**Class: Chromosome**

- **Purpose**: Representasi genetik dari satu solusi rute
- **Attributes**:
  - `genes`: List destinasi (urutan kunjungan)
  - `start_point`: Titik awal
  - `end_point`: Titik akhir
  - `fitness_value`: Cache nilai fitness
- **Methods**:
  - `calculate_fitness()`: Fitness = 1/distance
  - `is_valid()`: Validasi constraint
  - `copy()`: Deep copy kromosom

**Design Pattern**: Value Object dengan caching

#### `population.py`

**Class: Population**

- **Purpose**: Manajemen koleksi kromosom
- **Key Methods**:
  - `initialize_random_population()`: Generate populasi awal valid
  - `_create_random_valid_chromosome()`: Generate kromosom yang memenuhi pola K-C-W
  - `evaluate_fitness()`: Evaluasi semua kromosom
  - `sort_by_fitness()`: Sorting untuk seleksi
  - `get_best_n_chromosomes()`: Ambil n terbaik

**Constraint Handling**:

- Memastikan setiap kromosom mengikuti pola K1→C1→W1→K2→W2→C2→K3→O
- Tidak ada duplikasi destinasi dalam kategori yang sama

#### `operators.py`

**Class: GAOperators**
Implementasi operator-operator Genetic Algorithm sebagai static methods.

**Seleksi:**

1. **Tournament Selection**

   - Pilih k individu random
   - Return yang fitness tertinggi
   - Parameter: tournament_size (default=5)

2. **Roulette Wheel Selection**
   - Probabilitas terpilih ∝ fitness
   - Simulasi roda roulette

**Crossover:**

1. **Order Crossover (OX)**

   - Pilih subset dari parent1
   - Isi sisanya dengan order dari parent2
   - Preserve relative order

2. **Position Based Crossover**
   - Pilih posisi random dari parent1
   - Isi sisanya dengan order dari parent2

**Mutasi:**

1. **Swap Mutation**

   - Tukar posisi dua gen random
   - Simple tapi efektif

2. **Inversion Mutation**

   - Reverse subset gen
   - Bisa mengubah urutan signifikan

3. **Scramble Mutation**
   - Acak subset gen
   - Lebih agresif dari swap

#### `two_opt.py`

**Class: TwoOptOptimizer**

- **Purpose**: Local search optimization untuk memperbaiki rute

**Algorithm:**

```
untuk setiap edge i:
    untuk setiap edge j (j > i+1):
        reverse segment antara i dan j
        jika jarak lebih pendek:
            simpan perubahan
            tandai ada improvement
        jika tidak ada improvement:
            stop
```

**Methods:**

1. `optimize()`: 2-Opt tanpa constraint
2. `optimize_with_constraints()`: 2-Opt yang mempertahankan pola K-C-W
   - Hanya swap dalam kategori yang sama

#### `hga.py`

**Class: HybridGeneticAlgorithm**

- **Purpose**: Main orchestrator untuk HGA

**Lifecycle:**

```
1. Initialize population
2. For each generation:
   a. Evaluate fitness
   b. Check convergence
   c. Selection
   d. Crossover
   e. Mutation
   f. Local search (2-Opt)
   g. Elitism
   h. Replace population
3. Return best solutions
```

**Key Methods:**

- `run()`: Main entry point
- `_create_new_generation()`: Generate offspring
- `_check_convergence()`: Deteksi konvergensi
- `get_evolution_statistics()`: Tracking metrics

---

## 🔄 Alur Algoritma HGA

### Pseudocode

```
FUNCTION HybridGeneticAlgorithm(destinations, start_point, end_point):
    // 1. Inisialisasi
    population = InitializePopulation(destinations, start_point, end_point)
    EvaluateFitness(population)

    best_solution = GetBest(population)

    // 2. Evolusi
    FOR generation = 1 TO max_generations:
        // 3. Evaluasi
        EvaluateFitness(population)
        SortByFitness(population)

        // Track best
        current_best = GetBest(population)
        IF current_best.fitness > best_solution.fitness:
            best_solution = current_best

        // 9. Konvergensi check
        IF CheckConvergence(generation):
            BREAK

        // 8. Generate populasi baru
        new_population = []

        // Elitism
        elites = GetBestN(population, elitism_count)
        new_population.ADD(elites)

        WHILE new_population.size < population_size:
            // 4. Seleksi
            parent1 = TournamentSelection(population)
            parent2 = TournamentSelection(population)

            // 5. Crossover
            IF random() < crossover_rate:
                offspring1, offspring2 = OrderCrossover(parent1, parent2)
            ELSE:
                offspring1, offspring2 = parent1, parent2

            // 6. Mutasi
            offspring1 = SwapMutation(offspring1, mutation_rate)
            offspring2 = SwapMutation(offspring2, mutation_rate)

            // 7. Local search
            IF use_2opt:
                offspring1 = TwoOptOptimize(offspring1)
                offspring2 = TwoOptOptimize(offspring2)

            new_population.ADD(offspring1)
            IF new_population.size < population_size:
                new_population.ADD(offspring2)

        population = new_population

    RETURN GetBestN(population, num_solutions)
```

---

## 🔧 Detail Implementasi

### Fitness Function

```python
def calculate_fitness(self):
    total_distance = self.calculate_total_distance()

    if total_distance == 0:
        return float('inf')

    # Minimize distance = maximize 1/distance
    fitness = 1.0 / total_distance

    return fitness
```

**Rationale**:

- Tujuan: Minimasi jarak
- GA: Maximasi fitness
- Solusi: Inverse relationship

### Constraint Handling

**Approach**: Constrained Initialization

- Generate hanya kromosom valid
- Tidak perlu penalty function
- Lebih efisien

**Pattern Enforcement**:

```python
pattern = [
    'makanan_berat',   # Position 0: K1
    'makanan_ringan',  # Position 1: C1
    'non_kuliner',     # Position 2: W1
    'makanan_berat',   # Position 3: K2
    'non_kuliner',     # Position 4: W2
    'makanan_ringan',  # Position 5: C2
    'makanan_berat',   # Position 6: K3
    'oleh_oleh'        # Position 7: O
]
```

### Diversity Maintenance

**Mechanisms**:

1. **Mutation**: Introduce random changes
2. **Tournament Selection**: Balanced selection pressure
3. **No Duplicates**: Hindari destinasi duplikat dalam kategori sama

---

## ⚙️ Parameter Tuning

### Population Size

- **Small (30-50)**: Fast, tapi mungkin premature convergence
- **Medium (100-150)**: Balanced
- **Large (200+)**: Better exploration, tapi slow

**Recommendation**: 100 untuk balanced performance

### Generations

- Tergantung convergence rate
- Monitor fitness history
- Early stopping jika konvergen

### Crossover Rate

- **High (0.8-0.9)**: More exploration
- **Low (0.6-0.7)**: More exploitation

**Recommendation**: 0.8

### Mutation Rate

- **High (>0.2)**: Terlalu random
- **Medium (0.1-0.15)**: Balanced
- **Low (<0.05)**: Mungkin terjebak local optimum

**Recommendation**: 0.1

### 2-Opt Iterations

- Trade-off: quality vs speed
- Diminishing returns setelah 50-100 iterations

**Recommendation**: 50

---

## 🧪 Testing dan Validasi

### Unit Testing Checklist

```python
# test_distance.py
def test_haversine_distance():
    # Test known distances
    pass

# test_chromosome.py
def test_fitness_calculation():
    pass

def test_valid_route_pattern():
    pass

# test_population.py
def test_population_initialization():
    # Semua kromosom valid?
    pass

# test_operators.py
def test_crossover_preserves_genes():
    pass

def test_mutation_maintains_validity():
    pass
```

### Integration Testing

```python
def test_hga_produces_valid_routes():
    hga = HybridGeneticAlgorithm(...)
    solutions = hga.run(...)

    for solution in solutions:
        assert solution.is_valid()
        assert len(solution.genes) == 8
```

### Performance Benchmarking

```python
import time

def benchmark_hga():
    configs = ['fast', 'balanced', 'quality']

    for config in configs:
        start = time.time()
        hga = HGA(**get_config(config))
        solutions = hga.run(...)
        elapsed = time.time() - start

        print(f"{config}: {elapsed:.2f}s, "
              f"best: {solutions[0].get_total_distance():.2f}km")
```

---

## 📊 Expected Performance

### Computational Complexity

- **Population Init**: O(n × m) where n=pop_size, m=num_destinations
- **Fitness Evaluation**: O(n × d) where d=8 (destinations per route)
- **Per Generation**: O(n² × d) for selection and operators
- **2-Opt**: O(d² × k) where k=iterations
- **Total**: O(g × n² × d) where g=generations

### Typical Results

**Dataset**: ~140 destinations in Surabaya
**Config**: Balanced preset

- **Runtime**: 30-60 seconds
- **Best Distance**: 30-50 km (tergantung lokasi user)
- **Convergence**: ~80-150 generations
- **Quality**: Top 3 solutions biasanya dalam 10% dari optimal

---

## 🎯 Best Practices

1. **Start Simple**: Gunakan preset 'fast' untuk prototyping
2. **Monitor Convergence**: Plot fitness history
3. **Validate Results**: Cek apakah rute masuk akal geografis
4. **Tune Gradually**: Ubah satu parameter at a time
5. **Use Elitism**: Always keep best solutions
6. **Enable 2-Opt**: Significant improvement untuk TSP-like problems

---

## 📚 References

1. **Genetic Algorithms**:
   - Holland, J. H. (1992). "Adaptation in Natural and Artificial Systems"
2. **2-Opt Algorithm**:
   - Croes, G. A. (1958). "A Method for Solving Traveling-Salesman Problems"
3. **Hybrid Approaches**:

   - Talbi, E. G. (2009). "Metaheuristics: From Design to Implementation"

4. **TSP Variants**:
   - Applegate, D. et al. (2006). "The Traveling Salesman Problem"

---

**Last Updated**: October 2025
**Version**: 1.0
