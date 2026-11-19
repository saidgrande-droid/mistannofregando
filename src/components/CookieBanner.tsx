/**
 * src/components/CookieBanner.tsx
 * Garante Privacy / ePrivacy Compliant Consent Banner for "Mi Stanno Fregando?".
 *
 * Explains strictly-technical localStorage usage vs optional third-party ad/analytics cookies,
 * stores explicit consent choice ('essential' | 'accepted') locally, and allows re-opening
 * preferences from the footer at any time.
 */

import React from 'react';
import { ShieldCheck, X } from 'lucide-react';

export type CookieConsentLevel = 'essential' | 'accepted';

export const COOKIE_CONSENT_STORAGE_KEY = 'fregometro_cookie_consent_v1';

export interface CookieBannerProps {
  isVisible: boolean;
  currentChoice: CookieConsentLevel | null;
  onAcceptEssential: () => void;
  onAcceptAll: () => void;
  onOpenCookiePolicy: () => void;
  onDismiss?: () => void;
}

export function readStoredCookieConsent(): CookieConsentLevel | null {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return null;
    const raw = window.localStorage.getItem(COOKIE_CONSENT_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (parsed && (parsed.level === 'essential' || parsed.level === 'accepted')) {
      return parsed.level;
    }
  } catch {
    // Ignore storage parse failures
  }
  return null;
}

export function persistCookieConsent(level: CookieConsentLevel): void {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return;
    window.localStorage.setItem(
      COOKIE_CONSENT_STORAGE_KEY,
      JSON.stringify({
        level,
        updatedAt: new Date().toISOString(),
      })
    );
  } catch {
    // Ignore storage quota failures
  }
}

export const CookieBanner: React.FC<CookieBannerProps> = ({
  isVisible,
  currentChoice,
  onAcceptEssential,
  onAcceptAll,
  onOpenCookiePolicy,
  onDismiss,
}) => {
  if (!isVisible) return null;

  return (
    <aside
      role="region"
      aria-label="Preferenze cookie e archiviazione locale"
      className="fixed bottom-2.5 sm:bottom-4 left-2.5 sm:left-4 right-2.5 sm:right-4 z-40 max-w-4xl mx-auto animate-fade-in"
    >
      <div className="bg-white/95 backdrop-blur-md border-2 border-slate-900 rounded-2xl p-3 sm:p-5 shadow-2xl shadow-slate-900/20 flex flex-col md:flex-row md:items-center justify-between gap-2.5 sm:gap-4">
        <div className="flex items-start gap-2.5 sm:gap-3 min-w-0">
          <span className="hidden sm:flex w-9 h-9 rounded-xl bg-slate-900 text-white items-center justify-center shrink-0 mt-0.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </span>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <p className="text-xs sm:text-sm font-black text-slate-950 font-display">
                Privacy e Preferenze Cookie
              </p>
              {currentChoice && (
                <span className="text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-100 border border-slate-300 text-slate-700">
                  Scelta attuale: {currentChoice === 'accepted' ? 'Tutti accettati' : 'Solo essenziali'}
                </span>
              )}
            </div>
            <p className="text-[11px] sm:text-xs text-slate-600 font-medium leading-snug sm:leading-relaxed mt-0.5 sm:mt-1">
              Usiamo solo <code className="px-1 py-0.5 bg-slate-100 rounded font-mono text-[10px]">localStorage</code> tecnico senza profilazione; puoi gestire eventuali script futuri qui.{' '}
              <button
                type="button"
                onClick={onOpenCookiePolicy}
                className="font-extrabold text-slate-950 underline cursor-pointer"
              >
                Leggi la Cookie Policy
              </button>
              .
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0 w-full md:w-auto justify-end">
          <button
            type="button"
            onClick={onAcceptEssential}
            className="flex-1 sm:flex-none px-3 sm:px-3.5 py-2 rounded-xl border-2 border-slate-900 bg-white hover:bg-slate-100 text-slate-950 text-xs font-black transition-colors cursor-pointer text-center whitespace-nowrap"
          >
            Solo essenziali
          </button>
          <button
            type="button"
            onClick={onAcceptAll}
            className="flex-1 sm:flex-none px-3.5 sm:px-4 py-2 rounded-xl border-2 border-slate-900 bg-slate-900 hover:bg-slate-800 text-white text-xs font-black transition-colors cursor-pointer text-center whitespace-nowrap"
          >
            Accetta tutti
          </button>
          {onDismiss && currentChoice && (
            <button
              type="button"
              onClick={onDismiss}
              aria-label="Chiudi barra preferenze cookie"
              className="p-2 rounded-xl border border-slate-300 text-slate-600 hover:text-slate-950 hover:bg-slate-100 transition-colors cursor-pointer shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
};

export default CookieBanner;
