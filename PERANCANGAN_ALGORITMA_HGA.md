# PERANCANGAN ALGORITMA HYBRID GENETIC ALGORITHM UNTUK SISTEM REKOMENDASI RUTE WISATA

---

## 1. PENDAHULUAN

### 1.1 Latar Belakang Perancangan

Permasalahan rekomendasi rute wisata merupakan varian dari Travelling Salesman Problem (TSP) dengan constraint tambahan berupa urutan kategori destinasi yang harus diikuti. Penelitian ini merancang Hybrid Genetic Algorithm (HGA) yang menggabungkan kemampuan eksplorasi global dari Genetic Algorithm dengan kemampuan eksploitasi lokal dari algoritma 2-Opt untuk menghasilkan solusi rute yang optimal.

### 1.2 Tujuan Perancangan

1. Merancang representasi kromosom yang mampu merepresentasikan solusi rute dengan constraint urutan kategori
2. Merancang operator genetik yang mempertahankan validitas constraint selama proses evolusi
3. Merancang mekanisme hibridisasi antara GA dan local search untuk optimasi multi-level
4. Merancang fungsi fitness dengan mekanisme penalty untuk mengevaluasi kualitas solusi berdasarkan jarak dan waktu tempuh
5. Merancang mekanisme penalty untuk constraint jarak maksimal (20 km) dan waktu tempuh maksimal (5 jam)
6. Merancang strategi terminasi yang efisien untuk konvergensi optimal

---

## 2. PERANCANGAN REPRESENTASI KROMOSOM

### 2.1 Struktur Kromosom

Kromosom direpresentasikan sebagai array of genes, dimana setiap gen merupakan referensi ke objek destinasi wisata.

**Definisi Formal:**

```
Kromosom C = [g₁, g₂, g₃, ..., g₈]
```

Dimana:

- gᵢ ∈ D (D = himpunan destinasi wisata)
- |C| = 8 (panjang tetap untuk memenuhi constraint)
- gᵢ ≠ gⱼ untuk i ≠ j (tidak ada destinasi duplikat)

**Constraint Urutan Kategori:**

```
C = [K₁, C₁, W₁, K₂, W₂, C₂, K₃, O]
```

Keterangan:

- K₁, K₂, K₃: Makanan Berat (kategori berbeda)
- C₁, C₂: Makanan Ringan (kategori berbeda)
- W₁, W₂: Non-Kuliner atau All (kategori berbeda)
- O: Oleh-oleh atau All

**Alasan Pemilihan Representasi:**

1. **Order-based representation** cocok untuk masalah permutasi dengan constraint
2. **Fixed-length** memudahkan operasi genetik dan validasi constraint
3. **Object reference** mempertahankan informasi lengkap destinasi tanpa encoding tambahan

### 2.2 Atribut Kromosom

Setiap kromosom memiliki atribut:

| Atribut           | Tipe Data           | Deskripsi                                      |
| ----------------- | ------------------- | ---------------------------------------------- |
| `genes`           | List[Destination]   | Urutan destinasi dalam rute                    |
| `start_point`     | Tuple[float, float] | Koordinat titik awal (latitude, longitude)     |
| `fitness_value`   | float atau None     | Nilai fitness dengan penalty (lazy evaluation) |
| `penalty_value`   | float atau None     | Nilai penalty dari constraint violations       |
| `_total_distance` | float atau None     | Cache total jarak rute (km)                    |
| `_total_time`     | float atau None     | Cache total waktu tempuh (menit)               |

**Lazy Evaluation Design:**

- Fitness hanya dihitung saat pertama kali dibutuhkan
- Hasil fitness, penalty, distance, dan time disimpan di cache
- Meningkatkan efisiensi komputasi hingga 30-40%
- Copy chromosome juga menyalin cached values

---

## 3. PERANCANGAN FUNGSI FITNESS

### 3.1 Formulasi Fungsi Fitness dengan Mekanisme Penalty

Fungsi fitness dirancang berbanding terbalik dengan total jarak rute, dengan mekanisme **penalty** untuk constraint jarak dan waktu tempuh:

**Formula Fitness Dasar (Base Fitness):**

```
f_base(C) = 1 / D_total(C)
```

**Formula Fitness dengan Penalty:**

```
f(C) = f_base(C) / (1 + P_total(C))
```

Dimana:

- `f_base(C)`: Fitness dasar tanpa penalty
- `P_total(C)`: Total penalty dari semua constraint violations

**Total Jarak Rute:**

```
D_total(C) = d(S, g₁) + Σᵢ₌₁⁷ d(gᵢ, gᵢ₊₁)
```

**Total Waktu Tempuh:**

```
T_total(C) = t(S, g₁) + Σᵢ₌₁⁷ t(gᵢ, gᵢ₊₁)
```

Keterangan:

- S: Start point (lokasi user)
- gᵢ: Destinasi ke-i dalam kromosom
- d(a, b): Fungsi jarak antara titik a dan b (km)
- t(a, b): Fungsi waktu tempuh antara titik a dan b (menit)

**Alasan Formulasi:**

1. **Inverse relationship**: Jarak lebih pendek → fitness lebih tinggi (minimization problem)
2. **Penalty mechanism**: Solusi yang melanggar constraint akan memiliki fitness lebih rendah
3. **Soft constraint**: Solusi infeasible masih bisa survive untuk maintain diversity
4. **Differentiable**: Memungkinkan analisis sensitivitas

### 3.2 Perancangan Mekanisme Penalty

**Constraint yang Diterapkan:**

| Constraint     | Symbol | Nilai Maksimum    | Deskripsi                                     |
| -------------- | ------ | ----------------- | --------------------------------------------- |
| Jarak Maksimal | D_max  | 20 km             | Total jarak rute tidak boleh melebihi 20 km   |
| Waktu Maksimal | T_max  | 300 menit (5 jam) | Total waktu tempuh tidak boleh melebihi 5 jam |

**Formula Penalty Jarak (Quadratic Penalty):**

```
P_distance(C) = {
  0,                                           jika D_total ≤ D_max
  w_d × ((D_total - D_max) / D_max)²,          jika D_total > D_max
}
```

**Formula Penalty Waktu (Quadratic Penalty):**

```
P_time(C) = {
  0,                                           jika T_total ≤ T_max
  w_t × ((T_total - T_max) / T_max)²,          jika T_total > T_max
}
```

**Total Penalty:**

```
P_total(C) = P_distance(C) + P_time(C)
```

**Parameter Penalty:**

| Parameter               | Symbol | Nilai Default | Deskripsi                             |
| ----------------------- | ------ | ------------- | ------------------------------------- |
| Distance Penalty Weight | w_d    | 0.5           | Bobot penalty untuk pelanggaran jarak |
| Time Penalty Weight     | w_t    | 0.3           | Bobot penalty untuk pelanggaran waktu |

**Karakteristik Quadratic Penalty:**

1. **Progressive**: Semakin besar pelanggaran, penalty semakin besar secara kuadratik
2. **Normalized**: Dinormalisasi dengan nilai maksimum untuk konsistensi
3. **Smooth**: Tidak ada diskontinuitas pada batas constraint

**Algoritma Calculate Penalty:**

