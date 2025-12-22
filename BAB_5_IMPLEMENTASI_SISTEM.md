# BAB V IMPLEMENTASI SISTEM

## 5.1 Pengembangan Algoritma Sistem Rekomendasi Rute

### 5.1.1 Arsitektur Algoritma

Pengembangan algoritma sistem rekomendasi rute wisata pada penelitian ini menggunakan pendekatan _Hybrid Genetic Algorithm_ (HGA) yang diintegrasikan dengan metode _2-Opt Local Search_. Arsitektur algoritma dirancang dengan konsep modular dan berorientasi objek (_Object-Oriented Programming_) untuk memudahkan pengembangan, pemeliharaan, dan pengujian sistem.

Berdasarkan _class diagram_ yang telah dirancang, sistem terdiri dari beberapa komponen utama:

1. **Model Layer**: Terdiri dari class `Destination` dan `Route` yang merepresentasikan entitas data dalam sistem.
2. **Algorithm Core Layer**: Mencakup `Chromosome`, `Population`, `GAOperators`, dan `TwoOptOptimizer` yang mengimplementasikan logika inti algoritma genetika.
3. **Orchestration Layer**: Class `HybridGeneticAlgorithm` yang mengkoordinasikan seluruh proses evolusi algoritma.
4. **Utility Layer**: `DataLoader` dan `DistanceUtils` yang menyediakan fungsi-fungsi pendukung.
5. **Application Layer**: `TourismRouteRecommendationSystem` dan `FastAPI_App` yang menyediakan interface untuk pengguna.

### 5.1.2 Proses Rekomendasi Rute

Proses rekomendasi rute dimulai ketika client mengirimkan permintaan (_request_) melalui API endpoint dengan menyertakan data lokasi pengguna (latitude dan longitude) serta jumlah rute alternatif yang diinginkan. Berikut adalah alur lengkap proses rekomendasi:

#### 5.1.2.1 Penerimaan Request dari Client

Client mengirimkan HTTP POST request ke endpoint `/generate-routes` dengan format JSON:

```json
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
```

Data request ini diterima oleh class `FastAPI_App` dan divalidasi menggunakan model `LocationRequest` yang memastikan:

- Koordinat latitude berada dalam rentang -90° hingga 90°
- Koordinat longitude berada dalam rentang -180° hingga 180°
- Jumlah rute yang diminta berada dalam rentang 1 hingga 5
- Parameter konfigurasi HGA sesuai dengan constraint yang telah ditetapkan

#### 5.1.2.2 Inisialisasi Sistem dan Load Data

Setelah request tervalidasi, sistem melakukan inisialisasi dengan langkah-langkah:

1. **Load Destinasi Wisata**: Class `DataLoader` membaca file `data_wisata.jsonl` yang berisi 162 destinasi wisata di Surabaya dengan atribut:

   - `place_id`: Identifier unik destinasi
   - `nama_destinasi`: Nama tempat wisata
   - `kategori`: List kategori (makanan_berat, makanan_ringan, wisata_alam, oleh_oleh, dll.)
   - `latitude` dan `longitude`: Koordinat geografis
   - `alamat`: Alamat lengkap
   - `image_url`: URL gambar destinasi
   - `deskripsi`: Deskripsi singkat destinasi

2. **Grouping Destinasi**: Destinasi dikelompokkan berdasarkan kategori untuk memudahkan pemilihan gen yang valid:

   - **K (Kuliner/Makanan Berat)**: Destinasi dengan kategori `makanan_berat`
   - **C (Camilan/Makanan Ringan)**: Destinasi dengan kategori `makanan_ringan`
   - **W (Wisata)**: Destinasi dengan kategori `wisata_alam`, `wisata_budaya`, `wisata_religi`, `wisata_belanja`
   - **O (Oleh-oleh)**: Destinasi dengan kategori `oleh_oleh` atau all-category

3. **Inisialisasi Distance Matrix**: Sistem memuat _pre-calculated distance matrix_ yang berisi 24.881 pasangan jarak antar destinasi menggunakan data OSRM (OpenStreetMap Routing Machine) untuk menghindari perhitungan jarak real-time yang memakan waktu.

4. **Inisialisasi Travel Time Matrix**: Sistem memuat _travel time matrix_ yang berisi estimasi waktu tempuh antar destinasi dengan asumsi kecepatan rata-rata 30 km/jam untuk kendaraan bermotor di area urban.

#### 5.1.2.3 Inisialisasi Hybrid Genetic Algorithm

