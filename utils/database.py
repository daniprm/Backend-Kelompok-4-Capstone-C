"""
Database utility functions untuk mengakses data wisata dari SQLite
"""
import os
import sqlite3
from typing import List, Dict, Optional
from contextlib import contextmanager

# Get absolute path to database file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "data_wisata_surabaya.db")

@contextmanager
def get_db_connection(db_path: str = DB_PATH):
    """
    Context manager untuk koneksi database SQLite
    
    Args:
        db_path: Path ke file database SQLite
        
    Yields:
        sqlite3.Connection: Koneksi database
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Mengaktifkan akses kolom berdasarkan nama
    try:
        yield conn
    finally:
        conn.close()


def get_all_wisata(kategori: Optional[str] = None, limit: Optional[int] = None, offset: int = 0) -> tuple[List[Dict], int]:
    """
    Mengambil semua data wisata dari database dengan filtering dan pagination
    
    Args:
        kategori: Filter berdasarkan kategori (optional)
        limit: Batas jumlah data yang dikembalikan (optional)
        offset: Offset untuk pagination (default: 0)
        
    Returns:
        Tuple of (list of wisata dictionaries, total count)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Query untuk menghitung total
        if kategori:
            count_query = "SELECT COUNT(*) FROM wisata_sby WHERE kategori LIKE ?"
            cursor.execute(count_query, (f'%{kategori}%',))
        else:
            count_query = "SELECT COUNT(*) FROM wisata_sby"
            cursor.execute(count_query)
        
        total = cursor.fetchone()[0]
        
        # Query untuk mengambil data
        query = "SELECT * FROM wisata_sby"
        params = []
        
        if kategori:
            query += " WHERE kategori LIKE ?"
            params.append(f'%{kategori}%')
        
        query += " LIMIT ? OFFSET ?"
        params.extend([limit if limit else -1, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert Row objects ke dictionaries
        wisata_list = [dict(row) for row in rows]
        
        return wisata_list, total


def get_wisata_by_id(restaurant_id: int) -> Optional[Dict]:
    """
    Mengambil data wisata berdasarkan restaurant_id
    
    Args:
        restaurant_id: ID unik dari destinasi wisata
        
    Returns:
        Dictionary wisata data atau None jika tidak ditemukan
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM wisata_sby WHERE restaurant_id = ?"
        cursor.execute(query, (restaurant_id,))
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None


def search_wisata(search_term: str, limit: Optional[int] = None) -> List[Dict]:
    """
    Mencari wisata berdasarkan nama atau alamat
    
    Args:
        search_term: Kata kunci pencarian
        limit: Batas jumlah data yang dikembalikan (optional)
        
    Returns:
        List of wisata dictionaries
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM wisata_sby 
            WHERE nama_destinasi LIKE ? OR alamat LIKE ?
        """
        
        if limit:
            query += " LIMIT ?"
            cursor.execute(query, (f'%{search_term}%', f'%{search_term}%', limit))
        else:
            cursor.execute(query, (f'%{search_term}%', f'%{search_term}%'))
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]


def get_wisata_by_kategori(kategori: str) -> List[Dict]:
    """
    Mengambil semua wisata dengan kategori tertentu
    
    Args:
        kategori: Kategori yang dicari
        
    Returns:
        List of wisata dictionaries
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM wisata_sby WHERE kategori LIKE ?"
        cursor.execute(query, (f'%{kategori}%',))
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]


def get_wisata_statistics() -> Dict:
    """
    Mengambil statistik data wisata
    
    Returns:
        Dictionary berisi statistik data wisata
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total destinasi
        cursor.execute("SELECT COUNT(*) FROM wisata_sby")
        total = cursor.fetchone()[0]
        
        # Hitung per kategori
        cursor.execute("SELECT kategori FROM wisata_sby")
        rows = cursor.fetchall()
        
        kategori_count = {}
        for row in rows:
            kategori_str = row['kategori']
            # Split kategori jika ada multiple (dipisahkan koma)
            kategoris = [k.strip() for k in kategori_str.split(',')]
            for kat in kategoris:
                if kat:
                    kategori_count[kat] = kategori_count.get(kat, 0) + 1
        
        return {
            'total_destinations': total,
            'kategori_count': kategori_count
        }