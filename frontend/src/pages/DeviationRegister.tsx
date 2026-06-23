import { useState, useEffect } from 'react'
import API_URL from '../api'
import { Download, CheckCircle, XCircle, HelpCircle, Clock, ExternalLink } from 'lucide-react'
import clsx from 'clsx'

type Deviation = {
  id: string
  dev_id: string
  clause: string
  doc_ref: string
  customer_spec: string
  proposed_deviation: string
  justification: string
  status: 'pending' | 'accepted' | 'rejected' | 'clarification'
}

const MOCK: Deviation[] = [
  { id: 'd1', dev_id: 'DEV-001', clause: '4.2.1', doc_ref: 'SPC-MECH-001', customer_spec: 'All pressure-containing parts fabricated from ASTM A350 LF2 low-temp carbon steel rated to -50°C.', proposed_deviation: 'Standard ASTM A105 available to -29°C. ASTM A350 LF2 available on extended lead time (+4 wks). Seeking approval for A105 on non-cryogenic lines.', justification: 'Lines operating above -29°C do not require LF2 per ASME B31.3 Table A-1. LF2 applied only to cryogenic loop.', status: 'pending' },
  { id: 'd2', dev_id: 'DEV-002', clause: '9.1.2', doc_ref: 'SPC-MECH-001', customer_spec: 'All safety valves shall be certified under ASME Section I (Power Boilers).', proposed_deviation: 'Standard product certified under ASME Section VIII Div 1. Section I requires separate design qualification, welder requalification, and NDE. Lead time impact: +8 weeks.', justification: 'Section I qualification applies to fired pressure vessels. Safety valves here fall under Section VIII scope. Request technical concession.', status: 'rejected' },
  { id: 'd3', dev_id: 'DEV-003', clause: '8.3.1', doc_ref: 'SPC-MECH-001', customer_spec: 'Third-party inspection by SGS mandatory at final assembly stage.', proposed_deviation: 'Bureau Veritas proposed as equivalent TPI authority.', justification: 'Bureau Veritas holds ILAC/MRA mutual recognition with SGS. Same accreditation scope. Preferred vendor for this facility location.', status: 'accepted' },
  { id: 'd4', dev_id: 'DEV-004', clause: '6.4.2', doc_ref: 'SPC-MECH-001', customer_spec: 'Raised-face (RF) flanges conforming to ASME B16.5 Class 900. Ring-type joint (RTJ) acceptable upon written approval.', proposed_deviation: 'Requesting written confirmation: is RTJ required for all Class 900 items, or only HP gas lines above 5 bar?', justification: 'Seeking clarification to avoid unnecessary RTJ on utility lines where RF is standard and acceptable.', status: 'clarification' },
]

