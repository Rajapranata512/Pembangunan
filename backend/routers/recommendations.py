"""
routers/recommendations.py — Recommendation Engine sesuai PRD bagian 8.5.
POST /api/v1/recommendations → Top 5 wilayah berdasarkan tujuan investasi.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Region, Score, Demographic, StrategicArea, Facility, Infrastructure
from schemas import RecommendationRequest, RecommendationResponse, RecommendationItem, RegionSummary

router = APIRouter(prefix="/api/v1", tags=["Recommendations"])

# ──────────────────────────────────────────────────────
# Bobot per tujuan investasi (sesuai PRD 8.5)
# Setiap tujuan mendefinisikan bobot relatif terhadap
# 4 skor utama + faktor-faktor khusus.
# ──────────────────────────────────────────────────────
GOAL_WEIGHTS = {
    "membuka_usaha_kuliner": {
        "business": 0.40, "property": 0.05, "growth": 0.25, "risk_inv": 0.20,
        "bonus": "density",  # kepadatan tinggi = lebih banyak customer
        "label": "Membuka Usaha Kuliner",
    },
    "membuka_ruko_komersial": {
        "business": 0.35, "property": 0.15, "growth": 0.20, "risk_inv": 0.20,
        "bonus": "accessibility",
        "label": "Membuka Ruko / Usaha Komersial",
    },
    "membeli_tanah_investasi": {
        "business": 0.10, "property": 0.35, "growth": 0.30, "risk_inv": 0.20,
        "bonus": "affordability",
        "label": "Membeli Tanah untuk Investasi Jangka Panjang",
    },
    "membeli_rumah_hunian": {
        "business": 0.10, "property": 0.30, "growth": 0.15, "risk_inv": 0.25,
        "bonus": "facilities",
        "label": "Membeli Rumah untuk Hunian dan Investasi",
    },
    "properti_disewakan": {
        "business": 0.25, "property": 0.25, "growth": 0.15, "risk_inv": 0.20,
        "bonus": "density",
        "label": "Membeli Properti untuk Disewakan",
    },
    "gudang_logistik": {
        "business": 0.20, "property": 0.15, "growth": 0.20, "risk_inv": 0.15,
        "bonus": "industrial",
        "label": "Membuka Gudang atau Usaha Logistik",
    },
    "usaha_dekat_kampus": {
        "business": 0.30, "property": 0.10, "growth": 0.15, "risk_inv": 0.15,
        "bonus": "university",
        "label": "Membuka Usaha Dekat Kampus",
    },
    "usaha_dekat_industri": {
        "business": 0.30, "property": 0.10, "growth": 0.25, "risk_inv": 0.15,
        "bonus": "industrial",
        "label": "Membuka Usaha Dekat Kawasan Industri",
    },
    "daerah_berkembang_terjangkau": {
        "business": 0.10, "property": 0.25, "growth": 0.40, "risk_inv": 0.15,
        "bonus": "affordability",
        "label": "Mencari Daerah Berkembang dengan Harga Terjangkau",
    },
    "risiko_rendah": {
        "business": 0.15, "property": 0.20, "growth": 0.15, "risk_inv": 0.40,
        "bonus": None,
        "label": "Mencari Daerah dengan Risiko Investasi Rendah",
    },
}


def _calc_bonus(region: Region, bonus_type: str | None, db: Session) -> float:
    """Hitung bonus 0-10 berdasarkan faktor khusus."""
    if not bonus_type:
        return 0.0

    if bonus_type == "density":
        demo = (
            db.query(Demographic)
            .filter(Demographic.region_id == region.id)
            .order_by(Demographic.year.desc())
            .first()
        )
        if demo and demo.density_per_km2:
            return min(10.0, demo.density_per_km2 / 1500)
        return 0.0

    if bonus_type == "accessibility":
        infra = (
            db.query(Infrastructure)
            .filter(Infrastructure.region_id == region.id)
            .first()
        )
        if infra and infra.infrastructure_composite_score:
            return infra.infrastructure_composite_score / 10
        return 0.0

    if bonus_type == "affordability":
        from models import PropertyMarket
        prop = (
            db.query(PropertyMarket)
            .filter(PropertyMarket.region_id == region.id)
            .order_by(PropertyMarket.year.desc())
            .first()
        )
        if prop and prop.affordability_score:
            return prop.affordability_score / 10
        return 0.0

    if bonus_type == "facilities":
        fac = (
            db.query(Facility)
            .filter(Facility.region_id == region.id)
            .first()
        )
        if fac and fac.facilities_composite_score:
            return fac.facilities_composite_score / 10
        return 0.0

    if bonus_type == "industrial":
        strat = (
            db.query(StrategicArea)
            .filter(StrategicArea.region_id == region.id)
            .first()
        )
        if strat and strat.has_industrial_estate:
            return 10.0
        return 0.0

    if bonus_type == "university":
        fac = (
            db.query(Facility)
            .filter(Facility.region_id == region.id)
            .first()
        )
        if fac and fac.university_count:
            return min(10.0, fac.university_count / 8)
        return 0.0

    return 0.0


def _generate_reason(goal_label: str, region: Region, score: Score, bonus_type: str | None) -> str:
    """Generate alasan rekomendasi berdasarkan data."""
    parts = [f"{region.name} mendapat skor final {score.final_score:.1f}"]

    if score.business_score and score.business_score >= 60:
        parts.append(f"potensi usaha tinggi ({score.business_score:.1f})")
    if score.growth_score and score.growth_score >= 60:
        parts.append(f"pertumbuhan kuat ({score.growth_score:.1f})")
    if score.risk_score and score.risk_score <= 40:
        parts.append(f"risiko rendah ({score.risk_score:.1f})")
    if score.property_score and score.property_score >= 60:
        parts.append(f"properti prospektif ({score.property_score:.1f})")

    return ". ".join(parts) + f". Sangat cocok untuk tujuan: {goal_label}."


@router.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(req: RecommendationRequest, db: Session = Depends(get_db)):
    """Rekomendasi Top 5 wilayah berdasarkan tujuan investasi."""
    goal = req.goal.lower().strip()

    if goal not in GOAL_WEIGHTS:
        available = list(GOAL_WEIGHTS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Tujuan '{req.goal}' tidak valid. Pilihan: {available}",
        )

    weights = GOAL_WEIGHTS[goal]

    # Query semua region dengan skor
    query = db.query(Region)
    if req.province:
        query = query.filter(Region.province.ilike(f"%{req.province}%"))

    regions = query.all()

    scored_items = []
    for region in regions:
        score = (
            db.query(Score)
            .filter(Score.region_id == region.id)
            .order_by(Score.year.desc())
            .first()
        )
        if not score:
            continue

        # Filter populasi minimum
        if req.min_population:
            demo = (
                db.query(Demographic)
                .filter(Demographic.region_id == region.id)
                .order_by(Demographic.year.desc())
                .first()
            )
            if not demo or not demo.population or demo.population < req.min_population:
                continue

        # Hitung relevance score
        biz = (score.business_score or 0) * weights["business"]
        prop = (score.property_score or 0) * weights["property"]
        grw = (score.growth_score or 0) * weights["growth"]
        risk_inv = ((100 - (score.risk_score or 50))) * weights["risk_inv"]
        bonus = _calc_bonus(region, weights.get("bonus"), db) * 0.10

        relevance = biz + prop + grw + risk_inv + bonus

        scored_items.append((region, score, round(relevance, 2)))

    # Sort descending by relevance
    scored_items.sort(key=lambda x: x[2], reverse=True)
    top5 = scored_items[:5]

    results = []
    for rank, (region, score, relevance) in enumerate(top5, 1):
        results.append(RecommendationItem(
            rank=rank,
            region=RegionSummary(
                id=region.id,
                bps_code=region.bps_code,
                name=region.name,
                province=region.province,
                region_type=region.region_type,
                latitude=region.latitude,
                longitude=region.longitude,
                business_score=score.business_score,
                property_score=score.property_score,
                growth_score=score.growth_score,
                risk_score=score.risk_score,
                final_score=score.final_score,
            ),
            relevance_score=relevance,
            reason=_generate_reason(weights["label"], region, score, weights.get("bonus")),
        ))

    return RecommendationResponse(goal=goal, results=results)
