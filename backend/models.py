"""
models.py — SQLAlchemy ORM models untuk 10 tabel sesuai PRD bagian 13.
"""
import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text,
    ForeignKey, DateTime, SmallInteger,
)
from sqlalchemy.orm import relationship
from database import Base


# ──────────────────────────────────────────────
# 1. REGIONS — Master Data Wilayah
# ──────────────────────────────────────────────
class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    bps_code = Column(String(10), unique=True, nullable=False, index=True)
    province = Column(String(50), nullable=False)
    province_code = Column(String(5))
    name = Column(String(100), nullable=False)
    region_type = Column(String(10), nullable=False)   # "kota" | "kabupaten"
    area_km2 = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    geojson_path = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)

    # relationships
    demographics = relationship("Demographic", back_populates="region", cascade="all, delete-orphan")
    economies = relationship("Economy", back_populates="region", cascade="all, delete-orphan")
    infrastructure = relationship("Infrastructure", back_populates="region", uselist=False, cascade="all, delete-orphan")
    property_markets = relationship("PropertyMarket", back_populates="region", cascade="all, delete-orphan")
    facility = relationship("Facility", back_populates="region", uselist=False, cascade="all, delete-orphan")
    strategic_area = relationship("StrategicArea", back_populates="region", uselist=False, cascade="all, delete-orphan")
    development_plans = relationship("DevelopmentPlan", back_populates="region", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="region", cascade="all, delete-orphan")
    ai_insights = relationship("AiInsight", back_populates="region", cascade="all, delete-orphan")


# ──────────────────────────────────────────────
# 2. DEMOGRAPHICS — Data Demografi per Tahun
# ──────────────────────────────────────────────
class Demographic(Base):
    __tablename__ = "demographics"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    year = Column(SmallInteger, nullable=False)
    population = Column(Integer)
    population_growth_pct = Column(Float)
    density_per_km2 = Column(Float)
    productive_age_count = Column(Integer)
    household_count = Column(Integer)
    urbanization_rate = Column(Float)

    region = relationship("Region", back_populates="demographics")


# ──────────────────────────────────────────────
# 3. ECONOMY — Data Ekonomi per Tahun
# ──────────────────────────────────────────────
class Economy(Base):
    __tablename__ = "economy"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    year = Column(SmallInteger, nullable=False)
    pdrb_billion_idr = Column(Float)
    economic_growth_pct = Column(Float)
    pdrb_per_capita = Column(Float)
    unemployment_rate = Column(Float)
    poverty_rate = Column(Float)
    minimum_wage_idr = Column(Float)

    region = relationship("Region", back_populates="economies")


# ──────────────────────────────────────────────
# 4. INFRASTRUCTURE — Data Infrastruktur
# ──────────────────────────────────────────────
class Infrastructure(Base):
    __tablename__ = "infrastructure"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, unique=True)
    nearest_toll_gate_km = Column(Float)
    toll_access_score = Column(SmallInteger)        # 0-100
    nearest_station_km = Column(Float)
    railway_score = Column(SmallInteger)             # 0-100
    nearest_airport_km = Column(Float)
    nearest_port_km = Column(Float)
    public_transport_score = Column(SmallInteger)    # 0-100
    road_quality_score = Column(SmallInteger)        # 0-100
    infrastructure_composite_score = Column(SmallInteger)  # 0-100

    region = relationship("Region", back_populates="infrastructure")


# ──────────────────────────────────────────────
# 5. PROPERTY MARKET — Data Properti per Tahun
# ──────────────────────────────────────────────
class PropertyMarket(Base):
    __tablename__ = "property_market"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    year = Column(SmallInteger, nullable=False)
    avg_land_price_per_m2 = Column(Float)
    avg_house_price = Column(Float)
    property_price_growth_pct = Column(Float)
    listing_count = Column(Integer)
    affordability_score = Column(SmallInteger)       # 0-100
    data_source = Column(Text)

    region = relationship("Region", back_populates="property_markets")


# ──────────────────────────────────────────────
# 6. FACILITIES — Data Fasilitas Publik
# ──────────────────────────────────────────────
class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, unique=True)
    school_count = Column(Integer)
    university_count = Column(Integer)
    hospital_count = Column(Integer)
    clinic_count = Column(Integer)
    mall_count = Column(Integer)
    traditional_market_count = Column(Integer)
    hotel_count = Column(Integer)
    tourism_spot_count = Column(Integer)
    facilities_composite_score = Column(SmallInteger)  # 0-100

    region = relationship("Region", back_populates="facility")


# ──────────────────────────────────────────────
# 7. STRATEGIC AREAS — Kawasan Strategis
# ──────────────────────────────────────────────
class StrategicArea(Base):
    __tablename__ = "strategic_areas"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, unique=True)
    has_industrial_estate = Column(Boolean, default=False)
    industrial_estate_names = Column(Text)
    has_kek = Column(Boolean, default=False)
    has_tourism_area = Column(Boolean, default=False)
    has_education_hub = Column(Boolean, default=False)
    has_tod = Column(Boolean, default=False)
    strategic_score = Column(SmallInteger)  # 0-100

    region = relationship("Region", back_populates="strategic_area")


# ──────────────────────────────────────────────
# 8. DEVELOPMENT PLANS — Rencana Pembangunan
# ──────────────────────────────────────────────
class DevelopmentPlan(Base):
    __tablename__ = "development_plans"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    plan_type = Column(String(50))       # tol, kereta, KEK, dll
    plan_name = Column(Text)
    status = Column(String(20))          # planned | ongoing | completed
    target_year = Column(SmallInteger)
    impact_score = Column(SmallInteger)  # 0-10
    source = Column(Text)

    region = relationship("Region", back_populates="development_plans")


# ──────────────────────────────────────────────
# 9. SCORES — Skor Perhitungan
# ──────────────────────────────────────────────
class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    year = Column(SmallInteger, nullable=False)
    business_score = Column(Float)
    property_score = Column(Float)
    growth_score = Column(Float)
    risk_score = Column(Float)
    final_score = Column(Float)
    recommendation_tags = Column(Text)        # comma-separated tags
    data_completeness_pct = Column(Float)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)

    region = relationship("Region", back_populates="scores")


# ──────────────────────────────────────────────
# 10. AI INSIGHTS — Insight dari LLM
# ──────────────────────────────────────────────
class AiInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    insight_text = Column(Text)
    key_strengths = Column(Text)   # JSON string array
    key_risks = Column(Text)       # JSON string array
    best_for = Column(Text)        # JSON string array
    model_version = Column(String(50))
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    region = relationship("Region", back_populates="ai_insights")
