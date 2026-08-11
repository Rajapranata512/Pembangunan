"""Test script untuk verifikasi semua endpoint API."""
import urllib.request
import json

BASE = "http://127.0.0.1:8888"

def get(path):
    r = urllib.request.urlopen(BASE + path)
    return json.loads(r.read().decode())

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req)
    return json.loads(r.read().decode())

print("=" * 60)
print("TEST 1: GET /api/v1/regions")
d = get("/api/v1/regions?limit=3")
print(f"  Total wilayah: {d['total']}")
for item in d['data'][:3]:
    name = item['name']
    score = item['final_score']
    print(f"  - {name:25s} | Final Score: {score}")

print("\nTEST 2: GET /api/v1/regions/1 (detail Surabaya)")
d = get("/api/v1/regions/1")
print(f"  Nama: {d['name']}")
print(f"  Provinsi: {d['province']}")
print(f"  Populasi: {d['demographics'][0]['population'] if d['demographics'] else 'N/A'}")
print(f"  PDRB: {d['economy'][0]['pdrb_billion_idr'] if d['economy'] else 'N/A'} miliar")
print(f"  Infra Score: {d['infrastructure']['infrastructure_composite_score'] if d['infrastructure'] else 'N/A'}")

print("\nTEST 3: GET /api/v1/regions/1/scores")
d = get("/api/v1/regions/1/scores")
print(f"  Business: {d['business_score']}")
print(f"  Property: {d['property_score']}")
print(f"  Growth:   {d['growth_score']}")
print(f"  Risk:     {d['risk_score']}")
print(f"  Final:    {d['final_score']}")

print("\nTEST 4: GET /api/v1/regions/1/insight")
d = get("/api/v1/regions/1/insight")
print(f"  Insight: {d['insight_text'][:100]}...")

print("\nTEST 5: GET /api/v1/compare?ids=1,5,6")
d = get("/api/v1/compare?ids=1,5,6")
for item in d:
    name = item['name']
    score = item['scores'][0]['final_score'] if item['scores'] else 'N/A'
    print(f"  - {name:25s} | Final: {score}")

print("\nTEST 6: POST /api/v1/recommendations (Investasi tanah)")
d = post("/api/v1/recommendations", {"goal": "membeli_tanah_investasi"})
print(f"  Goal: {d['goal']}")
for item in d['results']:
    name = item['region']['name']
    rel = item['relevance_score']
    print(f"  #{item['rank']} {name:25s} | Relevance: {rel}")

print("\nTEST 7: GET /api/v1/map-data")
d = get("/api/v1/map-data")
print(f"  Data points: {len(d)}")
for item in d[:3]:
    name = item['name']
    lat = item['latitude']
    lng = item['longitude']
    score = item['final_score']
    print(f"  - {name:25s} | ({lat}, {lng}) | Final: {score}")

print("\n" + "=" * 60)
print("SEMUA TEST BERHASIL!")
print("=" * 60)
