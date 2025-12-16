# RENCANA UJI COBA SISTEM REKOMENDASI RUTE WISATA DENGAN HYBRID GENETIC ALGORITHM

---

## 1. TUJUAN UJI COBA

### 1.1 Tujuan Utama

Uji coba sistem bertujuan untuk **memvalidasi bahwa Hybrid Genetic Algorithm (HGA) yang dikembangkan mampu menghasilkan solusi rute wisata yang optimal dengan memenuhi constraint yang ditetapkan dalam waktu komputasi yang reasonable untuk aplikasi real-time**.

### 1.2 Tujuan Spesifik

#### A. **Analisis Kualitas Solusi**

1. Mengukur **kualitas solusi** yang dihasilkan HGA (total jarak rute)
2. Menguji **sensitivitas semua parameter** HGA terhadap kualitas solusi:
   - Population size (ukuran populasi)
   - Generations (jumlah generasi)
   - Crossover rate (laju persilangan)
   - Mutation rate (laju mutasi)
   - Tournament size (ukuran tournament selection)
   - 2-Opt local search (enable/disable)
3. Menentukan **kombinasi parameter optimal** untuk menghasilkan solusi terbaik
4. Mengevaluasi **konsistensi** hasil antar eksekusi (reproducibility)

#### B. **Analisis Konvergensi Algoritma**

1. Menganalisis **kecepatan konvergensi** HGA (berapa generasi untuk mencapai solusi optimal/near-optimal)
2. Memetakan **kurva konvergensi** (fitness evolution over generations)
3. Mengukur **diversity preservation** populasi selama evolusi
4. Mengidentifikasi **titik konvergensi** dan risiko premature convergence

---

## 2. UJI COBA HGA (SIMPLIFIED)

### 2.1 Analisis Kualitas Solusi (Solution Quality Analysis)

**Tujuan:** Menguji pengaruh **setiap parameter HGA** terhadap kualitas solusi rute wisata yang dihasilkan, mengukur jarak total rute, dan menentukan parameter optimal dengan mempertimbangkan trade-off antara kualitas solusi dan waktu eksekusi.

---

#### Skenario 2.1.1: Pengujian Parameter Populasi

**Tujuan Spesifik:**
Mengukur apakah ukuran populasi yang lebih besar menghasilkan solusi dengan jarak yang lebih pendek, dan menentukan populasi optimal dengan mempertimbangkan trade-off waktu eksekusi.

**Parameter yang Diuji:**

- **Population Size**: [100, 300, 500, 700]
- **Parameter Tetap (Fixed)**:
  - Generations: 40
  - Crossover rate: 0.8
  - Mutation rate: 0.05
  - 2-Opt: Enabled (True)

**Prosedur Pengujian:**

```
Step 1: Preparation
---------------------------------------
1. Siapkan dataset: 221 destinasi wisata Surabaya
2. Pilih start point: Surabaya city center (-7.2575, 112.7521)
3. Set random seed: 42 (untuk reproducibility)
4. Validasi distance matrix: Pastikan semua jarak terkalkulasi

Step 2: Execution
---------------------------------------
Untuk setiap ukuran populasi [100, 300, 500, 700]:

  FOR population_size IN [100, 300, 500, 700]:
    FOR run IN [1..10]:  # 10 runs untuk statistical validity

      1. Initialize HGA dengan config:
         - population_size = population_size
         - generations = 40
         - crossover_rate = 0.8
         - mutation_rate = 0.05
         - use_2opt = True
         - random_seed = 42 + run

      2. Record start time: t_start = time.now()

      3. Run HGA:
         best_routes = hga.run(
             destinations=all_destinations,
             start_point=start_point,
             num_solutions=3,
             config=hga_config
         )

      4. Record end time: t_end = time.now()

      5. Collect metrics:
         - best_distance = best_routes[0].get_total_distance()
         - execution_time = t_end - t_start
         - is_valid = best_routes[0].is_valid()
         - all_distances = [route.distance for route in best_routes]

      6. Save result:
         results.append({
           'test_type': 'population',
           'population_size': population_size,
           'run_id': run,
           'best_distance': best_distance,
           'avg_distance': mean(all_distances),
           'execution_time': execution_time,
           'is_valid': is_valid
         })

Step 3: Data Analysis
---------------------------------------
1. Aggregate hasil per population size:

   SQL Query:
   SELECT
       population_size,
       AVG(best_distance) as avg_best_distance,
       MIN(best_distance) as min_distance,
       MAX(best_distance) as max_distance,
       STDDEV(best_distance) as std_distance,
       AVG(execution_time) as avg_time,
       STDDEV(execution_time) as std_time
   FROM results
   WHERE test_type = 'population'
   GROUP BY population_size
   ORDER BY population_size;

2. Statistical Test (ANOVA):
   - H0: Semua populasi menghasilkan rata-rata jarak yang sama
   - H1: Ada perbedaan signifikan antar populasi
   - Significance level: α = 0.05

3. Effect Size (Cohen's d):
   Hitung perbedaan praktis antara populasi 100 vs 700

4. Trade-off Analysis:
   Score = (quality_improvement × w1) - (time_increase × w2)
   w1 = 0.7 (weight untuk kualitas)
   w2 = 0.3 (weight untuk waktu)

Step 4: Visualization
---------------------------------------
1. Box Plot:
   - X-axis: Population size [100, 300, 500, 700]
   - Y-axis: Best distance (km)
   - Tampilkan median, quartiles, outliers

2. Line Plot (Dual Y-axis):
   - X-axis: Population size
   - Y-axis (left): Average best distance (km)
   - Y-axis (right): Average execution time (seconds)
   - Tampilkan trend dan trade-off point

3. Bar Chart dengan Error Bars:
   - X-axis: Population size
   - Y-axis: Average distance
   - Error bars: ±1 standard deviation

Step 5: Determine Optimal
---------------------------------------
Kriteria pemilihan populasi optimal:
1. Distance Quality: avg_distance < target (misal 32 km)
2. Consistency: std_distance < 2 km
3. Time Efficiency: avg_time < 60 seconds
4. Statistical Significance: p-value < 0.05
5. Diminishing Returns: improvement < 3% dari ukuran sebelumnya

Contoh Decision Logic:
IF (pop500_distance < pop300_distance × 0.97) AND (pop500_time < 60s):
    optimal_population = 500
ELSE IF (pop700_distance < pop500_distance × 0.97) AND (pop700_time < 90s):
    optimal_population = 700
ELSE:
    optimal_population = 300  # Balance quality & speed
```

**Expected Results (Hypothesis):**

| Population | Avg Distance (km) | Avg Time (s) | Improvement | Time Increase |
| ---------- | ----------------- | ------------ | ----------- | ------------- |
| 100        | 36-38             | 8-12         | Baseline    | Baseline      |
| 300        | 32-34             | 20-30        | ~12%        | 2.5x          |
| 500        | 30-32             | 35-50        | ~6%         | 1.7x          |
| 700        | 29-31             | 50-70        | ~3%         | 1.4x          |

**Interpretation:**

- **Populasi kecil (100)**: Kurang eksplorasi, premature convergence, solusi suboptimal
- **Populasi sedang (300-500)**: Balance eksplorasi/eksploitasi, good quality
- **Populasi besar (700)**: Marginal improvement, diminishing returns, high computational cost
- **Optimal**: Likely 500 (sweet spot antara kualitas dan efisiensi)

---

#### Skenario 2.1.2: Pengujian Parameter Generasi

**Tujuan Spesifik:**
Menentukan pada generasi ke berapa algoritma mencapai konvergensi (tidak ada improvement signifikan), sehingga dapat menghentikan iterasi tanpa membuang waktu komputasi.

**Parameter yang Diuji:**

- **Generations**: [20, 40, 80]
- **Parameter Tetap (Fixed)**:
  - Population size: 500 (dari hasil optimal Skenario 2.1.1)
  - Crossover rate: 0.8
  - Mutation rate: 0.05
  - 2-Opt: Enabled (True)

**Prosedur Pengujian:**

```
Step 1: Extended Tracking Setup
---------------------------------------
Modifikasi HGA untuk tracking per-generation:

class HGAWithTracking:
    def run_with_tracking(self, ...):
        history = {
            'generation': [],
            'best_fitness': [],
            'avg_fitness': [],
            'worst_fitness': [],
            'diversity': []
        }

        for generation in range(max_generations):
            # ... evolusi populasi ...

            # Track metrics per generasi
            history['generation'].append(generation)
            history['best_fitness'].append(population[0].fitness)
            history['avg_fitness'].append(mean(pop.fitness))
            history['worst_fitness'].append(population[-1].fitness)
            history['diversity'].append(
                std(pop.fitness) / mean(pop.fitness)
            )

        return best_solution, history

Step 2: Execution dengan Extended Generations
---------------------------------------
Jalankan HGA dengan max_generations = 80 untuk semua test:

FOR gen_limit IN [20, 40, 80]:
  FOR run IN [1..10]:

    1. Run HGA dengan max_generations = 80
       (tracking aktif untuk semua generasi)

    2. Ekstrak hasil pada generasi ke-20, 40, dan 80:
       - best_distance_at_gen20 = get_distance_at_generation(20)
       - best_distance_at_gen40 = get_distance_at_generation(40)
       - best_distance_at_gen80 = get_distance_at_generation(80)

    3. Detect convergence point:
       convergence_gen = detect_convergence(
           fitness_history,
           threshold=0.001,  # 0.1% improvement
           patience=20       # No improvement for 20 generations
       )

    4. Save results:
       results.append({
         'test_type': 'generation',
         'run_id': run,
         'distance_gen20': best_distance_at_gen20,
         'distance_gen40': best_distance_at_gen40,
         'distance_gen80': best_distance_at_gen80,
         'convergence_generation': convergence_gen,
         'time_gen20': time_at_generation(20),
         'time_gen40': time_at_generation(40),
         'time_gen80': time_at_generation(80),
         'history': fitness_history  # Simpan untuk plotting
       })

Step 3: Convergence Detection Algorithm
---------------------------------------
def detect_convergence(fitness_history, threshold=0.001, patience=20):
    """
    Detect when algorithm converges:
    - Improvement < threshold for 'patience' consecutive generations
    """
    for i in range(len(fitness_history) - patience):
        window = fitness_history[i:i+patience]
        improvement = (max(window) - min(window)) / min(window)

        if improvement < threshold:
            return i  # Converged at generation i

    return len(fitness_history)  # Never converged

Step 4: Data Analysis
---------------------------------------
1. Improvement Analysis:

   FOR each generation_limit [20, 40, 80]:
     improvement_from_previous = (
         (distance_prev_gen - distance_current_gen)
         / distance_prev_gen × 100
     )

   Example:
   - Gen 0→20: 45 km → 33 km = 26.7% improvement
   - Gen 20→40: 33 km → 31 km = 6.1% improvement
   - Gen 40→80: 31 km → 30.5 km = 1.6% improvement (diminishing!)

2. Convergence Statistics:

   SELECT
       AVG(convergence_generation) as avg_convergence,
       MIN(convergence_generation) as fastest_convergence,
       MAX(convergence_generation) as slowest_convergence,
       STDDEV(convergence_generation) as std_convergence
   FROM results
   WHERE test_type = 'generation';

3. Cost-Benefit Analysis:

   benefit = distance_improvement (%)
   cost = time_increase (%)

   efficiency_ratio = benefit / cost

   Example:
   - Gen 20→40: benefit=6.1%, cost=100%, ratio=0.061
   - Gen 40→80: benefit=1.6%, cost=100%, ratio=0.016

   → Gen 40 lebih efficient (higher ratio)

Step 5: Visualization
---------------------------------------
1. Convergence Curves (Line Plot):
   - X-axis: Generation (0-80)
   - Y-axis: Best fitness / Distance
   - Plot: 10 runs (dengan transparency)
   - Highlight: Average convergence curve (bold line)
   - Markers: Gen 20, 40, 80 (vertical dashed lines)

2. Improvement Chart (Bar Chart):
   - X-axis: Generation windows [0-20, 20-40, 40-80]
   - Y-axis: % Improvement
   - Annotations: Show actual distances

3. Convergence Distribution (Histogram):
   - X-axis: Convergence generation
   - Y-axis: Frequency (dari 10 runs)
   - Vertical line: Mean convergence generation

4. Diversity Evolution (Line Plot):
   - X-axis: Generation
   - Y-axis: Diversity index
   - Show: Diversity decreases over time
   - Annotation: Point where diversity < 0.05 (converged)

Step 6: Determine Optimal Generations
---------------------------------------
Kriteria pemilihan:
1. Convergence Achieved: 95% of runs converged
2. Sufficient Improvement: > 30% dari initial random
3. Diminishing Returns: improvement gen N→N+20 < 3%
4. Time Reasonable: avg_time < 60 seconds

Decision Logic:
IF (avg_convergence_gen <= 30):
    optimal_generations = 40  # Safety margin
ELSE IF (avg_convergence_gen <= 50):
    optimal_generations = 60
ELSE:
    optimal_generations = 80

Expected: optimal_generations = 40
```

