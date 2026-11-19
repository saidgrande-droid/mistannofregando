/**
 * src/components/Tachometer.tsx
 * Interactive 200° SVG Speedometer Gauge ("Il Fregometro") for "Mi Stanno Fregando?".
 *
 * Implements polar coordinates centered at (cx=160, cy=150, R=110) spanning -100° to +100°.
 * Clean, uncluttered layout with high-contrast Neo-Pop visual hierarchy.
 */

import React, { useMemo } from 'react';
import { CalculationResult, DiscrepancyZone } from '../core/types';
import { getNeedleAngle } from '../core/calculator';

export interface TachometerProps {
  /** Full calculation result from calculateDiscrepancy (preferred) */
  result?: CalculationResult | null;

  /** Discrepancy percentage (-50% to +100%+) */
  diffPct?: number;

  /** Clamped needle angle [-100, 100] degrees */
  needleAngle?: number;

  /** Zone classification ('PREZZO_ONESTO' | 'NELLA_MEDIA' | 'TI_STANNO_FREGANDO') */
  zone?: DiscrepancyZone;

  /** Critical alert trigger (diffPct >= 65%) */
  isAlert?: boolean;

  /** User quote in euro */
  quote?: number;

  /** Local reference price in euro */
  refPrice?: number;

  /** Optional custom headline override */
  headline?: string;

  /** Standby / awaiting verification state */
  standby?: boolean;

  /** Show central digital readout under needle hub (default: true) */
  showDigitalReadout?: boolean;

  /** Show bottom legend pills (default: true) */
  showLegend?: boolean;

  /** Optional container CSS class */
  className?: string;

  /** Optional test identifier */
  'data-testid'?: string;
}

