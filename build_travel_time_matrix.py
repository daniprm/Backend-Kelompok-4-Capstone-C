"""
Script untuk build travel time matrix (waktu tempuh)
Jalankan sekali: python build_travel_time_matrix.py

Waktu tempuh didapatkan dari:
1. OSRM API (real driving time) - Prioritas utama
2. Estimasi dari jarak dengan kecepatan rata-rata 30 km/jam - Fallback
"""
import argparse
from utils.data_loader import load_destinations_from_csv
from utils.travel_time_matrix import TravelTimeMatrixCache, AVERAGE_SPEED_KMH

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Build Travel Time Matrix')
    parser.add_argument('--no-osrm', action='store_true', 
                        help='Skip OSRM API, use distance-based estimation only')
    parser.add_argument('--speed', type=float, default=AVERAGE_SPEED_KMH,
                        help=f'Average speed in km/h for estimation (default: {AVERAGE_SPEED_KMH})')
    args = parser.parse_args()
    
    print("="*70)
    print(" BUILD TRAVEL TIME MATRIX - Waktu Tempuh Antar Destinasi")
    print("="*70)
    print()
    
    # Load destinations
    print("📂 Loading destinations from JSONL...")
    destinations = load_destinations_from_csv("./data/data_wisata.jsonl")
    print(f"✓ Loaded {len(destinations)} destinations")
    print()
    
    # Info tentang strategi
    print("ℹ️  Strategi Perhitungan Waktu Tempuh:")
    print()
    
    if args.no_osrm:
        print("   📐 Mode: ESTIMATION ONLY (--no-osrm flag detected)")
        print(f"   🏍️  Average speed: {args.speed} km/h")
        print("   📝 Formula: time = distance / speed")
        print()
        print("   ⚠️  Estimasi mungkin kurang akurat karena:")
        print("       - Tidak memperhitungkan traffic")
        print("       - Tidak memperhitungkan kondisi jalan")
        print("       - Asumsi kecepatan konstan")
    else:
        print("   📡 Mode: OSRM + FALLBACK ESTIMATION")
        print()
        print("   1️⃣  OSRM API (Prioritas):")
        print("       - Real driving time dari routing service")
        print("       - Memperhitungkan jalan raya, jarak rute nyata")
        print("       - Profile: 'driving' (mobil/motor)")
        print()
        print("   2️⃣  Fallback Estimation:")
        print(f"       - Jika OSRM gagal: time = distance / {args.speed} km/h")
        print("       - Distance dari distance_matrix_osrm.json")
    
    print()
    print("   📊 Output: travel_time_matrix_osrm.json")
    print("       - duration: Waktu tempuh (menit)")
    print("       - distance: Jarak (km)")
    print("       - source: 'osrm' atau 'estimated'")
    print()
    
    # Confirmation
    total_pairs = len(destinations) * (len(destinations) - 1) // 2
    print(f"📊 Total pasangan destinasi: {total_pairs}")
    
    if not args.no_osrm:
        estimated_time = (total_pairs * 0.5) / 60  # ~0.5 detik per request
        print(f"⏱️  Estimasi waktu (OSRM): {estimated_time:.1f} menit")
    
    print()
    input("Press ENTER to start building travel time matrix...")
    print()
    
    # Build matrix
    cache = TravelTimeMatrixCache()
    cache.load()  # Load existing jika ada
    
    # Update speed jika custom
    if args.speed != AVERAGE_SPEED_KMH:
        from utils import travel_time_matrix
        travel_time_matrix.AVERAGE_SPEED_KMH = args.speed
    
    cache.build_matrix(
        destinations, 
        distance_matrix_file="./data/distance_matrix_osrm.json",
        use_osrm=not args.no_osrm,
        max_retries=3
    )
    
    # Print statistics
    print()
    print("📊 STATISTICS:")
    print("="*70)
    stats = cache.get_statistics()
    
    if stats:
        print(f"  Total pairs: {stats['total_pairs']}")
        print(f"  OSRM pairs: {stats['osrm_pairs']}")
        print(f"  Estimated pairs: {stats['estimated_pairs']}")
        print()
        print("  Duration (menit):")
        print(f"    Min: {stats['duration_stats']['min']:.1f}")
        print(f"    Max: {stats['duration_stats']['max']:.1f}")
        print(f"    Avg: {stats['duration_stats']['avg']:.1f}")
        print()
        print("  Distance (km):")
        print(f"    Min: {stats['distance_stats']['min']:.2f}")
        print(f"    Max: {stats['distance_stats']['max']:.2f}")
        print(f"    Avg: {stats['distance_stats']['avg']:.2f}")
    
    print()
    print("="*70)
    print(" 🎉 DONE!")
    print("="*70)
    print(f" Matrix file: {cache.cache_file}")
    print(f" Total travel times: {len(cache.matrix)}")
    print()
    print(" Usage dalam code:")
    print("   from utils.travel_time_matrix import get_travel_time")
    print("   time_minutes = get_travel_time((lat1, lon1), (lat2, lon2))")
    print()
    print(" Next time you run API, travel time lookup will be INSTANT! 🚀")
    print("="*70)


if __name__ == "__main__":
    main()