**Expected Results (Hypothesis):**

| Generations | Avg Distance (km) | Improvement from Gen 0 | Marginal Improvement | Avg Time (s) |
| ----------- | ----------------- | ---------------------- | -------------------- | ------------ |
| 20          | 33-35             | ~25%                   | 25% (from init)      | 20-25        |
| 40          | 30-32             | ~32%                   | 7% (from gen 20)     | 40-50        |
| 80          | 29.5-31.5         | ~34%                   | 2% (from gen 40)     | 75-90        |

**Interpretation:**

- **Gen 20**: Belum konvergen, masih banyak improvement potential
- **Gen 40**: Sudah konvergen (~95% runs), solusi near-optimal
- **Gen 80**: Minimal improvement (< 2%), tidak worth computational cost
- **Optimal**: 40 generations (sufficient convergence, reasonable time)

---

#### Skenario 2.1.3: Pengujian Parameter Crossover Rate

**Tujuan Spesifik:**
Menentukan crossover rate optimal yang balance antara eksploitasi (recombination) dan preservasi (building block) untuk menghasilkan solusi terbaik.

**Parameter yang Diuji:**

- **Crossover Rate**: [0.6, 0.7, 0.8, 0.9]
- **Parameter Tetap (Fixed)**:
  - Population size: 500
  - Generations: 40
  - Mutation rate: 0.05
  - 2-Opt: Enabled (True)

**Prosedur Pengujian:**

```
Step 1: Execution
---------------------------------------
FOR crossover_rate IN [0.6, 0.7, 0.8, 0.9]:
  FOR run IN [1..10]:

    1. Initialize HGA dengan:
       config.crossover_rate = crossover_rate
       config.population_size = 500
       config.generations = 40
       config.mutation_rate = 0.05
       config.use_2opt = True

    2. Run HGA dan track:
       - best_distance
       - convergence_generation
       - number_of_crossovers_performed
       - execution_time

    3. Save results dengan crossover_rate sebagai key

Step 2: Data Analysis
---------------------------------------
1. Aggregate per crossover rate:

   SELECT
       crossover_rate,
       AVG(best_distance) as avg_distance,
       STDDEV(best_distance) as std_distance,
       AVG(convergence_generation) as avg_conv_gen,
       MIN(best_distance) as best_found
   FROM results
   WHERE test_type = 'crossover'
   GROUP BY crossover_rate
   ORDER BY crossover_rate;

2. Identify Pattern (Expected: Inverted U-curve):
   - Low rate (0.6): Insufficient recombination → slower convergence
   - Optimal (0.7-0.8): Balance exploitation & preservation
   - High rate (0.9): Too destructive → breaks good building blocks

3. Statistical Test (ANOVA + Tukey HSD):
   - Test if differences are statistically significant
   - Identify which pairs significantly different

Step 3: Visualization
---------------------------------------
1. Line Plot dengan Error Bars:
   - X-axis: Crossover rate [0.6, 0.7, 0.8, 0.9]
   - Y-axis: Average best distance (km)
   - Error bars: ±1 std
   - Marker: Highlight optimal point
   - Expected: Slight U-curve with minimum at 0.7-0.8

2. Box Plot Comparison:
   - X-axis: Crossover rate
   - Y-axis: Best distance distribution
   - Show: Median, quartiles, outliers

Step 4: Determine Optimal
---------------------------------------
Kriteria:
1. Lowest average distance
2. Low standard deviation (consistency)
3. Statistically significant better than others (p < 0.05)
4. Literature validation (GA standard 0.7-0.9)

Expected: optimal_crossover_rate = 0.8
```

**Expected Results (Hypothesis):**

| Crossover Rate | Avg Distance (km) | Std Dev | Convergence Gen | Interpretation                   |
| -------------- | ----------------- | ------- | --------------- | -------------------------------- |
| 0.6            | 31.5-33           | 1.8     | 45              | Slow, insufficient recombination |
| 0.7            | 30.5-32           | 1.5     | 38              | Good balance                     |
| 0.8            | 30-31.5           | 1.4     | 35              | **Optimal**                      |
| 0.9            | 30.5-32.5         | 1.9     | 40              | Too aggressive, breaks patterns  |

---

#### Skenario 2.1.4: Pengujian Parameter Mutation Rate

**Tujuan Spesifik:**
Menentukan mutation rate optimal yang menjaga diversity populasi tanpa terlalu disruptive, untuk menghindari premature convergence dan local optimum.

**Parameter yang Diuji:**

- **Mutation Rate**: [0.01, 0.05, 0.2, 0.5]
- **Parameter Tetap (Fixed)**:
  - Population size: 500
  - Generations: 40
  - Crossover rate: 0.8
  - 2-Opt: Enabled (True)

**Prosedur Pengujian:**

```
Step 1: Execution dengan Diversity Tracking
---------------------------------------
FOR mutation_rate IN [0.01, 0.05, 0.2, 0.5]:
  FOR run IN [1..10]:

    1. Run HGA dengan tracking tambahan:
       - best_distance
       - convergence_generation
       - diversity_at_gen_20 (early phase)
       - diversity_at_convergence
       - premature_convergence_detected (bool)

    2. Premature Convergence Detection:
       IF diversity < 0.05 AND generation < 25:
           premature_convergence_detected = True

Step 2: Data Analysis
---------------------------------------
1. Aggregate per mutation rate:

   SELECT
       mutation_rate,
       AVG(best_distance) as avg_distance,
       AVG(diversity_at_gen_20) as avg_diversity_early,
       AVG(convergence_generation) as avg_conv_gen,
       SUM(premature_convergence_detected) as premature_count
   FROM results
   WHERE test_type = 'mutation'
   GROUP BY mutation_rate
   ORDER BY mutation_rate;

2. Identify Pattern (Expected: U-shaped curve):
   - Very low (0.01): Premature convergence, lack diversity
   - Optimal (0.05): Balance diversity & convergence
   - High (0.2): Too random, slower convergence
   - Very high (0.5): Acts like random search, poor quality

Step 3: Visualization
---------------------------------------
1. U-Curve Plot:
   - X-axis: Mutation rate (log scale: 0.01, 0.05, 0.2, 0.5)
   - Y-axis: Average best distance
   - Expected: U-shaped with minimum at 0.05
   - Annotations: Mark "Too low" and "Too high" regions

2. Diversity Evolution (Multiple Lines):
   - X-axis: Generation
   - Y-axis: Diversity index
   - Lines: One per mutation rate
   - Show: Higher mutation → sustained diversity longer

3. Premature Convergence Bar Chart:
   - X-axis: Mutation rate
   - Y-axis: Count of premature convergence (out of 10 runs)
   - Highlight: Rate 0.01 likely shows premature convergence

Step 4: Determine Optimal
---------------------------------------
Kriteria:
1. Lowest average distance
2. No/minimal premature convergence
3. Diversity maintained until gen 25-30
4. Convergence achieved before gen 50

Expected: optimal_mutation_rate = 0.05
```

**Expected Results (Hypothesis):**

| Mutation Rate | Avg Distance (km) | Premature Conv. | Diversity@Gen20 | Interpretation               |
| ------------- | ----------------- | --------------- | --------------- | ---------------------------- |
| 0.01          | 32-34             | 6/10 runs       | 0.04            | **Premature convergence**    |
| 0.05          | 30-31.5           | 0/10 runs       | 0.12            | **Optimal balance**          |
| 0.2           | 31-33             | 0/10 runs       | 0.20            | Too disruptive, slower       |
| 0.5           | 33-36             | 0/10 runs       | 0.35            | **Too random**, poor quality |

---

#### Skenario 2.1.5: Pengujian 2-Opt Local Search

**Tujuan Spesifik:**
Mengukur kontribusi 2-Opt local search terhadap kualitas solusi HGA, memvalidasi "Hybrid" component dalam algoritma.

**Parameter yang Diuji:**

- **Use 2-Opt**: [False, True]
- **Parameter Tetap (Fixed)**:
  - Population size: 500
  - Generations: 40
  - Crossover rate: 0.8
  - Mutation rate: 0.05

**Prosedur Pengujian:**

