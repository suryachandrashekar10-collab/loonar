import { useState } from 'react'
import { GitCompare, AlertTriangle, CheckCircle, Upload, Loader2 } from 'lucide-react'
import clsx from 'clsx'

const CHANGES = [
  {
    id: 'CHG-001',
    section: 'SPC-MECH-001 § 4.2.1',
    type: 'material',
    severity: 'critical',
    before: 'Body material: ASTM A105 Carbon Steel (standard grade)',
    after: 'Body material: ASTM A350 LF2 Low-Temperature Carbon Steel (rated to -46°C)',
    affectedDeviations: ['DEV-001'],
    affectedProposalSections: ['Section 3 — Material Specification', 'Annex B — Deviation List'],
    action: 'Update DEV-001 justification. Recalculate material cost delta (~€8,500 uplift).',
  },
  {
    id: 'CHG-002',
    section: 'SPC-QA-002 § 6.1',
    type: 'testing',
    severity: 'high',
    before: 'Safety valves: ASME Section VIII certification acceptable.',
    after: 'Safety valves: ASME Section I certification MANDATORY for all pressure-relief devices.',
    affectedDeviations: ['DEV-002'],
    affectedProposalSections: ['Section 5 — Quality & Testing', 'Commercial Schedule B'],
    action: 'DEV-002 status changes from Pending to Critical. Engineering must assess Section I redesign feasibility.',
  },
  {
    id: 'CHG-003',
    section: 'Commercial Terms § 12.4',
    type: 'commercial',
    severity: 'medium',
    before: 'Liquidated damages: 0.5% per week, capped at 5% of contract value.',
    after: 'Liquidated damages: 1.0% per week, capped at 10% of contract value.',
    affectedDeviations: [],
    affectedProposalSections: ['Section 7 — Commercial Terms', 'Risk Register'],
    action: 'Update risk register. Delivery schedule must be reviewed — current lead time leaves 2-week buffer only.',
  },
]

const severityColor = {
  critical: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
  high:     'text-amber-400 bg-amber-500/10 border-amber-500/30',
  medium:   'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
  low:      'text-slate-400 bg-slate-500/10 border-slate-500/20',
}

export default function AddendumTracker() {
  const [stage, setStage] = useState<'idle' | 'processing' | 'done'>('idle')

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white">Addendum Tracker</h1>
        <p className="text-slate-400 text-sm mt-1">Upload a revised RFQ document. Every changed clause is diffed and mapped to affected proposal sections and deviations.</p>
      </div>

      {stage === 'idle' && (
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="bg-panel border border-border rounded-xl p-6">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-3">Original Document</p>
            <div className="flex items-center gap-3 p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-lg">
              <CheckCircle size={14} className="text-emerald-400" />
              <span className="text-sm text-slate-300">SPC-MECH-001 Rev 2 — loaded</span>
            </div>
          </div>
          <div
            className="bg-panel border border-dashed border-border rounded-xl p-6 cursor-pointer hover:border-brand-500/50 transition-colors"
            onClick={() => { setStage('processing'); setTimeout(() => setStage('done'), 2500) }}
          >
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-3">Revised Document (Addendum)</p>
            <div className="flex items-center gap-3 p-3 bg-white/5 border border-border rounded-lg hover:bg-brand-500/5 transition-colors">
              <Upload size={14} className="text-slate-500" />
              <span className="text-sm text-slate-500">Drop Addendum 03 here or click to upload</span>
            </div>
          </div>
        </div>
      )}

      {stage === 'processing' && (
        <div className="bg-panel border border-border rounded-2xl p-12 flex flex-col items-center gap-4 mb-6">
          <Loader2 size={28} className="text-brand-400 animate-spin" />
          <p className="text-white font-medium">Diffing documents...</p>
          <p className="text-slate-500 text-sm">Mapping changes to proposal sections and deviation register</p>
        </div>
      )}

      {stage === 'done' && (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl mb-6">
            <AlertTriangle size={16} className="text-amber-400 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-amber-300">Addendum 03 processed — {CHANGES.length} changes detected</p>
              <p className="text-xs text-amber-500/70 mt-0.5">2 deviations affected · 5 proposal sections require update</p>
            </div>
          </div>

          {CHANGES.map(chg => (
            <div key={chg.id} className="bg-panel border border-border rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-5 py-3 border-b border-border">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-brand-400">{chg.id}</span>
                  <span className="text-xs text-slate-500">{chg.section}</span>
                  <span className="text-xs px-1.5 py-0.5 bg-white/5 border border-border rounded text-slate-500 capitalize">{chg.type}</span>
                </div>
                <span className={clsx('text-xs px-2.5 py-1 rounded-full border font-medium capitalize', severityColor[chg.severity as keyof typeof severityColor])}>
                  {chg.severity}
                </span>
              </div>

              <div className="grid grid-cols-2 divide-x divide-border">
                <div className="p-4">
                  <p className="text-xs text-rose-400 font-medium mb-2">— Removed</p>
                  <p className="text-xs text-slate-400 leading-relaxed bg-rose-500/5 rounded-lg p-3 border border-rose-500/10">{chg.before}</p>
                </div>
                <div className="p-4">
                  <p className="text-xs text-emerald-400 font-medium mb-2">+ Added</p>
                  <p className="text-xs text-slate-300 leading-relaxed bg-emerald-500/5 rounded-lg p-3 border border-emerald-500/10">{chg.after}</p>
                </div>
              </div>

              <div className="px-5 py-3 bg-white/[0.02] border-t border-border space-y-2">
                <div className="flex flex-wrap gap-x-6 gap-y-1">
                  {chg.affectedDeviations.length > 0 && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-500">Affected deviations:</span>
                      {chg.affectedDeviations.map(d => (
                        <span key={d} className="text-xs text-amber-400 font-mono">{d}</span>
                      ))}
                    </div>
                  )}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-slate-500">Affected sections:</span>
                    {chg.affectedProposalSections.map(s => (
                      <span key={s} className="text-xs text-slate-400">{s}</span>
                    ))}
                  </div>
                </div>
                <p className="text-xs text-brand-300">→ {chg.action}</p>
              </div>
            </div>
          ))}

          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={() => setStage('idle')}
              className="px-4 py-2 border border-border rounded-lg text-sm text-slate-400 hover:text-white transition-colors"
            >
              Upload Another Addendum
            </button>
            <button className="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors">
              Update Deviation Register →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
