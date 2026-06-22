"""Generate a sample pump RFQ PDF - clearly different from the valve/LNG one."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

def generate():
    pdf = SimpleDocTemplate(
        "sample_rfq_pump_bp.pdf",
        pagesize=A4,
        topMargin=20*mm, bottomMargin=20*mm,
        leftMargin=25*mm, rightMargin=25*mm,
    )
    styles = getSampleStyleSheet()
    h1  = ParagraphStyle("h1",  parent=styles["Heading1"], fontSize=13, spaceAfter=5)
    h2  = ParagraphStyle("h2",  parent=styles["Heading2"], fontSize=10, spaceAfter=4, textColor=colors.HexColor("#7b2d00"))
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9, spaceAfter=4, leading=14)
    small = ParagraphStyle("small", parent=body, fontSize=8, textColor=colors.grey)

    story = []

    # Cover
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("BP EXPLORATION OPERATING COMPANY LTD", ParagraphStyle("co", parent=styles["Normal"], fontSize=11, fontName="Helvetica-Bold", alignment=TA_CENTER)))
    story.append(Paragraph("North Sea Decommissioning — Forties Pipeline System", ParagraphStyle("title", parent=styles["Normal"], fontSize=15, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=3)))
    story.append(Paragraph("REQUEST FOR QUOTATION — CENTRIFUGAL PUMP PACKAGES", ParagraphStyle("sub", parent=styles["Normal"], fontSize=12, alignment=TA_CENTER, textColor=colors.HexColor("#c0392b"), spaceAfter=2)))
    story.append(Paragraph("Doc No: BP-RFQ-2024-FPS-0112 | Rev: A | Date: 2024-10-01", ParagraphStyle("ref", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#7b2d00")))
    story.append(Spacer(1, 5*mm))

    meta = [
        ["Project",     "Forties Pipeline System — Decommissioning Phase 2"],
        ["Client",      "BP Exploration Operating Company Ltd"],
        ["Commodity",   "API 610 Centrifugal Pump Packages (OH2, BB3 types)"],
        ["Quantity",    "18 pump packages (see MTO attached)"],
        ["Bid Deadline","2024-11-15 14:00 GMT"],
        ["Delivery",    "2025-09-01 — Aberdeen Quayside"],
        ["Incoterms",   "DDP Aberdeen"],
        ["Currency",    "GBP"],
    ]
    t = Table(meta, colWidths=[45*mm, 125*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#fdf0e8")),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 6*mm))

    # Section 1
    story.append(Paragraph("1. SCOPE OF SUPPLY", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7b2d00")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("1.1  This RFQ covers the supply of 18 centrifugal pump packages for crude oil transfer service on the Forties Pipeline System decommissioning project. All pumps shall be suitable for continuous offshore duty in a Zone 1 classified hazardous area.", body))

    scope = [
        ["Tag", "Type", "Duty", "Flow (m3/h)", "Head (m)", "Qty"],
        ["10-P-001/002", "OH2 (overhung, between bearing)", "Crude transfer primary", "850", "380", "4"],
        ["10-P-003/004", "OH2", "Crude transfer secondary", "420", "220", "4"],
        ["10-P-005/008", "BB3 (between bearing, double suction)", "Pipeline booster", "2400", "560", "4"],
        ["10-P-009/012", "BB3", "Seawater injection", "1800", "720", "4"],
        ["10-P-013/018", "OH2", "Chemical dosing", "45",  "180", "2"],
    ]
    t2 = Table(scope, colWidths=[32*mm, 50*mm, 40*mm, 22*mm, 18*mm, 10*mm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#7b2d00")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fff8f5")]),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(t2)
    story.append(Spacer(1, 6*mm))

    # Section 2 - Materials
    story.append(Paragraph("2. MATERIAL REQUIREMENTS", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7b2d00")))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("2.1  Casing & Cover", h2))
    story.append(Paragraph("Pump casings shall be ASTM A216 Grade WCB carbon steel for crude service. Seawater injection pumps (10-P-009 to 012) SHALL use Super Duplex 2507 (UNS S32750) casings. Note: Section 6.3 of this specification references carbon steel casings for all pump types — vendors must clarify which material applies to seawater pumps.", body))

    story.append(Paragraph("2.2  Impeller", h2))
    story.append(Paragraph("Impellers for crude service: ASTM A351 CF8M (316 SS). Seawater service impellers: Super Duplex 2507. Impeller trim shall not exceed 95% of maximum diameter. Closed impellers are mandatory for all BB3 type pumps.", body))

    story.append(Paragraph("2.3  Shaft", h2))
    story.append(Paragraph("Pump shafts shall be AISI 4140 alloy steel, heat treated to minimum 28 HRC. Maximum shaft deflection at seal faces shall not exceed 0.05 mm under any operating condition. Duplex stainless steel shafts (UNS S31803) are required for seawater injection service.", body))

    story.append(Paragraph("2.4  Mechanical Seal", h2))
    story.append(Paragraph("Mechanical seals shall be Plan 11 (API 682) as minimum for crude service. Seawater injection pumps require Plan 32 (external flush) with a dedicated clean water supply. Seal faces: Silicon Carbide vs Silicon Carbide for abrasive service, Carbon vs Silicon Carbide for clean service.", body))
    story.append(Spacer(1, 6*mm))

    # Section 3 - Standards
    story.append(Paragraph("3. APPLICABLE STANDARDS", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7b2d00")))
    story.append(Spacer(1, 3*mm))

    standards = [
        ["Standard", "Description", "Applicability"],
        ["API 610 (12th Ed)", "Centrifugal Pumps for Petroleum Industry", "All pumps — mandatory"],
        ["API 682 (4th Ed)", "Pumps — Shaft Sealing Systems", "Mechanical seals — mandatory"],
        ["API 670",          "Machinery Protection Systems", "All pumps >75 kW"],
        ["API 671",          "Special Purpose Couplings", "BB3 pumps only"],
        ["ATEX Directive 2014/34/EU", "Explosive Atmospheres Equipment", "Zone 1 — Ex d IIB T3"],
        ["NACE MR0175",      "Sour Service Materials", "If H2S detected in crude"],
        ["ISO 13709",        "Centrifugal Pumps — identical to API 610", "Alternative to API 610"],
        ["IEC 60034",        "Rotating Electrical Machines", "Drive motors"],
        ["BP GIS 32-301",    "BP Group Instruction for Rotating Equipment", "Supersedes where more stringent"],
    ]
    t3 = Table(standards, colWidths=[42*mm, 78*mm, 50*mm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#7b2d00")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fff8f5")]),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(t3)
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("3.1  ISO 13709 is technically identical to API 610 — vendors offering ISO 13709 compliance shall confirm equivalence in writing. Note: Section 7.2 mandates API 610 11th Edition, while this cover sheet references the 12th Edition — the 12th Edition shall take precedence.", body))
    story.append(Spacer(1, 6*mm))

    # Section 4 - Testing
    story.append(Paragraph("4. TESTING REQUIREMENTS", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7b2d00")))
    story.append(Spacer(1, 3*mm))

    tests = [
        ["Test", "Standard", "Acceptance Criteria", "Witness"],
        ["Hydraulic performance test", "API 610 §8.3.2", "Grade 1B tolerance", "BP TPA mandatory"],
        ["NPSH test", "API 610 §8.3.3", "3% head drop method", "BP TPA mandatory"],
        ["Mechanical running test (4hr)", "API 610 §8.3.4", "Vibration <4.5 mm/s RMS", "BP TPA mandatory"],
        ["Hydrostatic pressure test (1.5× MAWP)", "API 610 §8.2", "No leakage 30 min", "Cert review"],
        ["Complete unit test with motor", "API 610 §8.3.6", "Power within 3% predicted", "BP TPA mandatory"],
        ["Vibration analysis (FFT)", "API 670", "Sub-synchronous <25% of BEP flow", "BP TPA mandatory"],
        ["Noise level test", "ISO 3744", "Max 85 dB(A) at 1m", "Cert review"],
        ["ATEX verification", "IEC 60079-0", "Zone 1 Ex d IIB T3 Gc", "Notified body"],
    ]
    t4 = Table(tests, colWidths=[48*mm, 30*mm, 52*mm, 40*mm])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#c0392b")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fff8f5")]),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(t4)
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("4.1  Vibration acceptance: API 610 Table 9 limits apply. However BP GIS 32-301 Section 4.6 specifies a stricter limit of 3.5 mm/s RMS for offshore duty — the BP GIS limit shall govern. Vendors to confirm test rig capability.", body))
    story.append(Spacer(1, 6*mm))

    # Section 5 - Commercial
    story.append(Paragraph("5. COMMERCIAL TERMS", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7b2d00")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("5.1  Payment: 25% on order, 65% on FAT completion, 10% on delivery. Net 45 days from invoice.", body))
    story.append(Paragraph("5.2  Warranty: 24 months from commissioning or 30 months from delivery, whichever is earlier.", body))
    story.append(Paragraph("5.3  Liquidated Damages: 0.75% per week of delay, capped at 7.5% of contract value.", body))
    story.append(Paragraph("5.4  Lead time: Maximum 20 weeks. Bids exceeding 24 weeks delivery shall be rejected.", body))
    story.append(Paragraph("5.5  Spare parts: 2-year operational spares list mandatory. Commissioning spares included in base price.", body))
    story.append(Spacer(1, 6*mm))

    # Section 6 - Special notes with contradictions
    story.append(Paragraph("6. SPECIAL TECHNICAL REQUIREMENTS", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7b2d00")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("6.1  All pumps shall be supplied with API 610 12th Edition baseplate (Type A — grouted). Exception: chemical dosing pumps (10-P-013/018) may use Type C baseplates per vendor standard.", body))
    story.append(Paragraph("6.2  Coupling guard shall be fabricated from 316 SS. Non-sparking material required per ATEX Zone 1. Note: Section 3 specifies IIB gas group; offshore survey indicates IIC classification may apply — vendor to confirm gas group with BP hazardous area engineer before finalising.", body))
    story.append(Paragraph("6.3  Casings for all pump types shall be carbon steel per ASTM A216 WCB. [Note: contradicts Section 2.1 which mandates Super Duplex for seawater pumps — Super Duplex takes precedence for 10-P-009 to 012].", body))
    story.append(Paragraph("6.4  Driver: All pumps shall be driven by ATEX-certified electric motors (Ex d IIB T3). Variable speed drives (VFDs) are mandatory for all BB3 type pumps. VFD enclosure rating: IP55 minimum.", body))
    story.append(Spacer(1, 6*mm))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("CONFIDENTIAL — BP Exploration Operating Company Ltd. Doc: BP-RFQ-2024-FPS-0112 Rev A", small))

    pdf.build(story)
    print("Generated: sample_rfq_pump_bp.pdf")

if __name__ == "__main__":
    generate()
