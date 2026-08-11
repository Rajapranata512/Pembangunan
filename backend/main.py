"""
main.py — FastAPI Application Entry Point.
Platform Analisis Prospek Wilayah untuk Usaha dan Investasi Properti di Pulau Jawa.

Startup:
  1. Buat tabel database (jika belum ada)
  2. Seed data 10 kota/kabupaten sampel
  3. Hitung skor semua wilayah

Jalankan: uvicorn main:app --reload
Docs:     http://localhost:8000/docs
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base, SessionLocal
from seed_data import seed_database, seed_ai_insights
from scoring import recalculate_all_scores
import models_ai  # noqa: F401 — register AI tables with Base

from routers import regions, scores, insights, compare, recommendations, map_data, sync
from routers import ai as ai_router


# ──────────────────────────────────────────────
# Lifespan: startup & shutdown events
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Dijalankan saat server mulai: buat tabel, seed data, hitung skor."""
    print("=" * 60)
    print(">> Memulai Platform Analisis Prospek Wilayah Jawa...")
    print("=" * 60)

    # 1. Buat semua tabel
    Base.metadata.create_all(bind=engine)
    print("[DB] Tabel database berhasil dibuat/diverifikasi.")

    # 2. Seed 119 wilayah (data BPS riset)
    db = SessionLocal()
    try:
        seed_database(db)

        # 3. Hitung skor
        recalculate_all_scores(db, year=2024)

        # 4. Generate AI insights
        seed_ai_insights(db)
    finally:
        db.close()

    print("=" * 60)
    print("[OK] Server siap! Buka http://localhost:8888/docs untuk API docs.")
    print("=" * 60)

    yield  # server berjalan

    print("[STOP] Server shutdown.")


# ──────────────────────────────────────────────
# FastAPI App Instance
# ──────────────────────────────────────────────
app = FastAPI(
    title="Platform Analisis Prospek Wilayah Jawa",
    description=(
        "REST API untuk analisis prospek 119 kota/kabupaten di Pulau Jawa. "
        "Menyediakan skor potensi usaha, investasi properti, pertumbuhan wilayah, "
        "dan risiko investasi — dilengkapi AI Insight dan rekomendasi berbasis tujuan."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ──────────────────────────────────────────────
# CORS Middleware
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # MVP: izinkan semua. Production: restrict domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# Include Routers
# ──────────────────────────────────────────────
app.include_router(regions.router)
app.include_router(scores.router)
app.include_router(insights.router)
app.include_router(compare.router)
app.include_router(recommendations.router)
app.include_router(map_data.router)
app.include_router(ai_router.router)
app.include_router(sync.router)


# ──────────────────────────────────────────────
# Root Endpoint
# ──────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "platform": "Analisis Prospek Wilayah Jawa",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "regions": "/api/v1/regions",
            "compare": "/api/v1/compare",
            "recommendations": "/api/v1/recommendations",
            "map_data": "/api/v1/map-data",
        },
    }
