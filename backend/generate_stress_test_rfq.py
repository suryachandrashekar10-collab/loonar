"""
Stress-test RFQ PDF — Saipem FPSO Topsides Package
Complex document: 12 pages, 4 disciplines, intentional contradictions,
mixed standards (ASME / API / NACE / ISO / IEC), ambiguous clauses.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUT = "stress_test_rfq_saipem_fpso.pdf"

def generate():
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()

    title_style   = ParagraphStyle('Title',   fontSize=14, fontName='Helvetica-Bold',   alignment=TA_CENTER, spaceAfter=4)
    sub_style     = ParagraphStyle('Sub',     fontSize=10, fontName='Helvetica',         alignment=TA_CENTER, spaceAfter=2, textColor=colors.HexColor('#555555'))
    h1_style      = ParagraphStyle('H1',      fontSize=11, fontName='Helvetica-Bold',   spaceBefore=10, spaceAfter=4, textColor=colors.HexColor('#1a3a5c'))
    h2_style      = ParagraphStyle('H2',      fontSize=10, fontName='Helvetica-Bold',   spaceBefore=6,  spaceAfter=3, textColor=colors.HexColor('#2d5986'))
    body_style    = ParagraphStyle('Body',    fontSize=9,  fontName='Helvetica',         spaceAfter=4,  leading=13, alignment=TA_JUSTIFY)
    clause_style  = ParagraphStyle('Clause',  fontSize=9,  fontName='Helvetica-Bold',   spaceAfter=2,  leftIndent=0)
    req_style     = ParagraphStyle('Req',     fontSize=9,  fontName='Helvetica',         spaceAfter=4,  leftIndent=10, leading=13, alignment=TA_JUSTIFY)
    note_style    = ParagraphStyle('Note',    fontSize=8,  fontName='Helvetica-Oblique', spaceAfter=4,  leftIndent=10, textColor=colors.HexColor('#cc6600'))
    warn_style    = ParagraphStyle('Warn',    fontSize=8,  fontName='Helvetica-Bold',   spaceAfter=4,  leftIndent=10, textColor=colors.HexColor('#cc0000'))

    story = []

    # ── Cover Page ──────────────────────────────────────────────────────────────
    story += [
        Spacer(1, 20*mm),
        Paragraph("SAIPEM S.p.A.", title_style),
        Paragraph("OFFSHORE BUSINESS UNIT", sub_style),
        Spacer(1, 8*mm),
        HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a3a5c')),
        Spacer(1, 6*mm),
        Paragraph("REQUEST FOR QUOTATION", ParagraphStyle('T2', fontSize=16, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4)),
        Paragraph("FPSO GIRASSOL PHASE II TOPSIDES — PROCESS & UTILITY PACKAGE", ParagraphStyle('T3', fontSize=12, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4, textColor=colors.HexColor('#1a3a5c'))),
        Spacer(1, 6*mm),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')),
        Spacer(1, 10*mm),
    ]

    meta = [
        ["Document Number:", "SAI-GRS2-RFQ-PROC-0047"],
        ["Project:",         "Girassol Phase II FPSO — Angola Block 17"],
        ["Client:",          "TotalEnergies Angola"],
        ["Revision:",        "C2 — Issued for Quotation"],
        ["Date:",            "15 March 2026"],
        ["Due Date:",        "30 April 2026 17:00 CET"],
        ["Confidentiality:", "COMMERCIAL IN CONFIDENCE"],
    ]
    t = Table(meta, colWidths=[55*mm, 110*mm])
    t.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor('#f0f4f8'), colors.white]),
        ('BOX',       (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#dddddd')),
        ('TOPPADDING',   (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0), (-1,-1), 4),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
    ]))
    story += [t, Spacer(1, 10*mm)]

    story.append(Paragraph(
        "This document contains proprietary and confidential information. Recipients shall not disclose, reproduce, "
        "or use this document except for the purposes of preparing a quotation in response to this RFQ. "
        "Unauthorized disclosure may result in legal action.", note_style))

    # ── Page 2: Scope of Supply ─────────────────────────────────────────────────
    story += [
        Spacer(1, 6*mm),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a3a5c')),
        Paragraph("1. SCOPE OF SUPPLY", h1_style),
        Paragraph("1.1 General", h2_style),
        Paragraph(
            "The Vendor shall supply, fabricate, test, and deliver the complete Process & Utility Package for the "
            "FPSO Girassol Phase II topsides as detailed herein. The scope includes but is not limited to: "
            "gas compression trains, produced water treatment skids, chemical injection packages, flare knockout drums, "
            "closed drain vessels, and all associated instrumentation, piping, structural, and electrical works.", body_style),

        Paragraph("1.2 Battery Limits", h2_style),
        Paragraph(
            "Vendor's scope commences at the first isolation valve downstream of the FPSO riser base and terminates "
            "at the first flange connection to the topsides main headers. Interconnecting piping between skids is "
            "included in Vendor scope. Export pipeline interface is excluded.", body_style),

        Paragraph("1.3 Exclusions", h2_style),
        Paragraph(
            "The following items are explicitly excluded from Vendor scope: (a) marine and hull structural works; "
            "(b) mooring and anchoring systems; (c) fire and gas detection main systems (although interface signals are required); "
            "(d) accommodation module fit-out.", body_style),

        Paragraph("2. APPLICABLE CODES AND STANDARDS", h1_style),
        Paragraph("2.1 Governing Standards", h2_style),
        Paragraph(
            "All equipment and materials shall comply with the latest edition of the following standards unless "
            "specific revision is stated. In cases of conflict, the more stringent requirement shall govern.", body_style),
    ]

    standards = [
        ["Standard", "Title", "Application"],
        ["ASME VIII Div.1", "Pressure Vessels", "All pressure vessels"],
        ["ASME VIII Div.2", "Alternative Rules — Pressure Vessels", "High-pressure vessels >100 barg"],
        ["ASME B31.3", "Process Piping", "All process piping"],
        ["API 617", "Axial and Centrifugal Compressors", "Gas compression trains"],
        ["API 610", "Centrifugal Pumps", "All centrifugal pumps"],
        ["API 670", "Machinery Protection Systems", "Rotating equipment"],
        ["NACE MR0175 / ISO 15156", "Sour Service Materials", "All wetted parts — H2S service"],
        ["NACE SP0169", "External Corrosion Control", "Subsea and splash zone"],
        ["IEC 60079", "Explosive Atmospheres", "All electrical equipment"],
        ["IEC 61511", "Functional Safety", "Safety instrumented systems"],
        ["ISO 13709", "Centrifugal Pumps (identical to API 610)", "Pumps — where referenced by client"],
        ["PED 2014/68/EU", "Pressure Equipment Directive", "CE marking requirement"],
    ]
    t2 = Table(standards, colWidths=[45*mm, 75*mm, 45*mm])
    t2.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTNAME',  (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 8),
        ('BACKGROUND',(0,0), (-1,0),  colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0,0), (-1,0),  colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f0f4f8'), colors.white]),
        ('BOX',       (0,0), (-1,-1), 0.5, colors.HexColor('#aaaaaa')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#cccccc')),
        ('TOPPADDING',   (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0), (-1,-1), 3),
        ('LEFTPADDING',  (0,0), (-1,-1), 4),
    ]))
    story += [t2, Spacer(1, 4*mm)]

    story.append(Paragraph(
        "NOTE: Where ISO 13709 and API 610 requirements conflict, API 610 shall take precedence. "
        "Vendor shall identify all deviations from the above standards in the deviation register "
        "submitted with the technical proposal.", note_style))

    # ── Page 3: Material Requirements ──────────────────────────────────────────
    story += [
        Paragraph("3. MATERIAL REQUIREMENTS", h1_style),
        Paragraph("3.1 General Material Philosophy", h2_style),
        Paragraph(
            "All pressure-containing components shall be fabricated from materials suitable for the design conditions "
            "specified in the process datasheets. Materials shall be selected to provide a minimum 25-year design life "
            "under the operating conditions defined herein.", body_style),

        Paragraph("3.2 Carbon Steel — Sweet Service", h2_style),
        Paragraph("3.2.1", clause_style),
        Paragraph(
            "For sweet service applications (H2S partial pressure <0.05 psia, CO2 partial pressure <30 psia), "
            "carbon steel ASTM A516 Grade 70 shall be used for vessel shells. Minimum Charpy impact energy: "
            "27J longitudinal at -20°C. PWHT is mandatory for all shell welds with thickness exceeding 32mm.", req_style),

        Paragraph("3.2.2", clause_style),
        Paragraph(
            "Carbon steel piping shall be ASTM A106 Grade B seamless for nominal diameters up to 16 inches. "
            "Above 16 inches, ASTM A672 Grade C70 electric-fusion-welded pipe is acceptable subject to "
            "100% radiographic examination of longitudinal seams.", req_style),

        Paragraph("3.3 Sour Service — H2S Environments", h2_style),
        Paragraph("3.3.1", clause_style),
        Paragraph(
            "All equipment in H2S partial pressure >0.05 psia service shall comply with NACE MR0175 / ISO 15156. "
            "This applies to all produced fluid service from wellhead through first-stage separation. "
            "Material certification to NACE MR0175 Part 2 is required for carbon steel components.", req_style),

        Paragraph("3.3.2 — CONTRADICTION ALERT", warn_style),
        Paragraph(
            "Valve body and trim materials for sour service shall be AISI 316L stainless steel with maximum "
            "hardness of HRC 22. HOWEVER — see clause 3.3.4 below which specifies duplex stainless steel "
            "UNS S31803 for the same service. Vendor shall seek clarification prior to submitting proposal.", req_style),

        Paragraph("3.3.3", clause_style),
        Paragraph(
            "Bolting for sour service flanged connections shall be ASTM A193 Grade B7M studs with ASTM A194 "
            "Grade 2HM heavy hex nuts. B7 / 2H bolting (non-M suffix) is NOT acceptable in H2S service "
            "regardless of partial pressure levels.", req_style),

        Paragraph("3.3.4", clause_style),
        Paragraph(
            "Valve bodies for produced fluid service shall be fabricated from duplex stainless steel UNS S31803 "
            "(2205) with minimum PREN of 35. This requirement supersedes any previous specification for austenitic "
            "stainless steel in the same service. Maximum ferrite content: 55% by volume.", req_style),

        Paragraph("3.4 Cladding and Overlay", h2_style),
        Paragraph("3.4.1", clause_style),
        Paragraph(
            "Vessel internals exposed to produced water with chloride content >5,000 ppm shall be weld-overlay "
            "clad with Alloy 625 (UNS N06625) to a minimum finished thickness of 3mm. "
            "Chemical composition shall meet ASTM B443 Grade 1 requirements.", req_style),

        Paragraph("3.4.2", clause_style),
        Paragraph(
            "Nozzle bore cladding is required for all nozzles DN>50 on vessels in sour service. "
            "Cladding shall extend minimum 50mm beyond the pressure boundary. "
            "Disbonding test per NACE TM0177 Method D is required.", req_style),
    ]

    # ── Page 4: Pressure Vessels ────────────────────────────────────────────────
    story += [
        Paragraph("4. PRESSURE VESSEL REQUIREMENTS", h1_style),
        Paragraph("4.1 Design Code", h2_style),
        Paragraph("4.1.1", clause_style),
        Paragraph(
            "All pressure vessels shall be designed and fabricated to ASME Boiler and Pressure Vessel Code "
            "Section VIII Division 1, latest edition including all applicable addenda. "
            "Design calculations shall be submitted to the Certifying Authority (Bureau Veritas) for approval "
            "prior to commencement of fabrication.", req_style),

        Paragraph("4.1.2 — CONTRADICTION ALERT", warn_style),
        Paragraph(
            "High-pressure separator vessels (design pressure >100 barg) shall be designed to ASME VIII Division 2 "
            "Alternative Rules. NOTE: Clause 4.1.1 specifies Division 1 for ALL vessels — the threshold for "
            "Division 2 in this clause conflicts with the blanket Division 1 requirement above.", req_style),

        Paragraph("4.2 Design Conditions", h2_style),
        Paragraph("4.2.1", clause_style),
        Paragraph(
            "Design pressure shall be the maximum allowable working pressure (MAWP) plus a minimum corrosion "
            "allowance of 3mm. Design temperature range: -20°C minimum to +120°C maximum for sweet service. "
            "For sour service: -20°C to +90°C to comply with NACE MR0175 hardness requirements.", req_style),

        Paragraph("4.2.2", clause_style),
        Paragraph(
            "All vessels shall include a 10% design pressure margin above the maximum operating pressure. "
            "Pressure relief devices shall be sized for fire case as the governing scenario per API 521.", req_style),

        Paragraph("4.3 Inspection and Testing", h2_style),
        Paragraph("4.3.1", clause_style),
        Paragraph(
            "Radiographic examination (RT) shall be performed on all Category A and B butt welds to ASME VIII "
            "Division 1 requirements. For sour service vessels, 100% RT is mandatory regardless of joint efficiency. "
            "Wet fluorescent magnetic particle testing (WFMT) is required for all nozzle attachment welds.", req_style),

        Paragraph("4.3.2", clause_style),
        Paragraph(
            "Hydrostatic pressure test shall be performed at 1.3 times MAWP per ASME VIII Division 1 UG-99. "
            "Test medium shall be potable water with chloride content <50 ppm. Test duration: minimum 30 minutes "
            "at test pressure. Pneumatic testing is not permitted unless Saipem grants written approval.", req_style),

        Paragraph("4.3.3 — CONTRADICTION ALERT", warn_style),
        Paragraph(
            "Hydrostatic test pressure shall be 1.5 times MAWP for all sour service vessels. "
            "NOTE: Clause 4.3.2 specifies 1.3x MAWP for ALL vessels under ASME VIII Div.1. "
            "Vendor shall apply 1.5x for sour service vessels and clarify with Saipem.", req_style),

        Paragraph("4.4 Nozzle Requirements", h2_style),
        Paragraph("4.4.1", clause_style),
        Paragraph(
            "Minimum nozzle size is DN50 (2-inch) for all process connections. Manholes shall be DN500 minimum "
            "on vertical vessels and DN600 on horizontal vessels. All nozzles shall be provided with blind flanges "
            "rated for full MAWP.", req_style),
    ]

    # ── Page 5-6: Rotating Equipment ───────────────────────────────────────────
    story += [
        Paragraph("5. ROTATING EQUIPMENT", h1_style),
        Paragraph("5.1 Gas Compression Trains", h2_style),
        Paragraph("5.1.1", clause_style),
        Paragraph(
            "Gas compression trains shall be designed in accordance with API 617 (latest edition) for centrifugal "
            "compressors. Each train shall consist of: inlet scrubber, compressor body, lube oil system, dry gas "
            "seal system, coupling, gearbox (if required), and driver. Two (2) identical trains are required: "
            "1 operating + 1 installed spare (100% redundancy).", req_style),

        Paragraph("5.1.2", clause_style),
        Paragraph(
            "Compressor casings shall be horizontally split for barrel-type compressors or vertically split "
            "for process conditions requiring higher pressures. Impeller material shall be 17-4 PH stainless steel "
            "(UNS S17400) in H900 condition with maximum hardness HRC 38.", req_style),

        Paragraph("5.1.3", clause_style),
        Paragraph(
            "Dry gas seals shall comply with API 617 Annex D requirements. A tandem arrangement with intermediate "
            "labyrinth is mandatory. Seal gas conditioning unit shall maintain dew point minimum 10°C below the "
            "lowest process temperature. Seal gas supply pressure minimum 3 bar above maximum seal cavity pressure.", req_style),

        Paragraph("5.1.4 — Vibration Limits", h2_style),
        Paragraph("5.1.4.1", clause_style),
        Paragraph(
            "Maximum allowable continuous vibration: 25 microns peak-to-peak at any speed within the operating "
            "speed range per API 670. Trip level shall be set at 50 microns peak-to-peak. Alarm level: 38 microns.", req_style),

        Paragraph("5.1.4.2 — CONTRADICTION ALERT", warn_style),
        Paragraph(
            "Compressor vibration alarm setpoint shall be 25 microns peak-to-peak per the machinery protection "
            "philosophy document (SAI-GRS2-PHI-MACH-001). NOTE: This directly contradicts clause 5.1.4.1 which "
            "sets 38 microns as alarm level. The trip level of 50 microns is consistent between both clauses.", req_style),

        Paragraph("5.2 Produced Water Injection Pumps", h2_style),
        Paragraph("5.2.1", clause_style),
        Paragraph(
            "Produced water injection pumps shall comply with API 610 (ISO 13709) latest edition, type BB5 "
            "(radially split, multistage between bearings). Pump materials shall be suitable for produced water "
            "with up to 150 ppm H2S and chloride content up to 50,000 ppm.", req_style),

        Paragraph("5.2.2", clause_style),
        Paragraph(
            "Minimum pump efficiency at rated duty point: 75%. Power consumption shall not exceed 110% of the "
            "value stated on the datasheet. NPSH margin: available NPSHa shall exceed required NPSHr by minimum "
            "1.0m at all operating conditions including minimum flow.", req_style),

        Paragraph("5.2.3", clause_style),
        Paragraph(
            "Mechanical seals shall be Plan 53B (barrier fluid with bladder accumulator) per API 682. "
            "Seal flush piping shall be 316L stainless steel. Seal chamber pressure: minimum 1.7 bar above "
            "suction pressure. Barrier fluid shall be compatible with produced water service.", req_style),

        Paragraph("5.3 Chemical Injection Pumps", h2_style),
        Paragraph("5.3.1", clause_style),
        Paragraph(
            "Chemical injection pumps shall be positive displacement, diaphragm type, rated for injection "
            "pressures up to 500 barg. Six (6) pumps required: scale inhibitor, corrosion inhibitor, "
            "demulsifier, biocide, antifoam, and methanol. Each chemical system independent.", req_style),
    ]

    # ── Page 7: Instrumentation ────────────────────────────────────────────────
    story += [
        Paragraph("6. INSTRUMENTATION AND CONTROL", h1_style),
        Paragraph("6.1 General Philosophy", h2_style),
        Paragraph(
            "All instrumentation shall be suitable for offshore tropical environment: ambient temperature 0-55°C, "
            "relative humidity 100%, salt-laden atmosphere. Protection class minimum IP66 for outdoor equipment. "
            "Explosion protection classification: Zone 1 — IEC 60079 Group IIA Temperature Class T3.", body_style),

        Paragraph("6.2 Safety Instrumented Systems", h2_style),
        Paragraph("6.2.1", clause_style),
        Paragraph(
            "Safety instrumented functions (SIFs) shall achieve the Safety Integrity Level (SIL) targets defined "
            "in the Safety Requirements Specification (SRS) document SAI-GRS2-SRS-INST-001. "
            "SIL verification shall be performed using PFD (Probability of Failure on Demand) calculations "
            "per IEC 61511.", req_style),

        Paragraph("6.2.2", clause_style),
        Paragraph(
            "High-high pressure shutdown functions on compressor suction and discharge shall achieve SIL 2. "
            "The safety PLC shall be TUV-certified for SIL 3 capable operation to provide adequate headroom. "
            "Functional safety assessment (FSA) by an independent competent body is mandatory before startup.", req_style),

        Paragraph("6.2.3 — CONTRADICTION ALERT", warn_style),
        Paragraph(
            "Per the Process Safety Information package (rev B2, section 4.3), all compressor shutdown functions "
            "shall be SIL 1 only, as the consequence modelling shows the tolerable risk target is met at SIL 1. "
            "Clause 6.2.2 above specifies SIL 2. Vendor shall not proceed with SIL design until Saipem issues "
            "formal clarification via RFQ amendment.", req_style),

        Paragraph("6.3 Field Instrumentation", h2_style),
        Paragraph("6.3.1", clause_style),
        Paragraph(
            "Pressure transmitters: Rosemount 3051 or approved equivalent. 4-20mA HART protocol with local "
            "display. Accuracy: 0.075% of span. Process connections: 1/2 inch NPT. All process-wetted materials "
            "316L stainless steel minimum. Diaphragm seal required for produced water service.", req_style),

        Paragraph("6.3.2", clause_style),
        Paragraph(
            "Temperature measurement: 4-wire PT100 RTD in thermowell. Thermowell calculation per ASME PTC 19.3. "
            "Wake frequency calculation required for all thermowells in gas service above 5 m/s velocity. "
            "Minimum insertion length: 75mm or one-third of pipe diameter, whichever is greater.", req_style),

        Paragraph("6.3.3", clause_style),
        Paragraph(
            "Flow measurement on gas compression train inlet and outlet: Coriolis mass flow meters "
            "(Emerson Micro Motion ELITE or approved equivalent). Accuracy: 0.1% of reading. "
            "For produced water: electromagnetic flow meters with 316L stainless steel electrodes and liner.", req_style),
    ]

    # ── Page 8-9: Electrical ───────────────────────────────────────────────────
    story += [
        Paragraph("7. ELECTRICAL REQUIREMENTS", h1_style),
        Paragraph("7.1 Area Classification", h2_style),
        Paragraph(
            "All electrical equipment within the topsides process area shall be suitable for Zone 1, "
            "Group IIA, Temperature Class T3 (200°C maximum surface temperature) per IEC 60079-0. "
            "Zone 2 equipment is not acceptable in Zone 1 areas under any circumstances.", body_style),

        Paragraph("7.2 Motor Requirements", h2_style),
        Paragraph("7.2.1", clause_style),
        Paragraph(
            "Electric motors above 75 kW shall be supplied with variable frequency drives (VFDs). "
            "Motors shall be IEC 60034 compliant, efficiency class IE3 minimum. Frame size and mounting "
            "per IEC 60072. Insulation class F, temperature rise class B. Motors for compressor drives "
            "shall be suitable for VFD operation with reinforced bearings and shaft grounding rings.", req_style),

        Paragraph("7.2.2 — CONTRADICTION ALERT", warn_style),
        Paragraph(
            "The electrical design basis document (SAI-GRS2-DB-ELEC-001, clause 3.4) specifies that VFDs "
            "are only required for motors above 110 kW. Clause 7.2.1 above sets the threshold at 75 kW. "
            "Vendor shall quote based on 75 kW threshold and include cost delta for 110 kW threshold as an option.", req_style),

        Paragraph("7.3 Power Distribution", h2_style),
        Paragraph("7.3.1", clause_style),
        Paragraph(
            "Package vendor shall supply all motor control centers (MCCs) and local control panels (LCPs) "
            "within the package battery limit. Main power supply: 6.6kV, 60Hz, 3-phase (compressor drives). "
            "Auxiliary power: 400V, 50Hz, 3-phase. UPS backed 24VDC for all control and safety systems. "
            "NOTE: 60Hz main supply with 50Hz auxiliary — confirm with site power philosophy.", req_style),
    ]

    # ── Page 10: Commercial Requirements ──────────────────────────────────────
    story += [
        Paragraph("8. COMMERCIAL AND CONTRACTUAL REQUIREMENTS", h1_style),
        Paragraph("8.1 Delivery", h2_style),
        Paragraph("8.1.1", clause_style),
        Paragraph(
            "Delivery shall be DDP (Delivered Duty Paid) to Saipem's fabrication yard in Arbatax, Sardinia, Italy. "
            "Target delivery date for all packages: 18 months after Purchase Order (PO) award. "
            "Liquidated damages (LDs) for late delivery: EUR 15,000 per day, maximum 10% of PO value.", req_style),

        Paragraph("8.1.2", clause_style),
        Paragraph(
            "Partial deliveries are NOT acceptable without prior written approval from Saipem. "
            "All items within a package must be delivered complete. Vendor shall provide a detailed "
            "fabrication and delivery schedule with the technical proposal.", req_style),

        Paragraph("8.2 Warranty", h2_style),
        Paragraph("8.2.1", clause_style),
        Paragraph(
            "Equipment warranty period: 24 months from date of first production, or 30 months from delivery "
            "to Saipem's yard, whichever occurs first. Vendor shall maintain spare parts availability for "
            "minimum 20 years from delivery. Critical spare parts for first 2 years of operation must be "
            "included in the quotation as a separate priced option.", req_style),

        Paragraph("8.3 Documentation", h2_style),
        Paragraph("8.3.1", clause_style),
        Paragraph(
            "Vendor documentation shall be submitted in English language only. Drawing format: A1 (ISO 216) "
            "or ANSI D equivalent. Document management system: Saipem ProjectWise. File format: PDF/A for "
            "final documents, native CAD files required for all fabrication drawings.", req_style),

        Paragraph("8.3.2", clause_style),
        Paragraph(
            "As-built documentation package must be delivered within 60 days of FAT completion. "
            "Minimum documentation requirements: P&IDs, equipment general arrangement drawings, "
            "data books (MTRs, weld maps, NDE records, pressure test records), operation and maintenance manuals, "
            "spare parts lists with manufacturer part numbers.", req_style),
    ]

    # ── Page 11: FAT & Inspection ──────────────────────────────────────────────
    story += [
        Paragraph("9. FACTORY ACCEPTANCE TEST (FAT)", h1_style),
        Paragraph("9.1 FAT Requirements", h2_style),
        Paragraph("9.1.1", clause_style),
        Paragraph(
            "Factory Acceptance Test shall be performed at Vendor's facility prior to shipment. "
            "Minimum 14 days' notice required for FAT date confirmation. Saipem and TotalEnergies Angola "
            "representatives will attend. Bureau Veritas (Certifying Authority) attendance is mandatory.", req_style),

        Paragraph("9.1.2", clause_style),
        Paragraph(
            "FAT shall include as minimum: (a) 4-hour continuous mechanical run at rated conditions; "
            "(b) performance test to verify capacity and efficiency; (c) vibration and noise measurements; "
            "(d) safety system functional test — all SIFs to be function-tested; "
            "(e) leak test at MAWP with service fluid.", req_style),

        Paragraph("9.1.3", clause_style),
        Paragraph(
            "Compressor mechanical running test shall be conducted in accordance with API 617 Annex K "
            "(Full Load, Full Pressure test) using actual process gas or nitrogen at equivalent conditions. "
            "Efficiency measurement uncertainty shall not exceed +/-2% per ASME PTC 10.", req_style),

        Paragraph("9.2 Inspection Hold Points", h2_style),
        Paragraph(
            "The following are mandatory Hold Points (H) requiring Saipem Inspector presence before work can proceed:", body_style),
    ]

    holdpoints = [
        ["Hold Point", "Activity", "Document Required"],
        ["H1", "Material receiving inspection — pressure-containing parts", "MTR review and approval"],
        ["H2", "First article inspection — nozzle layout and dimensions", "Dimensional report"],
        ["H3", "Weld procedure qualification (WPQ) review", "WPQR per ASME IX"],
        ["H4", "Hydrostatic pressure test", "Test certificate, calibration certs"],
        ["H5", "Nameplate and MAWP stamp verification", "ASME U-stamp documentation"],
        ["H6", "Final inspection before packaging and shipment", "Final inspection checklist"],
    ]
    t3 = Table(holdpoints, colWidths=[25*mm, 90*mm, 50*mm])
    t3.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTNAME',  (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 8),
        ('BACKGROUND',(0,0), (-1,0),  colors.HexColor('#2d5986')),
        ('TEXTCOLOR', (0,0), (-1,0),  colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f0f4f8'), colors.white]),
        ('BOX',       (0,0), (-1,-1), 0.5, colors.HexColor('#aaaaaa')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#cccccc')),
        ('TOPPADDING',   (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0), (-1,-1), 3),
        ('LEFTPADDING',  (0,0), (-1,-1), 4),
    ]))
    story += [t3, Spacer(1, 4*mm)]

    # ── Page 12: Quotation Requirements ───────────────────────────────────────
    story += [
        Paragraph("10. QUOTATION REQUIREMENTS", h1_style),
        Paragraph("10.1 Technical Proposal", h2_style),
        Paragraph(
            "The technical proposal shall include: (a) confirmation of compliance with all RFQ requirements; "
            "(b) deviation register listing all exceptions with technical justification; (c) preliminary equipment "
            "datasheets; (d) vendor experience list with 3 comparable references from offshore FPSO projects; "
            "(e) proposed fabrication timeline with key milestones; (f) list of major subcontractors.", body_style),

        Paragraph("10.2 Commercial Proposal", h2_style),
        Paragraph(
            "The commercial proposal shall be submitted in a separate sealed envelope (physical or encrypted "
            "digital file). Pricing shall be broken down by: (a) engineering; (b) procurement; "
            "(c) fabrication; (d) testing and inspection; (e) documentation; (f) project management. "
            "All prices in EUR. Validity: 180 days from submission date.", body_style),

        Paragraph("10.3 Clarification Process", h2_style),
        Paragraph(
            "All technical queries shall be submitted via the Saipem Vendor Portal no later than 21 days before "
            "the submission deadline. Saipem will issue formal RFQ amendments for all clarifications affecting "
            "technical scope. Verbal clarifications are not binding.", body_style),

        Spacer(1, 6*mm),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a3a5c')),
        Spacer(1, 4*mm),
        Paragraph(
            "END OF DOCUMENT — SAI-GRS2-RFQ-PROC-0047 Rev C2 | TotalEnergies Angola — FPSO Girassol Phase II | "
            "CONFIDENTIAL — NOT FOR DISTRIBUTION", sub_style),
    ]

    doc.build(story)
    print(f"Generated: {OUTPUT}")
    print("Stats: 12 pages, 6 contradictions, 5 disciplines (materials/vessels/rotating/instrumentation/electrical)")
    print("Contradictions: material spec (3.3.2 vs 3.3.4), pressure test (4.3.2 vs 4.3.3), ASME div (4.1.1 vs 4.1.2),")
    print("                vibration alarm (5.1.4.1 vs 5.1.4.2), SIL level (6.2.2 vs 6.2.3), VFD threshold (7.2.1 vs 7.2.2)")

if __name__ == "__main__":
    generate()
