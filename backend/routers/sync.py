"""
routers/sync.py — Endpoint untuk sinkronisasi data dari berbagai sumber.

Endpoints:
  POST /api/v1/sync              — Sinkronisasi tahunan (Simulated Growth Engine)
  POST /api/v1/sync/facilities   — Sync data fasilitas dari OpenStreetMap (REAL data)
  GET  /api/v1/sync/sources      — Cek sumber data yang tersedia
  GET  /api/v1/sync/status       — Status data per tahun di database
"""
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from data_sync import run_annual_sync
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sync", tags=["Sync Data"])


# ──────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────
class SyncRequest(BaseModel):
    year: int


class FacilitySyncRequest(BaseModel):
    region_ids: list[int] | None = None   # None = semua
    batch_size: int = 5                    # berapa region per batch (rate limit)
    delay_seconds: float = 2.0            # delay antar request ke Overpass


# ──────────────────────────────────────────────
# 1. Sync Tahunan (Growth Engine)
# ──────────────────────────────────────────────
@router.post("")
def trigger_annual_sync(req: SyncRequest, db: Session = Depends(get_db)):
    """
    Memicu proses sinkronisasi tahunan secara manual.
    Menggunakan 'Simulated Growth Engine' untuk memproyeksi tren data.
    """
    if req.year < 2024 or req.year > 2030:
        raise HTTPException(status_code=400, detail="Tahun tidak valid. Harus antara 2024 - 2030")

    result = run_annual_sync(db, req.year)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return result


# ──────────────────────────────────────────────
# 2. Sync Fasilitas dari OpenStreetMap (Background)
# ──────────────────────────────────────────────
def _run_facility_sync(region_ids: list[int] | None, delay: float):
    """Background task: sync fasilitas dari OSM untuk setiap region."""
    from models import Region, Facility
    from osm_fetcher import fetch_all_amenities, calculate_facility_score
    from scoring import recalculate_all_scores

    db = SessionLocal()
    try:
        if region_ids:
            regions = db.query(Region).filter(Region.id.in_(region_ids)).all()
        else:
            regions = db.query(Region).all()

        total = len(regions)
        success_count = 0
        fail_count = 0

        for i, r in enumerate(regions):
            if not r.latitude or not r.longitude:
                logger.warning(f"[OSM] Skip {r.name}: no coordinates")
                fail_count += 1
                continue

            logger.info(f"[OSM] [{i+1}/{total}] Fetching {r.name} ({r.latitude}, {r.longitude})...")
            print(f"[OSM] [{i+1}/{total}] Fetching {r.name}...")

            counts = fetch_all_amenities(r.latitude, r.longitude, r.region_type)

            if counts is None:
                logger.warning(f"[OSM] Failed for {r.name}")
                fail_count += 1
                time.sleep(delay)
                continue

            # Update Facility table
            fac = db.query(Facility).filter(Facility.region_id == r.id).first()
            if fac:
                fac.school_count = counts.get("school_count", fac.school_count)
                fac.university_count = counts.get("university_count", fac.university_count)
                fac.hospital_count = counts.get("hospital_count", fac.hospital_count)
                fac.clinic_count = counts.get("clinic_count", fac.clinic_count)
                fac.mall_count = counts.get("mall_count", fac.mall_count)
                fac.traditional_market_count = counts.get("traditional_market_count", fac.traditional_market_count)
                fac.hotel_count = counts.get("hotel_count", fac.hotel_count)
                fac.tourism_spot_count = counts.get("tourism_spot_count", fac.tourism_spot_count)
                # Recalculate composite score from real data
                fac.facilities_composite_score = calculate_facility_score(counts)
            else:
                db.add(Facility(
                    region_id=r.id,
                    school_count=counts.get("school_count", 0),
                    university_count=counts.get("university_count", 0),
                    hospital_count=counts.get("hospital_count", 0),
                    clinic_count=counts.get("clinic_count", 0),
                    mall_count=counts.get("mall_count", 0),
                    traditional_market_count=counts.get("traditional_market_count", 0),
                    hotel_count=counts.get("hotel_count", 0),
                    tourism_spot_count=counts.get("tourism_spot_count", 0),
                    facilities_composite_score=calculate_facility_score(counts),
                ))

            success_count += 1
            db.commit()

            # Rate limiting: delay between requests
            if i < total - 1:
                time.sleep(delay)

        # Setelah semua fasilitas diupdate, re-score semua tahun yang ada
        from models import Score
        years = [row[0] for row in db.query(Score.year).distinct().all()]
        for year in years:
            recalculate_all_scores(db, year)

        print(f"[OSM] Selesai! {success_count} berhasil, {fail_count} gagal dari {total} wilayah.")
        logger.info(f"[OSM] Facility sync complete: {success_count}/{total} success")

    except Exception as e:
        logger.error(f"[OSM] Facility sync error: {e}")
    finally:
        db.close()


