# Google Maps URL Integration

## Update Tanggal: 11 Desember 2025

### Fitur Baru: Google Maps Navigation URL

Setiap rute yang dihasilkan oleh API sekarang dilengkapi dengan **Google Maps URL** yang dapat langsung dibuka untuk navigasi.

---

## Implementasi

### Fungsi: `generate_google_maps_url()`

**Location:** `api.py`

```python
def generate_google_maps_url(start_point, destinations_list):
    """
    Generate Google Maps URL untuk navigasi rute

    Format: https://www.google.com/maps/dir/start/dest1/dest2/.../destN
    Mode: driving (cocok untuk motor/mobil)
    """
```

**Format URL:**

```
https://www.google.com/maps/dir/
  'start_lat,start_lon'/
  dest1_lat,+dest1_lon/
  dest2_lat,+dest2_lon/
  .../
  destN_lat,+destN_lon
  ?entry=ttu&travelmode=driving
```

---

## Response API

### Field Baru: `google_maps_url`

Setiap route object sekarang memiliki field `google_maps_url`:

```json
{
  "routes": [
    {
      "rank": 1,
      "total_distance_km": 22.52,
      "total_travel_time_minutes": 30.9,
      "google_maps_url": "https://www.google.com/maps/dir/'-7.2575,112.7521'/-7.276346,+112.755779/...",
      "destinations": [...]
    }
  ]
}
```

---

## Contoh URL

**Input:**

- Start: (-7.2575, 112.7521)
- Destinasi 1: (-7.276346, 112.755779)
- Destinasi 2: (-7.2751227, 112.75597)
- Destinasi 3: (-7.2640551, 112.7453148)

**Generated URL:**

```
https://www.google.com/maps/dir/'-7.2575,112.7521'/-7.276346,+112.755779/-7.2751227,+112.75597/-7.2640551,+112.7453148?entry=ttu&travelmode=driving
```

**Hasil:**
URL ini akan membuka Google Maps dengan:

- ✓ Start point sudah diset
- ✓ Semua waypoints/destinasi sudah terurut
- ✓ Mode transportasi: driving (cocok untuk motor/mobil)
- ✓ Siap untuk navigasi

---

## Cara Penggunaan

### 1. Via API Response

**Request:**

```bash
curl -X POST "http://localhost:8000/generate-routes" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -7.2575,
    "longitude": 112.7521,
    "num_routes": 3
  }'
```

**Response:**

```json
{
  "routes": [
    {
      "rank": 1,
      "google_maps_url": "https://www.google.com/maps/dir/...",
      ...
    }
  ]
}
```

### 2. Via Client Application

**Frontend (JavaScript/React):**

```javascript
// Setelah mendapat response dari API
const route = response.data.routes[0];
const mapsUrl = route.google_maps_url;

// Open in new tab
window.open(mapsUrl, '_blank');

// Or create a link
<a href={mapsUrl} target="_blank" rel="noopener noreferrer">
  Open in Google Maps
</a>;
```

**Mobile (Flutter/React Native):**

```dart
// Flutter
import 'package:url_launcher/url_launcher.dart';

void openGoogleMaps(String url) async {
  if (await canLaunch(url)) {
    await launch(url);
  }
}
```

---

## Testing

### Test Script 1: URL Generation Only

```bash
python test_google_maps_url.py
```

### Test Script 2: Full Route with URL

```bash
python test_full_response.py
```

### Test Script 3: API Endpoint

```bash
python test_api_generate_routes.py
```

**Expected Output:**

```
Route #1:
  Distance: 22.52 km
  Duration: 30.9 min

  Google Maps URL:
    https://www.google.com/maps/dir/...
```

---

## Parameter URL

| Parameter    | Value     | Keterangan                      |
| ------------ | --------- | ------------------------------- |
| `travelmode` | `driving` | Mode transportasi (motor/mobil) |
| `entry`      | `ttu`     | Google Maps entry point         |

**Travel Mode Options:**

- `driving` - Motor/Mobil (default)
- `walking` - Jalan kaki
- `bicycling` - Sepeda
- `transit` - Transportasi umum

---

## Notes

1. **Kompatibilitas:**

   - ✓ Desktop browser (Chrome, Firefox, Safari, Edge)
   - ✓ Mobile browser
   - ✓ Google Maps app (iOS & Android)

2. **Limit:**

   - Google Maps support hingga ~25 waypoints per route
   - Sistem kita menggunakan 8 destinasi + 1 start = 9 points (aman)

3. **Fallback:**

   - Jika user tidak punya Google Maps app, akan buka di browser
   - URL tetap valid dan fungsional

4. **Privacy:**
   - URL tidak menyimpan data pribadi user
   - Hanya koordinat geografis

---

## Response Fields Lengkap

```json
{
  "success": true,
  "data": {
    "routes": [
      {
        "rank": 1,
        "fitness": 0.049548,
        "total_distance_km": 22.52,
        "total_travel_time_minutes": 30.9,
        "total_travel_time_hours": 0.52,
        "google_maps_url": "https://www.google.com/maps/dir/...",
        "osrm_recalculated": true,
        "osrm_route_geometry": "encoded_polyline...",
        "constraint_info": {
          "distance": {...},
          "time": {...},
          "is_feasible": false
        },
        "destinations": [...]
      }
    ]
  }
}
```

---

## Keuntungan

✅ **User Experience:**

- User bisa langsung navigasi tanpa input manual
- Semua waypoints sudah terurut optimal
- Save time & effort

✅ **Integration:**

- Mudah diintegrasikan ke frontend
- Universal URL format
- Cross-platform compatible

✅ **Accuracy:**

- Menggunakan hasil optimasi HGA
- Urutan destinasi sudah optimal
- Real-time navigation via Google Maps

---

## Files Modified

1. `api.py` - Added `generate_google_maps_url()` function
2. `api.py` - Updated `/generate-routes` endpoint
3. `test_google_maps_url.py` - Test script (new)
4. `test_full_response.py` - Test script (new)
5. `test_api_generate_routes.py` - Updated to show URL
