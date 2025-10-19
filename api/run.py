import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Impor dari modul lokal
from system import TourismRouteRecommendationSystem
from api.config import OUTPUT_DIR, DATA_FILE_PATH
from api.endpoints import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Perintah saat Startup Server ---
    print("Server FastAPI sedang berjalan...")
    
    # 1. Pastikan direktori output ada
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Direktori output di: {os.path.abspath(OUTPUT_DIR)}")
    print(f"Mencari data di: {os.path.abspath(DATA_FILE_PATH)}")

    # 2. Muat sistem rekomendasi (satu kali)
    print("Memuat sistem rekomendasi (satu kali)...")
    try:
        system = TourismRouteRecommendationSystem(data_file=DATA_FILE_PATH)
        system.load_data()
        # Simpan instance sistem di 'app.state' agar bisa diakses oleh endpoint
        app.state.recommendation_system = system
        print("Sistem rekomendasi berhasil dimuat.")
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Data file not found at {DATA_FILE_PATH}")
        print("Pastikan file 'data_wisata_sby.csv' ada di folder 'data'.")
        # Biarkan server crash jika data tidak ada
        raise e
        
    yield
    
    # --- Perintah saat Shutdown Server ---
    print("Server FastAPI sedang berhenti...")
    app.state.recommendation_system = None
    print("Sistem rekomendasi dibersihkan.")


# --- Inisialisasi Aplikasi FastAPI ---
app = FastAPI(
    title="API Optimasi Rute Wisata Halal (HGA)",
    description="API untuk mendapatkan rekomendasi rute wisata halal di Surabaya menggunakan Hybrid Genetic Algorithm.",
    version="1.0.0",
    lifespan=lifespan  # Gunakan fungsi lifespan di atas
)

# 1. Mount direktori statis
# Ini membuat folder 'api_outputs' dapat diakses publik melalui URL '/static'
app.mount("/static", StaticFiles(directory=OUTPUT_DIR), name="static")

# 2. Masukkan router dari endpoints.py
app.include_router(api_router)

# 3. Endpoint root sederhana
@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "Selamat datang di API Optimasi Rute Wisata HGA.",
        "docs": "/docs"
    }