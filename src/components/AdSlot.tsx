/**
 * src/components/AdSlot.tsx
 * Zero-CLS Programmatic Display Ad Slot Component for "Mi Stanno Fregando?".
 * Supports Google AdSense / Ezoic / Header Bidding standard placements:
 * - Leaderboard: 728x90 (Desktop) / 320x50 (Mobile)
 * - MPU: 300x250 (Mid content)
 * - Sticky: 320x50 (Mobile) / 728x90 (Desktop) viewport-fixed bottom anchor
 * - Skyscraper: 160x600 (Vertical sticky side rails on desktop + responsive twin card on mobile)
 *
 * Implements strict CSS min-height reservation to guarantee 0 Cumulative Layout Shift (CLS),
 * and compliant AGCM "PUBBLICITÀ" disclosure badges.
 */

import React, { useEffect, useState } from 'react';
import { Megaphone, X } from 'lucide-react';

export type AdSlotFormat = 'leaderboard' | 'mpu' | 'sticky' | 'skyscraper';

export interface AdSlotProps {
  /** Ad slot format / placement */
  format: AdSlotFormat;
  /** Custom slot identifier (e.g. 'leaderboard-top', 'mpu-mid', 'sticky-bottom', 'skyscraper-left') */
  slotId?: string;
  /** Optional AdSense Publisher ID (e.g. 'ca-pub-XXXXXXXX') */
  adClient?: string;
  /** Optional AdSense Ad Slot ID (e.g. '1234567890') */
  adSlot?: string;
  /** Optional custom className */
  className?: string;
  /** Allow dismissing sticky bottom ad (default: true) */
  dismissible?: boolean;
  /** Force mock placeholder view (useful for dev and testing) */
  isMock?: boolean;
  /** Compact mobile card variant for skyscraper banners on mobile/tablet */
  compactMobile?: boolean;
  /** Direct advertiser contact email for placeholder mailto links */
  contactEmail?: string;
  /** Stretch skyscraper slot vertically inside a flex column to match main content height */
  fillHeight?: boolean;
  /** Test identifier */
  'data-testid'?: string;
}

const DEFAULT_CONTACT_EMAIL = 'gadmediamanager@gmail.com';

function buildAdvertiseMailto(email: string, slotDescription: string): string {
  const subject = encodeURIComponent(
    `Richiesta spazio pubblicitario - ${slotDescription} (Mi Stanno Fregando?)`
  );
  const body = encodeURIComponent(
    `Buongiorno,\n\nsono interessato a pubblicizzare la mia attività nello spazio "${slotDescription}" su Mi Stanno Fregando?.\n\nNome / Azienda:\nSito web:\nPeriodo o durata desiderata:\n`
  );
  return `mailto:${email}?subject=${subject}&body=${body}`;
}

interface FormatConfig {
  defaultSlotId: string;
  minHeight: number;
  mobileMinHeight: number;
  desktopWidth: number;
  mobileWidth: number;
  label: string;
}

const FORMAT_CONFIGS: Record<AdSlotFormat, FormatConfig> = {
  leaderboard: {
    defaultSlotId: 'leaderboard-top',
    minHeight: 90,
    mobileMinHeight: 50,
    desktopWidth: 728,
    mobileWidth: 320,
    label: 'Leaderboard (728×90 / 320×50)',
  },
  mpu: {
    defaultSlotId: 'mpu-mid',
    minHeight: 250,
    mobileMinHeight: 250,
    desktopWidth: 300,
    mobileWidth: 300,
    label: 'MPU Mid-Content (300×250)',
  },
  sticky: {
    defaultSlotId: 'sticky-bottom',
    minHeight: 90,
    mobileMinHeight: 50,
    desktopWidth: 728,
    mobileWidth: 320,
    label: 'Sticky Bottom Anchor (728×90 / 320×50)',
  },
  skyscraper: {
    defaultSlotId: 'skyscraper-side',
    minHeight: 600,
    mobileMinHeight: 110,
    desktopWidth: 160,
    mobileWidth: 160,
    label: 'Skyscraper (160×600)',
  },
};

function getSkyscraperSlotLabel(slotId: string): string {
  const side = slotId.includes('right') ? 'Destra' : 'Sinistra';
  const match = /-(\d+)$/.exec(slotId);
  const num = match ? match[1] : '1';
  return `Spazio #${num} · ${side}`;
}