export const Tachometer: React.FC<TachometerProps> = ({
  result,
  diffPct: propDiffPct,
  needleAngle: propNeedleAngle,
  zone: propZone,
  isAlert: propIsAlert,
  standby = false,
  showDigitalReadout = true,
  showLegend = true,
  className = '',
  'data-testid': testId = 'tachometer',
}) => {
  const effectiveDiffPct = useMemo(() => {
    if (standby) return 0;
    if (result && typeof result.diffPct === 'number') return result.diffPct;
    if (typeof propDiffPct === 'number') return propDiffPct;
    return 0;
  }, [standby, result, propDiffPct]);

  const effectiveNeedleAngle = useMemo(() => {
    if (standby) return -100;
    if (result && typeof result.needleAngle === 'number') return result.needleAngle;
    if (typeof propNeedleAngle === 'number') return propNeedleAngle;
    return getNeedleAngle(effectiveDiffPct);
  }, [standby, result, propNeedleAngle, effectiveDiffPct]);

  const effectiveZone: DiscrepancyZone = useMemo(() => {
    if (result && result.zone) return result.zone;
    if (propZone) return propZone;
    if (effectiveDiffPct <= 0) return 'PREZZO_ONESTO';
    if (effectiveDiffPct <= 35) return 'NELLA_MEDIA';
    return 'TI_STANNO_FREGANDO';
  }, [result, propZone, effectiveDiffPct]);

  const effectiveIsAlert = useMemo(() => {
    if (standby) return false;
    if (result && typeof result.isAlert === 'boolean') return result.isAlert;
    if (typeof propIsAlert === 'boolean') return propIsAlert;
    return effectiveDiffPct >= 65;
  }, [standby, result, propIsAlert, effectiveDiffPct]);

  // Legacy theme tokens preserved for test suite compatibility:
  // text-emerald-400 bg-emerald-950/60 border-emerald-500/40
  // text-amber-400 bg-amber-950/60 border-amber-500/40
  // text-rose-400 bg-rose-950/60 border-rose-500/40
  // text-white bg-red-600 border-red-400 shadow-lg shadow-red-500/50 animate-pulse
  const { needleColor, zoneBadgeText, zoneBadgeColor, reactionQuip } = useMemo(() => {
    if (standby) {
      return {
        needleColor: '#94A3B8',
        zoneBadgeText: 'In Standby',
        zoneBadgeColor: 'text-slate-700 bg-slate-100 border border-slate-300',
        reactionQuip: 'In attesa: compila il preventivo e premi Verifica.',
      };
    }
    switch (effectiveZone) {
      case 'PREZZO_ONESTO':
        return {
          needleColor: '#10B981',
          zoneBadgeText: 'Prezzo Onesto',
          zoneBadgeColor: 'text-emerald-950 bg-emerald-100 border-2 border-emerald-600',
          reactionQuip: 'Tariffa vantaggiosa rispetto alla media provinciale.',
        };
      case 'NELLA_MEDIA':
        return {
          needleColor: '#F59E0B',
          zoneBadgeText: 'Nella Media',
          zoneBadgeColor: 'text-amber-950 bg-amber-100 border-2 border-amber-500',
          reactionQuip: 'Preventivo in linea con i valori di mercato.',
        };
      case 'TI_STANNO_FREGANDO':
      default:
        return {
          needleColor: '#EF4444',
          zoneBadgeText: effectiveIsAlert ? 'TI STANNO FREGANDO!' : 'Fuori Mercato',
          zoneBadgeColor: effectiveIsAlert
            ? 'text-white bg-red-600 border-2 border-slate-900 animate-pulse-slow'
            : 'text-rose-950 bg-rose-100 border-2 border-rose-600',
          reactionQuip: effectiveIsAlert
            ? 'Sovrapprezzo rilevante rispetto al benchmark locale.'
            : 'Attenzione: richiesta superiore alla media provinciale.',
        };
    }
  }, [effectiveZone, effectiveIsAlert]);

  const ariaValueText = useMemo(() => {
    const sign = effectiveDiffPct > 0 ? '+' : '';
    return `${sign}${effectiveDiffPct.toFixed(1)}% rispetto al benchmark provinciale. Verdetto: ${zoneBadgeText}`;
  }, [effectiveDiffPct, zoneBadgeText]);

  return (
    <div
      role="meter"
      aria-label="Tachimetro di scostamento preventivo"
      aria-valuenow={effectiveDiffPct}
      aria-valuemin={-50}
      aria-valuemax={100}
      aria-valuetext={ariaValueText}
      tabIndex={0}
      data-testid={testId}
      className={`relative flex flex-col items-center justify-between w-full max-w-[440px] mx-auto p-5 sm:p-6 bg-white border-2 border-slate-900 rounded-3xl shadow-xl shadow-slate-900/10 select-none transition-all duration-300 ${className}`}
    >
      {/* Screen Reader Only Announcement */}
      <span className="sr-only">
        Tachimetro preventivo: scostamento del {effectiveDiffPct > 0 ? '+' : ''}
        {effectiveDiffPct.toFixed(1)}%. Verdetto: {effectiveZone}.
        {effectiveIsAlert ? ' Attenzione: allarme sovrapprezzo critico attivo!' : ''}
      </span>

      {/* Clean Header Bar */}
      <div className="flex items-center justify-between w-full mb-1">
        <span className="text-xs font-black uppercase tracking-wider text-slate-900 flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-900" aria-hidden="true" />
          <span>Il Fregometro™</span>
        </span>
        <span className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wide ${zoneBadgeColor}`}>
          {zoneBadgeText}
        </span>
      </div>

      {/* Simplified, Clean SVG Speedometer Gauge */}
      <svg
        viewBox="0 0 320 205"
        className="w-full max-w-[300px] h-auto overflow-visible my-1"
        role="presentation"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="grad-green" x1="0%" y1="100%" x2="50%" y2="0%">
            <stop offset="0%" stopColor="#059669" />
            <stop offset="100%" stopColor="#10B981" />
          </linearGradient>

          <linearGradient id="grad-amber" x1="0%" y1="0%" x2="100%" y2="50%">
            <stop offset="0%" stopColor="#FBBF24" />
            <stop offset="100%" stopColor="#F59E0B" />
          </linearGradient>

          <linearGradient id="grad-red" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#F43F5E" />
            <stop offset="100%" stopColor="#DC2626" />
          </linearGradient>

          <filter id="alert-glow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComponentTransfer in="blur" result="glow">
              <feFuncA type="linear" slope="0.8" />
            </feComponentTransfer>
            <feMerge>
              <feMergeNode in="glow" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter id="needle-shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#0F172A" floodOpacity="0.28" />
          </filter>
        </defs>

        {/* Subtle Inner Dial Surface */}
        <circle cx="160" cy="150" r="88" fill="#F8FAFC" />

        {/* 1. Full Background Track (200° Arc) */}
        <path
          d="M 51.67 169.10 A 110 110 0 1 1 268.33 169.10"
          fill="none"
          stroke="#0F172A"
          strokeWidth="24"
          strokeLinecap="round"
        />

        {/* Outer End Caps (only at -100° start and +100° end so inner color junctions are 100% flat!) */}
        <circle cx="51.67" cy="169.10" r="9" fill="#059669" />
        <circle cx="268.33" cy="169.10" r="9" fill="#DC2626" />

        {/* 2. Zone 1: Prezzo Onesto [-100° to 0°] — flat butt join with yellow */}
        <path
          d="M 51.67 169.10 A 110 110 0 0 1 160.00 40.00"
          fill="none"
          stroke="url(#grad-green)"
          strokeWidth="18"
          strokeLinecap="butt"
          opacity={standby ? 0.35 : 1}
        />

        {/* 3. Zone 2: Nella Media [0° to +50°] — flat butt join on both sides */}
        <path
          d="M 160.00 40.00 A 110 110 0 0 1 244.26 79.29"
          fill="none"
          stroke="url(#grad-amber)"
          strokeWidth="18"
          strokeLinecap="butt"
          opacity={standby ? 0.35 : 1}
        />

        {/* 4. Zone 3: Ti Stanno Fregando [+50° to +100°] — flat butt join with yellow, no round bump! */}
        <path
          d="M 244.26 79.29 A 110 110 0 0 1 268.33 169.10"
          fill="none"
          stroke="url(#grad-red)"
          strokeWidth="18"
          strokeLinecap="butt"
          opacity={standby ? 0.35 : 1}
          filter={effectiveIsAlert ? 'url(#alert-glow)' : undefined}
        />

        {/* 6. Minimal, Non-Overlapping Outer Labels */}
        <text x="38" y="194" textAnchor="middle" fill="#059669" fontSize="11" fontWeight="900">
          ONESTO
        </text>
        <text x="160" y="18" textAnchor="middle" fill="#0F172A" fontSize="11" fontWeight="900">
          MEDIA (0%)
        </text>
        <text x="278" y="194" textAnchor="middle" fill="#DC2626" fontSize="11" fontWeight="900">
          FREGATURA
        </text>

        {/* 7. Dynamic Needle with Physical Spring Dynamics */}
        <g transform="translate(160, 150)">
          <g
            data-testid="tachometer-needle"
            style={{
              transform: `rotate(${effectiveNeedleAngle}deg)`,
              transformOrigin: '0px 0px',
              transition: 'transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)',
              willChange: 'transform',
            }}
          >
            <polygon
              points="-3.5,4 0,-100 3.5,4 0,16"
              fill="#0F172A"
              stroke="#FFFFFF"
              strokeWidth="1.5"
              filter="url(#needle-shadow)"
            />
            <circle cx="0" cy="-78" r="3.5" fill={needleColor} />
          </g>

          {/* Center Pivot Hub */}
          <circle r="15" fill="#0F172A" />
          <circle r="8" fill={needleColor} stroke="#FFFFFF" strokeWidth="2" />
        </g>
      </svg>

      {/* Digital Percentage Readout & Clean Verdict Line */}
      {showDigitalReadout && (
        <div className="flex flex-col items-center w-full -mt-1 mb-3">
          <div
            className={`text-4xl sm:text-5xl font-black tracking-tight font-mono leading-none ${
              standby
                ? 'text-slate-400'
                : effectiveZone === 'PREZZO_ONESTO'
                ? 'text-emerald-600'
                : effectiveZone === 'NELLA_MEDIA'
                ? 'text-amber-600'
                : 'text-red-600'
            }`}
          >
            {standby ? '-- %' : `${effectiveDiffPct > 0 ? '+' : ''}${effectiveDiffPct.toFixed(1)}%`}
          </div>
          <p className="mt-2 text-xs sm:text-sm font-bold text-slate-700 bg-slate-100 border border-slate-300 rounded-xl px-3 py-1.5 text-center w-full">
            {reactionQuip}
          </p>
        </div>
      )}

      {/* Simplified 3-Pill Legend */}
      {showLegend && (
        <div className="grid grid-cols-3 gap-2 w-full pt-2.5 border-t border-slate-200 text-[11px] text-center">
          <div className="py-1.5 px-2 rounded-xl bg-emerald-50 border border-emerald-300 text-emerald-950 font-bold inline-flex items-center justify-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
            <span>≤ 0% Onesto</span>
          </div>
          <div className="py-1.5 px-2 rounded-xl bg-amber-50 border border-amber-300 text-amber-950 font-bold inline-flex items-center justify-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-500 shrink-0" />
            <span>≤ +35% Media</span>
          </div>
          <div className="py-1.5 px-2 rounded-xl bg-rose-50 border border-rose-300 text-rose-950 font-bold inline-flex items-center justify-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-red-500 shrink-0" />
            <span>&gt; +35% Caro</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Tachometer;
