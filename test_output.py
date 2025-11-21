"""
Test output format dengan semua field
"""
import json
from utils.data_loader import load_destinations_from_csv
from models.route import Route

# Load destinations
print("Loading destinations...")
destinations = load_destinations_from_csv("./data/data_wisata.jsonl")
print(f"Loaded {len(destinations)} destinations\n")

# Test 1: Print first destination with all fields
print("="*70)
print("TEST 1: Destination Object dengan Semua Field")
print("="*70)
d = destinations[0]
print(f"Restaurant ID: {d.place_id}")
print(f"Nama: {d.nama}")
print(f"Kategori: {d.kategori}")
print(f"Latitude: {d.latitude}")
print(f"Longitude: {d.longitude}")
print(f"Alamat: {d.alamat}")
print(f"Image URL: {d.image_url}")
print(f"Deskripsi: {d.deskripsi}")
print()

# Test 2: Route summary format
print("="*70)
print("TEST 2: Route Summary Format (seperti API response)")
print("="*70)
# Ambil 8 destinasi pertama untuk simulasi route
sample_dests = destinations[:8]
route = Route((-7.2575, 112.7521), sample_dests)
summary = route.get_route_summary()

# Print dalam format JSON yang rapi
print(json.dumps(summary, indent=2, ensure_ascii=False))
print()

print("="*70)
print("✓ Semua field berhasil dimuat dan ditampilkan!")
print("="*70)
