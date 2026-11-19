/**
 * src/components/AffiliateCard.tsx
 * Dynamic Category-Matched Affiliate Partnership Card for "Mi Stanno Fregando?".
 *
 * Integrates directly with src/core/affiliate.ts:
 * - Category Mapping: Auto (AutoDoc), Casa (ProntoPro), Dentista (DentalPro),
 *   Veterinario (Babydog), Cerimonie (Matrimonio.com), Affitti (SoloAffitti).
 * - High-Urgency Alert Switching: When isOvercharged=true (or isAlert=true),
 *   switches to pulsing crimson emergency styling ("Non farti spennare! Risparmia fino al 40%").
 * - Calm Educational Styling: When fair price, renders reassuring optimization copy.
 * - AGCM Disclosure: Compliant "Sponsorizzato" disclaimer.
 */

import React, { useMemo } from 'react';
import {
  ArrowRight,
  CheckCircle2,
  ExternalLink,
  ShieldAlert,
  Sparkles,
  Tag,
} from 'lucide-react';
import { CategoryId, DiscrepancyZone } from '../core/types';
import { getAffiliateForCategory } from '../core/affiliate';

export interface AffiliateCardProps {
  /** Selected Category ID */
  category: CategoryId;
  /** True if quote exceeds fair market threshold (TI_STANNO_FREGANDO) */
  isOvercharged?: boolean;
  /** Critical alert trigger (diffPct >= 65%) */
  isAlert?: boolean;
  /** Discrepancy zone classification */
  zone?: DiscrepancyZone;
  /** Discrepancy in Euro (+X€) */
  diffEuro?: number;
  /** Discrepancy percentage (+X%) */
  diffPct?: number;
  /** User's province sigla for affiliate geo-targeting */
  provinceSigla?: string;
  /** Optional click tracking callback */
  onAffiliateClick?: (partnerName: string, url: string) => void;
  /** Optional container class overrides */
  className?: string;
  /** Test ID */
  'data-testid'?: string;
}

