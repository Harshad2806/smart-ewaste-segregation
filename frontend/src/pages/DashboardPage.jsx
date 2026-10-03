import {
  BarChart3, ScanSearch, TrendingUp, Target, Trash2,
  Smartphone, Laptop, Cable, Cpu, Zap, Package, Clock,
} from 'lucide-react';

const CLASS_ICON = {
  smartphones: Smartphone,
  laptops: Laptop,
  electrical_cables: Cable,
  electronic_chips: Cpu,
  small_appliances: Zap,
};

const CLASS_LABEL = {
  smartphones: 'Smartphones',
  laptops: 'Laptops',
  electrical_cables: 'Cables',
  electronic_chips: 'Chips',
  small_appliances: 'Appliances',
};

function StatCard({ icon: Icon, label, value, sub, accent = 'emerald' }) {
  const colors = {
    emerald: 'from-emerald-500/15 to-transparent text-emerald-400',
    cyan: 'from-cyan-500/15 to-transparent text-cyan-400',
    amber: 'from-amber-500/15 to-transparent text-amber-400',
    violet: 'from-violet-500/15 to-transparent text-violet-400',
  };
  return (
    <div className="glass-card p-5 relative overflow-hidden">
      <div className={`absolute inset-0 bg-gradient-to-br ${colors[accent]} opacity-30 pointer-events-none`} />
      <div className="relative">
        <div className="flex items-center gap-2 mb-3">
          <Icon className={`w-4 h-4 ${colors[accent].split(' ').pop()}`} />
          <span className="label-text">{label}</span>
        </div>
        <p className="text-2xl font-extrabold text-slate-100">{value}</p>
        {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
      </div>
    </div>
  );
}

function ClassBar({ cls, count, max }) {
  const Icon = CLASS_ICON[cls] || Package;
  const label = CLASS_LABEL[cls] || cls;
  const pct = max > 0 ? (count / max) * 100 : 0;
  return (
    <div className="flex items-center gap-3">
      <Icon className="w-4 h-4 text-slate-500 flex-shrink-0" />
      <span className="text-sm text-slate-400 w-24 truncate">{label}</span>
      <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 rounded-full transition-all duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs font-mono text-slate-500 w-8 text-right">{count}</span>
    </div>
  );
}

export default function DashboardPage({ history, stats, onClear }) {
  const maxCount = Math.max(...Object.values(stats.classCounts || {}), 1);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gradient mb-2">Dashboard</h1>
        <p className="text-slate-500 text-sm">
          Analysis statistics from your local session history.
        </p>
      </div>

      {stats.totalScans === 0 ? (
        /* ── Empty state ──────────────────────────────── */
        <div className="glass-card p-12 text-center animate-fade-in">
          <BarChart3 className="w-12 h-12 text-slate-700 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-slate-400 mb-1">No analyses yet</h2>
          <p className="text-sm text-slate-600">
            Upload and analyze e-waste images to start building your dashboard.
          </p>
        </div>
      ) : (
        <div className="space-y-6 animate-slide-up">
          {/* ── Stats grid ──────────────────────────────── */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard icon={ScanSearch}  label="Total Scans"     value={stats.totalScans} accent="emerald" />
            <StatCard icon={Target}      label="Avg Confidence"  value={`${(stats.avgConfidence * 100).toFixed(0)}%`} accent="cyan" />
            <StatCard icon={TrendingUp}  label="High Conf. Rate" value={`${(stats.highConfRate * 100).toFixed(0)}%`} accent="amber" />
            <StatCard
              icon={Package}
              label="Top Class"
              value={CLASS_LABEL[stats.topClass] || stats.topClass || '—'}
              accent="violet"
            />
          </div>

          {/* ── Class distribution ──────────────────────── */}
          <div className="glass-card p-5">
            <h3 className="section-title mb-4">
              <BarChart3 className="w-4 h-4 text-emerald-400" /> Class Distribution
            </h3>
            <div className="space-y-3">
              {Object.entries(stats.classCounts)
                .sort((a, b) => b[1] - a[1])
                .map(([cls, count]) => (
                  <ClassBar key={cls} cls={cls} count={count} max={maxCount} />
                ))}
            </div>
          </div>

          {/* ── Confidence tiers ────────────────────────── */}
          <div className="glass-card p-5">
            <h3 className="section-title mb-4">
              <Target className="w-4 h-4 text-emerald-400" /> Confidence Distribution
            </h3>
            <div className="grid grid-cols-3 gap-4">
              {[
                { tier: 'high',   color: 'emerald', label: 'High (≥80%)' },
                { tier: 'medium', color: 'amber',   label: 'Medium (55-79%)' },
                { tier: 'low',    color: 'red',      label: 'Low (<55%)' },
              ].map(({ tier, color, label }) => (
                <div key={tier} className="text-center">
                  <p className={`text-3xl font-extrabold text-${color}-400`}>
                    {stats.tierCounts[tier]}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">{label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* ── Recent history ──────────────────────────── */}
          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="section-title">
                <Clock className="w-4 h-4 text-emerald-400" /> Recent Analyses
              </h3>
              {history.length > 0 && (
                <button onClick={onClear} className="text-xs text-slate-600 hover:text-red-400 flex items-center gap-1 transition">
                  <Trash2 className="w-3.5 h-3.5" /> Clear
                </button>
              )}
            </div>
            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
              {history.slice(0, 20).map((entry) => {
                const Icon = CLASS_ICON[entry.vision?.predicted_class] || Package;
                return (
                  <div
                    key={entry.id}
                    className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/40
                               hover:bg-slate-800/70 transition"
                  >
                    <Icon className="w-4 h-4 text-slate-500 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-300 truncate">
                        {CLASS_LABEL[entry.vision?.predicted_class] || entry.vision?.predicted_class}
                      </p>
                      <p className="text-xs text-slate-600 truncate">{entry.imageName}</p>
                    </div>
                    <span className="text-xs font-mono text-slate-500">
                      {(entry.vision?.confidence * 100).toFixed(0)}%
                    </span>
                    <span className={`badge text-[10px] ${
                      entry.intelligence?.confidence_tier === 'high' ? 'badge-green' :
                      entry.intelligence?.confidence_tier === 'medium' ? 'badge-amber' : 'badge-red'
                    }`}>
                      {entry.intelligence?.confidence_tier}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
