"""
Pre-calculated travel time matrix untuk mempercepat komputasi
Menggunakan OSRM untuk waktu tempuh rute nyata
atau estimasi berdasarkan jarak jika OSRM tidak tersedia
"""
import json
import os
from typing import Dict, List, Tuple, Optional
import requests
import time
from tqdm import tqdm

# OSRM API Configuration
OSRM_BASE_URL = "http://router.project-osrm.org"
OSRM_PROFILE = "driving"  # Options: 'driving', 'bike', 'foot'
OSRM_TIMEOUT = 5  # Timeout in seconds
OSRM_MAX_RETRIES = 3  # Maximum retry attempts

# Kecepatan rata-rata untuk estimasi (km/jam)
# Digunakan jika OSRM tidak tersedia
AVERAGE_SPEED_KMH = 50  # Kecepatan rata-rata motor di Surabaya (urban traffic)


def calculate_travel_time_osrm(lat1: float, lon1: float, lat2: float, lon2: float) -> Optional[Tuple[float, float]]:
    """
    Menghitung waktu tempuh rute nyata antara dua titik menggunakan OSRM API
    
    Args:
        lat1: Latitude titik pertama
        lon1: Longitude titik pertama
        lat2: Latitude titik kedua
        lon2: Longitude titik kedua
        
    Returns:
        Tuple (duration_minutes, distance_km), atau None jika gagal
    """
    # Format: longitude,latitude (OSRM menggunakan lon,lat bukan lat,lon!)
    url = f"{OSRM_BASE_URL}/route/v1/{OSRM_PROFILE}/{lon1},{lat1};{lon2},{lat2}"
    params = {
        'overview': 'false',  # Tidak butuh geometry
        'steps': 'false'
    }
    
    for attempt in range(OSRM_MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=OSRM_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 'Ok' and 'routes' in data and len(data['routes']) > 0:
                    route = data['routes'][0]
                    
                    # Duration dalam detik, konversi ke menit
                    duration_minutes = route['duration'] / 60.0
                    
                    # Distance dalam meter, konversi ke kilometer
                    distance_km = route['distance'] / 1000.0
                    
                    return (duration_minutes, distance_km)
            
            # Jika gagal, tunggu sebentar sebelum retry
            if attempt < OSRM_MAX_RETRIES - 1:
                time.sleep(0.2)
                
        except (requests.RequestException, KeyError, ValueError) as e:
            # Jika error, tunggu sebentar sebelum retry
            if attempt < OSRM_MAX_RETRIES - 1:
                time.sleep(0.2)
            continue
    
    return None


def estimate_travel_time_from_distance(distance_km: float, speed_kmh: float = AVERAGE_SPEED_KMH) -> float:
    """
    Estimasi waktu tempuh berdasarkan jarak dan kecepatan rata-rata
    
    Args:
        distance_km: Jarak dalam kilometer
        speed_kmh: Kecepatan rata-rata dalam km/jam
        
    Returns:
        Waktu tempuh dalam menit
    """
    if distance_km <= 0:
        return 0.0
    
    # time = distance / speed (dalam jam)
    # konversi ke menit: × 60
    travel_time_minutes = (distance_km / speed_kmh) * 60
    
    return travel_time_minutes


class TravelTimeMatrixCache:
    """Cache untuk travel time matrix dengan OSRM"""
    
    def __init__(self, cache_file: str = "./data/travel_time_matrix_osrm.json"):
        self.cache_file = cache_file
        self.matrix: Dict[str, Dict] = {}  # key -> {duration: float, distance: float, source: str}
        self._key_cache: Dict[Tuple, str] = {}  # Cache untuk key lookup
        self.metadata = {
            "total_destinations": 0,
            "total_pairs": 0,
            "last_updated": None,
            "osrm_success": 0,
            "estimated_fallback": 0,
            "average_speed_kmh": AVERAGE_SPEED_KMH
        }
        
    def _make_key(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> str:
        """Buat key unik untuk pasangan koordinat (dengan caching)"""
        # Cache lookup key untuk performa
        cache_key = (coord1, coord2)
        if cache_key in self._key_cache:
            return self._key_cache[cache_key]
        
        # Sort agar (A,B) = (B,A) - untuk undirected travel time
        coords = sorted([coord1, coord2])
        key = f"{coords[0][0]:.6f},{coords[0][1]:.6f}|{coords[1][0]:.6f},{coords[1][1]:.6f}"
        
        # Simpan ke cache (both directions)
        self._key_cache[cache_key] = key
        self._key_cache[(coord2, coord1)] = key
        
        return key
    
    def get(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> Optional[Dict]:
        """
        Ambil waktu tempuh dari cache
        
        Returns:
            Dict dengan keys: duration (menit), distance (km), source (osrm/estimated)
        """
        key = self._make_key(coord1, coord2)
        return self.matrix.get(key)
    
    def get_duration(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> Optional[float]:
        """Ambil hanya duration (menit) dari cache"""
        data = self.get(coord1, coord2)
        return data.get('duration') if data else None
    
    def get_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> Optional[float]:
        """Ambil hanya distance (km) dari cache"""
        data = self.get(coord1, coord2)
        return data.get('distance') if data else None
    
    def set(self, coord1: Tuple[float, float], coord2: Tuple[float, float], 
            duration: float, distance: float, source: str = "osrm"):
        """
        Simpan waktu tempuh ke cache
        
        Args:
            duration: Waktu tempuh dalam menit
            distance: Jarak dalam kilometer
            source: Sumber data ('osrm' atau 'estimated')
        """
        key = self._make_key(coord1, coord2)
        self.matrix[key] = {
            'duration': round(duration, 2),
            'distance': round(distance, 4),
            'source': source
        }
    
    def load(self) -> bool:
        """Load matrix dari file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.matrix = data.get('matrix', {})
                    self.metadata = data.get('metadata', self.metadata)
                print(f"✓ Loaded {len(self.matrix)} cached travel times")
                print(f"  Last updated: {self.metadata.get('last_updated', 'Unknown')}")
                print(f"  OSRM success: {self.metadata.get('osrm_success', 0)}")
                print(f"  Estimated fallback: {self.metadata.get('estimated_fallback', 0)}")
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
        
        print(f"✓ Saved {len(self.matrix)} travel times to {self.cache_file}")
    
    def build_matrix(self, destinations: List, 
                     distance_matrix_file: str = "./data/distance_matrix_osrm.json",
                     use_osrm: bool = True,
                     max_retries: int = 3):
        """
        Build travel time matrix
        
        Strategi:
        1. Coba gunakan OSRM untuk mendapatkan waktu tempuh aktual (jika use_osrm=True)
        2. Jika OSRM gagal atau disabled, estimasi dari jarak dengan kecepatan rata-rata
        
        Args:
            destinations: List of Destination objects
            distance_matrix_file: Path ke distance matrix (untuk fallback)
            use_osrm: Gunakan OSRM API atau tidak
            max_retries: Jumlah percobaan ulang jika gagal
        """
        print("\n" + "="*70)
        print("🕐 BUILDING TRAVEL TIME MATRIX")
        print("="*70)
        
        if use_osrm:
            print("📡 Using OSRM API for real travel times")
        else:
            print("📐 Using distance-based estimation")
            print(f"   Average speed: {AVERAGE_SPEED_KMH} km/h")
        
        # Load distance matrix untuk fallback
        distance_matrix = {}
        if os.path.exists(distance_matrix_file):
            try:
                with open(distance_matrix_file, 'r') as f:
                    dm_data = json.load(f)
                    distance_matrix = dm_data.get('matrix', {})
                print(f"✓ Loaded distance matrix for fallback: {len(distance_matrix)} pairs")
            except Exception as e:
                print(f"⚠ Could not load distance matrix: {e}")
        
        # Kumpulkan koordinat
        coords = [(d.latitude, d.longitude) for d in destinations]
        
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
            print("\n✅ All travel times already cached! No calculation needed.")
            return
        
        # Hitung yang belum ada
        print(f"\n🚀 Calculating {len(to_calculate)} travel times...")
        if use_osrm:
            print("⏳ Using OSRM for real travel times (may take a while)...")
            print(f"🔄 Auto-retry enabled: up to {max_retries} attempts per pair")
        else:
            print("⚡ Using distance estimation (fast mode)")
        print("💡 Tip: This is done ONCE, then instant forever!\n")
        
        osrm_success = 0
        estimated_count = 0
        failed_count = 0
        
        with tqdm(total=len(to_calculate), desc="Progress", unit="pairs", ncols=80) as pbar:
            for coord1, coord2 in to_calculate:
                duration = None
                distance = None
                source = None
                
                # Strategi 1: OSRM (jika enabled)
                if use_osrm:
                    for attempt in range(max_retries):
                        result = calculate_travel_time_osrm(
                            coord1[0], coord1[1],
                            coord2[0], coord2[1]
                        )
                        
                        if result is not None:
                            duration, distance = result
                            source = "osrm"
                            osrm_success += 1
                            break
                        
                        if attempt < max_retries - 1:
                            time.sleep(0.3)  # Wait before retry
                
                # Strategi 2: Estimasi dari distance matrix
                if duration is None:
                    # Cari jarak dari distance matrix
                    dm_key = self._make_key(coord1, coord2)
                    
                    if dm_key in distance_matrix:
                        distance = distance_matrix[dm_key]
                        duration = estimate_travel_time_from_distance(distance)
                        source = "estimated"
                        estimated_count += 1
                    else:
                        # Hitung jarak haversine sebagai last resort
                        from .distance import calculate_distance_haversine
                        distance = calculate_distance_haversine(
                            coord1[0], coord1[1],
                            coord2[0], coord2[1]
                        )
                        # Apply multiplier untuk estimasi rute (1.3x dari garis lurus)
                        distance = distance * 1.3
                        duration = estimate_travel_time_from_distance(distance)
                        source = "estimated_haversine"
                        estimated_count += 1
                
                # Simpan hasil
                if duration is not None and distance is not None:
                    self.set(coord1, coord2, duration, distance, source)
                else:
                    failed_count += 1
                    print(f"\n❌ Failed to calculate: {coord1} - {coord2}")
                
                pbar.update(1)
                
                # Save setiap 100 kalkulasi untuk safety
                if (osrm_success + estimated_count) % 100 == 0:
                    self.metadata['osrm_success'] = osrm_success
                    self.metadata['estimated_fallback'] = estimated_count
                    self.save()
        
        # Update metadata final
        self.metadata['total_destinations'] = len(coords)
        self.metadata['osrm_success'] = osrm_success
        self.metadata['estimated_fallback'] = estimated_count
        self.metadata['average_speed_kmh'] = AVERAGE_SPEED_KMH
        
        # Final save
        self.save()
        
        print("\n" + "="*70)
        print("✅ TRAVEL TIME MATRIX BUILD COMPLETE!")
        print("="*70)
        print(f"  OSRM success: {osrm_success}")
        print(f"  Estimated: {estimated_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Total cached: {len(self.matrix)}")
        print("="*70)
    
    def get_statistics(self) -> Dict:
        """Dapatkan statistik travel time matrix"""
        if not self.matrix:
            return {}
        
        durations = [v['duration'] for v in self.matrix.values()]
        distances = [v['distance'] for v in self.matrix.values()]
        
        osrm_count = sum(1 for v in self.matrix.values() if v['source'] == 'osrm')
        estimated_count = sum(1 for v in self.matrix.values() if 'estimated' in v['source'])
        
        return {
            'total_pairs': len(self.matrix),
            'osrm_pairs': osrm_count,
            'estimated_pairs': estimated_count,
            'duration_stats': {
                'min': min(durations),
                'max': max(durations),
                'avg': sum(durations) / len(durations),
            },
            'distance_stats': {
                'min': min(distances),
                'max': max(distances),
                'avg': sum(distances) / len(distances),
            }
        }


# Global instance untuk digunakan di seluruh aplikasi
_travel_time_cache = TravelTimeMatrixCache()


def get_travel_time(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> Optional[float]:
    """
    Helper function untuk mendapatkan waktu tempuh dalam menit
    
    Args:
        coord1: (latitude, longitude) titik pertama
        coord2: (latitude, longitude) titik kedua
        
    Returns:
        Waktu tempuh dalam menit, atau None jika tidak ada
    """
    global _travel_time_cache
    
    # Load jika belum
    if len(_travel_time_cache.matrix) == 0:
        _travel_time_cache.load()
    
    return _travel_time_cache.get_duration(coord1, coord2)


def get_travel_time_and_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> Optional[Dict]:
    """
    Helper function untuk mendapatkan waktu tempuh dan jarak
    
    Returns:
        Dict dengan keys: duration (menit), distance (km), source
    """
    global _travel_time_cache
    
    # Load jika belum
    if len(_travel_time_cache.matrix) == 0:
        _travel_time_cache.load()
    
    return _travel_time_cache.get(coord1, coord2)
