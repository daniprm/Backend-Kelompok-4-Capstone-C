# 📊 Dokumentasi Visualisasi

## Overview

Modul visualisasi menyediakan tools untuk membuat:

1. **Peta Rute Interaktif** - Menggunakan Folium
2. **Grafik Konvergensi** - Menggunakan Matplotlib

Semua output disimpan di folder `visualization/outputs/`

---

## 🗺️ Map Visualization (Peta Rute)

### Features:

- **Peta Interaktif**: Dapat di-zoom dan di-pan
- **Marker Berwarna**: Setiap kategori memiliki warna berbeda
  - 🔴 Merah: Makanan Berat (K)
  - 🟠 Orange: Makanan Ringan (C)
  - 🔵 Biru: Non-Kuliner (W)
  - 🟣 Purple: Oleh-Oleh (O)
  - 🟢 Hijau: Titik Awal (START)
- **Polyline**: Garis menghubungkan semua destinasi
- **Popup Info**: Klik marker untuk melihat detail
- **Legend**: Penjelasan warna dan simbol
- **Numbering**: Urutan destinasi (1-8)

### Output Files:

1. `best_route_map.html` - Peta rute terbaik
2. `all_routes_map.html` - Peta dengan 3 rute terbaik (layer control)

### Cara Membuka:

1. Buka file HTML di browser (Chrome, Firefox, Edge)
2. Zoom in/out dengan scroll mouse
3. Klik marker untuk info detail
4. Di `all_routes_map.html`, gunakan layer control (kanan atas) untuk toggle rute

---

## 📈 Convergence Graphs (Grafik Konvergensi)

### 1. Fitness Evolution (`fitness_evolution.png`)

**Deskripsi**: Menampilkan evolusi fitness selama generasi

**Grafik**:

- **Blue Line**: Best Fitness per generasi
- **Orange Dashed Line**: Average Fitness per generasi

**Interpretasi**:

- Kenaikan grafik = peningkatan fitness (lebih baik)
- Plateau = konvergensi tercapai
- Gap antara best dan average = diversity populasi

### 2. Distance Evolution (`distance_evolution.png`)

**Deskripsi**: Menampilkan evolusi jarak (km) selama generasi

**Grafik**:

- **Green Line**: Best Distance (jarak terpendek)
- **Red Dashed Line**: Average Distance

**Interpretasi**:

- Penurunan grafik = jarak lebih pendek (lebih baik)
- Best distance mendekati konstan = optimal tercapai

### 3. Convergence Analysis (`convergence_analysis.png`)

**Deskripsi**: Analisis detail konvergensi dengan 2 subplot

**Subplot 1**: Best Fitness Evolution

- Menunjukkan trend fitness terbaik

**Subplot 2**: Improvement Rate (%)

- Menunjukkan persentase improvement per generasi
- Positive spike = ada improvement signifikan
- Near zero line = tidak ada perubahan (stagnant)

**Interpretasi**:

- Improvement rate tinggi di awal generasi = eksplorasi
- Improvement rate mendekati nol = konvergensi

### 4. Statistics Summary (`statistics_summary.png`)

**Deskripsi**: Dashboard lengkap dengan 4 panel

**Panel 1**: Fitness Evolution

- Best vs Average fitness

**Panel 2**: Distance Evolution

- Best vs Average distance

**Panel 3**: Text Summary

- Total generasi
- Best distance
- Initial & Final fitness
- Overall improvement %
- Convergence point

**Panel 4**: Distribution of Improvements

- Histogram showing when improvements occurred
- X-axis: Generation number
- Y-axis: Frequency of improvements

**Interpretasi**:

- Banyak improvement di awal = normal
- Few improvements di akhir = konvergensi

---

## 📁 Folder Structure

```
visualization/
├── __init__.py
├── map_plotter.py           # Map visualization class
├── convergence_plotter.py   # Graph plotting class
└── outputs/                 # Output directory
    ├── best_route_map.html
    ├── all_routes_map.html
    ├── fitness_evolution.png
    ├── distance_evolution.png
    ├── convergence_analysis.png
    └── statistics_summary.png
```