export const AdSlot: React.FC<AdSlotProps> = ({
  format,
  slotId: customSlotId,
  adClient,
  adSlot,
  className = '',
  dismissible = true,
  isMock = true,
  compactMobile = false,
  contactEmail = DEFAULT_CONTACT_EMAIL,
  fillHeight = false,
  'data-testid': testId,
}) => {
  const [isDismissed, setIsDismissed] = useState(false);
  const [adLoaded, setAdLoaded] = useState(false);
  const config = FORMAT_CONFIGS[format];
  const slotId = customSlotId || config.defaultSlotId;

  useEffect(() => {
    if (!isMock && typeof window !== 'undefined') {
      try {
        const adsWindow = window as unknown as { adsbygoogle?: Array<Record<string, unknown>> };
        adsWindow.adsbygoogle = adsWindow.adsbygoogle || [];
        adsWindow.adsbygoogle.push({});
        setAdLoaded(true);
      } catch {
        setAdLoaded(false);
      }
    }
  }, [isMock, format]);

  if (isDismissed) return null;

  const isSticky = format === 'sticky';
  const isMPU = format === 'mpu';
  const isSkyscraper = format === 'skyscraper';
  const slotBadge = getSkyscraperSlotLabel(slotId);
  const slotDescription = isSkyscraper
    ? `${slotBadge} (${config.label})`
    : `${slotId} (${config.label})`;
  const mailtoHref = buildAdvertiseMailto(contactEmail, slotDescription);

  // Compact Mobile Banner Render (used on mobile/tablet so lateral slots stay visible)
  if (isSkyscraper && compactMobile) {
    return (
      <aside
        id={`${slotId}-mobile`}
        data-slot-id={slotId}
        data-testid={testId || `${slotId}-mobile`}
        role="complementary"
        aria-label={`Spazio pubblicitario ${config.label}`}
        className={`w-full ${className}`}
      >
        <div className="flex items-center justify-between mb-1 px-1">
          <span className="text-[9px] tracking-widest uppercase font-black text-slate-500">
            Pubblicità
          </span>
          <span className="text-[9px] font-mono font-bold text-slate-400">160×600</span>
        </div>
        <a
          href={mailtoHref}
          aria-label={`Richiedi ${slotDescription} via email a ${contactEmail}`}
          title={`Scrivi a ${contactEmail} per questo spazio`}
          className="group p-3 rounded-2xl border-2 border-dashed border-slate-400 hover:border-slate-900 bg-white/95 shadow-sm hover:shadow-md flex flex-col justify-between min-h-[104px] transition-all cursor-pointer"
        >
          <div className="flex items-center gap-1.5">
            <span className="w-6 h-6 rounded-lg bg-amber-100 border border-slate-900 text-slate-900 flex items-center justify-center shrink-0">
              <Megaphone className="w-3.5 h-3.5" />
            </span>
            <span className="text-xs font-black text-slate-900 leading-tight truncate">
              Spazio Pubblicitario
            </span>
          </div>
          <p className="text-[11px] text-slate-600 font-semibold leading-snug my-1">
            Metti qui la tua pubblicità. Clicca per scriverci.
          </p>
          <span className="inline-flex items-center justify-center w-full py-1 px-2 rounded-lg bg-slate-900 group-hover:bg-slate-800 text-white text-[10px] font-extrabold uppercase tracking-wide transition-colors">
            {slotBadge} • Contatta
          </span>
        </a>
      </aside>
    );
  }

  return (
    <aside
      id={slotId}
      data-slot-id={slotId}
      data-testid={testId || slotId}
      role="complementary"
      aria-label={`Spazio pubblicitario ${config.label}`}
      style={{
        minHeight: `${config.minHeight}px`,
      }}
      className={`relative mx-auto transition-all ${
        isSticky
          ? 'fixed bottom-0 left-0 right-0 z-40 bg-white/95 border-t-2 border-slate-900 backdrop-blur-md shadow-2xl py-1.5 px-3 hidden sm:block'
          : isSkyscraper
          ? fillHeight
            ? 'w-[160px] min-h-[600px] flex-1 flex flex-col'
            : 'w-[160px] min-h-[600px]'
          : 'w-full my-3'
      } ${
        isMPU
          ? 'w-[300px] sm:w-[300px] min-h-[250px]'
          : isSkyscraper
          ? 'w-[160px]'
          : 'w-full max-w-[728px]'
      } ${className}`}
    >
      {/* AGCM Legal Disclosure Badge */}
      <div className="flex items-center justify-between w-full mb-1 px-1 shrink-0">
        <span className="text-[10px] tracking-widest uppercase font-extrabold text-slate-500 select-none">
          Pubblicità
        </span>
        {isSticky && dismissible && (
          <button
            type="button"
            onClick={() => setIsDismissed(true)}
            aria-label="Chiudi annuncio pubblicitario"
            className="p-1 rounded-full text-slate-500 hover:text-slate-900 hover:bg-slate-200 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Zero-CLS Bounding Frame */}
      <div
        className={`relative flex ${
          isSkyscraper ? 'flex-col items-stretch' : 'items-center justify-center'
        } overflow-hidden rounded-2xl ${
          isMPU
            ? 'w-[300px] h-[250px] min-h-[250px]'
            : isSkyscraper
            ? fillHeight
              ? 'w-[160px] flex-1 min-h-[600px]'
              : 'w-[160px] h-[600px] min-h-[600px]'
            : 'w-full h-[50px] sm:h-[90px] min-h-[50px] sm:min-h-[90px]'
        } ${
          isMock || !adLoaded
            ? 'bg-white/95 border-2 border-dashed border-slate-400 shadow-lg shadow-slate-900/5'
            : 'bg-transparent'
        }`}
        style={{
          minHeight: `${config.mobileMinHeight}px`,
        }}
      >
        {isMock || !adLoaded ? (
          isSkyscraper ? (
            /* Clean Editorial "Spazio Pubblicitario" Skyscraper Placeholder (clickable mailto) */
            <a
              href={mailtoHref}
              aria-label={`Richiedi ${slotDescription} via email a ${contactEmail}`}
              title={`Scrivi a ${contactEmail} per questo spazio`}
              className="group flex flex-col items-center justify-between flex-1 h-full w-full p-4 text-center select-none cursor-pointer transition-colors hover:bg-amber-50/40"
            >
              <div className="w-full pt-2">
                <span className="inline-block px-2.5 py-0.5 rounded-full bg-slate-100 border border-slate-300 text-slate-600 text-[9px] font-extrabold uppercase tracking-wider mb-4">
                  {slotBadge}
                </span>
                <div className="w-12 h-12 mx-auto rounded-2xl bg-amber-100 border-2 border-slate-900 shadow-sm flex items-center justify-center mb-4">
                  <Megaphone className="w-5 h-5 text-slate-900" />
                </div>
                <div className="text-slate-900 font-black text-sm leading-snug font-display">
                  Metti qui la tua pubblicità
                </div>
                <p className="text-[11px] text-slate-500 font-semibold mt-2.5 leading-relaxed">
                  Spazio disponibile per il tuo banner o brand.
                </p>
              </div>

              <div className="w-full py-4 px-2 rounded-xl border border-dashed border-slate-300 bg-slate-50/80">
                <span className="block text-[10px] font-black uppercase tracking-wider text-slate-700">
                  Il tuo annuncio qui
                </span>
                <span className="block mt-1 text-[10px] font-mono text-slate-400 font-bold">
                  160 × 600 px
                </span>
              </div>

              <div className="w-full pb-1">
                <span className="block w-full py-2 px-2 rounded-xl bg-slate-900 group-hover:bg-slate-800 text-white text-[10px] font-black uppercase tracking-wide transition-colors">
                  Contatta via Email
                </span>
              </div>
            </a>
          ) : (
            /* Clean Horizontal "Spazio Pubblicitario" Placeholder (clickable mailto) */
            <a
              href={mailtoHref}
              aria-label={`Richiedi ${slotDescription} via email a ${contactEmail}`}
              title={`Scrivi a ${contactEmail} per questo spazio`}
              className="group flex items-center justify-between w-full h-full px-4 py-2 select-none gap-3 cursor-pointer transition-colors hover:bg-amber-50/40"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-amber-100 border-2 border-slate-900 flex items-center justify-center shrink-0">
                  <Megaphone className="w-4 h-4 text-slate-900" />
                </div>
                <div className="text-left">
                  <div className="text-slate-900 font-black text-xs sm:text-sm leading-tight">
                    Metti qui il tuo spazio pubblicitario
                  </div>
                  <div className="text-[11px] text-slate-500 font-semibold hidden sm:block">
                    Clicca per scriverci e prenotare questo spazio • Formato {config.label}
                  </div>
                </div>
              </div>
              <span className="px-3 py-1.5 rounded-xl bg-slate-900 group-hover:bg-slate-800 text-white text-[10px] sm:text-[11px] font-black uppercase tracking-wide shrink-0 transition-colors">
                Contatta via Email
              </span>
            </a>
          )
        ) : (
          /* Actual Google AdSense Tag */
          <ins
            className="adsbygoogle"
            style={{ display: 'block', width: '100%', height: '100%' }}
            data-ad-client={adClient || 'ca-pub-0000000000000000'}
            data-ad-slot={adSlot || '0000000000'}
            data-ad-format={isMPU ? 'rectangle' : isSkyscraper ? 'vertical' : 'horizontal'}
            data-full-width-responsive="true"
          />
        )}
      </div>
    </aside>
  );
};

export default AdSlot;
