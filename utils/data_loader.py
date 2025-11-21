"""
Utility functions untuk memuat dan memproses data destinasi wisata
"""
import csv
import os
import sqlite3
from typing import List, Dict
from models.destination import Destination

def load_destinations_from_csv(filepath: str) -> List[Destination]:
    """
    Memuat data destinasi wisata dari file CSV
    
    Args:
        filepath: Path ke file CSV
        
    Returns:
        List of Destination objects
    """
    destinations = []
    
    with open(filepath, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            try:
                # Parse kategori (bisa multiple, dipisahkan koma)
                kategori_str = row['kategori'].strip()
                kategori_list = [k.strip() for k in kategori_str.split(',')]
                
                # Parse koordinat (handle format dengan koma sebagai desimal separator)
                lat_str = row['latitude'].replace(',', '.')
                lon_str = row['longitude'].replace(',', '.')
                
                # Parse optional fields (alamat, image_url, deskripsi)
                alamat = row.get('alamat', '').strip() if row.get('alamat') else None
                image_url = row.get('image_url', '').strip() if row.get('image_url') else None
                deskripsi = row.get('deskripsi', '').strip() if row.get('deskripsi') else None
                
                destination = Destination(
                    nama=row['nama_destinasi'].strip(),
                    kategori=kategori_list,
                    latitude=float(lat_str),
                    longitude=float(lon_str),
                    alamat=alamat,
                    image_url=image_url,
                    deskripsi=deskripsi
                )
                
                destinations.append(destination)
                
            except (ValueError, KeyError) as e:
                print(f"Error parsing row {row}: {e}")
                continue
    
    return destinations


def load_destinations_from_sqlite(db_path: str = None) -> List[Destination]:
    """
    Memuat data destinasi wisata dari database SQLite
    
    Args:
        db_path: Path ke file database SQLite (optional, uses default if not provided)
        
    Returns:
        List of Destination objects
    """
    if db_path is None:
        # Default to the data folder database path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, "data", "data_wisata_surabaya.db")
    
    destinations = []
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM wisata_sby")
        rows = cursor.fetchall()
        
        for row in rows:
            try:
                # Parse kategori (bisa multiple, dipisahkan koma)
                kategori_str = row['kategori'].strip()
                kategori_list = [k.strip() for k in kategori_str.split(',')]
                
                # Parse koordinat
                lat_str = row['latitude'].replace(',', '.')
                lon_str = row['longitude'].replace(',', '.')
                
                # Get optional fields
                alamat = row['alamat'] if row['alamat'] else None
                image_url = row['image_url'] if row['image_url'] else None
                deskripsi = row['deskripsi'] if row['deskripsi'] else None
                
                destination = Destination(
                    nama=row['nama_destinasi'].strip(),
                    kategori=kategori_list,
                    latitude=float(lat_str),
                    longitude=float(lon_str),
                    alamat=alamat,
                    image_url=image_url,
                    deskripsi=deskripsi
                )
                
                destinations.append(destination)
                
            except (ValueError, KeyError) as e:
                print(f"Error parsing row {dict(row)}: {e}")
                continue
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        print(f"Database path: {db_path}")
        raise
    
    return destinations


def filter_destinations_by_category(destinations: List[Destination], 
                                    category: str) -> List[Destination]:
    """
    Filter destinasi berdasarkan kategori tertentu
    
    Args:
        destinations: List semua destinasi
        category: Kategori yang dicari
        
    Returns:
        List destinasi yang memiliki kategori tersebut
    """
    return [dest for dest in destinations if dest.has_category(category)]


def group_destinations_by_category(destinations: List[Destination]) -> Dict[str, List[Destination]]:
    """
    Mengelompokkan destinasi berdasarkan kategori
    
    Args:
        destinations: List semua destinasi
        
    Returns:
        Dictionary dengan key kategori dan value list destinasi
    """
    grouped = {
        'makanan_berat': [],
        'makanan_ringan': [],
        'non_kuliner': [],
        'oleh_oleh': [],
        'all': []
    }
    
    for dest in destinations:
        for category in dest.kategori:
            if category in grouped:
                grouped[category].append(dest)
    
    return grouped