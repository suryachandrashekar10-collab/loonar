import { useState } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import {
  LayoutDashboard, FolderOpen, FileSearch, AlertTriangle,
  BookOpen, GitCompare, Scale, ChevronRight, Menu, X
} from 'lucide-react'
import clsx from 'clsx'

const nav = [
  { to: '/dashboard',  label: 'Dashboard',         icon: LayoutDashboard },
  { to: '/projects',   label: 'Projects',           icon: FolderOpen },
  { to: '/rfq',        label: 'RFQ Analyzer',       icon: FileSearch },
  { to: '/deviations', label: 'Deviation Register',  icon: AlertTriangle },
  { to: '/library',    label: 'Content Library',     icon: BookOpen },
  { to: '/addendum',   label: 'Addendum Tracker',    icon: GitCompare },
  { to: '/bid-no-bid', label: 'Bid / No-Bid',        icon: Scale },
]

function Sidebar({ onClose }: { onClose?: () => void }) {
  return (
    <aside className="w-60 flex-shrink-0 bg-panel border-r border-border flex flex-col h-full">
      <div className="px-5 py-6 border-b border-border flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-brand-500 flex items-center justify-center">
              <span className="text-white font-bold text-sm">L</span>
            </div>
            <span className="text-white font-semibold text-base tracking-tight">Loonar</span>
          </div>
          <p className="text-xs text-slate-500 mt-1 ml-9">Industrial RFQ Intelligence</p>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors md:hidden">
            <X size={18} />
          </button>
        )}
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all group',
                isActive
                  ? 'bg-brand-500/10 text-brand-400 font-medium'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={16} className={isActive ? 'text-brand-400' : 'text-slate-500 group-hover:text-slate-300'} />
                <span className="flex-1">{label}</span>
                {isActive && <ChevronRight size={12} className="text-brand-400" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-4 border-t border-border">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center">
            <span className="text-xs text-slate-300 font-medium">SC</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-slate-200 font-medium truncate">Surya C.</p>
            <p className="text-xs text-slate-500 truncate">Commercial Team</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="flex h-screen bg-surface overflow-hidden">
      {/* Desktop sidebar */}
      <div className="hidden md:flex">
        <Sidebar />
      </div>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div className="fixed inset-0 bg-black/60" onClick={() => setMobileOpen(false)} />
          <div className="relative z-10 flex">
            <Sidebar onClose={() => setMobileOpen(false)} />
          </div>
        </div>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile top bar */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 bg-panel border-b border-border flex-shrink-0">
          <button onClick={() => setMobileOpen(true)} className="text-slate-400 hover:text-white transition-colors">
            <Menu size={20} />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-brand-500 flex items-center justify-center">
              <span className="text-white font-bold text-xs">L</span>
            </div>
            <span className="text-white font-semibold text-sm">Loonar</span>
          </div>
        </div>

        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
