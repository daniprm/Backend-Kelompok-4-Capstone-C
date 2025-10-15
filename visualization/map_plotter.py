"""
Modul untuk plotting rute wisata pada peta interaktif
Menggunakan folium untuk visualisasi dengan routing API
"""
import folium
import requests
from typing import List, Tuple, Optional
from models.destination import Destination
from models.route import Route
import time

class RouteMapPlotter:
    """
    Class untuk membuat visualisasi peta rute wisata dengan routing API
    """
    
    def __init__(self, center_location: Tuple[float, float] = None, use_real_routes: bool = True):
        """
        Inisialisasi map plotter
        
        Args:
            center_location: Koordinat pusat peta (lat, lon). Default Surabaya
            use_real_routes: Gunakan routing API untuk rute jalan nyata (default: True)
        """
        if center_location is None:
            # Default: Pusat Surabaya
            center_location = (-7.2575, 112.7521)
        
        self.center_location = center_location
        self.map = None
        self.use_real_routes = use_real_routes
    
    def get_route_coordinates(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Mendapatkan koordinat rute jalan nyata menggunakan OSRM API
        
        Args:
            start: Koordinat awal (lat, lon)
            end: Koordinat akhir (lat, lon)
            
        Returns:
            List koordinat untuk rute atau fallback ke garis lurus
        """
        if not self.use_real_routes:
            return [start, end]
        
        try:
            # OSRM public API - format: lon,lat (terbalik dari lat,lon)
            url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
            params = {
                'overview': 'full',
                'geometries': 'geojson'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 'Ok' and 'routes' in data:
                    # Ambil koordinat dari geometry (format: [lon, lat])
                    coords = data['routes'][0]['geometry']['coordinates']
                    # Convert ke format (lat, lon)
                    route_coords = [(lat, lon) for lon, lat in coords]
                    
                    # Tambahkan delay kecil untuk menghindari rate limiting
                    time.sleep(0.1)
                    
                    return route_coords
            
            # Fallback: gunakan garis lurus jika API gagal
            print(f"  [INFO] Routing API gagal, menggunakan garis lurus")
            return [start, end]
            
        except Exception as e:
            # Jika ada error, gunakan garis lurus
            print(f"  [INFO] Error routing API: {e}, menggunakan garis lurus")
            return [start, end]
    
    def create_route_map(self, 
                        start_point: Tuple[float, float],
                        destinations: List[Destination],
                        route_name: str = "Rute Wisata") -> folium.Map:
        """
        Membuat peta dengan rute wisata
        
        Args:
            start_point: Koordinat titik awal
            destinations: List destinasi dalam urutan kunjungan
            route_name: Nama rute untuk label
            
        Returns:
            folium.Map object
        """
        # Buat peta dengan center di start point
        m = folium.Map(
            location=start_point,
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Marker untuk titik start
        folium.Marker(
            start_point,
            popup=f"<b>Titik Awal</b><br>User Location<br>{start_point}",
            tooltip="START",
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)
        
        # List untuk menyimpan semua koordinat rute (untuk fit bounds)
        all_route_coords = [start_point]
        
        # Marker untuk setiap destinasi
        labels = ['K1', 'C1', 'W1', 'K2', 'W2', 'C2', 'K3', 'O']
        colors = {
            'makanan_berat': 'red',
            'makanan_ringan': 'orange',
            'non_kuliner': 'blue',
            'oleh_oleh': 'purple',
            'all': 'gray'
        }
        
        # Titik sebelumnya untuk routing
        previous_point = start_point
        
        for i, dest in enumerate(destinations):
            dest_location = (dest.latitude, dest.longitude)
            
            # Dapatkan rute jalan nyata dari titik sebelumnya ke destinasi ini
            if self.use_real_routes:
                print(f"  Mengambil rute untuk segmen {i+1}/{len(destinations)}...")
            
            segment_coords = self.get_route_coordinates(previous_point, dest_location)
            
            # Gambar polyline untuk segmen ini
            folium.PolyLine(
                segment_coords,
                color='darkblue',
                weight=3,
                opacity=0.7,
                popup=f"<b>Segmen {i+1}</b><br>Ke: {dest.nama}",
                tooltip=f"Segmen {i+1}"
            ).add_to(m)
            
            # Tambahkan semua koordinat segmen ke list (kecuali titik awal yang sudah ada)
            all_route_coords.extend(segment_coords[1:])
            
            # Update titik sebelumnya
            previous_point = dest_location
            
            # Tentukan warna marker berdasarkan kategori utama
            kategori_utama = dest.kategori[0] if dest.kategori else 'all'
            marker_color = colors.get(kategori_utama, 'gray')
            
            # Buat popup info
            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="margin: 0; color: #2c3e50;">[{labels[i]}] {dest.nama}</h4>
                <hr style="margin: 5px 0;">
                <b>Kategori:</b> {', '.join(dest.kategori)}<br>
                <b>Koordinat:</b> ({dest.latitude:.6f}, {dest.longitude:.6f})<br>
                <b>Urutan:</b> Destinasi ke-{i+1}
            </div>
            """
            
            # Tambahkan marker dengan number label
            folium.Marker(
                dest_location,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{i+1}. {labels[i]} - {dest.nama}",
                icon=folium.Icon(
                    color=marker_color,
                    icon='info-sign',
                    prefix='glyphicon'
                )
            ).add_to(m)
            
            # Tambahkan circle marker dengan number
            folium.CircleMarker(
                dest_location,
                radius=15,
                popup=f"{i+1}",
                color=marker_color,
                fill=True,
                fillColor=marker_color,
                fillOpacity=0.3,
                weight=2
            ).add_to(m)
            
            # Tambahkan text number di atas marker
            folium.DivIcon(
                html=f'<div style="font-size: 12pt; color: white; font-weight: bold; text-align: center; background-color: {marker_color}; border-radius: 50%; width: 25px; height: 25px; line-height: 25px;">{i+1}</div>',
                icon_size=(25, 25),
                icon_anchor=(12, 12)
            )
        
        # Fit bounds untuk menampilkan semua marker dan rute
        m.fit_bounds(all_route_coords)
        
        self.map = m
        return m
    
    def add_legend(self, map_obj: folium.Map) -> folium.Map:
        """
        Menambahkan legend ke peta
        
        Args:
            map_obj: folium Map object
            
        Returns:
            Map dengan legend
        """
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; 
                    right: 50px; 
                    width: 250px; 
                    height: auto; 
                    background-color: white; 
                    border: 2px solid grey; 
                    z-index: 9999; 
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0;">Legenda</h4>
            <div style="margin: 5px 0;">
                <i class="fa fa-map-marker" style="color: red;"></i> 
                <b>K</b> - Makanan Berat
            </div>
            <div style="margin: 5px 0;">
                <i class="fa fa-map-marker" style="color: orange;"></i> 
                <b>C</b> - Makanan Ringan
            </div>
            <div style="margin: 5px 0;">
                <i class="fa fa-map-marker" style="color: blue;"></i> 
                <b>W</b> - Wisata Non-Kuliner
            </div>
            <div style="margin: 5px 0;">
                <i class="fa fa-map-marker" style="color: purple;"></i> 
                <b>O</b> - Oleh-Oleh
            </div>
            <div style="margin: 5px 0;">
                <i class="fa fa-play" style="color: green;"></i> 
                Titik Awal
            </div>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(legend_html))
        return map_obj
    
    def save_map(self, filename: str = "route_map.html"):
        """
        Menyimpan peta ke file HTML
        
        Args:
            filename: Nama file output
        """
        if self.map is None:
            raise ValueError("Map belum dibuat. Panggil create_route_map() terlebih dahulu.")
        
        # Tambahkan legend
        self.map = self.add_legend(self.map)
        
        # Simpan ke file
        self.map.save(filename)
        print(f"Peta berhasil disimpan ke: {filename}")
    
    def create_multiple_routes_map(self,
                                   start_point: Tuple[float, float],
                                   routes_data: List[dict]) -> folium.Map:
        """
        Membuat peta dengan beberapa rute sekaligus
        
        Args:
            start_point: Koordinat titik awal
            routes_data: List of dict dengan format:
                         [{'destinations': [...], 'name': 'Rute 1', 'color': 'blue'}, ...]
            
        Returns:
            folium.Map object
        """
        # Buat peta
        m = folium.Map(
            location=start_point,
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Marker untuk titik start
        folium.Marker(
            start_point,
            popup="<b>Titik Awal</b><br>User Location",
            tooltip="START",
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)
        
        # Warna untuk setiap rute
        route_colors = ['blue', 'red', 'purple', 'orange', 'green']
        
        all_coords = [start_point]
        
        for idx, route_data in enumerate(routes_data):
            destinations = route_data['destinations']
            route_name = route_data.get('name', f'Rute {idx+1}')
            route_color = route_data.get('color', route_colors[idx % len(route_colors)])
            
            # Create feature group untuk route ini
            feature_group = folium.FeatureGroup(name=route_name)
            
            # Titik sebelumnya untuk routing
            previous_point = start_point
            
            for i, dest in enumerate(destinations):
                dest_location = (dest.latitude, dest.longitude)
                
                # Dapatkan rute jalan nyata untuk segmen ini
                if self.use_real_routes:
                    print(f"  Rute {idx+1} - Segmen {i+1}/{len(destinations)}...")
                
                segment_coords = self.get_route_coordinates(previous_point, dest_location)
                all_coords.extend(segment_coords)
                
                # Polyline untuk segmen ini
                folium.PolyLine(
                    segment_coords,
                    color=route_color,
                    weight=3,
                    opacity=0.7,
                    popup=f"{route_name} - Segmen {i+1}"
                ).add_to(feature_group)
                
                # Marker untuk destinasi
                folium.CircleMarker(
                    dest_location,
                    radius=8,
                    popup=f"<b>{route_name}</b><br>{dest.nama}",
                    color=route_color,
                    fill=True,
                    fillColor=route_color,
                    fillOpacity=0.6
                ).add_to(feature_group)
                
                # Update titik sebelumnya
                previous_point = dest_location
            
            feature_group.add_to(m)
        
        # Tambahkan layer control
        folium.LayerControl().add_to(m)
        
        # Fit bounds
        m.fit_bounds(all_coords)
        
        self.map = m
        return m