Class `HybridGeneticAlgorithm` diinisialisasi dengan parameter konfigurasi yang diterima dari client atau menggunakan nilai default:

```python
hga = HybridGeneticAlgorithm(
    population_size=600,           # Ukuran populasi kromosom
    generations=40,                # Jumlah iterasi evolusi
    crossover_rate=0.8,           # Probabilitas crossover
    mutation_rate=0.05,           # Probabilitas mutasi
    elitism_count=2,              # Jumlah solusi terbaik yang dipertahankan
    tournament_size=8,            # Ukuran tournament untuk seleksi
    use_2opt=True,                # Mengaktifkan optimasi 2-Opt
    two_opt_iterations=100        # Jumlah iterasi 2-Opt
)
```

Pada tahap ini, sistem juga menginisialisasi:

- Object `GAOperators` untuk operasi seleksi, crossover, dan mutasi
- Object `TwoOptOptimizer` untuk optimasi lokal rute
- List `best_fitness_history` untuk tracking evolusi fitness

#### 5.1.2.4 Eksekusi Algoritma HGA

Eksekusi algoritma HGA dilakukan melalui method `run()` yang merupakan orchestrator utama. Berikut adalah step-by-step detail proses algoritma:

**Step 1: Inisialisasi Populasi Awal**

Class `Population` melakukan inisialisasi 600 kromosom secara random dengan memastikan setiap kromosom valid:

```python
def initialize_random_population(destinations, start_point, grouped_destinations):
    chromosomes = []
    for _ in range(population_size):
        # Generate kromosom dengan constraint K,C,W,K,W,C,K,O
        genes = []

        # Posisi 1: K1 (Makanan Berat)
        genes.append(random.choice(grouped_destinations['K']))

        # Posisi 2: C1 (Makanan Ringan)
        genes.append(random.choice(grouped_destinations['C']))

        # Posisi 3: W1 (Wisata)
        w1 = random.choice(grouped_destinations['W'])
        genes.append(w1)

        # Posisi 4: K2 (Makanan Berat, berbeda dari K1)
        k_options = [k for k in grouped_destinations['K'] if k.place_id != genes[0].place_id]
        genes.append(random.choice(k_options))

        # Posisi 5: W2 (Wisata, berbeda dari W1)
        w_options = [w for w in grouped_destinations['W'] if w.place_id != w1.place_id]
        genes.append(random.choice(w_options))

        # Posisi 6: C2 (Makanan Ringan, berbeda dari C1)
        c_options = [c for c in grouped_destinations['C'] if c.place_id != genes[1].place_id]
        genes.append(random.choice(c_options))

        # Posisi 7: K3 (Makanan Berat, berbeda dari K1 dan K2)
        k3_options = [k for k in grouped_destinations['K']
                      if k.place_id not in [genes[0].place_id, genes[3].place_id]]
        genes.append(random.choice(k3_options))

        # Posisi 8: O (Oleh-oleh)
        genes.append(random.choice(grouped_destinations['O']))

        # Buat kromosom
        chromosome = Chromosome(genes, start_point)
        chromosomes.append(chromosome)

    return chromosomes
```

**Step 2: Evaluasi Fitness Populasi Awal**

Setiap kromosom dievaluasi fitness-nya menggunakan fungsi dengan penalty mechanism:

```python
def calculate_fitness(chromosome):
    # Hitung total jarak rute
    total_distance = chromosome.get_total_distance()

    # Hitung total waktu tempuh
    total_time = chromosome.get_total_travel_time()

    # Hitung base fitness (inverse distance)
    base_fitness = 1.0 / total_distance if total_distance > 0 else 0

    # Hitung penalty untuk constraint violations
    distance_penalty = 0
    time_penalty = 0

    # Constraint: Jarak maksimal 20 km
    if total_distance > 20.0:
        excess_distance = total_distance - 20.0
        distance_penalty = 0.5 * (excess_distance / 20.0) ** 2

    # Constraint: Waktu tempuh maksimal 300 menit (5 jam)
    if total_time > 300.0:
        excess_time = total_time - 300.0
        time_penalty = 0.3 * (excess_time / 300.0) ** 2

    # Total penalty
    total_penalty = distance_penalty + time_penalty

    # Penalized fitness
    penalized_fitness = base_fitness / (1 + total_penalty)

    return penalized_fitness
```

Populasi kemudian diurutkan berdasarkan fitness dari tertinggi ke terendah.

