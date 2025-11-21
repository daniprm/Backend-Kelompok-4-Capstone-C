import os

# Menentukan path relatif terhadap LOKASI FILE INI
# Path ke root proyek (naik 3 level: config.py -> api -> halal_route_optimizer)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Path absolut ke folder data dan output
DATA_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "data_wisata_sby.csv")
DB_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "data_wisata_surabaya.db")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "api_outputs")
