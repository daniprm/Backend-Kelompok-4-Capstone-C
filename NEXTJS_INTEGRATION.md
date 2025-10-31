# Integrasi API dengan Next.js

## 📋 Persiapan

### 1. Pastikan API FastAPI Berjalan
```bash
# Di terminal project Python
cd c:\Users\rahma\Documents\Kuliah\TA\API\dev
python -m uvicorn api.run:app --reload --host 127.0.0.1 --port 8000
```

**API akan berjalan di**: `http://127.0.0.1:8000`

### 2. Buat Project Next.js (Jika Belum Ada)
```bash
npx create-next-app@latest tourism-route-app
cd tourism-route-app
npm install
```

---

## 🔌 Cara Integrasi

### **Opsi 1: Menggunakan Fetch API (Built-in)**

#### 1️⃣ Buat Service File
Buat file: `src/services/routeApi.js`

```javascript
// src/services/routeApi.js

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

/**
 * Generate route recommendations
 * @param {Object} params - Request parameters
 * @param {number} params.latitude - User latitude
 * @param {number} params.longitude - User longitude
 * @param {number} params.num_routes - Number of routes (default: 3)
 * @param {number} params.generations - GA generations (default: 1000)
 * @param {number} params.population_size - GA population size (default: 50)
 * @param {number} params.crossover_rate - Crossover rate (default: 0.8)
 * @param {number} params.mutation_rate - Mutation rate (default: 0.1)
 */
export async function generateRoutes(params) {
  try {
    const response = await fetch(`${API_BASE_URL}/generate-routes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to generate routes');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating routes:', error);
    throw error;
  }
}

/**
 * Check API health
 */
export async function checkApiHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/`);
    return response.ok;
  } catch (error) {
    return false;
  }
}
```

#### 2️⃣ Buat Component React
Buat file: `src/components/RouteGenerator.jsx`

```jsx
// src/components/RouteGenerator.jsx
'use client';

import { useState } from 'react';
import { generateRoutes } from '@/services/routeApi';

export default function RouteGenerator() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  
  const [formData, setFormData] = useState({
    latitude: -7.2458,
    longitude: 112.7378,
    num_routes: 3,
    generations: 1000,
    population_size: 50,
    crossover_rate: 0.8,
    mutation_rate: 0.1,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await generateRoutes(formData);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'number' ? parseFloat(value) : value,
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">
        Generator Rute Wisata Surabaya
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Latitude
            </label>
            <input
              type="number"
              step="any"
              name="latitude"
              value={formData.latitude}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-md"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Longitude
            </label>
            <input
              type="number"
              step="any"
              name="longitude"
              value={formData.longitude}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-md"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Jumlah Rute
            </label>
            <input
              type="number"
              name="num_routes"
              min="1"
              max="10"
              value={formData.num_routes}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Generasi (HGA)
            </label>
            <input
              type="number"
              name="generations"
              min="11"
              max="10000"
              value={formData.generations}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Population Size
            </label>
            <input
              type="number"
              name="population_size"
              min="11"
              max="200"
              value={formData.population_size}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Crossover Rate
            </label>
            <input
              type="number"
              step="0.01"
              name="crossover_rate"
              min="0"
              max="1"
              value={formData.crossover_rate}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Generating Routes...' : 'Generate Routes'}
        </button>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          Error: {error}
        </div>
      )}

      {results && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Results</h2>
          <p className="text-gray-600">{results.message}</p>
          
          <div className="space-y-4">
            {results.recommendations.map((route, idx) => (
              <div key={idx} className="border rounded-lg p-4 bg-white shadow">
                <h3 className="text-xl font-semibold mb-2">
                  Rute #{route.rank}
                </h3>
                <p className="text-gray-700 mb-2">
                  <strong>Total Jarak:</strong> {route.total_distance_km} km
                </p>
                <p className="text-gray-700 mb-3">
                  <strong>Valid:</strong> {route.is_valid_order ? '✓ Ya' : '✗ Tidak'}
                </p>
                
                <h4 className="font-semibold mb-2">Destinasi:</h4>
                <ul className="space-y-2">
                  {route.destinations.map((dest, destIdx) => (
                    <li key={destIdx} className="flex items-start">
                      <span className="font-medium mr-2">{dest.order}.</span>
                      <div>
                        <p className="font-medium">{dest.nama}</p>
                        <p className="text-sm text-gray-600">
                          {dest.kategori.join(', ')}
                        </p>
                        <p className="text-xs text-gray-500">
                          {dest.coordinates[0].toFixed(6)}, {dest.coordinates[1].toFixed(6)}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

#### 3️⃣ Gunakan di Page
Buat/Edit file: `src/app/page.jsx`

```jsx
// src/app/page.jsx
import RouteGenerator from '@/components/RouteGenerator';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <RouteGenerator />
    </main>
  );
}
```

#### 4️⃣ Konfigurasi Environment Variable
Buat file: `.env.local`

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

### **Opsi 2: Menggunakan Axios**

#### 1️⃣ Install Axios
```bash
npm install axios
```

#### 2️⃣ Buat Service dengan Axios
```javascript
// src/services/routeApi.js
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function generateRoutes(params) {
  try {
    const response = await api.post('/generate-routes', params);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to generate routes');
  }
}

