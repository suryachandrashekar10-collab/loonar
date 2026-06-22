import { useState, useRef } from 'react'
import { Upload, FileText, AlertOctagon, CheckCircle, Loader2, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import clsx from 'clsx'

type Requirement = {
  id: string
  clause: string
  text: string
  category: string
  risk: 'high' | 'medium' | 'low'
  page: number
  doc: string
}

type Contradiction = {
  id: string
  desc: string
  doc1: string
  doc2: string
  clause1: string
  clause2: string
}

const MOCK_REQUIREMENTS: Requirement[] = [
  { id: 'REQ-001', clause: '4.2.1', text: 'All pressure-containing parts shall be fabricated from ASTM A350 LF2 low-temperature carbon steel.', category: 'Material', risk: 'high', page: 42, doc: 'SPC-MECH-001' },
  { id: 'REQ-002', clause: '5.1.3', text: 'Valves shall comply with NACE MR0175 / ISO 15156 for sour service applications.', category: 'Standards', risk: 'high', page: 67, doc: 'SPC-MECH-001' },
  { id: 'REQ-003', clause: '6.4.2', text: 'Hydrostatic shell test pressure shall be 1.5× design pressure for minimum 10 minutes.', category: 'Testing', risk: 'medium', page: 89, doc: 'SPC-QA-002' },
  { id: 'REQ-004', clause: '3.1.1', text: 'Flanges shall conform to ASME B16.5 Class 900 raised-face configuration.', category: 'Dimensional', risk: 'medium', page: 31, doc: 'SPC-MECH-001' },
  { id: 'REQ-005', clause: '8.2.1', text: 'Third-party inspection by Bureau Veritas is mandatory at final assembly stage.', category: 'Inspection', risk: 'low', page: 142, doc: 'SPC-QA-002' },
]

const MOCK_CONTRADICTIONS: Contradiction[] = [
  {
    id: 'CONT-001',
    desc: 'Conflicting material specification: body material differs between documents',
    doc1: 'SPC-MECH-001 §4.2.1',
    doc2: 'PIPING-SPEC-003 §2.1.4',
    clause1: 'Body material: ASTM A105 Carbon Steel',
    clause2: 'All valves in sour service lines: Duplex Stainless Steel UNS S31803',
  },
  {
    id: 'CONT-002',
    desc: 'Testing standard conflict: ASME Section I vs Section VIII',
    doc1: 'SPC-QA-002 §6.1',
    doc2: 'PROJECT-ADDENDUM-01 §3.2',
    clause1: 'Safety valves certified under ASME Section VIII (Pressure Vessels)',
    clause2: 'All safety devices shall meet ASME Section I (Power Boilers)',
  },
]

const riskColor = {
  high:   'text-rose-400 bg-rose-500/10 border-rose-500/20',
  medium: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  low:    'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
}

export default function RFQAnalyzer() {
  const [stage, setStage] = useState<'idle' | 'uploading' | 'processing' | 'done'>('idle')
  const [expanded, setExpanded] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleUpload = () => {
    setStage('uploading')
    setTimeout(() => setStage('processing'), 1200)
    setTimeout(() => setStage('done'), 3500)
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white">RFQ Analyzer</h1>
        <p className="text-slate-400 text-sm mt-1">Upload a ZIP or PDF package — requirements extracted, contradictions flagged, every finding cited to source.</p>
      </div>

      {stage === 'idle' && (
        <div
          onClick={() => fileRef.current?.click()}
          className="border-2 border-dashed border-border rounded-2xl p-16 flex flex-col items-center justify-center gap-4 cursor-pointer hover:border-brand-500/50 hover:bg-brand-500/5 transition-all group"
        >
          <div className="w-14 h-14 rounded-2xl bg-brand-500/10 flex items-center justify-center group-hover:bg-brand-500/20 transition-colors">
            <Upload size={24} className="text-brand-400" />
          </div>
          <div className="text-center">
            <p className="text-white font-medium">Drop RFQ package here</p>
            <p className="text-slate-500 text-sm mt-1">Supports .zip, .pdf, .xlsx — up to 2 GB</p>
          </div>
          <button className="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors">
            Browse Files
          </button>
          <input ref={fileRef} type="file" className="hidden" onChange={handleUpload} />
        </div>
      )}

      {(stage === 'uploading' || stage === 'processing') && (
        <div className="bg-panel border border-border rounded-2xl p-12 flex flex-col items-center gap-6">
          <Loader2 size={32} className="text-brand-400 animate-spin" />
          <div className="text-center">
            <p className="text-white font-medium">
              {stage === 'uploading' ? 'Uploading package...' : 'Analyzing requirements...'}
            </p>
            <p className="text-slate-500 text-sm mt-1">
              {stage === 'uploading'
                ? 'Extracting and OCR-processing documents'
                : 'Running contradiction detection across all documents'}
            </p>
          </div>
          <div className="w-64 bg-border rounded-full h-1.5">
            <div
              className="bg-brand-500 h-1.5 rounded-full transition-all duration-1000"
              style={{ width: stage === 'uploading' ? '30%' : '80%' }}
            />
          </div>
        </div>
      )}

      {stage === 'done' && (
        <div className="space-y-6">
          {/* Summary bar */}
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Requirements', value: MOCK_REQUIREMENTS.length, color: 'text-brand-400' },
              { label: 'High Risk',    value: MOCK_REQUIREMENTS.filter(r => r.risk === 'high').length,   color: 'text-rose-400' },
              { label: 'Medium Risk',  value: MOCK_REQUIREMENTS.filter(r => r.risk === 'medium').length, color: 'text-amber-400' },
              { label: 'Contradictions', value: MOCK_CONTRADICTIONS.length, color: 'text-purple-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-panel border border-border rounded-xl p-4">
                <div className={`text-2xl font-semibold ${color}`}>{value}</div>
                <div className="text-xs text-slate-500 mt-1">{label}</div>
              </div>
            ))}
          </div>

          {/* Contradictions */}
          {MOCK_CONTRADICTIONS.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <AlertOctagon size={16} className="text-rose-400" />
                <h2 className="text-sm font-semibold text-white">Cross-Document Contradictions</h2>
                <span className="ml-auto text-xs px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded-full">
                  {MOCK_CONTRADICTIONS.length} detected
                </span>
              </div>
              <div className="space-y-3">
                {MOCK_CONTRADICTIONS.map(c => (
                  <div key={c.id} className="bg-panel border border-rose-500/20 rounded-xl p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <span className="text-xs font-mono text-rose-400">{c.id}</span>
                        <p className="text-sm text-white font-medium mt-1">{c.desc}</p>
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-2 gap-3">
                      <div className="bg-rose-500/5 border border-rose-500/10 rounded-lg p-3">
                        <p className="text-xs text-rose-400 font-medium mb-1">{c.doc1}</p>
                        <p className="text-xs text-slate-300">{c.clause1}</p>
                      </div>
                      <div className="bg-rose-500/5 border border-rose-500/10 rounded-lg p-3">
                        <p className="text-xs text-rose-400 font-medium mb-1">{c.doc2}</p>
                        <p className="text-xs text-slate-300">{c.clause2}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Requirements table */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle size={16} className="text-brand-400" />
              <h2 className="text-sm font-semibold text-white">Extracted Requirements</h2>
            </div>
            <div className="bg-panel border border-border rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    {['ID', 'Category', 'Requirement', 'Risk', 'Source'].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {MOCK_REQUIREMENTS.map((req, i) => (
                    <>
                      <tr
                        key={req.id}
                        onClick={() => setExpanded(expanded === req.id ? null : req.id)}
                        className={clsx(
                          'cursor-pointer hover:bg-white/5 transition-colors',
                          i !== MOCK_REQUIREMENTS.length - 1 && 'border-b border-border'
                        )}
                      >
                        <td className="px-4 py-3 font-mono text-xs text-brand-400">{req.id}</td>
                        <td className="px-4 py-3 text-xs text-slate-400">{req.category}</td>
                        <td className="px-4 py-3 text-xs text-slate-300 max-w-xs truncate">{req.text}</td>
                        <td className="px-4 py-3">
                          <span className={clsx('text-xs px-2 py-0.5 rounded-full border font-medium', riskColor[req.risk])}>
                            {req.risk}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1 text-xs text-slate-500">
                            <FileText size={11} />
                            <span>{req.doc} p.{req.page}</span>
                            <ExternalLink size={10} className="ml-1 text-brand-500 opacity-0 group-hover:opacity-100" />
                          </div>
                        </td>
                      </tr>
                      {expanded === req.id && (
                        <tr key={`${req.id}-exp`} className="bg-brand-500/5 border-b border-border">
                          <td colSpan={5} className="px-6 py-4">
                            <p className="text-xs text-slate-300 leading-relaxed">{req.text}</p>
                            <div className="flex items-center gap-4 mt-2">
                              <span className="text-xs text-slate-500">§ {req.clause} · {req.doc} · Page {req.page}</span>
                              <button className="text-xs text-brand-400 hover:underline">Open in source document →</button>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <button
              onClick={() => setStage('idle')}
              className="px-4 py-2 border border-border rounded-lg text-sm text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
            >
              Upload Another
            </button>
            <button className="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors">
              Export to Deviation Register →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
