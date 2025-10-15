# Changelog - Sistem Rekomendasi Rute Wisata

## [1.1.0] - 2025-10-14

### ✨ Added - Real Road Routing

- **OSRM Integration**: Integrasi dengan OpenStreetMap Routing Machine API
- **Real Routes**: Peta sekarang menampilkan rute jalan nyata, bukan garis lurus
- **Automatic Fallback**: Sistem otomatis fallback ke garis lurus jika API gagal
- **Rate Limiting**: Built-in delay untuk menghindari rate limiting (100ms per request)

### 📦 New Dependencies

- `requests>=2.25.0`: HTTP library untuk routing API calls

### 📝 New Files

- `visualization/ROUTING_API_INFO.md`: Dokumentasi lengkap routing API
- `CHANGELOG.md`: File ini

### 🔧 Modified Files

- `visualization/map_plotter.py`:
  - Added `use_real_routes` parameter (default: True)
  - Added `get_route_coordinates()` method untuk OSRM API calls
  - Modified `create_route_map()` untuk drawing segmen-segmen rute
  - Modified `create_multiple_routes_map()` untuk support real routes
- `example.py`:
  - Updated map plotter initialization dengan `use_real_routes=True`
  - Added routing progress messages
- `Main.py`:
  - Updated map plotter initialization dengan `use_real_routes=True`
- `requirements.txt`:
  - Added `requests>=2.25.0`
- `README.md`:
  - Updated fitur list dengan visualisasi dan routing
  - Updated struktur project dengan folder visualization
  - Added visualisasi section dengan detail lengkap

### 🎯 Features

- **Transport Mode**: Default menggunakan mode "driving" (mobil)
- **Geometry Format**: GeoJSON dengan full overview
- **Coordinate Conversion**: Otomatis convert `[lon,lat]` → `(lat,lon)`
- **Error Handling**: Robust error handling dengan fallback

### 📊 Performance

- Request time: ~100-300ms per segmen
- Total untuk 1 rute (8 segmen): ~2-3 detik
- Total untuk 3 rute (24 segmen): ~6-9 detik

---

## [1.0.0] - 2025-10-14

### ✨ Initial Release - Visualization Features

#### Added

- **Interactive Maps**: Folium-based HTML maps
  - `best_route_map.html`: Single best route visualization
  - `all_routes_map.html`: Multiple routes with layer control
- **Convergence Graphs**: 4 statistical graphs using Matplotlib

  - Fitness evolution
  - Distance evolution
  - Convergence analysis
  - Statistics summary

- **Visualization Package**:
  - `visualization/map_plotter.py`: Map generation
  - `visualization/convergence_plotter.py`: Graph generation
  - `visualization/README_VISUALIZATION.md`: Complete documentation
  - `visualization/outputs/`: Output directory

#### Dependencies

- `folium>=0.12.0`: Interactive map visualization
- `matplotlib>=3.3.0`: Statistical graph plotting

#### Map Features

- Color-coded markers by category
- Popup info for each destination
- Legend with category explanations
- Responsive zoom and pan
- Layer control for multiple routes

#### Graph Features

- Best/Average fitness tracking
- Best/Average distance tracking
- Convergence threshold visualization
- Final statistics comparison

---

## [0.9.0] - 2025-10-13

### 🐛 Bug Fixes

#### Fixed

- **IndexError in crossover**: Object comparison issue
  - Changed from `gene not in list` to `id(gene) not in id_set`
  - Added fallback mechanism when filtered list exhausted
- **TypeError in Route**: Signature mismatch

  - Updated all `Route(start, genes, end)` to `Route(start, genes)`
  - Removed end_point parameter per user modification

- **UnicodeEncodeError**: Windows terminal encoding
  - Replaced all Unicode symbols (✓, ✗, 📄, 🗺️, etc.) with ASCII alternatives
  - Changed to `[OK]`, `Ya/Tidak`, `[JSON]`, `[MAP]` format

#### Modified Files

- `algorithms/operators.py`: Fixed crossover operators
- `algorithms/chromosome.py`: Commented end_point
- `models/route.py`: Removed end_point parameter
- `example.py`: Replaced Unicode characters
- `Main.py`: Replaced Unicode characters

---

## [0.1.0] - 2025-10-13

### 🎉 Initial Development

#### Core Features

- **Hybrid Genetic Algorithm**: 9-stage implementation

  1. Genetic representation
  2. Population initialization with constraints
  3. Fitness evaluation
  4. Parent selection (tournament & roulette)
  5. Crossover (order & position-based)
  6. Mutation (swap, inversion, scramble)
  7. 2-Opt local search
  8. Elitism
  9. Convergence detection

- **Constraint Handling**: K→C→W→K→W→C→K→O pattern enforcement
- **Multiple Solutions**: Generate 3 optimal routes
- **Distance Calculation**: Haversine formula for geographic distance

#### Architecture

- **OOP Design**: Modular package structure

  - `models/`: Data models (Destination, Route)
  - `utils/`: Utilities (distance, data_loader)
  - `algorithms/`: HGA implementation (chromosome, population, operators, 2-opt)

- **Data Input**: CSV file with 137 Surabaya destinations
- **Output**: JSON with detailed route information

#### Files Created

- Core algorithm modules (7 files)
- Data models (2 files)
- Utilities (2 files)
- Main applications (Main.py, example.py)
- Configuration (config.py)
- Documentation (README.md, DOCUMENTATION.md, SUMMARY.md)
- Data (data_wisata_sby.csv)

---

## Version Naming Convention

- **Major.Minor.Patch** (Semantic Versioning)
  - **Major**: Breaking changes, major features
  - **Minor**: New features, backward compatible
  - **Patch**: Bug fixes, small improvements

## Future Releases (Planned)

### [1.2.0] - Planned

- [ ] Alternative routing providers (ORS, GraphHopper)
- [ ] Local OSRM server support
- [ ] Distance/duration display on map
- [ ] Transport mode selection (car/bike/foot)

### [2.0.0] - Planned

- [ ] Time constraint optimization
- [ ] User preference weighting
- [ ] Multi-day tour planning
- [ ] Budget optimization
- [ ] Real-time traffic integration

---

**Maintained by**: Tourism Route Recommendation System Team
**Last Updated**: October 14, 2025
