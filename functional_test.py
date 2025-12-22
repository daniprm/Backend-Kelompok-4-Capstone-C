"""
Functional Test untuk Validasi Constraint Sistem Rekomendasi Rute Wisata
Melakukan validasi terhadap 3 aturan utama:
1. Rute berisi 8 destinasi wisata
2. Tidak ada duplikat destinasi dalam satu rute
3. Urutan kategori sesuai: K1, C1, W1, K2, W2, C2, K3, O
"""

import requests
import json
import sys
from typing import Dict, List
from collections import Counter

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Konfigurasi
API_URL = "http://localhost:8000/generate-routes"
NUM_TESTS = 3  # Jumlah test yang akan dilakukan (ubah ke 100 atau 1000 untuk full test)
NUM_ROUTES_PER_TEST = 3  # Jumlah rute per request

# Lokasi test (bisa diganti sesuai kebutuhan)
TEST_LOCATION = {
    "latitude": -7.2575,
    "longitude": 112.7521
}

# Expected order berdasarkan constraint: K1, C1, W1, K2, W2, C2, K3, O
EXPECTED_ORDER = ["K", "C", "W", "K", "W", "C", "K", "O"]

class ValidationResult:
    def __init__(self):
        self.total_tests = 0
        self.total_routes = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.constraint_violations = {
            "wrong_length": 0,
            "duplicate_destinations": 0,
            "wrong_order": 0
        }
        self.failed_details = []
    
    def add_violation(self, test_num: int, route_num: int, violation_type: str, details: str):
        """Catat pelanggaran constraint"""
        self.constraint_violations[violation_type] += 1
        self.failed_details.append({
            "test": test_num,
            "route": route_num,
            "violation": violation_type,
            "details": details
        })
    
    def print_summary(self):
        """Cetak ringkasan hasil validasi"""
        print("\n" + "="*80)
        print("FUNCTIONAL TEST SUMMARY")
        print("="*80)
        print(f"Total Tests Run: {self.total_tests}")
        print(f"Total Routes Validated: {self.total_routes}")
        print(f"Passed Tests: {self.passed_tests} ({self.passed_tests/self.total_tests*100:.2f}%)")
        print(f"Failed Tests: {self.failed_tests} ({self.failed_tests/self.total_tests*100:.2f}%)")
        
        print("\n" + "-"*80)
        print("CONSTRAINT VIOLATIONS:")
        print("-"*80)
        print(f"1. Wrong Route Length (harus 8): {self.constraint_violations['wrong_length']}")
        print(f"2. Duplicate Destinations: {self.constraint_violations['duplicate_destinations']}")
        print(f"3. Wrong Category Order: {self.constraint_violations['wrong_order']}")
        
        if self.failed_details:
            print("\n" + "-"*80)
            print("FAILED TEST DETAILS:")
            print("-"*80)
            for detail in self.failed_details[:10]:  # Tampilkan 10 pertama
                print(f"Test #{detail['test']}, Route #{detail['route']}")
                print(f"  Violation: {detail['violation']}")
                print(f"  Details: {detail['details']}")
                print()
        
        print("="*80)
        if self.failed_tests == 0:
            print("✅ ALL TESTS PASSED! System meets all functional requirements.")
        else:
            print("❌ SOME TESTS FAILED! System has constraint violations.")
        print("="*80)

def validate_route_length(destinations: List[Dict]) -> bool:
    """Validasi: Rute harus berisi 8 destinasi"""
    return len(destinations) == 8

def validate_no_duplicates(destinations: List[Dict]) -> tuple:
    """Validasi: Tidak ada destinasi duplikat"""
    # Gunakan place_id jika ada, jika tidak gunakan nama_destinasi
    if destinations and 'place_id' in destinations[0] and destinations[0]['place_id'] is not None:
        ids = [dest['place_id'] for dest in destinations]
        duplicates = [pid for pid, count in Counter(ids).items() if count > 1]
        if duplicates:
            return False, f"Duplicate place_ids found: {duplicates}"
    else:
        # Fallback ke nama destinasi
        names = [dest.get('nama_destinasi', dest.get('nama', '')) for dest in destinations]
        duplicates = [name for name, count in Counter(names).items() if count > 1]
        if duplicates:
            return False, f"Duplicate destinations found: {duplicates}"
    
    return True, ""

