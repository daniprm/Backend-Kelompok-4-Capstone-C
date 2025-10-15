"""
Utility functions untuk menghitung jarak antar koordinat
"""
import math

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Menghitung jarak antara dua titik koordinat menggunakan formula Haversine
    
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