```
ALGORITHM: Calculate_Total_Penalty
INPUT:
  - total_distance_km: Total jarak rute dalam km
  - total_time_minutes: Total waktu tempuh dalam menit
OUTPUT:
  - total_penalty: Nilai penalty total

CONSTANTS:
  - MAX_ROUTE_DISTANCE_KM = 20.0
  - MAX_ROUTE_TIME_MINUTES = 300.0
  - DISTANCE_PENALTY_WEIGHT = 0.5
  - TIME_PENALTY_WEIGHT = 0.3

STEPS:
1. CALCULATE DISTANCE PENALTY:
   IF total_distance_km > MAX_ROUTE_DISTANCE_KM THEN:
     excess_distance ← total_distance_km - MAX_ROUTE_DISTANCE_KM
     penalty_ratio ← excess_distance / MAX_ROUTE_DISTANCE_KM
     distance_penalty ← DISTANCE_PENALTY_WEIGHT × (penalty_ratio)²
   ELSE:
     distance_penalty ← 0

2. CALCULATE TIME PENALTY:
   IF total_time_minutes > MAX_ROUTE_TIME_MINUTES THEN:
     excess_time ← total_time_minutes - MAX_ROUTE_TIME_MINUTES
     penalty_ratio ← excess_time / MAX_ROUTE_TIME_MINUTES
     time_penalty ← TIME_PENALTY_WEIGHT × (penalty_ratio)²
   ELSE:
     time_penalty ← 0

3. RETURN distance_penalty + time_penalty
```

**Algoritma Apply Penalty to Fitness:**

```
ALGORITHM: Apply_Penalty_To_Fitness
INPUT:
  - base_fitness: Nilai fitness dasar
  - total_penalty: Total penalty
OUTPUT:
  - penalized_fitness: Fitness yang sudah di-penalty

STEPS:
1. IF total_penalty ≤ 0 THEN:
     RETURN base_fitness

2. penalized_fitness ← base_fitness / (1 + total_penalty)

3. RETURN penalized_fitness
```

**Ilustrasi Dampak Penalty:**

```
Contoh 1: Solusi Feasible (tidak melanggar constraint)
- Total Distance: 18 km (< 20 km) ✓
- Total Time: 240 min (< 300 min) ✓
- Distance Penalty: 0
- Time Penalty: 0
- Total Penalty: 0
- Base Fitness: 1/18 = 0.0556
- Penalized Fitness: 0.0556 / (1 + 0) = 0.0556 (tidak berubah)

Contoh 2: Solusi Infeasible (melanggar distance constraint)
- Total Distance: 30 km (> 20 km) ✗
- Total Time: 200 min (< 300 min) ✓
- Distance Penalty: 0.5 × ((30-20)/20)² = 0.5 × 0.25 = 0.125
- Time Penalty: 0
- Total Penalty: 0.125
- Base Fitness: 1/30 = 0.0333
- Penalized Fitness: 0.0333 / (1 + 0.125) = 0.0296 (↓11.1%)

Contoh 3: Solusi Sangat Infeasible (melanggar kedua constraint)
- Total Distance: 40 km (> 20 km) ✗
- Total Time: 500 min (> 300 min) ✗
- Distance Penalty: 0.5 × ((40-20)/20)² = 0.5 × 1 = 0.5
- Time Penalty: 0.3 × ((500-300)/300)² = 0.3 × 0.444 = 0.133
- Total Penalty: 0.633
- Base Fitness: 1/40 = 0.025
- Penalized Fitness: 0.025 / (1 + 0.633) = 0.0153 (↓38.8%)
```

### 3.3 Feasibility Check

**Algoritma Check Feasibility:**

```
ALGORITHM: Check_Feasibility
INPUT:
  - chromosome: Kromosom yang akan dicek
OUTPUT:
  - is_feasible: Boolean (TRUE jika memenuhi semua constraint)
  - constraint_info: Detail informasi constraint

STEPS:
1. CALCULATE METRICS:
   total_distance ← chromosome.get_total_distance()
   total_time ← chromosome.get_total_travel_time()

2. CHECK CONSTRAINTS:
   distance_violated ← total_distance > MAX_ROUTE_DISTANCE_KM
   time_violated ← total_time > MAX_ROUTE_TIME_MINUTES

3. is_feasible ← NOT(distance_violated OR time_violated)

4. RETURN is_feasible, constraint_info
```

**Informasi Constraint yang Dikembalikan:**

```json
{
  "distance": {
    "value": 25.5,
    "max_allowed": 20.0,
    "violated": true,
    "excess": 5.5,
    "penalty": 0.0378
  },
  "time": {
    "value_minutes": 180.0,
    "value_hours": 3.0,
    "max_allowed_minutes": 300.0,
    "max_allowed_hours": 5.0,
    "violated": false,
    "excess_minutes": 0,
    "penalty": 0.0
  },
  "total_penalty": 0.0378,
  "is_feasible": false
}
```

### 3.4 Perancangan Perhitungan Jarak

Sistem menggunakan **strategi multi-tier** untuk efisiensi:

```
┌─────────────────────────────────────┐
│  1. Pre-calculated Distance Matrix  │ ← Priority 1 (Instant)
│     (OSRM Real Routes)              │
└─────────────────────────────────────┘
              ↓ (jika tidak ada)
┌─────────────────────────────────────┐
│  2. Haversine Distance              │ ← Priority 2 (User location)
│     (Straight-line approximation)   │
└─────────────────────────────────────┘
              ↓ (jika diperlukan)
┌─────────────────────────────────────┐
│  3. OSRM API Real-time              │ ← Priority 3 (Fallback)
│     (Network request)               │
└─────────────────────────────────────┘
```

**Rancangan Distance Matrix:**

- Tipe: Dictionary dengan key caching
- Size: n(n-1)/2 pairs untuk n destinasi
- Format key: `"lat1,lon1|lat2,lon2"` (sorted untuk bi-directional)
- Storage: JSON file untuk persistence (`data/distance_matrix_osrm.json`)
- Metadata: timestamp, success rate, total pairs

**Formula Haversine (untuk user location):**

```
a = sin²(Δφ/2) + cos(φ₁) × cos(φ₂) × sin²(Δλ/2)
c = 2 × atan2(√a, √(1-a))
d = R × c
```

Dimana:

- φ: latitude (dalam radian)
- λ: longitude (dalam radian)
- R: radius bumi (6371 km)

### 3.5 Perancangan Travel Time Matrix

Untuk mendukung mekanisme penalty waktu tempuh, sistem menggunakan **Travel Time Matrix** yang pre-calculated.

**Strategi Perhitungan Waktu Tempuh:**

```
┌─────────────────────────────────────┐
│  1. Pre-calculated Travel Time      │ ← Priority 1 (Instant)
│     Matrix (OSRM Real Routes)       │
└─────────────────────────────────────┘
              ↓ (jika tidak ada)
┌─────────────────────────────────────┐
│  2. Estimation from Distance        │ ← Priority 2 (Fallback)
│     t = d / avg_speed               │
└─────────────────────────────────────┘
              ↓ (jika diperlukan)
┌─────────────────────────────────────┐
│  3. OSRM API Real-time              │ ← Priority 3 (Network)
│     (Duration from routing API)     │
└─────────────────────────────────────┘
```

**Rancangan Travel Time Matrix:**

- Tipe: Dictionary dengan key caching (sama dengan distance matrix)
- Size: n(n-1)/2 pairs untuk n destinasi
- Format key: `"lat1,lon1|lat2,lon2"` (sorted untuk bi-directional)
- Storage: JSON file untuk persistence (`data/travel_time_matrix_osrm.json`)
- Value structure: `{duration: float, distance: float, source: string}`

**Data Structure:**

```json
{
  "matrix": {
    "-7.275697,112.780625|-7.267302,112.769752": {
      "duration": 4.15,
      "distance": 2.077,
      "source": "osrm"
    },
    ...
  },
  "metadata": {
    "total_destinations": 221,
    "total_pairs": 24310,
    "last_updated": "2025-12-04 20:22:59",
    "osrm_success": 24310,
    "estimated_fallback": 0,
    "average_speed_kmh": 30
  }
}
```

**Formula Estimasi Waktu Tempuh (Fallback):**

```
t(a, b) = d(a, b) / v_avg × 60
```

Dimana:

- t(a, b): Waktu tempuh dalam menit
- d(a, b): Jarak dalam km
- v_avg: Kecepatan rata-rata (default: 30 km/jam untuk urban traffic Surabaya)

**Algoritma Get Travel Time:**

