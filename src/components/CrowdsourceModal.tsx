/**
 * src/components/CrowdsourceModal.tsx
 * "Io ho pagato X€" Crowdsourced Pricing Submission Flow for "Mi Stanno Fregando?".
 *
 * Features:
 * - 1-click modal trigger and preset chips
 * - Context pre-filling (category, prestation, province, benchmark)
 * - Input parsing (comma/dot/€) & anti-spam bounds validation
 * - Direct integration with src/core/crowdsource.ts & src/core/storage.ts
 * - Instant celebratory feedback screen (before vs after average comparison & delta)
 * - Real-time parent recalculation callback
 * - Full W3C WAI-ARIA dialog accessibility (focus trap, ESC, backdrop click, scroll lock)
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  X,
  Send,
  Coins,
  CheckCircle2,
  AlertCircle,
  TrendingDown,
  TrendingUp,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Info,
  MapPin,
  Tag,
} from 'lucide-react';
import { CategoryId, IDataStore } from '../core/types';
import { getPrestationById, getProvinceBySigla, getCategoryById } from '../core/dataset';
import { validateCrowdsourcedPrice, submitCrowdsourcedPrice } from '../core/crowdsource';
import { getDataStore } from '../core/storage';

export interface CrowdsourceSuccessPayload {
  categoryId: CategoryId;
  prestationId: string;
  provinceSigla: string;
  paidAmount: number;
  previousAverage: number;
  newAverage: number;
  previousSampleCount: number;
  newSampleCount: number;
  diffFromPrevious: number;
  diffPctFromPrevious: number;
}

export interface CrowdsourceModalProps {
  /** Controls dialog open state */
  isOpen: boolean;
  /** Handler to dismiss the modal */
  onClose: () => void;
  /** Active Category ID */
  categoryId: CategoryId;
  /** Active prestation ID */
  prestationId: string;
  /** 2-letter uppercase province code (e.g. 'MI', 'RM', 'NA') */
  provinceSigla: string;
  /** Optional human-readable category name */
  categoryName?: string;
  /** Optional category emoji */
  categoryIcon?: string;
  /** Optional human-readable prestation name */
  prestationName?: string;
  /** Optional measurement unit */
  prestationUnit?: string;
  /** Optional human-readable province name */
  provinceName?: string;
  /** Current active reference price benchmark in Euro */
  currentRefPrice?: number;
  /** Current active sample count (defaults to 100) */
  currentSampleCount?: number;
  /** Quote entered in the calculator (used for 1-click preset chip) */
  activeQuote?: number;
  /** Callback fired on successful submission with full payload */
  onSuccess?: (payload: CrowdsourceSuccessPayload) => void;
  /** Callback fired on successful submission with updated average and count */
  onSubmissionSuccess?: (newAverage: number, newCount: number) => void;
  /** Optional custom data store (defaults to active LocalStorage/InMemory singleton) */
  dataStore?: IDataStore;
  /** Optional data-testid for automated testing */
  'data-testid'?: string;
}

