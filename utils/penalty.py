"""
Modul untuk menghitung penalty pada fitness function
Digunakan untuk membatasi constraint jarak dan waktu tempuh rute
"""
from typing import Tuple

# =============================================================================
# CONSTRAINT CONSTANTS
# =============================================================================

# Maximum distance constraint (dalam km)
MAX_ROUTE_DISTANCE_KM = 20.0

# Maximum travel time constraint (dalam jam)
MAX_ROUTE_TIME_HOURS = 5.0

# Maximum travel time dalam menit (untuk komputasi internal)
MAX_ROUTE_TIME_MINUTES = MAX_ROUTE_TIME_HOURS * 60  # 300 menit

# =============================================================================
# PENALTY WEIGHTS
# =============================================================================

# Penalty weight untuk distance violation
# Semakin tinggi, semakin besar penalti jika melebihi batas jarak
DISTANCE_PENALTY_WEIGHT = 0.5

# Penalty weight untuk time violation  
# Semakin tinggi, semakin besar penalti jika melebihi batas waktu
TIME_PENALTY_WEIGHT = 0.3


def calculate_distance_penalty(total_distance_km: float) -> float:
    """
    Menghitung penalty berdasarkan pelanggaran constraint jarak
    
    Penalty = 0 jika total_distance <= MAX_ROUTE_DISTANCE_KM
    Penalty = weight * (excess_distance / MAX_ROUTE_DISTANCE_KM)^2 jika melebihi
    
    Menggunakan quadratic penalty agar pelanggaran besar mendapat penalti lebih tinggi
    
    Args:
        total_distance_km: Total jarak rute dalam km
        
    Returns:
        Nilai penalty (0 jika tidak melanggar, > 0 jika melanggar)
    """
    if total_distance_km <= MAX_ROUTE_DISTANCE_KM:
        return 0.0
    
    # Hitung seberapa banyak melebihi batas (excess)
    excess_distance = total_distance_km - MAX_ROUTE_DISTANCE_KM
    
    # Quadratic penalty - semakin jauh melebihi, penalty semakin besar
    # Normalisasi dengan MAX untuk mendapat rasio
    penalty_ratio = excess_distance / MAX_ROUTE_DISTANCE_KM
    
    penalty = DISTANCE_PENALTY_WEIGHT * (penalty_ratio ** 2)
    
    return penalty


def calculate_time_penalty(total_time_minutes: float) -> float:
    """
    Menghitung penalty berdasarkan pelanggaran constraint waktu tempuh
    
    Penalty = 0 jika total_time <= MAX_ROUTE_TIME_MINUTES
    Penalty = weight * (excess_time / MAX_ROUTE_TIME_MINUTES)^2 jika melebihi
    
    Args:
        total_time_minutes: Total waktu tempuh dalam menit
        
    Returns:
        Nilai penalty (0 jika tidak melanggar, > 0 jika melanggar)
    """
    if total_time_minutes <= MAX_ROUTE_TIME_MINUTES:
        return 0.0
    
    # Hitung seberapa banyak melebihi batas (excess)
    excess_time = total_time_minutes - MAX_ROUTE_TIME_MINUTES
    
    # Quadratic penalty
    penalty_ratio = excess_time / MAX_ROUTE_TIME_MINUTES
    
    penalty = TIME_PENALTY_WEIGHT * (penalty_ratio ** 2)
    
    return penalty


def calculate_total_penalty(total_distance_km: float, total_time_minutes: float) -> float:
    """
    Menghitung total penalty dari semua constraint violations
    
    Args:
        total_distance_km: Total jarak rute dalam km
        total_time_minutes: Total waktu tempuh dalam menit
        
    Returns:
        Total penalty (jumlah dari semua penalty)
    """
    distance_penalty = calculate_distance_penalty(total_distance_km)
    time_penalty = calculate_time_penalty(total_time_minutes)
    
    return distance_penalty + time_penalty


def get_constraint_violation_info(total_distance_km: float, total_time_minutes: float) -> dict:
    """
    Mendapatkan informasi detail tentang pelanggaran constraint
    
    Args:
        total_distance_km: Total jarak rute dalam km
        total_time_minutes: Total waktu tempuh dalam menit
        
    Returns:
        Dictionary berisi informasi pelanggaran constraint
    """
    distance_violated = total_distance_km > MAX_ROUTE_DISTANCE_KM
    time_violated = total_time_minutes > MAX_ROUTE_TIME_MINUTES
    
    return {
        'distance': {
            'value': round(total_distance_km, 2),
            'max_allowed': MAX_ROUTE_DISTANCE_KM,
            'violated': distance_violated,
            'excess': round(max(0, total_distance_km - MAX_ROUTE_DISTANCE_KM), 2),
            'penalty': round(calculate_distance_penalty(total_distance_km), 6)
        },
        'time': {
            'value_minutes': round(total_time_minutes, 2),
            'value_hours': round(total_time_minutes / 60, 2),
            'max_allowed_minutes': MAX_ROUTE_TIME_MINUTES,
            'max_allowed_hours': MAX_ROUTE_TIME_HOURS,
            'violated': time_violated,
            'excess_minutes': round(max(0, total_time_minutes - MAX_ROUTE_TIME_MINUTES), 2),
            'penalty': round(calculate_time_penalty(total_time_minutes), 6)
        },
        'total_penalty': round(calculate_total_penalty(total_distance_km, total_time_minutes), 6),
        'is_feasible': not distance_violated and not time_violated
    }


def apply_penalty_to_fitness(base_fitness: float, total_penalty: float) -> float:
    """
    Menerapkan penalty pada nilai fitness
    
    Fitness yang di-penalty = base_fitness / (1 + total_penalty)
    
    Dengan formula ini:
    - Jika penalty = 0, fitness tetap sama
    - Jika penalty > 0, fitness akan berkurang
    - Semakin besar penalty, fitness semakin kecil
    
    Args:
        base_fitness: Nilai fitness dasar (tanpa penalty)
        total_penalty: Total penalty dari constraint violations
        
    Returns:
        Nilai fitness yang sudah di-penalty
    """
    if total_penalty <= 0:
        return base_fitness
    
    # Penalized fitness: fitness berkurang seiring penalty meningkat
    penalized_fitness = base_fitness / (1.0 + total_penalty)
    
    return penalized_fitness
