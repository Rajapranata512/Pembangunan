"""
seed_data.py — Seeder untuk 119 kota/kabupaten di Pulau Jawa.
Menggunakan data riset dari BPS 2023/2024.
"""
import json
import datetime
from sqlalchemy.orm import Session
from models import (
    Region, Demographic, Economy, Infrastructure, PropertyMarket,
    Facility, StrategicArea, DevelopmentPlan, AiInsight,
)
from data import ALL_REGIONS


def _derive_fields(r: dict) -> dict:
    """Hitung field turunan dari data primer."""
    pop = r["pop"]
    area = r["area"]
    density = round(pop / area, 1) if area > 0 else 0
    productive = int(pop * 0.67)  # rasio usia produktif rata-rata BPS
    household = int(pop / 3.8)    # rata-rata anggota RT BPS
    urbanization = 100.0 if r["type"] == "kota" else min(85, max(20, r.get("infra", 50) * 0.8 + 10))

    # Infrastructure sub-scores
    toll_km = r["toll_km"]
    toll_score = max(0, min(100, int(100 - toll_km * 3))) if toll_km < 999 else 5
    station_km = r["station_km"]
    rail_score = max(0, min(100, int(100 - station_km * 4))) if station_km < 999 else 5
    airport_km = r["airport_km"]

    # Port
    port_km = r.get("port_km", 100)

    # Facility composite
    school = r["school"]
    univ = r["univ"]
    hosp = r["hosp"]
    fac_composite = r["fac"]

    # Listing count estimate
    listing = max(50, int(pop / 2000))

    return {
        "density": density,
        "productive": productive,
        "household": household,
        "urbanization": urbanization,
        "toll_score": toll_score,
        "rail_score": rail_score,
        "port_km": port_km,
        "listing": listing,
    }


def seed_database(db: Session):
    """Seed seluruh database dengan data 119 wilayah."""
    existing = db.query(Region).count()
    if existing >= 100:
        print(f"[Seed] Data sudah ada ({existing} wilayah), skip seeding.")
        return

    # Hapus semua data lama jika ada < 100 (data dummy lama)
    if existing > 0:
        for model in [AiInsight, DevelopmentPlan, StrategicArea, Facility,
                      PropertyMarket, Infrastructure, Economy, Demographic, Region]:
            db.query(model).delete()
        db.commit()
        print(f"[Seed] Data lama ({existing} wilayah) dihapus.")

    count = 0
    for r in ALL_REGIONS:
        d = _derive_fields(r)

        # 1. Region
        region = Region(
            bps_code=r["bps"],
            name=r["name"],
            province=r["prov"],
            province_code=r["prov_code"],
            region_type=r["type"],
            area_km2=r["area"],
            latitude=r["lat"],
            longitude=r["lng"],
        )
        db.add(region)
        db.flush()  # get region.id

        # 2. Demographic
        db.add(Demographic(
            region_id=region.id, year=2024,
            population=r["pop"],
            population_growth_pct=r["pop_gr"],
            density_per_km2=d["density"],
            productive_age_count=d["productive"],
            household_count=d["household"],
            urbanization_rate=d["urbanization"],
        ))

        # 3. Economy
        db.add(Economy(
            region_id=region.id, year=2024,
            pdrb_billion_idr=r["pdrb"],
            economic_growth_pct=r["econ_gr"],
            pdrb_per_capita=r["capita"],
            unemployment_rate=r["unemp"],
            poverty_rate=r["poverty"],
            minimum_wage_idr=r["umk"],
        ))

        # 4. Infrastructure
        db.add(Infrastructure(
            region_id=region.id,
            nearest_toll_gate_km=r["toll_km"] if r["toll_km"] < 999 else None,
            toll_access_score=d["toll_score"],
            nearest_station_km=r["station_km"] if r["station_km"] < 999 else None,
            railway_score=d["rail_score"],
            nearest_airport_km=r["airport_km"] if r["airport_km"] < 999 else None,
            nearest_port_km=d["port_km"] if d["port_km"] < 999 else None,
            public_transport_score=min(100, max(10, r["infra"] - 5)),
            road_quality_score=min(100, max(10, r["infra"] - 3)),
            infrastructure_composite_score=r["infra"],
        ))

        # 5. Property Market
        db.add(PropertyMarket(
            region_id=region.id, year=2024,
            avg_land_price_per_m2=r["land_price"],
            avg_house_price=r["house_price"],
            property_price_growth_pct=r["prop_gr"],
            listing_count=d["listing"],
            affordability_score=r["afford"],
            data_source="BPS SHPR Estimasi 2024",
        ))

        # 6. Facility
        db.add(Facility(
            region_id=region.id,
            school_count=r["school"],
            university_count=r["univ"],
            hospital_count=r["hosp"],
            clinic_count=int(r["school"] * 0.4),
            mall_count=max(0, int(r["fac"] / 12)),
            traditional_market_count=max(3, int(r["school"] * 0.08)),
            hotel_count=max(2, int(r["fac"] * 0.5)),
            tourism_spot_count=max(1, int(r["fac"] * 0.3)),
            facilities_composite_score=r["fac"],
        ))

        # 7. Strategic Area
        db.add(StrategicArea(
            region_id=region.id,
            has_industrial_estate=r["industrial"],
            industrial_estate_names=r["ind_names"],
            has_kek=r["kek"],
            has_tourism_area=r["tourism"],
            has_education_hub=r["edu_hub"],
            has_tod=r["tod"],
            strategic_score=r["strat"],
        ))

        count += 1

    db.commit()
    print(f"[Seed] {count} wilayah berhasil di-seed dari data BPS riset.")


