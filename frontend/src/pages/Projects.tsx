import { useState, useEffect } from 'react'
import API_URL from '../api'
import { Plus, FolderOpen, TrendingUp, Clock, ChevronRight, X } from 'lucide-react'
import clsx from 'clsx'
import { useNavigate } from 'react-router-dom'

type Project = {
  id: string
  name: string
  customer: string
  rfq_ref?: string
  value_eur?: number
  deadline?: string
  status?: 'active' | 'won' | 'lost' | 'no-bid'
  created_at?: string
}

const MOCK_PROJECTS: Project[] = [
  { id: 'proj-001', name: 'Shell LNG Terminal — Gate 4B', customer: 'Shell Energy',     rfq_ref: 'SH-LNG-2026-04B', value_eur: 4800000,  deadline: '2026-08-15', status: 'active',  created_at: '2026-06-10T09:00:00Z' },
  { id: 'proj-002', name: 'Saudi Aramco EPIC — Ras Tanura', customer: 'Saudi Aramco',   rfq_ref: 'SA-RT-EPIC-2026', value_eur: 12400000, deadline: '2026-07-30', status: 'active',  created_at: '2026-05-28T14:00:00Z' },
  { id: 'proj-003', name: 'TotalEnergies Downstream — FCC',  customer: 'TotalEnergies', rfq_ref: 'TE-FCC-2025-12',  value_eur: 2100000,  deadline: '2025-12-15', status: 'won',     created_at: '2025-10-01T08:00:00Z' },
  { id: 'proj-004', name: 'Equinor Oseberg FPSO Upgrade',    customer: 'Equinor',        rfq_ref: 'EQ-FPSO-2025-08', value_eur: 890000,   deadline: '2025-08-30', status: 'lost',    created_at: '2025-07-15T11:00:00Z' },
]

const STATUS_STYLE = {
  active:   'text-brand-400 bg-brand-500/10 border-brand-500/20',
  won:      'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  lost:     'text-rose-400 bg-rose-500/10 border-rose-500/20',
  'no-bid': 'text-slate-400 bg-slate-500/10 border-slate-500/20',
}

function CreateProjectModal({ onClose, onCreated }: { onClose: () => void; onCreated: (p: Project) => void }) {
  const [form, setForm] = useState({ name: '', customer: '', rfq_ref: '', value_eur: '', deadline: '' })
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name || !form.customer) return
    setSaving(true)
    try {
      const res = await fetch(`${API_URL}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, value_eur: form.value_eur ? parseFloat(form.value_eur) : null }),
      })
      if (res.ok) {
        onCreated(await res.json())
      } else {
        // Mock if backend not running
        onCreated({ id: crypto.randomUUID(), ...form, value_eur: parseFloat(form.value_eur) || undefined, status: 'active', created_at: new Date().toISOString() })
      }
    } catch {
      onCreated({ id: crypto.randomUUID(), ...form, value_eur: parseFloat(form.value_eur) || undefined, status: 'active', created_at: new Date().toISOString() })
    }
    setSaving(false)
    onClose()
  }

  const field = (key: keyof typeof form, label: string, type = 'text', placeholder = '') => (
    <div>
      <label className="block text-xs text-slate-400 mb-1">{label}</label>
      <input
        type={type}
        value={form[key]}
        onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
        placeholder={placeholder}
        className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-brand-500"
      />
    </div>
  )

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="bg-panel border border-border rounded-2xl w-full max-w-lg p-6 shadow-2xl">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-white">New Project</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors"><X size={18} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {field('name',      'Project Name *',          'text', 'Shell LNG Terminal — Gate 4B')}
          {field('customer',  'Customer / Owner *',      'text', 'Shell Energy B.V.')}
          {field('rfq_ref',   'RFQ Reference',           'text', 'SH-LNG-2026-04B')}
          {field('value_eur', 'Estimated Value (EUR)',   'number', '4800000')}
          {field('deadline',  'Submission Deadline',     'date')}
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 py-2 border border-border rounded-lg text-sm text-slate-400 hover:text-white transition-colors">Cancel</button>
            <button type="submit" disabled={saving || !form.name || !form.customer}
              className="flex-1 py-2 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors">
              {saving ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetch(`${API_URL}/projects`)
      .then(r => r.json())
      .then(data => setProjects(Array.isArray(data) ? data : []))
      .catch(() => setProjects([]))
      .finally(() => setLoading(false))
  }, [])

  const handleCreated = (p: Project) => setProjects(prev => [p, ...prev])

  const totalValue = projects.filter(p => p.status === 'active').reduce((s, p) => s + (p.value_eur || 0), 0)
  const wonValue   = projects.filter(p => p.status === 'won').reduce((s, p) => s + (p.value_eur || 0), 0)

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-white">Projects</h1>
          <p className="text-slate-400 text-sm mt-1">Each project is one RFQ bid. All analysis, deviations, and documents are scoped to a project.</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors">
          <Plus size={16} /> New Project
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Active pipeline', value: `€${(totalValue / 1e6).toFixed(1)}M`, sub: `${projects.filter(p => p.status === 'active').length} active bids`, icon: TrendingUp, color: 'text-brand-400' },
          { label: 'Won this year',   value: `€${(wonValue / 1e6).toFixed(1)}M`,   sub: `${projects.filter(p => p.status === 'won').length} projects`,   icon: TrendingUp, color: 'text-emerald-400' },
          { label: 'Total projects',  value: projects.length,                        sub: 'all time',                                                         icon: FolderOpen, color: 'text-slate-400' },
        ].map(({ label, value, sub, icon: Icon, color }) => (
          <div key={label} className="bg-panel border border-border rounded-xl p-4">
            <div className={`text-2xl font-semibold ${color}`}>{value}</div>
            <div className="text-xs text-slate-500 mt-0.5">{label}</div>
            <div className="text-xs text-slate-600 mt-1">{sub}</div>
          </div>
        ))}
      </div>

      {/* Project list */}
      <div className="bg-panel border border-border rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="p-12 text-center">
            <FolderOpen size={32} className="text-slate-700 mx-auto mb-3" />
            <p className="text-slate-400 font-medium">No projects yet</p>
            <p className="text-slate-600 text-sm mt-1">Create a project to start analysing RFQs</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                {['Project', 'Customer', 'RFQ Ref', 'Value', 'Deadline', 'Status', ''].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {projects.map((p, i) => (
                <tr key={p.id}
                  onClick={() => { localStorage.setItem('lastProjectId', p.id); navigate(`/rfq?project=${p.id}`) }}
                  className={clsx('cursor-pointer hover:bg-white/5 transition-colors', i < projects.length - 1 && 'border-b border-border')}>
                  <td className="px-4 py-3">
                    <div className="text-white font-medium text-sm">{p.name}</div>
                    <div className="text-xs text-slate-600 mt-0.5">{p.created_at ? new Date(p.created_at).toLocaleDateString() : ''}</div>
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{p.customer}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{p.rfq_ref || '—'}</td>
                  <td className="px-4 py-3 text-sm text-white font-medium">
                    {p.value_eur ? `€${(p.value_eur / 1e6).toFixed(1)}M` : '—'}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">
                    {p.deadline ? new Date(p.deadline).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={clsx('text-xs px-2 py-0.5 rounded-full border capitalize', STATUS_STYLE[p.status || 'active'])}>
                      {p.status || 'active'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600 hover:text-white transition-colors">
                    <ChevronRight size={16} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showCreate && <CreateProjectModal onClose={() => setShowCreate(false)} onCreated={handleCreated} />}
    </div>
  )
}
