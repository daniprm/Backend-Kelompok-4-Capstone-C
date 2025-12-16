"""
Model untuk representasi rute wisata
"""
from typing import List, Tuple
from models.destination import Destination
from utils.distance import calculate_distance
from utils.travel_time_matrix import get_travel_time

class Route:
    """
    Class untuk merepresentasikan satu rute wisata
    
    Attributes:
        start_point: Koordinat titik awal (latitude, longitude)
        destinations: List destinasi yang dikunjungi dalam urutan tertentu
        end_point: Koordinat titik akhir (latitude, longitude)
    """
    
    def __init__(
          self, start_point: Tuple[float, float], 
          destinations: List[Destination],
          # end_point: Tuple[float, float] = None
        ):
        """
        Inisialisasi rute
        
        Args:
            start_point: Koordinat awal (lat, lon)
            destinations: List destinasi yang dikunjungi
            end_point: Koordinat akhir, default sama dengan start_point
        """
        self.start_point = start_point
        self.destinations = destinations
        # self.end_point = end_point if end_point else start_point
        
    def calculate_total_distance(self) -> float:
        """
        Menghitung total jarak rute dari titik awal ke semua destinasi dan kembali ke titik akhir
        
        Returns:
            Total jarak dalam kilometer
        """
        if not self.destinations:
            return 0.0
        
        total_distance = 0.0
        
        # Jarak dari titik awal ke destinasi pertama
        total_distance += calculate_distance(
            self.start_point[0], self.start_point[1],
            self.destinations[0].latitude, self.destinations[0].longitude
        )
        
        # Jarak antar destinasi
        for i in range(len(self.destinations) - 1):
            total_distance += calculate_distance(
                self.destinations[i].latitude, self.destinations[i].longitude,
                self.destinations[i + 1].latitude, self.destinations[i + 1].longitude
            )
        
        # # Jarak dari destinasi terakhir ke titik akhir
        # total_distance += calculate_distance(
        #     self.destinations[-1].latitude, self.destinations[-1].longitude,
        #     self.end_point[0], self.end_point[1]
        # )
        
        return total_distance
    
    def calculate_total_travel_time(self) -> float:
        """
        Menghitung total waktu tempuh rute menggunakan travel time matrix
        
        Returns:
            Total waktu tempuh dalam menit
        """
        if not self.destinations:
            return 0.0
        
        total_time = 0.0
        
        # Waktu tempuh dari titik awal ke destinasi pertama
        time_to_first = get_travel_time(
            self.start_point,
            (self.destinations[0].latitude, self.destinations[0].longitude)
        )
        if time_to_first is not None:
            total_time += time_to_first
        
        # Waktu tempuh antar destinasi
        for i in range(len(self.destinations) - 1):
            coord1 = (self.destinations[i].latitude, self.destinations[i].longitude)
            coord2 = (self.destinations[i + 1].latitude, self.destinations[i + 1].longitude)
            
            travel_time = get_travel_time(coord1, coord2)
            if travel_time is not None:
                total_time += travel_time
        
        return total_time
    
    def is_valid_route_order(self) -> bool:
        """
        Memvalidasi apakah urutan rute sesuai dengan pola: K1, C1, W1, K2, W2, C2, K3, O
        
        Returns:
            True jika urutan valid
        """
        if len(self.destinations) != 8:
            return False
        
        # Pola urutan yang diharapkan
        expected_pattern = [
            'makanan_berat',  # K1
            'makanan_ringan',  # C1
            'non_kuliner',     # W1
            'makanan_berat',   # K2
            'non_kuliner',     # W2
            'makanan_ringan',  # C2
            'makanan_berat',   # K3
            'oleh_oleh'        # O
        ]
        
        # Validasi urutan
        for i, expected_category in enumerate(expected_pattern):
            if not self.destinations[i].has_category(expected_category):
                return False
        
        return True
    
    def get_route_summary(self) -> dict:
        """
        Mendapatkan ringkasan rute
        
        Returns:
            Dictionary berisi informasi rute
        """
        from utils.penalty import get_constraint_violation_info
        
        total_distance = self.calculate_total_distance()
        total_time = self.calculate_total_travel_time()
        constraint_info = get_constraint_violation_info(total_distance, total_time)
        
        return {
            'start_point': self.start_point,
            # 'end_point': self.end_point,
            'total_destinations': len(self.destinations),
            'total_distance_km': round(total_distance, 2),
            'total_travel_time_minutes': round(total_time, 2),
            'total_travel_time_hours': round(total_time / 60, 2),
            'constraint_info': constraint_info,
            'destinations': [
                {
                    'order': i + 1,
                    'place_id': dest.place_id,
                    'nama_destinasi': dest.nama,
                    'kategori': dest.kategori,
                    'latitude': dest.latitude,
                    'longitude': dest.longitude,
                    'alamat': dest.alamat,
                    'image_url': dest.image_url,
                    'deskripsi': dest.deskripsi
                }
                for i, dest in enumerate(self.destinations)
            ],
            'is_valid_order': self.is_valid_route_order()
        }
    
    def __repr__(self) -> str:
        return f"Route(destinations={len(self.destinations)}, distance={self.calculate_total_distance():.2f}km)"
