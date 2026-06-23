import { useState, useEffect } from 'react'
import { FileSearch, AlertTriangle, BookOpen, GitCompare, Scale, TrendingUp, Clock, Target } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import API_URL from '../api'

const modules = [
  {
    to: '/rfq',
    icon: FileSearch,
    label: 'RFQ Analyzer',
    desc: 'Upload RFQ packages. Extract requirements, detect cross-document contradictions, cite sources.',
    color: 'bg-brand-500/10 text-brand-400',
    badge: 'Core',
  },
  {
    to: '/deviations',
    icon: AlertTriangle,
    label: 'Deviation Register',
    desc: 'Auto-generated Excel-ready deviation list with clause references and technical justifications.',
    color: 'bg-amber-500/10 text-amber-400',
    badge: 'Critical',
  },
  {
    to: '/library',
    icon: BookOpen,
    label: 'Content Library',
    desc: 'Semantic search across past proposals, manuals, and supplier offers. Ask in natural language.',
    color: 'bg-emerald-500/10 text-emerald-400',
    badge: 'Reuse',
  },
  {
    to: '/addendum',
    icon: GitCompare,
    label: 'Addendum Tracker',
    desc: 'Mid-bid revision detection. Flags exactly which proposal sections and deviation rows are affected.',
    color: 'bg-purple-500/10 text-purple-400',
    badge: 'Unique',
  },
  {
    to: '/bid-no-bid',
    icon: Scale,
    label: 'Bid / No-Bid',
    desc: '5-minute feasibility score. Technical fit, delivery risk, and commercial exposure at a glance.',
    color: 'bg-rose-500/10 text-rose-400',
    badge: 'Strategy',
  },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<any[]>([])

  useEffect(() => {
    fetch(`${API_URL}/projects`)
      .then(r => r.json())
      .then(data => setProjects(Array.isArray(data) ? data : []))
      .catch(() => {})
  }, [])

  const activeRFQs = projects.filter(p => p.status === 'active').length
  const openDeviations = projects.reduce((sum, p) => sum + (p.pending_deviations || 0), 0)

  const stats = [
    { label: 'Active RFQs',       value: String(activeRFQs),    delta: `${projects.length} total projects`, icon: FileSearch,    color: 'text-brand-400' },
    { label: 'Open Deviations',   value: String(openDeviations), delta: 'across all projects',              icon: AlertTriangle, color: 'text-amber-400' },
    { label: 'Library Documents', value: '0',                    delta: 'upload to grow library',           icon: BookOpen,      color: 'text-emerald-400' },
    { label: 'Pending Addenda',   value: '0',                    delta: 'no addenda tracked yet',           icon: GitCompare,    color: 'text-rose-400' },
  ]

  const recentActivity = projects.length > 0
    ? projects.slice(0, 4).map(p => ({
        time: p.created_at ? new Date(p.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) : '',
        text: `Project '${p.name}' — ${p.requirement_count ?? 0} requirements extracted`,
        type: 'info' as const,
      }))
    : []

  return (
    <div className="p-4 md:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-white">Overview</h1>
        <p className="text-slate-400 text-sm mt-1">
          Industrial RFQ intelligence platform — {new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' })}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map(({ label, value, delta, icon: Icon, color }) => (
          <div key={label} className="bg-panel border border-border rounded-xl p-5">
            <div className="flex items-start justify-between mb-3">
              <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">{label}</span>
              <Icon size={16} className={color} />
            </div>
            <div className="text-3xl font-semibold text-white mb-1">{value}</div>
            <div className="text-xs text-slate-500">{delta}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Modules grid */}
        <div className="lg:col-span-2">
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">Modules</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {modules.map(({ to, icon: Icon, label, desc, color, badge }) => (
              <button
                key={to}
                onClick={() => navigate(to)}
                className="bg-panel border border-border rounded-xl p-5 text-left hover:border-brand-500/40 hover:bg-brand-500/5 transition-all group"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${color}`}>
                    <Icon size={18} />
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-slate-400 border border-border">{badge}</span>
                </div>
                <h3 className="text-sm font-semibold text-white mb-1 group-hover:text-brand-300 transition-colors">{label}</h3>
                <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Activity feed */}
        <div>
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">Recent Activity</h2>
          <div className="bg-panel border border-border rounded-xl p-4 space-y-4">
            {recentActivity.length > 0 ? recentActivity.map((item, i) => (
              <div key={i} className="flex gap-3">
                <div className={`mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                  (item.type as string) === 'warning' ? 'bg-amber-400' :
                  (item.type as string) === 'success' ? 'bg-emerald-400' : 'bg-brand-400'
                }`} />
                <div>
                  <p className="text-xs text-slate-300 leading-relaxed">{item.text}</p>
                  <p className="text-xs text-slate-600 mt-0.5">{item.time}</p>
                </div>
              </div>
            )) : (
              <p className="text-xs text-slate-500">No recent activity.</p>
            )}
          </div>

          {/* Key metric */}
          <div className="mt-4 bg-panel border border-border rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp size={14} className="text-emerald-400" />
              <span className="text-xs font-medium text-slate-300">Win Rate Impact</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Without AI</span>
                <span className="text-slate-400">5–15%</span>
              </div>
              <div className="w-full bg-border rounded-full h-1.5">
                <div className="bg-rose-500 h-1.5 rounded-full" style={{ width: '10%' }} />
              </div>
              <div className="flex justify-between text-xs mt-2">
                <span className="text-slate-500">With Loonar</span>
                <span className="text-emerald-400">20–35%</span>
              </div>
              <div className="w-full bg-border rounded-full h-1.5">
                <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: '28%' }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
