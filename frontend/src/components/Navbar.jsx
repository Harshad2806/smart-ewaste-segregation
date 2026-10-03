import { NavLink } from 'react-router-dom';
import { Leaf, ScanSearch, LayoutDashboard, Camera } from 'lucide-react';

const links = [
  { to: '/', label: 'Analyze', icon: ScanSearch },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/camera', label: 'Camera', icon: Camera },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <NavLink to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500
                            flex items-center justify-center shadow-lg shadow-emerald-500/20
                            group-hover:shadow-emerald-500/40 transition-shadow">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <span className="text-base font-bold text-gradient">Smart E-Waste</span>
              <span className="text-[10px] block -mt-1 text-slate-500 font-medium tracking-wider uppercase">
                AI Segregation System
              </span>
            </div>
          </NavLink>

          {/* Navigation */}
          <nav className="flex items-center gap-1">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-emerald-500/10 text-emerald-400'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