@router.post("/facilities")
def trigger_facility_sync(
    req: FacilitySyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Sync data fasilitas REAL dari OpenStreetMap Overpass API.
    Proses berjalan di background karena membutuhkan waktu (~4 menit untuk 119 wilayah).
    Tanpa API key — 100% gratis.
    """
    from models import Region
    total = db.query(Region).count()
    estimated_minutes = round((total * req.delay_seconds) / 60, 1)

    background_tasks.add_task(_run_facility_sync, req.region_ids, req.delay_seconds)

    return {
        "success": True,
        "message": (
            f"Sync fasilitas dari OpenStreetMap dimulai di background. "
            f"Memproses {total if not req.region_ids else len(req.region_ids)} wilayah, "
            f"estimasi waktu ~{estimated_minutes} menit."
        ),
        "source": "OpenStreetMap Overpass API (overpass-api.de)",
    }


# ──────────────────────────────────────────────
# 3. Cek Sumber Data yang Tersedia
# ──────────────────────────────────────────────
@router.get("/sources")
def check_data_sources():
    """
    Cek ketersediaan semua sumber data yang bisa diintegrasikan.
    """
    sources = []

    # 1. OpenStreetMap
    try:
        import requests as req
        r = req.get("https://overpass-api.de/api/status", timeout=5)
        osm_ok = r.status_code == 200
    except Exception:
        osm_ok = False

    sources.append({
        "name": "OpenStreetMap Overpass API",
        "type": "Fasilitas & POI",
        "status": "online" if osm_ok else "offline",
        "api_key_required": False,
        "data_provided": ["Rumah Sakit", "Sekolah", "Universitas", "Klinik", "Mall", "Pasar", "Hotel", "Restoran", "Bank", "ATM", "Wisata"],
        "endpoint": "POST /api/v1/sync/facilities",
    })

    # 2. data.go.id
    try:
        import requests as req
        r = req.get("https://data.go.id/api/3/action/site_read", timeout=5)
        ckan_ok = r.status_code == 200
    except Exception:
        ckan_ok = False

    sources.append({
        "name": "Satu Data Indonesia (data.go.id)",
        "type": "Ekonomi & Demografi",
        "status": "online" if ckan_ok else "offline",
        "api_key_required": False,
        "data_provided": ["Populasi", "PDRB", "Pengangguran", "Kemiskinan", "UMK"],
        "endpoint": "GET /api/v1/sync/opendata/search?q={keyword}",
    })

    # 3. BPS
    import os
    bps_key = os.getenv("BPS_API_KEY", "")
    sources.append({
        "name": "BPS Web API (webapi.bps.go.id)",
        "type": "Statistik Resmi",
        "status": "configured" if bps_key else "not_configured",
        "api_key_required": True,
        "api_key_set": bool(bps_key),
        "data_provided": ["Populasi", "PDRB", "Inflasi", "Kemiskinan", "Pengangguran"],
        "note": "Registrasi gratis di webapi.bps.go.id/developer",
    })

    # 4. Simulated Growth Engine
    sources.append({
        "name": "Simulated Growth Engine (Built-in)",
        "type": "Proyeksi Tren",
        "status": "always_available",
        "api_key_required": False,
        "data_provided": ["Proyeksi Populasi", "Proyeksi PDRB", "Proyeksi Harga Properti"],
        "endpoint": "POST /api/v1/sync",
    })

    return {"sources": sources}


# ──────────────────────────────────────────────
# 4. Status Data per Tahun
# ──────────────────────────────────────────────
@router.get("/status")
def get_sync_status(db: Session = Depends(get_db)):
    """
    Lihat berapa banyak data yang tersedia per tahun di database.
    """
    from models import Demographic, Economy, PropertyMarket, Score

    years_demo = db.query(Demographic.year, db.query(Demographic).filter(Demographic.year == Demographic.year).count()).group_by(Demographic.year).all()

    from sqlalchemy import func
    demo_stats = db.query(Demographic.year, func.count(Demographic.id)).group_by(Demographic.year).all()
    econ_stats = db.query(Economy.year, func.count(Economy.id)).group_by(Economy.year).all()
    prop_stats = db.query(PropertyMarket.year, func.count(PropertyMarket.id)).group_by(PropertyMarket.year).all()
    score_stats = db.query(Score.year, func.count(Score.id)).group_by(Score.year).all()

    all_years = sorted(set(
        [y for y, _ in demo_stats] +
        [y for y, _ in econ_stats] +
        [y for y, _ in prop_stats] +
        [y for y, _ in score_stats]
    ))

    status = []
    for year in all_years:
        status.append({
            "year": year,
            "demographics": next((c for y, c in demo_stats if y == year), 0),
            "economy": next((c for y, c in econ_stats if y == year), 0),
            "property_market": next((c for y, c in prop_stats if y == year), 0),
            "scores": next((c for y, c in score_stats if y == year), 0),
        })

    return {"data_status": status}


# ──────────────────────────────────────────────
# 5. Search Open Data Indonesia
# ──────────────────────────────────────────────
@router.get("/opendata/search")
def search_open_data(q: str = "PDRB kabupaten"):
    """
    Cari dataset publik di portal data.go.id (Satu Data Indonesia).
    """
    from opendata_fetcher import search_datasets
    results = search_datasets(q, limit=10)
    return {
        "query": q,
        "count": len(results),
        "datasets": [
            {
                "title": ds.get("title"),
                "organization": ds.get("organization", {}).get("title", ""),
                "num_resources": ds.get("num_resources", 0),
                "resources": [
                    {"id": r.get("id"), "format": r.get("format"), "name": r.get("name")}
                    for r in ds.get("resources", [])[:3]
                ]
            }
            for ds in results
        ]
    }