const STATUS_META = {
  pending:       { label: 'Pending',       icon: Clock,       style: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  accepted:      { label: 'Accepted',      icon: CheckCircle, style: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  rejected:      { label: 'Rejected',      icon: XCircle,     style: 'text-rose-400 bg-rose-500/10 border-rose-500/20' },
  clarification: { label: 'Clarification', icon: HelpCircle,  style: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
}

const FILTERS = ['all', 'pending', 'accepted', 'rejected', 'clarification'] as const

export default function DeviationRegister() {
  const [deviations, setDeviations] = useState<Deviation[]>([])
  const [filter, setFilter] = useState<typeof FILTERS[number]>('all')
  const [expanded, setExpanded] = useState<string | null>(null)
  const [exporting, setExporting] = useState(false)

  const projectId = new URLSearchParams(window.location.search).get('project') || 'demo-project'

  useEffect(() => {
    fetch(`${API_URL}/projects/${projectId}/deviations`)
      .then(r => r.json())
      .then(data => setDeviations(data.length ? data : MOCK))
      .catch(() => setDeviations(MOCK))
  }, [projectId])

  const handleStatusChange = async (id: string, status: Deviation['status']) => {
    setDeviations(prev => prev.map(d => d.id === id ? { ...d, status } : d))
    try {
      await fetch(`${API_URL}/deviations/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      })
    } catch { /* backend offline */ }
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      const res = await fetch(`${API_URL}/projects/${projectId}/deviations/export`)
      if (res.ok) {
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `deviation_register_${projectId.slice(0, 8)}.xlsx`
        a.click()
        URL.revokeObjectURL(url)
      }
    } catch { /* backend offline */ }
    setExporting(false)
  }

  const visible = filter === 'all' ? deviations : deviations.filter(d => d.status === filter)
  const counts = (['pending', 'accepted', 'rejected', 'clarification'] as const).reduce((acc, s) => {
    acc[s] = deviations.filter(d => d.status === s).length
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-white">Deviation Register</h1>
          <p className="text-slate-400 text-sm mt-1">
            AI-generated from RFQ analysis. Review each deviation, update status, and export to Excel for customer submission.
          </p>
        </div>
        <button onClick={handleExport} disabled={exporting}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white text-sm font-medium rounded-lg transition-colors">
          <Download size={15} />
          {exporting ? 'Generating...' : 'Export Excel'}
        </button>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 mb-5">
        {FILTERS.map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={clsx('px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors',
              filter === f ? 'bg-brand-500 text-white' : 'bg-panel border border-border text-slate-400 hover:text-white')}>
            {f === 'all' ? `All (${deviations.length})` : `${f} (${counts[f] || 0})`}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {visible.map(dev => {
          const meta = STATUS_META[dev.status]
          const Icon = meta.icon
          const isExpanded = expanded === dev.id

          return (
            <div key={dev.id} className="bg-panel border border-border rounded-xl overflow-hidden">
              <div className="flex items-center gap-4 px-5 py-4 cursor-pointer hover:bg-white/5 transition-colors"
                onClick={() => setExpanded(isExpanded ? null : dev.id)}>
                <span className="font-mono text-xs text-brand-400 w-16 shrink-0">{dev.dev_id}</span>
                <span className="text-xs text-slate-500 w-16 shrink-0">§ {dev.clause}</span>
                <p className="text-sm text-slate-300 flex-1 line-clamp-1">{dev.customer_spec}</p>
                <span className={clsx('flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border shrink-0', meta.style)}>
                  <Icon size={10} /> {meta.label}
                </span>
                <span className="text-slate-600 text-xs">{dev.doc_ref}</span>
              </div>

              {isExpanded && (
                <div className="border-t border-border">
                  <div className="grid grid-cols-2 divide-x divide-border">
                    <div className="p-5">
                      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Customer Specification</p>
                      <p className="text-sm text-rose-200/80 leading-relaxed bg-rose-500/5 rounded-lg p-3">{dev.customer_spec}</p>
                    </div>
                    <div className="p-5">
                      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Proposed Deviation</p>
                      <p className="text-sm text-emerald-200/80 leading-relaxed bg-emerald-500/5 rounded-lg p-3">{dev.proposed_deviation}</p>
                    </div>
                  </div>

                  <div className="border-t border-border px-5 py-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Technical Justification</p>
                    <p className="text-sm text-slate-300 leading-relaxed">{dev.justification}</p>
                  </div>

                  <div className="border-t border-border px-5 py-3 flex items-center gap-3 bg-black/20">
                    <span className="text-xs text-slate-500">Update status:</span>
                    {(['pending', 'accepted', 'rejected', 'clarification'] as const).map(s => (
                      <button key={s} onClick={() => handleStatusChange(dev.id, s)}
                        className={clsx('text-xs px-2.5 py-1 rounded-full border capitalize transition-all',
                          dev.status === s ? STATUS_META[s].style : 'border-border text-slate-500 hover:text-white')}>
                        {s}
                      </button>
                    ))}
                    <button className="ml-auto flex items-center gap-1 text-xs text-slate-500 hover:text-brand-400 transition-colors">
                      <ExternalLink size={11} /> View source §{dev.clause}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )
        })}

        {visible.length === 0 && (
          <div className="text-center py-12 text-slate-500 text-sm">No {filter} deviations.</div>
        )}
      </div>
    </div>
  )
}
