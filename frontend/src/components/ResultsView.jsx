import {
  Recycle, ShieldCheck, Wrench, RotateCcw, Zap, AlertTriangle,
  Cpu, Smartphone, Laptop, Cable, ChevronDown,
  Leaf, Package, FlaskConical, BadgeInfo, Factory, MessageSquareText,
} from 'lucide-react';
import { useState } from 'react';

/* ────────────────────────────────────────────────────────────
   CLASS → ICON / COLOR mappings
   ──────────────────────────────────────────────────────────── */
const CLASS_META = {
  smartphones:       { icon: Smartphone, color: 'cyan',    label: 'Smartphone' },
  laptops:           { icon: Laptop,     color: 'emerald', label: 'Laptop' },
  electrical_cables: { icon: Cable,      color: 'amber',   label: 'Electrical Cable' },
  electronic_chips:  { icon: Cpu,        color: 'violet',  label: 'Electronic Chip' },
  small_appliances:  { icon: Zap,        color: 'orange',  label: 'Small Appliance' },
};

const tierColor = (t) =>
  t === 'high' ? 'text-emerald-400' : t === 'medium' ? 'text-amber-400' : 'text-red-400';
const tierBadge = (t) =>
  t === 'high' ? 'badge-green' : t === 'medium' ? 'badge-amber' : 'badge-red';
const riskBadge = (l) =>
  l === 'low' ? 'badge-green' : l === 'medium' ? 'badge-amber' : 'badge-red';

/* ────────────────────────────────────────────────────────────
   CONFIDENCE RING (SVG)
   ──────────────────────────────────────────────────────────── */
