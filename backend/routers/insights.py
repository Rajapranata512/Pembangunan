"""
routers/insights.py — Endpoint AI Insight per wilayah.
GET /api/v1/regions/{id}/insight → Teks insight + strengths + risks + best_for.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Region, AiInsight
from schemas import AiInsightOut

router = APIRouter(prefix="/api/v1", tags=["AI Insights"])


@router.get("/regions/{region_id}/insight", response_model=AiInsightOut)
def get_region_insight(region_id: int, db: Session = Depends(get_db)):
    """Insight AI aktif untuk satu wilayah."""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Wilayah tidak ditemukan")

    insight = (
        db.query(AiInsight)
        .filter(AiInsight.region_id == region_id, AiInsight.is_active == True)
        .order_by(AiInsight.generated_at.desc())
        .first()
    )

    if not insight:
        raise HTTPException(status_code=404, detail="Insight AI belum tersedia untuk wilayah ini")

    return AiInsightOut.model_validate(insight)