def seed_ai_insights(db: Session):
    """Generate AI insight placeholder untuk semua region yang belum punya."""
    regions = db.query(Region).all()
    for r in regions:
        existing = db.query(AiInsight).filter(AiInsight.region_id == r.id, AiInsight.is_active == True).first()
        if existing:
            continue

        # Auto-generate insight dari data
        scores_obj = r.scores[0] if r.scores else None
        econ = sorted(r.economies, key=lambda e: e.year, reverse=True)
        e = econ[0] if econ else None
        infra = r.infrastructure
        strat = r.strategic_area

        strengths = []
        risks = []
        best_for = []

        if scores_obj:
            if scores_obj.business_score and scores_obj.business_score > 60:
                strengths.append("Potensi bisnis kuat")
                best_for.append("Usaha retail & jasa")
            if scores_obj.property_score and scores_obj.property_score > 60:
                strengths.append("Pasar properti prospektif")
                best_for.append("Investasi properti")
            if scores_obj.growth_score and scores_obj.growth_score > 60:
                strengths.append("Pertumbuhan wilayah tinggi")
                best_for.append("Investasi jangka panjang")

        if e:
            if e.economic_growth_pct and e.economic_growth_pct > 5.5:
                strengths.append(f"Pertumbuhan ekonomi {e.economic_growth_pct}%")
            if e.unemployment_rate and e.unemployment_rate > 8:
                risks.append(f"Pengangguran tinggi ({e.unemployment_rate}%)")
            if e.poverty_rate and e.poverty_rate > 12:
                risks.append(f"Kemiskinan tinggi ({e.poverty_rate}%)")

        if infra:
            if infra.infrastructure_composite_score and infra.infrastructure_composite_score > 75:
                strengths.append("Infrastruktur lengkap")
            elif infra.infrastructure_composite_score and infra.infrastructure_composite_score < 40:
                risks.append("Infrastruktur terbatas")

        if strat:
            if strat.has_industrial_estate:
                strengths.append("Kawasan industri tersedia")
                best_for.append("Industri & manufaktur")
            if strat.has_kek:
                strengths.append("Kawasan Ekonomi Khusus (KEK)")
            if strat.has_tourism_area:
                best_for.append("Pariwisata & hospitality")

        if not best_for:
            best_for.append("Investasi konservatif")

        prov_short = r.province.replace("Jawa ", "J.")
        insight_text = (
            f"{r.name} ({prov_short}) merupakan {r.region_type} dengan luas "
            f"{r.area_km2:,.0f} km\u00b2. "
        )
        if e:
            insight_text += (
                f"PDRB mencapai Rp {e.pdrb_billion_idr:,.1f} miliar dengan pertumbuhan "
                f"{e.economic_growth_pct}% dan PDRB per kapita Rp {e.pdrb_per_capita:,.0f}. "
            )
        if strengths:
            insight_text += f"Kekuatan utama: {', '.join(strengths[:3])}. "
        if risks:
            insight_text += f"Risiko: {', '.join(risks[:2])}."

        db.add(AiInsight(
            region_id=r.id,
            insight_text=insight_text,
            key_strengths=json.dumps(strengths[:5]),
            key_risks=json.dumps(risks[:5]),
            best_for=json.dumps(best_for[:5]),
            model_version="auto-gen-v1",
            generated_at=datetime.datetime.utcnow(),
            is_active=True,
        ))

    db.commit()
    print(f"[Seed] AI Insights generated for {len(regions)} wilayah.")