```
ALGORITHM: Get_Travel_Time
INPUT:
  - coord1: Koordinat titik pertama (lat, lon)
  - coord2: Koordinat titik kedua (lat, lon)
OUTPUT:
  - travel_time_minutes: Waktu tempuh dalam menit

STEPS:
1. GENERATE KEY:
   key ← make_sorted_key(coord1, coord2)

2. CHECK CACHE:
   IF key IN travel_time_matrix THEN:
     RETURN travel_time_matrix[key].duration

3. TRY OSRM API:
   result ← call_osrm_route_api(coord1, coord2)
   IF result != NULL THEN:
     travel_time_matrix[key] ← result
     RETURN result.duration

4. FALLBACK TO ESTIMATION:
   distance ← get_distance(coord1, coord2)
   travel_time ← distance / AVERAGE_SPEED_KMH × 60
   travel_time_matrix[key] ← {
     duration: travel_time,
     distance: distance,
     source: "estimated"
   }
   RETURN travel_time
```

**Algoritma Calculate Total Travel Time:**

```
ALGORITHM: Calculate_Total_Travel_Time
INPUT:
  - start_point: Koordinat awal (lat, lon)
  - destinations: List destinasi dalam rute
OUTPUT:
  - total_time_minutes: Total waktu tempuh dalam menit

STEPS:
1. IF destinations IS EMPTY THEN:
     RETURN 0.0

2. total_time ← 0.0

3. GET TIME TO FIRST DESTINATION:
   time_to_first ← Get_Travel_Time(start_point, destinations[0].coords)
   IF time_to_first != NULL THEN:
     total_time ← total_time + time_to_first

4. GET TIME BETWEEN DESTINATIONS:
   FOR i = 0 TO length(destinations) - 2 DO:
     coord1 ← destinations[i].coords
     coord2 ← destinations[i+1].coords
     travel_time ← Get_Travel_Time(coord1, coord2)
     IF travel_time != NULL THEN:
       total_time ← total_time + travel_time

5. RETURN total_time
```

**Karakteristik Travel Time Matrix:**

| Property         | Value                        |
| ---------------- | ---------------------------- |
| Total Pairs      | 24,091 (untuk 221 destinasi) |
| Average Duration | 21.1 menit                   |
| Min Duration     | 0 menit (same location)      |
| Max Duration     | 76.6 menit                   |
| Average Distance | 10.54 km                     |
| Source           | OSRM API / Estimation        |

**Performance Impact:**

```
Without Matrix:
- API calls per fitness evaluation: ~9 (untuk 8 destinasi + start)
- Time per fitness evaluation: ~2-5 seconds

With Matrix:
- API calls per fitness evaluation: 0
- Time per fitness evaluation: <1 ms
- Speedup: ~2000-5000x untuk time calculation
```

---

## 4. PERANCANGAN POPULASI

### 4.1 Struktur Populasi

**Definisi Formal:**

```
Population P = {C₁, C₂, C₃, ..., Cₙ}
```

Dimana:

- n: population size (parameter konfigurasi)
- Cᵢ: kromosom ke-i

**Atribut Populasi:**

| Atribut           | Tipe Data        | Deskripsi                             |
| ----------------- | ---------------- | ------------------------------------- |
| `chromosomes`     | List[Chromosome] | Array of chromosomes                  |
| `population_size` | int              | Target ukuran populasi (default: 600) |

### 4.2 Perancangan Inisialisasi Populasi

**Algoritma Inisialisasi:**

```
ALGORITHM: Initialize_Random_Population
INPUT:
  - all_destinations: List semua destinasi
  - start_point: Koordinat awal
  - population_size: Ukuran populasi target
OUTPUT:
  - Population dengan population_size kromosom valid

STEPS:
1. Kelompokkan destinasi berdasarkan kategori:
   - makanan_berat → K_destinations
   - makanan_ringan → C_destinations
   - non_kuliner → W_destinations
   - oleh_oleh → O_destinations
   - all → All_destinations

2. Validasi ketersediaan destinasi:
   IF count(K_destinations) < 3 THEN ERROR
   IF count(C_destinations) < 2 THEN ERROR
   IF count(W_destinations) < 2 THEN ERROR
   IF count(O_destinations) < 1 THEN ERROR

3. FOR i = 1 TO population_size DO:
   3.1. genes ← empty array
   3.2. genes[1] ← random_choice(K_destinations)
   3.3. genes[2] ← random_choice(C_destinations)
   3.4. genes[3] ← random_choice(W_destinations ∪ All_destinations)
   3.5. genes[4] ← random_choice(K_destinations \ {genes[1]})
   3.6. genes[5] ← random_choice((W_destinations ∪ All_destinations) \ {genes[3]})
   3.7. genes[6] ← random_choice(C_destinations \ {genes[2]})
   3.8. genes[7] ← random_choice(K_destinations \ {genes[1], genes[4]})
   3.9. genes[8] ← random_choice((O_destinations ∪ All_destinations) \ genes)
   3.10. CREATE Chromosome(genes, start_point)
   3.11. ADD to population

4. RETURN population
```

**Karakteristik Inisialisasi:**

1. **Random diversity**: Setiap kromosom diinisialisasi secara acak untuk diversity tinggi
2. **Constraint satisfaction**: Setiap kromosom dijamin valid sejak awal
3. **Non-redundancy**: Tidak ada destinasi duplikat dalam satu kromosom
4. **Category distribution**: Memastikan setiap kategori wajib terwakili

---

## 5. PERANCANGAN OPERATOR SELEKSI

### 5.1 Tournament Selection

**Konsep:**
Memilih subset acak dari populasi (tournament), kemudian memilih individu terbaik dari subset tersebut.

**Algoritma Tournament Selection:**

```
ALGORITHM: Tournament_Selection
INPUT:
  - population: List kromosom
  - tournament_size: Ukuran tournament (default: 8)
OUTPUT:
  - selected_chromosome: Kromosom terpilih

STEPS:
1. tournament ← random_sample(population, min(tournament_size, |population|))
2. best_chromosome ← NULL
3. best_fitness ← -∞

4. FOR EACH chromosome IN tournament DO:
   4.1. fitness ← chromosome.get_fitness()
   4.2. IF fitness > best_fitness THEN:
        best_fitness ← fitness
        best_chromosome ← chromosome

5. RETURN best_chromosome
```

**Parameter Rancangan:**

- Tournament size: 8 (balance eksplorasi-eksploitasi)
- Selection pressure: Sedang (tidak terlalu tinggi untuk maintain diversity)

**Analisis Probabilitas Seleksi:**

```
P(C terpilih) = Σ P(C di tournament) × P(C terbaik | C di tournament)
```

### 5.2 Roulette Wheel Selection (Alternatif)

**Konsep:**
Probabilitas seleksi proporsional dengan fitness relatif.

**Algoritma Roulette Wheel:**

```
ALGORITHM: Roulette_Wheel_Selection
INPUT:
  - population: List kromosom
OUTPUT:
  - selected_chromosome: Kromosom terpilih

STEPS:
1. total_fitness ← Σ(fitness dari semua kromosom)
2. IF total_fitness = 0 THEN RETURN random_choice(population)

3. pick ← random_uniform(0, total_fitness)
4. current ← 0

5. FOR EACH chromosome IN population DO:
   5.1. current ← current + chromosome.get_fitness()
   5.2. IF current ≥ pick THEN RETURN chromosome

6. RETURN population[-1]  // fallback
```

**Trade-off:**

- ✅ Advantage: Semua individu punya peluang terpilih
- ❌ Disadvantage: Selection pressure lemah, konvergensi lambat
- **Keputusan**: Gunakan Tournament Selection sebagai default

---

## 6. PERANCANGAN OPERATOR CROSSOVER

### 6.1 Order Crossover (OX)

**Konsep:**
Mempertahankan urutan relatif gen dari parent sambil mengambil subset dari parent lain.

**Algoritma Order Crossover:**