```
Step 1: Execution (A/B Testing)
---------------------------------------
Configuration A (Pure GA - Without 2-Opt):
  FOR run IN [1..20]:  # More runs untuk robust comparison
    config.use_2opt = False
    result_A = run_hga(config)
    results_pure_ga.append(result_A)

Configuration B (HGA - With 2-Opt):
  FOR run IN [1..20]:
    config.use_2opt = True
    result_B = run_hga(config)
    results_hga.append(result_B)

Step 2: Paired Analysis
---------------------------------------
Karena menggunakan same random seeds, hasil dapat dipaired:

FOR i IN [1..20]:
    improvement = (
        (distance_without_2opt[i] - distance_with_2opt[i])
        / distance_without_2opt[i] × 100
    )

    improvements.append(improvement)

Step 3: Statistical Testing
---------------------------------------
1. Paired T-Test:
   - H0: 2-Opt tidak memberikan perbedaan (μ_diff = 0)
   - H1: 2-Opt memberikan improvement (μ_diff > 0)
   - Use: scipy.stats.ttest_rel()

2. Effect Size (Cohen's d):
   d = (mean_without_2opt - mean_with_2opt) / pooled_std

   Interpretation:
   - d > 0.8: Large effect (expected)
   - d = 0.5-0.8: Medium effect
   - d < 0.5: Small effect

3. Wilcoxon Signed-Rank Test (non-parametric alternative):
   - Jika data tidak normal distributed

Step 4: Visualization
---------------------------------------
1. Paired Bar Chart:
   - X-axis: Configuration [Pure GA, HGA]
   - Y-axis: Average distance (km)
   - Error bars: ±1 std
   - Annotations: Show % improvement

2. Before-After Plot (Paired Lines):
   - X-axis: [Without 2-Opt, With 2-Opt]
   - Y-axis: Distance (km)
   - Lines: Connect each paired run (20 lines)
   - Color: Green if improved, Red if worse
   - Expected: All/most lines slope downward (improvement)

3. Improvement Distribution (Histogram):
   - X-axis: % Improvement
   - Y-axis: Frequency
   - Stats: Mean improvement, median, std

Step 5: Determine Impact
---------------------------------------
Kriteria 2-Opt Effective:
1. Average improvement > 10%
2. p-value < 0.05 (statistically significant)
3. Effect size (Cohen's d) > 0.8 (large effect)
4. 90%+ runs show improvement

Expected:
- Average improvement: 15-20%
- All criteria met → 2-Opt is ESSENTIAL
```

**Expected Results (Hypothesis):**

| Configuration      | Avg Distance (km) | Min  | Max | Std Dev | Improvement |
| ------------------ | ----------------- | ---- | --- | ------- | ----------- |
| Pure GA (no 2-Opt) | 36-38             | 34   | 40  | 2.2     | Baseline    |
| HGA (with 2-Opt)   | 30-31.5           | 28.5 | 33  | 1.5     | **18-20%**  |

**Statistical Validation:**

- Paired t-test: p < 0.001 (highly significant)
- Cohen's d: 1.2-1.5 (very large effect)
- Wilcoxon: p < 0.001
- Improvement consistency: 19/20 runs (95%)

**Conclusion:**
2-Opt local search adalah **komponen penting** yang memberikan kontribusi terbesar (18-20%) terhadap kualitas solusi HGA, memvalidasi istilah "Hybrid" dalam Hybrid Genetic Algorithm.

**Metrik yang Diukur:**

```
1. Solution Quality Metrics
   - Average best distance (km): Mean dari 10 runs
   - Min distance (km): Best case dari 10 runs
   - Max distance (km): Worst case dari 10 runs
   - Std deviation (km): Konsistensi solusi

2. Execution Time
   - Average time (seconds): Mean waktu eksekusi
   - Time per generation: Avg time / generations

3. Success Rate
   - Valid routes (%): Percentage rute memenuhi constraint K,C,W,K,W,C,K,O
   - Constraint violations: Count duplikasi atau invalid pattern

4. Quality Score (Normalized)
   Score = (baseline_distance - current_distance) / baseline_distance × 100%
   → Percentage improvement terhadap baseline
```

**Test Procedure:**

````python
import itertools
import random
import numpy as np
from typing import Dict, List
import json

class ComprehensiveParameterTesting:
    """
    Comprehensive testing untuk SEMUA parameter HGA
    """

    def __init__(self):
        # Define parameter space
        self.param_space = {
            'population_size': [100, 300, 600, 1000],
            'generations': [20, 40, 80],
            'crossover_rate': [0.6, 0.7, 0.8, 0.9],
            'mutation_rate': [0.01, 0.03, 0.05, 0.08, 0.1],
            'tournament_size': [3, 5, 8, 12],
            'use_2opt': [True, False]
        }

        # Baseline configuration
-- Specific analysis untuk mutation rate
SELECT
    mutation_rate,
    AVG(best_distance) as avg_distance,
    STDDEV(best_distance) as std_distance,
    MIN(best_distance) as best_found,
    MAX(best_distance) as worst_found,
    COUNT(*) as n_runs
FROM experiment_results
GROUP BY mutation_rate
ORDER BY avg_distance ASC;

**Visualisasi Comprehensive:**

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def generate_comprehensive_visualizations(results_df, output_dir='plots'):
    """
    Generate semua visualisasi untuk analisis parameter
    """

    # 1. Parameter Sensitivity - All Parameters (6 subplots)
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Parameter Sensitivity Analysis - All HGA Parameters', fontsize=16)

    parameters = [
        'population_size', 'generations', 'crossover_rate',
        'mutation_rate', 'tournament_size', 'use_2opt'
    ]

    for idx, param in enumerate(parameters):
        ax = axes[idx // 3, idx % 3]

        # Extract parameter values from config
        param_values = results_df['config'].apply(lambda x: x[param])

        # Box plot per parameter value
        sns.boxplot(x=param_values, y=results_df['best_distance'], ax=ax)
        ax.set_title(f'Impact of {param}')
        ax.set_xlabel(param.replace('_', ' ').title())
        ax.set_ylabel('Distance (km)')
        ax.grid(True, alpha=0.3)

        # Rotate x labels if needed
        if param in ['population_size', 'generations']:
            ax.tick_params(axis='x', rotation=0)
        else:
            ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/all_parameters_sensitivity.png', dpi=300)
    plt.close()

    # 2. Population vs Generations Heatmap
    pivot = results_df.pivot_table(
        values='best_distance',
        index=results_df['config'].apply(lambda x: x['population_size']),
        columns=results_df['config'].apply(lambda x: x['generations']),
        aggfunc='mean'
    )

    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn_r',
                cbar_kws={'label': 'Average Distance (km)'})
    plt.title('Parameter Interaction: Population Size vs Generations')
    plt.xlabel('Generations')
    plt.ylabel('Population Size')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/population_generations_heatmap.png', dpi=300)
    plt.close()

    # 3. Crossover vs Mutation Heatmap
    pivot2 = results_df.pivot_table(
        values='best_distance',
        index=results_df['config'].apply(lambda x: x['crossover_rate']),
        columns=results_df['config'].apply(lambda x: x['mutation_rate']),
        aggfunc='mean'
    )

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot2, annot=True, fmt='.1f', cmap='RdYlGn_r',
                cbar_kws={'label': 'Average Distance (km)'})
    plt.title('Parameter Interaction: Crossover Rate vs Mutation Rate')
    plt.xlabel('Mutation Rate')
    plt.ylabel('Crossover Rate')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/crossover_mutation_heatmap.png', dpi=300)
    plt.close()

    # 4. Top 10 Configurations Comparison
    config_performance = results_df.groupby(
        results_df['config'].apply(str)
    )['best_distance'].agg(['mean', 'std'])

    top_10 = config_performance.sort_values('mean').head(10)

    plt.figure(figsize=(14, 8))
    x_pos = range(len(top_10))
    plt.barh(x_pos, top_10['mean'], xerr=top_10['std'],
             color='skyblue', edgecolor='navy', alpha=0.7)
    plt.yticks(x_pos, [f'Config {i+1}' for i in range(len(top_10))])
    plt.xlabel('Average Distance (km)')
    plt.title('Top 10 Best Configurations')
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/top_10_configurations.png', dpi=300)
    plt.close()

    # 5. Execution Time vs Quality Trade-off
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(
        results_df['execution_time'],
        results_df['best_distance'],
        c=results_df['config'].apply(lambda x: x['population_size']),
        s=100, alpha=0.6, cmap='viridis'
    )
    plt.colorbar(scatter, label='Population Size')
    plt.xlabel('Execution Time (seconds)')
    plt.ylabel('Distance (km)')
    plt.title('Quality vs Speed Trade-off')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/quality_vs_speed.png', dpi=300)
    plt.close()

    # 6. Distribution of Solution Quality
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.hist(results_df['best_distance'], bins=50, edgecolor='black', alpha=0.7)
    plt.xlabel('Distance (km)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Solution Quality')
    plt.grid(axis='y', alpha=0.3)

    plt.subplot(1, 2, 2)
    sns.violinplot(y=results_df['best_distance'], color='lightblue')
    plt.ylabel('Distance (km)')
    plt.title('Solution Quality Violin Plot')
    plt.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/solution_quality_distribution.png', dpi=300)
    plt.close()

    print(f"\nAll visualizations saved to {output_dir}/")
