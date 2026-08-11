"""
schemas.py — Pydantic models untuk validasi request/response API.
"""
from pydantic import BaseModel
from typing import Optional


# ──────────────────────────────────────────────
# Response: Region (ringkas, untuk list)
# ──────────────────────────────────────────────
class RegionSummary(BaseModel):
    id: int
    bps_code: str
    name: str
    province: str
    region_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    business_score: Optional[float] = None
    property_score: Optional[float] = None
    growth_score: Optional[float] = None
    risk_score: Optional[float] = None
    final_score: Optional[float] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: Demografi
# ──────────────────────────────────────────────
class DemographicOut(BaseModel):
    year: int
    population: Optional[int] = None
    population_growth_pct: Optional[float] = None
    density_per_km2: Optional[float] = None
    productive_age_count: Optional[int] = None
    household_count: Optional[int] = None
    urbanization_rate: Optional[float] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: Ekonomi
# ──────────────────────────────────────────────
class EconomyOut(BaseModel):
    year: int
    pdrb_billion_idr: Optional[float] = None
    economic_growth_pct: Optional[float] = None
    pdrb_per_capita: Optional[float] = None
    unemployment_rate: Optional[float] = None
    poverty_rate: Optional[float] = None
    minimum_wage_idr: Optional[float] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: Infrastruktur
# ──────────────────────────────────────────────
class InfrastructureOut(BaseModel):
    nearest_toll_gate_km: Optional[float] = None
    toll_access_score: Optional[int] = None
    nearest_station_km: Optional[float] = None
    railway_score: Optional[int] = None
    nearest_airport_km: Optional[float] = None
    nearest_port_km: Optional[float] = None
    public_transport_score: Optional[int] = None
    road_quality_score: Optional[int] = None
    infrastructure_composite_score: Optional[int] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: Properti
# ──────────────────────────────────────────────
class PropertyMarketOut(BaseModel):
    year: int
    avg_land_price_per_m2: Optional[float] = None
    avg_house_price: Optional[float] = None
    property_price_growth_pct: Optional[float] = None
    listing_count: Optional[int] = None
    affordability_score: Optional[int] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: Fasilitas
# ──────────────────────────────────────────────
class FacilityOut(BaseModel):
    school_count: Optional[int] = None
    university_count: Optional[int] = None
    hospital_count: Optional[int] = None
    clinic_count: Optional[int] = None
    mall_count: Optional[int] = None
    traditional_market_count: Optional[int] = None
    hotel_count: Optional[int] = None
    tourism_spot_count: Optional[int] = None
    facilities_composite_score: Optional[int] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: Kawasan Strategis
# ──────────────────────────────────────────────
class StrategicAreaOut(BaseModel):
    has_industrial_estate: bool = False
    industrial_estate_names: Optional[str] = None
    has_kek: bool = False
    has_tourism_area: bool = False
    has_education_hub: bool = False
    has_tod: bool = False
    strategic_score: Optional[int] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: Rencana Pembangunan
# ──────────────────────────────────────────────
class DevelopmentPlanOut(BaseModel):
    plan_type: Optional[str] = None
    plan_name: Optional[str] = None
    status: Optional[str] = None
    target_year: Optional[int] = None
    impact_score: Optional[int] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: Skor
# ──────────────────────────────────────────────
class ScoreOut(BaseModel):
    year: int
    business_score: Optional[float] = None
    property_score: Optional[float] = None
    growth_score: Optional[float] = None
    risk_score: Optional[float] = None
    final_score: Optional[float] = None
    data_completeness_pct: Optional[float] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: AI Insight
# ──────────────────────────────────────────────
class AiInsightOut(BaseModel):
    insight_text: Optional[str] = None
    key_strengths: Optional[str] = None   # JSON string
    key_risks: Optional[str] = None       # JSON string
    best_for: Optional[str] = None        # JSON string

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: Region Detail (lengkap)
# ──────────────────────────────────────────────
class RegionDetail(BaseModel):
    id: int
    bps_code: str
    name: str
    province: str
    province_code: Optional[str] = None
    region_type: str
    area_km2: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    demographics: list[DemographicOut] = []
    economy: list[EconomyOut] = []
    infrastructure: Optional[InfrastructureOut] = None
    property_market: list[PropertyMarketOut] = []
    facilities: Optional[FacilityOut] = None
    strategic_area: Optional[StrategicAreaOut] = None
    development_plans: list[DevelopmentPlanOut] = []
    scores: list[ScoreOut] = []
    ai_insight: Optional[AiInsightOut] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Response: Map Data (minimal, untuk render peta)
# ──────────────────────────────────────────────
class MapDataPoint(BaseModel):
    id: int
    name: str
    province: str
    region_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    business_score: Optional[float] = None
    property_score: Optional[float] = None
    growth_score: Optional[float] = None
    risk_score: Optional[float] = None
    final_score: Optional[float] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Request: Recommendation
# ──────────────────────────────────────────────
class RecommendationRequest(BaseModel):
    goal: str
    province: Optional[str] = None
    min_population: Optional[int] = None
    max_property_price: Optional[float] = None


class RecommendationItem(BaseModel):
    rank: int
    region: RegionSummary
    relevance_score: float
    reason: str


class RecommendationResponse(BaseModel):
    goal: str
    results: list[RecommendationItem]


# ──────────────────────────────────────────────
# Response: Paginated List
# ──────────────────────────────────────────────
class PaginatedRegions(BaseModel):
    total: int
    page: int
    limit: int
    data: list[RegionSummary]


# ──────────────────────────────────────────────
# Request/Response: AI Chatbot
# ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str


# ──────────────────────────────────────────────
# Response: News Sentiment
# ──────────────────────────────────────────────
class SentimentOut(BaseModel):
    overall_sentiment: str = "netral"
    confidence_score: float = 0.5
    summary: str = ""
    highlights: list[dict] = []
    headlines: list[str] = []
    cached: bool = False


# ──────────────────────────────────────────────
# Response: Generate Insight
# ──────────────────────────────────────────────
class GenerateInsightResponse(BaseModel):
    success: bool
    message: str
    insight: Optional[AiInsightOut] = None
