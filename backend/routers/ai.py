"""
routers/ai.py — Endpoint untuk semua fitur AI/LLM.
- Generate insight (single + batch)
- Chatbot
- PDF report
- News sentiment
"""
import json
import uuid
import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Region, Demographic, Economy, Infrastructure, PropertyMarket, Facility, StrategicArea, Score, AiInsight
from models_ai import ChatHistory, NewsSentiment
from ai_service import get_ai_service
from schemas import (
    ChatRequest, ChatResponse,
    SentimentOut, GenerateInsightResponse,
    AiInsightOut,
)
from news_scraper import fetch_news_headlines, get_headlines_text
from pdf_generator import generate_pdf_report

import io

router = APIRouter(prefix="/api/v1/ai", tags=["AI / LLM"])


# ──────────────────────────────────────────────
# Helper: collect all region data into a flat dict
# ──────────────────────────────────────────────
def _collect_region_data(region: Region, db: Session) -> dict:
    """Gather all data for a region into a flat dictionary for AI prompts."""
    demo = sorted(region.demographics, key=lambda d: d.year, reverse=True)
    d = demo[0] if demo else None

    econ = sorted(region.economies, key=lambda e: e.year, reverse=True)
    e = econ[0] if econ else None

    infra = region.infrastructure
    prop_list = sorted(region.property_markets, key=lambda p: p.year, reverse=True)
    prop = prop_list[0] if prop_list else None

    fac = region.facility
    strat = region.strategic_area
    score = region.scores[0] if region.scores else None

    return {
        "name": region.name,
        "province": region.province,
        "region_type": "Kota" if region.region_type == "kota" else "Kabupaten",
        "area_km2": region.area_km2 or 0,
        # Demographics
        "population": d.population if d else 0,
        "pop_growth": d.population_growth_pct if d else 0,
        "density": d.density_per_km2 if d else 0,
        "productive_age": d.productive_age_count if d else 0,
        "urbanization": d.urbanization_rate if d else 0,
        # Economy
        "pdrb": e.pdrb_billion_idr if e else 0,
        "econ_growth": e.economic_growth_pct if e else 0,
        "pdrb_capita": e.pdrb_per_capita if e else 0,
        "unemployment": e.unemployment_rate if e else 0,
        "poverty": e.poverty_rate if e else 0,
        "umk": e.minimum_wage_idr if e else 0,
        # Infrastructure
        "infra_score": infra.infrastructure_composite_score if infra else 0,
        "toll_km": infra.nearest_toll_gate_km if infra and infra.nearest_toll_gate_km else "N/A",
        "station_km": infra.nearest_station_km if infra and infra.nearest_station_km else "N/A",
        "airport_km": infra.nearest_airport_km if infra and infra.nearest_airport_km else "N/A",
        # Property
        "land_price": prop.avg_land_price_per_m2 if prop else 0,
        "house_price": prop.avg_house_price if prop else 0,
        "prop_growth": prop.property_price_growth_pct if prop else 0,
        "affordability": prop.affordability_score if prop else 0,
        # Facilities
        "schools": fac.school_count if fac else 0,
        "universities": fac.university_count if fac else 0,
        "hospitals": fac.hospital_count if fac else 0,
        "malls": fac.mall_count if fac else 0,
        "facility_score": fac.facilities_composite_score if fac else 0,
        # Strategic
        "has_industrial": "Ya" if (strat and strat.has_industrial_estate) else "Tidak",
        "industrial_names": strat.industrial_estate_names if strat and strat.industrial_estate_names else "-",
        "has_kek": "Ya" if (strat and strat.has_kek) else "Tidak",
        "has_tourism": "Ya" if (strat and strat.has_tourism_area) else "Tidak",
        "has_edu_hub": "Ya" if (strat and strat.has_education_hub) else "Tidak",
        "has_tod": "Ya" if (strat and strat.has_tod) else "Tidak",
        "strategic_score": strat.strategic_score if strat else 0,
        # Scores
        "business_score": round(score.business_score, 1) if score and score.business_score else 0,
        "property_score": round(score.property_score, 1) if score and score.property_score else 0,
        "growth_score": round(score.growth_score, 1) if score and score.growth_score else 0,
        "risk_score": round(score.risk_score, 1) if score and score.risk_score else 0,
        "final_score": round(score.final_score, 1) if score and score.final_score else 0,
    }