```         (-7.2459, 112.7378),  # Pusat
            (-7.3166, 112.7789),  # Timur
            (-7.2464, 112.6340),  # Barat
            (-7.2417, 112.7810),  # Utara
            (-7.3272, 112.6972)   # Selatan
        ]

        self.results = []

    def generate_ofat_configs(self) -> List[Dict]:
        """
        One-Factor-at-a-Time: Test satu parameter at a time
        """
        configs = [self.baseline.copy()]  # Include baseline

        for param_name, param_values in self.param_space.items():
            for value in param_values:
                if value != self.baseline[param_name]:
                    config = self.baseline.copy()
                    config[param_name] = value
                    configs.append(config)

        return configs

    def generate_random_configs(self, n_samples: int = 30) -> List[Dict]:
        """
        Random sampling dari parameter space
        """
        configs = []

        for _ in range(n_samples):
            config = {
                param: random.choice(values)
                for param, values in self.param_space.items()
            }
            configs.append(config)

        return configs

    def run_experiment(self, config: Dict, location: tuple, run_id: int):
        """
        Run single experiment dengan given config
        """
        import time

        start_time = time.time()

        # Set seed untuk reproducibility
        random.seed(run_id)
        np.random.seed(run_id)

        # Run HGA dengan config
        best_routes = hga.run(
            destinations=all_destinations,
            start_point=location,
            num_solutions=3,
            config=HGAConfig(**config)
        )

        execution_time = time.time() - start_time

        # Collect metrics
        result = {
            'config': config,
            'location': location,
            'run_id': run_id,
            'best_distance': best_routes[0].get_total_distance(),
            'execution_time': execution_time,
            'is_valid': best_routes[0].is_valid(),
            'all_routes': [r.get_total_distance() for r in best_routes]
        }

        return result

    def run_full_experiment(self):
        """
        Run complete experiment: OFAT + Random + Validation
        """
        print("=" * 70)
        print("COMPREHENSIVE PARAMETER TESTING - HGA")
        print("=" * 70)

        # Phase 1: OFAT Analysis
        print("\n[Phase 1] One-Factor-at-a-Time Analysis...")
        ofat_configs = self.generate_ofat_configs()
        print(f"Testing {len(ofat_configs)} OFAT configurations")

        for config_idx, config in enumerate(ofat_configs):
            print(f"\nConfig {config_idx+1}/{len(ofat_configs)}: {config}")

            for loc_idx, location in enumerate(self.locations):
                for run in range(10):
                    result = self.run_experiment(config, location, run)
                    self.results.append(result)
                    print(f"  Loc {loc_idx+1}, Run {run+1}: {result['best_distance']:.2f} km")

        # Phase 2: Random Search
        print("\n[Phase 2] Random Configuration Sampling...")
        random_configs = self.generate_random_configs(n_samples=30)
        print(f"Testing {len(random_configs)} random configurations")

        for config_idx, config in enumerate(random_configs):
            print(f"\nConfig {config_idx+1}/{len(random_configs)}: {config}")

            for loc_idx, location in enumerate(self.locations):
                for run in range(10):
                    result = self.run_experiment(config, location, run)
                    self.results.append(result)

        # Phase 3: Best Config Validation
        print("\n[Phase 3] Validating Top 3 Configurations...")
        top_configs = self.analyze_and_get_top_configs(n=3)

        for config_idx, config in enumerate(top_configs):
            print(f"\nValidating Config {config_idx+1}: {config}")

            for loc_idx, location in enumerate(self.locations):
                for run in range(30):  # More runs for validation
                    result = self.run_experiment(config, location, run)
                    self.results.append(result)

        # Save results
        self.save_results()

        # Generate analysis
        self.analyze_results()

    def analyze_and_get_top_configs(self, n: int = 3) -> List[Dict]:
        """
        Analyze results dan return top N configurations
        """
        import pandas as pd

        df = pd.DataFrame(self.results)

        # Group by config dan calculate average distance
        config_performance = df.groupby(
            df['config'].apply(lambda x: str(x))
        )['best_distance'].agg(['mean', 'std', 'min', 'max'])

        # Sort by mean distance (lower is better)
        config_performance = config_performance.sort_values('mean')

        # Get top N configs
        top_config_strings = config_performance.head(n).index.tolist()

        # Convert back to dict
        top_configs = []
        for config_str in top_config_strings:
            # Find original config dict
            for result in self.results:
                if str(result['config']) == config_str:
                    top_configs.append(result['config'])
                    break

        return top_configs

    def save_results(self):
        """Save results to JSON"""
        with open('comprehensive_parameter_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\nResults saved: {len(self.results)} experiment runs")

    def analyze_results(self):
        """Generate comprehensive analysis"""
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns

        df = pd.DataFrame(self.results)

        print("\n" + "=" * 70)
        print("COMPREHENSIVE ANALYSIS RESULTS")
        print("=" * 70)

        # Overall statistics
        print(f"\nTotal experiments: {len(df)}")
        print(f"Average distance: {df['best_distance'].mean():.2f} km")
        print(f"Best distance found: {df['best_distance'].min():.2f} km")
        print(f"Worst distance found: {df['best_distance'].max():.2f} km")
        print(f"Std deviation: {df['best_distance'].std():.2f} km")

        # Analyze each parameter
        for param in self.param_space.keys():
            print(f"\n--- Analysis: {param} ---")

            param_analysis = df.groupby(
                df['config'].apply(lambda x: x[param])
            )['best_distance'].agg(['mean', 'std', 'count'])

            print(param_analysis.sort_values('mean'))

            # Plot
            plt.figure(figsize=(10, 6))
            param_values = df['config'].apply(lambda x: x[param])
            sns.boxplot(x=param_values, y=df['best_distance'])
            plt.title(f'Impact of {param} on Solution Quality')
            plt.ylabel('Distance (km)')
            plt.xlabel(param)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'analysis_{param}.png', dpi=300)
            plt.close()

# Run experiment
tester = ComprehensiveParameterTesting()
tester.run_full_experiment()
````

**Analisis Statistik:**

```sql
-- SQL queries untuk analisis hasil

-- 1. General aggregation per configuration
SELECT
    config_name,
    AVG(best_distance) as avg_best_distance,
    MIN(best_distance) as min_distance,
    MAX(best_distance) as max_distance,
    STDDEV(best_distance) as stddev_distance,
    AVG(execution_time) as avg_time
FROM experiment_results
GROUP BY config_name
ORDER BY avg_best_distance ASC;

-- Specific analysis untuk crossover rate
SELECT
    crossover_rate,
    AVG(best_distance) as avg_distance,
    STDDEV(best_distance) as std_distance,
    COUNT(*) as n_runs
FROM experiment_results
WHERE population_size = 600 AND generations = 40 AND use_2opt = TRUE
GROUP BY crossover_rate
ORDER BY crossover_rate;

-- Specific analysis untuk mutation rate
SELECT
    mutation_rate,
    AVG(best_distance) as avg_distance,
    STDDEV(best_distance) as std_distance,
    AVG(convergence_generation) as avg_conv_gen
FROM experiment_results
WHERE population_size = 600 AND generations = 40 AND use_2opt = TRUE
GROUP BY mutation_rate
ORDER BY mutation_rate;
```

**Visualisasi untuk Crossover & Mutation:**

```python
import matplotlib.pyplot as plt
import numpy as np

# Plot 1: Crossover Rate Sensitivity
crossover_rates = [0.5, 0.6, 0.7, 0.8, 0.9]
avg_distances = [35.2, 32.8, 31.5, 31.0, 31.4]  # Example data

plt.figure(figsize=(10, 6))
plt.plot(crossover_rates, avg_distances, marker='o', linewidth=2, markersize=10)
plt.axvline(x=0.8, color='red', linestyle='--', alpha=0.5, label='Optimal')
plt.xlabel('Crossover Rate')
plt.ylabel('Average Distance (km)')
plt.title('Impact of Crossover Rate on Solution Quality')
plt.grid(True, alpha=0.3)
plt.legend()
plt.savefig('crossover_sensitivity.png', dpi=300)

# Plot 2: Mutation Rate Sensitivity (U-curve expected)
mutation_rates = [0.01, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2]
avg_distances = [34.2, 31.8, 31.0, 31.3, 32.1, 33.8, 35.5]  # Example data