function ConfidenceRing({ confidence, tier }) {
  const size = 140;
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - confidence);

  const ringColor =
    tier === 'high'
      ? 'stroke-emerald-400'
      : tier === 'medium'
        ? 'stroke-amber-400'
        : 'stroke-red-400';

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" strokeWidth={stroke}
          className="stroke-slate-800"
        />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" strokeWidth={stroke} strokeLinecap="round"
          className={`confidence-ring-fg ${ringColor}`}
          style={{
            '--ring-circumference': circumference,
            '--ring-offset': offset,
            strokeDasharray: circumference,
            strokeDashoffset: offset,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-extrabold ${tierColor(tier)}`}>
          {(confidence * 100).toFixed(0)}%
        </span>
        <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mt-0.5">
          confidence
        </span>
      </div>
    </div>
  );
}

/* ────────────────────────────────────────────────────────────
   PROFILE QUICK-FACT CARDS
   ──────────────────────────────────────────────────────────── */
function QuickFact({ icon: Icon, label, value, badgeClass }) {
  return (
    <div className="glass-card-sm p-3 flex items-start gap-3">
      <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0 mt-0.5">
        <Icon className="w-4 h-4 text-slate-400" />
      </div>
      <div>
        <p className="label-text">{label}</p>
        {badgeClass ? (
          <span className={`badge mt-1 ${badgeClass}`}>{value}</span>
        ) : (
          <p className="text-sm font-semibold text-slate-200 mt-0.5">{value}</p>
        )}
      </div>
    </div>
  );
}

/* ────────────────────────────────────────────────────────────
   RECOVERY PATHWAY (TIMELINE)
   ──────────────────────────────────────────────────────────── */
function RecoveryPathway({ steps }) {
  if (!steps || steps.length === 0) return null;
  return (
    <div className="space-y-0">
      {steps.map((step, i) => (
        <div key={i} className="flex gap-3">
          {/* vertical line + dot */}
          <div className="flex flex-col items-center">
            <div className="w-7 h-7 rounded-full bg-emerald-500/15 border border-emerald-500/30
                            flex items-center justify-center flex-shrink-0 text-xs font-bold text-emerald-400">
              {i + 1}
            </div>
            {i < steps.length - 1 && (
              <div className="w-px flex-1 bg-gradient-to-b from-emerald-500/30 to-transparent min-h-[24px]" />
            )}
          </div>
          <p className="text-sm text-slate-300 pt-1 pb-4 leading-relaxed">{step}</p>
        </div>
      ))}
    </div>
  );
}

/* ────────────────────────────────────────────────────────────
   AI REASONING ACCORDION
   ──────────────────────────────────────────────────────────── */
function ReasoningSection({ icon: Icon, title, content, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  if (!content) return null;
  return (
    <div className="border-b border-slate-800/60 last:border-0">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 py-3 px-1 text-left
                   hover:bg-slate-800/30 transition rounded-lg group"
      >
        <Icon className="w-4 h-4 text-slate-500 flex-shrink-0" />
        <span className="text-sm font-medium text-slate-300 flex-1">{title}</span>
        <ChevronDown
          className={`w-4 h-4 text-slate-600 transition-transform duration-200 ${
            open ? 'rotate-180' : ''
          }`}
        />
      </button>
      {open && (
        <div className="pb-4 pl-8 pr-2 text-sm text-slate-400 leading-relaxed animate-fade-in">
          {content}
        </div>
      )}
    </div>
  );
}

/* ────────────────────────────────────────────────────────────
   MAIN RESULTS VIEW
   ──────────────────────────────────────────────────────────── */
export default function ResultsView({ result }) {
  if (!result) return null;

  const { vision, intelligence } = result;
  const cls = vision.predicted_class;
  const meta = CLASS_META[cls] || { icon: Package, color: 'slate', label: cls };
  const Icon = meta.icon;
  const profile = intelligence.profile;
  const recovery = intelligence.recovery_recommendation;
  const ai = intelligence.ai_reasoning;

  return (
    <div className="space-y-6 animate-slide-up">
      {/* ── Hero: Class + Confidence ─────────────────────── */}
      <div className="glass-card p-6 flex flex-col sm:flex-row items-center gap-6">
        <ConfidenceRing confidence={vision.confidence} tier={intelligence.confidence_tier} />

        <div className="flex-1 text-center sm:text-left">
          <div className="flex items-center gap-2 justify-center sm:justify-start mb-1">
            <span className={`badge ${tierBadge(intelligence.confidence_tier)}`}>
              {intelligence.confidence_tier} confidence
            </span>
            {!vision.is_confident && (
              <span className="badge badge-amber">
                <AlertTriangle className="w-3 h-3" /> Needs verification
              </span>
            )}
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-50 flex items-center gap-3 justify-center sm:justify-start mt-2">
            <Icon className="w-8 h-8 text-emerald-400" />
            {meta.label}
          </h2>
          {profile && (
            <p className="text-sm text-slate-500 mt-1">{profile.category}</p>
          )}
        </div>
      </div>

      {/* ── Profile Quick Facts ──────────────────────────── */}
      {profile && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <QuickFact icon={Recycle}      label="Recycling Stream" value={recovery.recycling_stream} />
          <QuickFact icon={RotateCcw}    label="Reuse Potential"  value={profile.reuse_potential}   badgeClass={profile.reuse_potential === 'high' ? 'badge-green' : profile.reuse_potential === 'moderate' ? 'badge-amber' : 'badge-red'} />
          <QuickFact icon={Wrench}       label="Repairability"    value={profile.repairability}     badgeClass={profile.repairability === 'moderate' ? 'badge-amber' : profile.repairability === 'none' ? 'badge-red' : 'badge-green'} />
          <QuickFact icon={ShieldCheck}  label="Risk Level"       value={profile.risk_level}        badgeClass={riskBadge(profile.risk_level)} />
        </div>
      )}

      {/* ── Materials & Components ───────────────────────── */}
      {profile && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="glass-card p-5">
            <h3 className="section-title mb-3">
              <FlaskConical className="w-4 h-4 text-emerald-400" /> Materials
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {profile.materials.map((m, i) => (
                <span key={i} className="badge badge-cyan text-[10px]">{m}</span>
              ))}
            </div>
          </div>
          <div className="glass-card p-5">
            <h3 className="section-title mb-3">
              <Package className="w-4 h-4 text-emerald-400" /> Components
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {profile.components.map((c, i) => (
                <span key={i} className="badge bg-slate-800 text-slate-400 ring-1 ring-slate-700 text-[10px]">{c}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Recovery Pathway ─────────────────────────────── */}
      {recovery && recovery.recovery_pathway?.length > 0 && (
        <div className="glass-card p-5">
          <h3 className="section-title mb-4">
            <Factory className="w-4 h-4 text-emerald-400" /> Recovery Pathway
          </h3>
          <RecoveryPathway steps={recovery.recovery_pathway} />
        </div>
      )}

      {/* ── Safety / Safe Handling ────────────────────────── */}
      {recovery && recovery.safe_handling?.length > 0 && (
        <div className="glass-card p-5 border-amber-500/20">
          <h3 className="section-title mb-3 text-amber-400">
            <AlertTriangle className="w-4 h-4" /> Safety & Handling
          </h3>
          <ul className="space-y-2">
            {recovery.safe_handling.map((s, i) => (
              <li key={i} className="flex gap-2 text-sm text-slate-400">
                <ShieldCheck className="w-4 h-4 text-amber-500/60 flex-shrink-0 mt-0.5" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── AI Reasoning ─────────────────────────────────── */}
      {ai && (
        <div className="glass-card p-5">
          <h3 className="section-title mb-2">
            <MessageSquareText className="w-4 h-4 text-emerald-400" /> AI Analysis
          </h3>
          <ReasoningSection icon={BadgeInfo}         title="Assessment"               content={ai.assessment}               defaultOpen={true} />
          <ReasoningSection icon={RotateCcw}         title="Reuse Recommendation"     content={ai.reuse_recommendation}     />
          <ReasoningSection icon={Wrench}            title="Repair Recommendation"    content={ai.repair_recommendation}    />
          <ReasoningSection icon={Factory}           title="Recovery Pathway"          content={ai.recovery_pathway}         />
          <ReasoningSection icon={Recycle}            title="Recycling Recommendation" content={ai.recycling_recommendation} />
          <ReasoningSection icon={AlertTriangle}     title="Risk Summary"             content={ai.risk_summary}             />
          <ReasoningSection icon={MessageSquareText} title="User Explanation"          content={ai.user_explanation}         defaultOpen={true} />
        </div>
      )}

      {/* ── Reasoning Basis ──────────────────────────────── */}
      {intelligence.reasoning && (
        <div className="glass-card-sm p-4 border-l-2 border-emerald-500/40">
          <p className="label-text mb-1">Reasoning Basis</p>
          <p className="text-sm text-slate-400 leading-relaxed italic">
            {intelligence.reasoning}
          </p>
        </div>
      )}
    </div>
  );
}
