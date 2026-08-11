"""
osm_fetcher.py — OpenStreetMap Overpass API Integration.
Mengambil data fasilitas REAL (rumah sakit, sekolah, universitas, restoran, bank, ATM, hotel, mall)
untuk setiap wilayah berdasarkan koordinat lat/lng.

Sumber: https://overpass-api.de/api/interpreter (100% gratis, tanpa API key)
"""
import time
import requests
import logging

logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_MIRROR = "https://overpass.kumi.systems/api/interpreter"

# Mapping dari tipe amenity OSM ke kolom database kita
AMENITY_MAP = {
    "hospital":    "hospital_count",
    "school":      "school_count",
    "university":  "university_count",
    "clinic":      "clinic_count",
    "marketplace": "traditional_market_count",
    "hotel":       "hotel_count",
    "mall":        "mall_count",         # Kita query sebagai shop=mall
    "restaurant":  "restaurant_count",   # Extra data
    "bank":        "bank_count",         # Extra data
    "atm":         "atm_count",          # Extra data
}

# Radius pencarian dalam meter — disesuaikan per tipe wilayah
RADIUS_KOTA = 8000      # 8 km untuk kota (lebih padat)
RADIUS_KABUPATEN = 15000  # 15 km untuk kabupaten (lebih luas)


def _build_query(lat: float, lng: float, radius: int, amenity_type: str) -> str:
    """
    Bangun query Overpass QL untuk menghitung jumlah amenity
    di dalam radius tertentu dari titik koordinat.
    """
    if amenity_type == "mall":
        # Mall tidak ada di tag 'amenity', tapi di 'shop=mall'
        return f"""
[out:json][timeout:25];
(
  nwr["shop"="mall"](around:{radius},{lat},{lng});
);
out count;
"""
    else:
        return f"""
[out:json][timeout:25];
(
  nwr["amenity"="{amenity_type}"](around:{radius},{lat},{lng});
);
out count;
"""


def _build_batch_query(lat: float, lng: float, radius: int) -> str:
    """
    Bangun satu query Overpass yang mengambil SEMUA amenity sekaligus.
    Lebih efisien daripada query per-tipe.
    """
    amenity_types = "hospital|school|university|clinic|marketplace|hotel|restaurant|bank|atm"
    return f"""
[out:json][timeout:60];
(
  nwr["amenity"~"{amenity_types}"](around:{radius},{lat},{lng});
  nwr["shop"="mall"](around:{radius},{lat},{lng});
  nwr["tourism"~"hotel|guest_house"](around:{radius},{lat},{lng});
  nwr["tourism"~"attraction|museum|theme_park|zoo"](around:{radius},{lat},{lng});
);
out tags;
"""


def fetch_amenity_count(lat: float, lng: float, amenity_type: str, radius: int = 10000) -> int:
    """Ambil jumlah satu tipe amenity dari Overpass API."""
    query = _build_query(lat, lng, radius, amenity_type)
    headers = {"User-Agent": "ProspekJawa/1.0 (Contact: admin@prospekjawa.com)"}
    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        elements = data.get("elements", [])
        if elements and elements[0].get("type") == "count":
            return int(elements[0]["tags"].get("total", 0))
        return len(elements)
    except Exception as e:
        logger.warning(f"Overpass query failed for {amenity_type} at ({lat},{lng}): {e}")
        return -1  # -1 = gagal, jangan overwrite data lama