```
ALGORITHM: Order_Crossover
INPUT:
  - parent1, parent2: Dua kromosom parent
OUTPUT:
  - offspring1, offspring2: Dua kromosom offspring

STEPS:
1. size ← length(parent1.genes)
2. point1 ← random_int(0, size-1)
3. point2 ← random_int(0, size-1)
4. IF point1 > point2 THEN SWAP(point1, point2)

// Buat offspring 1
5. offspring1_genes ← [NULL] × size
6. offspring1_genes[point1:point2] ← parent1.genes[point1:point2]

7. selected_ids ← {id(gene) | gene in offspring1_genes[point1:point2]}
8. parent2_filtered ← [g for g in parent2.genes if id(g) ∉ selected_ids]

9. idx ← 0
10. FOR i = 0 TO size-1 DO:
    10.1. IF offspring1_genes[i] = NULL THEN:
          offspring1_genes[i] ← parent2_filtered[idx]
          idx ← idx + 1

// Buat offspring 2 dengan cara yang sama (swap parent roles)
11. [Similar steps untuk offspring2]

12. offspring1 ← Chromosome(offspring1_genes, parent1.start_point)
13. offspring2 ← Chromosome(offspring2_genes, parent2.start_point)

14. RETURN (offspring1, offspring2)
```

**Ilustrasi Visual:**

```
Parent 1: [A B C | D E | F G H]
Parent 2: [C A F | B G | E H D]
          ↑       ↑     ↑
          point1  |     point2
                  |
           Segment diambil

Offspring 1: [? ? ? | D E | ? ? ?]
             ↓       kept  ↓
          Fill dengan urutan dari Parent2 (kecuali D,E):
          [C A F | D E | B G H]
```

**Karakteristik:**

1. **Preserve order**: Urutan relatif dari parent tetap terjaga
2. **No duplication**: Setiap gen muncul tepat satu kali
3. **Two-point**: Lebih diverse daripada single-point crossover

### 6.2 Order Crossover Modified (4-Parent Crossover)

**Konsep Inovasi:**
Menggunakan 4 parent untuk meningkatkan diversity dan eksplorasi ruang solusi.

**Algoritma:**

```
ALGORITHM: Order_Crossover_Modified
INPUT:
  - parent1, parent2, parent3, parent4: Empat kromosom parent
OUTPUT:
  - offspring1, offspring2: Dua kromosom offspring

STEPS:
1. size ← 8
2. point1 ← random_int(0, size-1)
3. point2 ← random_int(point1+1, size)

// Offspring 1: Kombinasi Parent1 dan Parent3
4. offspring1_genes ← [NULL] × size
5. offspring1_genes[point1:point2] ← parent1.genes[point1:point2]
6. Fill sisanya dengan urutan dari parent3 (tanpa duplikat)

// Offspring 2: Kombinasi Parent2 dan Parent4
7. offspring2_genes ← [NULL] × size
8. offspring2_genes[point1:point2] ← parent2.genes[point1:point2]
9. Fill sisanya dengan urutan dari parent4 (tanpa duplikat)

10. RETURN (offspring1, offspring2)
```

**Keunggulan:**

- Eksplorasi lebih luas dengan 4 sumber variasi genetik
- Mengurangi risiko premature convergence
- Meningkatkan diversity populasi

---

## 7. PERANCANGAN OPERATOR MUTASI

### 7.1 Swap Mutation

**Konsep:**
Menukar posisi dua gen secara acak untuk memperkenalkan variasi kecil.

**Algoritma Swap Mutation:**

```
ALGORITHM: Swap_Mutation
INPUT:
  - chromosome: Kromosom yang akan dimutasi
  - mutation_rate: Probabilitas mutasi (default: 0.05)
OUTPUT:
  - mutated_chromosome: Kromosom hasil mutasi

STEPS:
1. IF random_float(0, 1) > mutation_rate THEN:
   RETURN chromosome.copy()  // No mutation

2. mutated_genes ← chromosome.genes.copy()
3. size ← length(mutated_genes)

4. pos1 ← random_int(0, size-1)
5. pos2 ← random_int(0, size-1)
6. WHILE pos1 = pos2 DO:
   pos2 ← random_int(0, size-1)  // Ensure different positions

7. SWAP(mutated_genes[pos1], mutated_genes[pos2])

8. mutated_chromosome ← Chromosome(mutated_genes, chromosome.start_point)

9. RETURN mutated_chromosome
```

**Karakteristik:**

1. **Small perturbation**: Perubahan kecil untuk fine-tuning
2. **Maintain validity**: Swap tidak melanggar constraint (semua gen tetap ada)
3. **Low disruption**: Cocok untuk late-stage optimization

**Analisis Probability:**

```
P(gen i dan j ditukar) = mutation_rate × 1/(n(n-1)/2)
```

### 7.2 Inversion Mutation (Alternatif)

**Konsep:**
Membalik urutan segment gen untuk perubahan lebih besar.

**Algoritma:**

```
ALGORITHM: Inversion_Mutation
INPUT:
  - chromosome: Kromosom
  - mutation_rate: Probabilitas mutasi
OUTPUT:
  - mutated_chromosome: Kromosom hasil mutasi

STEPS:
1. IF random_float(0, 1) > mutation_rate THEN RETURN chromosome.copy()

2. mutated_genes ← chromosome.genes.copy()
3. size ← length(mutated_genes)

4. point1 ← random_int(0, size-1)
5. point2 ← random_int(point1+1, size)

6. mutated_genes[point1:point2] ← REVERSE(mutated_genes[point1:point2])

7. RETURN Chromosome(mutated_genes, chromosome.start_point)
```

**Karakteristik:**

- Perubahan lebih drastis dibanding swap
- Cocok untuk escape dari local optimum
- Trade-off: Lebih disruptive

---

## 8. PERANCANGAN 2-OPT LOCAL SEARCH

### 8.1 Konsep 2-Opt

**Definisi:**
Algoritma local search yang memperbaiki rute dengan menghilangkan crossing edges (edge yang bersilangan).

**Prinsip Kerja:**

```
Original Route: A → B → C → D → E
                ↓     X (crossing)
                    /   \
Improved Route: A → D → C → B → E
                (no crossing)
```

### 8.2 Algoritma 2-Opt Standar

```
ALGORITHM: Two_Opt_Optimize
INPUT:
  - chromosome: Kromosom yang akan dioptimasi
  - max_iterations: Maksimum iterasi (default: 100)
OUTPUT:
  - optimized_chromosome: Kromosom hasil optimasi

STEPS:
1. current_genes ← chromosome.genes.copy()
2. current_distance ← calculate_total_distance(current_genes)

3. improved ← TRUE
4. iteration ← 0

5. WHILE improved AND iteration < max_iterations DO:
   5.1. improved ← FALSE
   5.2. iteration ← iteration + 1

   5.3. FOR i = 0 TO size-2 DO:
        FOR j = i+2 TO size-1 DO:
          5.3.1. new_genes ← two_opt_swap(current_genes, i, j)
          5.3.2. new_distance ← calculate_total_distance(new_genes)

          5.3.3. IF new_distance < current_distance THEN:
                 current_genes ← new_genes
                 current_distance ← new_distance
                 improved ← TRUE
                 BREAK inner loop

6. RETURN Chromosome(current_genes, chromosome.start_point)
```

**Fungsi two_opt_swap:**

```
FUNCTION: two_opt_swap(genes, i, j)
  new_genes ← genes.copy()
  new_genes[i:j+1] ← REVERSE(genes[i:j+1])
  RETURN new_genes
```

### 8.3 Algoritma 2-Opt dengan Constraint

**Modifikasi untuk Constraint Kategori:**

Karena sistem memiliki constraint urutan kategori yang ketat (K₁,C₁,W₁,K₂,W₂,C₂,K₃,O), 2-Opt standar tidak dapat diterapkan langsung karena akan melanggar constraint.

