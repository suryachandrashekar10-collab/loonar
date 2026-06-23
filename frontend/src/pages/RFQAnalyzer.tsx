import React, { useState, useRef, useEffect } from 'react'
import API_URL from '../api'
import { useSearchParams } from 'react-router-dom'
import {
  Upload, FileText, AlertOctagon, CheckCircle, Loader2,
  ExternalLink, ShieldCheck, ShieldAlert, ShieldQuestion,
  ChevronDown, ChevronRight, PenLine, ThumbsUp
} from 'lucide-react'
import clsx from 'clsx'

// ── Types ────────────────────────────────────────────────────────────────────

type JobStatus = 'idle' | 'queued' | 'ingesting' | 'extracting' | 'detecting' | 'done' | 'failed'

type Progress = {
  stage: string
  pages_processed: number
  pages_total: number
  requirements_found: number
  contradictions_found: number
}

type Requirement = {
  id: string
  req_id: string
  clause: string
  category: string
  text: string
  risk_level: 'high' | 'medium' | 'low'
  confidence: number
  page_number: number
  verified: boolean
  verified_by?: string
}

type Contradiction = {
  id: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  req_a?: { req_id: string; clause: string; text: string; page_number: number }
  req_b?: { req_id: string; clause: string; text: string; page_number: number }
}

// ── Mock data (used when backend is not connected) ───────────────────────────

const MOCK_REQUIREMENTS: Requirement[] = [
  { id: '1', req_id: 'REQ-001', clause: '4.2.1', category: 'Material',    text: 'All pressure-containing parts shall be fabricated from ASTM A350 LF2 low-temperature carbon steel rated to -50°C.',     risk_level: 'high',   confidence: 0.96, page_number: 42,  verified: false },
  { id: '2', req_id: 'REQ-002', clause: '5.1.3', category: 'Standards',   text: 'Valves shall comply with NACE MR0175 / ISO 15156 for sour service applications. H₂S partial pressure >0.05 psia.',        risk_level: 'high',   confidence: 0.98, page_number: 67,  verified: false },
  { id: '3', req_id: 'REQ-003', clause: '6.4.2', category: 'Testing',     text: 'Hydrostatic shell test pressure shall be 1.5× design pressure for a minimum hold time of 10 minutes.',                    risk_level: 'medium', confidence: 0.91, page_number: 89,  verified: true, verified_by: 'J. Eriksson' },
  { id: '4', req_id: 'REQ-004', clause: '3.1.1', category: 'Dimensional', text: 'Flanges shall conform to ASME B16.5 Class 900 raised-face (RF) configuration. RTJ acceptable upon written approval.',       risk_level: 'medium', confidence: 0.87, page_number: 31,  verified: false },
  { id: '5', req_id: 'REQ-005', clause: '8.2.1', category: 'Inspection',  text: 'Third-party inspection by Bureau Veritas is mandatory at final assembly stage. No substitutions without Owner approval.',   risk_level: 'low',    confidence: 0.93, page_number: 142, verified: false },
  { id: '6', req_id: 'REQ-006', clause: '9.1.2', category: 'Safety',      text: 'All safety valves shall be certified under ASME Section I (Power Boilers). ASME Section VIII not acceptable.',             risk_level: 'high',   confidence: 0.95, page_number: 178, verified: false },
]

const MOCK_CONTRADICTIONS: Contradiction[] = [
  {
    id: 'c1',
    description: 'Body material conflict: §4.2.1 specifies carbon steel; piping spec §2.1.4 mandates duplex stainless for sour service lines',
    severity: 'critical',
    req_a: { req_id: 'REQ-001', clause: '4.2.1', text: 'ASTM A350 LF2 Carbon Steel',                  page_number: 42 },
    req_b: { req_id: 'REQ-002', clause: '5.1.3', text: 'NACE MR0175 — sour service compliance required', page_number: 67 },
  },
  {
    id: 'c2',
    description: 'ASME code conflict: §8.2.1 implies Section VIII acceptance; §9.1.2 explicitly mandates Section I only',
    severity: 'high',
    req_a: { req_id: 'REQ-003', clause: '6.4.2', text: 'Hydrostatic testing per API 598',              page_number: 89 },
    req_b: { req_id: 'REQ-006', clause: '9.1.2', text: 'ASME Section I certification mandatory',       page_number: 178 },
  },
]

