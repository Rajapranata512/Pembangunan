"""
routers/map_data.py — Data ringkas untuk render peta.
GET /api/v1/map-data → Array GeoJSON-compatible data wilayah.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Region, Score
from schemas import MapDataPoint

router = APIRouter(prefix="/api/v1", tags=["Map Data"])


@router.get("/map-data", response_model=list[MapDataPoint])
def get_map_data(
    province: str | None = Query(None, description="Filter provinsi"),
    score_type: str = Query("final_score", description="Skor untuk warna: final_score, business_score, property_score, growth_score, risk_score"),
    db: Session = Depends(get_db),
):
    """Data minimal (id, nama, koordinat, skor) untuk render peta interaktif."""
    query = db.query(Region)
    if province:
        query = query.filter(Region.province.ilike(f"%{province}%"))

    regions = query.all()
    results = []

    for r in regions:
        latest_score = (
            db.query(Score)
            .filter(Score.region_id == r.id)
            .order_by(Score.year.desc())
            .first()
        )
        s = latest_score
        results.append(MapDataPoint(
            id=r.id,
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
        ))

    return results
