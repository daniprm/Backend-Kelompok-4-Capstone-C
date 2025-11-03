# OSRM Integration Guide

## Overview

Sistem ini menggunakan **OSRM (Open Source Routing Machine)** untuk mendapatkan jarak rute nyata di jalan, bukan jarak garis lurus (Haversine). Ini memberikan hasil yang lebih akurat untuk rekomendasi rute wisata.

**Profil Transportasi:** Sistem ini menggunakan profil **'driving'** yang cocok untuk **motor/sepeda motor** di Indonesia.

## Bagaimana Cara Kerjanya?

### 1. **OSRM API**

- Default menggunakan public OSRM server: `http://router.project-osrm.org`
- Profil: **'driving'** (untuk motor/mobil)
- Menghitung jarak menggunakan rute jalan yang sebenarnya
- Lebih akurat daripada jarak garis lurus

### 2. **Profil Transportasi**

Tersedia 3 profil transportasi:

- **`driving`** (Default) - **Motor/Mobil**
  - Paling cocok untuk motor/sepeda motor di Indonesia
  - Menggunakan jalan yang bisa dilalui kendaraan bermotor
  - Rute tercepat untuk kendaraan
- **`bike`** - Sepeda
  - Rute khusus sepeda (jika tersedia)
  - Bisa melewati jalur sepeda
- **`foot`** - Jalan Kaki
  - Rute untuk pejalan kaki
  - Bisa melewati gang dan jalan setapak

**Catatan Penting:** Public OSRM server tidak memiliki profil khusus 'motorcycle'. Profil 'driving' paling sesuai untuk motor karena motor dapat menggunakan jalan yang sama dengan mobil di Indonesia.

### 2. **Fallback Mechanism**

Jika OSRM gagal (timeout, error, atau tidak tersedia):

- Otomatis fallback ke **Haversine formula** (jarak garis lurus)
- Sistem tetap berjalan tanpa error

### 3. **Caching**

- Hasil OSRM di-cache untuk menghindari request berulang
- Meningkatkan performa secara signifikan
- Cache dapat di-clear via API endpoint

## Configuration

### File: `utils/distance.py`

```python
# OSRM API Configuration
OSRM_BASE_URL = "http://router.project-osrm.org"
OSRM_PROFILE = "driving"  # 'driving' untuk motor/mobil, 'bike', 'foot'
USE_OSRM = True  # Set False untuk fallback ke Haversine
OSRM_TIMEOUT = 5  # Timeout in seconds
OSRM_MAX_RETRIES = 2  # Maximum retry attempts
```

### Mengubah Profil Transportasi

**Via API (Recommended):**

```bash
# Set ke profil driving (motor/mobil) - default
curl -X POST "http://localhost:8000/api/osrm/set-profile?profile=driving"

# Set ke profil bike (sepeda)
curl -X POST "http://localhost:8000/api/osrm/set-profile?profile=bike"

# Set ke profil foot (jalan kaki)
curl -X POST "http://localhost:8000/api/osrm/set-profile?profile=foot"
```

**Via Code:**

```python
from utils.distance import set_osrm_profile

# Set profil motor/mobil
set_osrm_profile('driving')
```

## API Endpoints untuk OSRM

### 1. Get OSRM Status

```bash
GET /api/osrm/status
```

**Response:**

```json
{
  "success": true,
  "data": {
    "osrm_enabled": true,
    "osrm_base_url": "http://router.project-osrm.org",
    "osrm_profile": "driving",
    "profile_description": "Motor/Mobil (paling cocok untuk motor di Indonesia)",
    "cache_size": 150,
    "available_profiles": ["driving", "bike", "foot"],
    "description": "OSRM is used to calculate real route distances..."
  }
}
```

### 2. Clear OSRM Cache

```bash
POST /api/osrm/clear-cache
```

**Response:**

```json
{
  "success": true,
  "message": "OSRM cache cleared successfully"
}
```

### 3. Toggle OSRM On/Off

```bash
POST /api/osrm/toggle?enable=true
```

**Parameters:**

- `enable`: `true` untuk mengaktifkan OSRM, `false` untuk menggunakan Haversine saja

**Response:**

```json
{
  "success": true,
  "message": "OSRM has been enabled",
  "osrm_enabled": true
}
```

### 4. Set OSRM Profile (NEW)

```bash
POST /api/osrm/set-profile?profile=driving
```

**Parameters:**

- `profile`: Profil transportasi
  - `driving`: Motor/Mobil (default)
  - `bike`: Sepeda
  - `foot`: Jalan kaki

**Response:**