plt.figure(figsize=(10, 6))
plt.plot(mutation_rates, avg_distances, marker='s', linewidth=2, markersize=10, color='orange')
plt.axvline(x=0.05, color='red', linestyle='--', alpha=0.5, label='Optimal')
plt.xlabel('Mutation Rate')
plt.ylabel('Average Distance (km)')
plt.title('Impact of Mutation Rate on Solution Quality (U-shaped Curve)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.savefig('mutation_sensitivity.png', dpi=300)
plt.show()
```

**Expected Results:**

```
Hypothesis Sub-test A (Population & Generations):
- Populasi lebih besar → solusi lebih baik (dengan diminishing returns)
  Expected: pop=100 (38km), pop=300 (33km), pop=600 (31km), pop=1000 (30.5km)
- Generasi lebih banyak → konvergensi lebih baik (plateau setelah 40-60)
  Expected: gen=20 (34km), gen=40 (31km), gen=80 (30.8km, marginal)

Hypothesis Sub-test B (Crossover Rate):
- Crossover rate optimal: 0.7-0.85
- Terlalu rendah (<0.6) → lambat converge, kurang exploitation
- Terlalu tinggi (>0.9) → destructive, memecah good building blocks
- Expected curve: U-shaped dengan minimum di 0.75-0.8
  Expected: 0.5 (35km), 0.6 (32.5km), 0.7 (31.2km), 0.8 (31.0km), 0.9 (31.5km)

Hypothesis Sub-test C (Mutation Rate):
- Mutation rate optimal: 0.03-0.08
- Terlalu rendah (<0.02) → premature convergence, lack diversity
- Terlalu tinggi (>0.15) → too disruptive, seperti random search
- Expected curve: U-shaped dengan minimum di 0.05
  Expected: 0.01 (34km, converged early), 0.03 (31.5km), 0.05 (31.0km),
           0.08 (31.2km), 0.1 (32km), 0.15 (33.5km), 0.2 (35km, too random)

Hypothesis Sub-test D (2-Opt):
- 2-Opt enabled → jarak lebih pendek (15-25% improvement)
- Expected: Without 2-Opt (38km), With 2-Opt (31km)
- This validates "Hybrid" dalam HGA

Statistical Validation:
- T-test untuk pairwise comparison (e.g., 0.8 vs 0.9 crossover)
- ANOVA untuk multiple group comparison
- Post-hoc test (Tukey HSD) untuk identify significant differences
- Effect size (Cohen's d) untuk measure practical significance
```

---

#### Skenario 2.2.2: Analisis Konvergensi

**Test Setup:**

```
Fixed Configuration:
- Population: 600
- Generations: 200 (extended untuk observasi penuh)
- Start point: Surabaya city center

Track per Generation:
- Best fitness
- Average fitness
- Worst fitness
- Population diversity
```

**Metrik yang Diukur:**

```
1. Convergence Rate
   - Generation ketika 95% final fitness tercapai
   - Generation ketika no improvement selama 20 generasi

2. Convergence Curve
   Plot: Generation (x-axis) vs Fitness (y-axis)

3. Diversity Metric
   Diversity(t) = σ(fitness at generation t) / μ(fitness at generation t)

   Interpretasi:
   - High diversity (>0.2): Population masih exploring
   - Low diversity (<0.05): Population converged
```

**Analisis:**

```python
# Detect convergence point
def detect_convergence(fitness_history, threshold=0.001):
    for i in range(len(fitness_history) - 20):
        window = fitness_history[i:i+20]
        improvement = (max(window) - min(window)) / min(window)
        if improvement < threshold:
            return i
    return len(fitness_history)

convergence_gen = detect_convergence(best_fitness_history)
print(f"Converged at generation: {convergence_gen}")
```

**Expected Results:**

```
Hypothesis:
- Konvergensi tercapai dalam 30-50 generasi
- 2-Opt mempercepat konvergensi (local refinement)
- Diversity menurun seiring generasi (natural selection)

Warning Signs:
- Premature convergence: Diversity drop <0.05 sebelum gen 20
- No convergence: Masih improving setelah gen 200
```

---

#### Skenario 2.2.3: Ablation Study (Analisis Kontribusi Komponen)

**Tujuan:** Mengukur kontribusi masing-masing komponen HGA

**Test Configurations:**

| Config       | Crossover | Mutation | 2-Opt | Elitism | Description           |
| ------------ | --------- | -------- | ----- | ------- | --------------------- |
| Baseline     | ❌        | ❌       | ❌    | ❌      | Random search only    |
| GA-Only      | ✅        | ✅       | ❌    | ✅      | Pure GA               |
| GA+2Opt      | ✅        | ✅       | ✅    | ✅      | Full HGA              |
| No-Mutation  | ✅        | ❌       | ✅    | ✅      | Test mutation impact  |
| No-Crossover | ❌        | ✅       | ✅    | ✅      | Test crossover impact |

**Test Setup:**

```
Fixed Parameters:
- Population: 600
- Generations: 40
- Runs: 20 per configuration
- Start point: Same for all configs
```

**Metrik Perbandingan:**

```
1. Solution Quality
   - Average best distance
   - Improvement over Baseline (%)

2. Convergence Speed
   - Generations to reach 95% final fitness

3. Computational Cost
   - Average execution time
   - Fitness evaluations per second
```

**Expected Results:**

```
Ranking (best to worst distance):
1. GA+2Opt (Full HGA) ← Best quality
2. GA-Only ← Good, slower convergence
3. No-Mutation ← Lack exploration
4. No-Crossover ← Poor diversity
5. Baseline ← Worst (random)

Impact Analysis:
- 2-Opt contribution: 15-25% distance reduction
- Crossover contribution: 30-40% improvement over random
- Mutation contribution: 5-10% (prevents stagnation)
```

---

## 3. METRIK EVALUASI

### 3.1 Metrik Kualitas Solusi (Solution Quality Metrics)

**Tujuan:** Mengukur performa sistem dan scalability

#### Skenario 2.3.1: Analisis Waktu Eksekusi

**Test Matrix:**

| Population | Generations | Expected Time | Max Acceptable |
| ---------- | ----------- | ------------- | -------------- |
| 100        | 20          | ~5s           | 10s            |
| 300        | 40          | ~15s          | 25s            |
| 600        | 40          | ~30s          | 45s            |
| 1000       | 40          | ~50s          | 70s            |
| 600        | 80          | ~60s          | 90s            |

**Test Procedure:**

```python
import time
import numpy as np

results = []

for pop_size in [100, 300, 600, 1000]:
    for generations in [20, 40, 80]:
        times = []
        for run in range(10):
            start = time.time()

            # Run HGA
            best_routes = hga.run(
                destinations=all_destinations,
                start_point=test_location,
                num_solutions=3,
                config=HGAConfig(
                    population_size=pop_size,
                    generations=generations
                )
            )

            elapsed = time.time() - start
            times.append(elapsed)

        results.append({
            'population': pop_size,
            'generations': generations,
            'avg_time': np.mean(times),
            'std_time': np.std(times),
            'min_time': np.min(times),
            'max_time': np.max(times)
        })
```

**Analisis Scalability:**

```python
# Linear regression untuk predict time complexity
from sklearn.linear_model import LinearRegression

X = [[r['population'], r['generations']] for r in results]
y = [r['avg_time'] for r in results]

model = LinearRegression()
model.fit(X, y)

print(f"Time ≈ {model.coef_[0]:.4f} × population + "
      f"{model.coef_[1]:.4f} × generations + {model.intercept_:.2f}")

# Expected: Time ≈ 0.0001 × pop × gen + constant
```

---

#### Skenario 2.3.2: Memory Profiling

**Test Setup:**

```python
import tracemalloc

tracemalloc.start()

# Snapshot awal
snapshot1 = tracemalloc.take_snapshot()

# Run HGA
best_routes = hga.run(destinations, start_point, num_solutions=3)

# Snapshot akhir
snapshot2 = tracemalloc.take_snapshot()

# Analisis memory usage
top_stats = snapshot2.compare_to(snapshot1, 'lineno')

for stat in top_stats[:10]:
    print(stat)
```

**Metrik:**

```
1. Peak Memory Usage
   - Maximum memory consumption during execution
   - Target: < 500 MB

2. Memory Allocation Rate
   - Objects created per second
   - Target: Consistent (no memory leak)

3. Memory by Component
   - Population: ~50 MB (600 chromosomes × 8 destinations)
   - Distance Matrix: ~20 MB (24,881 pairs)
   - Other: ~30 MB
   - Total: ~100 MB
```

---

#### Skenario 2.3.3: Profiling Bottleneck Analysis

**Tool:** cProfile

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run HGA
best_routes = hga.run(destinations, start_point, num_solutions=3)

profiler.disable()

# Analisis hasil
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

**Expected Hotspots:**

```
1. calculate_fitness() - 40-50% total time
   └─ calculate_total_distance() - 35-45%
      └─ get_distance() - 30-40%

2. order_crossover_modified() - 15-20%

3. optimize() (2-Opt) - 10-15%

4. tournament_selection() - 5-10%

5. swap_mutation() - 2-5%
```

**Optimization Opportunities:**

```
IF calculate_fitness > 50%:
   → Implement fitness caching lebih aggressive
   → Parallelize fitness evaluation

IF get_distance > 30%:
   → Verify distance matrix coverage
   → Cache key optimization

IF 2-opt > 15%:
   → Reduce max_iterations
   → Implement early stopping
```

---

### 2.4 Uji Coba Perbandingan Algoritma (Comparative Testing)

**Tujuan:** Membandingkan HGA dengan algoritma baseline

#### Skenario 2.4.1: Comparison dengan Random Search

**Algoritma Random Search:**

```python
def random_search(destinations, start_point, num_iterations=1000):
    best_route = None
    best_distance = float('inf')

    for _ in range(num_iterations):
        # Generate random valid route
        route = generate_random_valid_route(destinations, start_point)
        distance = route.calculate_total_distance()

        if distance < best_distance:
            best_distance = distance
            best_route = route

    return best_route
```

**Test Setup:**

```
Configurations:
1. Random Search: 24,000 evaluations (600 pop × 40 gen)
2. Pure GA: 600 pop, 40 gen, no 2-Opt
3. HGA (Proposed): 600 pop, 40 gen, with 2-Opt

Runs: 30 per algorithm
Start point: Same for all
```

**Expected Results:**

```
Algorithm         | Avg Distance | Std Dev | Avg Time | Win Rate
------------------|--------------|---------|----------|----------
Random Search     | 45-55 km     | 8-12 km | ~1s      | 0%
Pure GA           | 35-40 km     | 3-5 km  | ~20s     | 10-20%
HGA (Proposed)    | 28-35 km     | 2-4 km  | ~30s     | 70-90%

Statistical Test:
- Paired t-test: HGA vs GA (p < 0.05)
- Effect size (Cohen's d): > 0.8 (large effect)
```

---

#### Skenario 2.4.2: Comparison dengan Greedy Nearest Neighbor

**Algoritma Greedy:**

```python
def greedy_nearest_neighbor(destinations, start_point, constraints):
    route = []
    current_location = start_point

    for category in constraints:  # [K,C,W,K,W,C,K,O]
        # Filter destinations by category
        candidates = [d for d in destinations
                      if d.has_category(category)
                      and d not in route]

        # Pilih yang terdekat
        nearest = min(candidates,
                      key=lambda d: calculate_distance(current_location, d))

        route.append(nearest)
        current_location = (nearest.latitude, nearest.longitude)

    return route
```

**Expected Results:**

```
Algorithm            | Avg Distance | Consistency | Speed
---------------------|--------------|-------------|-------
Greedy NN            | 40-50 km     | ✓✓ (100%)   | ⚡⚡⚡ (<1s)
HGA (Proposed)       | 28-35 km     | ✓ (varies)  | ⚡ (~30s)

Trade-off Analysis:
- Greedy: Fast, consistent, tapi suboptimal (30-40% lebih panjang)
- HGA: Slower, tapi 30-40% lebih optimal

Use Case Recommendation:
- Greedy: Quick preview, draft planning
- HGA: Final recommendation, optimize travel cost
```

---

### 2.5 Uji Coba Parameter Tuning (Hyperparameter Testing)

**Tujuan:** Menemukan kombinasi parameter optimal

#### Skenario 2.5.1: Grid Search untuk Parameter Tuning

**Parameter Space:**

```python
param_grid = {
    'population_size': [100, 300, 600, 1000],
    'generations': [20, 40, 80],
    'crossover_rate': [0.6, 0.7, 0.8, 0.9],
    'mutation_rate': [0.01, 0.05, 0.1, 0.2],
    'tournament_size': [3, 5, 8, 12],
    'use_2opt': [True, False]
}

# Total combinations: 4 × 3 × 4 × 4 × 4 × 2 = 1,536 combinations
```

**Optimization Strategy: Random Search (Efficient Alternative)**

```python
import random

n_iterations = 50  # Sample 50 random combinations

results = []

for _ in range(n_iterations):
    config = {
        'population_size': random.choice([100, 300, 600, 1000]),
        'generations': random.choice([20, 40, 80]),
        'crossover_rate': random.uniform(0.6, 0.9),
        'mutation_rate': random.uniform(0.01, 0.2),
        'tournament_size': random.choice([3, 5, 8, 12]),
        'use_2opt': random.choice([True, False])
    }

    # Run 5 times untuk average
    distances = []
    times = []

    for run in range(5):
        best_route, exec_time = run_hga_with_config(config)
        distances.append(best_route.get_total_distance())
        times.append(exec_time)

    results.append({
        'config': config,
        'avg_distance': np.mean(distances),
        'avg_time': np.mean(times),
        'score': calculate_score(np.mean(distances), np.mean(times))
    })

# Sort by score (kombinasi distance dan time)
results.sort(key=lambda x: x['score'], reverse=True)

print("Top 5 Configurations:")
for i, result in enumerate(results[:5]):
    print(f"{i+1}. Distance: {result['avg_distance']:.2f} km, "
          f"Time: {result['avg_time']:.2f}s")
    print(f"   Config: {result['config']}")
```

**Score Function:**

```python
def calculate_score(distance, time,
                    distance_weight=0.7,
                    time_weight=0.3,
                    distance_target=30.0,
                    time_target=30.0):
    """
    Lower distance is better, lower time is better
    Normalize and combine into single score (0-1, higher is better)
    """
    distance_score = max(0, 1 - (distance - distance_target) / distance_target)
    time_score = max(0, 1 - (time - time_target) / time_target)

    return distance_weight * distance_score + time_weight * time_score
```

---

#### Skenario 2.5.2: Sensitivity Analysis

**Tujuan:** Memahami pengaruh setiap parameter terhadap hasil

**Test Procedure:**

```python
# Fix semua parameter kecuali satu yang divariasikan
baseline_config = {
    'population_size': 600,
    'generations': 40,
    'crossover_rate': 0.8,
    'mutation_rate': 0.05,
    'tournament_size': 8,
    'use_2opt': True
}

# Test impact of population_size
for pop_size in [50, 100, 200, 400, 600, 800, 1000]:
    config = baseline_config.copy()
    config['population_size'] = pop_size

    results = run_experiments(config, n_runs=10)
    plot_results(pop_size, results)
```

**Expected Insights:**

```
Parameter: population_size
Effect: Strong positive correlation dengan quality (diminishing returns)
Curve: Logarithmic improvement
Mechanism: Lebih banyak solutions explored per generation
Recommendation: 600 (sweet spot untuk quality/time balance)
Evidence: pop=100 (38km) vs pop=600 (31km) = 18% improvement
          pop=600 (31km) vs pop=1000 (30.5km) = only 1.6% improvement

Parameter: generations
Effect: Strong positive correlation up to 40-60, plateau after
Curve: Logarithmic with early plateau
Mechanism: Algorithm converges, no more improvement setelah plateau
Recommendation: 40 (sufficient untuk convergence)
Evidence: gen=20 (34km) vs gen=40 (31km) = 9% improvement
          gen=40 (31km) vs gen=80 (30.8km) = only 0.6% improvement

Parameter: crossover_rate
Effect: Moderate positive correlation dengan optimal range
Curve: Slightly U-shaped (optimal di 0.75-0.85)
Mechanism:
  - Too low (<0.6): Insufficient recombination, slow exploitation
  - Optimal (0.7-0.85): Balance building block preservation & exploration
  - Too high (>0.9): Destructive, breaks good partial solutions
Recommendation: 0.8 (standard GA literature)
Evidence: rate=0.6 (32.8km) vs rate=0.8 (31.0km) = 5.5% improvement
          rate=0.8 (31.0km) vs rate=0.9 (31.4km) = 1.3% worse (destructive)

Parameter: mutation_rate
Effect: Non-linear (U-shaped curve with minimum ~0.05)
Curve: U-shaped (high at extremes, low at optimal)
Mechanism:
  - Too low (<0.02): Population converges prematurely, stuck in local optimum
  - Optimal (0.03-0.08): Maintain diversity, escape local optima
  - Too high (>0.15): Too disruptive, acts like random search
Recommendation: 0.05 (5% genes mutated, standard practice)
Evidence: rate=0.01 (34.2km, premature) vs rate=0.05 (31.0km) = 9% improvement
          rate=0.05 (31.0km) vs rate=0.2 (35.5km) = 14% worse (too random)
Diversity impact: rate=0.01 (diversity drops to 0.03 at gen 15)
                  rate=0.05 (diversity maintained at 0.08 until gen 35)

Parameter: tournament_size
Effect: Moderate correlation dengan convergence speed
Curve: Linear positive (larger → faster, but less diverse)
Mechanism:
  - Small (k=3): Weak selection pressure, more diversity, slower convergence
  - Medium (k=5-8): Balance pressure & diversity
  - Large (k>12): Strong pressure, fast convergence, risk premature
Recommendation: 8 (balance untuk 600 population, ~1.3% selection pressure)
Evidence: k=3 (32.5km, gen 55 converge) vs k=8 (31.0km, gen 38 converge)
          k=8 (31.0km, gen 38) vs k=12 (31.2km, gen 28, premature)

Parameter: use_2opt
Effect: Very strong impact (15-25% distance reduction)
Curve: Binary switch with large effect
Mechanism: Local search refinement post-evolution
Recommendation: Always True (core component of "Hybrid" GA)
Evidence: 2opt=False (38km) vs 2opt=True (31km) = 18% improvement
          This is LARGEST single-component contribution
          Justifies calling it "Hybrid" Genetic Algorithm
```

---

### 2.6 Uji Coba Real-World Scenarios (User Experience Testing)

**Tujuan:** Validasi sistem dalam konteks penggunaan nyata

#### Skenario 2.6.1: Multi-Location Testing

**Test Locations (Diverse Surabaya Areas):**

```
1. Surabaya Pusat (Tugu Pahlawan)
   Lat: -7.2459, Lon: 112.7378
   Expected: Balanced routes ke semua area

2. Surabaya Timur (Rungkut)
   Lat: -7.3166, Lon: 112.7789
   Expected: Prioritas destinasi Surabaya Timur

3. Surabaya Barat (Benowo)
   Lat: -7.2464, Lon: 112.6340
   Expected: Prioritas destinasi Surabaya Barat

4. Surabaya Utara (Kenjeran)
   Lat: -7.2417, Lon: 112.7810
   Expected: Include destinasi pesisir

5. Surabaya Selatan (Wiyung)
   Lat: -7.3272, Lon: 112.6972
   Expected: Cluster destinasi selatan
```

**Evaluation Criteria:**

```
1. Route Locality
   - Measure: Average distance from start point
   - Expected: Routes closer to start point preferred

2. Route Compactness
   - Measure: Ratio of total distance to convex hull perimeter
   - Expected: Compact routes (ratio < 2.0)

3. Geographical Balance
   - Measure: Variance of destination locations
   - Expected: Low variance (destinations clustered)
```

---

#### Skenario 2.6.2: Multiple Solutions Diversity

**Test Setup:**

```python
# Generate 3 solusi
routes = hga.run(destinations, start_point, num_solutions=3)

# Measure diversity
def calculate_route_similarity(route1, route2):
    """
    Jaccard similarity: |intersection| / |union|
    """
    set1 = set(route1.destinations)
    set2 = set(route2.destinations)

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union

# Calculate pairwise similarities
similarities = []
for i in range(len(routes)):
    for j in range(i+1, len(routes)):
        sim = calculate_route_similarity(routes[i], routes[j])
        similarities.append(sim)

avg_similarity = np.mean(similarities)
print(f"Average similarity: {avg_similarity:.2f}")
```

**Expected Results:**

```
Similarity Score Interpretation:
- 0.0-0.3: Highly diverse (minimal overlap) ✓ IDEAL
- 0.3-0.5: Moderate diversity ✓ ACCEPTABLE
- 0.5-0.7: Low diversity ⚠ WARNING
- 0.7-1.0: Almost identical ❌ POOR

Target: Average similarity < 0.4

If similarity > 0.5:
  → Increase mutation rate
  → Increase population diversity
  → Use different random seeds
```

---

#### Skenario 2.6.3: Category Distribution Analysis

**Test:**

```python
def analyze_category_distribution(routes):
    """
    Analyze apakah kategori terdistribusi dengan baik
    atau selalu pilih destinasi populer yang sama
    """
    category_positions = {
        'K1': 0, 'C1': 1, 'W1': 2,
        'K2': 3, 'W2': 4, 'C2': 5,
        'K3': 6, 'O': 7
    }

    destination_frequency = {}

    for route in routes:
        for pos_name, pos_idx in category_positions.items():
            dest = route.destinations[pos_idx]
            key = (pos_name, dest.nama)

            destination_frequency[key] = destination_frequency.get(key, 0) + 1

    # Analyze diversity per position
    for pos_name in category_positions.keys():
        pos_dests = [k for k, v in destination_frequency.items()
                     if k[0] == pos_name]

        unique_count = len(pos_dests)
        max_freq = max([destination_frequency[k] for k in pos_dests])

        print(f"{pos_name}: {unique_count} unique destinations, "
              f"max frequency: {max_freq}")
```

**Expected Results:**

```
Position | Expected Unique | Expected Max Freq
---------|----------------|------------------
K1       | 8-12           | ≤ 15 (of 30 runs)
C1       | 6-10           | ≤ 15
W1       | 8-12           | ≤ 15
K2       | 8-12           | ≤ 15
W2       | 8-12           | ≤ 15
C2       | 6-10           | ≤ 15
K3       | 8-12           | ≤ 15
O        | 5-8            | ≤ 15

Interpretation:
- Good diversity: Multiple destinations muncul dengan frekuensi seimbang
- Poor diversity: 1-2 destinations dominan (always selected)

If poor diversity detected:
  → Check constraint filtering (mungkin terlalu strict)
  → Verify destination data quality
  → Increase exploration (higher mutation, larger tournament)
```

---

### 3.1 Metrik Kualitas Solusi

| Metrik                      | Formula                               | Target  | Interpretasi             |
| --------------------------- | ------------------------------------- | ------- | ------------------------ |
| **Total Distance**          | `Σ d(i, i+1)`                         | < 35 km | Lower is better          |
| **Distance Deviation**      | `σ(distances)`                        | < 5 km  | Consistency across runs  |
| **Optimality Gap**          | `(current - best_known) / best_known` | < 10%   | How far from optimal     |
| **Constraint Satisfaction** | `valid_routes / total_routes`         | 100%    | All routes must be valid |

### 3.2 Metrik Efisiensi Algoritma

| Metrik                     | Formula                         | Target    | Interpretasi                     |
| -------------------------- | ------------------------------- | --------- | -------------------------------- |
| **Convergence Generation** | Gen when 95% fitness reached    | < 35      | Faster is better                 |
| **Fitness Evaluations**    | `population_size × generations` | ~24,000   | Computational cost               |
| **Improvement Rate**       | `(final - initial) / initial`   | > 40%     | Algorithm effectiveness          |
| **Diversity Preservation** | `σ(fitness) / μ(fitness)`       | 0.05-0.15 | Balance exploration/exploitation |

---

## 4. PROSEDUR EKSPERIMEN SISTEMATIS

### 4.1 Preparation Phase

```
1. Environment Setup
   □ Python 3.11+ installed
   □ All dependencies installed (requirements.txt)
   □ Distance matrix pre-calculated (24,881 pairs)
   □ Data validation: 221 destinations loaded correctly

2. Hardware Specification
   □ CPU: Document processor model and cores
   □ RAM: Document available memory
   □ Storage: SSD preferred untuk fast I/O
   □ Network: Stable connection untuk OSRM fallback

3. Software Configuration
   □ Disable unnecessary background processes
   □ Set consistent random seeds untuk reproducibility
   □ Configure logging untuk detailed tracking
   □ Prepare data storage untuk results

4. Test Data Preparation
   □ Select 10 diverse start points
   □ Prepare baseline solutions (greedy, random)
   □ Validate destination data integrity
```

### 4.2 Execution Phase

```python
# Standard experiment template
import json
import numpy as np
from datetime import datetime

class ExperimentRunner:
    def __init__(self, output_dir="experiment_results"):
        self.output_dir = output_dir
        self.results = []

    def run_experiment(self, name, config, start_points, n_runs=10):
        """
        Run systematic experiment dengan multiple runs
        """
        experiment_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"Starting experiment: {experiment_id}")
        print(f"Configuration: {config}")
        print(f"Number of runs: {n_runs}")

        for start_idx, start_point in enumerate(start_points):
            print(f"\nTesting start point {start_idx+1}/{len(start_points)}")

            for run in range(n_runs):
                print(f"  Run {run+1}/{n_runs}...", end=" ")

                # Set random seed untuk reproducibility
                random.seed(run)
                np.random.seed(run)

                # Run HGA
                start_time = time.time()

                best_routes = hga.run(
                    destinations=all_destinations,
                    start_point=start_point,
                    num_solutions=3,
                    config=config
                )

                execution_time = time.time() - start_time

                # Collect results
                result = {
                    'experiment_id': experiment_id,
                    'config': config.__dict__,
                    'start_point': start_point,
                    'run': run,
                    'execution_time': execution_time,
                    'routes': [
                        {
                            'rank': i+1,
                            'distance': route.get_total_distance(),
                            'fitness': route.get_fitness(),
                            'is_valid': route.is_valid(),
                            'destinations': [d.nama for d in route.destinations]
                        }
                        for i, route in enumerate(best_routes)
                    ]
                }

                self.results.append(result)
                print(f"Distance: {best_routes[0].get_total_distance():.2f} km")

        # Save results
        self.save_results(experiment_id)

        # Generate summary
        self.print_summary(experiment_id)

    def save_results(self, experiment_id):
        """Save hasil ke JSON file"""
        filename = f"{self.output_dir}/{experiment_id}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {filename}")

    def print_summary(self, experiment_id):
        """Print statistical summary"""
        exp_results = [r for r in self.results
                       if r['experiment_id'] == experiment_id]

        distances = [r['routes'][0]['distance'] for r in exp_results]
        times = [r['execution_time'] for r in exp_results]

        print("\n" + "="*60)
        print(f"EXPERIMENT SUMMARY: {experiment_id}")
        print("="*60)
        print(f"Total runs: {len(exp_results)}")
        print(f"\nDistance (km):")
        print(f"  Mean:   {np.mean(distances):.2f} ± {np.std(distances):.2f}")
        print(f"  Median: {np.median(distances):.2f}")
        print(f"  Min:    {np.min(distances):.2f}")
        print(f"  Max:    {np.max(distances):.2f}")
        print(f"\nExecution Time (s):")
        print(f"  Mean:   {np.mean(times):.2f} ± {np.std(times):.2f}")
        print(f"  Median: {np.median(times):.2f}")
        print(f"  Min:    {np.min(times):.2f}")
        print(f"  Max:    {np.max(times):.2f}")
        print("="*60)
```

### 4.3 Analysis Phase

```python
# Statistical analysis template
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

class ExperimentAnalyzer:
    def __init__(self, results_file):
        with open(results_file) as f:
            self.data = json.load(f)
        self.df = self._convert_to_dataframe()

    def _convert_to_dataframe(self):
        """Convert JSON results to pandas DataFrame"""
        rows = []
        for result in self.data:
            row = {
                'experiment_id': result['experiment_id'],
                'run': result['run'],
                'execution_time': result['execution_time'],
                'best_distance': result['routes'][0]['distance'],
                'best_fitness': result['routes'][0]['fitness'],
                'is_valid': result['routes'][0]['is_valid'],
                **result['config']  # Unpack config parameters
            }
            rows.append(row)
        return pd.DataFrame(rows)

    def compare_configurations(self, config_column='population_size'):
        """Compare different configurations"""
        grouped = self.df.groupby(config_column)['best_distance']

        print(f"\nComparison by {config_column}:")
        print(grouped.describe())

        # Statistical test
        groups = [group for name, group in grouped]
        f_stat, p_value = stats.f_oneway(*groups)

        print(f"\nANOVA Test:")
        print(f"  F-statistic: {f_stat:.4f}")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Significant: {'Yes' if p_value < 0.05 else 'No'}")

        # Visualization
        plt.figure(figsize=(10, 6))
        self.df.boxplot(column='best_distance', by=config_column)
        plt.title(f'Distance Distribution by {config_column}')
        plt.ylabel('Total Distance (km)')
        plt.suptitle('')  # Remove default title
        plt.savefig(f'comparison_{config_column}.png')
        print(f"Plot saved: comparison_{config_column}.png")

    def plot_convergence(self, fitness_history):
        """Plot convergence curve"""
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        plt.plot(fitness_history['best'], label='Best', linewidth=2)
        plt.plot(fitness_history['avg'], label='Average', alpha=0.7)
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.title('Fitness Evolution')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.subplot(1, 2, 2)
        diversity = np.array(fitness_history['std']) / np.array(fitness_history['avg'])
        plt.plot(diversity, color='orange', linewidth=2)
        plt.xlabel('Generation')
        plt.ylabel('Diversity Index')
        plt.title('Population Diversity')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('convergence_analysis.png')
        print("Convergence plot saved: convergence_analysis.png")
```

---

## 5. DOKUMENTASI HASIL

### 5.1 Struktur Laporan Eksperimen

````markdown
# LAPORAN HASIL UJI COBA SISTEM REKOMENDASI RUTE WISATA

## 1. RINGKASAN EKSEKUTIF

- Tujuan uji coba
- Metodologi singkat
- Temuan utama (3-5 poin)
- Rekomendasi

## 2. METODOLOGI

- Environment setup
- Parameter configurations tested
- Test scenarios
- Metrik evaluasi

## 3. HASIL UJI COBA FUNGSIONAL

- Validasi constraint
- Validasi perhitungan jarak
- API endpoint testing
- Screenshots/logs

## 4. HASIL UJI COBA PERFORMA

- Kualitas solusi (tabel + grafik)
- Analisis konvergensi (convergence curves)
- Ablation study results
- Statistical significance tests

## 5. STRUKTUR LAPORAN HASIL UJI COBA

### 5.1 Format Laporan

````markdown
# BAB IV: HASIL DAN PEMBAHASAN

## 4.1 Analisis Kualitas Solusi

### 4.1.1 Hasil Pengujian Semua Parameter

- Tabel summary: parameter values vs average distance
- Box plot semua parameter (6 subplots)
- Heatmap: Population vs Generations
- Heatmap: Crossover vs Mutation
- Top 10 best configurations

### 4.1.2 Analisis Parameter Individual

**A. Population Size**

- Tabel hasil: [100, 300, 600, 1000] vs distance
- Plot: Distance vs Population Size
- Interpretation: Logarithmic improvement with diminishing returns
- Optimal value: 600 (balance quality/time)

**B. Generations**

- Tabel hasil: [20, 40, 80] vs distance
- Plot: Distance vs Generations
- Interpretation: Early plateau after 40 generations
- Optimal value: 40 (sufficient convergence)

**C. Crossover Rate**

- Tabel hasil: [0.6, 0.7, 0.8, 0.9] vs distance
- Plot: Distance vs Crossover Rate (U-curve expected)
- Interpretation: Balance recombination vs preservation
- Optimal value: 0.8 (standard GA practice validated)

**D. Mutation Rate**

- Tabel hasil: [0.01, 0.03, 0.05, 0.08, 0.1] vs distance
- Plot: Distance vs Mutation Rate (U-curve expected)
- Interpretation: Balance exploration vs convergence
- Optimal value: 0.05 (5% gene mutation optimal)

**E. Tournament Size**

- Tabel hasil: [3, 5, 8, 12] vs distance
- Plot: Distance vs Tournament Size
- Interpretation: Higher pressure → faster convergence
- Optimal value: 8 (balanced selection pressure)

**F. 2-Opt Local Search**

- Tabel hasil: [False, True] vs distance
- Bar chart comparison
- Interpretation: 18% improvement with 2-Opt
- Decision: ALWAYS enable (core "Hybrid" component)

### 4.1.3 Konfigurasi Optimal

```json
{
  "population_size": 600,
  "generations": 40,
  "crossover_rate": 0.8,
  "mutation_rate": 0.05,
  "tournament_size": 8,
  "use_2opt": true
}
```
````
````

- Average distance: 30.5 km
- Best distance: 28.2 km
- Execution time: 32 seconds
- Success rate: 100%

---

## 4.2 Analisis Konvergensi HGA

### 4.2.1 Pola Konvergensi

- Convergence curves (3 configurations)
- Table: Convergence generation per config
- Diversity evolution plot
- Phase identification: Exploration → Exploitation → Fine-tuning

### 4.2.2 Kecepatan Konvergensi

- Baseline config: Converges at gen ~50
- Fast config: Converges at gen ~30 (risk premature)
- Slow config: Converges at gen ~80 (safer but slower)

### 4.2.3 Diversity Preservation

- Plot: Diversity vs Generation
- Healthy diversity: >0.15 at gen 20
- Convergence: <0.05 at gen 60
- No premature convergence detected

---

## 4.3 Validasi Statistik

### 4.3.1 ANOVA Test Results

- F-statistic: 245.32 (p < 0.001) → All parameters significant
- Post-hoc Tukey HSD: Pairwise comparisons
- Effect sizes (Cohen's d):
  - Population 100→600: d = 1.2 (large)
  - 2-Opt OFF→ON: d = 1.5 (very large)
  - Mutation 0.01→0.05: d = 0.9 (large)

### 4.3.2 Consistency Analysis

- Standard deviation: 1.8 km (good reproducibility)
- Coefficient of variation: 5.9% (acceptable)
- 95% confidence interval: [29.2, 31.8] km

---

## 4.4 Diskusi

### 4.4.1 Interpretasi Hasil

- Parameter sensitivity validated
- Optimal configuration identified
- HGA outperforms pure GA by 18% (2-Opt contribution)
- Convergence behavior healthy (no premature convergence)

### 4.4.2 Perbandingan dengan Literatur

- Population size optimal at 600 (consistent with literature)
- Mutation rate 0.05 matches GA best practices
- Crossover rate 0.8 standard in academic papers
- 2-Opt contribution (18%) similar to other TSP studies (15-25%)

### 4.4.3 Limitasi

- Testing pada single city (Surabaya)
- 2,750 total runs (not exhaustive grid search)
- Execution time 30s may be acceptable for real-time usage

### 4.4.4 Kontribusi Penelitian

1. Comprehensive parameter sensitivity analysis (6 parameters)
2. Validated 2-Opt contribution to TSP quality
3. Identified optimal HGA configuration for tourism routing
4. Demonstrated HGA effectiveness for real-world application

---

## 4.5 Kesimpulan Uji Coba

- HGA successfully generates optimal tourism routes
- All 6 parameters show statistically significant impact
- Optimal configuration reduces distance by 39% from random
- 2-Opt is the largest contributor (18% improvement)
- Convergence achieved within 40-60 generations
- System ready for production deployment

````

### 5.2 Visualisasi yang Diperlukan

```python
# Generate comprehensive visualizations
import matplotlib.pyplot as plt
import seaborn as sns

def generate_all_plots(results_df, output_dir="plots"):
    """Generate all visualization untuk laporan"""

    # 1. Distance distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(results_df['best_distance'], bins=30, kde=True)
    plt.xlabel('Total Distance (km)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Solution Quality')
    plt.savefig(f'{output_dir}/distance_distribution.png', dpi=300)
    plt.close()

    # 2. Time vs Distance scatter
    plt.figure(figsize=(10, 6))
    plt.scatter(results_df['execution_time'], results_df['best_distance'],
                alpha=0.6, s=100)
    plt.xlabel('Execution Time (seconds)')
    plt.ylabel('Total Distance (km)')
    plt.title('Quality vs Speed Trade-off')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{output_dir}/quality_vs_speed.png', dpi=300)
    plt.close()

    # 3. Parameter sensitivity heatmap
    pivot = results_df.pivot_table(
        values='best_distance',
        index='population_size',
        columns='generations',
        aggfunc='mean'
    )

    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn_r',
                cbar_kws={'label': 'Average Distance (km)'})
    plt.title('Parameter Sensitivity: Population Size vs Generations')
    plt.savefig(f'{output_dir}/parameter_heatmap.png', dpi=300)
    plt.close()

    # 4. Box plot comparison
    plt.figure(figsize=(12, 6))
    results_df.boxplot(column='best_distance',
                       by=['use_2opt'],
                       figsize=(8, 6))
    plt.ylabel('Total Distance (km)')
    plt.xlabel('2-Opt Enabled')
    plt.title('Impact of 2-Opt Local Search')
    plt.suptitle('')
    plt.savefig(f'{output_dir}/2opt_impact.png', dpi=300)
    plt.close()

    print(f"All plots saved to {output_dir}/")
