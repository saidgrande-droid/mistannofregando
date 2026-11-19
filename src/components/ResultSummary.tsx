/**
 * src/components/ResultSummary.tsx
 * Viral Italian result presentation card with dynamic verdict badges and 4-tile statistical comparison grid.
 *
 * Designed for immediate emotional validation, mathematical proof, screenshot capture, and virality.
 */

import React, { useMemo } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  MinusCircle,
  Share2,
  TrendingUp,
  TrendingDown,
  Info,
  MapPin,
  Sparkles,
} from 'lucide-react';
import { CalculationResult, CategoryId } from '../core/types';

export interface ResultSummaryProps {
  /** The calculated result object produced by calculateDiscrepancy() or calculateFromPrice() */
  result: CalculationResult;

  /** Human-readable category details or slug */
  categoryName?: string;
  categoryId?: CategoryId;
  categoryIcon?: string;

  /** Prestation name and measurement unit */
  prestationName?: string;
  prestationUnit?: string;

  /** Province details for geographic context */
  provinceName?: string;
  provinceSigla?: string;
  regionName?: string;

  /** Optional crowdsourced sample count contributing to this calculation */
  crowdsourceCount?: number;

  /** Callback when user clicks "Hai pagato una cifra diversa?" */
  onCrowdsourceClick?: () => void;

  /** Callback when user clicks "Condividi Scheda" */
  onShareClick?: () => void;

  /** Optional CSS class override */
  className?: string;

  /** Optional compact mode */
  compact?: boolean;
}