**Step 3: Loop Evolusi (Iterasi Generasi)**

Proses evolusi dilakukan selama 40 generasi dengan langkah-langkah berikut di setiap generasi:

**a. Elitism (Preservasi Solusi Terbaik)**

2 kromosom dengan fitness tertinggi langsung dimasukkan ke populasi baru tanpa modifikasi:

```python
new_population = []
# Simpan 2 kromosom terbaik
for i in range(elitism_count):
    new_population.append(current_population[i].copy())
```

**b. Selection (Seleksi Parent)**

Untuk mengisi sisa populasi (598 kromosom), dilakukan seleksi parent menggunakan _Tournament Selection_:

```python
def tournament_selection(population, tournament_size=8):
    # Pilih tournament_size kromosom secara random
    tournament = random.sample(population, tournament_size)

    # Return kromosom dengan fitness tertinggi
    return max(tournament, key=lambda c: c.get_fitness())
```

**c. Crossover (Rekombinasi Genetik)**

Dua parent yang terpilih dikombinasikan menggunakan _Order Crossover (OX)_ dengan probabilitas 0.8:

```python
def order_crossover(parent1, parent2):
    size = len(parent1.genes)

    # Pilih dua titik potong secara random
    point1, point2 = sorted(random.sample(range(size), 2))

    # Offspring 1: Ambil segmen dari parent1
    offspring1_genes = [None] * size
    offspring1_genes[point1:point2] = parent1.genes[point1:point2]

    # Isi posisi kosong dengan gen dari parent2 (menjaga urutan)
    parent2_filtered = [g for g in parent2.genes
                        if g.place_id not in [dest.place_id for dest in offspring1_genes[point1:point2]]]

    idx = 0
    for i in range(size):
        if offspring1_genes[i] is None:
            offspring1_genes[i] = parent2_filtered[idx]
            idx += 1

    # Offspring 2: Sebaliknya (parent role swap)
    offspring2_genes = [None] * size
    offspring2_genes[point1:point2] = parent2.genes[point1:point2]

    parent1_filtered = [g for g in parent1.genes
                        if g.place_id not in [dest.place_id for dest in offspring2_genes[point1:point2]]]

    idx = 0
    for i in range(size):
        if offspring2_genes[i] is None:
            offspring2_genes[i] = parent1_filtered[idx]
            idx += 1

    return (Chromosome(offspring1_genes, parent1.start_point),
            Chromosome(offspring2_genes, parent2.start_point))
```

**d. Mutation (Mutasi Genetik)**

Offspring hasil crossover mengalami mutasi dengan probabilitas 0.05 menggunakan _Swap Mutation_:

```python
def swap_mutation(chromosome):
    genes = chromosome.genes.copy()

    # Pilih dua posisi secara random
    pos1, pos2 = random.sample(range(len(genes)), 2)

    # Tukar posisi gen
    genes[pos1], genes[pos2] = genes[pos2], genes[pos1]

    # Buat kromosom baru dengan gen yang sudah dimutasi
    mutated = Chromosome(genes, chromosome.start_point)

    # Validasi constraint setelah mutasi
    if not mutated.is_valid():
        # Jika tidak valid, kembalikan kromosom original
        return chromosome

    return mutated
```

**e. Local Search dengan 2-Opt**

Setiap kromosom baru dioptimasi menggunakan algoritma _2-Opt_ untuk memperbaiki urutan destinasi:

```python
def two_opt_optimize(chromosome, max_iterations=100):
    current_genes = chromosome.genes.copy()
    current_distance = calculate_route_distance(chromosome.start_point, current_genes)

    improved = True
    iteration = 0

    while improved and iteration < max_iterations:
        improved = False

        # Coba semua kemungkinan swap 2 edge
        for i in range(1, len(current_genes) - 2):
            for j in range(i + 1, len(current_genes)):
                # Lakukan 2-opt swap
                new_genes = current_genes[:i] + current_genes[i:j+1][::-1] + current_genes[j+1:]

                # Hitung jarak baru
                new_distance = calculate_route_distance(chromosome.start_point, new_genes)

                # Jika lebih baik dan tetap valid, update
                if new_distance < current_distance:
                    temp_chromosome = Chromosome(new_genes, chromosome.start_point)
                    if temp_chromosome.is_valid():
                        current_genes = new_genes
                        current_distance = new_distance
                        improved = True
                        break

            if improved:
                break

        iteration += 1

    # Return kromosom yang sudah dioptimasi
    return Chromosome(current_genes, chromosome.start_point)
```