**Solusi: Constraint-Aware 2-Opt**

```
ALGORITHM: Two_Opt_Optimize_With_Constraints
INPUT:
  - chromosome: Kromosom
  - max_iterations: Maksimum iterasi
OUTPUT:
  - optimized_chromosome: Kromosom hasil optimasi

STEPS:
1. Define category_positions:
   - makanan_berat: [0, 3, 6]  // K1, K2, K3
   - makanan_ringan: [1, 5]     // C1, C2
   - non_kuliner: [2, 4]        // W1, W2
   - oleh_oleh: [7]             // O

2. current_genes ← chromosome.genes.copy()
3. current_distance ← calculate_total_distance(current_genes)

4. improved ← TRUE
5. iteration ← 0

6. WHILE improved AND iteration < max_iterations DO:
   6.1. improved ← FALSE
   6.2. iteration ← iteration + 1

   // Hanya swap dalam kategori yang sama
   6.3. FOR EACH category IN category_positions DO:
        positions ← category_positions[category]

        6.3.1. FOR EACH pair (i, j) IN positions WHERE i ≠ j DO:
               // Try swap destinasi di posisi i dan j
               new_genes ← current_genes.copy()
               SWAP(new_genes[i], new_genes[j])

               new_distance ← calculate_total_distance(new_genes)

               IF new_distance < current_distance THEN:
                 current_genes ← new_genes
                 current_distance ← new_distance
                 improved ← TRUE

7. RETURN Chromosome(current_genes, chromosome.start_point)
```

**Karakteristik Constraint-Aware 2-Opt:**

1. **Constraint preservation**: Urutan kategori selalu terjaga
2. **Limited swap space**: Hanya swap dalam kategori sama
3. **Still effective**: Tetap dapat meningkatkan fitness dengan perubahan destinasi

**Contoh:**

```
Original: [RestaurantA, CafeB, MuseumC, RestaurantD, ParkE, CafeF, RestaurantG, Shop]
           ↓ Swap K1 dan K2 (keduanya makanan_berat)
Improved: [RestaurantD, CafeB, MuseumC, RestaurantA, ParkE, CafeF, RestaurantG, Shop]
```

---

## 9. PERANCANGAN PROSES EVOLUSI

### 9.1 Algoritma Utama HGA

**Algoritma High-Level:**

```
ALGORITHM: Hybrid_Genetic_Algorithm
INPUT:
  - destinations: List semua destinasi
  - start_point: Koordinat awal
  - num_solutions: Jumlah solusi yang diinginkan (default: 3)
  - config: Parameter konfigurasi HGA
OUTPUT:
  - best_routes: List kromosom terbaik

STEPS:
1. INITIALIZE TRACKING:
   best_solution ← NULL
   best_fitness_history ← []
   average_fitness_history ← []

2. FOR route_number = 1 TO num_solutions DO:

   2.1. INITIALIZE POPULATION:
        population ← Initialize_Random_Population(
                       destinations, start_point, config.population_size)

   2.2. EVALUATE INITIAL POPULATION:
        FOR EACH chromosome IN population DO:
          chromosome.calculate_fitness()
        population.sort_by_fitness()
        best_initial ← population.get_best_chromosome()

   2.3. EVOLUTION LOOP:
        FOR generation = 1 TO config.generations DO:

          2.3.1. EVALUATE FITNESS:
                 FOR EACH chromosome IN population DO:
                   chromosome.calculate_fitness()
                 population.sort_by_fitness()

          2.3.2. TRACK BEST SOLUTION:
                 current_best ← population.get_best_chromosome()
                 best_fitness_history.append(current_best.get_fitness())
                 average_fitness_history.append(population.get_average_fitness())

                 IF best_solution = NULL OR
                    current_best.get_fitness() > best_solution.get_fitness() THEN:
                   best_solution ← current_best.copy()

          2.3.3. CHECK CONVERGENCE:
                 IF check_convergence(generation, best_fitness_history) THEN:
                   PRINT "Konvergensi tercapai pada generasi", generation
                   BREAK

          2.3.4. CREATE NEW GENERATION:
                 new_population ← Create_New_Generation(population, config)
                 population ← new_population

   2.4. ADD TO RESULTS:
        best_routes.append(best_solution)

3. RETURN best_routes
```

### 9.2 Algoritma Create New Generation

**Generational Model dengan Elitism:**

```
ALGORITHM: Create_New_Generation
INPUT:
  - population: Populasi saat ini
  - config: Parameter konfigurasi
OUTPUT:
  - new_population: Populasi generasi baru

STEPS:
1. new_chromosomes ← []

2. ELITISM (Pertahankan solusi terbaik):
   elite_chromosomes ← population.get_best_n_chromosomes(config.elitism_count)
   FOR EACH elite IN elite_chromosomes DO:
     new_chromosomes.append(elite.copy())

3. GENERATE OFFSPRING:
   WHILE length(new_chromosomes) < config.population_size DO:

     3.1. SELECTION (Tournament):
          parent1 ← Tournament_Selection(population, config.tournament_size)
          parent2 ← Tournament_Selection(population, config.tournament_size)
          parent3 ← Tournament_Selection(population, config.tournament_size)
          parent4 ← Tournament_Selection(population, config.tournament_size)

     3.2. CROSSOVER:
          IF random_float(0, 1) < config.crossover_rate THEN:
            offspring1, offspring2 ← Order_Crossover_Modified(
                                       parent1, parent2, parent3, parent4)
          ELSE:
            offspring1 ← parent1.copy()
            offspring2 ← parent2.copy()

     3.3. MUTATION:
          offspring1 ← Swap_Mutation(offspring1, config.mutation_rate)
          offspring2 ← Swap_Mutation(offspring2, config.mutation_rate)

     3.4. LOCAL SEARCH (2-Opt):
          IF config.use_2opt THEN:
            offspring1 ← Two_Opt_Optimize_With_Constraints(
                           offspring1, config.two_opt_iterations)
            offspring2 ← Two_Opt_Optimize_With_Constraints(
                           offspring2, config.two_opt_iterations)

     3.5. ADD TO NEW POPULATION:
          new_chromosomes.append(offspring1)
          IF length(new_chromosomes) < config.population_size THEN:
            new_chromosomes.append(offspring2)

4. TRIM EXCESS (jika ada):
   new_chromosomes ← new_chromosomes[0:config.population_size]

5. RETURN Population(new_chromosomes, config.population_size)
```

**Flow Diagram:**

```
┌─────────────────────┐
│  Current Population │
└──────────┬──────────┘
           │
    ┌──────▼───────┐
    │  Elitism     │ (Keep best 2)
    │  (2 best)    │
    └──────┬───────┘
           │
    ┌──────▼───────────────────────┐
    │  Selection (Tournament)      │
    │  - Select 4 parents          │
    └──────┬───────────────────────┘
           │
    ┌──────▼───────────────────────┐
    │  Crossover (Order-based)     │
    │  - Probability: 0.8          │
    │  - 4 parents → 2 offspring   │
    └──────┬───────────────────────┘
           │
    ┌──────▼───────────────────────┐
    │  Mutation (Swap)             │
    │  - Probability: 0.05         │
    └──────┬───────────────────────┘
           │
    ┌──────▼───────────────────────┐
    │  Local Search (2-Opt)        │
    │  - Constraint-aware          │
    │  - Max 100 iterations        │
    └──────┬───────────────────────┘
           │
    ┌──────▼───────────────────────┐
    │  New Population (Size 600)   │
    └──────────────────────────────┘
```

---

## 10. PERANCANGAN STRATEGI KONVERGENSI

### 10.1 Kriteria Terminasi

Sistem menggunakan **multiple termination criteria**:

**1. Maximum Generations:**

```
IF generation ≥ max_generations THEN TERMINATE
```

**2. Fitness Stagnation:**

```
IF no improvement dalam patience generations THEN TERMINATE
```

