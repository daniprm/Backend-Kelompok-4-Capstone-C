# Sistem Rekomendasi Rute Wisata Surabaya dengan Hybrid Genetic Algorithm

Sistem rekomendasi rute wisata dengan menggunakan **Hybrid Genetic Algorithm (HGA)** untuk menemukan 3 rute wisata optimal (jarak terpendek) di Surabaya berdasarkan koordinat user.

## Fitur

- **Optimasi Rute**: Menghasilkan rute dengan jarak minimal
- **Hybrid Genetic Algorithm**: Kombinasi GA dengan 2-Opt local search
- **Constraint-Based Planning**: Rute mengikuti pola K1→C1→W1→K2→W2→C2→K3→O
- **Visualisasi Peta**: Peta dengan rute jalan nyata menggunakan OSRM API
- **Real Road Routing**: Menggunakan OpenStreetMap untuk rute jalan sebenarnya

## Constraint dan Aturan Rute

### Pola Urutan Rute

Setiap rute harus mengikuti pola: **K1 → C1 → W1 → K2 → W2 → C2 → K3 → O**

- **K1, K2, K3**: Destinasi kuliner makanan berat (3 tempat)
- **C1, C2**: Lokasi makanan ringan/cemilan (2 tempat)
- **W1, W2**: Destinasi non-kuliner (2 tempat)
- **O**: Lokasi oleh-oleh/souvenir (1 tempat)

### Batasan

1. Perjalanan dimulai di titik yang ditentukan pengguna
2. Tidak ada subtours
3. Minimal 8 destinasi dengan kategori yang ditentukan
4. Rute dioptimasi untuk jarak terpendek

## Tahapan Hybrid Genetic Algorithm

### 1. Representasi Genetik

- **Kromosom**: Merepresentasikan satu rute wisata
- **Gen**: Destinasi wisata individual dalam urutan tertentu

### 2. Inisialisasi Populasi

- Generate populasi awal dengan kromosom random
- Setiap kromosom valid mengikuti constraint pola rute

### 3. Fungsi Fitness

```
Fitness = 1 / total_distance
```

- Jarak lebih pendek = fitness lebih tinggi
- Menggunakan distance matrix yang didapatkan dari rute nyata menggunakan OSRM dan haversine untuk jarak titik user ke destinasi pertama.

### 4. Seleksi

- **Tournament Selection**: Memilih individu terbaik dari subset random

### 5. Crossover

- **Order Crossover (OX)**: Mempertahankan urutan relatif gen sesuai pola rute

### 6. Mutasi

- **Swap Mutation**: Menukar posisi dua gen tetap berdasarkan aturan pola rute

### 7. Local Search (2-Opt)

- Optimasi lokal untuk memperbaiki rute
- Menghilangkan crossing edges

### 8. Elitism

- Menyalin individu terbaik ke generasi berikutnya
- Memastikan solusi terbaik tidak hilang

### 9. Konvergensi

- Berhenti jika tidak ada improvement dalam N generasi
- Atau mencapai maksimal generasi

## Cara Penggunaan

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

## Format Data CSV

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

## Algoritma Detail

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
