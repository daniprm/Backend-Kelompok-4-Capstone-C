import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Impor dari modul lokal
from api.config import OUTPUT_DIR, DB_FILE_PATH
from api.endpoints import router as api_router, initialize_system

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Perintah saat Startup Server ---
    print("Server FastAPI sedang berjalan...")
    
    # 1. Pastikan direktori output ada
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Direktori output di: {os.path.abspath(OUTPUT_DIR)}")
    print(f"Mencari database di: {os.path.abspath(DB_FILE_PATH)}")

    # 2. Inisialisasi destinations untuk endpoints
    print("\n=== Initializing Destinations from SQLite ===")
    try:
        initialize_system()
        print("✓ Destinations initialized successfully for API endpoints")
    except Exception as e:
        print(f"✗ FATAL ERROR: Failed to initialize destinations")
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise e
    
    print("\n✓✓✓ Server startup completed successfully! ✓✓✓\n")
        
    yield
    
    # --- Perintah saat Shutdown Server ---
    print("Server FastAPI sedang berhenti...")
    print("Sistem dibersihkan.")


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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)