**f. Replacement (Penggantian Populasi)**

Populasi baru menggantikan populasi lama:

```python
current_population = new_population
```

**g. Tracking dan Logging**

Di setiap generasi, sistem mencatat:

- Best fitness dari populasi
- Best distance dari kromosom terbaik
- Status feasibility (apakah memenuhi constraint)

```python
best_chromosome = population.get_best_chromosome()
best_fitness_history.append(best_chromosome.get_fitness())

print(f"Gen {generation} - Best: {best_chromosome.get_total_distance():.2f} km, "
      f"Time: {best_chromosome.get_total_travel_time():.1f} min "
      f"[{'✓' if best_chromosome.is_feasible() else '✗'}]")
```

**Step 4: Ekstraksi Solusi Terbaik**

Setelah 40 generasi selesai, sistem mengekstrak 3 solusi terbaik (sesuai `num_routes`):

```python
# Sort populasi final berdasarkan fitness
population.sort_by_fitness()

# Ambil top-N solusi
best_chromosomes = population.chromosomes[:num_routes]
```

**Step 5: Rekalkulasi dengan OSRM Real-Time**

Sebelum hasil dikirim ke client, setiap solusi direkalkulasi menggunakan OSRM API untuk mendapatkan:

- Jarak real berdasarkan jalanan aktual
- Waktu tempuh real dengan memperhitungkan kondisi jalan
- Route geometry (polyline) untuk visualisasi di peta

```python
def recalculate_route_with_osrm(start_point, destinations):
    # Build koordinat waypoints
    coordinates = [f"{start_point[1]},{start_point[0]}"]  # lon,lat format OSRM
    for dest in destinations:
        coordinates.append(f"{dest.longitude},{dest.latitude}")

    # Call OSRM Route API
    coordinates_str = ";".join(coordinates)
    url = f"http://router.project-osrm.org/route/v1/driving/{coordinates_str}"
    params = {
        "overview": "full",
        "geometries": "polyline",
        "steps": "false"
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 200:
        data = response.json()
        route = data['routes'][0]

        return {
            'success': True,
            'total_distance_km': route['distance'] / 1000,  # meter to km
            'total_duration_minutes': route['duration'] / 60,  # second to minute
            'total_duration_hours': route['duration'] / 3600,
            'geometry': route['geometry']  # Encoded polyline
        }
    else:
        return {
            'success': False,
            'error': f"OSRM API error: {response.status_code}"
        }
```

**Step 6: Sorting Berdasarkan Jarak OSRM**

Setelah rekalkulasi, solusi diurutkan kembali berdasarkan jarak real dari OSRM (terpendek ke terpanjang):

```python
# Sort berdasarkan jarak OSRM
recommendations.sort(key=lambda x: x.get('total_distance_km', float('inf')))

# Update rank setelah sorting
for i, route in enumerate(recommendations):
    route['rank'] = i + 1
```

#### 5.1.2.5 Pembentukan Response

Sistem membentuk response JSON yang berisi:

```json
{
  "success": true,
  "message": "Successfully generated 3 route recommendations",
  "data": {
    "user_location": {
      "latitude": -7.2575,
      "longitude": 112.7521
    },
    "hga_config": {
      "population_size": 600,
      "generations": 40,
      "crossover_rate": 0.8,
      "mutation_rate": 0.05,
      "elitism_count": 2,
      "tournament_size": 8,
      "use_2opt": true,
      "two_opt_iterations": 100
    },
    "statistics": {
      "total_generations": 40,
      "best_distance_km": 16.6,
      "initial_fitness": 0.0221,
      "final_fitness": 0.0602,
      "improvement_percentage": 172.4
    },
    "routes": [
      {
        "rank": 1,
        "fitness": 0.0602,
        "total_distance_km": 16.6,
        "total_travel_time_minutes": 18.2,
        "total_travel_time_hours": 0.3,
        "osrm_recalculated": true,
        "osrm_route_geometry": "encoded_polyline_string",
        "google_maps_url": "https://www.google.com/maps/dir/...",
        "constraint_info": {
          "distance": {
            "value": 16.6,
            "max_allowed": 20.0,
            "violated": false,
            "excess": 0.0,
            "penalty": 0.0
          },
          "time": {
            "value_minutes": 18.2,
            "value_hours": 0.3,
            "max_allowed_minutes": 300.0,
            "violated": false,
            "excess_minutes": 0.0,
            "penalty": 0.0
          },
          "total_penalty": 0.0,
          "is_feasible": true
        },
        "destinations": [
          {
            "order": 1,
            "place_id": 42,
            "nama_destinasi": "Kampung Kue",
            "kategori": ["makanan_ringan"],
            "latitude": -7.323768814,
            "longitude": 112.769831,
            "alamat": "Jl. Rungkut Lor Gg. II No.1",
            "image_url": "https://...",
            "deskripsi": "Kampung Kue Rungkut..."
          }
          // ... 7 destinasi lainnya
        ]
      }
      // ... 2 rute lainnya
    ]
  },
  "timestamp": "2025-12-16T10:30:45.123456"
}
```

