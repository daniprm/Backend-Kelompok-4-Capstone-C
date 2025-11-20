import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Impor dari modul lokal
from system import TourismRouteRecommendationSystem
from api.config import OUTPUT_DIR, DATA_FILE_PATH
from api.endpoints import router as api_router, initialize_system

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Perintah saat Startup Server ---
    print("Server FastAPI sedang berjalan...")
    
    # 1. Pastikan direktori output ada
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Direktori output di: {os.path.abspath(OUTPUT_DIR)}")
    
    # 2. Load destinations dari SQLite (dipanggil dari endpoints.py)
    print("Memuat data destinasi dari SQLite...")
    try:
        initialize_system()
        print("Destinasi berhasil dimuat dari database.")
    except Exception as e:
        print(f"FATAL ERROR: Gagal memuat data destinasi: {e}")
        raise e
        
    yield
    
    # --- Perintah saat Shutdown Server ---
    print("Server FastAPI sedang berhenti...")
    print("Cleanup selesai.")


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        '*'
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)