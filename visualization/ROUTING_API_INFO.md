# Routing API - Rute Jalan Nyata

## Overview

Sistem sekarang menggunakan **OSRM (Open Source Routing Machine) API** untuk menampilkan rute jalan nyata di peta, bukan hanya garis lurus antar destinasi.

## Fitur

### ✅ Rute Jalan Nyata

- Mengikuti jalan yang sebenarnya
- Menggunakan OpenStreetMap data
- Automatic fallback ke garis lurus jika API gagal

### 🌐 OSRM API

- **Provider**: OSRM Public API
- **URL**: http://router.project-osrm.org
- **Mode**: Driving (mobil)
- **Format**: GeoJSON geometries
- **Rate Limiting**: Otomatis delay 0.1 detik per request

## Cara Kerja

### 1. Request Format

```
http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson
```

**Catatan**: OSRM menggunakan format `lon,lat` (terbalik dari biasanya!)

### 2. Response

```json
{
  "code": "Ok",
  "routes": [{
    "geometry": {
      "coordinates": [
        [lon1, lat1],
        [lon2, lat2],
        ...
      ]
    },
    "distance": 1234.5,
    "duration": 123.4
  }]
}
```

### 3. Konversi

Sistem otomatis mengkonversi `[lon, lat]` → `(lat, lon)` untuk Folium.

## Penggunaan

### Mengaktifkan Real Routes (Default)

```python
from visualization.map_plotter import RouteMapPlotter

# Dengan real routes (default)
plotter = RouteMapPlotter(use_real_routes=True)
```

### Menonaktifkan Real Routes (Garis Lurus)

```python
# Tanpa real routes (garis lurus)
plotter = RouteMapPlotter(use_real_routes=False)
```

### Membuat Peta

```python
# Sama seperti biasa
route_map = plotter.create_route_map(
    start_point=user_location,
    destinations=destinations,
    route_name="Rute Wisata"
)
```

## Error Handling

### Automatic Fallback

Jika routing API gagal, sistem otomatis fallback ke garis lurus:

1. **Network Error**: Timeout, koneksi gagal
2. **API Error**: Response code bukan "Ok"
3. **Rate Limiting**: Terlalu banyak request

### Error Messages

```
[INFO] Routing API gagal, menggunakan garis lurus
[INFO] Error routing API: <error_message>, menggunakan garis lurus
```

## Performance

### Request Time

- Per segmen: ~100-300ms (tergantung jarak)
- Total waktu untuk 8 segmen: ~2-3 detik
- Delay antar request: 100ms (anti rate-limit)

### Total Requests

- **Single Route Map**: 8 requests (1 per segmen)
- **Multiple Routes Map (3 rute)**: 24 requests (3 × 8 segmen)

### Optimization Tips

```python
# Untuk testing cepat, nonaktifkan real routes
plotter = RouteMapPlotter(use_real_routes=False)
```

## Alternatif API

### 1. OpenRouteService (ORS)

```python
# Ganti URL di get_route_coordinates()
url = f"https://api.openrouteservice.org/v2/directions/driving-car"
# Perlu API key gratis dari openrouteservice.org
```

### 2. GraphHopper

```python
url = f"https://graphhopper.com/api/1/route"
# Perlu API key gratis dari graphhopper.com
```

### 3. Local OSRM Server

```python
# Install OSRM locally
url = f"http://localhost:5000/route/v1/driving/..."
# Lebih cepat, no rate limit
```

## Troubleshooting

### Problem: API Timeout

**Solution**:

```python
# Tingkatkan timeout di map_plotter.py
response = requests.get(url, params=params, timeout=10)  # dari 5 ke 10
```

### Problem: Rate Limited

**Solution**:

```python
# Tambahkan delay di map_plotter.py
time.sleep(0.2)  # dari 0.1 ke 0.2
```

### Problem: Koordinat Terbalik

**Solution**:
OSRM format: `lon,lat` (sudah dihandle otomatis)
Folium format: `(lat, lon)` (sudah dikonversi otomatis)

### Problem: Rute Tidak Muncul

**Check**:

1. Internet connection aktif
2. Koordinat valid (dalam range Indonesia)
3. OSRM server online (cek http://project-osrm.org)

## Kustomisasi

### Ganti Mode Transport

Edit `get_route_coordinates()` di `map_plotter.py`:

```python
# Mobil (default)
url = f"http://router.project-osrm.org/route/v1/driving/..."

# Motor/Bike
url = f"http://router.project-osrm.org/route/v1/bike/..."

# Jalan Kaki
url = f"http://router.project-osrm.org/route/v1/foot/..."
```

### Tambahkan Informasi Jarak dan Waktu

```python
if data.get('code') == 'Ok' and 'routes' in data:
    route = data['routes'][0]
    distance = route['distance']  # meter
    duration = route['duration']  # detik

    print(f"Jarak: {distance/1000:.2f} km")
    print(f"Waktu: {duration/60:.1f} menit")
```

### Gunakan API Key Pribadi

Untuk production, gunakan API dengan key:

```python
# OpenRouteService
headers = {'Authorization': 'YOUR_API_KEY'}
response = requests.get(url, headers=headers, params=params)
```

## Credits

- **OSRM**: OpenStreetMap Routing Machine
- **OpenStreetMap**: Map data provider
- **Folium**: Python map visualization
- **Requests**: HTTP library

## License

OSRM Public API untuk penggunaan non-komersial.
Untuk production/komersial, pertimbangkan:

- Setup OSRM server sendiri
- Gunakan Google Maps Directions API
- Gunakan OpenRouteService dengan API key

---

**Last Updated**: October 2025
**Version**: 1.0.0