#### 5.1.2.6 Pengiriman Response ke Client

Response JSON dikirim kembali ke client melalui HTTP dengan status code 200 (OK). Client kemudian dapat:

- Menampilkan rute di peta menggunakan `osrm_route_geometry`
- Membuat link navigasi menggunakan `google_maps_url`
- Menampilkan detail destinasi dan estimasi waktu tempuh
- Mengevaluasi constraint violations jika ada

<!-- ### 5.1.3 Mekanisme Penalty dan Constraint Handling

Sistem mengimplementasikan mekanisme penalty untuk memastikan rute yang dihasilkan memenuhi dua constraint utama:

1. **Distance Constraint**: Jarak total rute maksimal 20 km
2. **Time Constraint**: Waktu tempuh total maksimal 300 menit (5 jam)

Formula penalty yang digunakan adalah *quadratic penalty*:

$$P_{distance} = 0.5 \times \left(\frac{d_{excess}}{d_{max}}\right)^2$$

$$P_{time} = 0.3 \times \left(\frac{t_{excess}}{t_{max}}\right)^2$$

$$P_{total} = P_{distance} + P_{time}$$

$$f_{penalized} = \frac{f_{base}}{1 + P_{total}}$$

Di mana:
- $d_{excess}$ = jarak yang melebihi batas (km)
- $d_{max}$ = batas jarak maksimal (20 km)
- $t_{excess}$ = waktu yang melebihi batas (menit)
- $t_{max}$ = batas waktu maksimal (300 menit)
- $f_{base}$ = fitness dasar (1/distance)
- $f_{penalized}$ = fitness setelah penalty

Mekanisme ini memastikan bahwa:
- Solusi yang melanggar constraint mendapat fitness lebih rendah
- Semakin besar pelanggaran, semakin besar penalty
- Algoritma cenderung evolve menuju solusi yang feasible

### 5.1.4 Validasi Constraint Kategori

Setiap kromosom divalidasi untuk memastikan urutan kategori destinasi sesuai pattern **K-C-W-K-W-C-K-O**:

```python
def is_valid_route_order(destinations):
    expected_pattern = [
        ['makanan_berat'],                    # Posisi 1: K1
        ['makanan_ringan'],                   # Posisi 2: C1
        ['wisata_alam', 'wisata_budaya',
         'wisata_religi', 'wisata_belanja'],  # Posisi 3: W1
        ['makanan_berat'],                    # Posisi 4: K2
        ['wisata_alam', 'wisata_budaya',
         'wisata_religi', 'wisata_belanja'],  # Posisi 5: W2
        ['makanan_ringan'],                   # Posisi 6: C2
        ['makanan_berat'],                    # Posisi 7: K3
        ['oleh_oleh', 'all']                  # Posisi 8: O
    ]

    # Check setiap posisi
    for i, dest in enumerate(destinations):
        valid_categories = expected_pattern[i]
        if not any(cat in dest.kategori for cat in valid_categories):
            return False

    # Check uniqueness
    k_ids = [destinations[0].place_id, destinations[3].place_id, destinations[6].place_id]
    if len(set(k_ids)) != 3:  # K1, K2, K3 harus berbeda
        return False

    c_ids = [destinations[1].place_id, destinations[5].place_id]
    if len(set(c_ids)) != 2:  # C1, C2 harus berbeda
        return False

    w_ids = [destinations[2].place_id, destinations[4].place_id]
    if len(set(w_ids)) != 2:  # W1, W2 harus berbeda
        return False

    # Check no duplicates
    all_ids = [d.place_id for d in destinations]
    if len(set(all_ids)) != len(all_ids):
        return False

    return True
``` -->

---

## 5.2 Integrasi Algoritma Sistem Rekomendasi Rute dengan Website

