"""
Generate a realistic sample industrial RFQ PDF for testing Loonar.
Run: python generate_sample_rfq.py
Output: sample_rfq_shell_lng.pdf
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate():
    pdf = SimpleDocTemplate(
        "sample_rfq_shell_lng.pdf",
        pagesize=A4,
        topMargin=20*mm, bottomMargin=20*mm,
        leftMargin=25*mm, rightMargin=25*mm,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=14, spaceAfter=6)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, spaceAfter=4, textColor=colors.HexColor("#1a3a5c"))
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9, spaceAfter=4, leading=14)
    bold = ParagraphStyle("bold", parent=body, fontName="Helvetica-Bold")
    small = ParagraphStyle("small", parent=body, fontSize=8, textColor=colors.grey)

    story = []

    # ── Cover ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph("SHELL GLOBAL SOLUTIONS B.V.", ParagraphStyle("cover_co", parent=styles["Normal"], fontSize=11, fontName="Helvetica-Bold", alignment=TA_CENTER)))
    story.append(Paragraph("LNG Terminal Expansion — Maasvlakte II", ParagraphStyle("cover_title", parent=styles["Normal"], fontSize=16, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph("REQUEST FOR QUOTATION", ParagraphStyle("cover_sub", parent=styles["Normal"], fontSize=13, alignment=TA_CENTER, textColor=colors.HexColor("#c0392b"), spaceAfter=2)))
    story.append(Paragraph("Document No: SH-RFQ-2024-LNG-0047 | Rev: B | Date: 2024-11-15", ParagraphStyle("cover_ref", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=2)))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 6*mm))

    meta = [
        ["Project", "LNG Terminal Expansion — Maasvlakte II, Rotterdam"],
        ["Client", "Shell Global Solutions B.V."],
        ["Contract Ref", "SH-2024-LNG-EPC-001"],
        ["Commodity", "On/Off Gate Valves, Globe Valves, Check Valves — Cryogenic Service"],
        ["Quantity", "142 valves (see attached MTO)"],
        ["Bid Deadline", "2024-12-10 17:00 CET"],
        ["Delivery Required", "2025-06-30 (critical path item)"],
        ["Incoterms", "DAP Rotterdam (Maasvlakte II)"],
        ["Currency", "EUR"],
    ]
    t = Table(meta, colWidths=[55*mm, 115*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#eaf0fb")),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 8*mm))

    # ── Section 1: Scope ────────────────────────────────────────────────────
    story.append(Paragraph("1. SCOPE OF SUPPLY", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("1.1  This RFQ covers the design, manufacture, inspection, testing, and delivery of cryogenic valves for the Shell Maasvlakte II LNG import terminal expansion. All valves shall be suitable for continuous operation in liquefied natural gas (LNG) service at temperatures down to -196°C.", body))
    story.append(Paragraph("1.2  The scope includes the following valve types:", body))
    scope_items = [
        ["Tag Range", "Type", "Size", "Rating", "Qty"],
        ["10-GV-001 to 040", "Gate Valve (slab, full bore)", "2\" – 24\"", "ASME Class 300", "40"],
        ["10-GV-041 to 080", "Gate Valve (slab, full bore)", "26\" – 48\"", "ASME Class 150", "40"],
        ["10-GLV-001 to 022", "Globe Valve (angle pattern)", "1\" – 6\"", "ASME Class 600", "22"],
        ["10-CV-001 to 040", "Check Valve (tilting disc)", "4\" – 36\"", "ASME Class 150/300", "40"],
    ]
    t2 = Table(scope_items, colWidths=[45*mm, 55*mm, 25*mm, 30*mm, 15*mm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a3a5c")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f5f8ff")]),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(t2)
    story.append(Spacer(1, 6*mm))

    # ── Section 2: Material Requirements ───────────────────────────────────
    story.append(Paragraph("2. MATERIAL REQUIREMENTS", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("2.1  Body & Bonnet", h2))
    story.append(Paragraph("All valve bodies and bonnets shall be manufactured from ASTM A351 Grade CF8M (316L equivalent) austenitic stainless steel. Alternative: ASTM A182 Grade F316L for forged construction. Carbon steel bodies are NOT acceptable for any service in this specification.", body))

    story.append(Paragraph("2.2  Trim Materials", h2))
    story.append(Paragraph("Stems shall be ASTM A276 Type 316L. Seats and discs shall be Stellite 6 hardfaced on 316L SS substrate. For gate valves in sizes ≥12\", integral Stellite seat rings are mandatory — weld overlay is not acceptable.", body))

    story.append(Paragraph("2.3  Bolting", h2))
    story.append(Paragraph("All pressure-retaining bolting shall be ASTM A193 Grade B8M (Class 2) studs with ASTM A194 Grade 8M heavy hex nuts. Low-temperature bolting per ASME B31.3 Table A-2 is mandatory. Carbon steel bolting (Grade B7/2H) is expressly prohibited.", body))

    story.append(Paragraph("2.4  Sealing / Packing", h2))
    story.append(Paragraph("Valve packing shall be flexible graphite (Grafoil or equal) rated to -196°C. PTFE packing is acceptable only for globe valves ≤2\" in utility service. Asbestos-containing materials are strictly prohibited.", body))
    story.append(Spacer(1, 6*mm))

    # ── Section 3: Design Standards ─────────────────────────────────────────
    story.append(Paragraph("3. APPLICABLE STANDARDS & CODES", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("3.1  All valves shall be designed, manufactured, and tested in strict accordance with the following standards (latest edition unless noted):", body))

    standards = [
        ["Standard", "Title", "Applicability"],
        ["ASME B16.34", "Valves — Flanged, Threaded and Welding End", "All valves — mandatory"],
        ["API 598", "Valve Inspection and Testing", "All valves — mandatory"],
        ["API 600", "Bolted Bonnet Steel Gate Valves", "Gate valves ≥2\""],
        ["API 623", "Steel Globe Valves", "Globe valves"],
        ["ASME B16.5", "Pipe Flanges and Flanged Fittings", "Flange dimensions"],
        ["BS 6364", "Valves for Cryogenic Service", "Mandatory for all LNG service"],
        ["Shell DEP 80.30.00.19-Gen", "Valves for Cryogenic and Low Temperature", "Supersedes where more stringent"],
        ["NACE MR0103", "Materials Resistant to Sulfide Stress Cracking", "Applicable if H2S >50 ppmv"],
        ["PED 2014/68/EU", "Pressure Equipment Directive", "CE marking mandatory"],
        ["ISO 9001:2015", "Quality Management Systems", "QMS certification required"],
    ]
    t3 = Table(standards, colWidths=[40*mm, 80*mm, 50*mm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a3a5c")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f5f8ff")]),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(t3)
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("3.2  In case of conflict between standards, the more stringent requirement shall apply. Shell DEP takes precedence over API/ASME where more restrictive.", body))
    story.append(Spacer(1, 6*mm))

    # ── Section 4: Testing ──────────────────────────────────────────────────
    story.append(Paragraph("4. INSPECTION & TESTING REQUIREMENTS", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("4.1  Mandatory Testing", h2))
    tests = [
        ["Test", "Standard", "Acceptance", "Witness"],
        ["Shell hydrostatic test (1.5× MAOP)", "API 598 / ASME B16.34", "Zero leakage", "Shell TPA mandatory"],
        ["Seat leakage test — liquid nitrogen", "BS 6364 §8.3", "Class A (zero leakage)", "Shell TPA mandatory"],
        ["Cryogenic function test (-196°C)", "BS 6364 §8.4", "Full stroke, zero binding", "Shell TPA mandatory"],
        ["NDE — Radiography (RT) of castings", "ASME B16.34 App. A", "Level 2 acceptance", "Cert review"],
        ["NDE — Liquid Penetrant (LPT) of welds", "ASME V / VIII", "Linear indications = reject", "Cert review"],
        ["PMI (Positive Material Identification)", "Shell DEP", "100% of wetted parts", "Shell TPA mandatory"],
        ["Hardness testing of trim", "NACE MR0103", "≤22 HRC", "Cert review"],
        ["Fugitive emissions test", "ISO 15848-1", "Class AH, Tightness B", "Shell TPA mandatory"],
    ]
    t4 = Table(tests, colWidths=[50*mm, 35*mm, 45*mm, 40*mm])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#c0392b")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fff5f5")]),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(t4)
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("4.2  All test certificates shall be EN 10204 Type 3.2 (dual-certified by manufacturer and Shell-appointed TPA). Type 3.1 certificates are NOT acceptable for pressure-retaining parts.", body))
    story.append(Paragraph("4.3  Shell reserves the right to conduct unannounced shop visits at any stage of manufacture. 14 days written notice is required prior to any witness test.", body))
    story.append(Spacer(1, 6*mm))

    # ── Section 5: Commercial ───────────────────────────────────────────────
    story.append(Paragraph("5. COMMERCIAL REQUIREMENTS", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("5.1  Payment Terms: Net 60 days from invoice date. Payment milestone: 30% on order placement, 60% on FAT completion, 10% on delivery.", body))
    story.append(Paragraph("5.2  Warranty: 24 months from date of commissioning or 30 months from date of delivery, whichever is earlier. Extended warranty to 36 months is preferred and will be evaluated in bid scoring.", body))
    story.append(Paragraph("5.3  Liquidated Damages: 0.5% of order value per week of delay, capped at 10% of total contract value.", body))
    story.append(Paragraph("5.4  Spare Parts: Quotation shall include a recommended 2-year operational spares list. Commissioning spares to be included in base scope at no extra cost.", body))
    story.append(Paragraph("5.5  Lead Time: Maximum acceptable lead time is 22 weeks from purchase order to delivery Rotterdam. Bids exceeding 26 weeks will be disqualified.", body))
    story.append(Spacer(1, 6*mm))

    # ── Section 6: Documentation ────────────────────────────────────────────
    story.append(Paragraph("6. DOCUMENTATION REQUIREMENTS", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("6.1  The following documentation shall be submitted with the bid:", body))
    for doc in [
        "Technical data sheets for each valve type",
        "Compliance matrix against this specification (clause-by-clause)",
        "List of deviations and exceptions (mandatory — nil return if none)",
        "Quality plan / ITP (Inspection and Test Plan)",
        "CV and certifications of proposed Responsible Welding Coordinator",
        "Sample EN 10204 3.2 material certificates for reference order",
        "Current ISO 9001:2015 certificate",
        "List of three reference projects for LNG cryogenic valves (last 5 years)",
    ]:
        story.append(Paragraph(f"• {doc}", ParagraphStyle("bullet", parent=body, leftIndent=10)))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("6.2  Post-order documentation shall be submitted in English in PDF format via Shell's supplier portal (SIIS). Native CAD files (DWG/STEP) are required for custom items.", body))
    story.append(Spacer(1, 6*mm))

    # ── Section 7: Contradictions (intentional) ─────────────────────────────
    story.append(Paragraph("7. SPECIAL TECHNICAL NOTES", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("7.1  Fire-safe design per API 607 is required for all gate and globe valves. Note: Section 2.4 permits PTFE packing for small bore globe valves — vendors must confirm PTFE packing is acceptable for fire-safe certification or propose alternative.", body))
    story.append(Paragraph("7.2  All valve actuators shall be pneumatic (spring-return, fail-closed). Electric actuators may be proposed as an alternative for sizes ≤4\" where pneumatic supply is unavailable.", body))
    story.append(Paragraph("7.3  Flange facing: RF (Raised Face) per ASME B16.5 for Class 150/300. Note: cryogenic service per BS 6364 recommends RTJ facing for Class 300 and above — vendor to advise preferred facing for LNG service.", body))
    story.append(Paragraph("7.4  Maximum allowable packing emission per ISO 15848-1 is Class AH. However, Section 4.1 test requirement references Class BH acceptance — vendor to clarify which class applies and confirm test capability.", body))
    story.append(Spacer(1, 6*mm))

    # ── Footer note ─────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("CONFIDENTIAL — This document contains proprietary information of Shell Global Solutions B.V. Distribution to third parties is prohibited without written consent. Document No: SH-RFQ-2024-LNG-0047 Rev B", small))

    pdf.build(story)
    print("Generated: sample_rfq_shell_lng.pdf")

if __name__ == "__main__":
    generate()