export const ResultSummary: React.FC<ResultSummaryProps> = ({
  result,
  categoryIcon,
  prestationName,
  prestationUnit,
  provinceName,
  provinceSigla,
  crowdsourceCount,
  onCrowdsourceClick,
  onShareClick,
  className = '',
}) => {
  const {
    quote,
    refPrice,
    diffEuro,
    diffPct,
    zone,
    isAlert,
    headline,
    subheadline,
  } = result;

  // Formatted numeric values
  const fmtQuote = useMemo(() => `${quote.toLocaleString('it-IT')} €`, [quote]);
  const fmtRefPrice = useMemo(() => `${refPrice.toLocaleString('it-IT')} €`, [refPrice]);
  const fmtDiffEuro = useMemo(() => {
    if (diffEuro > 0) return `+${diffEuro.toLocaleString('it-IT')} €`;
    return `${diffEuro.toLocaleString('it-IT')} €`;
  }, [diffEuro]);
  const fmtDiffPct = useMemo(() => {
    if (diffPct > 0) return `+${diffPct.toFixed(1)}%`;
    return `${diffPct.toFixed(1)}%`;
  }, [diffPct]);

  // Dynamic visual configurations per zone
  const zoneConfig = useMemo(() => {
    switch (zone) {
      case 'PREZZO_ONESTO':
        return {
          pillBg: 'bg-emerald-100 border-2 border-emerald-600 shadow-sm',
          pillText: 'text-emerald-950',
          badgeLabel: 'Prezzo Onesto',
          subLabel: 'Preventivo competitivo rispetto alla media',
          icon: <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0" />,
          headlineColor: 'text-emerald-700',
          statHighlightBg: 'bg-emerald-50 border-2 border-slate-900 text-emerald-800',
          cardBorder: 'border-slate-900 shadow-xl shadow-slate-900/10',
          headerBg: 'bg-emerald-50',
        };
      case 'NELLA_MEDIA':
        return {
          pillBg: 'bg-amber-100 border-2 border-amber-500 shadow-sm',
          pillText: 'text-amber-950',
          badgeLabel: 'Nella Media',
          subLabel: 'Allineato ai prezzi della tua zona',
          icon: <MinusCircle className="w-5 h-5 text-amber-700 shrink-0" />,
          headlineColor: 'text-amber-700',
          statHighlightBg: 'bg-amber-50 border-2 border-slate-900 text-amber-800',
          cardBorder: 'border-slate-900 shadow-xl shadow-slate-900/10',
          headerBg: 'bg-amber-50',
        };
      case 'TI_STANNO_FREGANDO':
      default:
        return {
          pillBg: isAlert
            ? 'bg-red-600 text-white border-2 border-slate-900 shadow-sm animate-pulse-slow'
            : 'bg-rose-100 border-2 border-rose-600 shadow-sm text-rose-950',
          pillText: isAlert ? 'text-white' : 'text-rose-950',
          badgeLabel: 'TI STANNO FREGANDO!',
          subLabel: isAlert
            ? 'Sovrapprezzo critico: tariffa fuori mercato'
            : 'Superiore alla media nella tua provincia',
          icon: (
            <AlertTriangle
              className={`w-5 h-5 shrink-0 ${isAlert ? 'text-white' : 'text-rose-700'}`}
            />
          ),
          headlineColor: 'text-red-600',
          statHighlightBg: 'bg-rose-50 border-2 border-slate-900 text-red-700',
          cardBorder: isAlert
            ? 'border-red-600 shadow-xl shadow-red-600/15 ring-4 ring-red-500/15'
            : 'border-slate-900 shadow-xl shadow-slate-900/10',
          headerBg: 'bg-rose-50',
        };
    }
  }, [zone, isAlert]);

  const locationDisplay = provinceName
    ? `${provinceName}${provinceSigla ? ` (${provinceSigla})` : ''}`
    : provinceSigla || 'Italia';

  return (
    <article
      id="result-summary-card"
      role="region"
      aria-label="Riepilogo e verdetto del confronto preventivo"
      aria-live="polite"
      className={`relative w-full max-w-2xl mx-auto bg-white rounded-3xl border-2 ${zoneConfig.cardBorder} transition-all duration-300 ${className}`}
    >
      {/* 1. Header Bar: Branding & Scope */}
      <div className={`flex items-center justify-between px-5 sm:px-6 py-3.5 border-b-2 border-slate-900 rounded-t-[22px] ${zoneConfig.headerBg}`}>
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-slate-900 shrink-0" aria-hidden="true" />
          <span className="text-xs sm:text-sm font-black uppercase tracking-wider text-slate-900">
            Verdetto Analisi
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-xs font-extrabold px-3 py-1 rounded-full bg-white border border-slate-900 text-slate-800 shadow-sm">
          <MapPin className="w-3.5 h-3.5 text-rose-500 shrink-0" />
          <span className="truncate max-w-[200px]">
            {prestationName ? `${prestationName} • ` : ''}
            {locationDisplay}
          </span>
        </div>
      </div>

      <div className="p-5 sm:p-6 space-y-4">
        {/* 2. Emotional Copywriting + Verdict Badge */}
        <div className="space-y-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div
              role="status"
              className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-black tracking-wide uppercase ${zoneConfig.pillBg} ${zoneConfig.pillText}`}
            >
              {zoneConfig.icon}
              <span>{zoneConfig.badgeLabel}</span>
            </div>
            <span className="text-xs text-slate-600 font-bold">
              {zoneConfig.subLabel}
            </span>
          </div>

          <h2 className={`text-xl sm:text-2xl font-black tracking-tight leading-snug ${zoneConfig.headlineColor}`}>
            {headline}
          </h2>
          <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-medium">
            {subheadline}
          </p>
        </div>

        {/* 3. 4-Tile Statistical Comparison Grid */}
        <div className="grid grid-cols-2 gap-3">
          {/* Tile 1: Preventivo Ricevuto */}
          <div className="bg-slate-50 p-3.5 rounded-2xl border-2 border-slate-900 flex flex-col justify-between">
            <span className="text-[11px] font-black text-slate-600 uppercase tracking-wider">
              Preventivo Ricevuto
            </span>
            <div className="my-1">
              <span className="text-2xl sm:text-3xl font-black font-mono text-slate-950 tracking-tight">
                {fmtQuote}
              </span>
              {prestationUnit && (
                <span className="text-xs text-slate-500 font-semibold ml-1">/{prestationUnit}</span>
              )}
            </div>
            <span className="text-[11px] text-slate-500 font-semibold">
              Importo richiesto
            </span>
          </div>

          {/* Tile 2: Media Locale */}
          <div className="bg-slate-50 p-3.5 rounded-2xl border-2 border-slate-900 flex flex-col justify-between">
            <span className="text-[11px] font-black text-slate-600 uppercase tracking-wider">
              Media a {provinceSigla || 'Zona'}
            </span>
            <div className="my-1">
              <span className="text-2xl sm:text-3xl font-black font-mono text-slate-950 tracking-tight">
                {fmtRefPrice}
              </span>
              {prestationUnit && (
                <span className="text-xs text-slate-500 font-semibold ml-1">/{prestationUnit}</span>
              )}
            </div>
            <span className="text-[11px] text-slate-500 font-semibold">
              Prezzo medio reale
            </span>
          </div>

          {/* Tile 3: Differenza in Euro */}
          <div className="bg-slate-50 p-3.5 rounded-2xl border-2 border-slate-900 flex flex-col justify-between">
            <span className="text-[11px] font-black text-slate-600 uppercase tracking-wider flex items-center justify-between">
              Differenza
              {diffEuro > 0 ? (
                <TrendingUp className="w-4 h-4 text-red-600" />
              ) : diffEuro < 0 ? (
                <TrendingDown className="w-4 h-4 text-emerald-600" />
              ) : null}
            </span>
            <div className="my-1">
              <span
                className={`text-2xl sm:text-3xl font-black font-mono tracking-tight ${
                  diffEuro > 0
                    ? 'text-red-600'
                    : diffEuro < 0
                    ? 'text-emerald-600'
                    : 'text-slate-800'
                }`}
              >
                {fmtDiffEuro}
              </span>
            </div>
            <span className="text-[11px] text-slate-600 font-semibold">
              {diffEuro > 0 ? 'Sovrapprezzo stimato' : diffEuro < 0 ? 'Risparmio netto!' : 'In parità'}
            </span>
          </div>

          {/* Tile 4: Scostamento Percentuale (Giant Font) */}
          <div
            className={`p-3.5 rounded-2xl flex flex-col justify-between ${zoneConfig.statHighlightBg}`}
          >
            <span className="text-[11px] font-black uppercase tracking-wider text-slate-900">
              Scostamento %
            </span>
            <div className="my-0.5">
              <span className="text-4xl sm:text-5xl font-black font-mono tracking-tight block leading-none">
                {fmtDiffPct}
              </span>
            </div>
            <span className="text-[11px] font-extrabold text-slate-800">
              {diffPct > 0 ? 'Sopra la media' : diffPct < 0 ? 'Sotto la media' : 'Esattamente in media'}
            </span>
          </div>
        </div>

        {/* 5. Crowdsource Benchmark Micro-Notice */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-3 text-xs text-slate-600 border-t-2 border-dashed border-slate-200">
          <div className="flex items-center gap-1.5 font-medium">
            <Info className="w-4 h-4 shrink-0 text-amber-600" />
            <span>
              {crowdsourceCount && crowdsourceCount > 0
                ? `Media basata su ISTAT + ${crowdsourceCount} segnalazioni reali.`
                : 'Stima calcolata su indici ISTAT e prezziari provinciali.'}
            </span>
          </div>
          {onCrowdsourceClick && (
            <button
              type="button"
              onClick={onCrowdsourceClick}
              className="font-extrabold text-rose-600 hover:text-rose-700 underline underline-offset-2 text-left sm:text-right transition-colors"
            >
              Hai pagato una cifra diversa? Dillo qui!
            </button>
          )}
        </div>
      </div>

      {/* 6. Screenshot-Friendly Footer & Action Bar (Inset pill so corners never bleed white lines!) */}
      <div className="px-5 sm:px-6 pb-5">
        <div className="bg-slate-900 text-white px-4 py-3 rounded-2xl flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-1.5 text-xs">
            <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="font-black tracking-wide">mistannofregando.it</span>
            <span className="hidden sm:inline text-slate-400">• Il Fregometro dei Prezzi in Italia</span>
          </div>

          {onShareClick && (
            <button
              type="button"
              onClick={onShareClick}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-emerald-400 hover:bg-emerald-300 text-slate-950 text-xs sm:text-sm font-black shadow-sm transition-all"
            >
              <Share2 className="w-3.5 h-3.5" />
              <span>Condividi Scheda</span>
            </button>
          )}
        </div>
      </div>
    </article>
  );
};

export default ResultSummary;
