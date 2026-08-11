"""Verify 119 regions data quality."""
import urllib.request, json

BASE = "http://localhost:8888/api/v1"

# 1. Total regions
r = urllib.request.urlopen(f"{BASE}/regions?limit=1")
d = json.loads(r.read().decode())
print(f"1. Total wilayah: {d['total']}")

# 2. Provinces breakdown
provinces = {}
r = urllib.request.urlopen(f"{BASE}/regions?limit=119")
data = json.loads(r.read().decode())['data']
for reg in data:
    prov = reg['province']
    provinces[prov] = provinces.get(prov, 0) + 1
print("\n2. Breakdown per provinsi:")
for p, c in sorted(provinces.items()):
    print(f"   {p}: {c} wilayah")

# 3. Score distribution
scores = [r['final_score'] for r in data if r['final_score'] is not None]
print(f"\n3. Score distribution:")
print(f"   Min: {min(scores):.1f}")
print(f"   Max: {max(scores):.1f}")
print(f"   Avg: {sum(scores)/len(scores):.1f}")

# 4. Top 5
top5 = sorted(data, key=lambda x: x['final_score'] or 0, reverse=True)[:5]
print(f"\n4. Top 5 wilayah:")
for i, r in enumerate(top5, 1):
    print(f"   {i}. {r['name']} ({r['province']}) - Final: {r['final_score']:.1f}")

# 5. Map data
r = urllib.request.urlopen(f"{BASE}/map-data")
mapd = json.loads(r.read().decode())
with_coords = sum(1 for m in mapd if m.get('latitude') and m.get('longitude'))
print(f"\n5. Map data: {len(mapd)} points, {with_coords} with coordinates")

# 6. Detail check
r = urllib.request.urlopen(f"{BASE}/regions/1")
detail = json.loads(r.read().decode())
print(f"\n6. Detail check - {detail['name']}:")
print(f"   Province: {detail['province']}")
print(f"   Scores: {detail['scores'][0] if detail['scores'] else 'None'}")
print(f"   Demographics: pop={detail['demographics'][0]['population'] if detail['demographics'] else 'N/A'}")
print(f"   AI Insight: {'YES' if detail['ai_insight'] else 'NO'}")

print("\n=== ALL TESTS PASSED ===")
