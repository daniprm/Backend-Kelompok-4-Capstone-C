# Tourism Route Recommendation API

API untuk sistem rekomendasi rute wisata Surabaya menggunakan Hybrid Genetic Algorithm (HGA).

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run API Server

```bash
python api.py
```

Atau menggunakan uvicorn langsung:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di: `http://localhost:8000`

### 3. Akses API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### 1. Root Endpoint

```
GET /
```

Menampilkan informasi dasar API.

**Response:**

```json
{
  "message": "Tourism Route Recommendation API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "recommend": "/generate-routes (POST)"
  }
}
```

### 2. Health Check

```
GET /health
```

Mengecek status API dan data yang dimuat.

**Response:**

```json
{
  "status": "healthy",
  "destinations_loaded": true,
  "total_destinations": 199,
  "timestamp": "2025-10-31T10:00:00.000000"
}
```

### 3. Get Default Configuration

```
GET /api/config/default
```

Mendapatkan konfigurasi default HGA yang digunakan (sesuai dengan Main.py).

**Response:**

```json
{
  "success": true,
  "data": {
    "hga_config": {
      "population_size": 70,
      "generations": 10000,
      "crossover_rate": 0.8,
      "mutation_rate": 0.1,
      "elitism_count": 2,
      "tournament_size": 5,
      "use_2opt": true,
      "two_opt_iterations": 500
    },
    "description": "Default configuration used in Main.py",
    "note": "You can override these values in your request to /generate-routes"
  }
}
```

### 4. Get Route Recommendations (Main Endpoint)

```
POST /generate-routes
```

Mendapatkan rekomendasi rute wisata optimal.

**Request Body:**

```json
{
  "latitude": -7.2575,
  "longitude": 112.7521,
  "num_routes": 3,
  "hga_config": {
    "population_size": 70,
    "generations": 10000,
    "crossover_rate": 0.8,
    "mutation_rate": 0.1,
    "elitism_count": 2,
    "tournament_size": 5,
    "use_2opt": true,
    "two_opt_iterations": 500
  }
}
```

**Parameters:**

- `latitude` (required): Latitude lokasi user (-90 to 90)
- `longitude` (required): Longitude lokasi user (-180 to 180)
- `num_routes` (optional): Jumlah rute yang diinginkan (1-5, default: 3)
- `hga_config` (optional): Konfigurasi HGA (jika tidak diisi, akan menggunakan default dari Main.py)
  - `population_size`: Ukuran populasi (10-200, **default: 70**)
  - `generations`: Jumlah generasi (100-20000, **default: 10000**)
  - `crossover_rate`: Probabilitas crossover (0.0-1.0, **default: 0.8**)
  - `mutation_rate`: Probabilitas mutasi (0.0-1.0, **default: 0.1**)
  - `elitism_count`: Jumlah solusi terbaik yang dipertahankan (1-10, **default: 2**)
  - `tournament_size`: Ukuran tournament selection (2-20, **default: 5**)
  - `use_2opt`: Menggunakan 2-Opt optimization (**default: true**)
  - `two_opt_iterations`: Jumlah iterasi 2-Opt (10-2000, **default: 500**)

**Response:**

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
      "population_size": 70,
      "generations": 10000,
      "crossover_rate": 0.8,
      "mutation_rate": 0.1,
      "elitism_count": 2,
      "tournament_size": 5,
      "use_2opt": true,
      "two_opt_iterations": 500
    },
    "statistics": {
      "total_generations": 10000,
      "best_distance_km": 9.19,
      "initial_fitness": 0.031401,
      "final_fitness": 0.108811,
      "improvement_percentage": 246.52
    },
    "routes": [
      {
        "rank": 1,
        "total_distance_km": 9.19,
        "is_valid_order": true,
        "fitness": 0.108811,
        "destinations": [
          {
            "order": 1,
            "nama": "Tahu Telor Pak Jayen Pusat",
            "kategori": ["makanan_berat"],
            "coordinates": [-7.268097, 112.774744]
          }
          // ... 7 destinasi lainnya
        ]
      }
      // ... rute lainnya
    ]
  },
  "timestamp": "2025-10-31T10:00:00.000000"
}
```

### 4. Get All Destinations

```
GET /api/destinations
```

Mendapatkan daftar semua destinasi yang tersedia.

**Response:**

```json
{
  "success": true,
  "total": 199,
  "data": [
    {
      "nama": "Tugu Pahlawan",
      "kategori": ["non_kuliner"],
      "coordinates": {
        "latitude": -7.246209,
        "longitude": 112.738031
      }
    }
    // ... destinasi lainnya
  ]
}
```

## 🧪 Testing dengan cURL

### Simple Request (Minimal)

```bash
curl -X POST "http://localhost:8000/generate-routes" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -7.2575,
    "longitude": 112.7521
  }'
```

### Full Request (dengan HGA Config)

```bash
curl -X POST "http://localhost:8000/generate-routes" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -7.2575,
    "longitude": 112.7521,
    "num_routes": 3,
    "hga_config": {
      "population_size": 100,
      "generations": 5000,
      "crossover_rate": 0.8,
      "mutation_rate": 0.1
    }
  }'
```

## 🧪 Testing dengan Python

```python
import requests

url = "http://localhost:8000/generate-routes"
payload = {
    "latitude": -7.2575,
    "longitude": 112.7521,
    "num_routes": 3
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Success: {data['success']}")
print(f"Best Route Distance: {data['data']['statistics']['best_distance_km']} km")
```

## 🧪 Testing dengan JavaScript/Fetch

```javascript
const url = 'http://localhost:8000/generate-routes';
const payload = {
  latitude: -7.2575,
  longitude: 112.7521,
  num_routes: 3,
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(payload),
})
  .then((response) => response.json())
  .then((data) => {
    console.log('Success:', data.success);
    console.log('Best Route:', data.data.routes[0]);
  });
```

## ⚙️ Configuration

### CORS Settings

API sudah dikonfigurasi dengan CORS yang memperbolehkan semua origin (`*`).

Untuk production, ubah di `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Ganti dengan domain Anda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Performance Tuning

Untuk response yang lebih cepat (testing):

```json
{
  "hga_config": {
    "population_size": 30,
    "generations": 1000
  }
}
```

Untuk hasil yang lebih optimal (production):

```json
{
  "hga_config": {
    "population_size": 100,
    "generations": 10000
  }
}
```

## 📝 Notes

- **Processing Time**: Tergantung konfigurasi HGA, bisa 5-60 detik
- **Route Pattern**: K1 → C1 → W1 → K2 → W2 → C2 → K3 → O
  - K = Kuliner Berat (3x)
  - C = Kuliner Ringan (2x)
  - W = Wisata Non-Kuliner (2x)
  - O = Oleh-oleh (1x)

## 🐛 Error Handling

API akan mengembalikan error dengan format:

```json
{
  "detail": "Error message here"
}
```

Common errors:

- `500`: Server error atau data tidak dimuat
- `422`: Validation error (parameter tidak valid)

## 🔧 Production Deployment

### Dengan Gunicorn + Uvicorn Workers

```bash
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Dengan Docker (Coming Soon)

```dockerfile
# Dockerfile example
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📞 Support

Untuk pertanyaan atau issue, silakan buka issue di repository GitHub.
