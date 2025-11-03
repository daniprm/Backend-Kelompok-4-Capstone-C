"""
Model untuk representasi destinasi wisata
"""
from typing import List, Set
from dataclasses import dataclass

@dataclass
class Destination:
    """
    Class untuk merepresentasikan satu destinasi wisata
    
    Attributes:
        nama: Nama destinasi wisata
        kategori: List kategori destinasi (makanan_berat, makanan_ringan, non_kuliner, oleh_oleh)
        latitude: Koordinat latitude
        longitude: Koordinat longitude
        alamat: Alamat destinasi (optional)
        image_url: URL gambar destinasi (optional)
        deskripsi: Deskripsi destinasi (optional)
    """
    nama: str
    kategori: List[str]
    latitude: float
    longitude: float
    alamat: str = None
    image_url: str = None
    deskripsi: str = None
    
    def has_category(self, category: str) -> bool:
        """
        Mengecek apakah destinasi memiliki kategori tertentu
        
        Args:
            category: Kategori yang dicari
            
        Returns:
            True jika destinasi memiliki kategori tersebut
        """
        return category in self.kategori
    
    def __repr__(self) -> str:
        return f"Destination(nama={self.nama}, kategori={self.kategori})"
