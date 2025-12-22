# Extended Hyperparameter Tuning - README

## Overview

File `hyperparameter_tuning_extended.py` dibuat untuk menguji parameter baru yang ditambahkan ke HGA tanpa menghapus konfigurasi tuning yang sudah ada.

## Parameter Baru yang Diuji

Berdasarkan konfigurasi HGA yang digunakan saat ini:

```python
{
    "population_size": 700,
    "generations": 20,
    "crossover_rate": 0.8,
    "mutation_rate": 0.01,
    "elitism_count": 2,
    "tournament_size": 8,
    "use_2opt": True,
    "two_opt_iterations": 100
}
```

Parameter yang sekarang bisa di-tune:

- **elitism_count**: [2, 5, 10]
- **tournament_size**: [3, 5, 8]
- **two_opt_iterations**: [50, 100, 500]

## Strategi Testing

### File: `hyperparameter_tuning.py` (UPDATED)

- **Status**: Diperbarui untuk include semua parameter baru
- **Total Konfigurasi**: 10,368 (4 × 3 × 4 × 4 × 2 × 3 × 3 × 3)
- **Total Runs**: 31,104 (3 runs per config)
- **Estimasi Waktu**: 86-173 jam (3.5-7 hari)
- **Use Case**: Comprehensive grid search untuk menemukan konfigurasi optimal absolut

**Parameter Grid Lengkap**:

```python
PARAMETER_GRID = {
    'population_size': [100, 300, 500, 700],
    'generations': [20, 40, 80],
    'crossover_rate': [0.6, 0.7, 0.8, 0.9],
    'mutation_rate': [0.01, 0.05, 0.2, 0.5],
    'use_2opt': [True, False],
    'elitism_count': [2, 5, 10],
    'tournament_size': [3, 5, 8],
    'two_opt_iterations': [50, 100, 500]
}
```

### File: `hyperparameter_tuning_extended.py` (NEW)

- **Status**: File baru yang fokus pada parameter baru
- **Total Konfigurasi**: 162 (6 base variants × 27 new param combos)
- **Total Runs**: 486 (3 runs per config)
- **Estimasi Waktu**: 1.4-2.7 jam
- **Use Case**: Focused testing untuk parameter baru dengan base config yang baik

**Base Configurations** (6 variants):

```python
VARIANT_CONFIGS = [
    # Baseline user config
    {'pop': 700, 'gen': 20, 'cross': 0.8, 'mut': 0.01, '2opt': True},
    # Variasi population
    {'pop': 500, 'gen': 20, 'cross': 0.8, 'mut': 0.01, '2opt': True},
    {'pop': 300, 'gen': 20, 'cross': 0.8, 'mut': 0.01, '2opt': True},
    # Variasi generations
    {'pop': 700, 'gen': 40, 'cross': 0.8, 'mut': 0.01, '2opt': True},
    {'pop': 700, 'gen': 80, 'cross': 0.8, 'mut': 0.01, '2opt': True},
    # Variasi mutation
    {'pop': 700, 'gen': 20, 'cross': 0.8, 'mut': 0.05, '2opt': True},
]
```

**New Parameters Grid**:

```python
NEW_PARAMETER_GRID = {
    'elitism_count': [2, 5, 10],
    'tournament_size': [3, 5, 8],
    'two_opt_iterations': [50, 100, 500]
}
```

## Cara Penggunaan

### Option 1: Full Grid Search (Waktu Lama)

```bash
python hyperparameter_tuning.py
```

Gunakan ini jika:

- Anda memiliki waktu 3-7 hari
- Ingin eksplorasi komprehensif semua kombinasi
- Butuh hasil optimal absolut

### Option 2: Extended Tuning (Rekomendasi)

```bash
python hyperparameter_tuning_extended.py
```

Gunakan ini jika:

- Anda ingin hasil cepat (1-3 jam)
- Fokus pada parameter baru (elitism, tournament, 2opt_iterations)
- Base parameters sudah diketahui cukup baik

## Output Files

### Full Grid Search

- `hyperparameter_tuning_detailed_YYYYMMDD_HHMMSS.csv`
- `hyperparameter_tuning_aggregated_YYYYMMDD_HHMMSS.csv`
- `hyperparameter_tuning_full_YYYYMMDD_HHMMSS.json`

### Extended Tuning

- `extended_tuning_detailed_YYYYMMDD_HHMMSS.csv`
- `extended_tuning_aggregated_YYYYMMDD_HHMMSS.csv`
- `extended_tuning_full_YYYYMMDD_HHMMSS.json`

## Analisis Results

Kedua script akan menghasilkan analisis komprehensif:

1. **TOP 5 Configurations** - Konfigurasi dengan jarak terbaik
2. **Parameter Effect Analysis** - Efek setiap parameter individual
3. **Best Balanced Configuration** - Konfigurasi optimal untuk distance + speed
4. **Detailed Statistics** - Mean, std dev, min, max, convergence

## Rekomendasi

### Tahap 1: Extended Tuning (1-3 jam)

Jalankan `hyperparameter_tuning_extended.py` untuk:

- Mendapatkan gambaran awal efek parameter baru
- Menemukan range yang paling promising
- Validasi apakah parameter baru memberi improvement signifikan

### Tahap 2 (Optional): Full Grid Search (3-7 hari)

Jika hasil extended tuning menunjukkan improvement signifikan:

- Jalankan full grid search untuk eksplorasi komprehensif
- Atau buat custom grid dengan range yang sudah di-narrow down

## Interpretasi Results

### Elitism Count

- **Rendah (2)**: Lebih eksplorasi, konvergensi lambat
- **Medium (5)**: Balance eksplorasi-eksploitasi
- **Tinggi (10)**: Konvergensi cepat, risiko premature convergence

### Tournament Size

- **Kecil (3)**: Selection pressure rendah, lebih diverse
- **Medium (5)**: Balance diversity-convergence
- **Besar (8)**: Selection pressure tinggi, konvergensi cepat

### 2-Opt Iterations

- **50**: Cepat tapi mungkin kurang optimal
- **100**: Balance speed-quality
- **500**: Slow tapi lebih optimal

## Perubahan pada File yang Ada

### `hyperparameter_tuning.py`

- ✅ PARAMETER_GRID ditambah: elitism_count, tournament_size, two_opt_iterations
- ✅ FIXED_PARAMS sekarang kosong (semua parameter tunable)
- ✅ run_single_experiment() menerima 3 parameter baru
- ✅ CSV headers di-update untuk include parameter baru
- ✅ Analisis menampilkan efek parameter baru
- ✅ TOP 5 dan Recommended Config menampilkan semua parameter

### `algorithms/hga.py`

- ✅ Ditambahkan method `get_evolution_statistics()` untuk convergence analysis

## Time Estimation Update

Berdasarkan waktu eksekusi aktual (10-20 detik per run):

| Script      | Configs | Runs   | Time Range    | Duration   |
| ----------- | ------- | ------ | ------------- | ---------- |
| Full Grid   | 10,368  | 31,104 | 86-173 hours  | 3.5-7 days |
| Extended    | 162     | 486    | 1.4-2.7 hours | ~2 hours   |
| Quick (old) | 48      | 96     | 15-25 min     | ~20 min    |

## Visualisasi

Setelah tuning selesai, gunakan:

```bash
python visualize_tuning_results.py
```

Script visualisasi sudah support parameter baru dan akan menghasilkan:

- 12 subplots termasuk heatmap untuk parameter baru
- Convergence curves untuk top 3 configurations
- Parameter interaction plots
- Feasibility rate analysis
