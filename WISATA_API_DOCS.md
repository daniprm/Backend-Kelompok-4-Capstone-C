# Wisata API Endpoints Documentation

## Overview
API endpoints untuk mengakses data wisata dari database SQLite (`api/data_wisata_surabaya.db`).

## Endpoints

### 1. GET `/wisata`
Mengambil daftar data wisata dengan filtering dan pagination.

**Query Parameters:**
- `kategori` (optional): Filter berdasarkan kategori (mall, oleh_oleh, non_kuliner, makanan_ringan, makanan_berat, all)
- `limit` (optional): Batas jumlah data yang dikembalikan (harus > 0)
- `offset` (optional): Posisi awal data untuk pagination (default: 0)
- `search` (optional): Kata kunci pencarian untuk nama atau alamat

**Response:**
```json
{
  "message": "Data wisata berhasil diambil",
  "total": 50,
  "data": [
    {
      "restaurant_id": 1,
      "nama_destinasi": "Galaxy Mall",
      "kategori": "mall",
      "latitude": "-7.2756967",
      "longitude": "112.7806254",
      "alamat": "Jl. Dr. Ir. H. Soekarno No.35, Mulyorejo, Kec. Mulyorejo, Surabaya, Jawa Timur",
      "image_url": "https://galaxymall.co.id/wp-content/uploads/2023/01/FOOTER-GM3.jpg",
      "deskripsi": null
    }
  ]
}
```

**Examples:**
- Get all wisata: `GET /wisata`
- Get with pagination: `GET /wisata?limit=10&offset=0`
- Filter by kategori: `GET /wisata?kategori=mall`
- Search by name: `GET /wisata?search=Galaxy`

---

### 2. GET `/wisata/{restaurant_id}`
Mengambil detail satu destinasi wisata berdasarkan ID.

**Path Parameters:**
- `restaurant_id` (required): ID unik dari destinasi wisata

**Response:**
```json
{
  "restaurant_id": 1,
  "nama_destinasi": "Galaxy Mall",
  "kategori": "mall",
  "latitude": "-7.2756967",
  "longitude": "112.7806254",
  "alamat": "Jl. Dr. Ir. H. Soekarno No.35, Mulyorejo, Kec. Mulyorejo, Surabaya, Jawa Timur",
  "image_url": "https://galaxymall.co.id/wp-content/uploads/2023/01/FOOTER-GM3.jpg",
  "deskripsi": null
}
```

**Examples:**
- Get wisata with ID 1: `GET /wisata/1`
- Get wisata with ID 25: `GET /wisata/25`

**Error Response (404):**
```json
{
  "detail": "Destinasi wisata dengan ID 999 tidak ditemukan"
}
```

---

### 3. GET `/wisata/stats/overview`
Mengambil statistik data wisata.

**Response:**
```json
{
  "message": "Statistik data wisata berhasil diambil",
  "total_destinations": 50,
  "kategori_count": {
    "mall": 8,
    "oleh_oleh": 5,
    "non_kuliner": 25,
    "makanan_ringan": 3,
    "makanan_berat": 2,
    "all": 7
  }
}
```

**Examples:**
- Get statistics: `GET /wisata/stats/overview`

---

## Database Functions

The following utility functions are available in `utils/database.py`:

1. **`get_all_wisata(kategori, limit, offset)`** - Get all wisata with filtering and pagination
2. **`get_wisata_by_id(restaurant_id)`** - Get wisata by ID
3. **`search_wisata(search_term, limit)`** - Search wisata by name or address
4. **`get_wisata_by_kategori(kategori)`** - Get all wisata with specific kategori
5. **`get_wisata_statistics()`** - Get statistics about wisata data

## Database Schema

Table: `wisata_sby`

| Column | Type | Description |
|--------|------|-------------|
| restaurant_id | BIGINT | Unique identifier |
| nama_destinasi | VARCHAR | Destination name |
| kategori | VARCHAR | Category (can be comma-separated) |
| latitude | VARCHAR | Latitude coordinate |
| longitude | VARCHAR | Longitude coordinate |
| alamat | VARCHAR | Address |
| image_url | VARCHAR | Image URL |
| deskripsi | VARCHAR | Description |

Index: `idx_restaurant_id` on `restaurant_id`

## Error Handling

All endpoints include proper error handling:
- **404**: Resource not found
- **500**: Internal server error (database connection issues, etc.)
- **400**: Bad request (invalid parameters)