````

---

## 6. CHECKLIST UJI COBA (SIMPLIFIED)

### Phase 1: Preparation ✓

- [ ] Environment setup (Python, dependencies)
- [ ] Data validation (221 destinations)
- [ ] Distance matrix pre-calculation
- [ ] Hardware specification documentation
- [ ] Experiment scripts preparation
- [ ] Random seed configuration

### Phase 2: Solution Quality Analysis ✓

- [ ] OFAT Analysis (16 configurations × 5 locations × 10 runs = 800 runs)

  - [ ] Test Population Size [100, 300, 600, 1000]
  - [ ] Test Generations [20, 40, 80]
  - [ ] Test Crossover Rate [0.6, 0.7, 0.8, 0.9]
  - [ ] Test Mutation Rate [0.01, 0.03, 0.05, 0.08, 0.1]
  - [ ] Test Tournament Size [3, 5, 8, 12]
  - [ ] Test 2-Opt [True, False]

- [ ] Random Search (30 configurations × 5 locations × 10 runs = 1,500 runs)

  - [ ] Generate 30 random parameter combinations
  - [ ] Execute experiments
  - [ ] Collect results

- [ ] Best Config Validation (3 configurations × 5 locations × 30 runs = 450 runs)

  - [ ] Identify top 3 configurations
  - [ ] Extended validation runs (30 each)
  - [ ] Statistical validation

