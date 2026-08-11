"""
pdf_generator.py — Generate professional PDF investment reports per region.
Uses reportlab for PDF generation with ProspekJawa branding.
"""
import io
import json
import datetime
from typing import Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.units import mm, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak,
    )
    from reportlab.pdfbase import pdfmetrics
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("[PDF] WARNING: reportlab not installed. PDF generation disabled.")


# ──────────────────────────────────────────────
# Color Palette (matches frontend dark theme)
# ──────────────────────────────────────────────
COLOR_PRIMARY = HexColor("#3b82f6") if REPORTLAB_AVAILABLE else None
COLOR_PURPLE = HexColor("#8b5cf6") if REPORTLAB_AVAILABLE else None
COLOR_BG_DARK = HexColor("#0f172a") if REPORTLAB_AVAILABLE else None
COLOR_BG_CARD = HexColor("#1e293b") if REPORTLAB_AVAILABLE else None
COLOR_TEXT = HexColor("#f1f5f9") if REPORTLAB_AVAILABLE else None
COLOR_MUTED = HexColor("#94a3b8") if REPORTLAB_AVAILABLE else None
COLOR_GREEN = HexColor("#22c55e") if REPORTLAB_AVAILABLE else None
COLOR_RED = HexColor("#ef4444") if REPORTLAB_AVAILABLE else None
COLOR_YELLOW = HexColor("#eab308") if REPORTLAB_AVAILABLE else None


def _score_color(score: Optional[float]):
    """Get color based on score value."""
    if score is None:
        return COLOR_MUTED
    if score >= 80:
        return COLOR_GREEN
    if score >= 60:
        return COLOR_PRIMARY
    if score >= 40:
        return COLOR_YELLOW
    return COLOR_RED


def _score_label(score: Optional[float]) -> str:
    if score is None:
        return "N/A"
    if score >= 80:
        return "Sangat Potensial"
    if score >= 60:
        return "Potensial"
    if score >= 40:
        return "Moderat"
    if score >= 20:
        return "Terbatas"
    return "Kurang Menarik"


def _fmt_num(val, prefix="", suffix="", decimals=0):
    """Format number with thousand separators."""
    if val is None:
        return "-"
    if decimals > 0:
        formatted = f"{val:,.{decimals}f}"
    else:
        formatted = f"{val:,.0f}"
    return f"{prefix}{formatted}{suffix}"