### 5.2.1 Arsitektur Integrasi

    Integrasi algoritma dengan website menggunakan arsitektur *RESTful API* dengan FastAPI sebagai backend framework. Arsitektur ini memungkinkan:
    - **Separation of Concerns**: Backend (algoritma) dan frontend (UI) terpisah
    - **Scalability**: Backend dapat di-scale secara independen
    - **Flexibility**: Frontend dapat diganti tanpa mengubah backend
    - **Interoperability**: API dapat diakses dari berbagai platform (web, mobile, desktop)

Diagram arsitektur integrasi:

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Web Browser / Mobile App                     │   │
│  │  ┌────────────────┐  ┌──────────────────────────┐   │   │
│  │  │  User Interface│  │   Map Visualization      │   │   │
│  │  │  - Input Form  │  │   - Google Maps          │   │   │
│  │  │  - Results     │  │   - Route Display        │   │   │
│  │  └────────────────┘  └──────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP POST Request (JSON)
                              │ {latitude, longitude, num_routes}
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               FastAPI Application                     │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Endpoint: POST /generate-routes               │  │   │
│  │  │  - Request Validation (LocationRequest)        │  │   │
│  │  │  - CORS Middleware                             │  │   │
│  │  │  - Error Handling                              │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Validated Request
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │    TourismRouteRecommendationSystem                  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  1. Load Destinations (DataLoader)             │  │   │
│  │  │  2. Initialize HGA with Config                 │  │   │
│  │  │  3. Execute Algorithm                          │  │   │
│  │  │  4. Format Results                             │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Best Chromosomes
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Algorithm Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Hybrid Genetic Algorithm (HGA)               │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Population → Selection → Crossover →          │  │   │
│  │  │  Mutation → 2-Opt → Evaluation → Repeat        │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  ┌───────────┐  ┌─────────────┐  ┌──────────────┐  │   │
│  │  │GAOperators│  │TwoOptOptimiz│  │  Population  │  │   │
│  │  │           │  │     er      │  │              │  │   │
│  │  └───────────┘  └─────────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Route Data
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Utility Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ┌─────────────────┐    ┌────────────────────────┐  │   │
│  │  │ DistanceUtils   │    │ PenaltyCalculator      │  │   │
│  │  │ - Haversine     │    │ - Distance Penalty     │  │   │
│  │  │ - OSRM API      │    │ - Time Penalty         │  │   │
│  │  │ - Matrix Cache  │    │ - Feasibility Check    │  │   │
│  │  └─────────────────┘    └────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ OSRM Recalculation
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   External Services                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     OSRM Route API (router.project-osrm.org)         │   │
│  │     - Real road distance calculation                 │   │
│  │     - Travel time estimation                         │   │
│  │     - Route geometry (polyline)                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Enriched Route Data
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Response Formation                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  JSON Response:                                       │   │
│  │  - Route rankings                                     │   │
│  │  - Distance & time metrics                           │   │
│  │  - Constraint info                                    │   │
│  │  - Google Maps URLs                                   │   │
│  │  - Destination details                                │   │
│  │  - OSRM geometry                                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Response (JSON)
                              ▼
                        ┌─────────────┐
                        │   Client    │
                        └─────────────┘
```

### 5.2.2 Implementasi Backend API

#### 5.2.2.1 Setup FastAPI Application

FastAPI application diinisialisasi dengan konfigurasi CORS dan lifespan management:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Global variable untuk cache destinations
destinations = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load data destinations
    global destinations
    print("Loading destinations data...")
    destinations = load_destinations_from_jsonl("./data/data_wisata.jsonl")
    print(f"Successfully loaded {len(destinations)} destinations")
    yield
    # Shutdown: Cleanup if needed
    print("API Server shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Tourism Route Recommendation API",
    description="API untuk rekomendasi rute wisata Surabaya menggunakan HGA",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware - Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 5.2.2.2 Request/Response Models

Pydantic models untuk validasi request dan response:

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class HGAConfig(BaseModel):
    population_size: Optional[int] = Field(600, ge=100, le=1000)
    generations: Optional[int] = Field(40, ge=20, le=200)
    crossover_rate: Optional[float] = Field(0.8, ge=0.0, le=1.0)
    mutation_rate: Optional[float] = Field(0.05, ge=0.0, le=1.0)
    elitism_count: Optional[int] = Field(2, ge=1, le=10)
    tournament_size: Optional[int] = Field(8, ge=2, le=20)
    use_2opt: Optional[bool] = True
    two_opt_iterations: Optional[int] = Field(100, ge=10, le=500)

class RouteRecommendationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    num_routes: Optional[int] = Field(3, ge=1, le=5)
    hga_config: Optional[HGAConfig] = None

    class Config:
        schema_extra = {
            "example": {
                "latitude": -7.2575,
                "longitude": 112.7521,
                "num_routes": 3
            }
        }

class DestinationInfo(BaseModel):
    order: int
    place_id: int
    nama_destinasi: str
    kategori: List[str]
    latitude: float
    longitude: float
    alamat: Optional[str]
    image_url: Optional[str]
    deskripsi: Optional[str]

class ConstraintInfo(BaseModel):
    distance: dict
    time: dict
    total_penalty: float
    is_feasible: bool

class RouteInfo(BaseModel):
    rank: int
    fitness: float
    total_distance_km: float
    total_travel_time_minutes: float
    total_travel_time_hours: float
    osrm_recalculated: bool
    osrm_route_geometry: Optional[str]
    google_maps_url: str
    constraint_info: ConstraintInfo
    destinations: List[DestinationInfo]

class RouteRecommendationResponse(BaseModel):
    success: bool
    message: str
    data: dict
    timestamp: str
```

