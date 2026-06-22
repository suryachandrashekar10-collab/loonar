import { useState } from 'react'
import { Download, Filter, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react'
import clsx from 'clsx'

type Status = 'pending' | 'accepted' | 'rejected' | 'clarification'

type Deviation = {
  id: string
  clause: string
  doc: string
  customerSpec: string
  proposedDeviation: string
  justification: string
  status: Status
  impact: string
}

const DEVIATIONS: Deviation[] = [
  {
    id: 'DEV-001',
    clause: '4.2.1',
    doc: 'SPC-MECH-001',
    customerSpec: 'All pressure-containing parts shall be fabricated from ASTM A350 LF2 low-temperature carbon steel rated to -50°C.',
    proposedDeviation: 'Vendor offers ASTM A350 LF2 certified to -46°C per standard manufacturing process.',
    justification: 'ASTM A350 LF2 is certified to -46°C per standard. Extension to -50°C requires additional Charpy testing at additional cost of €12,000.',
    status: 'pending',
    impact: 'Low — 4°C margin; request buyer confirmation of operating temperature.',
  },
  {
    id: 'DEV-002',
    clause: '6.4.2',
    doc: 'SPC-QA-002',
    customerSpec: 'Safety valves shall be certified under ASME Section I (Power Boilers).',
    proposedDeviation: 'Vendor standard product line is certified under ASME Section VIII (Pressure Vessels).',
    justification: 'Section I certification requires separate valve body design, welder requalification and documentation. Lead time impact: +8 weeks.',
    status: 'rejected',
    impact: 'High — Section I requires complete re-engineering. Cost impact: €85,000.',
  },
  {
    id: 'DEV-003',
    clause: '8.2.1',
    doc: 'SPC-QA-002',
    customerSpec: 'Third-party inspection mandatory by Bureau Veritas at final assembly.',
    proposedDeviation: 'Vendor proposes SGS as alternative approved TPI agency.',
    justification: 'Bureau Veritas has 6-week scheduling backlog in vendor\'s manufacturing location. SGS offers equivalent capability and accreditation.',
    status: 'accepted',
    impact: 'None — SGS and Bureau Veritas hold equivalent UKAS accreditation.',
  },
  {
    id: 'DEV-004',
    clause: '3.1.1',
    doc: 'SPC-MECH-001',
    customerSpec: 'All flanges shall conform to ASME B16.5 Class 900 raised-face.',
    proposedDeviation: 'Vendor proposes Class 900 ring-type-joint (RTJ) face in lieu of raised face for sour service.',
    justification: 'RTJ flanges provide superior sealing in high-pressure sour service per API 6A recommendations. Equivalent or superior performance.',
    status: 'clarification',
    impact: 'Medium — Customer to confirm if RTJ is acceptable; interface with mating flanges must be checked.',
  },
]

const statusConfig: Record<Status, { label: string; icon: React.ElementType; color: string }> = {
  pending:       { label: 'Pending',       icon: Clock,        color: 'text-slate-400 bg-slate-500/10 border-slate-500/20' },
  accepted:      { label: 'Accepted',      icon: CheckCircle,  color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  rejected:      { label: 'Rejected',      icon: XCircle,      color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' },
  clarification: { label: 'Clarification', icon: AlertTriangle, color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
}

export default function DeviationRegister() {
  const [filter, setFilter] = useState<Status | 'all'>('all')

  const visible = filter === 'all' ? DEVIATIONS : DEVIATIONS.filter(d => d.status === filter)

  return (
    <div className="p-8">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-white">Deviation Register</h1>
          <p className="text-slate-400 text-sm mt-1">Auto-generated from RFQ analysis. Export directly to customer Excel template.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors">
          <Download size={14} />
          Export Excel
        </button>
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-2 mb-6">
        {(['all', 'pending', 'accepted', 'rejected', 'clarification'] as const).map(s => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={clsx(
              'px-3 py-1.5 rounded-lg text-xs font-medium transition-colors capitalize',
              filter === s
                ? 'bg-brand-500 text-white'
                : 'bg-panel border border-border text-slate-400 hover:text-white'
            )}
          >
            {s === 'all' ? `All (${DEVIATIONS.length})` : `${s} (${DEVIATIONS.filter(d => d.status === s).length})`}
          </button>
        ))}
      </div>

      {/* Deviation cards */}
      <div className="space-y-4">
        {visible.map(dev => {
          const { label, icon: Icon, color } = statusConfig[dev.status]
          return (
            <div key={dev.id} className="bg-panel border border-border rounded-xl overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between px-5 py-3 border-b border-border">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-brand-400 font-medium">{dev.id}</span>
                  <span className="text-xs text-slate-500">§ {dev.clause} · {dev.doc}</span>
                </div>
                <span className={clsx('flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border font-medium', color)}>
                  <Icon size={11} />
                  {label}
                </span>
              </div>

              {/* Body */}
              <div className="grid grid-cols-2 gap-0 divide-x divide-border">
                <div className="p-5">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Customer Specification</p>
                  <p className="text-sm text-slate-300 leading-relaxed">{dev.customerSpec}</p>
                </div>
                <div className="p-5">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Proposed Deviation</p>
                  <p className="text-sm text-slate-300 leading-relaxed">{dev.proposedDeviation}</p>
                </div>
              </div>

              {/* Footer */}
              <div className="px-5 py-3 bg-white/[0.02] border-t border-border flex items-start gap-6">
                <div className="flex-1">
                  <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Justification · </span>
                  <span className="text-xs text-slate-400">{dev.justification}</span>
                </div>
                <div className="text-right flex-shrink-0 max-w-xs">
                  <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Impact · </span>
                  <span className={clsx('text-xs', dev.status === 'rejected' ? 'text-rose-400' : 'text-slate-400')}>{dev.impact}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