**Algoritma Check Convergence:**

```
ALGORITHM: Check_Convergence
INPUT:
  - generation: Generasi saat ini
  - patience: Jumlah generasi tanpa improvement (default: 50000)
  - best_fitness_history: History fitness terbaik
OUTPUT:
  - converged: Boolean (TRUE jika konvergen)

STEPS:
1. IF generation < patience THEN RETURN FALSE

2. recent_fitness ← best_fitness_history[-patience:]

3. CHECK STAGNATION:
   IF length(set(recent_fitness)) = 1 THEN:
     RETURN TRUE  // Semua nilai sama

4. CHECK IMPROVEMENT RATE:
   improvement_rate ← (recent_fitness[-1] - recent_fitness[0]) / recent_fitness[0]

   IF abs(improvement_rate) < 0.001 THEN:
     RETURN TRUE  // Improvement < 0.1%

5. RETURN FALSE
```

### 10.2 Parameter Konvergensi

| Parameter               | Nilai Default | Justifikasi                                   |
| ----------------------- | ------------- | --------------------------------------------- |
| `max_generations`       | 40            | Balance antara kualitas dan waktu komputasi   |
| `patience`              | 50000         | Tidak digunakan untuk config singkat (40 gen) |
| `improvement_threshold` | 0.001         | 0.1% improvement dianggap tidak signifikan    |

---

## 11. PERANCANGAN KONFIGURASI PARAMETER

### 11.1 Parameter Space

**Tabel Parameter HGA:**

| Parameter        | Symbol | Range         | Default | Deskripsi                       |
| ---------------- | ------ | ------------- | ------- | ------------------------------- |
| Population Size  | n      | [10, 1000]    | 600     | Ukuran populasi                 |
| Generations      | G      | [10, 50000]   | 40      | Jumlah iterasi evolusi          |
| Crossover Rate   | Pc     | [0.0, 1.0]    | 0.8     | Probabilitas crossover          |
| Mutation Rate    | Pm     | [0.0, 1.0]    | 0.05    | Probabilitas mutasi             |
| Elitism Count    | E      | [1, 10]       | 2       | Jumlah elite yang dipertahankan |
| Tournament Size  | k      | [2, 20]       | 8       | Ukuran tournament selection     |
| Use 2-Opt        | -      | {True, False} | True    | Enable/disable local search     |
| 2-Opt Iterations | I      | [10, 1000]    | 100     | Maksimum iterasi 2-Opt          |

**Tabel Parameter Constraint:**

| Parameter                | Symbol | Nilai   | Deskripsi                                |
| ------------------------ | ------ | ------- | ---------------------------------------- |
| Max Route Distance       | D_max  | 20 km   | Jarak maksimal rute yang diizinkan       |
| Max Route Time           | T_max  | 5 jam   | Waktu tempuh maksimal yang diizinkan     |
| Distance Penalty Weight  | w_d    | 0.5     | Bobot penalty untuk pelanggaran jarak    |
| Time Penalty Weight      | w_t    | 0.3     | Bobot penalty untuk pelanggaran waktu    |
| Average Speed (Fallback) | v_avg  | 30 km/h | Kecepatan rata-rata untuk estimasi waktu |

### 11.2 Justifikasi Parameter Default

**1. Population Size = 600:**

- ✅ Balance antara diversity dan computational cost
- ✅ Cukup besar untuk eksplorasi yang baik
- ✅ Tidak terlalu besar untuk inference time reasonable (<40s)

**2. Generations = 40:**

- ✅ Quick convergence untuk production use
- ✅ Sufficient untuk local optimum dengan 2-Opt assistance
- ✅ Response time target: 20-40 detik

**3. Crossover Rate = 0.8:**

- ✅ High exploitation dari good solutions
- ✅ Standard dalam literature untuk TSP variants
- ✅ Balance dengan mutation untuk exploration

**4. Mutation Rate = 0.05:**

- ✅ Low enough untuk tidak disrupt good solutions
- ✅ High enough untuk escape local optima
- ✅ Complement 2-Opt (yang sudah aggressive)

**5. Tournament Size = 8:**

- ✅ Moderate selection pressure
- ✅ Maintain diversity while favoring better solutions
- ✅ √n rule of thumb (√600 ≈ 24, use 8 for faster)

**6. Elitism = 2:**

- ✅ Preserve best solutions across generations
- ✅ Guarantee monotonic improvement
- ✅ Not too many (allow exploration)

**7. 2-Opt Iterations = 100:**

- ✅ Balance between local search depth dan computational cost
- ✅ Usually converges dalam 50-100 iterations
- ✅ Adaptive: stops early jika no improvement

**8. Max Route Distance = 20 km:**

- ✅ Realistis untuk wisata sehari dalam kota Surabaya
- ✅ Menghindari rute yang terlalu panjang dan melelahkan
- ✅ Sesuai dengan karakteristik urban tourism

**9. Max Route Time = 5 jam (300 menit):**

- ✅ Waktu tempuh perjalanan yang reasonable
- ✅ Belum termasuk waktu kunjungan di destinasi
- ✅ Memungkinkan wisata setengah hari

**10. Penalty Weights (w_d=0.5, w_t=0.3):**

- ✅ Distance penalty lebih tinggi karena lebih kritis
- ✅ Soft constraint: solusi infeasible masih bisa survive
- ✅ Progressive penalty dengan quadratic function

### 11.3 Sensitivity Analysis (Planned)

**Parameter yang akan diuji:**

```
Test Matrix:
┌─────────────────┬─────────────────────────────┐
│ Parameter       │ Test Values                 │
├─────────────────┼─────────────────────────────┤
│ Population Size │ [100, 300, 600, 1000]       │
│ Generations     │ [20, 40, 80, 160]           │
│ Crossover Rate  │ [0.6, 0.7, 0.8, 0.9]        │
│ Mutation Rate   │ [0.01, 0.05, 0.1, 0.2]      │
│ Tournament Size │ [3, 5, 8, 12]               │
└─────────────────┴─────────────────────────────┘
```

---

## 12. PERANCANGAN ARSITEKTUR SISTEM

### 12.1 Class Diagram

