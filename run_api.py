"""
FastAPI application untuk sistem rekomendasi rute wisata Surabaya
menggunakan Hybrid Genetic Algorithm (HGA)
"""
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import List, Optional
# from contextlib import asynccontextmanager
# import json
# from datetime import datetime

# from algorithms.hga import HybridGeneticAlgorithm
# from utils.data_loader import load_destinations_from_csv
# from models.route import Route
import uvicorn

def run_api():
    
    uvicorn.run(
        "api.run:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        # reload_dirs=["halal_route_optimizer"] # Aktifkan jika Anda ingin auto-reload
    )
    

if __name__ == "__main__":
    run_api()