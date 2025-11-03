"""
Utility functions untuk menghitung jarak antar koordinat
Menggunakan pre-calculated distance matrix dengan OSRM real routes
"""
import math
import requests
from typing import Optional
import time

# OSRM API Configuration
OSRM_BASE_URL = "http://router.project-osrm.org"
OSRM_PROFILE = "driving"  # Options: 'driving', 'bike', 'foot' (motor menggunakan 'driving')
# Note: Public OSRM tidak punya profil 'motorcycle', gunakan 'driving' untuk motor
USE_OSRM = True  # Set False untuk fallback ke Haversine
OSRM_TIMEOUT = 5  # Timeout in seconds
OSRM_MAX_RETRIES = 2  # Maximum retry attempts

# Distance Matrix Configuration
USE_DISTANCE_MATRIX = True  # Prioritas utama: gunakan pre-calculated matrix
_distance_matrix_cache = None  # Will be initialized on first use

# Cache untuk menyimpan hasil OSRM agar tidak request berulang untuk koordinat yang sama
_osrm_cache = {}

def calculate_distance_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Menghitung jarak antara dua titik koordinat menggunakan formula Haversine
    (jarak garis lurus/as the crow flies)
    
    Args:
        lat1: Latitude titik pertama
        lon1: Longitude titik pertama
        lat2: Latitude titik kedua
        lon2: Longitude titik kedua
        
    Returns:
        Jarak dalam kilometer
    """
    # Radius bumi dalam kilometer
    R = 6371.0
    
    # Konversi derajat ke radian
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Selisih koordinat
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Formula Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Jarak dalam kilometer
    distance = R * c
    
    return distance

def calculate_distance_osrm(lat1: float, lon1: float, lat2: float, lon2: float) -> Optional[float]:
    """
    Menghitung jarak rute nyata antara dua titik menggunakan OSRM API
    Menggunakan profil kendaraan yang dikonfigurasi (default: driving untuk motor/mobil)
    
    Args:
        lat1: Latitude titik pertama
        lon1: Longitude titik pertama
        lat2: Latitude titik kedua
        lon2: Longitude titik kedua
        
    Returns:
        Jarak rute dalam kilometer, atau None jika gagal
    """
    # Cek cache
    cache_key = f"{lat1},{lon1}-{lat2},{lon2}-{OSRM_PROFILE}"
    if cache_key in _osrm_cache:
        return _osrm_cache[cache_key]
    
    # Format: longitude,latitude (OSRM menggunakan lon,lat bukan lat,lon!)
    # Untuk motor/motorcycle, gunakan profil 'driving' karena public OSRM tidak punya profil motorcycle
    url = f"{OSRM_BASE_URL}/route/v1/{OSRM_PROFILE}/{lon1},{lat1};{lon2},{lat2}"
    params = {
        'overview': 'false',  # Kita hanya butuh jarak, tidak butuh geometry
        'steps': 'false'
    }
    
    for attempt in range(OSRM_MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=OSRM_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 'Ok' and 'routes' in data and len(data['routes']) > 0:
                    # Jarak dalam meter, konversi ke kilometer
                    distance_km = data['routes'][0]['distance'] / 1000.0
                    
                    # Simpan ke cache
                    _osrm_cache[cache_key] = distance_km
                    
                    return distance_km
            
            # Jika gagal, tunggu sebentar sebelum retry
            if attempt < OSRM_MAX_RETRIES - 1:
                time.sleep(0.1)
                
        except (requests.RequestException, KeyError, ValueError) as e:
            # Jika error, tunggu sebentar sebelum retry
            if attempt < OSRM_MAX_RETRIES - 1:
                time.sleep(0.1)
            continue
    
    # Jika semua retry gagal, return None
    return None

def _get_distance_matrix():
    """Lazy load distance matrix cache"""
    global _distance_matrix_cache
    if _distance_matrix_cache is None:
        try:
            from .distance_matrix import _distance_cache
            _distance_matrix_cache = _distance_cache
            # Load matrix jika belum loaded (cek length, bukan truthiness)
            if len(_distance_matrix_cache.matrix) == 0:
                _distance_matrix_cache.load()
        except Exception:
            # Jika gagal load, disable distance matrix
            _distance_matrix_cache = False
    return _distance_matrix_cache if _distance_matrix_cache else None


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float, 
                      use_haversine_for_user: bool = False) -> float:
    """
    Menghitung jarak antara dua titik koordinat.
    
    Strategi:
    1. Pre-calculated Distance Matrix untuk destination-to-destination (OSRM real routes)
    2. Haversine untuk user location (tidak ada di matrix, instant, acceptable untuk start point)
    3. OSRM real-time API sebagai fallback (slow)
    
    Args:
        lat1: Latitude titik pertama
        lon1: Longitude titik pertama
        lat2: Latitude titik kedua
        lon2: Longitude titik kedua
        use_haversine_for_user: Jika True, skip matrix lookup (untuk user location)
        
    Returns:
        Jarak dalam kilometer
    """
    # Jika koordinat sama, return 0
    if lat1 == lat2 and lon1 == lon2:
        return 0.0
    
    # Jika flag haversine aktif (untuk user location), langsung gunakan Haversine
    if use_haversine_for_user:
        return calculate_distance_haversine(lat1, lon1, lat2, lon2)
    
    # PRIORITAS 1: Coba gunakan Distance Matrix (pre-calculated OSRM routes)
    if USE_DISTANCE_MATRIX:
        matrix = _get_distance_matrix()
        if matrix is not None:
            coord1 = (lat1, lon1)
            coord2 = (lat2, lon2)
            distance = matrix.get(coord1, coord2)
            if distance is not None:
                return distance
            # Jika tidak ada di matrix, kemungkinan besar salah satu adalah user location
            # Gunakan Haversine untuk performa (tidak perlu hit OSRM API)
            else:
                return calculate_distance_haversine(lat1, lon1, lat2, lon2)
    
    # PRIORITAS 2: Coba gunakan OSRM real-time jika diaktifkan (jarang terjadi)
    if USE_OSRM:
        osrm_distance = calculate_distance_osrm(lat1, lon1, lat2, lon2)
        if osrm_distance is not None:
            return osrm_distance
    
    # PRIORITAS 3: Fallback ke Haversine
    return calculate_distance_haversine(lat1, lon1, lat2, lon2)


def calculate_route_distance(points: list) -> float:
    """
    Menghitung total jarak untuk serangkaian titik koordinat
    
    Args:
        points: List of tuples (latitude, longitude)
        
    Returns:
        Total jarak dalam kilometer
    """
    if len(points) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(points) - 1):
        total_distance += calculate_distance(
            points[i][0], points[i][1],
            points[i + 1][0], points[i + 1][1]
        )
    
    return total_distance


def clear_osrm_cache():
    """
    Menghapus cache OSRM
    """
    global _osrm_cache
    _osrm_cache.clear()


def get_osrm_cache_stats() -> dict:
    """
    Mendapatkan statistik cache OSRM dan Distance Matrix
    
    Returns:
        Dictionary berisi statistik cache
    """
    matrix = _get_distance_matrix()
    matrix_stats = {
        'enabled': False,
        'cached_pairs': 0,
        'last_updated': None
    }
    
    if matrix is not None:
        matrix_stats = {
            'enabled': True,
            'cached_pairs': len(matrix.matrix),
            'last_updated': matrix.metadata.get('last_updated', 'Unknown'),
            'osrm_success': matrix.metadata.get('osrm_success', 0),
            'total_destinations': matrix.metadata.get('total_destinations', 0)
        }
    
    return {
        'distance_matrix': matrix_stats,
        'osrm_runtime_cache_size': len(_osrm_cache),
        'osrm_enabled': USE_OSRM,
        'osrm_base_url': OSRM_BASE_URL,
        'osrm_profile': OSRM_PROFILE,
        'use_distance_matrix': USE_DISTANCE_MATRIX
    }


def set_use_osrm(enabled: bool):
    """
    Mengaktifkan atau menonaktifkan penggunaan OSRM
    
    Args:
        enabled: True untuk menggunakan OSRM, False untuk Haversine saja
    """
    global USE_OSRM
    USE_OSRM = enabled


def set_use_distance_matrix(enabled: bool):
    """
    Mengaktifkan atau menonaktifkan penggunaan Distance Matrix
    
    Args:
        enabled: True untuk menggunakan pre-calculated matrix, False untuk disable
    """
    global USE_DISTANCE_MATRIX
    USE_DISTANCE_MATRIX = enabled


def set_osrm_profile(profile: str):
    """
    Mengatur profil OSRM (mode transportasi)
    
    Args:
        profile: Profil OSRM - 'driving' (motor/mobil), 'bike' (sepeda), 'foot' (jalan kaki)
    
    Note:
        - 'driving': Untuk motor/mobil (paling cocok untuk motor di Indonesia)
        - 'bike': Untuk sepeda
        - 'foot': Untuk pejalan kaki
        Public OSRM server tidak memiliki profil 'motorcycle' terpisah.
    """
    global OSRM_PROFILE
    valid_profiles = ['driving', 'bike', 'foot']
    
    if profile not in valid_profiles:
        raise ValueError(f"Invalid profile. Must be one of: {valid_profiles}")
    
    OSRM_PROFILE = profile
    # Clear cache karena profil berbeda akan menghasilkan jarak berbeda
    clear_osrm_cache()