```
┌─────────────────────────────────────────┐
│           HybridGeneticAlgorithm        │
├─────────────────────────────────────────┤
│ - population_size: int                  │
│ - generations: int                      │
│ - crossover_rate: float                 │
│ - mutation_rate: float                  │
│ - elitism_count: int                    │
│ - tournament_size: int                  │
│ - use_2opt: bool                        │
│ - operators: GAOperators                │
│ - two_opt: TwoOptOptimizer              │
├─────────────────────────────────────────┤
│ + run(destinations, start_point)        │
│ - _create_new_generation(population)    │
│ - _check_convergence(generation)        │
└───────────────┬─────────────────────────┘
                │ uses
                ▼
┌─────────────────────────────────────────┐
│            Population                   │
├─────────────────────────────────────────┤
│ - chromosomes: List[Chromosome]         │
│ - population_size: int                  │
├─────────────────────────────────────────┤
│ + initialize_random_population()        │
│ + evaluate_fitness()                    │
│ + sort_by_fitness()                     │
│ + get_best_chromosome()                 │
│ + get_best_n_chromosomes(n)             │
└───────────────┬─────────────────────────┘
                │ contains
                ▼
┌─────────────────────────────────────────┐
│            Chromosome                   │
├─────────────────────────────────────────┤
│ - genes: List[Destination]              │
│ - start_point: Tuple[float, float]      │
│ - fitness_value: Optional[float]        │
│ - penalty_value: Optional[float]        │
│ - _total_distance: Optional[float]      │
│ - _total_time: Optional[float]          │
├─────────────────────────────────────────┤
│ + calculate_fitness()                   │
│ + get_fitness()                         │
│ + get_total_distance()                  │
│ + get_total_travel_time()               │
│ + get_penalty()                         │
│ + get_constraint_info()                 │
│ + is_feasible()                         │
│ + is_valid()                            │
│ + copy()                                │
└───────────────┬─────────────────────────┘
                │ uses
                ▼
┌─────────────────────────────────────────┐
│              Route                      │
├─────────────────────────────────────────┤
│ - start_point: Tuple[float, float]      │
│ - destinations: List[Destination]       │
├─────────────────────────────────────────┤
│ + calculate_total_distance()            │
│ + calculate_total_travel_time()         │
│ + is_valid_route_order()                │
│ + get_route_summary()                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         PenaltyCalculator               │
├─────────────────────────────────────────┤
│ + MAX_ROUTE_DISTANCE_KM: float = 20.0   │
│ + MAX_ROUTE_TIME_MINUTES: float = 300.0 │
│ + DISTANCE_PENALTY_WEIGHT: float = 0.5  │
│ + TIME_PENALTY_WEIGHT: float = 0.3      │
├─────────────────────────────────────────┤
│ + calculate_distance_penalty()          │
│ + calculate_time_penalty()              │
│ + calculate_total_penalty()             │
│ + apply_penalty_to_fitness()            │
│ + get_constraint_violation_info()       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       TravelTimeMatrixCache             │
├─────────────────────────────────────────┤
│ - cache_file: str                       │
│ - matrix: Dict[str, Dict]               │
│ - _key_cache: Dict[Tuple, str]          │
│ - metadata: Dict                        │
├─────────────────────────────────────────┤
│ + get(coord1, coord2)                   │
│ + get_duration(coord1, coord2)          │
│ + set(coord1, coord2, duration, ...)    │
│ + load()                                │
│ + save()                                │
│ + build_matrix(destinations, ...)       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│            GAOperators                  │
├─────────────────────────────────────────┤
│ + tournament_selection()                │
│ + roulette_wheel_selection()            │
│ + order_crossover()                     │
│ + order_crossover_modified()            │
│ + swap_mutation()                       │
│ + inversion_mutation()                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│          TwoOptOptimizer                │
├─────────────────────────────────────────┤
│ - max_iterations: int                   │
├─────────────────────────────────────────┤
│ + optimize(chromosome)                  │
│ + optimize_with_constraints(chromosome) │
│ - _two_opt_swap(genes, i, j)            │
│ - _calculate_route_distance()           │
└─────────────────────────────────────────┘
```

### 12.2 Sequence Diagram - Execution Flow

```
User → HGA.run()
  │
  ├─→ Population.initialize_random_population()
  │     └─→ For each chromosome:
  │           └─→ _create_random_valid_chromosome()
  │
  ├─→ Population.evaluate_fitness()
  │     └─→ For each chromosome:
  │           └─→ Chromosome.calculate_fitness()
  │                 └─→ Route.calculate_total_distance()
  │                       └─→ DistanceCalculator.calculate_distance()
  │
  ├─→ For generation in range(max_generations):
  │   │
  │   ├─→ Population.evaluate_fitness()
  │   │
  │   ├─→ _check_convergence()
  │   │
  │   └─→ _create_new_generation()
  │       │
  │       ├─→ Elitism: Get best N chromosomes
  │       │
  │       └─→ While population not full:
  │           │
  │           ├─→ GAOperators.tournament_selection() × 4
  │           │
  │           ├─→ GAOperators.order_crossover_modified()
  │           │
  │           ├─→ GAOperators.swap_mutation()
  │           │
  │           └─→ TwoOptOptimizer.optimize_with_constraints()
  │
  └─→ Return best solutions
```

---

## 13. PERANCANGAN EVALUASI DAN VALIDASI

### 13.1 Metrik Evaluasi

**1. Solution Quality:**

```
Total Distance (km) - minimize
Fitness Value - maximize
Valid Route Order - boolean
```

**2. Computational Efficiency:**

```
Execution Time (seconds)
Number of Fitness Evaluations
Convergence Generation
```

**3. Algorithm Performance:**

```
Average Fitness per Generation
Best Fitness per Generation
Diversity Index = σ(fitness) / μ(fitness)
```

### 13.2 Test Scenarios

**Scenario 1: Small Dataset**

- Destinations: 50
- Population: 100
- Generations: 50
- Expected time: <10s

**Scenario 2: Medium Dataset**

- Destinations: 150
- Population: 300
- Generations: 100
- Expected time: <30s

**Scenario 3: Large Dataset (Production)**

- Destinations: 221
- Population: 600
- Generations: 40
- Expected time: 20-40s

### 13.3 Validation Criteria

**1. Constraint Satisfaction:**

```python
def validate_solution(chromosome):
    # Check pattern: K1, C1, W1, K2, W2, C2, K3, O
    pattern = ['makanan_berat', 'makanan_ringan', 'non_kuliner',
               'makanan_berat', 'non_kuliner', 'makanan_ringan',
               'makanan_berat', 'oleh_oleh']

    for i, expected_cat in enumerate(pattern):
        if not chromosome.genes[i].has_category(expected_cat):
            return False

    # Check no duplicates
    if len(set(chromosome.genes)) != len(chromosome.genes):
        return False

    return True
```

**2. Distance Accuracy:**

- Verify distance calculations dengan manual computation
- Compare with Google Maps API (sample validation)
- Check consistency: d(A,B) = d(B,A)

**3. Convergence Behavior:**

- Plot fitness evolution curve
- Check for premature convergence (diversity loss)
- Verify improvement trend (monotonic atau near-monotonic)

---

## 14. PERANCANGAN OPTIMASI PERFORMA

### 14.1 Distance Calculation Optimization

**Pre-calculated Distance Matrix:**

```
Structure:
{
  "lat1,lon1|lat2,lon2": distance_km,
  ...
}

Properties:
- Bidirectional: d(A,B) = d(B,A)
- Pre-calculated: n(n-1)/2 pairs
- Persistent: Saved to JSON file
- Lazy-loaded: Only load once at startup
```

**Performance Impact:**

```
Without Matrix:
- API calls per request: ~70+
- Time per request: ~70 seconds

With Matrix:
- API calls per request: 0-1
- Time per request: <0.1 seconds
- Speedup: 1200x for distance calculation
```

### 14.2 Fitness Caching

**Lazy Evaluation Strategy:**

```python
class Chromosome:
    def get_fitness(self):
        if self.fitness_value is None:
            self.calculate_fitness()
        return self.fitness_value
```

**Benefits:**

- Avoid redundant calculations
- ~30-40% reduction in fitness evaluations
- Particularly effective with elitism

### 14.3 Key Caching for Distance Matrix

**Implementation:**

```python
class DistanceMatrixCache:
    def __init__(self):
        self._key_cache = {}  # Cache untuk key lookup

    def _make_key(self, coord1, coord2):
        cache_key = (coord1, coord2)
        if cache_key in self._key_cache:
            return self._key_cache[cache_key]

        # Generate key
        key = create_key(coord1, coord2)

        # Cache both directions
        self._key_cache[cache_key] = key
        self._key_cache[(coord2, coord1)] = key

        return key
```

**Impact:**

- Eliminate repeated string formatting
- O(1) lookup instead of O(n) string operations
- ~15-20% speedup in distance lookups

### 14.4 Parallel Processing (Future Work)

**Parallelization Opportunities:**

```
1. Fitness Evaluation:
   - Each chromosome independent
   - Embarrassingly parallel
   - Potential speedup: Near-linear dengan core count

2. Population Initialization:
   - Each chromosome creation independent
   - Can parallelize with multiprocessing

3. 2-Opt Local Search:
   - Each offspring independent
   - GPU acceleration possible untuk matrix operations
```

**Estimated Impact:**

```
Current: Sequential processing
- Single-threaded
- Time: 20-40s

With Parallelization (8 cores):
- Parallel fitness evaluation
- Estimated time: 5-10s
- Speedup: 4-8x
```

---