export async function checkApiHealth() {
  try {
    await api.get('/');
    return true;
  } catch {
    return false;
  }
}
```

---

### **Opsi 3: Menggunakan React Query (Recommended)**

#### 1️⃣ Install Dependencies
```bash
npm install @tanstack/react-query axios
```

#### 2️⃣ Setup Query Client
Buat file: `src/app/providers.jsx`

```jsx
// src/app/providers.jsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export default function Providers({ children }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        refetchOnWindowFocus: false,
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

Update: `src/app/layout.jsx`

```jsx
// src/app/layout.jsx
import Providers from './providers';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
```

#### 3️⃣ Buat Custom Hook
```javascript
// src/hooks/useRouteGenerator.js
import { useMutation } from '@tanstack/react-query';
import { generateRoutes } from '@/services/routeApi';

export function useRouteGenerator() {
  return useMutation({
    mutationFn: generateRoutes,
    onSuccess: (data) => {
      console.log('Routes generated successfully:', data);
    },
    onError: (error) => {
      console.error('Failed to generate routes:', error);
    },
  });
}
```

#### 4️⃣ Gunakan di Component
```jsx
// src/components/RouteGenerator.jsx
'use client';

import { useState } from 'react';
import { useRouteGenerator } from '@/hooks/useRouteGenerator';

export default function RouteGenerator() {
  const { mutate, data, isLoading, error } = useRouteGenerator();
  
  const [formData, setFormData] = useState({
    latitude: -7.2458,
    longitude: 112.7378,
    num_routes: 3,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate(formData);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        {/* Form fields */}
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Generating...' : 'Generate Routes'}
        </button>
      </form>

      {error && <div>Error: {error.message}</div>}
      {data && <div>{/* Display results */}</div>}
    </div>
  );
}
```

---

## 🗺️ Integrasi dengan Map (Leaflet)

### Install Leaflet
```bash
npm install react-leaflet leaflet
```

### Buat Map Component
```jsx
// src/components/RouteMap.jsx
'use client';

import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function RouteMap({ route, userLocation }) {
  const center = [userLocation[0], userLocation[1]];

  return (
    <MapContainer
      center={center}
      zoom={13}
      style={{ height: '500px', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      
      {/* User Location Marker */}
      <Marker position={center}>
        <Popup>Lokasi Anda</Popup>
      </Marker>

      {/* Route Polyline */}
      {route && (
        <>
          <Polyline
            positions={[
              center,
              ...route.destinations.map(d => d.coordinates)
            ]}
            color="blue"
          />
          
          {/* Destination Markers */}
          {route.destinations.map((dest, idx) => (
            <Marker key={idx} position={dest.coordinates}>
              <Popup>
                <strong>{dest.nama}</strong><br />
                {dest.kategori.join(', ')}
              </Popup>
            </Marker>
          ))}
        </>
      )}
    </MapContainer>
  );
}
```

---

## 🚀 Menjalankan Development

### Terminal 1: Backend (FastAPI)
```bash
cd c:\Users\rahma\Documents\Kuliah\TA\API\dev
python -m uvicorn api.run:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2: Frontend (Next.js)
```bash
cd tourism-route-app
npm run dev
```

**Frontend akan berjalan di**: `http://localhost:3000`

---

## 📝 TypeScript Support (Optional)

### Install TypeScript
```bash
npm install --save-dev typescript @types/react @types/node
```

### Buat Type Definitions
```typescript
// src/types/route.ts

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface DestinationDetail {
  order: number;
  nama: string;
  kategori: string[];
  coordinates: [number, number];
}

export interface RouteResponse {
  rank: number;
  start_point: [number, number];
  total_destinations: number;
  total_distance_km: number;
  destinations: DestinationDetail[];
  is_valid_order: boolean;
}

export interface RecommendationResponse {
  message: string;
  user_location: [number, number];
  recommendations: RouteResponse[];
}

export interface RouteRequest {
  latitude: number;
  longitude: number;
  num_routes?: number;
  generations?: number;
  population_size?: number;
  crossover_rate?: number;
  mutation_rate?: number;
}
```

---

## 🔍 Testing API dari Browser

### Test Langsung di Browser Console
Buka http://localhost:3000 dan buka Console (F12):

```javascript
// Test API Call
fetch('http://127.0.0.1:8000/generate-routes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    latitude: -7.2458,
    longitude: 112.7378,
    num_routes: 3
  })
})
.then(res => res.json())
.then(data => console.log(data))
.catch(err => console.error(err));
```

---

## 📚 Resources

- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI CORS**: https://fastapi.tiangolo.com/tutorial/cors/
- **React Query**: https://tanstack.com/query/latest
- **React Leaflet**: https://react-leaflet.js.org/

---

## ⚠️ Troubleshooting

### CORS Error
Jika masih ada CORS error, pastikan:
1. FastAPI sudah menambahkan middleware CORS
2. URL di `allow_origins` sudah benar
3. Server FastAPI sudah direstart

### Connection Refused
Pastikan:
1. API FastAPI berjalan di port 8000
2. URL di `.env.local` sudah benar
3. Tidak ada firewall yang memblokir

### Slow Response
API membutuhkan waktu untuk generate routes (tergantung parameter `generations`).
Pertimbangkan:
- Kurangi `generations` untuk testing (e.g., 500)
- Tampilkan loading indicator yang jelas
- Implementasi timeout handling

---

**Happy Coding!** 🚀