- [ ] Results Analysis
  - [ ] Generate box plots (all parameters)
  - [ ] Create heatmaps (parameter interactions)
  - [ ] Identify optimal configuration
  - [ ] ANOVA statistical tests
  - [ ] Effect size calculations

### Phase 3: Convergence Analysis ✓

- [ ] Baseline Config Convergence (10 runs)

  - [ ] Track fitness evolution (gen 0-200)
  - [ ] Measure diversity preservation
  - [ ] Identify convergence generation

- [ ] Fast Config Convergence (10 runs)

  - [ ] High pressure configuration
  - [ ] Observe premature convergence risk

- [ ] Slow Config Convergence (10 runs)

  - [ ] Low pressure configuration
  - [ ] Observe exploration patterns

- [ ] Results Analysis
  - [ ] Generate convergence curves
  - [ ] Diversity evolution plots
  - [ ] Compare convergence speeds
  - [ ] Identify optimal convergence pattern

### Phase 4: Statistical Validation ✓

- [ ] ANOVA testing (all parameters)
- [ ] Post-hoc Tukey HSD tests
- [ ] Cohen's d effect sizes
- [ ] Confidence interval calculations
- [ ] Reproducibility assessment (CV < 10%)

### Phase 5: Documentation ✓

- [ ] Generate all visualizations (15+ plots)
- [ ] Create comprehensive tables
- [ ] Write analysis report
- [ ] Document optimal configuration
- [ ] Prepare presentation materials
- [ ] Archive all raw data

