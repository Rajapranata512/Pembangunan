"""
scoring.py — Scoring Engine sesuai PRD bagian 11.
Menghitung 4 skor kategori + Final Opportunity Score menggunakan
Min-Max Normalisasi untuk seluruh wilayah Pulau Jawa.
"""
import datetime
from sqlalchemy.orm import Session
from models import Region, Score


def _min_max(value: float, min_val: float, max_val: float) -> float:
    """Normalisasi Min-Max ke skala 0-100."""
    if max_val == min_val:
        return 50.0
    return max(0.0, min(100.0, ((value - min_val) / (max_val - min_val)) * 100))


def _safe(val, default=0.0):
    """Return default jika val None."""
    return val if val is not None else default


def _collect_indicators(regions: list[Region]) -> list[dict]:
    """
    Kumpulkan semua indikator mentah per wilayah menjadi dict flat.
    Mengambil data tahun terbaru yang tersedia.
    """
    rows = []
    for r in regions:
        # Demografi terbaru
        demo = sorted(r.demographics, key=lambda d: d.year, reverse=True)
        d = demo[0] if demo else None

        # Ekonomi terbaru
        econ = sorted(r.economies, key=lambda e: e.year, reverse=True)
        e = econ[0] if econ else None

        # Infrastruktur (one-to-one)
        infra = r.infrastructure

        # Properti terbaru
        prop = sorted(r.property_markets, key=lambda p: p.year, reverse=True)
        p = prop[0] if prop else None

        # Fasilitas (one-to-one)
        fac = r.facility

        # Kawasan Strategis (one-to-one)
        strat = r.strategic_area

        # Development plans — hitung impact rata-rata
        plans = r.development_plans
        avg_plan_impact = (
            sum(_safe(pl.impact_score) for pl in plans) / len(plans)
            if plans else 0.0
        )

        row = {
            "region_id": r.id,
            # --- Business Potential ---
            "population": _safe(d.population if d else None),
            "pdrb_per_capita": _safe(e.pdrb_per_capita if e else None),
            "density": _safe(d.density_per_km2 if d else None),
            "accessibility_score": _safe(infra.infrastructure_composite_score if infra else None),
            "facilities_score": _safe(fac.facilities_composite_score if fac else None),
            "economic_growth": _safe(e.economic_growth_pct if e else None),
            # --- Property Investment ---
            "infra_score": _safe(infra.infrastructure_composite_score if infra else None),
            "pop_growth": _safe(d.population_growth_pct if d else None),
            "econ_growth": _safe(e.economic_growth_pct if e else None),
            "affordability": _safe(p.affordability_score if p else None),
            "plan_impact": avg_plan_impact,
            # --- Regional Growth ---
            "strategic_score": _safe(strat.strategic_score if strat else None),
            # --- Investment Risk ---
            "avg_land_price": _safe(p.avg_land_price_per_m2 if p else None),
            "unemployment": _safe(e.unemployment_rate if e else None),
            "poverty": _safe(e.poverty_rate if e else None),
            # --- Completeness tracking ---
            "data_points_filled": sum([
                d is not None, e is not None, infra is not None,
                p is not None, fac is not None, strat is not None,
            ]),
        }
        rows.append(row)
    return rows


def _normalize_all(rows: list[dict], keys: list[str]) -> dict[str, tuple[float, float]]:
    """Hitung min/max per indikator untuk normalisasi."""
    bounds = {}
    for key in keys:
        values = [r[key] for r in rows if r[key] is not None]
        if values:
            bounds[key] = (min(values), max(values))
        else:
            bounds[key] = (0.0, 0.0)
    return bounds


def _calc_business_score(row: dict, bounds: dict) -> float:
    """
    Business Potential Score (PRD 11.1):
    Penduduk 20% + PDRB/kapita 20% + Kepadatan 15% +
    Aksesibilitas 15% + Fasilitas 15% + Pertumbuhan Ekonomi 15%
    """
    scores = [
        _min_max(row["population"],         *bounds["population"])         * 0.20,
        _min_max(row["pdrb_per_capita"],     *bounds["pdrb_per_capita"])     * 0.20,
        _min_max(row["density"],            *bounds["density"])            * 0.15,
        _min_max(row["accessibility_score"], *bounds["accessibility_score"]) * 0.15,
        _min_max(row["facilities_score"],    *bounds["facilities_score"])    * 0.15,
        _min_max(row["economic_growth"],     *bounds["economic_growth"])     * 0.15,
    ]
    return sum(scores)


def _calc_property_score(row: dict, bounds: dict) -> float:
    """
    Property Investment Score (PRD 11.2):
    Infrastruktur 25% + Penduduk YoY 20% + Ekonomi YoY 20% +
    Keterjangkauan 15% + Fasilitas 10% + Rencana Pembangunan 10%
    """
    scores = [
        _min_max(row["infra_score"],     *bounds["infra_score"])     * 0.25,
        _min_max(row["pop_growth"],      *bounds["pop_growth"])      * 0.20,
        _min_max(row["econ_growth"],     *bounds["econ_growth"])     * 0.20,
        _min_max(row["affordability"],   *bounds["affordability"])   * 0.15,
        _min_max(row["facilities_score"], *bounds["facilities_score"]) * 0.10,
        _min_max(row["plan_impact"],     *bounds["plan_impact"])     * 0.10,
    ]
    return sum(scores)