def _build_regions_summary(db: Session) -> str:
    """Build a summary of all regions for chatbot context."""
    regions = (
        db.query(Region)
        .join(Score, Region.id == Score.region_id)
        .order_by(Score.final_score.desc())
        .limit(30)
        .all()
    )

    lines = []
    for r in regions:
        s = r.scores[0] if r.scores else None
        e_list = sorted(r.economies, key=lambda x: x.year, reverse=True)
        e = e_list[0] if e_list else None
        d_list = sorted(r.demographics, key=lambda x: x.year, reverse=True)
        d = d_list[0] if d_list else None

        line = (
            f"- {r.name} ({r.province}, {r.region_type}): "
            f"Final={s.final_score:.1f}, Business={s.business_score:.1f}, "
            f"Property={s.property_score:.1f}, Growth={s.growth_score:.1f}, "
            f"Risk={s.risk_score:.1f}"
        )
        if d:
            line += f", Pop={d.population:,}"
        if e:
            line += f", PDRB={e.pdrb_billion_idr:,.0f}M, UMK={e.minimum_wage_idr:,.0f}"
        lines.append(line)

    return "\n".join(lines)


# ──────────────────────────────────────────────
# 1. GENERATE INSIGHT (Single Region)
# ──────────────────────────────────────────────
@router.post("/generate-insight/{region_id}", response_model=GenerateInsightResponse)
def generate_insight(region_id: int, db: Session = Depends(get_db)):
    """Generate a new AI insight for a specific region using Gemini."""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Wilayah tidak ditemukan")

    ai = get_ai_service()
    if not ai.is_available:
        raise HTTPException(
            status_code=503,
            detail="AI service tidak tersedia. Pastikan GEMINI_API_KEY sudah di-set di file .env"
        )

    # Collect data
    data = _collect_region_data(region, db)

    # Generate insight
    result = ai.generate_region_insight(data)

    if not result.success:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {result.error}")

    # Deactivate old insights
    db.query(AiInsight).filter(
        AiInsight.region_id == region_id,
        AiInsight.is_active == True,
    ).update({"is_active": False})

    # Save new insight
    new_insight = AiInsight(
        region_id=region_id,
        insight_text=result.insight_text,
        key_strengths=json.dumps(result.key_strengths, ensure_ascii=False),
        key_risks=json.dumps(result.key_risks, ensure_ascii=False),
        best_for=json.dumps(result.best_for, ensure_ascii=False),
        model_version=result.model_version,
        generated_at=datetime.datetime.utcnow(),
        is_active=True,
    )
    db.add(new_insight)
    db.commit()

    return GenerateInsightResponse(
        success=True,
        message=f"AI insight berhasil di-generate untuk {region.name}",
        insight=AiInsightOut(
            insight_text=new_insight.insight_text,
            key_strengths=new_insight.key_strengths,
            key_risks=new_insight.key_risks,
            best_for=new_insight.best_for,
        ),
    )


