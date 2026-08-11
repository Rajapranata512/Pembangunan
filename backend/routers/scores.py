"""
routers/scores.py — Endpoint skor per wilayah.
GET /api/v1/regions/{id}/scores → Object skor 4 kategori + final.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Region, Score
from schemas import ScoreOut

router = APIRouter(prefix="/api/v1", tags=["Scores"])


@router.get("/regions/{region_id}/scores", response_model=ScoreOut)
def get_region_scores(
    region_id: int,
    year: int | None = Query(None, description="Tahun skor (default: terbaru)"),
    db: Session = Depends(get_db),
):
    """Skor per kategori untuk satu wilayah."""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Wilayah tidak ditemukan")

    query = db.query(Score).filter(Score.region_id == region_id)
    if year:
        query = query.filter(Score.year == year)

    score = query.order_by(Score.year.desc()).first()
    if not score:
        raise HTTPException(status_code=404, detail="Skor belum tersedia untuk wilayah ini")

    return ScoreOut.model_validate(score)