#### 5.2.2.3 Main Endpoint Implementation

```python
@app.post("/generate-routes", response_model=RouteRecommendationResponse)
async def get_route_recommendations(request: RouteRecommendationRequest):
    """
    Generate route recommendations using HGA

    Returns:
        RouteRecommendationResponse with top N routes
    """
    try:
        # Validate destinations loaded
        if destinations is None:
            raise HTTPException(
                status_code=500,
                detail="Destinations data not loaded"
            )

        # Extract request data
        user_location = (request.latitude, request.longitude)
        num_routes = request.num_routes
        hga_config = request.hga_config or HGAConfig()

        # Initialize HGA
        hga = HybridGeneticAlgorithm(
            population_size=hga_config.population_size,
            generations=hga_config.generations,
            crossover_rate=hga_config.crossover_rate,
            mutation_rate=hga_config.mutation_rate,
            elitism_count=hga_config.elitism_count,
            tournament_size=hga_config.tournament_size,
            use_2opt=hga_config.use_2opt,
            two_opt_iterations=hga_config.two_opt_iterations
        )

        # Run HGA algorithm
        best_chromosomes = hga.run(
            destinations=destinations,
            start_point=user_location,
            num_solutions=num_routes
        )

        # Format results
        recommendations = []
        for i, chromosome in enumerate(best_chromosomes):
            route = Route(user_location, chromosome.genes)
            route_info = route.get_route_summary()

            # Generate Google Maps URL
            google_maps_url = generate_google_maps_url(
                user_location,
                chromosome.genes
            )
            route_info['google_maps_url'] = google_maps_url

            # Recalculate with OSRM
            osrm_data = recalculate_route_with_osrm(
                user_location,
                chromosome.genes
            )

            if osrm_data['success']:
                route_info['total_distance_km'] = osrm_data['total_distance_km']
                route_info['total_travel_time_minutes'] = osrm_data['total_duration_minutes']
                route_info['total_travel_time_hours'] = osrm_data['total_duration_hours']
                route_info['osrm_recalculated'] = True
                route_info['osrm_route_geometry'] = osrm_data['geometry']

                # Update constraint info with OSRM data
                route_info['constraint_info'] = recalculate_constraint_info(
                    osrm_data['total_distance_km'],
                    osrm_data['total_duration_minutes']
                )
            else:
                route_info['osrm_recalculated'] = False
                route_info['osrm_error'] = osrm_data.get('error')

            recommendations.append(route_info)

        # Sort by OSRM distance (shortest first)
        recommendations.sort(key=lambda x: x['total_distance_km'])

        # Update ranks after sorting
        for i, route in enumerate(recommendations):
            route['rank'] = i + 1

        # Get algorithm statistics
        stats = hga.get_evolution_statistics()

        # Build response
        response_data = {
            "user_location": {
                "latitude": user_location[0],
                "longitude": user_location[1]
            },
            "hga_config": hga_config.dict(),
            "statistics": {
                "total_generations": stats['total_generations'],
                "best_distance_km": stats['best_distance'],
                "initial_fitness": stats['best_fitness_history'][0],
                "final_fitness": stats['best_fitness_history'][-1],
                "improvement_percentage": (
                    (stats['best_fitness_history'][-1] -
                     stats['best_fitness_history'][0]) /
                    stats['best_fitness_history'][0] * 100
                )
            },
            "routes": recommendations
        }

        return RouteRecommendationResponse(
            success=True,
            message=f"Successfully generated {len(recommendations)} routes",
            data=response_data,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )
```