export const AffiliateCard: React.FC<AffiliateCardProps> = ({
  category,
  isOvercharged: propIsOvercharged,
  isAlert = false,
  zone,
  diffEuro,
  diffPct,
  provinceSigla,
  onAffiliateClick,
  className = '',
  'data-testid': testId,
}) => {
  const isOvercharged = useMemo(() => {
    if (propIsOvercharged !== undefined) return propIsOvercharged;
    if (zone === 'TI_STANNO_FREGANDO') return true;
    if (diffPct !== undefined && diffPct > 35) return true;
    return false;
  }, [propIsOvercharged, zone, diffPct]);

  const affiliate = useMemo(
    () => getAffiliateForCategory(category, isOvercharged, provinceSigla),
    [category, isOvercharged, provinceSigla]
  );

  const handleClick = () => {
    onAffiliateClick?.(affiliate.partnerName, affiliate.url);
  };

  // High-Urgency Emergency State (crimson alert theme: border-red-500/80 from-red-950)
  if (isOvercharged || isAlert) {
    return (
      <aside
        data-testid={testId || 'affiliate-card-alert'}
        role="complementary"
        aria-label={`Allarme sovrapprezzo: offerta partner ${affiliate.partnerName}`}
        className={`relative w-full h-full flex flex-col justify-between overflow-hidden rounded-3xl border-2 border-red-500/80 bg-gradient-to-br from-rose-50 via-white to-amber-50 p-5 sm:p-6 shadow-xl shadow-red-600/15 transition-all duration-300 animate-pulse-slow ${className}`}
      >
        {/* Top Badge & Disclaimer Bar */}
        <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-600 border-2 border-slate-900 text-white text-xs font-black tracking-wide uppercase shadow-sm">
            <ShieldAlert className="w-4 h-4 text-amber-300" />
            <span>{affiliate.badgeText || '🚨 ALLARME SOVRAPPREZZO'}</span>
          </div>
          <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">
            Sponsorizzato • Partner Ufficiale
          </span>
        </div>

        {/* Dynamic Alert Headline */}
        <h3 className="text-lg sm:text-xl font-black text-slate-900 leading-tight mb-2">
          {affiliate.headline}
        </h3>

        {/* Contextual Overcharge Callout */}
        {diffEuro !== undefined && diffEuro > 0 && (
          <p className="text-sm text-rose-950 font-medium mb-4 bg-rose-100/90 border-2 border-rose-300 rounded-2xl p-3">
            💸 Ti stanno chiedendo ben{' '}
            <strong className="text-red-700 font-black underline decoration-red-500">
              +{diffEuro.toLocaleString('it-IT')} €
            </strong>{' '}
            {diffPct !== undefined && `(+${diffPct.toFixed(1)}%)`} in più rispetto alla media della tua provincia!
            Fai un confronto furbo prima di pagare:
          </p>
        )}

        {/* Discount Callout */}
        {affiliate.discountCallout && (
          <div className="flex items-center gap-2 text-xs sm:text-sm text-amber-800 bg-amber-100 border border-amber-300 rounded-xl px-3 py-1.5 font-extrabold mb-4">
            <Tag className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{affiliate.discountCallout}</span>
          </div>
        )}

        {/* Primary High-Urgency CTA Button */}
        <a
          href={affiliate.url}
          target="_blank"
          rel="noopener noreferrer sponsored"
          onClick={handleClick}
          className="group relative flex items-center justify-center gap-2 w-full py-3.5 px-6 rounded-2xl bg-gradient-to-r from-red-600 via-rose-500 to-orange-500 hover:from-red-500 hover:to-rose-400 border-2 border-slate-900 text-white font-black text-sm sm:text-base shadow-md hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0.5 transition-all duration-150"
        >
          <span>{affiliate.ctaText || `Risparmia subito con ${affiliate.partnerName} →`}</span>
          <ArrowRight className="w-5 h-5 transition-transform duration-200 group-hover:translate-x-1" />
        </a>

        {/* Secondary Alternative Partner Link */}
        {affiliate.secondaryPartnerName && affiliate.secondaryUrl && (
          <div className="mt-3 text-center">
            <a
              href={affiliate.secondaryUrl}
              target="_blank"
              rel="noopener noreferrer sponsored"
              className="text-xs font-bold text-slate-600 hover:text-slate-950 underline decoration-slate-400 transition-colors inline-flex items-center gap-1"
            >
              <span>Oppure confronta le offerte su {affiliate.secondaryPartnerName}</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        )}

        {/* Legal Transparency */}
        <p className="mt-3 text-[10px] text-slate-500 font-medium text-center select-none">
          Trasparenza: Il link verso {affiliate.partnerName} sostiene il Fregometro gratuito. Zero costi extra per te.
        </p>
      </aside>
    );
  }

  // Calm Educational State (PREZZO_ONESTO / NELLA_MEDIA)
  return (
    <aside
      data-testid={testId || 'affiliate-card-calm'}
      role="complementary"
      aria-label={`Opportunità di risparmio con partner ${affiliate.partnerName}`}
      className={`relative w-full h-full flex flex-col justify-between overflow-hidden rounded-3xl border-2 border-emerald-500 bg-gradient-to-br from-emerald-50 via-white to-teal-50 p-5 sm:p-6 shadow-xl shadow-emerald-600/15 transition-all duration-300 ${className}`}
    >
      {/* Top Badge & Disclaimer Bar */}
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-300 border-2 border-slate-900 text-slate-950 text-xs font-black shadow-sm">
          <CheckCircle2 className="w-4 h-4 text-slate-950" />
          <span>{affiliate.badgeText || 'Partner Certificato'}</span>
        </div>
        <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">
          Sponsorizzato • Risparmio Extra
        </span>
      </div>

      {/* Dynamic Calm Headline */}
      <h3 className="text-base sm:text-lg font-black text-slate-900 leading-snug mb-2">
        {affiliate.headline}
      </h3>

      {/* Reassuring Educational Subtitle */}
      <p className="text-xs sm:text-sm text-slate-700 font-medium mb-4">
        Il tuo preventivo è già buono, ma se vuoi risparmiare ancora qualche euro puoi dare un&apos;occhiata alle tariffe di {affiliate.partnerName}.
      </p>

      {/* Discount / Benefit Callout */}
      {affiliate.discountCallout && (
        <div className="flex items-center gap-2 text-xs text-emerald-800 bg-emerald-100 border border-emerald-300 rounded-xl px-3 py-1.5 font-bold mb-4">
          <Sparkles className="w-3.5 h-3.5 shrink-0 text-emerald-600" />
          <span>{affiliate.discountCallout}</span>
        </div>
      )}

      {/* Calm Action Button */}
      <a
        href={affiliate.url}
        target="_blank"
        rel="noopener noreferrer sponsored"
        onClick={handleClick}
        className="group relative flex items-center justify-center gap-2 w-full py-3.5 px-5 rounded-2xl bg-emerald-500 hover:bg-emerald-400 border-2 border-slate-900 text-slate-950 font-black text-sm shadow-md hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0.5 transition-all duration-150"
      >
        <span>{affiliate.ctaText || `Scopri le offerte su ${affiliate.partnerName}`}</span>
        <ArrowRight className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" />
      </a>

      {/* Legal Transparency */}
      <p className="mt-3 text-[10px] text-slate-500 font-medium text-center select-none">
        Trasparenza: Mi Stanno Fregando è indipendente. I link sponsorizzati mantengono il servizio 100% gratuito.
      </p>
    </aside>
  );
};

export default AffiliateCard;