def fetch_all_amenities(lat: float, lng: float, region_type: str = "kota") -> dict:
    """
    Ambil SEMUA data fasilitas untuk satu wilayah sekaligus.
    Mengembalikan dict dengan jumlah per kategori.
    
    Returns:
        {
            "hospital_count": 12,
            "school_count": 145,
            "university_count": 8,
            "clinic_count": 34,
            "traditional_market_count": 5,
            "hotel_count": 22,
            "mall_count": 3,
            "restaurant_count": 89,
            "bank_count": 45,
            "atm_count": 67,
            "tourism_spot_count": 6,
            "source": "OpenStreetMap Overpass API",
            "fetched_at": "2026-06-09T16:00:00"
        }
    """
    radius = RADIUS_KOTA if region_type == "kota" else RADIUS_KABUPATEN
    query = _build_batch_query(lat, lng, radius)
    headers = {"User-Agent": "ProspekJawa/1.0 (Contact: admin@prospekjawa.com)"}

    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, headers=headers, timeout=60)
        if resp.status_code == 429 or resp.status_code == 406:
            # Rate limited or not acceptable, coba mirror
            logger.info("Overpass rate limited/406, trying mirror...")
            time.sleep(2)
            resp = requests.post(OVERPASS_MIRROR, data={"data": query}, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"Overpass batch query failed at ({lat},{lng}): {e}")
        return None

    # Parse elements dan hitung per kategori
    counts = {
        "hospital_count": 0,
        "school_count": 0,
        "university_count": 0,
        "clinic_count": 0,
        "traditional_market_count": 0,
        "hotel_count": 0,
        "mall_count": 0,
        "restaurant_count": 0,
        "bank_count": 0,
        "atm_count": 0,
        "tourism_spot_count": 0,
    }

    for el in data.get("elements", []):
        tags = el.get("tags", {})
        amenity = tags.get("amenity", "")
        shop = tags.get("shop", "")
        tourism = tags.get("tourism", "")

        if amenity == "hospital":
            counts["hospital_count"] += 1
        elif amenity == "school":
            counts["school_count"] += 1
        elif amenity == "university":
            counts["university_count"] += 1
        elif amenity == "clinic" or amenity == "doctors":
            counts["clinic_count"] += 1
        elif amenity == "marketplace":
            counts["traditional_market_count"] += 1
        elif amenity == "restaurant" or amenity == "fast_food" or amenity == "cafe":
            counts["restaurant_count"] += 1
        elif amenity == "bank":
            counts["bank_count"] += 1
        elif amenity == "atm":
            counts["atm_count"] += 1

        if shop == "mall" or shop == "department_store":
            counts["mall_count"] += 1

        if tourism in ("hotel", "guest_house"):
            counts["hotel_count"] += 1
        elif tourism in ("attraction", "museum", "theme_park", "zoo", "viewpoint"):
            counts["tourism_spot_count"] += 1

    counts["source"] = "OpenStreetMap Overpass API"

    return counts


def calculate_facility_score(counts: dict) -> int:
    """
    Hitung skor fasilitas komposit (0-100) berdasarkan data nyata OSM.
    Formula berbobot yang memperhitungkan kelengkapan layanan.
    """
    if not counts:
        return 0

    # Bobot per kategori (total = 100)
    weights = {
        "hospital_count": 15,        # Kesehatan penting
        "school_count": 12,          # Pendidikan dasar
        "university_count": 10,      # Pendidikan tinggi
        "clinic_count": 8,           # Layanan kesehatan dasar
        "traditional_market_count": 8,  # Ekonomi lokal
        "mall_count": 10,            # Pusat perbelanjaan modern
        "hotel_count": 10,           # Akomodasi & pariwisata
        "restaurant_count": 7,       # Ekosistem kuliner
        "bank_count": 10,            # Akses finansial
        "tourism_spot_count": 5,     # Destinasi wisata
        "atm_count": 5,             # Akses ATM
    }

    # Threshold "ideal" per kategori (angka ini = skor penuh untuk kategori tsb)
    thresholds = {
        "hospital_count": 15,
        "school_count": 100,
        "university_count": 10,
        "clinic_count": 30,
        "traditional_market_count": 10,
        "mall_count": 5,
        "hotel_count": 20,
        "restaurant_count": 80,
        "bank_count": 30,
        "tourism_spot_count": 8,
        "atm_count": 40,
    }

    score = 0
    for key, weight in weights.items():
        actual = counts.get(key, 0)
        threshold = thresholds.get(key, 10)
        # Normalized: min(actual/threshold, 1.0) * weight
        normalized = min(actual / threshold, 1.0) if threshold > 0 else 0
        score += normalized * weight

    return min(100, max(0, int(score)))