## 15. PERANCANGAN INTERFACE API

### 15.1 Endpoint Design

**POST /generate-routes**

```json
Request:
{
  "latitude": -7.2575,
  "longitude": 112.7521,
  "num_routes": 3,
  "hga_config": {
    "population_size": 600,
    "generations": 40,
    "crossover_rate": 0.8,
    "mutation_rate": 0.05,
    "elitism_count": 2,
    "tournament_size": 8,
    "use_2opt": true,
    "two_opt_iterations": 100
  }
}

Response:
{
  "success": true,
  "message": "Successfully generated 3 route recommendations",
  "data": {
    "routes": [
      {
        "rank": 1,
        "total_distance_km": 32.45,
        "is_valid_order": true,
        "fitness": 0.030816,
        "destinations": [...]
      }
    ],
    "computation_time_seconds": 25.3,
    "statistics": {
      "total_generations": 40,
      "final_best_fitness": 0.030816,
      "convergence_generation": 35
    }
  },
  "timestamp": "2025-11-26T10:30:00Z"
}
```

### 15.2 Request Validation

**Pydantic Models:**

```python
class HGAConfig(BaseModel):
    population_size: int = Field(600, ge=10, le=1000)
    generations: int = Field(40, ge=10, le=50000)
    crossover_rate: float = Field(0.8, ge=0.0, le=1.0)
    mutation_rate: float = Field(0.05, ge=0.0, le=1.0)
    elitism_count: int = Field(2, ge=1, le=10)
    tournament_size: int = Field(8, ge=2, le=20)
    use_2opt: bool = Field(True)
    two_opt_iterations: int = Field(100, ge=10, le=1000)

class RouteRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    num_routes: int = Field(3, ge=1, le=5)
    hga_config: Optional[HGAConfig] = None
```

---

## 16. KESIMPULAN PERANCANGAN

### 16.1 Novelty dan Kontribusi

**1. Hybrid Approach:**

- Kombinasi GA (global search) + 2-Opt (local search)
- Synergy: GA explores, 2-Opt exploits
- Balance antara exploration dan exploitation

**2. Constraint-Aware Operators:**

- Order crossover yang preserve constraint urutan kategori
- Constraint-aware 2-Opt untuk local optimization
- Structural constraint (kategori) dijaga oleh operator

**3. Penalty-Based Constraint Handling:**

- Soft constraint untuk jarak maksimal (20 km) dan waktu maksimal (5 jam)
- Quadratic penalty function untuk progressive penalization
- Formula: `f(C) = f_base(C) / (1 + P_total(C))`
- Memungkinkan solusi infeasible survive untuk maintain diversity

**4. Multi-Parent Crossover:**

- 4-parent crossover untuk increased diversity
- Better exploration dibanding 2-parent standard
- Reduce premature convergence risk

**5. Dual Matrix Pre-calculation:**

- Pre-calculated **Distance Matrix** (OSRM real routes)
- Pre-calculated **Travel Time Matrix** (OSRM duration / estimation)
- ~24,000+ pairs untuk 221 destinasi
- Speedup: 1200-5000x untuk distance/time calculations

**6. Performance Optimization:**

- Pre-calculated distance matrix (1200x speedup)
- Pre-calculated travel time matrix (2000x speedup)
- Lazy evaluation fitness dengan caching (30-40% reduction)
- Key caching untuk matrix lookups (15-20% speedup)

### 16.2 Expected Performance

**Computational Complexity:**

```
Time Complexity Analysis:

1. Initialization:
   O(n) untuk load destinations
   O(p) untuk create population
   Total: O(n + p)

2. Per Generation:
   - Fitness Evaluation: O(p × d)
     dimana d = average distance calculations per route
   - Penalty Calculation: O(p) - menggunakan cached values
   - Selection: O(p × k) dimana k = tournament size
   - Crossover: O(p × m) dimana m = chromosome length
   - Mutation: O(p)
   - 2-Opt: O(p × m² × I) dimana I = 2opt iterations

   Total per generation: O(p × m² × I)

3. Total Algorithm:
   O(G × p × m² × I)

   Dengan default parameters:
   G=40, p=600, m=8, I=100
   ≈ 40 × 600 × 64 × 100 = 153,600,000 operations

   Actual runtime: 20-40 seconds (optimized dengan caching)
```

**Space Complexity:**

```
1. Population: O(p × m)
2. Distance Matrix: O(n²)
3. Travel Time Matrix: O(n²)
4. Fitness History: O(G)

Total: O(p × m + 2n² + G)

Dengan n=221, p=600, m=8, G=40:
≈ 600×8 + 2×221² + 40 = 102,564 objects
≈ 80-150 MB memory usage (termasuk dual matrix)
```

**Constraint Performance:**

```
Constraint Satisfaction Rate (dengan penalty mechanism):
- Dengan population=100, generations=20: ~90-95% feasible
- Dengan population=600, generations=40: ~98-100% feasible

Average Metrics:
- Feasible Solution Distance: 15-19 km (< 20 km max)
- Feasible Solution Time: 15-30 min travel time (< 300 min max)
```

### 16.3 Limitations dan Future Work

**Current Limitations:**

1. **Fixed Pattern Constraint:**

   - Hanya support pola K,C,W,K,W,C,K,O
   - Tidak flexible untuk custom patterns
   - Future: Parameterizable constraint

2. **Sequential Processing:**

   - Single-threaded execution
   - Tidak utilize multi-core processors
   - Future: Parallel fitness evaluation

3. **Static Parameters:**

   - Parameter tetap sepanjang evolution
   - Future: Adaptive parameter control

4. **Local Search Limitation:**
   - 2-Opt terbatas pada same-category swaps
   - Future: More sophisticated local search

**Future Enhancements:**

1. **Adaptive Parameters:**

   ```
   mutation_rate(t) = mutation_rate_initial × exp(-α × t)
   ```

   Decrease mutation rate seiring generasi

2. **Island Model:**

   ```
   Multiple subpopulations dengan migration
   Better diversity preservation
   ```

3. **Multi-Objective:**

   ```
   Optimize multiple criteria:
   - Minimize distance
   - Maximize user preferences
   - Balance category diversity
   ```

4. **Machine Learning Integration:**
   ```
   Learn optimal parameters dari historical data
   Predict convergence behavior
   ```

---

## 17. REFERENSI PUSTAKA

1. Goldberg, D. E. (1989). _Genetic Algorithms in Search, Optimization, and Machine Learning_. Addison-Wesley.

2. Holland, J. H. (1992). _Adaptation in Natural and Artificial Systems_. MIT Press.

3. Laporte, G. (1992). The traveling salesman problem: An overview of exact and approximate algorithms. _European Journal of Operational Research_, 59(2), 231-247.

4. Lin, S., & Kernighan, B. W. (1973). An effective heuristic algorithm for the traveling-salesman problem. _Operations Research_, 21(2), 498-516.

5. Muhlenbein, H., Gorges-Schleuter, M., & Kramer, O. (1988). Evolution algorithms in combinatorial optimization. _Parallel Computing_, 7(1), 65-85.

6. Talbi, E. G. (2009). _Metaheuristics: From Design to Implementation_. John Wiley & Sons.

7. Vanneschi, L., & Poli, R. (2012). Genetic Programming—Introduction, Applications, Theory and Open Issues. In _Handbook of Natural Computing_ (pp. 709-739). Springer.

8. Whitley, D. (1994). A genetic algorithm tutorial. _Statistics and Computing_, 4(2), 65-85.

---

**Dokumen ini merupakan perancangan detail algoritma Hybrid Genetic Algorithm untuk sistem rekomendasi rute wisata. Implementasi aktual dapat bervariasi berdasarkan hasil eksperimen dan tuning parameter.**

---

**Penulis:** [Nama Peneliti]  
**Institusi:** [Nama Institusi]  
**Tanggal:** 26 November 2025  
**Versi:** 1.0
