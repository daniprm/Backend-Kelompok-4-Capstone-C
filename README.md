# Sistem Rekomendasi Rute Wisata Surabaya dengan Hybrid Genetic Algorithm

Sistem rekomendasi rute wisata yang menggunakan **Hybrid Genetic Algorithm (HGA)** untuk menemukan 3 rute wisata optimal (jarak terpendek) di Surabaya berdasarkan koordinat user.

## 📋 Fitur

- **Optimasi Rute Multi-Kriteria**: Menghasilkan rute dengan jarak minimal
- **Hybrid Genetic Algorithm**: Kombinasi GA dengan 2-Opt local search
- **Constraint-Based Planning**: Rute mengikuti pola K1→C1→W1→K2→W2→C2→K3→O
- **Multiple Solutions**: Memberikan 3 alternatif rute terbaik
- **🗺️ Visualisasi Peta Interaktif**: Peta dengan rute jalan nyata menggunakan OSRM API
- **📊 Grafik Konvergensi**: Analisis evolusi algoritma dalam 4 grafik statistik
- **🛣️ Real Road Routing**: Menggunakan OpenStreetMap untuk rute jalan sebenarnya

## 🏗️ Struktur Project

```
dev/
├── algorithms/
│   ├── __init__.py
│   ├── chromosome.py        # Representasi kromosom (solusi rute)
│   ├── population.py        # Manajemen populasi
│   ├── operators.py         # Operator GA (seleksi, crossover, mutasi)
│   ├── two_opt.py          # Algoritma 2-Opt untuk local search
│   └── hga.py              # Hybrid Genetic Algorithm utama
├── models/
│   ├── __init__.py
│   ├── destination.py      # Model destinasi wisata
│   └── route.py            # Model rute wisata
├── utils/
│   ├── __init__.py
│   ├── distance.py         # Perhitungan jarak (Haversine)
│   └── data_loader.py      # Loading data dari CSV
├── visualization/           # 🆕 Modul visualisasi
│   ├── __init__.py
│   ├── map_plotter.py      # Plotting peta dengan routing API
│   ├── convergence_plotter.py  # Plotting grafik statistik
│   ├── README_VISUALIZATION.md # Dokumentasi visualisasi
│   ├── ROUTING_API_INFO.md     # Info routing API
│   └── outputs/            # Output visualisasi
│       ├── best_route_map.html
│       ├── all_routes_map.html
│       └── *.png (4 grafik)
├── data_wisata_sby.csv     # Data destinasi wisata Surabaya
├── Main.py                 # Aplikasi interaktif
└── example.py              # Demo non-interaktif
```

## 🎯 Constraint dan Aturan Rute

### Pola Urutan Rute

Setiap rute harus mengikuti pola: **K1 → C1 → W1 → K2 → W2 → C2 → K3 → O**

- **K1, K2, K3**: Destinasi kuliner makanan berat (3 tempat)
- **C1, C2**: Lokasi makanan ringan/cemilan (2 tempat)
- **W1, W2**: Destinasi non-kuliner (2 tempat)
- **O**: Lokasi oleh-oleh/souvenir (1 tempat)

### Batasan

1. Titik awal dan akhir rute sama (kembali ke lokasi user)
2. Tidak ada subtours
3. Minimal 8 destinasi dengan kategori yang ditentukan
4. Rute dioptimasi untuk jarak terpendek

## 🧬 Tahapan Hybrid Genetic Algorithm

### 1. Representasi Genetik

- **Kromosom**: Merepresentasikan satu rute wisata
- **Gen**: Destinasi wisata individual dalam urutan tertentu

### 2. Inisialisasi Populasi

- Generate populasi awal dengan kromosom random
- Setiap kromosom valid mengikuti constraint pola K-C-W

### 3. Fungsi Fitness

```
Fitness = 1 / total_distance
```

- Jarak lebih pendek = fitness lebih tinggi
- Menggunakan formula Haversine untuk jarak

### 4. Seleksi

- **Tournament Selection**: Memilih individu terbaik dari subset random
- **Roulette Wheel Selection**: Probabilitas berdasarkan fitness

### 5. Crossover

- **Order Crossover (OX)**: Mempertahankan urutan relatif gen
- **Position Based Crossover**: Alternatif untuk variasi

### 6. Mutasi

- **Swap Mutation**: Menukar posisi dua gen
- **Inversion Mutation**: Membalik urutan subset
- **Scramble Mutation**: Mengacak subset gen

### 7. Local Search (2-Opt)

- Optimasi lokal untuk memperbaiki rute
- Menghilangkan crossing edges
- Dengan dan tanpa constraint

### 8. Elitism

- Menyalin individu terbaik ke generasi berikutnya
- Memastikan solusi terbaik tidak hilang

### 9. Konvergensi

- Berhenti jika tidak ada improvement dalam N generasi
- Atau mencapai maksimal generasi

## 💻 Cara Penggunaan

### Prerequisites

```bash
pip install python>=3.7
```

### Menjalankan Sistem

```bash
python main.py
```

### Input

- Koordinat latitude dan longitude lokasi user
- Contoh: Latitude: -7.2575, Longitude: 112.7521

