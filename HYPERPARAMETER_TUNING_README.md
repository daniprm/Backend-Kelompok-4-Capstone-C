# Hyperparameter Tuning - Hybrid Genetic Algorithm

Dokumentasi lengkap untuk uji performa dan hyperparameter tuning algoritma HGA pada sistem rekomendasi rute wisata.

## 📋 Daftar Isi

1. [Tujuan Pengujian](#tujuan-pengujian)
2. [Parameter yang Diuji](#parameter-yang-diuji)
3. [Script yang Tersedia](#script-yang-tersedia)
4. [Cara Penggunaan](#cara-penggunaan)
5. [Output yang Dihasilkan](#output-yang-dihasilkan)
6. [Interpretasi Hasil](#interpretasi-hasil)

---

## 🎯 Tujuan Pengujian

Uji performa algoritma dilakukan untuk:

1. **Menilai kualitas solusi**: Mengukur kemampuan HGA dalam menghasilkan rute dengan jarak minimum
2. **Mengukur efisiensi waktu**: Memastikan waktu komputasi layak untuk sistem real-time
3. **Menemukan parameter optimal**: Menentukan kombinasi parameter terbaik dengan trade-off distance vs speed
4. **Analisis konvergensi**: Mengetahui pada generasi berapa algoritma mencapai solusi optimal

---

## 🔧 Parameter yang Diuji

### a. Population Size (Ukuran Populasi)

- **Nilai**: 100, 300, 500, 700
- **Tujuan**: Mengetahui apakah populasi lebih besar menghasilkan solusi lebih baik
- **Trade-off**: Populasi besar = solusi lebih baik tetapi waktu eksekusi lebih lama

### b. Generations (Jumlah Generasi)

- **Nilai**: 20, 40, 80
- **Tujuan**: Mengetahui pada generasi berapa algoritma konvergen
- **Indikator konvergensi**: Algoritma tidak menghasilkan improvement signifikan (< 0.1% untuk 5 generasi berturut-turut)

### c. Crossover Rate (Tingkat Crossover)

- **Nilai**: 0.6, 0.7, 0.8, 0.9
- **Tujuan**: Menentukan crossover rate optimal untuk eksplorasi solusi
- **Trade-off**: Rate tinggi = eksplorasi lebih agresif

### d. Mutation Rate (Tingkat Mutasi)

- **Nilai**: 0.01, 0.05, 0.2, 0.5
- **Tujuan**: Menentukan mutation rate optimal untuk diversity
- **Trade-off**: Rate tinggi = diversity tinggi tetapi bisa merusak solusi bagus

### e. 2-Opt Local Search

- **Nilai**: True, False
- **Tujuan**: Mengukur kontribusi 2-Opt dalam meningkatkan kualitas solusi
- **Expected**: 2-Opt seharusnya meningkatkan kualitas solusi dengan overhead waktu minimal

---

## 📦 Script yang Tersedia

### 1. `hyperparameter_tuning.py` - Full Grid Search

**Fitur:**

- Testing semua kombinasi parameter (4×3×4×4×2 = 384 konfigurasi)
- 3 runs per konfigurasi untuk statistical significance
- Total: 1,152 experiments
- Estimasi waktu: ~1.5-2 jam

**Kapan digunakan:**

- Untuk penelitian mendalam
- Ketika waktu tidak menjadi kendala
- Untuk publikasi/paper yang memerlukan data lengkap

**Cara menjalankan:**

```bash
python hyperparameter_tuning.py
```

### 2. `quick_hyperparameter_tuning.py` - Quick Test

**Fitur:**

- Testing subset parameter (3×2×2×2×2 = 48 konfigurasi)
- 2 runs per konfigurasi
- Total: 96 experiments
- Estimasi waktu: ~8-10 menit

**Kapan digunakan:**

- Testing cepat untuk development
- Validasi perubahan kode
- Exploratory analysis

**Cara menjalankan:**

```bash
python quick_hyperparameter_tuning.py
```

### 3. `visualize_tuning_results.py` - Visualization

**Fitur:**

- Membaca hasil tuning terbaru
- Generate 9 visualisasi berbeda
- Plot convergence curves untuk top 5 konfigurasi
- Generate text report

**Cara menjalankan:**

```bash
python visualize_tuning_results.py
```

---

## 🚀 Cara Penggunaan

### Step 1: Pastikan Dependencies Terinstal

```bash
pip install matplotlib seaborn pandas numpy
```

### Step 2: Jalankan Quick Test (Recommended untuk pertama kali)

```bash
python quick_hyperparameter_tuning.py
```

**Output yang akan muncul:**

```
================================================================================
QUICK HYPERPARAMETER TUNING
================================================================================
Loading destinations data...
Loaded 162 destinations

Configurations: 48
Runs per config: 2
Total experiments: 96
Estimated time: ~8.0 minutes

Press Enter to start...
```

### Step 3: Monitor Progress

Script akan menampilkan progress real-time:

```
################################################################################
Configuration 1/48
################################################################################

============================================================
Run #1 | Pop:100 Gen:20 Cross:0.7 Mut:0.05 2Opt:True
============================================================
Gen 1 - Best: 25.45 km, Fitness: 0.0393 [✗]
Gen 2 - Best: 23.12 km, Fitness: 0.0432 [✗]
...
Gen 20 - Best: 18.34 km, Fitness: 0.0545 [✓]

✓ Distance: 18.34km | Time: 3.45s | Feasible: True
```

### Step 4: Review Results

Setelah selesai, script akan menampilkan analysis:

```
================================================================================
QUICK ANALYSIS
================================================================================

🏆 BEST DISTANCE: 16.89km
   Population: 500
   Generations: 40
   Crossover: 0.8
   Mutation: 0.05
   2-Opt: True
   Execution Time: 8.23s

⚡ FASTEST (Feasible): 2.45s
   Distance: 19.12km
   Population: 100
   Generations: 20
```

### Step 5: Visualisasi Hasil

```bash
python visualize_tuning_results.py
```

Akan menghasilkan:

- `hyperparameter_tuning_visualization_[timestamp].png` - 9 plots analisis
- `convergence_curves_top5_[timestamp].png` - Convergence curves
- `hyperparameter_tuning_report_[timestamp].txt` - Text report

### Step 6 (Optional): Full Grid Search

Jika memerlukan data lebih komprehensif:

```bash
python hyperparameter_tuning.py
```

⚠️ **Warning**: Proses ini memakan waktu ~2 jam!

---

## 📊 Output yang Dihasilkan

### 1. CSV Files

#### Detailed Results (`*_detailed_*.csv`)

Berisi hasil individual untuk setiap run:

- `population_size`, `generations`, `crossover_rate`, `mutation_rate`, `use_2opt`
- `run_number` (1, 2, atau 3)
- `best_distance_km` - Jarak terbaik yang ditemukan
- `best_fitness` - Nilai fitness
- `travel_time_minutes` - Estimasi waktu tempuh
- `is_feasible` - Apakah memenuhi constraint (≤20km, ≤300min)
- `execution_time_seconds` - Waktu eksekusi
- `improvement_km` - Improvement dari initial ke final
- `improvement_percentage` - Improvement dalam persen
- `convergence_generation` - Generasi saat konvergen

#### Aggregated Results (`*_aggregated_*.csv`)

Berisi summary statistik untuk setiap konfigurasi:

- `mean_distance_km` - Rata-rata jarak dari semua run
- `std_distance_km` - Standard deviation jarak
- `min_distance_km`, `max_distance_km` - Range jarak
- `mean_execution_time` - Rata-rata waktu eksekusi
- `mean_improvement_pct` - Rata-rata improvement
- `mean_convergence_gen` - Rata-rata generasi konvergen
- `feasible_rate` - Persentase solusi feasible (0-100%)

### 2. JSON File

`hyperparameter_tuning_full_*.json` berisi:

- Semua detailed results dengan fitness/distance history
- Aggregated results
- Parameter grid yang digunakan
- Fixed parameters
- Metadata eksperimen

**Format:**

```json
{
  "detailed_results": [...],
  "aggregated_results": [...],
  "parameter_grid": {
    "population_size": [100, 300, 500, 700],
    "generations": [20, 40, 80],
    ...
  },
  "fixed_parameters": {
    "elitism_count": 2,
    "tournament_size": 8,
    "two_opt_iterations": 100
  },
  "num_runs_per_config": 3
}
```

### 3. Visualizations

#### Main Visualization (9 subplots):

1. **Population Size Effect** - Distance vs time dengan varying population
2. **Generations Effect** - Distance vs convergence generation
3. **Crossover Rate Effect** - Distance vs improvement percentage
4. **Mutation Rate Effect** - Distance vs improvement percentage
5. **2-Opt Effect** - Bar chart comparing with/without 2-Opt
6. **Distance vs Time Scatter** - Scatter plot dengan color = feasible rate
7. **Population vs Generations Heatmap** - Mean distance heatmap
8. **Crossover vs Mutation Heatmap** - Mean distance heatmap
9. **Top 10 Configurations** - Horizontal bar chart

#### Convergence Curves:

- 6 subplots untuk top 5 konfigurasi
- Menampilkan distance evolution per generation
- Individual runs (transparant) + mean (bold red)

### 4. Text Report

`hyperparameter_tuning_report_*.txt` berisi:

- Summary statistics
- Best configuration (minimum distance)
- Parameter effect analysis
- Detailed breakdown untuk setiap parameter

---

## 📈 Interpretasi Hasil

### 1. Metrik Utama

#### a. Mean Distance (km)

- **Lower is better**
- Target: < 20 km (constraint)
- Ideal: 16-18 km range

#### b. Execution Time (seconds)

- **Lower is better** (untuk real-time system)
- Target: < 10 seconds untuk user experience
- Acceptable: < 30 seconds

#### c. Feasible Rate (%)

- **Higher is better**
- Target: ≥ 80%
- Indicates: Berapa % solusi yang memenuhi constraint

#### d. Improvement Percentage (%)

- **Higher is better**
- Indicates: Seberapa efektif algoritma improve dari initial solution
- Typical: 30-50% improvement

#### e. Convergence Generation

- **Lower is better** (cepat konvergen)
- Indicates: Efisiensi algoritma
- Warning: Terlalu cepat konvergen bisa berarti premature convergence

### 2. Trade-offs

#### Distance vs Speed:

```
High Population + High Generations = Better Distance BUT Slower
Low Population + Low Generations = Faster BUT Worse Distance
```

**Recommendation**:

- Untuk production: Balance dengan population=300-500, generations=40
- Untuk testing: population=100, generations=20

#### Exploration vs Exploitation:

```
High Crossover + High Mutation = More Exploration (diverse solutions)
Low Crossover + Low Mutation = More Exploitation (refine good solutions)
```

**Recommendation**:

- Crossover: 0.7-0.8 (moderate-high exploration)
- Mutation: 0.05-0.1 (low-moderate diversity)

### 3. Analisis Parameter Effects

#### Population Size:

- **100**: Fast but may miss optimal solutions
- **300**: Good balance
- **500**: Better solutions, acceptable time
- **700**: Diminishing returns, significantly slower

#### Generations:

- **20**: Quick convergence, may be premature
- **40**: Good balance, usually converges before Gen 40
- **80**: Overkill, waste computation (convergence around Gen 30-40)

#### 2-Opt:

- **Expected**: 5-10% distance improvement
- **Cost**: ~20-30% execution time overhead
- **Recommendation**: Always use 2-Opt for production

### 4. Contoh Interpretasi

**Scenario 1: Development/Testing**

```
Best Config:
  Population: 100
  Generations: 20
  Crossover: 0.7
  Mutation: 0.05
  2-Opt: True

Result: Distance=19.2km, Time=2.5s
Interpretation: Fast enough for rapid iteration, acceptable quality
```

**Scenario 2: Production**

```
Best Config:
  Population: 500
  Generations: 40
  Crossover: 0.8
  Mutation: 0.05
  2-Opt: True

Result: Distance=16.8km, Time=8.3s
Interpretation: High quality solutions, acceptable latency for users
```

**Scenario 3: Research/Publication**

```
Best Config:
  Population: 700
  Generations: 80
  Crossover: 0.8
  Mutation: 0.05
  2-Opt: True

Result: Distance=16.5km, Time=18.7s
Interpretation: Best possible quality, but too slow for real-time
Use case: Benchmarking, comparison with other algorithms
```

---

## 🎯 Recommended Workflow

### For First Time:

1. **Quick Test**:

   ```bash
   python quick_hyperparameter_tuning.py
   ```

   Get initial sense of parameter space (~10 minutes)

2. **Analyze**:

   ```bash
   python visualize_tuning_results.py
   ```

   Review quick results, identify promising ranges

3. **Full Grid Search**:

   ```bash
   python hyperparameter_tuning.py
   ```

   If needed, do comprehensive search (~2 hours)

4. **Final Visualization**:
   ```bash
   python visualize_tuning_results.py
   ```
   Generate publication-ready visualizations

### For Development:

- Run quick test after major code changes
- Verify performance doesn't degrade
- Use as regression test

### For Production Deployment:

- Use full grid search results
- Select configuration based on:
  - User experience requirements (speed)
  - Solution quality needs (distance)
  - Infrastructure constraints (CPU)

---

## 📝 Notes

1. **Random Seed**: Not fixed by default untuk real statistical analysis. Tambahkan `random.seed(42)` jika perlu reproducibility.

2. **Start Point**: Default ke (-7.2575, 112.7521) Surabaya pusat. Ganti di variable `START_POINT` untuk testing lokasi lain.

3. **Parallel Execution**: Script saat ini sequential. Untuk speedup, bisa dimodifikasi menggunakan `multiprocessing`.

4. **Memory Usage**: Full grid search dengan history data bisa menggunakan ~500MB RAM. Monitor jika menjalankan di server dengan resource terbatas.

5. **Interrupted Tuning**: Tekan Ctrl+C untuk stop. Data yang sudah dikumpulkan akan hilang. Consider adding checkpoint mechanism untuk long runs.

---

## 🔬 Advanced Usage

### Custom Parameter Grid:

Edit `PARAMETER_GRID` di script:

```python
PARAMETER_GRID = {
    'population_size': [200, 400, 600],  # Custom values
    'generations': [30, 50],
    # ...
}
```

### Different Start Points:

Test multiple locations:

```python
START_POINTS = [
    (-7.2575, 112.7521),  # Surabaya pusat
    (-7.2754, 112.7688),  # Gubeng
    (-7.2897, 112.7308),  # Tunjungan
]

for start in START_POINTS:
    results = run_tuning(start_point=start)
```

### Export to LaTeX:

Untuk paper/thesis:

```python
import pandas as pd

df = pd.read_csv('hyperparameter_tuning_aggregated_*.csv')
latex_table = df.to_latex(index=False)
print(latex_table)
```

---

## 📚 References

- Goldberg, D.E. (1989). Genetic Algorithms in Search, Optimization and Machine Learning
- Holland, J.H. (1992). Adaptation in Natural and Artificial Systems
- Lin, S., & Kernighan, B.W. (1973). An Effective Heuristic Algorithm for TSP

---

**Last Updated**: December 18, 2025
**Author**: Rahmat Ramadhan Permana
**Project**: Tourism Route Recommendation System - Hybrid Genetic Algorithm
