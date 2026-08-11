"""
routers/compare.py — Endpoint perbandingan antarwilayah.
GET /api/v1/compare?ids=1,2,3 → Data lengkap perbandingan.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Region, Score, AiInsight
from schemas import RegionDetail, DemographicOut, EconomyOut, InfrastructureOut, PropertyMarketOut, FacilityOut, StrategicAreaOut, DevelopmentPlanOut, ScoreOut, AiInsightOut

router = APIRouter(prefix="/api/v1", tags=["Comparison"])


@router.get("/compare", response_model=list[RegionDetail])
def compare_regions(
    ids: str = Query(..., description="ID wilayah dipisah koma, e.g. 1,2,3 (maks 4)"),
    db: Session = Depends(get_db),
):
    """Perbandingan data lengkap untuk 2-4 wilayah."""
    try:
        id_list = [int(x.strip()) for x in ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Format ids tidak valid. Gunakan angka dipisah koma.")

    if len(id_list) < 2:
        raise HTTPException(status_code=400, detail="Minimal 2 wilayah untuk perbandingan.")
    if len(id_list) > 4:
        raise HTTPException(status_code=400, detail="Maksimal 4 wilayah untuk perbandingan.")

    regions = (
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
        .filter(Region.id.in_(id_list))
        .all()
    )

    if len(regions) != len(id_list):
        found_ids = {r.id for r in regions}
        missing = [i for i in id_list if i not in found_ids]
        raise HTTPException(status_code=404, detail=f"Wilayah tidak ditemukan: {missing}")

    results = []
    for region in regions:
        active_insight = next(
            (i for i in region.ai_insights if i.is_active), None
        )
        results.append(RegionDetail(
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
        ))

    return results