def _calc_growth_score(row: dict, bounds: dict) -> float:
    """
    Regional Growth Score (PRD 11.3):
    Ekonomi YoY 25% + Penduduk YoY 20% + Infra Baru 20% +
    Kawasan Industri/KEK 15% + Rencana Strategis 10% + Fasilitas 10%
    """
    scores = [
        _min_max(row["econ_growth"],     *bounds["econ_growth"])     * 0.25,
        _min_max(row["pop_growth"],      *bounds["pop_growth"])      * 0.20,
        _min_max(row["plan_impact"],     *bounds["plan_impact"])     * 0.20,
        _min_max(row["strategic_score"], *bounds["strategic_score"]) * 0.15,
        _min_max(row["plan_impact"],     *bounds["plan_impact"])     * 0.10,
        _min_max(row["facilities_score"], *bounds["facilities_score"]) * 0.10,
    ]
    return sum(scores)


def _calc_risk_score(row: dict, bounds: dict) -> float:
    """
    Investment Risk Score (PRD 11.4):
    Harga Overvalued 25% + Ekonomi Stagnan 20% + Penduduk Negatif 15% +
    Akses Terbatas 15% + Monosektor 10% + Pengangguran 10%

    Note: Skor TINGGI = risiko LEBIH BESAR.
    Untuk indikator 'baik' (ekonomi tinggi, infra tinggi), kita inversi.
    """
    # Harga tinggi = risiko tinggi (langsung)
    price_risk = _min_max(row["avg_land_price"], *bounds["avg_land_price"])

    # Ekonomi rendah = risiko tinggi (inversi: 100 - normalized)
    econ_risk = 100 - _min_max(row["economic_growth"], *bounds["economic_growth"])

    # Pertumbuhan penduduk rendah = risiko tinggi (inversi)
    pop_risk = 100 - _min_max(row["pop_growth"], *bounds["pop_growth"])

    # Infra rendah = risiko tinggi (inversi)
    infra_risk = 100 - _min_max(row["infra_score"], *bounds["infra_score"])

    # Monosektor — approksimasi: pakai inversi strategic_score (makin rendah makin tergantung 1 sektor)
    mono_risk = 100 - _min_max(row["strategic_score"], *bounds["strategic_score"])

    # Pengangguran tinggi = risiko tinggi (langsung)
    unemp_risk = _min_max(row["unemployment"], *bounds["unemployment"])

    return (
        price_risk * 0.25
        + econ_risk * 0.20
        + pop_risk * 0.15
        + infra_risk * 0.15
        + mono_risk * 0.10
        + unemp_risk * 0.10
    )


def recalculate_all_scores(db: Session, year: int = 2024):
    """
    Hitung ulang seluruh skor untuk semua wilayah.
    Menghapus skor lama untuk tahun yang sama, lalu insert yang baru.

    Formula Final Score (PRD 11.5):
    Final = (Business × 30%) + (Property × 30%) + (Growth × 25%) + (100 − Risk) × 15%
    """
    regions = db.query(Region).all()
    if not regions:
        return

    rows = _collect_indicators(regions)

    # Kunci indikator yang perlu dinormalisasi
    indicator_keys = [
        "population", "pdrb_per_capita", "density", "accessibility_score",
        "facilities_score", "economic_growth", "infra_score", "pop_growth",
        "econ_growth", "affordability", "plan_impact", "strategic_score",
        "avg_land_price", "unemployment", "poverty",
    ]
    bounds = _normalize_all(rows, indicator_keys)

    # Hapus skor lama untuk tahun ini
    db.query(Score).filter(Score.year == year).delete()

    for row in rows:
        biz = round(_calc_business_score(row, bounds), 2)
        prop = round(_calc_property_score(row, bounds), 2)
        growth = round(_calc_growth_score(row, bounds), 2)
        risk = round(_calc_risk_score(row, bounds), 2)
        final = round(
            biz * 0.30 + prop * 0.30 + growth * 0.25 + (100 - risk) * 0.15,
            2,
        )

        completeness = round((row["data_points_filled"] / 6) * 100, 1)

        score = Score(
            region_id=row["region_id"],
            year=year,
            business_score=biz,
            property_score=prop,
            growth_score=growth,
            risk_score=risk,
            final_score=final,
            data_completeness_pct=completeness,
            calculated_at=datetime.datetime.utcnow(),
        )
        db.add(score)

    db.commit()
    print(f"[Scoring] Skor dihitung untuk {len(rows)} wilayah (tahun {year}).")
