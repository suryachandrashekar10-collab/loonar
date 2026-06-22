import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, FileSearch, AlertTriangle,
  BookOpen, GitCompare, Scale, ChevronRight
} from 'lucide-react'
import clsx from 'clsx'

const nav = [
  { to: '/dashboard',  label: 'Dashboard',         icon: LayoutDashboard },
  { to: '/rfq',        label: 'RFQ Analyzer',       icon: FileSearch },
  { to: '/deviations', label: 'Deviation Register',  icon: AlertTriangle },
  { to: '/library',    label: 'Content Library',     icon: BookOpen },
  { to: '/addendum',   label: 'Addendum Tracker',    icon: GitCompare },
  { to: '/bid-no-bid', label: 'Bid / No-Bid',        icon: Scale },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className="flex h-screen bg-surface overflow-hidden">
      {/* Sidebar */}
      <aside className="w-60 flex-shrink-0 bg-panel border-r border-border flex flex-col">
        {/* Logo */}
        <div className="px-5 py-6 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-brand-500 flex items-center justify-center">
              <span className="text-white font-bold text-sm">L</span>
            </div>
            <span className="text-white font-semibold text-base tracking-tight">Loonar</span>
          </div>
          <p className="text-xs text-slate-500 mt-1 ml-9">Industrial RFQ Intelligence</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          {nav.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
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

        {/* Footer */}
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

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