// ── Helpers ───────────────────────────────────────────────────────────────────

const riskStyle = {
  high:   { chip: 'text-rose-400 bg-rose-500/10 border-rose-500/20',   dot: 'bg-rose-400' },
  medium: { chip: 'text-amber-400 bg-amber-500/10 border-amber-500/20', dot: 'bg-amber-400' },
  low:    { chip: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20', dot: 'bg-emerald-400' },
}

const sevStyle = {
  critical: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
  high:     'text-amber-400 bg-amber-500/10 border-amber-500/30',
  medium:   'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
  low:      'text-slate-400 bg-slate-500/10 border-slate-500/20',
}

function ConfidenceIcon({ score }: { score: number }) {
  if (score >= 0.9) return <ShieldCheck size={12} className="text-emerald-400" />
  if (score >= 0.7) return <ShieldQuestion size={12} className="text-amber-400" />
  return <ShieldAlert size={12} className="text-rose-400" />
}

function ProgressBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0
  return (
    <div className="w-full bg-border rounded-full h-1">
      <div className="bg-brand-500 h-1 rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
    </div>
  )
}

// ── Main Component ────────────────────────────────────────────────────────────

export default function RFQAnalyzer() {
  const DEMO_PROJECT_ID = '00000001-0000-0000-0000-000000000001'
  const [searchParams] = useSearchParams()
  const [jobStatus, setJobStatus] = useState<JobStatus>('idle')
  const [jobId, setJobId]         = useState<string | null>(null)
  const [projectId, setProjectId] = useState<string>(
    searchParams.get('project') || localStorage.getItem('lastProjectId') || DEMO_PROJECT_ID
  )
  const [progress, setProgress]   = useState<Progress>({ stage: '', pages_processed: 0, pages_total: 0, requirements_found: 0, contradictions_found: 0 })
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [contradictions, setContradictions] = useState<Contradiction[]>([])
  const [expandedReq, setExpandedReq] = useState<string | null>(null)
  const [overrideReq, setOverrideReq] = useState<string | null>(null)
  const [overrideNote, setOverrideNote] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)
  const sseRef  = useRef<EventSource | null>(null)

  const loadResults = async (pid: string) => {
    try {
      const [reqRes, conRes] = await Promise.all([
        fetch(`${API_URL}/projects/${pid}/requirements`),
        fetch(`${API_URL}/projects/${pid}/contradictions`),
      ])
      if (reqRes.ok) setRequirements(await reqRes.json())
      else setRequirements([])
      if (conRes.ok) setContradictions(await conRes.json())
      else setContradictions([])
    } catch (err) {
      console.error('loadResults failed:', err)
      setRequirements([])
      setContradictions([])
    }
  }

  // Load project results on mount (or when project changes)
  useEffect(() => {
    loadResults(projectId)
  }, [projectId])

  // Stream progress via SSE
  useEffect(() => {
    if (!jobId) return
    const es = new EventSource(`${API_URL}/rfq/status/${jobId}`)
    sseRef.current = es

    es.onmessage = (e) => {
      const data = JSON.parse(e.data)
      setJobStatus(data.status)
      if (data.progress) setProgress(data.progress)
      if (data.status === 'done') {
        es.close()
        loadResults(data.project_id || projectId)
      }
      if (data.status === 'failed') es.close()
    }
    es.onerror = () => {
      // Backend not running — simulate with mock
      es.close()
      simulateMock()
    }
    return () => es.close()
  }, [jobId])

  const simulateMock = () => {
    const stages: [JobStatus, Partial<Progress>][] = [
      ['ingesting',  { stage: 'Splitting document into chunks...', pages_processed: 0,  pages_total: 47, requirements_found: 0,  contradictions_found: 0 }],
      ['extracting', { stage: 'Extracting requirements... chunk 4/12',  pages_processed: 12, pages_total: 47, requirements_found: 8,  contradictions_found: 0 }],
      ['extracting', { stage: 'Extracting requirements... chunk 9/12',  pages_processed: 28, pages_total: 47, requirements_found: 23, contradictions_found: 0 }],
      ['detecting',  { stage: 'Detecting cross-document contradictions...', pages_processed: 42, pages_total: 47, requirements_found: 31, contradictions_found: 0 }],
      ['done',       { stage: 'Complete', pages_processed: 47, pages_total: 47, requirements_found: 6, contradictions_found: 2 }],
    ]
    let i = 0
    const tick = () => {
      if (i >= stages.length) return
      const [s, p] = stages[i++]
      setJobStatus(s)
      setProgress(prev => ({ ...prev, ...p }))
      if (s === 'done') {
        setTimeout(() => loadResults(projectId), 1500)
      } else {
        setTimeout(tick, 900)
      }
    }
    setTimeout(tick, 400)
  }

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setJobStatus('queued')
    const fakeJobId = crypto.randomUUID()
    setJobId(fakeJobId)
    // Try real upload; fall back to mock SSE
    try {
      const form = new FormData()
      form.append('file', file)
      form.append('project_id', projectId)
      const res = await fetch(`${API_URL}/rfq/upload`, { method: 'POST', body: form })
      if (res.ok) {
        const data = await res.json()
        setJobId(data.job_id)
        if (data.project_id) setProjectId(data.project_id)
      } else {
        simulateMock()
      }
    } catch {
      simulateMock()
    }
  }

  const handleVerify = (reqId: string) => {
    const req = requirements.find(r => r.id === reqId)
    setRequirements(prev => prev.map(r =>
      r.id === reqId ? { ...r, verified: true, verified_by: 'You' } : r
    ))
    try {
      fetch(`${API_URL}/corrections`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requirement_id: reqId,
          original_text: req?.text || '',
          corrected_text: req?.text || '',
          correction_type: 'verify',
          corrected_by: 'engineer',
        }),
      }).catch(() => {})
    } catch { /* fire and forget */ }
  }

  const handleOverride = (reqId: string) => {
    if (!overrideNote.trim()) return
    const req = requirements.find(r => r.id === reqId)
    setRequirements(prev => prev.map(r =>
      r.id === reqId ? { ...r, verified: true, verified_by: 'You' } : r
    ))
    try {
      fetch(`${API_URL}/corrections`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requirement_id: reqId,
          original_text: req?.text || '',
          corrected_text: overrideNote,
          correction_type: 'override',
          corrected_by: 'engineer',
        }),
      }).catch(() => {})
    } catch { /* fire and forget */ }
    setOverrideReq(null)
    setOverrideNote('')
  }

  const isProcessing = ['queued', 'ingesting', 'extracting', 'detecting'].includes(jobStatus)

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white">RFQ Analyzer</h1>
        <p className="text-slate-400 text-sm mt-1">
          Upload a ZIP or PDF package — requirements extracted, contradictions flagged, every finding cited to source.
        </p>
      </div>

      {/* Upload zone */}
      {jobStatus === 'idle' && requirements.length === 0 && (
        <div
          onClick={() => fileRef.current?.click()}
          className="border-2 border-dashed border-border rounded-2xl p-14 flex flex-col items-center gap-4 cursor-pointer hover:border-brand-500/50 hover:bg-brand-500/5 transition-all group"
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
          <input ref={fileRef} type="file" accept=".pdf,.zip,.xlsx" className="hidden" onChange={handleFile} />
        </div>
      )}

      {/* Live progress */}
      {isProcessing && (
        <div className="bg-panel border border-border rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <Loader2 size={20} className="text-brand-400 animate-spin" />
            <span className="text-white font-medium">{progress.stage || 'Initializing...'}</span>
          </div>

          <ProgressBar value={progress.pages_processed} max={progress.pages_total || 1} />

          <div className="grid grid-cols-3 gap-4 mt-6">
            {[
              { label: 'Pages processed', value: `${progress.pages_processed}${progress.pages_total ? ` / ${progress.pages_total}` : ''}` },
              { label: 'Requirements found', value: progress.requirements_found },
              { label: 'Contradictions',     value: progress.contradictions_found },
            ].map(({ label, value }) => (
              <div key={label} className="bg-white/5 rounded-xl p-4 text-center">
                <div className="text-2xl font-semibold text-white">{value}</div>
                <div className="text-xs text-slate-500 mt-1">{label}</div>
              </div>
            ))}
          </div>

          <div className="mt-4 flex items-center gap-2">
            {(['ingesting', 'extracting', 'detecting'] as JobStatus[]).map((s, i) => (
              <div key={s} className="flex items-center gap-2">
                <div className={clsx('w-2 h-2 rounded-full', jobStatus === s ? 'bg-brand-400 animate-pulse' : ['done'].includes(jobStatus) || i < ['ingesting','extracting','detecting'].indexOf(jobStatus) ? 'bg-emerald-400' : 'bg-border')} />
                <span className={clsx('text-xs', jobStatus === s ? 'text-brand-400' : 'text-slate-600 capitalize')}>{s}</span>
                {i < 2 && <div className="w-6 h-px bg-border" />}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {(jobStatus === 'done' || requirements.length > 0) && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Requirements',   value: requirements.length,                                          color: 'text-brand-400' },
              { label: 'High Risk',      value: requirements.filter(r => r.risk_level === 'high').length,    color: 'text-rose-400' },
              { label: 'Unverified',     value: requirements.filter(r => !r.verified).length,                color: 'text-amber-400' },
              { label: 'Contradictions', value: contradictions.length,                                        color: 'text-purple-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-panel border border-border rounded-xl p-4">
                <div className={`text-2xl font-semibold ${color}`}>{value}</div>
                <div className="text-xs text-slate-500 mt-1">{label}</div>
              </div>
            ))}
          </div>

          {/* Contradictions */}
          {contradictions.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-3">
                <AlertOctagon size={15} className="text-rose-400" />
                <h2 className="text-sm font-semibold text-white">Cross-Document Contradictions</h2>
                <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  {contradictions.length} detected
                </span>
              </div>
              <div className="space-y-3">
                {contradictions.map(c => (
                  <div key={c.id} className="bg-panel border border-rose-500/20 rounded-xl overflow-hidden">
                    <div className="flex items-center gap-3 px-4 py-3 border-b border-rose-500/10">
                      <span className={clsx('text-xs px-2 py-0.5 rounded-full border font-medium capitalize', sevStyle[c.severity])}>
                        {c.severity}
                      </span>
                      <p className="text-sm text-white font-medium">{c.description}</p>
                    </div>
                    <div className="grid grid-cols-2 divide-x divide-rose-500/10">
                      {[c.req_a, c.req_b].map((req, i) => req && (
                        <div key={i} className="p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-mono text-xs text-rose-400">{req.req_id}</span>
                            <span className="text-xs text-slate-600">§ {req.clause}</span>
                            <CitationChip page={req.page_number} doc={(req as any).filename || (req as any).document_id || 'Document'} />
                          </div>
                          <p className="text-xs text-slate-300 leading-relaxed">{req.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Requirements table */}
          <section>
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle size={15} className="text-brand-400" />
              <h2 className="text-sm font-semibold text-white">Extracted Requirements</h2>
              <span className="ml-auto text-xs text-slate-500">Click row to expand · verify or override AI output</span>
            </div>

            <div className="bg-panel border border-border rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    {['ID', 'Category', 'Requirement', 'Risk', 'Confidence', 'Source', 'Status'].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {requirements.map((req, i) => (
                    <React.Fragment key={req.id}>
                      <tr
                        onClick={() => setExpandedReq(expandedReq === req.id ? null : req.id)}
                        className={clsx(
                          'cursor-pointer hover:bg-white/5 transition-colors',
                          i < requirements.length - 1 && 'border-b border-border'
                        )}
                      >
                        <td className="px-4 py-3 font-mono text-xs text-brand-400 whitespace-nowrap">{req.req_id}</td>
                        <td className="px-4 py-3 text-xs text-slate-400 whitespace-nowrap">{req.category}</td>
                        <td className="px-4 py-3 text-xs text-slate-300 max-w-xs">
                          <span className="line-clamp-2">{req.text}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={clsx('text-xs px-2 py-0.5 rounded-full border font-medium', riskStyle[req.risk_level].chip)}>
                            {req.risk_level}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1.5">
                            <ConfidenceIcon score={req.confidence} />
                            <span className="text-xs text-slate-400 font-mono">{Math.round(req.confidence * 100)}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <CitationChip page={req.page_number} doc={(req as any).filename || (req as any).document_id || 'Document'} />
                        </td>
                        <td className="px-4 py-3">
                          {req.verified
                            ? <span className="flex items-center gap-1 text-xs text-emerald-400"><CheckCircle size={11} /> {req.verified_by}</span>
                            : <span className="text-xs text-slate-600">Unverified</span>
                          }
                        </td>
                      </tr>

                      {expandedReq === req.id && (
                        <tr>
                          <td colSpan={7} className="bg-brand-500/5 border-b border-border px-6 py-4">
                            <p className="text-sm text-slate-200 leading-relaxed mb-3">{req.text}</p>
                            <div className="flex items-center gap-2 text-xs text-slate-500 mb-4">
                              <FileText size={11} />
                              <span>§ {req.clause} · SPC-MECH-001 · Page {req.page_number}</span>
                              <button onClick={() => alert('PDF viewer — coming soon')} className="text-brand-400 hover:underline ml-2">Open in document →</button>
                            </div>

                            {overrideReq === req.id ? (
                              <div className="flex items-start gap-3">
                                <input
                                  value={overrideNote}
                                  onChange={e => setOverrideNote(e.target.value)}
                                  placeholder="Describe your correction or note..."
                                  className="flex-1 bg-panel border border-border rounded-lg px-3 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-brand-500"
                                />
                                <button onClick={() => handleOverride(req.id)} className="px-3 py-2 bg-brand-500 text-white text-xs rounded-lg">Save</button>
                                <button onClick={() => setOverrideReq(null)} className="px-3 py-2 border border-border text-slate-400 text-xs rounded-lg">Cancel</button>
                              </div>
                            ) : (
                              <div className="flex gap-2">
                                {!req.verified && (
                                  <button onClick={() => handleVerify(req.id)}
                                    className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-lg hover:bg-emerald-500/20 transition-colors">
                                    <ThumbsUp size={11} /> Mark verified
                                  </button>
                                )}
                                <button onClick={() => setOverrideReq(req.id)}
                                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 border border-border text-slate-400 text-xs rounded-lg hover:text-white transition-colors">
                                  <PenLine size={11} /> Override / correct
                                </button>
                              </div>
                            )}
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <div className="flex justify-end gap-3">
            <button onClick={() => { setJobStatus('idle'); setJobId(null); setRequirements([]); setContradictions([]) }}
              className="px-4 py-2 border border-border rounded-lg text-sm text-slate-400 hover:text-white transition-colors">
              Upload Another
            </button>
            <button className="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors">
              Export to Deviation Register →
            </button>
          </div>
        </div>
      )}

      {jobStatus === 'failed' && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-6 text-center">
          <p className="text-rose-400 font-medium mb-2">Analysis failed</p>
          <button onClick={() => setJobStatus('idle')} className="text-xs text-slate-400 hover:text-white">Try again</button>
        </div>
      )}
    </div>
  )
}

// ── Citation chip ─────────────────────────────────────────────────────────────

function CitationChip({ page, doc }: { page: number; doc: string }) {
  return (
    <span className="inline-flex items-center gap-1 text-xs px-1.5 py-0.5 bg-brand-500/10 border border-brand-500/20 rounded text-brand-400 font-mono cursor-pointer hover:bg-brand-500/20 transition-colors" title={`${doc}, page ${page}`}>
      <FileText size={9} />
      p.{page}
      <ExternalLink size={8} className="opacity-60" />
    </span>
  )
}