export const CrowdsourceModal: React.FC<CrowdsourceModalProps> = ({
  isOpen,
  onClose,
  categoryId,
  prestationId,
  provinceSigla,
  categoryName: propCatName,
  categoryIcon: propCatIcon,
  prestationName: propPrestName,
  provinceName: propProvName,
  currentRefPrice: propRefPrice,
  currentSampleCount: propSampleCount,
  activeQuote,
  onSuccess,
  onSubmissionSuccess,
  dataStore,
  'data-testid': testId = 'crowdsource-modal',
}) => {
  // 1. Resolve Context Metadata from Dataset and Storage
  const store = dataStore ?? getDataStore();
  const existingOverride = store.getCrowdsourceOverride(categoryId, prestationId, provinceSigla);

  const category = useMemo(() => getCategoryById(categoryId), [categoryId]);
  const prestation = useMemo(() => getPrestationById(prestationId), [prestationId]);
  const province = useMemo(() => getProvinceBySigla(provinceSigla), [provinceSigla]);

  const catName = propCatName || category?.name || categoryId;
  const catIcon = propCatIcon || category?.icon || '🏷️';
  const prestName = propPrestName || prestation?.name || prestationId;
  const provName = propProvName || province?.nome || provinceSigla;

  // Effective baseline benchmark
  const effectiveRefPrice = useMemo(() => {
    if (existingOverride?.currentAvg) return existingOverride.currentAvg;
    if (propRefPrice && propRefPrice > 0) return propRefPrice;
    if (prestation) {
      const coeff = province?.costCoefficient ?? 1.0;
      return Math.round(prestation.basePrice * coeff);
    }
    return 100;
  }, [existingOverride, propRefPrice, prestation, province]);

  const effectiveSampleCount = useMemo(() => {
    if (existingOverride?.sampleCount) return existingOverride.sampleCount;
    return propSampleCount ?? 100;
  }, [existingOverride, propSampleCount]);

  // Validation bounds
  const bounds = useMemo(() => {
    const minBound = prestation?.validationBounds?.[0] ?? Math.max(1, Math.round(effectiveRefPrice * 0.15));
    const maxBound = prestation?.validationBounds?.[1] ?? Math.round(effectiveRefPrice * 8.0);
    return { minBound, maxBound };
  }, [prestation, effectiveRefPrice]);

  // 2. Component State
  const [rawAmount, setRawAmount] = useState<string>('');
  const [inputError, setInputError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [successResult, setSuccessResult] = useState<CrowdsourceSuccessPayload | null>(null);

  // 3. DOM Refs for Accessibility & Focus Trap
  const dialogRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const previousActiveElement = useRef<Element | null>(null);

  // Reset state on open/close
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement;
      setRawAmount('');
      setInputError(null);
      setIsSubmitting(false);
      setSuccessResult(null);

      // Lock body scroll
      const originalOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';

      const timer = setTimeout(() => {
        inputRef.current?.focus();
      }, 50);

      return () => {
        document.body.style.overflow = originalOverflow;
        clearTimeout(timer);
      };
    } else {
      if (previousActiveElement.current instanceof HTMLElement) {
        previousActiveElement.current.focus();
      }
    }
  }, [isOpen]);

  // Keyboard navigation: ESC key dismissal and Focus Trap
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }

      if (e.key === 'Tab' && dialogRef.current) {
        const focusableElements = dialogRef.current.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Helper: Parse string input to float
  const parseAmount = (val: string): number => {
    const cleaned = val
      .replace(/€/g, '')
      .replace(/\s+/g, '')
      .replace(/\./g, '')
      .replace(',', '.');
    return parseFloat(cleaned);
  };

  // Helper: Live input validation
  const validateInput = (val: string): { isValid: boolean; numVal: number; error?: string } => {
    if (!val || val.trim() === '') {
      return { isValid: false, numVal: 0, error: 'Inserisci la cifra che hai effettivamente pagato.' };
    }
    const num = parseAmount(val);
    const res = validateCrowdsourcedPrice(num, effectiveRefPrice, bounds);
    if (!res.isValid) {
      return { isValid: false, numVal: num, error: res.error };
    }
    return { isValid: true, numVal: num };
  };

  // Handle Input Changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setRawAmount(val);
    if (val.trim()) {
      const check = validateInput(val);
      setInputError(check.isValid ? null : check.error || 'Importo non valido.');
    } else {
      setInputError(null);
    }
  };

  // Handle Preset Chip Click
  const handlePresetClick = (amount: number) => {
    const strVal = amount.toString();
    setRawAmount(strVal);
    const check = validateInput(strVal);
    setInputError(check.isValid ? null : check.error || null);
    inputRef.current?.focus();
  };

  // Handle Form Submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const check = validateInput(rawAmount);
    if (!check.isValid) {
      setInputError(check.error || 'Importo non valido.');
      inputRef.current?.focus();
      return;
    }

    setIsSubmitting(true);
    setInputError(null);

    try {
      const submission = {
        categoryId,
        prestationId,
        provinceSigla,
        paidAmount: check.numVal,
      };

      const result = submitCrowdsourcedPrice(submission, {
        dataStore: store,
        baselineRefPrice: effectiveRefPrice,
        baselineSampleCount: effectiveSampleCount,
        customBounds: bounds,
      });

      if (!result.success || result.newAverage === undefined) {
        setInputError(result.error || 'Errore durante la registrazione del prezzo.');
        setIsSubmitting(false);
        return;
      }

      const prevAvg = effectiveRefPrice;
      const newAvg = result.newAverage;
      const prevCount = effectiveSampleCount;
      const newCount = result.newSampleCount ?? prevCount + 1;
      const diffEuro = Math.round((newAvg - prevAvg) * 100) / 100;
      const diffPct = Math.round(((newAvg - prevAvg) / prevAvg) * 10000) / 100;

      const payload: CrowdsourceSuccessPayload = {
        categoryId,
        prestationId,
        provinceSigla,
        paidAmount: check.numVal,
        previousAverage: prevAvg,
        newAverage: newAvg,
        previousSampleCount: prevCount,
        newSampleCount: newCount,
        diffFromPrevious: diffEuro,
        diffPctFromPrevious: diffPct,
      };

      setSuccessResult(payload);
      setIsSubmitting(false);

      // Trigger parent callbacks
      onSuccess?.(payload);
      onSubmissionSuccess?.(newAvg, newCount);
    } catch {
      setInputError('Si è verificato un errore imprevisto. Riprova tra poco.');
      setIsSubmitting(false);
    }
  };

  // Handle Backdrop Click
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in"
      onClick={handleBackdropClick}
      data-testid={testId}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="crowdsource-modal-title"
        aria-describedby="crowdsource-modal-desc"
        className="w-full max-w-lg bg-white border-2 border-slate-900 rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh] animate-scale-in text-slate-900"
      >
        {/* Header Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b-2 border-slate-900 bg-amber-100">
          <div className="flex items-center gap-2.5">
            <span className="text-xl" aria-hidden="true">
              {catIcon}
            </span>
            <div>
              <h2
                id="crowdsource-modal-title"
                className="text-base sm:text-lg font-black text-slate-950 leading-tight font-display"
              >
                Segnala quanto hai pagato
              </h2>
              <p className="text-xs text-slate-700 font-semibold">
                Contributo 100% anonimo alla trasparenza dei prezzi
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Chiudi finestra"
            className="p-1.5 rounded-xl border border-slate-900 bg-white text-slate-900 hover:bg-rose-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5 bg-white text-slate-900">
          {successResult ? (
            /* ==========================================
               INSTANT FEEDBACK SCREEN (SUCCESS STATE)
               ========================================== */
            <div className="space-y-5 text-center py-2 animate-fade-in">
              <div className="w-14 h-14 mx-auto rounded-full bg-emerald-200 border-2 border-slate-900 flex items-center justify-center text-slate-950">
                <CheckCircle2 className="w-8 h-8" />
              </div>

              <div>
                <h3 className="text-xl font-black text-slate-950">
                  Segnalazione Anonima Registrata!
                </h3>
                <p id="crowdsource-modal-desc" className="text-sm text-slate-700 font-medium mt-1">
                  Grazie! Il tuo dato è stato integrato istantaneamente con aggiornamento Bayesiano ponderato.
                </p>
              </div>

              {/* Before vs After Benchmark Card */}
              <div className="bg-slate-50 border-2 border-slate-900 rounded-2xl p-4 text-left space-y-3">
                <div className="flex items-center justify-between text-xs font-black text-slate-700 uppercase tracking-wider pb-2 border-b border-slate-200">
                  <span>Confronto Media Locale ({provName})</span>
                  <span className="text-emerald-700 flex items-center gap-1 font-black">
                    <Sparkles className="w-3.5 h-3.5" /> Aggiornato
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-white border border-slate-300">
                    <span className="text-xs text-slate-500 font-bold block">Vecchia Media</span>
                    <span className="text-lg font-black text-slate-800">
                      {successResult.previousAverage.toLocaleString('it-IT')} €
                    </span>
                    <span className="text-xs text-slate-500 block mt-0.5">
                      {successResult.previousSampleCount} segnalazioni
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-emerald-100 border-2 border-slate-900">
                    <span className="text-xs text-emerald-900 font-black block">
                      Nuova Media
                    </span>
                    <span className="text-lg font-black text-slate-950">
                      {successResult.newAverage.toLocaleString('it-IT')} €
                    </span>
                    <span className="text-xs text-emerald-800 font-bold block mt-0.5">
                      {successResult.newSampleCount} segnalazioni
                    </span>
                  </div>
                </div>

                {/* Shift Callout */}
                <div className="flex items-center justify-between pt-1 text-xs text-slate-700 font-semibold">
                  <span>Variazione benchmark:</span>
                  <span
                    className={`font-black flex items-center gap-1 ${
                      successResult.diffFromPrevious > 0
                        ? 'text-amber-700'
                        : successResult.diffFromPrevious < 0
                        ? 'text-emerald-700'
                        : 'text-slate-600'
                    }`}
                  >
                    {successResult.diffFromPrevious > 0 ? (
                      <TrendingUp className="w-3.5 h-3.5" />
                    ) : successResult.diffFromPrevious < 0 ? (
                      <TrendingDown className="w-3.5 h-3.5" />
                    ) : null}
                    {successResult.diffFromPrevious > 0 ? '+' : ''}
                    {successResult.diffFromPrevious.toFixed(2)} € (
                    {successResult.diffPctFromPrevious > 0 ? '+' : ''}
                    {successResult.diffPctFromPrevious.toFixed(2)}%)
                  </span>
                </div>
              </div>

              {/* Privacy badge */}
              <div className="flex items-center justify-center gap-2 text-xs text-slate-600 font-semibold">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>Nessun IP memorizzato • 100% confidenziale</span>
              </div>

              {/* Primary Dismiss Button */}
              <button
                type="button"
                onClick={onClose}
                className="w-full py-3 px-4 rounded-2xl font-black text-slate-950 bg-emerald-400 hover:bg-emerald-300 border-2 border-slate-900 shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2"
              >
                <span>Vedi il tuo preventivo ricalcolato</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            /* ==========================================
               INPUT FORM SCREEN (INITIAL STATE)
               ========================================== */
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Context Summary Pill */}
              <div
                id="crowdsource-modal-desc"
                className="bg-slate-50 border-2 border-slate-900 rounded-2xl p-3.5 text-xs text-slate-700 space-y-1.5"
              >
                <div className="flex items-center justify-between font-black">
                  <span className="text-slate-950 flex items-center gap-1.5">
                    <Tag className="w-4 h-4 text-slate-700 shrink-0" />
                    <span>{prestName}</span>
                  </span>
                  <span className="px-2.5 py-0.5 rounded-full bg-amber-100 border border-slate-900 text-slate-950 text-[11px] font-black inline-flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-rose-600 shrink-0" />
                    <span>{provName} ({provinceSigla})</span>
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-600 font-semibold pt-1">
                  <span>Prezzo medio di riferimento:</span>
                  <span className="font-black text-slate-950">
                    {effectiveRefPrice.toLocaleString('it-IT')} € ({effectiveSampleCount} campioni)
                  </span>
                </div>
              </div>

              {/* Quick Preset Chips */}
              <div className="space-y-1.5">
                <span className="text-xs font-black text-slate-700 block">
                  Scelta rapida:
                </span>
                <div className="flex flex-wrap gap-2">
                  {activeQuote &&
                    activeQuote >= bounds.minBound &&
                    activeQuote <= bounds.maxBound && (
                      <button
                        type="button"
                        onClick={() => handlePresetClick(activeQuote)}
                        className="px-3 py-1.5 rounded-xl text-xs font-black bg-emerald-200 text-slate-950 border-2 border-slate-900 hover:bg-emerald-300 transition-colors flex items-center gap-1.5"
                      >
                        <Coins className="w-3.5 h-3.5" />
                        <span>Ho pagato {activeQuote} €</span>
                      </button>
                    )}
                  <button
                    type="button"
                    onClick={() => handlePresetClick(Math.round(effectiveRefPrice * 0.85))}
                    className="px-2.5 py-1 rounded-xl text-xs font-bold bg-slate-100 border border-slate-300 text-slate-800 hover:bg-amber-100 transition-colors"
                  >
                    -15% ({Math.round(effectiveRefPrice * 0.85)} €)
                  </button>
                  <button
                    type="button"
                    onClick={() => handlePresetClick(effectiveRefPrice)}
                    className="px-2.5 py-1 rounded-xl text-xs font-bold bg-slate-100 border border-slate-300 text-slate-800 hover:bg-amber-100 transition-colors"
                  >
                    Esattamente la media ({effectiveRefPrice} €)
                  </button>
                  <button
                    type="button"
                    onClick={() => handlePresetClick(Math.round(effectiveRefPrice * 1.25))}
                    className="px-2.5 py-1 rounded-xl text-xs font-bold bg-slate-100 border border-slate-300 text-slate-800 hover:bg-amber-100 transition-colors"
                  >
                    +25% ({Math.round(effectiveRefPrice * 1.25)} €)
                  </button>
                </div>
              </div>

              {/* Amount Input */}
              <div className="space-y-1.5">
                <label
                  htmlFor="crowdsource-amount-input"
                  className="block text-sm font-black text-slate-950"
                >
                  Quanto hai pagato effettivamente?
                </label>
                <div className="relative rounded-2xl">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-rose-600 font-black text-lg">
                    €
                  </div>
                  <input
                    ref={inputRef}
                    id="crowdsource-amount-input"
                    type="text"
                    inputMode="decimal"
                    autoComplete="off"
                    value={rawAmount}
                    onChange={handleInputChange}
                    placeholder="Es. 280"
                    className={`block w-full pl-9 pr-16 py-3 rounded-2xl text-lg font-mono font-black bg-amber-50/60 text-slate-950 border-2 outline-none transition-all ${
                      inputError
                        ? 'border-red-600 bg-red-50'
                        : 'border-slate-900 focus:bg-white focus:ring-2 focus:ring-amber-400'
                    }`}
                  />
                  <div className="absolute inset-y-0 right-0 pr-3.5 flex items-center pointer-events-none text-xs font-black text-slate-500 uppercase">
                    EUR
                  </div>
                </div>

                {/* Validation helper or error */}
                {inputError ? (
                  <p className="text-xs text-red-600 flex items-center gap-1 font-bold mt-1">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                    <span>{inputError}</span>
                  </p>
                ) : (
                  <p className="text-xs text-slate-600 font-medium flex items-center gap-1 mt-1">
                    <Info className="w-3.5 h-3.5 shrink-0" />
                    <span>
                      Range verosimile per {catName}: da {bounds.minBound} € a {bounds.maxBound} €
                    </span>
                  </p>
                )}
              </div>

              {/* Privacy disclosure note */}
              <div className="flex items-start gap-2 p-3 rounded-2xl bg-emerald-50 border border-emerald-300 text-xs text-emerald-950 font-medium">
                <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-600 mt-0.5" />
                <span>
                  <strong>Nessun dato personale richiesto:</strong> la segnalazione viene aggregata in modo anonimo alla media provinciale e aiuta migliaia di consumatori a non farsi fregare.
                </span>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting || !rawAmount || Boolean(inputError)}
                className="w-full py-3.5 px-4 rounded-2xl font-black text-slate-950 bg-emerald-400 hover:bg-emerald-300 border-2 border-slate-900 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer"
              >
                {isSubmitting ? (
                  <span>Aggiornamento in corso...</span>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Invia Segnalazione Anonima</span>
                  </>
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default CrowdsourceModal;

/**
 * Reusable Trigger Button for 1-click modal opening.
 */
export const CrowdsourceTriggerButton: React.FC<{
  onClick: () => void;
  label?: string;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  className?: string;
}> = ({
  onClick,
  label = 'Io ho pagato una cifra diversa',
  variant = 'outline',
  className = '',
}) => {
  const baseClasses =
    'inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500';

  let variantClasses = '';
  switch (variant) {
    case 'primary':
      variantClasses = 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm';
      break;
    case 'secondary':
      variantClasses =
        'bg-emerald-50 hover:bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300';
      break;
    case 'ghost':
      variantClasses =
        'text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 hover:bg-slate-100 dark:hover:bg-slate-800';
      break;
    case 'outline':
    default:
      variantClasses =
        'border border-emerald-300 dark:border-emerald-700/60 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-950/40';
      break;
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`${baseClasses} ${variantClasses} ${className}`}
    >
      <Coins className="w-4 h-4" />
      <span>{label}</span>
    </button>
  );
};
