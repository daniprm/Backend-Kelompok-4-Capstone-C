"""
Utility functions untuk memuat dan memproses data destinasi wisata
"""
import json
from typing import List, Dict
from models.destination import Destination

def load_destinations_from_csv(filepath: str) -> List[Destination]:
    """
    Memuat data destinasi wisata dari file JSONL
    
    Args:
        filepath: Path ke file JSONL
        
    Returns:
        List of Destination objects
    """
    destinations = []
    
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                # Parse JSON dari setiap baris
                data = json.loads(line.strip())
                
                # Parse kategori (bisa multiple, dipisahkan koma)
                kategori_str = data['kategori'].strip()
                kategori_list = [k.strip() for k in kategori_str.split(',')]
                
                # Parse koordinat (handle format string dengan koma sebagai desimal separator)
                lat_str = str(data['latitude']).replace(',', '.')
                lon_str = str(data['longitude']).replace(',', '.')
                latitude = float(lat_str)
                longitude = float(lon_str)
                
                # Parse place_id
                place_id = data.get('place_id')
                
                # Parse optional fields (alamat, image_url, deskripsi)
                alamat = data.get('alamat', '').strip() if data.get('alamat') else None
                image_url = data.get('image_url', '').strip() if data.get('image_url') else None
                deskripsi = data.get('deskripsi', '').strip() if data.get('deskripsi') else None
                
                # Set None jika string kosong atau 'null'
                if alamat == '':
                    alamat = None
                if image_url == '':
                    image_url = None
                if deskripsi == '' or deskripsi == 'null':
                    deskripsi = None
                
                destination = Destination(
                    nama=data['nama_destinasi'].strip(),
                    kategori=kategori_list,
                    latitude=latitude,
                    longitude=longitude,
                    place_id=place_id,
                    alamat=alamat,
                    image_url=image_url,
                    deskripsi=deskripsi
                )
                
                destinations.append(destination)
                
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                print(f"Error parsing line: {e}")
                continue
    
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
