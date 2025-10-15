"""
File konfigurasi untuk parameter Hybrid Genetic Algorithm
Dapat disesuaikan untuk tuning performa
"""

# ============================================================================
# KONFIGURASI HYBRID GENETIC ALGORITHM
# ============================================================================

HGA_CONFIG = {
    # --- Parameter Populasi ---
    'population_size': 100,
    # Ukuran populasi (jumlah solusi yang dievaluasi setiap generasi)
    # Nilai lebih besar = eksplorasi lebih baik, tapi lebih lambat
    # Rekomendasi: 50-200
    
    'generations': 200,
    # Jumlah maksimal generasi (iterasi algoritma)
    # Nilai lebih besar = lebih banyak waktu untuk konvergensi
    # Rekomendasi: 100-500
    
    # --- Parameter Operator Genetik ---
    'crossover_rate': 0.8,
    # Probabilitas crossover terjadi (0.0 - 1.0)
    # Nilai tinggi = lebih banyak eksplorasi kombinasi solusi
    # Rekomendasi: 0.7-0.9
    
    'mutation_rate': 0.1,
    # Probabilitas mutasi terjadi (0.0 - 1.0)
    # Nilai rendah = menjaga kestabilan, nilai tinggi = lebih eksploratif
    # Rekomendasi: 0.05-0.15
    
    # --- Parameter Seleksi ---
    'elitism_count': 2,
    # Jumlah individu terbaik yang dipertahankan setiap generasi
    # Memastikan solusi terbaik tidak hilang
    # Rekomendasi: 1-5
    
    'tournament_size': 5,
    # Ukuran tournament untuk tournament selection
    # Nilai lebih besar = selective pressure lebih tinggi
    # Rekomendasi: 3-7
    
    # --- Parameter Local Search (2-Opt) ---
    'use_2opt': True,
    # Apakah menggunakan 2-Opt local search
    # True = hybrid approach, False = pure GA
    
    'two_opt_iterations': 50,
    # Maksimal iterasi untuk 2-Opt optimization
    # Nilai lebih tinggi = optimasi lokal lebih intensif
    # Rekomendasi: 30-100
    
    # --- Parameter Konvergensi ---
    'convergence_patience': 30,
    # Jumlah generasi tanpa improvement untuk dianggap konvergen
    # Algoritma berhenti jika tidak ada improvement dalam N generasi
    # Rekomendasi: 20-50
    
    'convergence_threshold': 0.001,
    # Threshold improvement rate untuk konvergensi (0.1%)
    # Improvement lebih kecil dari threshold = konvergen
    # Rekomendasi: 0.001-0.01
}

# ============================================================================
# KONFIGURASI OUTPUT
# ============================================================================

OUTPUT_CONFIG = {
    'num_solutions': 3,
    # Jumlah rute terbaik yang dikembalikan
    
    'save_to_file': True,
    # Apakah menyimpan hasil ke file JSON
    
    'output_filename': 'route_recommendations.json',
    # Nama file output
    
    'print_progress': True,
    # Apakah mencetak progress setiap N generasi
    
    'progress_interval': 20,
    # Interval generasi untuk print progress
}

# ============================================================================
# KONFIGURASI DATA
# ============================================================================

DATA_CONFIG = {
    'csv_file': './data/data_wisata_sby.csv',
    # Path ke file data destinasi
    
    'encoding': 'utf-8',
    # Encoding file CSV
}

# ============================================================================
# KONFIGURASI CONSTRAINT RUTE
# ============================================================================

ROUTE_CONSTRAINTS = {
    # Pola urutan rute: K1, C1, W1, K2, W2, C2, K3, O
    'pattern': [
        'makanan_berat',   # K1
        'makanan_ringan',  # C1
        'non_kuliner',     # W1
        'makanan_berat',   # K2
        'non_kuliner',     # W2
        'makanan_ringan',  # C2
        'makanan_berat',   # K3
        'oleh_oleh'        # O
    ],
    
    'total_destinations': 8,
    # Total destinasi dalam satu rute
    
    'min_required': {
        'makanan_berat': 3,
        'makanan_ringan': 2,
        'non_kuliner': 2,
        'oleh_oleh': 1
    },
    # Minimum destinasi per kategori
}

# ============================================================================
# PRESET KONFIGURASI
# ============================================================================

PRESETS = {
    'fast': {
        # Untuk testing cepat
        'population_size': 30,
        'generations': 50,
        'two_opt_iterations': 20,
    },
    
    'balanced': {
        # Keseimbangan antara kecepatan dan kualitas
        'population_size': 100,
        'generations': 200,
        'two_opt_iterations': 50,
    },
    
    'quality': {
        # Untuk hasil terbaik (lebih lambat)
        'population_size': 200,
        'generations': 500,
        'two_opt_iterations': 100,
    },
    
    'production': {
        # Untuk production use
        'population_size': 150,
        'generations': 300,
        'two_opt_iterations': 75,
        'convergence_patience': 50,
    }
}


def get_config(preset: str = 'balanced') -> dict:
    """
    Mendapatkan konfigurasi berdasarkan preset
    
    Args:
        preset: Nama preset ('fast', 'balanced', 'quality', 'production')
        
    Returns:
        Dictionary konfigurasi HGA
    """
    config = HGA_CONFIG.copy()
    
    if preset in PRESETS:
        config.update(PRESETS[preset])
    
    return config


def print_config(config: dict):
    """
    Mencetak konfigurasi dengan format yang mudah dibaca
    
    Args:
        config: Dictionary konfigurasi
    """
    print("="*60)
    print(" KONFIGURASI HYBRID GENETIC ALGORITHM")
    print("="*60)
    
    print("\nParameter Populasi:")
    print(f"  Population Size      : {config.get('population_size', 'N/A')}")
    print(f"  Generations          : {config.get('generations', 'N/A')}")
    
    print("\nOperator Genetik:")
    print(f"  Crossover Rate       : {config.get('crossover_rate', 'N/A')}")
    print(f"  Mutation Rate        : {config.get('mutation_rate', 'N/A')}")
    
    print("\nSeleksi:")
    print(f"  Elitism Count        : {config.get('elitism_count', 'N/A')}")
    print(f"  Tournament Size      : {config.get('tournament_size', 'N/A')}")
    
    print("\nLocal Search:")
    print(f"  Use 2-Opt            : {config.get('use_2opt', 'N/A')}")
    print(f"  2-Opt Iterations     : {config.get('two_opt_iterations', 'N/A')}")
    
    print("\nKonvergensi:")
    print(f"  Patience             : {config.get('convergence_patience', 'N/A')}")
    print(f"  Threshold            : {config.get('convergence_threshold', 'N/A')}")
    
    print("="*60)