```json
{
  "success": true,
  "message": "OSRM profile changed to 'driving'",
  "profile": "driving",
  "description": "Motor/Mobil",
  "note": "Cache has been cleared due to profile change"
}
```

## Perbandingan: OSRM vs Haversine

### Haversine (Jarak Garis Lurus)

- ✅ **Kelebihan:**
  - Sangat cepat (tidak perlu API call)
  - Selalu tersedia (offline)
  - Tidak ada batasan rate limit
- ❌ **Kekurangan:**
  - Tidak akurat untuk jarak jalan
  - Tidak memperhitungkan jalan, sungai, gedung, dll
  - Contoh: Jarak Haversine 5 km, tapi jarak jalan sebenarnya bisa 7-8 km

### OSRM (Jarak Rute Nyata)

- ✅ **Kelebihan:**
  - Akurat sesuai jalan yang sebenarnya
  - Memperhitungkan rute yang bisa dilalui
  - Lebih realistic untuk navigasi
- ❌ **Kekurangan:**
  - Butuh koneksi internet
  - Lebih lambat (API call)
  - Ada potensi rate limit pada public server

## Contoh Penggunaan dalam Code

### Direct Function Call

```python
from utils.distance import (
    calculate_distance,           # Auto: OSRM → Haversine fallback
    calculate_distance_osrm,      # Hanya OSRM
    calculate_distance_haversine  # Hanya Haversine
)

# Otomatis menggunakan OSRM, fallback ke Haversine jika gagal
distance = calculate_distance(-7.2575, 112.7521, -7.2600, 112.7550)
print(f"Distance: {distance:.2f} km")

# Hanya OSRM (return None jika gagal)
osrm_dist = calculate_distance_osrm(-7.2575, 112.7521, -7.2600, 112.7550)
if osrm_dist:
    print(f"OSRM Distance: {osrm_dist:.2f} km")

# Hanya Haversine (selalu berhasil)
haversine_dist = calculate_distance_haversine(-7.2575, 112.7521, -7.2600, 112.7550)
print(f"Haversine Distance: {haversine_dist:.2f} km")
```

### Toggle OSRM Programmatically

```python
from utils.distance import set_use_osrm

# Disable OSRM (gunakan Haversine saja)
set_use_osrm(False)

# Enable OSRM
set_use_osrm(True)
```

### Clear Cache

```python
from utils.distance import clear_osrm_cache

# Clear cache
clear_osrm_cache()
```

## Performance Tips

### 1. Cache Management

- Cache otomatis menyimpan hasil OSRM
- Untuk testing dengan data berbeda, clear cache via API
- Cache akan reset saat server restart

### 2. Timeout Setting

- Default timeout: 5 detik
- Untuk koneksi lambat, tingkatkan `OSRM_TIMEOUT`
- Untuk koneksi cepat, turunkan timeout untuk response lebih cepat

### 3. Retry Logic

- Default max retry: 2
- Tingkatkan untuk koneksi tidak stabil
- Turunkan untuk response lebih cepat

## Self-Hosted OSRM (Optional)

Untuk production atau traffic tinggi, pertimbangkan setup OSRM server sendiri:

### Docker Setup (Quick)

```bash
# Download map data (contoh: Indonesia)
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/indonesia-latest.osm.pbf

# Process data
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/indonesia-latest.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/indonesia-latest.osrm

# Run OSRM server
docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/indonesia-latest.osrm
```

Kemudian update config:

```python
OSRM_BASE_URL = "http://localhost:5000"
```

## Troubleshooting

### OSRM selalu fallback ke Haversine?

1. Check koneksi internet
2. Test OSRM API manual:
   ```bash
   curl "http://router.project-osrm.org/route/v1/driving/112.7521,-7.2575;112.7550,-7.2600?overview=false"
   ```
3. Check logs untuk error message

### Jarak OSRM tidak masuk akal?

1. Pastikan koordinat valid (latitude/longitude tidak terbalik)
2. OSRM menggunakan format `longitude,latitude` (berbeda dari Google Maps)
3. Check apakah lokasi terisolasi (pulau, area tertutup)

### Cache terlalu besar?

```bash
# Clear via API
curl -X POST http://localhost:8000/api/osrm/clear-cache

# Check cache size
curl http://localhost:8000/api/osrm/status
```

## Best Practices

1. **Production**: Gunakan self-hosted OSRM server
2. **Development**: Gunakan public OSRM (sudah default)
3. **Testing**: Toggle OSRM off untuk testing cepat
4. **Monitor**: Check cache size secara berkala
5. **Fallback**: Selalu siap dengan Haversine fallback

## References

- OSRM Documentation: http://project-osrm.org/
- OSRM API Docs: https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md
- Public OSRM Demo: https://map.project-osrm.org/
