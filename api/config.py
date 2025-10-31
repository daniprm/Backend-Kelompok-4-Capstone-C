import os

# Menentukan path relatif terhadap LOKASI FILE INI
# Path ke root proyek (naik 3 level: config.py -> api -> halal_route_optimizer)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path absolut ke folder data dan output
DATA_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "data_wisata_sby.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "api_outputs")

# === Konfigurasi Default untuk HGA dan Rekomendasi Rute ===
# Parameter HGA
DEFAULT_POPULATION_SIZE = 100
DEFAULT_GENERATIONS = 5000
DEFAULT_CROSSOVER_RATE = 0.8
DEFAULT_MUTATION_RATE = 0.1

# Parameter Rekomendasi
DEFAULT_NUM_ROUTES = 3  # Jumlah rute alternatif yang akan dikembalikan
