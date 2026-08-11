"""
routers/regions.py — Endpoint untuk daftar dan detail wilayah.
GET /api/v1/regions        → List semua wilayah + skor ringkas
GET /api/v1/regions/{id}   → Detail lengkap satu wilayah
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Region, Score, AiInsight
from schemas import (
    RegionSummary, RegionDetail, PaginatedRegions,
    DemographicOut, EconomyOut, InfrastructureOut,
    PropertyMarketOut, FacilityOut, StrategicAreaOut,
    DevelopmentPlanOut, ScoreOut, AiInsightOut,
)

router = APIRouter(prefix="/api/v1", tags=["Regions"])


@router.get("/regions", response_model=PaginatedRegions)
def list_regions(
    province: str | None = Query(None, description="Filter berdasarkan provinsi"),
    type: str | None = Query(None, description="Filter: kota / kabupaten"),
    min_score: float | None = Query(None, description="Skor final minimum"),
    max_risk: float | None = Query(None, description="Skor risiko maksimum"),
    sort_by: str = Query("final_score", description="Kolom sorting: final_score, business_score, property_score, growth_score, risk_score, name"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Daftar semua wilayah dengan skor ringkas, filter, dan pagination."""
    query = db.query(Region)

    # Filters
    if province:
        query = query.filter(Region.province.ilike(f"%{province}%"))
    if type:
        query = query.filter(Region.region_type == type.lower())

    regions = query.all()

    # Build summary list with latest scores
    results = []
    for r in regions:
        latest_score = (
            db.query(Score)
            .filter(Score.region_id == r.id)
            .order_by(Score.year.desc())
            .first()
        )
        s = latest_score
        summary = RegionSummary(
            id=r.id,
            bps_code=r.bps_code,
            name=r.name,
            province=r.province,
            region_type=r.region_type,
            latitude=r.latitude,
            longitude=r.longitude,
            business_score=s.business_score if s else None,
            property_score=s.property_score if s else None,
            growth_score=s.growth_score if s else None,
            risk_score=s.risk_score if s else None,
            final_score=s.final_score if s else None,
        )

        # Post-filter berdasarkan skor
        if min_score and (summary.final_score is None or summary.final_score < min_score):
            continue
        if max_risk and (summary.risk_score is None or summary.risk_score > max_risk):
            continue

        results.append(summary)

    # Sorting
    sort_field = sort_by if sort_by in [
        "final_score", "business_score", "property_score",
        "growth_score", "risk_score", "name"
    ] else "final_score"

    reverse = sort_field != "name"  # descending untuk skor, ascending untuk nama
    if sort_field == "name":
        results.sort(key=lambda x: x.name)
    else:
        results.sort(
            key=lambda x: getattr(x, sort_field) or 0,
            reverse=reverse,
        )

    # Pagination
    total = len(results)
    start = (page - 1) * limit
    end = start + limit
    paginated = results[start:end]

    return PaginatedRegions(total=total, page=page, limit=limit, data=paginated)


@router.get("/regions/{region_id}", response_model=RegionDetail)
def get_region_detail(region_id: int, db: Session = Depends(get_db)):
    """Detail lengkap satu wilayah: semua indikator, skor, dan insight AI."""
    region = (
        db.query(Region)
        .options(
            joinedload(Region.demographics),
            joinedload(Region.economies),
            joinedload(Region.infrastructure),
            joinedload(Region.property_markets),
            joinedload(Region.facility),
            joinedload(Region.strategic_area),
            joinedload(Region.development_plans),
            joinedload(Region.scores),
            joinedload(Region.ai_insights),
        )
        .filter(Region.id == region_id)
        .first()
    )

    if not region:
        raise HTTPException(status_code=404, detail="Wilayah tidak ditemukan")

    # Ambil insight aktif
    active_insight = next(
        (i for i in region.ai_insights if i.is_active), None
    )

    return RegionDetail(
        id=region.id,
        bps_code=region.bps_code,
        name=region.name,
        province=region.province,
        province_code=region.province_code,
        region_type=region.region_type,
        area_km2=region.area_km2,
        latitude=region.latitude,
        longitude=region.longitude,
        demographics=[DemographicOut.model_validate(d) for d in region.demographics],
        economy=[EconomyOut.model_validate(e) for e in region.economies],
        infrastructure=InfrastructureOut.model_validate(region.infrastructure) if region.infrastructure else None,
        property_market=[PropertyMarketOut.model_validate(p) for p in region.property_markets],
        facilities=FacilityOut.model_validate(region.facility) if region.facility else None,
        strategic_area=StrategicAreaOut.model_validate(region.strategic_area) if region.strategic_area else None,
        development_plans=[DevelopmentPlanOut.model_validate(dp) for dp in region.development_plans],
        scores=[ScoreOut.model_validate(s) for s in region.scores],
        ai_insight=AiInsightOut.model_validate(active_insight) if active_insight else None,
    )
