import sys
sys.path.insert(0, '.')

print("Testing database loading...")
print("=" * 50)

# Test 1: Load from data_loader
print("\n1. Testing load_destinations_from_sqlite():")
try:
    from utils.data_loader import load_destinations_from_sqlite
    dests = load_destinations_from_sqlite()
    print(f"   ✓ Loaded {len(dests)} destinations")
    if dests:
        print(f"   ✓ First destination: {dests[0].nama}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Initialize system like endpoints.py does
print("\n2. Testing initialize_system() from endpoints:")
try:
    from api.endpoints import initialize_system, destinations
    print(f"   Current destinations: {destinations}")
    initialize_system()
    from api.endpoints import destinations as dest_after
    print(f"   ✓ After init: {len(dest_after) if dest_after else 0} destinations")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