def generate_pdf_report(
    region_data: dict,
    ai_narrative: str = "",
    insight_data: dict = None,
) -> Optional[bytes]:
    """
    Generate a professional PDF report for a region.

    Args:
        region_data: Dict containing all region information
        ai_narrative: AI-generated executive summary text
        insight_data: Dict with key_strengths, key_risks, best_for

    Returns:
        PDF file as bytes, or None if reportlab not available
    """
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )

    # ── Styles ──
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=24, textColor=HexColor("#1e293b"),
        spaceAfter=6, fontName='Helvetica-Bold',
    )
    style_subtitle = ParagraphStyle(
        'CustomSubtitle', parent=styles['Normal'],
        fontSize=12, textColor=HexColor("#64748b"),
        spaceAfter=20,
    )
    style_heading = ParagraphStyle(
        'CustomHeading', parent=styles['Heading2'],
        fontSize=14, textColor=HexColor("#3b82f6"),
        spaceBefore=16, spaceAfter=8, fontName='Helvetica-Bold',
    )
    style_body = ParagraphStyle(
        'CustomBody', parent=styles['Normal'],
        fontSize=10, textColor=HexColor("#334155"),
        leading=16, alignment=TA_JUSTIFY, spaceAfter=8,
    )
    style_small = ParagraphStyle(
        'SmallText', parent=styles['Normal'],
        fontSize=8, textColor=HexColor("#94a3b8"),
    )
    style_tag = ParagraphStyle(
        'TagStyle', parent=styles['Normal'],
        fontSize=9, textColor=HexColor("#3b82f6"),
    )

    elements = []

    # ── HEADER ──
    name = region_data.get("name", "Wilayah")
    province = region_data.get("province", "")
    region_type = region_data.get("region_type", "")

    elements.append(Paragraph("LAPORAN ANALISIS PROSPEK INVESTASI", style_small))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(name, style_title))
    elements.append(Paragraph(
        f"{province} &bull; {region_type.title()} &bull; "
        f"Luas: {_fmt_num(region_data.get('area_km2'))} km&sup2;",
        style_subtitle,
    ))

    # Separator
    elements.append(HRFlowable(
        width="100%", thickness=2, color=COLOR_PRIMARY,
        spaceBefore=4, spaceAfter=12,
    ))

    # ── SCORE SUMMARY TABLE ──
    elements.append(Paragraph("Ringkasan Skor", style_heading))

    scores = [
        ("Business", region_data.get("business_score")),
        ("Property", region_data.get("property_score")),
        ("Growth", region_data.get("growth_score")),
        ("Risk", region_data.get("risk_score")),
        ("FINAL", region_data.get("final_score")),
    ]

    score_data = [["Kategori", "Skor", "Rating"]]
    for label, val in scores:
        rating = _score_label(val)
        score_str = f"{val:.1f}" if val is not None else "N/A"
        score_data.append([label, score_str, rating])

    score_table = Table(score_data, colWidths=[120, 80, 120])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#3b82f6")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor("#f8fafc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#f8fafc"), HexColor("#f1f5f9")]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        # Bold the FINAL row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor("#eff6ff")),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 10 * mm))

    # ── AI EXECUTIVE SUMMARY ──
    if ai_narrative:
        elements.append(Paragraph("Executive Summary (AI Analysis)", style_heading))
        # Split by newlines and add as paragraphs
        for para in ai_narrative.split("\n"):
            para = para.strip()
            if para:
                elements.append(Paragraph(para, style_body))
        elements.append(Spacer(1, 6 * mm))

    # ── KEY INSIGHTS ──
    if insight_data:
        strengths = insight_data.get("key_strengths", [])
        risks = insight_data.get("key_risks", [])
        best_for = insight_data.get("best_for", [])

        if strengths:
            elements.append(Paragraph("Kekuatan Utama", style_heading))
            for s in strengths:
                elements.append(Paragraph(f"&bull; {s}", style_body))

        if risks:
            elements.append(Paragraph("Risiko", style_heading))
            for r in risks:
                elements.append(Paragraph(f"&bull; {r}", style_body))

        if best_for:
            elements.append(Paragraph("Paling Cocok Untuk", style_heading))
            for b in best_for:
                elements.append(Paragraph(f"&bull; {b}", style_body))

        elements.append(Spacer(1, 6 * mm))

    # ── DATA TABLES ──
    elements.append(Paragraph("Data Detail Wilayah", style_heading))

    # Demographics
    demo_data = [
        ["Demografi", "Nilai"],
        ["Populasi", _fmt_num(region_data.get("population"), suffix=" jiwa")],
        ["Pertumbuhan Penduduk", _fmt_num(region_data.get("pop_growth"), suffix="%", decimals=2)],
        ["Kepadatan", _fmt_num(region_data.get("density"), suffix=" jiwa/km²")],
        ["Urbanisasi", _fmt_num(region_data.get("urbanization"), suffix="%", decimals=1)],
    ]

    # Economy
    econ_data = [
        ["Ekonomi", "Nilai"],
        ["PDRB", _fmt_num(region_data.get("pdrb"), prefix="Rp ", suffix=" miliar", decimals=1)],
        ["Pertumbuhan Ekonomi", _fmt_num(region_data.get("econ_growth"), suffix="%", decimals=2)],
        ["PDRB per Kapita", _fmt_num(region_data.get("pdrb_capita"), prefix="Rp ")],
        ["Pengangguran", _fmt_num(region_data.get("unemployment"), suffix="%", decimals=2)],
        ["Kemiskinan", _fmt_num(region_data.get("poverty"), suffix="%", decimals=2)],
        ["UMK", _fmt_num(region_data.get("umk"), prefix="Rp ")],
    ]

    # Property
    prop_data = [
        ["Properti", "Nilai"],
        ["Harga Tanah", _fmt_num(region_data.get("land_price"), prefix="Rp ", suffix="/m²")],
        ["Harga Rumah", _fmt_num(region_data.get("house_price"), prefix="Rp ")],
        ["Kenaikan Harga", _fmt_num(region_data.get("prop_growth"), suffix="%/tahun", decimals=1)],
        ["Keterjangkauan", _fmt_num(region_data.get("affordability"), suffix="/100")],
    ]

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1e293b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#f8fafc"), white]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ])

    for data_rows in [demo_data, econ_data, prop_data]:
        t = Table(data_rows, colWidths=[200, 260])
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(1, 4 * mm))

    # ── FOOTER ──
    elements.append(Spacer(1, 10 * mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor("#e2e8f0")))
    elements.append(Spacer(1, 4 * mm))
    now = datetime.datetime.now().strftime("%d %B %Y, %H:%M WIB")
    elements.append(Paragraph(
        f"Laporan dihasilkan oleh <b>ProspekJawa AI</b> pada {now}. "
        "Data bersumber dari BPS dan riset publik. "
        "Laporan ini bersifat informasional dan bukan merupakan saran investasi profesional.",
        style_small,
    ))

    # Build PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