### Output

1. **Console Output**: Detail 3 rute terbaik dengan urutan destinasi
2. **JSON File**: `route_recommendations.json` berisi hasil rekomendasi

## 📊 Contoh Output

```
======================================================================
RUTE #1
======================================================================
Total Jarak: 45.32 km
Valid Order: ✓

Urutan Destinasi:
----------------------------------------------------------------------
1. [K1] GADO GADO PAK HARDI
   Kategori: makanan_berat
   Koordinat: (-7.2772519, 112.7691333)

2. [C1] Kampung Kue
   Kategori: makanan_ringan
   Koordinat: (-7.324722, 112.769831)

3. [W1] Museum Etnografi
   Kategori: non_kuliner
   Koordinat: (-7.272492, 112.757315)
...
```

## 🔧 Konfigurasi HGA

Pada `main.py`, Anda dapat mengatur parameter:

```python
system.initialize_hga(
    population_size=100,      # Ukuran populasi
    generations=200,          # Jumlah generasi
    crossover_rate=0.8,       # Probabilitas crossover
    mutation_rate=0.1         # Probabilitas mutasi
)
```

## 📝 Format Data CSV

File `data_wisata_sby.csv`:

```csv
nama_destinasi,kategori,latitude,longitude
Galaxy Mall,mall,-7.2756967,112.7806254
Pusat Oleh-oleh Bu Rudy,oleh_oleh,-7.2673018,112.7697516
...
```

### Kategori yang Digunakan:

- `makanan_berat`: Restoran/rumah makan
- `makanan_ringan`: Toko cemilan/snack
- `non_kuliner`: Tempat wisata, museum, taman, dll
- `oleh_oleh`: Toko souvenir/oleh-oleh

## 🎓 Algoritma Detail

### Haversine Distance

Menghitung jarak antara dua koordinat geografis:

```python
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius bumi dalam km
    # ... formula Haversine
    return distance
```

### 2-Opt Algorithm

Optimasi lokal dengan menukar edges:

1. Pilih dua edges dalam rute
2. Reverse segment di antaranya
3. Jika lebih baik, gunakan rute baru
4. Ulangi hingga tidak ada improvement

## 📈 Monitoring Evolusi

Sistem melacak:

- Best fitness per generasi
- Average fitness populasi
- Total generasi hingga konvergensi
- History evolusi dalam JSON output

## 🚀 Pengembangan Lebih Lanjut

### Fitur yang Sudah Tersedia:

1. ✅ **Visualisasi Peta Interaktif**: Peta HTML dengan Folium
2. ✅ **Real Road Routing**: Rute jalan nyata menggunakan OSRM API
3. ✅ **Grafik Konvergensi**: 4 grafik analisis evolusi algoritma
4. ✅ **Multiple Solutions**: 3 rute alternatif terbaik

### Fitur yang Dapat Ditambahkan:

1. **Time Constraint**: Batasan waktu kunjungan per hari
2. **User Preferences**: Preferensi kategori destinasi
3. **Real-time Traffic**: Integrasi data traffic
4. **Multi-day Tours**: Rute untuk beberapa hari
5. **Budget Optimization**: Optimasi berdasarkan budget
6. **Mobile App**: Aplikasi mobile untuk user

## 🗺️ Visualisasi

### Peta Interaktif

Sistem menghasilkan 2 file peta HTML:

- `best_route_map.html`: Peta rute terbaik dengan marker dan rute jalan nyata
- `all_routes_map.html`: Peta semua 3 rute dengan layer control

**Fitur Peta:**

- ✅ Rute jalan nyata menggunakan OSRM Routing API
- ✅ Marker berwarna sesuai kategori destinasi
- ✅ Popup info detail untuk setiap lokasi
- ✅ Legend untuk kategori
- ✅ Interactive zoom dan pan

### Grafik Konvergensi

4 grafik PNG untuk analisis:

1. `fitness_evolution.png`: Evolusi fitness terbaik dan rata-rata
2. `distance_evolution.png`: Evolusi jarak terbaik dan rata-rata
3. `convergence_analysis.png`: Analisis konvergensi dengan threshold
4. `statistics_summary.png`: Ringkasan statistik final

**Dokumentasi Lengkap**: Lihat `visualization/README_VISUALIZATION.md`

**Info Routing API**: Lihat `visualization/ROUTING_API_INFO.md`

## 📚 Referensi Algoritma

- **Genetic Algorithm**: Holland, 1975
- **2-Opt Algorithm**: Croes, 1958
- **OSRM**: Open Source Routing Machine - Project OSRM
- **Folium**: Python library untuk visualisasi peta
- **Hybrid Approaches**: Kombinasi metaheuristik dan local search
- **TSP Optimization**: Traveling Salesman Problem variants

## 👨‍💻 Author

Dikembangkan sebagai sistem rekomendasi rute wisata berbasis AI menggunakan pendekatan optimasi metaheuristik.

## 📄 License

Educational/Academic Use

---

**Note**: Sistem ini menggunakan OOP (Object-Oriented Programming) dengan arsitektur modular untuk memudahkan maintenance dan pengembangan lebih lanjut.
