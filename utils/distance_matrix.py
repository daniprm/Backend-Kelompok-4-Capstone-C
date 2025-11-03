"""
Pre-calculated distance matrix untuk mempercepat komputasi
Menggunakan OSRM untuk jarak rute nyata
"""
import json
import os
from typing import Dict, List, Tuple, Optional
from .distance import calculate_distance_osrm
from tqdm import tqdm
import time

class DistanceMatrixCache:
    """Cache untuk distance matrix dengan OSRM"""
    
    def __init__(self, cache_file: str = "./data/distance_matrix_osrm.json"):
        self.cache_file = cache_file
        self.matrix: Dict[str, float] = {}
        self._key_cache: Dict[Tuple, str] = {}  # Cache untuk key lookup
        self.metadata = {
            "total_destinations": 0,
            "total_pairs": 0,
            "last_updated": None,
            "osrm_enabled": True,
            "osrm_success": 0,
            "osrm_fallback": 0
        }
        
    def _make_key(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> str:
        """Buat key unik untuk pasangan koordinat (dengan caching)"""
        # Cache lookup key untuk performa
        cache_key = (coord1, coord2)
        if cache_key in self._key_cache:
            return self._key_cache[cache_key]
        
        # Sort agar (A,B) = (B,A)
        coords = sorted([coord1, coord2])
        key = f"{coords[0][0]:.6f},{coords[0][1]:.6f}|{coords[1][0]:.6f},{coords[1][1]:.6f}"
        
        # Simpan ke cache (both directions)
        self._key_cache[cache_key] = key
        self._key_cache[(coord2, coord1)] = key
        
        return key
    
    def get(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> Optional[float]:
        """Ambil jarak dari cache"""
        key = self._make_key(coord1, coord2)
        return self.matrix.get(key)
    
    def set(self, coord1: Tuple[float, float], coord2: Tuple[float, float], distance: float):
        """Simpan jarak ke cache"""
        key = self._make_key(coord1, coord2)
        self.matrix[key] = distance
    
    def load(self) -> bool:
        """Load matrix dari file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.matrix = data.get('matrix', {})
                    self.metadata = data.get('metadata', self.metadata)
                print(f"✓ Loaded {len(self.matrix)} cached distances")
                print(f"  Last updated: {self.metadata.get('last_updated', 'Unknown')}")
                print(f"  OSRM success: {self.metadata.get('osrm_success', 0)}")
                print(f"  OSRM fallback: {self.metadata.get('osrm_fallback', 0)}")
                return True
            except Exception as e:
                print(f"⚠ Error loading cache: {e}")
        return False
    
    def save(self):
        """Simpan matrix ke file"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        # Update metadata
        self.metadata['total_pairs'] = len(self.matrix)
        self.metadata['last_updated'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        data = {
            'matrix': self.matrix,
            'metadata': self.metadata
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Saved {len(self.matrix)} distances to {self.cache_file}")
    
    def build_matrix(self, destinations: List, user_location: Tuple[float, float] = None, max_retries: int = 3):
        """
        Build distance matrix dengan OSRM REAL ROUTES ONLY
        SMART: Hanya hitung pasangan yang belum ada di cache!
        RETRY: Coba ulang jika gagal (max 3x per pair)
        
        Args:
            destinations: List of Destination objects
            user_location: Optional user location
            max_retries: Jumlah percobaan ulang jika gagal (default: 3)
        """
        print("\n" + "="*70)
        print("🔨 BUILDING DISTANCE MATRIX - OSRM REAL ROUTES ONLY")
        print("="*70)
        
        # Kumpulkan koordinat
        coords = [(d.latitude, d.longitude) for d in destinations]
        if user_location:
            coords.append(user_location)
        
        total_possible = len(coords) * (len(coords) - 1) // 2
        already_cached = 0
        to_calculate = []
        
        # Cek mana yang perlu dihitung
        print("\n📊 Analyzing pairs...")
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                coord1, coord2 = coords[i], coords[j]
                
                if self.get(coord1, coord2) is not None:
                    already_cached += 1
                else:
                    to_calculate.append((coord1, coord2))
        
        print(f"  Total pairs: {total_possible}")
        print(f"  Already cached: {already_cached} ✓")
        print(f"  Need to calculate: {len(to_calculate)} 🔄")
        
        if len(to_calculate) == 0:
            print("\n✅ All distances already cached! No calculation needed.")
            return
        
        # Hitung yang belum ada
        print(f"\n🚀 Calculating {len(to_calculate)} distances using OSRM (real road routes)")
        print("⏳ This may take a while for the first time...")
        print(f"� Auto-retry enabled: up to {max_retries} attempts per pair")
        print("�💡 Tip: Be patient! This is done ONCE, then instant forever!\n")
        
        calculated = 0
        osrm_success = 0
        osrm_failed = 0
        retry_count = 0
        
        with tqdm(total=len(to_calculate), desc="Progress", unit="pairs", ncols=80) as pbar:
            for idx, (coord1, coord2) in enumerate(to_calculate):
                distance = None
                
                # Retry loop untuk setiap pair
                for attempt in range(max_retries):
                    try:
                        distance = calculate_distance_osrm(coord1[0], coord1[1], coord2[0], coord2[1])
                        
                        if distance is not None:
                            # Berhasil!
                            self.set(coord1, coord2, distance)
                            osrm_success += 1
                            calculated += 1
                            if attempt > 0:
                                retry_count += 1
                            break
                        else:
                            # OSRM return None, tunggu sebentar lalu retry
                            if attempt < max_retries - 1:
                                time.sleep(0.5)  # Wait 0.5s before retry
                            
                    except Exception as e:
                        # Error, tunggu sebentar lalu retry
                        if attempt < max_retries - 1:
                            time.sleep(0.5)  # Wait 0.5s before retry
                        else:
                            # Gagal setelah max retries
                            print(f"\n⚠ Failed after {max_retries} attempts: {coord1} - {coord2}")
                            print(f"   Error: {str(e)[:100]}")
                
                # Jika masih gagal setelah semua retry
                if distance is None:
                    osrm_failed += 1
                    print(f"\n❌ SKIPPED pair (no route found): {coord1} - {coord2}")
                
                pbar.update(1)
                
                # Save setiap 50 kalkulasi untuk safety
                if calculated % 50 == 0 and calculated > 0:
                    # Update metadata sebelum save
                    self.metadata['osrm_success'] = self.metadata.get('osrm_success', 0) + osrm_success
                    self.metadata['osrm_fallback'] = 0
                    osrm_success = 0  # Reset counter setelah save
                    self.save()
        
        # Update metadata final
        self.metadata['total_destinations'] = len(coords)
        self.metadata['osrm_enabled'] = True
        self.metadata['osrm_success'] = self.metadata.get('osrm_success', 0) + osrm_success
        self.metadata['osrm_fallback'] = 0  # No fallback
        
        # Final save
        self.save()
        
        print("\n" + "="*70)
        print("✅ DISTANCE MATRIX BUILD COMPLETE!")
        print("="*70)
        print(f"  Successfully calculated: {osrm_success}")
        print(f"  Failed (no route): {osrm_failed}")
        print(f"  Retry successes: {retry_count}")
        print(f"  Total cached distances: {len(self.matrix)}")
        print(f"  Cache file: {self.cache_file}")
        print("="*70)
        print("\n💾 Matrix saved! Next time will be instant!")


# Global cache instance
_distance_cache = DistanceMatrixCache()

def get_cached_distance(coord1: Tuple[float, float], coord2: Tuple[float, float], max_retries: int = 3) -> Optional[float]:
    """
    Get distance dari cache (atau hitung jika belum ada)
    ONLY OSRM REAL ROUTES - No Haversine fallback!
    
    Args:
        coord1: Koordinat pertama (lat, lon)
        coord2: Koordinat kedua (lat, lon)
        max_retries: Retry attempts jika gagal
        
    Returns:
        Distance dalam km (atau None jika tidak ada rute)
    """
    # Cek cache
    distance = _distance_cache.get(coord1, coord2)
    
    # Jika tidak ada, hitung dengan OSRM dan simpan (dengan retry)
    if distance is None:
        for attempt in range(max_retries):
            try:
                distance = calculate_distance_osrm(coord1[0], coord1[1], coord2[0], coord2[1])
                if distance is not None:
                    _distance_cache.set(coord1, coord2, distance)
                    break
                else:
                    # Wait before retry
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
        
        # Jika masih gagal, return None (no fallback!)
        if distance is None:
            print(f"⚠ Warning: No route found for {coord1} - {coord2}")
    
    return distance

def initialize_distance_cache(destinations: List, user_location: Tuple[float, float] = None, rebuild: bool = False, max_retries: int = 3):
    """
    Initialize cache dan build matrix jika perlu
    ONLY OSRM REAL ROUTES!
    
    Args:
        destinations: List destinasi
        user_location: User location (optional)
        rebuild: Force rebuild matrix (default: False, auto-detect)
        max_retries: Retry attempts per pair jika gagal
    """
    # Load existing cache
    cache_exists = _distance_cache.load()
    
    if rebuild or not cache_exists:
        # Build/Rebuild matrix
        _distance_cache.build_matrix(destinations, user_location, max_retries=max_retries)
    else:
        # Auto-detect: cek apakah ada destinasi baru
        coords = [(d.latitude, d.longitude) for d in destinations]
        if user_location:
            coords.append(user_location)
        
        # Cek apakah jumlah destinasi berubah
        cached_dest = _distance_cache.metadata.get('total_destinations', 0)
        current_dest = len(coords)
        
        if current_dest > cached_dest:
            print(f"\n🔔 Detected new destinations: {cached_dest} → {current_dest}")
            print("   Running incremental build...")
            _distance_cache.build_matrix(destinations, user_location, max_retries=max_retries)
        else:
            print("✓ Distance cache is up to date!")

def rebuild_distance_cache(destinations: List, user_location: Tuple[float, float] = None, max_retries: int = 3):
    """Force rebuild entire distance matrix - OSRM REAL ROUTES ONLY"""
    _distance_cache.matrix = {}  # Clear cache
    _distance_cache.metadata = {
        "total_destinations": 0,
        "total_pairs": 0,
        "last_updated": None,
        "osrm_enabled": True,
        "osrm_success": 0,
        "osrm_fallback": 0
    }
    _distance_cache.build_matrix(destinations, user_location, max_retries=max_retries)

def get_cache_stats() -> dict:
    """Get statistik cache"""
    return {
        "total_cached_pairs": len(_distance_cache.matrix),
        "cache_file": _distance_cache.cache_file,
        "cache_exists": os.path.exists(_distance_cache.cache_file),
        "metadata": _distance_cache.metadata
    }
