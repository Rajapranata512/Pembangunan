"""
opendata_fetcher.py — Integrasi dengan portal Open Data Indonesia.

Sumber data:
1. Satu Data Indonesia (data.go.id) — CKAN API, tanpa API key
2. Open Data Jabar (data.jabarprov.go.id) — tanpa API key
"""
import requests
import logging
import csv
import io

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 1. Satu Data Indonesia (CKAN)
# ──────────────────────────────────────────────
CKAN_BASE = "https://data.go.id/api/3/action"


def search_datasets(query: str, limit: int = 10) -> list:
    """
    Cari dataset di portal data.go.id berdasarkan kata kunci.
    Returns: list of dataset dicts with 'name', 'title', 'resources'
    """
    try:
        resp = requests.get(
            f"{CKAN_BASE}/package_search",
            params={"q": query, "rows": limit},
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("success"):
            return data["result"]["results"]
        return []
    except Exception as e:
        logger.warning(f"data.go.id search failed for '{query}': {e}")
        return []


def get_dataset_data(resource_id: str, limit: int = 500) -> list:
    """
    Ambil data dari datastore CKAN berdasarkan resource_id.
    Returns: list of record dicts
    """
    try:
        resp = requests.get(
            f"{CKAN_BASE}/datastore_search",
            params={"resource_id": resource_id, "limit": limit},
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("success"):
            return data["result"]["records"]
        return []
    except Exception as e:
        logger.warning(f"data.go.id datastore fetch failed for '{resource_id}': {e}")
        return []


def download_csv_resource(url: str) -> list:
    """
    Download dan parse file CSV dari URL resource data.go.id.
    Returns: list of dicts (rows)
    """
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        content = resp.content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)
    except Exception as e:
        logger.warning(f"CSV download failed from {url}: {e}")
        return []


# ──────────────────────────────────────────────
# 2. Open Data Jabar
# ──────────────────────────────────────────────
JABAR_BASE = "https://data.jabarprov.go.id/api-backend"


def search_jabar_datasets(query: str) -> list:
    """
    Cari dataset di portal Open Data Jawa Barat.
    """
    try:
        resp = requests.get(
            f"{JABAR_BASE}/dataset",
            params={"search": query},
            timeout=15
        )
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception as e:
        logger.warning(f"Open Data Jabar search failed for '{query}': {e}")
        return []


# ──────────────────────────────────────────────
# 3. High-level: Cari data ekonomi per kabupaten
# ──────────────────────────────────────────────
def find_economic_datasets() -> dict:
    """
    Mencari dataset ekonomi utama yang tersedia di data.go.id.
    Returns: dict of available dataset info per indicator
    """
    indicators = {
        "penduduk": "jumlah penduduk kabupaten kota",
        "pdrb": "PDRB kabupaten kota",
        "pengangguran": "tingkat pengangguran terbuka",
        "kemiskinan": "persentase penduduk miskin kabupaten",
        "umk": "upah minimum kabupaten",
    }

    found = {}
    for key, query in indicators.items():
        results = search_datasets(query, limit=3)
        if results:
            found[key] = {
                "dataset_count": len(results),
                "datasets": [
                    {
                        "title": ds.get("title", ""),
                        "name": ds.get("name", ""),
                        "organization": ds.get("organization", {}).get("title", ""),
                        "resources": [
                            {
                                "id": r.get("id"),
                                "format": r.get("format"),
                                "url": r.get("url"),
                                "name": r.get("name"),
                            }
                            for r in ds.get("resources", [])[:3]
                        ]
                    }
                    for ds in results
                ]
            }
        else:
            found[key] = {"dataset_count": 0, "datasets": []}

    return found
