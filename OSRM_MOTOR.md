# Penggunaan OSRM untuk Motor/Sepeda Motor

## 🏍️ Konfigurasi untuk Motor

Sistem ini telah dikonfigurasi untuk menggunakan **OSRM dengan profil 'driving'** yang cocok untuk **motor/sepeda motor** di Indonesia.

### Mengapa Profil 'Driving'?

1. **Public OSRM tidak punya profil 'motorcycle'** khusus
2. Motor di Indonesia dapat menggunakan **jalan yang sama dengan mobil**
3. Profil 'driving' memberikan **rute tercepat** untuk kendaraan bermotor
4. Lebih akurat daripada profil 'bike' (sepeda) yang mungkin menggunakan jalur khusus sepeda

## 📝 Default Setting

```python
OSRM_PROFILE = "driving"  # Untuk motor/mobil
```

Ini adalah setting default saat sistem startup, **tidak perlu diubah** untuk penggunaan motor.

## 🔧 Cara Mengubah Profil (Jika Diperlukan)

### Via API

**Cek profil saat ini:**

```bash
curl http://localhost:8000/api/osrm/status
```

**Ganti ke profil lain (jika perlu):**

```bash
# Motor/Mobil (default)
curl -X POST "http://localhost:8000/api/osrm/set-profile?profile=driving"

# Sepeda
curl -X POST "http://localhost:8000/api/osrm/set-profile?profile=bike"

# Jalan kaki
curl -X POST "http://localhost:8000/api/osrm/set-profile?profile=foot"
```

### Via Code

```python
from utils.distance import set_osrm_profile

# Set ke profil motor/mobil
set_osrm_profile('driving')
```

## ✅ Verifikasi

Jalankan test sederhana:

```bash
python test_osrm_quick.py
```

Output yang diharapkan:

```
OSRM Configuration:
  Enabled: True
  Profile: driving (Motor/Mobil)
  Server: http://router.project-osrm.org

Calculating distances...
  Haversine (straight line): 3.50 km
  OSRM (motor route):        4.20 km
  Difference:                +20.0%

✓ OSRM working! Using real road distances for motor.
```

## 📊 Perbandingan Jarak

### Haversine (Garis Lurus)

- Jarak langsung tanpa mempertimbangkan jalan
- Contoh: 5 km

### OSRM dengan Profil 'driving' (Motor)

- Jarak mengikuti jalan yang bisa dilalui motor
- Memperhitungkan jalur satu arah, jembatan, dll
- Contoh: 6.5 km (30% lebih jauh dari garis lurus)
- **Lebih akurat untuk navigasi motor!**

## 🚀 Best Practices

1. **Gunakan profil 'driving' (default)** untuk motor di Indonesia
2. **Cache otomatis** menyimpan hasil untuk performa lebih cepat
3. **Fallback ke Haversine** jika OSRM gagal/timeout
4. Clear cache jika ganti profil: `POST /api/osrm/clear-cache`

## 💡 Catatan Penting

- Public OSRM server **gratis** tapi ada **rate limit**
- Untuk production dengan traffic tinggi, pertimbangkan **self-hosted OSRM**
- Profil 'driving' **sudah optimal** untuk motor, tidak perlu diubah
- Jarak OSRM biasanya **20-40% lebih panjang** dari Haversine (lebih realistis!)

## 🔗 Dokumentasi Lengkap

Lihat `OSRM_INTEGRATION.md` untuk dokumentasi lengkap tentang:

- Setup self-hosted OSRM
- Advanced configuration
- Troubleshooting
- Performance tuning
