-- Seed data for local development and demo.
-- Run after all three migrations.
-- ─────────────────────────────────────────────────────────────

-- Demo project
insert into projects (id, name, customer, rfq_ref, value_eur, deadline, status)
values (
  'demo-project-0001-0000-0000-000000000000',
  'Shell LNG Terminal — Gate 4B',
  'Shell Energy B.V.',
  'SH-LNG-2026-04B',
  4800000,
  '2026-08-15',
  'active'
) on conflict (id) do nothing;

-- Demo document
insert into documents (id, project_id, filename, doc_type, storage_path)
values (
  'demo-doc-00000-0000-0000-000000000000',
  'demo-project-0001-0000-0000-000000000000',
  'SPC-MECH-001_Rev3.pdf',
  'rfq',
  'rfq/demo-project-0001-0000-0000-000000000000/SPC-MECH-001_Rev3.pdf'
) on conflict (id) do nothing;

-- Demo requirements (matches frontend mock so real API looks same as mock)
insert into requirements
  (id, project_id, document_id, req_id, clause, category, text, risk_level, confidence, page_number, verified)
values
  ('req-001-0000-0000-0000-000000000000', 'demo-project-0001-0000-0000-000000000000', 'demo-doc-00000-0000-0000-000000000000',
   'REQ-001', '4.2.1', 'Material',
   'All pressure-containing parts shall be fabricated from ASTM A350 LF2 low-temperature carbon steel rated to -50°C.',
   'high', 0.96, 42, false),
  ('req-002-0000-0000-0000-000000000000', 'demo-project-0001-0000-0000-000000000000', 'demo-doc-00000-0000-0000-000000000000',
   'REQ-002', '5.1.3', 'Standards',
   'Valves shall comply with NACE MR0175 / ISO 15156 for sour service applications. H₂S partial pressure >0.05 psia.',
   'high', 0.98, 67, false),
  ('req-003-0000-0000-0000-000000000000', 'demo-project-0001-0000-0000-000000000000', 'demo-doc-00000-0000-0000-000000000000',
   'REQ-003', '6.4.2', 'Testing',
   'Hydrostatic shell test pressure shall be 1.5× design pressure for a minimum hold time of 10 minutes.',
   'medium', 0.91, 89, true),
  ('req-004-0000-0000-0000-000000000000', 'demo-project-0001-0000-0000-000000000000', 'demo-doc-00000-0000-0000-000000000000',
   'REQ-004', '3.1.1', 'Dimensional',
   'Flanges shall conform to ASME B16.5 Class 900 raised-face (RF) configuration. RTJ acceptable upon written approval.',
   'medium', 0.87, 31, false),
  ('req-005-0000-0000-0000-000000000000', 'demo-project-0001-0000-0000-000000000000', 'demo-doc-00000-0000-0000-000000000000',
   'REQ-005', '8.2.1', 'Inspection',
   'Third-party inspection by Bureau Veritas is mandatory at final assembly stage. No substitutions without Owner approval.',
   'low', 0.93, 142, false),
  ('req-006-0000-0000-0000-000000000000', 'demo-project-0001-0000-0000-000000000000', 'demo-doc-00000-0000-0000-000000000000',
   'REQ-006', '9.1.2', 'Safety',
   'All safety valves shall be certified under ASME Section I (Power Boilers). ASME Section VIII not acceptable.',
   'high', 0.95, 178, false)
on conflict (id) do nothing;

-- Demo contradictions
insert into contradictions (project_id, req_id_a, req_id_b, description, severity, resolved)
values
  ('demo-project-0001-0000-0000-000000000000',
   'req-001-0000-0000-0000-000000000000',
   'req-002-0000-0000-0000-000000000000',
   'Body material conflict: §4.2.1 specifies carbon steel; NACE sour service requirement §5.1.3 mandates corrosion-resistant alloy per ISO 15156 Part 2',
   'critical', false),
  ('demo-project-0001-0000-0000-000000000000',
   'req-003-0000-0000-0000-000000000000',
   'req-006-0000-0000-0000-000000000000',
   'ASME code conflict: hydrostatic test §6.4.2 implies Section VIII scope; §9.1.2 explicitly mandates Section I only',
   'high', false)
on conflict do nothing;

-- Demo deviations (auto-generated from high-risk requirements)
insert into deviations
  (project_id, requirement_id, dev_id, clause, doc_ref, customer_spec, proposed_deviation, justification, status)
values
  ('demo-project-0001-0000-0000-000000000000', 'req-001-0000-0000-0000-000000000000',
   'DEV-001', '4.2.1', 'SPC-MECH-001',
   'All pressure-containing parts fabricated from ASTM A350 LF2 low-temp carbon steel rated to -50°C.',
   'Standard ASTM A105 available to -29°C. ASTM A350 LF2 available on extended lead time (+4 wks). Seeking approval for A105 on non-cryogenic lines.',
   'Lines operating above -29°C do not require LF2 per ASME B31.3 Table A-1. LF2 applied only to cryogenic loop.',
   'pending'),
  ('demo-project-0001-0000-0000-000000000000', 'req-006-0000-0000-0000-000000000000',
   'DEV-002', '9.1.2', 'SPC-MECH-001',
   'All safety valves shall be certified under ASME Section I (Power Boilers).',
   'Standard product certified under ASME Section VIII Div 1. Section I requires separate design qualification, welder requalification, and NDE. Lead time impact: +8 weeks.',
   'Section I qualification applies to fired pressure vessels. Safety valves in this application fall under Section VIII scope. Request technical concession.',
   'rejected'),
  ('demo-project-0001-0000-0000-000000000000', 'req-005-0000-0000-0000-000000000000',
   'DEV-003', '8.3.1', 'SPC-MECH-001',
   'Third-party inspection by SGS mandatory at final assembly stage.',
   'Bureau Veritas proposed as equivalent TPI authority.',
   'Bureau Veritas holds ILAC/MRA mutual recognition with SGS. Same accreditation scope. Preferred vendor for this facility location.',
   'accepted'),
  ('demo-project-0001-0000-0000-000000000000', 'req-004-0000-0000-0000-000000000000',
   'DEV-004', '6.4.2', 'SPC-MECH-001',
   'Raised-face (RF) flanges conforming to ASME B16.5 Class 900. Ring-type joint (RTJ) acceptable upon written approval.',
   'Requesting written confirmation: is RTJ required for all Class 900 items, or only HP gas lines above 5 bar?',
   'Seeking clarification to avoid unnecessary RTJ on utility lines where RF is standard and acceptable.',
   'clarification')
on conflict do nothing;