---

## 7. TIMELINE ESTIMASI (SIMPLIFIED)

```
Week 1: Preparation & Setup
├─ Day 1-2: Environment setup, data validation
├─ Day 3-4: Distance matrix calculation
├─ Day 5-6: Implement experiment framework
└─ Day 7: Test run & validation

Week 2: Solution Quality Analysis (OFAT)
├─ Day 1-2: Population & Generations testing (800 runs)
├─ Day 3-4: Crossover & Mutation testing
├─ Day 5-6: Tournament & 2-Opt testing
└─ Day 7: Preliminary analysis

Week 3: Random Search & Validation
├─ Day 1-3: Random search (1,500 runs)
├─ Day 4-5: Identify top configurations
├─ Day 6-7: Extended validation (450 runs)

Week 4: Convergence Analysis
├─ Day 1-2: Baseline config convergence
├─ Day 3: Fast & slow config convergence
├─ Day 4-5: Convergence analysis
└─ Day 6-7: Statistical validation

Week 5: Documentation & Visualization
├─ Day 1-2: Generate all plots
├─ Day 3-4: Statistical analysis report
├─ Day 5-6: Write comprehensive findings
└─ Day 7: Prepare presentation

Total: ~5 weeks full-time atau ~10 weeks part-time
Total Runs: 2,750 experiments
Estimated Compute Time: ~800 hours (33 days continuous)
```

---

## KESIMPULAN

Uji coba sistem rekomendasi rute wisata dengan HGA yang **disederhanakan** fokus pada 2 analisis utama:

1. **Analisis Kualitas Solusi** → Comprehensive parameter testing (6 parameters)

   - OFAT analysis untuk parameter individual effects
   - Random search untuk parameter interactions
   - Statistical validation untuk significance

2. **Analisis Konvergensi** → Understanding HGA evolution dynamics
   - Convergence speed measurement
   - Diversity preservation analysis
   - Premature convergence detection

### Phase 1: Pre-Experiment ✓

- [ ] Environment setup dan dependency check
- [ ] Distance matrix validation (24,881 pairs)
- [ ] Data integrity check (221 destinations)
- [ ] Baseline implementations ready (Random, Greedy)
- [ ] Logging dan monitoring configuredDengan pendekatan **efisien dan fokus**, uji coba ini akan menghasilkan:
- ✅ Identifikasi konfigurasi optimal HGA
- ✅ Validasi kontribusi setiap parameter
- ✅ Understanding convergence behavior
- ✅ Statistical evidence untuk keunggulan HGA
- ✅ Dokumentasi lengkap untuk reproducibility

**Simplified approach** mengurangi kompleksitas testing dari 6 jenis uji coba menjadi 2 fokus utama, namun tetap **comprehensive** dalam coverage parameter dan **rigorous** dalam validasi statistik. Ideal untuk thesis defense dan publikasi ilmiah.

---

## LAMPIRAN

### A. Quick Reference - Optimal Configuration

```json
{
  "population_size": 600,
  "generations": 40,
  "crossover_rate": 0.8,
  "mutation_rate": 0.05,
  "tournament_size": 8,
  "use_2opt": true,
  "elitism_count": 5
}
```

### B. Statistical Validation Checklist

- [ ] Normality test (Shapiro-Wilk) untuk each parameter group
- [ ] ANOVA F-test (p < 0.05) untuk overall significance
- [ ] Post-hoc Tukey HSD untuk pairwise comparisons
- [ ] Cohen's d untuk effect size (small: 0.2, medium: 0.5, large: 0.8)
- [ ] Confidence intervals (95%) untuk all means
- [ ] Cross-validation (k=5) untuk robustness

### C. Visualization Checklist

#### Solution Quality Analysis (6 plots)

1. ✓ Box plots - All 6 parameters
2. ✓ Heatmap - Population vs Generations
3. ✓ Heatmap - Crossover vs Mutation
4. ✓ Bar chart - Top 10 configurations
5. ✓ Scatter plot - Quality vs Speed trade-off
6. ✓ Histogram - Solution distribution

#### Convergence Analysis (4 plots)

7. ✓ Line plot - Convergence curves (3 configs)
8. ✓ Line plot - Diversity evolution
9. ✓ Bar chart - Convergence generation comparison
10. ✓ Area plot - Phases of evolution

#### Statistical Validation (3 plots)

11. ✓ ANOVA visualization - F-statistics
12. ✓ Effect size visualization - Cohen's d
13. ✓ Confidence intervals - All parameters

### D. Data Archive Structure

```
experiment_results/
├── raw_data/
│   ├── ofat_results.json
│   ├── random_search_results.json
│   └── validation_results.json
├── processed_data/
│   ├── aggregated_metrics.csv
│   ├── statistical_tests.json
│   └── optimal_configs.json
├── visualizations/
│   ├── quality_analysis/
│   │   ├── all_parameters_sensitivity.png
│   │   ├── population_generations_heatmap.png
│   │   └── crossover_mutation_heatmap.png
│   ├── convergence_analysis/
│   │   ├── convergence_curves.png
│   │   └── diversity_evolution.png
│   └── statistical_validation/
│       ├── anova_results.png
│       └── effect_sizes.png
└── reports/
    ├── experiment_summary.pdf
    ├── statistical_analysis.pdf
    └── presentation_slides.pptx
```

---

**AKHIR DOKUMEN**
