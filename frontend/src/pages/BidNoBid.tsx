import { useState } from 'react'
import { Scale, TrendingUp, AlertTriangle, CheckCircle, XCircle, ChevronRight } from 'lucide-react'
import clsx from 'clsx'

const CRITERIA = [
  { label: 'Technical Capability',  score: 82, weight: 30, detail: 'All core requirements within standard product range. 2 high-risk deviations identified (ASME Section I, low-temp rating).' },
  { label: 'Delivery Feasibility',  score: 55, weight: 25, detail: 'Customer deadline: 26 weeks. Current factory lead time: 32 weeks at 70% capacity. Risk of LD exposure.' },
  { label: 'Commercial Margin',     score: 70, weight: 20, detail: 'Estimated GM: 28%. LD cap at 10% = €480k exposure. Net margin at risk if delivery slips.' },
  { label: 'Customer Relationship', score: 90, weight: 15, detail: 'Shell — existing Approved Vendor List. 4 successful past projects. Strong relationship.' },
  { label: 'Strategic Fit',         score: 75, weight: 10, detail: 'Core vertical (LNG upstream). Reference project value. Aligns with 2026 growth targets.' },
]

const weighted = CRITERIA.reduce((acc, c) => acc + (c.score * c.weight) / 100, 0)
const verdict = weighted >= 75 ? 'bid' : weighted >= 55 ? 'conditional' : 'no-bid'

const verdictConfig = {
  bid:         { label: 'Recommend BID',         color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30', icon: CheckCircle },
  conditional: { label: 'Conditional BID',        color: 'text-amber-400',   bg: 'bg-amber-500/10 border-amber-500/30',   icon: AlertTriangle },
  'no-bid':    { label: 'Recommend NO-BID',       color: 'text-rose-400',    bg: 'bg-rose-500/10 border-rose-500/30',     icon: XCircle },
}

function ScoreBar({ score }: { score: number }) {
  const color = score >= 75 ? 'bg-emerald-500' : score >= 55 ? 'bg-amber-500' : 'bg-rose-500'
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-border rounded-full h-1.5">
        <div className={`${color} h-1.5 rounded-full transition-all`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-xs font-mono text-slate-300 w-8 text-right">{score}</span>
    </div>
  )
}

export default function BidNoBid() {
  const [expanded, setExpanded] = useState<string | null>(null)
  const { label, color, bg, icon: VerdictIcon } = verdictConfig[verdict]

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white">Bid / No-Bid</h1>
        <p className="text-slate-400 text-sm mt-1">Weighted feasibility score based on extracted RFQ requirements and company capability profile.</p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Score panel */}
        <div className="col-span-1">
          <div className="bg-panel border border-border rounded-xl p-6 sticky top-8">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-4">RFQ</p>
            <p className="text-white font-semibold text-sm mb-1">Shell LNG Terminal — Gate 4B</p>
            <p className="text-xs text-slate-500 mb-6">Valve Package · €4.8M · Deadline 26 wks</p>

            {/* Dial */}
            <div className="flex flex-col items-center py-6">
              <div className="relative w-36 h-36">
                <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
                  <circle cx="60" cy="60" r="50" fill="none" stroke="#222840" strokeWidth="10" />
                  <circle
                    cx="60" cy="60" r="50" fill="none"
                    stroke={verdict === 'bid' ? '#10b981' : verdict === 'conditional' ? '#f59e0b' : '#f43f5e'}
                    strokeWidth="10"
                    strokeDasharray={`${(weighted / 100) * 314} 314`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold text-white">{Math.round(weighted)}</span>
                  <span className="text-xs text-slate-500">/ 100</span>
                </div>
              </div>
            </div>

            <div className={clsx('flex items-center gap-2 px-4 py-3 rounded-xl border', bg)}>
              <VerdictIcon size={16} className={color} />
              <span className={clsx('text-sm font-semibold', color)}>{label}</span>
            </div>

            <div className="mt-4 space-y-2">
              <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">Key risks</p>
              <div className="flex items-start gap-2">
                <AlertTriangle size={11} className="text-amber-400 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-slate-400">Delivery lead time exceeds deadline by 6 weeks</p>
              </div>
              <div className="flex items-start gap-2">
                <AlertTriangle size={11} className="text-amber-400 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-slate-400">ASME Section I deviation may trigger full re-engineering</p>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle size={11} className="text-emerald-400 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-slate-400">Existing AVL status reduces commercial risk</p>
              </div>
            </div>
          </div>
        </div>

        {/* Criteria breakdown */}
        <div className="col-span-2 space-y-3">
          {CRITERIA.map(c => (
            <div
              key={c.label}
              className="bg-panel border border-border rounded-xl overflow-hidden cursor-pointer"
              onClick={() => setExpanded(expanded === c.label ? null : c.label)}
            >
              <div className="flex items-center gap-4 px-5 py-4">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white">{c.label}</span>
                    <span className="text-xs text-slate-500">Weight: {c.weight}%</span>
                  </div>
                  <ScoreBar score={c.score} />
                </div>
                <ChevronRight
                  size={14}
                  className={clsx('text-slate-500 transition-transform flex-shrink-0', expanded === c.label && 'rotate-90')}
                />
              </div>
              {expanded === c.label && (
                <div className="px-5 pb-4 border-t border-border pt-3">
                  <p className="text-xs text-slate-400 leading-relaxed">{c.detail}</p>
                </div>
              )}
            </div>
          ))}

          <div className="flex justify-end gap-3 pt-2">
            <button className="px-4 py-2 border border-border rounded-lg text-sm text-slate-400 hover:text-white transition-colors">
              Save Assessment
            </button>
            <button className="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors">
              Proceed to RFQ Analysis →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