---

## 🔧 Usage Examples

### Example 1: Dari example.py (Automatic)

```python
python example.py
```

Otomatis membuat semua visualisasi.

### Example 2: Manual - Map Only

```python
from visualization.map_plotter import RouteMapPlotter

plotter = RouteMapPlotter()
map_obj = plotter.create_route_map(
    start_point=(-7.2458, 112.7378),
    destinations=best_chromosome.genes,
    route_name="Rute Wisata Surabaya"
)
plotter.save_map('my_route.html')
```

### Example 3: Manual - Graphs Only

```python
from visualization.convergence_plotter import ConvergencePlotter

plotter = ConvergencePlotter()
stats = hga.get_evolution_statistics()
plotter.create_all_plots(stats)
```

### Example 4: Multiple Routes on One Map

```python
routes_data = [
    {
        'destinations': route1_genes,
        'name': 'Rute A',
        'color': 'blue'
    },
    {
        'destinations': route2_genes,
        'name': 'Rute B',
        'color': 'red'
    }
]

map_obj = plotter.create_multiple_routes_map(
    start_point=user_location,
    routes_data=routes_data
)
```

---

## 🎨 Customization

### Mengubah Warna Marker

Edit `map_plotter.py`:

```python
colors = {
    'makanan_berat': 'red',      # Ubah ke 'darkred', 'pink', dll
    'makanan_ringan': 'orange',  # Ubah ke 'yellow', 'beige', dll
    'non_kuliner': 'blue',       # Ubah ke 'lightblue', 'navy', dll
    'oleh_oleh': 'purple',       # Ubah ke 'pink', 'darkpurple', dll
}
```

### Mengubah Style Grafik

Edit `convergence_plotter.py`:

```python
plt.style.use('seaborn')  # Atau 'ggplot', 'fivethirtyeight', dll
```

### Mengubah Resolusi Grafik

```python
plt.savefig(filepath, dpi=300)  # Ubah 300 ke 150 (smaller) atau 600 (larger)
```

---

## 📊 Interpreting Results

### Good Convergence Signs:

✅ Best fitness meningkat pesat di awal
✅ Plateau pada best fitness (stable)
✅ Gap best-average mengecil
✅ Distance turun signifikan
✅ Improvement rate mendekati nol di akhir

### Poor Convergence Signs:

❌ Best fitness berfluktuasi terus
❌ Gap best-average tetap besar
❌ Distance tidak turun signifikan
❌ Improvement rate masih tinggi di akhir
❌ Konvergensi terlalu cepat (premature)

### Actions:

- **Premature convergence**: Tingkatkan mutation rate, population size
- **No convergence**: Tingkatkan generations, cek crossover operator
- **Slow convergence**: Enable 2-Opt, tune parameters

---

## 🚀 Performance Tips

### Untuk Grafik yang Cepat:

- Kurangi `markersize`
- Kurangi `dpi` saat save
- Gunakan `plt.style.use('fast')`

### Untuk Peta yang Ringan:

- Batasi jumlah marker
- Gunakan `CircleMarker` daripada custom icons
- Kurangi detail polyline

---

## 📝 Notes

1. **Folium maps** bersifat interaktif dan harus dibuka di browser
2. **Matplotlib graphs** adalah static images (PNG)
3. Semua output disimpan di `visualization/outputs/`
4. File HTML dapat di-share langsung (standalone)
5. Grafik PNG cocok untuk laporan/presentasi

---

## 🐛 Troubleshooting

### Map tidak muncul:

- Pastikan folium terinstall: `pip install folium`
- Cek file HTML ada di folder outputs
- Buka dengan browser modern

### Grafik blur/pixelated:

- Tingkatkan DPI: `dpi=600`
- Gunakan format vector: `.svg` atau `.pdf`

### Memory error saat plotting:

- Kurangi jumlah generasi yang di-plot
- Sample data (ambil setiap 5 atau 10 generasi)
- Close figure setelah save: `plt.close()`

---

**Last Updated**: October 2025
**Version**: 1.0
