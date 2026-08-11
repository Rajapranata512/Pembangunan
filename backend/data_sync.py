import os
import random
import datetime
from sqlalchemy.orm import Session
from models import Region, Demographic, Economy, PropertyMarket, Score
from scoring import recalculate_all_scores

def simulate_growth_rate(base_pct: float, volatility: float = 1.0) -> float:
    """Generate a realistic growth rate variation based on previous year."""
    variation = random.uniform(-volatility, volatility)
    new_pct = base_pct + variation
    return round(new_pct, 2)

def run_annual_sync(db: Session, target_year: int) -> dict:
    """
    Menjalankan sinkronisasi tahunan untuk semua region.
    Karena API BPS sedang diblokir (Cloudflare), fungsi ini menggunakan
    'Simulated Growth Engine' untuk memproyeksikan data historis.
    """
    regions = db.query(Region).all()
    if not regions:
        return {"success": False, "message": "Tidak ada data wilayah untuk disinkronisasi."}

    # Cek apakah tahun ini sudah disync
    existing = db.query(Score).filter(Score.year == target_year).first()
    if existing:
        return {"success": False, "message": f"Data untuk tahun {target_year} sudah ada di database."}

    prev_year = target_year - 1
    processed = 0

    for r in regions:
        # Ambil data tahun sebelumnya
        prev_demo = db.query(Demographic).filter(Demographic.region_id == r.id, Demographic.year == prev_year).first()
        prev_econ = db.query(Economy).filter(Economy.region_id == r.id, Economy.year == prev_year).first()
        prev_prop = db.query(PropertyMarket).filter(PropertyMarket.region_id == r.id, PropertyMarket.year == prev_year).first()

        # 1. Demographics Projection
        if prev_demo:
            pop_growth = simulate_growth_rate(prev_demo.population_growth_pct, 0.2)
            new_pop = int(prev_demo.population * (1 + (pop_growth / 100)))
            new_density = round(new_pop / r.area_km2, 1) if r.area_km2 else prev_demo.density_per_km2
            
            db.add(Demographic(
                region_id=r.id,
                year=target_year,
                population=new_pop,
                population_growth_pct=pop_growth,
                density_per_km2=new_density,
                productive_age_count=int(new_pop * 0.67), # Asumsi rasio stabil
                household_count=int(new_pop / 3.8),
                urbanization_rate=min(100.0, prev_demo.urbanization_rate + random.uniform(0.1, 0.5))
            ))

        # 2. Economy Projection
        if prev_econ:
            econ_growth = simulate_growth_rate(prev_econ.economic_growth_pct, 1.5)
            # PDRB grows by economic growth + small inflation factor
            new_pdrb = round(prev_econ.pdrb_billion_idr * (1 + ((econ_growth + 2.0) / 100)), 2)
            
            # Recalculate per capita based on new pop
            new_per_capita = round((new_pdrb * 1000000000) / new_pop, 2) if 'new_pop' in locals() else prev_econ.pdrb_per_capita
            
            db.add(Economy(
                region_id=r.id,
                year=target_year,
                pdrb_billion_idr=new_pdrb,
                economic_growth_pct=econ_growth,
                pdrb_per_capita=new_per_capita,
                unemployment_rate=max(3.0, simulate_growth_rate(prev_econ.unemployment_rate, 0.5)),
                poverty_rate=max(2.0, simulate_growth_rate(prev_econ.poverty_rate, 0.3)),
                minimum_wage_idr=round(prev_econ.minimum_wage_idr * (1 + (random.uniform(3.0, 7.0) / 100)), 0)
            ))

        # 3. Property Market Projection
        if prev_prop:
            prop_growth = simulate_growth_rate(prev_prop.property_price_growth_pct, 2.0)
            new_land_price = round(prev_prop.avg_land_price_per_m2 * (1 + (prop_growth / 100)), 0)
            new_house_price = round(prev_prop.avg_house_price * (1 + (prop_growth / 100)), 0)
            
            db.add(PropertyMarket(
                region_id=r.id,
                year=target_year,
                avg_land_price_per_m2=new_land_price,
                avg_house_price=new_house_price,
                property_price_growth_pct=prop_growth,
                listing_count=int(prev_prop.listing_count * random.uniform(0.95, 1.15)),
                affordability_score=prev_prop.affordability_score, # Dianggap stabil kecuali gaji naik drastis
                data_source="Simulated AI Growth Engine (Fallback)"
            ))

        processed += 1

    db.commit()

    # Setelah data tersimpan, jalankan kalkulasi skor untuk tahun baru
    recalculate_all_scores(db, target_year)

    return {
        "success": True, 
        "message": f"Sinkronisasi berhasil! Data proyeksi untuk {processed} wilayah pada tahun {target_year} telah digenerate dan di-skoring ulang."
    }
