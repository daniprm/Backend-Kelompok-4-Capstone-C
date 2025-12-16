"""
Script untuk build distance matrix pertama kali
Jalankan sekali: python build_distance_matrix.py
"""
from utils.data_loader import load_destinations_from_csv
from utils.distance_matrix import DistanceMatrixCache

def main():
    print("="*70)
    print(" BUILD DISTANCE MATRIX - OSRM Real Routes")
    print("="*70)
    print()
    
    # Load destinations
    print("📂 Loading destinations from JSONL...")
    destinations = load_destinations_from_csv("./data/data_wisata.jsonl")
    print(f"✓ Loaded {len(destinations)} destinations")
    print()
    
    # Info
    print("ℹ️  Information:")
    print("   - Using OSRM for REAL ROUTE distances (via roads)")
    print("   - NO FALLBACK to Haversine - only accurate real routes!")
    print("   - Auto-retry up to 3x if request fails")
    print("   - Results are cached for instant future lookups")
    print("   - This process may take 2-5 minutes for first time")
    print()
    
    input("Press ENTER to start building matrix...")
    print()
    
    # Build matrix
    cache = DistanceMatrixCache()
    cache.load()  # Load existing jika ada
    cache.build_matrix(destinations, max_retries=3)
    
    print()
    print("="*70)
    print(" 🎉 DONE!")
    print("="*70)
    print(f" Matrix file: {cache.cache_file}")
    print(f" Total distances: {len(cache.matrix)}")
    print(f" OSRM success: {cache.metadata.get('osrm_success', 0)}")
    print(f" OSRM fallback: {cache.metadata.get('osrm_fallback', 0)}")
    print()
    print(" Next time you run API, it will be INSTANT! 🚀")
    print("="*70)

if __name__ == "__main__":
    main()