# ──────────────────────────────────────────────
# 2. GENERATE ALL INSIGHTS (Background Batch)
# ──────────────────────────────────────────────
def _batch_generate_insights(db_url: str):
    """Background task to generate insights for all regions."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import time

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()

    ai = get_ai_service()
    if not ai.is_available:
        print("[AI Batch] AI service not available, aborting.")
        db.close()
        return

    regions = db.query(Region).all()
    total = len(regions)
    print(f"[AI Batch] Starting batch generation for {total} regions...")

    for i, region in enumerate(regions):
        try:
            data = _collect_region_data(region, db)
            result = ai.generate_region_insight(data)

            if result.success:
                # Deactivate old
                db.query(AiInsight).filter(
                    AiInsight.region_id == region.id,
                    AiInsight.is_active == True,
                ).update({"is_active": False})

                # Save new
                db.add(AiInsight(
                    region_id=region.id,
                    insight_text=result.insight_text,
                    key_strengths=json.dumps(result.key_strengths, ensure_ascii=False),
                    key_risks=json.dumps(result.key_risks, ensure_ascii=False),
                    best_for=json.dumps(result.best_for, ensure_ascii=False),
                    model_version=result.model_version,
                    generated_at=datetime.datetime.utcnow(),
                    is_active=True,
                ))
                db.commit()
                print(f"[AI Batch] [{i+1}/{total}] ✅ {region.name}")
            else:
                print(f"[AI Batch] [{i+1}/{total}] ❌ {region.name}: {result.error}")

            # Rate limiting: ~4 seconds between calls to stay within 15 RPM
            time.sleep(4.5)

        except Exception as e:
            print(f"[AI Batch] [{i+1}/{total}] ❌ {region.name}: {e}")
            time.sleep(5)

    db.close()
    print(f"[AI Batch] ✅ Batch generation complete for {total} regions.")


@router.post("/generate-all-insights")
def generate_all_insights(background_tasks: BackgroundTasks):
    """Start batch generation of AI insights for all regions (background task)."""
    ai = get_ai_service()
    if not ai.is_available:
        raise HTTPException(
            status_code=503,
            detail="AI service tidak tersedia. Pastikan GEMINI_API_KEY sudah di-set."
        )

    from database import SQLALCHEMY_DATABASE_URL
    background_tasks.add_task(_batch_generate_insights, SQLALCHEMY_DATABASE_URL)

    return {
        "success": True,
        "message": "Batch generation dimulai di background. Proses untuk 119 wilayah membutuhkan ~9 menit (rate limit 15 RPM).",
    }


# ──────────────────────────────────────────────
# 3. CHATBOT
# ──────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    """Interactive investment chatbot powered by Gemini."""
    ai = get_ai_service()
    if not ai.is_available:
        return ChatResponse(
            session_id=req.session_id or str(uuid.uuid4()),
            response="Maaf, layanan AI belum aktif. Silakan set GEMINI_API_KEY di file .env backend dan restart server.",
        )

    session_id = req.session_id or str(uuid.uuid4())

    # Get chat history for this session
    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
        .limit(20)
        .all()
    )

    # Build context
    regions_summary = _build_regions_summary(db)

    # Build history string
    history_text = ""
    if history:
        history_text = "\n".join(
            f"{'User' if h.role == 'user' else 'Assistant'}: {h.content}"
            for h in history[-10:]  # Last 10 messages
        )

    # Get region stats
    total_regions = db.query(Region).count()
    all_scores = db.query(Score).all()
    avg_score = sum(s.final_score for s in all_scores if s.final_score) / max(len(all_scores), 1)
    best = max(all_scores, key=lambda s: s.final_score or 0) if all_scores else None
    worst = min(all_scores, key=lambda s: s.final_score or 100) if all_scores else None

    best_region_name = db.query(Region).filter(Region.id == best.region_id).first().name if best else "N/A"
    worst_region_name = db.query(Region).filter(Region.id == worst.region_id).first().name if worst else "N/A"

    from prompts import CHATBOT_CONTEXT_TEMPLATE
    context = CHATBOT_CONTEXT_TEMPLATE.format(
        top_regions_summary=regions_summary,
        total_regions=total_regions,
        avg_score=avg_score,
        best_region=best_region_name,
        best_score=best.final_score if best else 0,
        worst_region=worst_region_name,
        worst_score=worst.final_score if worst else 0,
        chat_history=history_text or "(belum ada percakapan)",
        user_message=req.message,
    )

    # Call AI
    response_text = ai.chat(req.message, context=context)

    # Save history
    db.add(ChatHistory(session_id=session_id, role="user", content=req.message))
    db.add(ChatHistory(session_id=session_id, role="assistant", content=response_text))
    db.commit()

    return ChatResponse(
        session_id=session_id,
        response=response_text,
    )


# ──────────────────────────────────────────────
# 4. PDF REPORT
# ──────────────────────────────────────────────
@router.get("/report/{region_id}")
def download_report(region_id: int, db: Session = Depends(get_db)):
    """Generate and download a PDF investment report for a region."""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Wilayah tidak ditemukan")

    data = _collect_region_data(region, db)

    # Try to get AI narrative
    ai = get_ai_service()
    ai_narrative = ""
    if ai.is_available:
        ai_narrative = ai.generate_pdf_narrative(data)

    # Get existing insight data
    insight = (
        db.query(AiInsight)
        .filter(AiInsight.region_id == region_id, AiInsight.is_active == True)
        .first()
    )
    insight_data = None
    if insight:
        insight_data = {
            "key_strengths": json.loads(insight.key_strengths) if insight.key_strengths else [],
            "key_risks": json.loads(insight.key_risks) if insight.key_risks else [],
            "best_for": json.loads(insight.best_for) if insight.best_for else [],
        }

    # Generate PDF
    pdf_bytes = generate_pdf_report(data, ai_narrative, insight_data)

    if pdf_bytes is None:
        raise HTTPException(
            status_code=503,
            detail="PDF generation tidak tersedia. Install reportlab: pip install reportlab"
        )

    filename = f"ProspekJawa_Report_{region.name.replace(' ', '_')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ──────────────────────────────────────────────
# 5. NEWS SENTIMENT
# ──────────────────────────────────────────────
@router.get("/sentiment/{region_id}", response_model=SentimentOut)
def get_sentiment(region_id: int, db: Session = Depends(get_db)):
    """Get news sentiment analysis for a region."""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Wilayah tidak ditemukan")

    # Check cache (24 hours)
    cache = (
        db.query(NewsSentiment)
        .filter(NewsSentiment.region_id == region_id)
        .order_by(NewsSentiment.analyzed_at.desc())
        .first()
    )
    if cache:
        age_hours = (datetime.datetime.utcnow() - cache.analyzed_at).total_seconds() / 3600
        if age_hours < 24:
            return SentimentOut(
                overall_sentiment=cache.overall_sentiment or "netral",
                confidence_score=cache.confidence_score or 0.5,
                summary=cache.summary or "",
                highlights=json.loads(cache.highlights_json) if cache.highlights_json else [],
                headlines=json.loads(cache.headlines_json) if cache.headlines_json else [],
                cached=True,
            )

    # Fetch fresh news
    news_items = fetch_news_headlines(region.name, region.province)
    headlines = [item["title"] for item in news_items]

    if not headlines:
        return SentimentOut(
            overall_sentiment="netral",
            confidence_score=0.0,
            summary=f"Tidak ditemukan berita terkini tentang {region.name} dalam konteks investasi/ekonomi.",
            highlights=[],
            headlines=[],
            cached=False,
        )

    # Analyze with AI
    ai = get_ai_service()
    if not ai.is_available:
        return SentimentOut(
            overall_sentiment="netral",
            confidence_score=0.0,
            summary="AI service tidak tersedia untuk analisis sentimen. Berita ditemukan tetapi belum dianalisis.",
            highlights=[],
            headlines=headlines,
            cached=False,
        )

    result = ai.analyze_sentiment(headlines, region.name, region.province)

    # Cache result
    db.add(NewsSentiment(
        region_id=region_id,
        headlines_json=json.dumps(headlines, ensure_ascii=False),
        overall_sentiment=result.overall_sentiment,
        confidence_score=result.confidence_score,
        summary=result.summary,
        highlights_json=json.dumps(result.highlights, ensure_ascii=False),
        analyzed_at=datetime.datetime.utcnow(),
    ))
    db.commit()

    return SentimentOut(
        overall_sentiment=result.overall_sentiment,
        confidence_score=result.confidence_score,
        summary=result.summary,
        highlights=result.highlights,
        headlines=headlines,
        cached=False,
    )