def validate_category_order(destinations: List[Dict]) -> tuple:
    """
    Validasi: Urutan kategori harus sesuai K1, C1, W1, K2, W2, C2, K3, O
    
    Mapping kategori:
    - K: Kuliner (makanan_berat)
    - C: Cemilan (makanan_ringan)
    - W: Wisata (non_kuliner)
    - O: Oleh-oleh (oleh_oleh)
    """
    # Expected category order dari sistem
    EXPECTED_CATEGORY_ORDER = [
        'makanan_berat',   # K1
        'makanan_ringan',  # C1
        'non_kuliner',     # W1
        'makanan_berat',   # K2
        'non_kuliner',     # W2
        'makanan_ringan',  # C2
        'makanan_berat',   # K3
        'oleh_oleh'        # O
    ]
    
    actual_categories = []
    
    for dest in destinations:
        categories = dest['kategori']
        
        # Tentukan kategori utama (prioritas: oleh_oleh > makanan > non_kuliner)
        if 'oleh_oleh' in categories:
            actual_categories.append('oleh_oleh')
        elif 'makanan_berat' in categories:
            actual_categories.append('makanan_berat')
        elif 'makanan_ringan' in categories:
            actual_categories.append('makanan_ringan')
        elif 'non_kuliner' in categories:
            actual_categories.append('non_kuliner')
        else:
            # Fallback jika tidak ada kategori yang cocok
            actual_categories.append('unknown')
    
    # Bandingkan dengan expected order
    if actual_categories != EXPECTED_CATEGORY_ORDER:
        # Buat representasi yang lebih mudah dibaca
        expected_simple = []
        actual_simple = []
        
        for cat in EXPECTED_CATEGORY_ORDER:
            if cat == 'makanan_berat':
                expected_simple.append('K')
            elif cat == 'makanan_ringan':
                expected_simple.append('C')
            elif cat == 'non_kuliner':
                expected_simple.append('W')
            elif cat == 'oleh_oleh':
                expected_simple.append('O')
        
        for cat in actual_categories:
            if cat == 'makanan_berat':
                actual_simple.append('K')
            elif cat == 'makanan_ringan':
                actual_simple.append('C')
            elif cat == 'non_kuliner':
                actual_simple.append('W')
            elif cat == 'oleh_oleh':
                actual_simple.append('O')
            else:
                actual_simple.append('?')
        
        return False, f"Expected: {expected_simple}, Got: {actual_simple}"
    
    return True, ""

def run_single_test(test_num: int, result: ValidationResult):
    """Jalankan satu test"""
    try:
        # Request ke API
        response = requests.post(
            API_URL,
            json={
                "latitude": TEST_LOCATION["latitude"],
                "longitude": TEST_LOCATION["longitude"],
                "num_routes": NUM_ROUTES_PER_TEST
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Test #{test_num}: API error (status {response.status_code})")
            result.failed_tests += 1
            return
        
        data = response.json()
        routes = data['data']['routes']
        
        test_passed = True
        
        # Validasi setiap rute
        for route_idx, route in enumerate(routes, 1):
            destinations = route['destinations']
            route_num = route_idx
            
            result.total_routes += 1
            
            # Debug: Tampilkan sample destinasi untuk test pertama
            if test_num == 1 and route_idx == 1:
                print("\n[DEBUG] Sample destination structure:")
                if destinations:
                    print(f"Keys: {list(destinations[0].keys())}")
                    print(f"Sample: {destinations[0]}")
                print()
            
            # Constraint 1: Jumlah destinasi harus 8
            if not validate_route_length(destinations):
                result.add_violation(
                    test_num, route_num, "wrong_length",
                    f"Route has {len(destinations)} destinations (expected 8)"
                )
                test_passed = False
            
            # Constraint 2: Tidak ada duplikat
            is_valid, error_msg = validate_no_duplicates(destinations)
            if not is_valid:
                result.add_violation(
                    test_num, route_num, "duplicate_destinations",
                    error_msg
                )
                test_passed = False
            
            # Constraint 3: Urutan kategori benar
            is_valid, error_msg = validate_category_order(destinations)
            if not is_valid:
                result.add_violation(
                    test_num, route_num, "wrong_order",
                    error_msg
                )
                test_passed = False
        
        if test_passed:
            result.passed_tests += 1
            print(f"✅ Test #{test_num}: PASSED")
        else:
            result.failed_tests += 1
            print(f"❌ Test #{test_num}: FAILED")
        
        result.total_tests += 1
        
    except Exception as e:
        print(f"❌ Test #{test_num}: Exception - {str(e)}")
        result.failed_tests += 1
        result.total_tests += 1

def main():
    """Main function untuk menjalankan functional test"""
    print("="*80)
    print("FUNCTIONAL TEST - Validasi Constraint Sistem Rekomendasi Rute Wisata")
    print("="*80)
    print(f"Test Configuration:")
    print(f"  - Number of Tests: {NUM_TESTS}")
    print(f"  - Routes per Test: {NUM_ROUTES_PER_TEST}")
    print(f"  - Total Routes to Validate: {NUM_TESTS * NUM_ROUTES_PER_TEST}")
    print(f"  - Test Location: {TEST_LOCATION}")
    print("\nConstraints to Validate:")
    print("  1. Rute harus berisi 8 destinasi wisata")
    print("  2. Tidak ada destinasi duplikat dalam satu rute")
    print("  3. Urutan kategori: K, C, W, K, W, C, K, O")
    print("="*80)
    print("\nStarting tests...\n")
    
    result = ValidationResult()
    
    # Jalankan test
    for i in range(1, NUM_TESTS + 1):
        run_single_test(i, result)
    
    # Tampilkan hasil
    result.print_summary()

if __name__ == "__main__":
    main()