<!--
### 5.2.3 Additional API Endpoints

#### 5.2.3.1 Health Check

```python
@app.get("/health")
async def health_check():
    """Check API health status"""
    osrm_stats = get_osrm_cache_stats()
    return {
        "status": "healthy",
        "destinations_loaded": destinations is not None,
        "total_destinations": len(destinations) if destinations else 0,
        "osrm_cache_size": osrm_stats['cache_size'],
        "timestamp": datetime.now().isoformat()
    }
```

#### 5.2.3.2 Get All Destinations

```python
@app.get("/api/destinations")
async def get_destinations():
    """Get all available destinations"""
    if destinations is None:
        raise HTTPException(500, "Destinations not loaded")

    return {
        "success": True,
        "total": len(destinations),
        "data": [
            {
                "place_id": d.place_id,
                "nama_destinasi": d.nama,
                "kategori": d.kategori,
                "latitude": d.latitude,
                "longitude": d.longitude,
                "alamat": d.alamat,
                "image_url": d.image_url,
                "deskripsi": d.deskripsi
            }
            for d in destinations
        ]
    }
```

#### 5.2.3.3 Get Default Configuration

```python
@app.get("/api/config/default")
async def get_default_config():
    """Get default HGA configuration"""
    return {
        "success": True,
        "data": {
            "population_size": 600,
            "generations": 40,
            "crossover_rate": 0.8,
            "mutation_rate": 0.05,
            "elitism_count": 2,
            "tournament_size": 8,
            "use_2opt": True,
            "two_opt_iterations": 100
        }
    }
``` -->

### 5.2.4 Frontend Integration

Frontend dapat mengakses API menggunakan HTTP client library (contoh menggunakan JavaScript fetch):

```javascript
// Example: Call recommendation API from frontend
async function getRouteRecommendations(latitude, longitude, numRoutes = 3) {
  try {
    const response = await fetch('http://localhost:8000/generate-routes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        latitude: latitude,
        longitude: longitude,
        num_routes: numRoutes,
        hga_config: {
          population_size: 600,
          generations: 40,
          use_2opt: true,
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (data.success) {
      // Process routes
      displayRoutes(data.data.routes);

      // Display statistics
      displayStatistics(data.data.statistics);

      // Show on map
      data.data.routes.forEach((route) => {
        displayRouteOnMap(route.osrm_route_geometry);
      });
    }

    return data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
}

// Display routes in UI
function displayRoutes(routes) {
  routes.forEach((route, index) => {
    console.log(`Route ${route.rank}:`);
    console.log(`  Distance: ${route.total_distance_km} km`);
    console.log(`  Time: ${route.total_travel_time_minutes} minutes`);
    console.log(
      `  Feasible: ${route.constraint_info.is_feasible ? 'Yes' : 'No'}`
    );
    console.log(`  Google Maps: ${route.google_maps_url}`);

    route.destinations.forEach((dest) => {
      console.log(`    ${dest.order}. ${dest.nama_destinasi}`);
    });
  });
}

// Display route on Google Maps
function displayRouteOnMap(encodedPolyline) {
  // Decode polyline and display on map
  const decodedPath = google.maps.geometry.encoding.decodePath(encodedPolyline);

  const routePath = new google.maps.Polyline({
    path: decodedPath,
    geodesic: true,
    strokeColor: '#FF0000',
    strokeOpacity: 1.0,
    strokeWeight: 2,
  });

  routePath.setMap(map);
}
```

<!--
### 5.2.5 Error Handling dan Logging

Backend mengimplementasikan comprehensive error handling:

```python
# Custom exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

# General exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# Logging configuration
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
``` -->
<!--
### 5.2.6 Deployment

Backend API dapat di-deploy menggunakan berbagai platform:

**1. Local Development**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**2. Production dengan Gunicorn**
```bash
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**3. Docker Container**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**4. Cloud Deployment (Heroku/Railway/Render)**
```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn api:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
``` -->

Dengan implementasi ini, sistem rekomendasi rute wisata telah terintegrasi penuh dengan website, memungkinkan pengguna untuk mendapatkan rekomendasi rute optimal secara real-time melalui interface web yang user-friendly.
