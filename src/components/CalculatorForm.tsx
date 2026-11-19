/**
 * src/components/CalculatorForm.tsx
 * High-performance, accessible, and reactive form component for "Mi Stanno Fregando?".
 *
 * Implements:
 * 1. 6 Categories with emoji icons, responsive cards, and ARIA radio semantics.
 * 2. Cascading Prestation Selector (36 baseline prestations + custom description fallback).
 * 3. 107 Italian Provinces Searchable Combobox with ranked instant filtering, keyboard navigation,
 *    and dual view modes (Grouped by Region vs Alphabetical A-Z).
 * 4. Robust Euro (€) Currency Parser supporting European comma (1.250,50 or 1250,00) and standard dot (1250.50).
 * 5. Quick quote preset suggestion pills based on realistic prestation market range.
 * 6. Real-time reactive calculation trigger on valid field change + explicit "Verifica Subito" CTA button.
 * 7. TypeScript contracts aligned with PROJECT.md and M2 components.
 */

import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Car,
  Home,
  Smile,
  HeartPulse,
  Sparkles,
  Key,
  Search,
  Check,
  ChevronDown,
  MapPin,
  AlertCircle,
  Calculator,
  ArrowRight,
  X,
  Layers,
  ListFilter,
  Info,
} from 'lucide-react';
import { dataset, getPrestationsByCategory } from '../core/dataset';
import { CategoryId, Prestation, Province } from '../core/types';

// ==========================================
// 1. Interfaces & Types
// ==========================================

export interface CalculatorFormParams {
  categoryId: CategoryId;
  prestationId: string;
  provinceSigla: string;
  quote: number;
  customPrestationDescription?: string;
}

export interface CalculatorFormState {
  categoryId: CategoryId;
  prestationId: string;
  isCustomPrestation: boolean;
  customDescription: string;
  provinceSigla: string;
  rawQuote: string;
  parsedQuote: number | null;
  quoteError: string | null;
  isValid: boolean;
}

export interface CalculatorFormProps {
  /** Initial or controlled category */
  initialCategory?: CategoryId;
  /** Initial or controlled prestation ID */
  initialPrestationId?: string;
  /** Initial or controlled custom prestation description */
  initialCustomDescription?: string;
  /** Initial or controlled province sigla (e.g. 'MI', 'RM') */
  initialProvinceSigla?: string;
  /** Initial or controlled quote amount */
  initialQuote?: number | string;
  /** Primary calculation callback triggered on valid changes and explicit button submit */
  onCalculate: (params: CalculatorFormParams) => void;
  /** Optional form submission alias callback */
  onSubmit?: (params: CalculatorFormParams) => void;
  /** Optional reactive state change callback */
  onChange?: (state: CalculatorFormState) => void;
  /** Calculating state flag for spinner inside CTA */
  isCalculating?: boolean;
  /** Optional CSS class override */
  className?: string;
  /** Test identifier */
  'data-testid'?: string;
}

// Category visual metadata mapping
const CATEGORY_META: Record<
  CategoryId,
  { label: string; iconEmoji: string; LucideIcon: React.ElementType; color: string; ringColor: string }
> = {
  auto: {
    label: 'Auto',
    iconEmoji: '🚗',
    LucideIcon: Car,
    color: 'from-blue-500/20 to-cyan-500/10 text-cyan-400 border-cyan-500/40',
    ringColor: 'ring-cyan-500/40',
  },
  casa: {
    label: 'Casa',
    iconEmoji: '🏠',
    LucideIcon: Home,
    color: 'from-amber-500/20 to-orange-500/10 text-amber-400 border-amber-500/40',
    ringColor: 'ring-amber-500/40',
  },
  dentista: {
    label: 'Dentista',
    iconEmoji: '🦷',
    LucideIcon: Smile,
    color: 'from-emerald-500/20 to-teal-500/10 text-emerald-400 border-emerald-500/40',
    ringColor: 'ring-emerald-500/40',
  },
  veterinario: {
    label: 'Veterinario',
    iconEmoji: '🐾',
    LucideIcon: HeartPulse,
    color: 'from-rose-500/20 to-pink-500/10 text-rose-400 border-rose-500/40',
    ringColor: 'ring-rose-500/40',
  },
  cerimonie: {
    label: 'Cerimonie',
    iconEmoji: '💐',
    LucideIcon: Sparkles,
    color: 'from-purple-500/20 to-indigo-500/10 text-purple-400 border-purple-500/40',
    ringColor: 'ring-purple-500/40',
  },
  affitti: {
    label: 'Affitti',
    iconEmoji: '🔑',
    LucideIcon: Key,
    color: 'from-indigo-500/20 to-blue-500/10 text-indigo-400 border-indigo-500/40',
    ringColor: 'ring-indigo-500/40',
  },
};

// ==========================================
// 2. Pure Helper Utilities
// ==========================================

/**
 * Normalizes Italian strings by stripping diacritics, converting to lowercase,
 * and normalizing apostrophes, quotes, hyphens, and whitespace to spaces.
 * Ensures "Forlì" -> "forli", "L'Aquila" -> "l aquila", "l aquila" -> "l aquila",
 * and "Reggio nell'Emilia" -> "reggio nell emilia".
 */
export function normalizeItalianText(text: string): string {
  if (!text) return '';
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/['’‘`´\-–—]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Known cadastral, historical, and alternative administrative aliases for Italian provinces.
 * Ensures official cadastral designations (e.g. "Reggio nell'Emilia" -> RE)
 * and alternate naming formats match seamlessly.
 */
export const PROVINCE_ALIASES: Record<string, string[]> = {
  RE: ["Reggio nell'Emilia", "Reggio nell Emilia", "Reggio nellemilia"],
  RC: ["Reggio di Calabria", "Reggio Calabria"],
  BZ: ["Bolzano-Bozen", "Bozen", "Bolzano Bozen"],
  AO: ["Valle d'Aosta", "Valle d Aosta", "Aoste"],
  FC: ["Cesena-Forlì", "Cesena Forli", "Forlì Cesena", "Forli Cesena"],
  MB: ["Monza e Brianza", "Monza Brianza", "Monza-Brianza"],
  PU: ["Pesaro e Urbino", "Pesaro Urbino", "Pesaro-Urbino"],
  SP: ["La Spezia"],
  AQ: ["L'Aquila", "L Aquila", "LAquila"],
};

/**
 * Robust Euro (€) Quote input parser.
 * Handles:
 * - European notation with dot thousands and comma decimal: `1.250,50` -> 1250.50
 * - European simple comma decimal: `1250,00` or `250,5` -> 1250.00
 * - Standard dot decimal: `1250.50` -> 1250.50
 * - Anglo-saxon comma thousands with dot decimal: `1,250.50` -> 1250.50
 * - Italian thousands dot without decimal: `1.250` -> 1250.00
 * - Plain integers: `250` -> 250.00
 * - Negative and zero value validations.
 */
export function parseQuoteInput(raw: unknown): { value: number | null; error: string | null } {
  if (raw === null || raw === undefined) {
    return { value: null, error: 'Inserisci un importo valido.' };
  }

  const str = String(raw).trim().replace(/€/g, '').replace(/\s+/g, '');
  if (!str) {
    return { value: null, error: "Inserisci l'importo del preventivo." };
  }

  // Check valid numerical characters
  if (!/^-?[0-9.,]+$/.test(str)) {
    return { value: null, error: "Inserisci un numero valido per l'importo." };
  }

  const isNegative = str.startsWith('-');
  const body = isNegative ? str.slice(1) : str;

  let normalized: string;

  if (body.includes('.') && body.includes(',')) {
    const lastDot = body.lastIndexOf('.');
    const lastComma = body.lastIndexOf(',');
    if (lastComma > lastDot) {
      // European: 1.250,50 -> remove dots, replace comma with dot
      normalized = body.replace(/\./g, '').replace(',', '.');
    } else {
      // Anglo-saxon: 1,250.50 -> remove commas
      normalized = body.replace(/,/g, '');
    }
  } else if (body.includes(',')) {
    const parts = body.split(',');
    if (parts.length === 2) {
      normalized = `${parts[0]}.${parts[1]}`;
    } else {
      normalized = body.replace(/,/g, '');
    }
  } else if (body.includes('.')) {
    if ((body.match(/\./g) || []).length > 1) {
      // Multiple dots: 1.000.000
      normalized = body.replace(/\./g, '');
    } else {
      const parts = body.split('.');
      // Italian 3-digit thousands separator check (e.g. 1.250 or 50.000)
      if (parts[1].length === 3 && parts[0].length <= 3) {
        normalized = body.replace(/\./g, '');
      } else {
        normalized = body;
      }
    }
  } else {
    normalized = body;
  }

  const parsed = parseFloat(normalized);
  if (isNaN(parsed) || !Number.isFinite(parsed)) {
    return { value: null, error: "Inserisci un numero valido per l'importo." };
  }

  const finalVal = isNegative ? -parsed : parsed;

  if (finalVal < 0) {
    return { value: finalVal, error: "L'importo del preventivo non può essere negativo." };
  }
  if (finalVal === 0) {
    return { value: 0, error: 'Inserisci un importo superiore a zero.' };
  }
  if (finalVal > 10_000_000) {
    return { value: finalVal, error: 'Importo fuori scala (massimo 10.000.000 €).' };
  }

  return { value: Math.round(finalVal * 100) / 100, error: null };
}

// ==========================================
// 3. React CalculatorForm Component
// ==========================================

export const CalculatorForm: React.FC<CalculatorFormProps> = ({
  initialCategory = 'auto',
  initialPrestationId,
  initialCustomDescription = '',
  initialProvinceSigla = 'MI',
  initialQuote = '',
  onCalculate,
  onSubmit,
  onChange,
  isCalculating = false,
  className = '',
  'data-testid': testId = 'calculator-form',
}) => {
  // 1. Form State
  const [selectedCategory, setSelectedCategory] = useState<CategoryId>(initialCategory);
  const [selectedPrestationId, setSelectedPrestationId] = useState<string>(() => {
    if (initialPrestationId && initialPrestationId !== 'custom') return initialPrestationId;
    const firstPrest = getPrestationsByCategory(initialCategory)[0];
    return firstPrest ? firstPrest.id : '';
  });
  const [isCustomPrestation, setIsCustomPrestation] = useState<boolean>(
    initialPrestationId === 'custom'
  );
  const [customDescription, setCustomDescription] = useState<string>(
    initialCustomDescription || ''
  );

  const [selectedProvinceSigla, setSelectedProvinceSigla] = useState<string>(
    initialProvinceSigla.toUpperCase()
  );

  // Quote State
  const [rawQuote, setRawQuote] = useState<string>(
    initialQuote !== undefined && initialQuote !== null ? String(initialQuote) : ''
  );
  const [quoteTouched, setQuoteTouched] = useState<boolean>(false);

  // Category & Province Dropdown UI State
  const [isCategoryOpen, setIsCategoryOpen] = useState<boolean>(false);
  const [isProvinceOpen, setIsProvinceOpen] = useState<boolean>(false);
  const [provinceSearchQuery, setProvinceSearchQuery] = useState<string>('');
  const [provinceViewMode, setProvinceViewMode] = useState<'region' | 'alphabetical'>('region');
  const [highlightedProvinceIndex, setHighlightedProvinceIndex] = useState<number>(0);

  // "Proponi Categoria" Suggestion Box State
  const [isSuggestCategoryOpen, setIsSuggestCategoryOpen] = useState<boolean>(false);
  const [suggestedCatName, setSuggestedCatName] = useState<string>('');
  const [suggestedCatExample, setSuggestedCatExample] = useState<string>('');
  const [suggestionSent, setSuggestionSent] = useState<boolean>(false);

  const handleSaveCategorySuggestion = () => {
    if (!suggestedCatName.trim()) return;
    try {
      const key = 'msf_category_suggestions_v1';
      const existingRaw = typeof window !== 'undefined' ? window.localStorage.getItem(key) : null;
      const existing = existingRaw ? JSON.parse(existingRaw) : [];
      existing.push({
        category: suggestedCatName.trim(),
        example: suggestedCatExample.trim(),
        createdAt: new Date().toISOString(),
      });
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(existing));
      }
    } catch {
      // ignore storage errors
    }
    setSuggestionSent(true);
    setTimeout(() => {
      setSuggestedCatName('');
      setSuggestedCatExample('');
    }, 3500);
  };

  // Refs for outside click & focus & stable callback refs
  const categoryDropdownRef = useRef<HTMLDivElement | null>(null);
  const provinceDropdownRef = useRef<HTMLDivElement | null>(null);
  const provinceSearchInputRef = useRef<HTMLInputElement | null>(null);
  const provinceListRef = useRef<HTMLDivElement | null>(null);
  const onChangeRef = useRef(onChange);
  const onCalculateRef = useRef(onCalculate);
  onChangeRef.current = onChange;
  onCalculateRef.current = onCalculate;

  // Synchronize incoming props (e.g. from URL share links)
  useEffect(() => {
    if (initialCategory && initialCategory !== selectedCategory) {
      setSelectedCategory(initialCategory);
    }
  }, [initialCategory]);

  useEffect(() => {
    if (initialPrestationId) {
      if (initialPrestationId === 'custom') {
        setIsCustomPrestation(true);
      } else if (initialPrestationId !== selectedPrestationId) {
        setIsCustomPrestation(false);
        setSelectedPrestationId(initialPrestationId);
      }
    }
  }, [initialPrestationId]);

  useEffect(() => {
    if (initialCustomDescription !== undefined && initialCustomDescription !== customDescription) {
      setCustomDescription(initialCustomDescription);
    }
  }, [initialCustomDescription]);

  useEffect(() => {
    if (initialProvinceSigla && initialProvinceSigla.toUpperCase() !== selectedProvinceSigla) {
      setSelectedProvinceSigla(initialProvinceSigla.toUpperCase());
    }
  }, [initialProvinceSigla]);

  useEffect(() => {
    if (
      initialQuote !== undefined &&
      initialQuote !== null &&
      parseQuoteInput(rawQuote).value !== initialQuote
    ) {
      setRawQuote(String(initialQuote));
    }
  }, [initialQuote]);

  // Available prestations for active category
  const availablePrestations = useMemo<Prestation[]>(() => {
    return getPrestationsByCategory(selectedCategory);
  }, [selectedCategory]);

  // Currently selected prestation object
  const currentPrestation = useMemo<Prestation | undefined>(() => {
    if (isCustomPrestation) return undefined;
    return availablePrestations.find((p) => p.id === selectedPrestationId);
  }, [availablePrestations, selectedPrestationId, isCustomPrestation]);

  // Currently selected province object
  const currentProvince = useMemo<Province | undefined>(() => {
    return dataset.provinces.find((p) => p.sigla.toUpperCase() === selectedProvinceSigla.toUpperCase());
  }, [selectedProvinceSigla]);

  // Parsed quote and error calculation
  const { value: parsedQuote, error: quoteError } = useMemo(() => {
    return parseQuoteInput(rawQuote);
  }, [rawQuote]);

  // Form validity check
  const isFormValid = useMemo<boolean>(() => {
    const hasCategory = Boolean(selectedCategory);
    const hasPrestation = isCustomPrestation ? customDescription.trim().length > 0 : Boolean(selectedPrestationId);
    const hasProvince = Boolean(selectedProvinceSigla && currentProvince);
    const hasValidQuote = parsedQuote !== null && parsedQuote > 0 && !quoteError;

    return hasCategory && hasPrestation && hasProvince && hasValidQuote;
  }, [selectedCategory, isCustomPrestation, customDescription, selectedPrestationId, selectedProvinceSigla, currentProvince, parsedQuote, quoteError]);

  // Notify parent of state changes
  useEffect(() => {
    onChangeRef.current?.({
      categoryId: selectedCategory,
      prestationId: isCustomPrestation ? 'custom' : selectedPrestationId,
      isCustomPrestation,
      customDescription,
      provinceSigla: selectedProvinceSigla,
      rawQuote,
      parsedQuote,
      quoteError,
      isValid: isFormValid,
    });
  }, [selectedCategory, selectedPrestationId, isCustomPrestation, customDescription, selectedProvinceSigla, rawQuote, parsedQuote, quoteError, isFormValid]);

  // Handle Category Click inside Dropdown
  const handleCategorySelect = (catId: CategoryId) => {
    setSelectedCategory(catId);
    setIsCategoryOpen(false);
    setIsSuggestCategoryOpen(false);
    const prests = getPrestationsByCategory(catId);
    if (prests.length > 0) {
      setSelectedPrestationId(prests[0].id);
      setIsCustomPrestation(false);
    }
  };

  // Handle Prestation Change
  const handlePrestationSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    if (val === 'custom') {
      setIsCustomPrestation(true);
    } else {
      setIsCustomPrestation(false);
      setSelectedPrestationId(val);
    }
  };

  // 107 Filtered & Ranked Provinces with Cadastral Aliases and Diacritic Normalization
  const filteredProvinces = useMemo<Province[]>(() => {
    const q = normalizeItalianText(provinceSearchQuery);
    if (!q) {
      return [...dataset.provinces].sort((a, b) => a.nome.localeCompare(b.nome));
    }

    const scored: { province: Province; score: number }[] = [];
    for (const p of dataset.provinces) {
      const nomeNorm = normalizeItalianText(p.nome);
      const siglaNorm = normalizeItalianText(p.sigla);
      const regNorm = normalizeItalianText(p.regione);
      const aliases = PROVINCE_ALIASES[p.sigla] || [];
      const aliasesNorm = aliases.map((a) => normalizeItalianText(a));

      let score = 999;
      if (siglaNorm === q) {
        score = 1;
      } else if (
        nomeNorm.startsWith(q) ||
        aliasesNorm.some((a) => a.startsWith(q) || q.startsWith(a))
      ) {
        score = 2;
      } else if (siglaNorm.startsWith(q)) {
        score = 3;
      } else if (
        nomeNorm.includes(q) ||
        aliasesNorm.some((a) => a.includes(q) || q.includes(a))
      ) {
        score = 4;
      } else if (regNorm.startsWith(q)) {
        score = 5;
      } else if (regNorm.includes(q)) {
        score = 6;
      }

      if (score < 999) {
        scored.push({ province: p, score });
      }
    }

    scored.sort((a, b) => {
      if (a.score !== b.score) return a.score - b.score;
      return a.province.nome.localeCompare(b.province.nome);
    });

    return scored.map((s) => s.province);
  }, [provinceSearchQuery]);

  // Provinces Grouped by Region
  const provincesByRegion = useMemo<Record<string, Province[]>>(() => {
    const map: Record<string, Province[]> = {};
    for (const p of filteredProvinces) {
      if (!map[p.regione]) {
        map[p.regione] = [];
      }
      map[p.regione].push(p);
    }
    return map;
  }, [filteredProvinces]);

  // Click outside listener for category & province dropdowns
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      if (
        categoryDropdownRef.current &&
        !categoryDropdownRef.current.contains(target)
      ) {
        setIsCategoryOpen(false);
      }
      if (
        provinceDropdownRef.current &&
        !provinceDropdownRef.current.contains(target)
      ) {
        setIsProvinceOpen(false);
      }
    };

    if (isCategoryOpen || isProvinceOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      if (isProvinceOpen) {
        setTimeout(() => {
          provinceSearchInputRef.current?.focus();
        }, 50);
      }
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isCategoryOpen, isProvinceOpen]);

  // Keyboard navigation for province list
  const handleProvinceKeyDown = (e: React.KeyboardEvent) => {
    if (!isProvinceOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        setIsProvinceOpen(true);
      }
      return;
    }

    if (e.key === 'Escape') {
      e.preventDefault();
      setIsProvinceOpen(false);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedProvinceIndex((prev) =>
        prev < filteredProvinces.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedProvinceIndex((prev) =>
        prev > 0 ? prev - 1 : filteredProvinces.length - 1
      );
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const p = filteredProvinces[highlightedProvinceIndex];
      if (p) {
        setSelectedProvinceSigla(p.sigla);
        setIsProvinceOpen(false);
        setProvinceSearchQuery('');
      }
    }
  };

  // Scroll active item into view
  useEffect(() => {
    if (isProvinceOpen && provinceListRef.current) {
      const activeEl = provinceListRef.current.querySelector(
        `[data-index="${highlightedProvinceIndex}"]`
      );
      if (activeEl) {
        activeEl.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [highlightedProvinceIndex, isProvinceOpen]);

  // Form Submit Handler ("Verifica Subito")
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setQuoteTouched(true);

    if (!isFormValid || parsedQuote === null || parsedQuote <= 0) {
      return;
    }

    const params: CalculatorFormParams = {
      categoryId: selectedCategory,
      prestationId: isCustomPrestation ? 'custom' : selectedPrestationId,
      provinceSigla: selectedProvinceSigla,
      quote: parsedQuote,
      customPrestationDescription: isCustomPrestation ? customDescription.trim() : undefined,
    };

    onCalculate(params);
    onSubmit?.(params);
  };

  const activeCatObj = dataset.categories.find((c) => c.id === selectedCategory);
  const ActiveCatIcon = CATEGORY_META[selectedCategory]?.LucideIcon || Layers;

  return (
    <form
      onSubmit={handleSubmit}
      data-testid={testId}
      className={`w-full max-w-5xl mx-auto p-5 sm:p-6 bg-white border-2 border-slate-900 rounded-3xl shadow-xl shadow-slate-900/10 text-slate-900 ${className}`}
    >
      {/* SINGLE CLEAN HORIZONTAL BAR: Categoria (tendina) + Prestazione (senza media) + Provincia + Preventivo + Verifica */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
        {/* COL 1: Categoria a tendina (2 cols on desktop) */}
        <div className="md:col-span-2 w-full relative" ref={categoryDropdownRef}>
          <label className="h-5 text-[11px] uppercase font-black tracking-wider text-slate-700 flex items-center gap-1.5 mb-1.5 whitespace-nowrap">
            <span className="w-4 h-4 rounded-full bg-amber-300 border border-slate-900 text-slate-950 flex items-center justify-center text-[10px] font-black shrink-0">1</span>
            <span>Categoria</span>
          </label>
          <button
            type="button"
            onClick={() => setIsCategoryOpen(!isCategoryOpen)}
            aria-expanded={isCategoryOpen}
            aria-haspopup="true"
            className="w-full h-[50px] bg-slate-50 hover:bg-white border-2 border-slate-900 text-slate-900 rounded-2xl px-3 flex items-center justify-between gap-1.5 outline-none transition-all duration-150 shadow-sm cursor-pointer"
          >
            <span className="flex items-center gap-2 min-w-0">
              <ActiveCatIcon className="w-4 h-4 text-slate-900 shrink-0" />
              <span className="font-bold text-sm text-slate-900 truncate">
                {activeCatObj?.name || 'Categoria'}
              </span>
            </span>
            <ChevronDown className={`w-4 h-4 text-slate-900 shrink-0 transition-transform duration-200 ${isCategoryOpen ? 'rotate-180' : ''}`} />
          </button>

          {isCategoryOpen && (
            <div
              role="radiogroup"
              aria-label="Seleziona la categoria di intervento"
              className="absolute left-0 top-full mt-2 w-60 bg-white border-2 border-slate-900 rounded-2xl shadow-2xl p-2 z-50 animate-fade-in space-y-1"
            >
              {dataset.categories.map((cat) => {
                const isSelected = selectedCategory === cat.id && !isSuggestCategoryOpen;
                const CatIcon = CATEGORY_META[cat.id]?.LucideIcon || Layers;
                return (
                  <button
                    key={cat.id}
                    type="button"
                    role="radio"
                    aria-checked={isSelected}
                    onClick={() => handleCategorySelect(cat.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-sm font-bold transition-colors cursor-pointer ${
                      isSelected
                        ? 'bg-slate-900 text-white'
                        : 'text-slate-800 hover:bg-slate-100'
                    }`}
                  >
                    <span className="flex items-center gap-2.5">
                      <CatIcon className={`w-4 h-4 shrink-0 ${isSelected ? 'text-amber-300' : 'text-slate-600'}`} />
                      <span>{cat.name}</span>
                    </span>
                    {isSelected && <Check className="w-3.5 h-3.5 stroke-[3] shrink-0" />}
                  </button>
                );
              })}

              <div className="pt-1 mt-1 border-t border-slate-200">
                <button
                  type="button"
                  data-testid="proponi-categoria-btn"
                  onClick={() => {
                    setIsCategoryOpen(false);
                    setIsSuggestCategoryOpen(!isSuggestCategoryOpen);
                    setSuggestionSent(false);
                  }}
                  className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-extrabold text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
                >
                  <Layers className="w-4 h-4 text-slate-500 shrink-0" />
                  <span>Altra categoria (Proponi tu)</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* COL 2: Prestazione (3 cols on desktop — SENZA medie anticipate) */}
        <div className="md:col-span-3 w-full">
          <label htmlFor="prestation-select" className="h-5 text-[11px] uppercase font-black tracking-wider text-slate-700 flex items-center gap-1.5 mb-1.5 whitespace-nowrap">
            <span className="w-4 h-4 rounded-full bg-slate-900 text-white flex items-center justify-center text-[10px] font-black shrink-0">2</span>
            <span>Prestazione o Intervento</span>
          </label>
          <div className="relative">
            <select
              id="prestation-select"
              value={isCustomPrestation ? 'custom' : selectedPrestationId}
              onChange={handlePrestationSelect}
              className="w-full h-[50px] appearance-none bg-slate-50 hover:bg-white border-2 border-slate-900 focus:bg-white focus:ring-2 focus:ring-amber-400 text-slate-900 text-sm font-bold rounded-2xl px-3.5 pr-9 outline-none transition-all duration-150 cursor-pointer shadow-sm"
            >
              {availablePrestations.map((p) => (
                <option key={p.id} value={p.id} className="bg-white text-slate-900 py-1 font-semibold">
                  {p.name}
                </option>
              ))}
              <option value="custom" className="bg-amber-50 text-slate-900 font-bold py-1">
                Altra prestazione (personalizzata)...
              </option>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-900">
              <ChevronDown className="w-4 h-4 stroke-[2.5]" />
            </div>
          </div>
        </div>

        {/* COL 3: Provincia (3 cols on desktop) */}
        <div className="md:col-span-3 w-full" ref={provinceDropdownRef}>
          <label className="h-5 text-[11px] uppercase font-black tracking-wider text-slate-700 flex items-center gap-1.5 mb-1.5 whitespace-nowrap">
            <span className="w-4 h-4 rounded-full bg-emerald-200 border border-slate-900 text-slate-950 flex items-center justify-center text-[10px] font-black shrink-0">3</span>
            <span>Provincia</span>
          </label>

          <button
            type="button"
            role="combobox"
            aria-haspopup="listbox"
            aria-controls="provinces-listbox"
            aria-expanded={isProvinceOpen}
            onClick={() => setIsProvinceOpen(!isProvinceOpen)}
            onKeyDown={handleProvinceKeyDown}
            className="w-full h-[50px] bg-slate-50 hover:bg-white border-2 border-slate-900 text-slate-900 rounded-2xl px-3 flex items-center justify-between outline-none transition-all duration-150 shadow-sm"
          >
            {currentProvince ? (
              <div className="flex items-center gap-2 truncate">
                <span className="bg-emerald-300 text-slate-950 border border-slate-900 px-2 py-0.5 rounded-lg font-mono font-black text-xs shrink-0">
                  {currentProvince.sigla}
                </span>
                <span className="font-extrabold text-sm text-slate-900 truncate">
                  {currentProvince.nome}
                </span>
              </div>
            ) : (
              <span className="text-slate-500 text-sm font-medium truncate">Provincia...</span>
            )}
            <ChevronDown className={`w-4 h-4 text-slate-900 shrink-0 transition-transform duration-200 ${isProvinceOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Floating Searchable Dropdown Overlay */}
          {isProvinceOpen && (
            <div className="relative z-50">
              <div className="absolute top-2 left-0 w-full md:w-[360px] bg-white border-2 border-slate-900 rounded-2xl shadow-2xl p-3 animate-fade-in">
                <div className="flex items-center gap-2 mb-3">
                  <div className="relative flex-1">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      ref={provinceSearchInputRef}
                      type="text"
                      value={provinceSearchQuery}
                      onChange={(e) => {
                        setProvinceSearchQuery(e.target.value);
                        setHighlightedProvinceIndex(0);
                      }}
                      onKeyDown={handleProvinceKeyDown}
                      placeholder="Cerca (es. Milano, RM)..."
                      className="w-full bg-slate-50 border-2 border-slate-900 text-slate-900 font-semibold text-xs rounded-xl py-2 pl-8 pr-7 outline-none"
                    />
                    {provinceSearchQuery && (
                      <button
                        type="button"
                        onClick={() => setProvinceSearchQuery('')}
                        className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-800"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>

                  <div className="flex items-center bg-slate-100 border border-slate-300 p-0.5 rounded-xl shrink-0">
                    <button
                      type="button"
                      title="Raggruppa per Regione"
                      onClick={() => setProvinceViewMode('region')}
                      className={`p-1.5 rounded-lg text-[11px] font-bold flex items-center gap-1 transition-colors ${
                        provinceViewMode === 'region'
                          ? 'bg-slate-900 text-white'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      <Layers className="w-3 h-3" />
                      <span>Reg.</span>
                    </button>
                    <button
                      type="button"
                      title="Ordine Alfabetico A-Z"
                      onClick={() => setProvinceViewMode('alphabetical')}
                      className={`p-1.5 rounded-lg text-[11px] font-bold flex items-center gap-1 transition-colors ${
                        provinceViewMode === 'alphabetical'
                          ? 'bg-slate-900 text-white'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      <ListFilter className="w-3 h-3" />
                      <span>A-Z</span>
                    </button>
                  </div>
                </div>

                <div
                  ref={provinceListRef}
                  id="provinces-listbox"
                  role="listbox"
                  className="max-h-60 overflow-y-auto space-y-1 pr-1 custom-scrollbar"
                >
                  {filteredProvinces.length === 0 ? (
                    <div className="p-4 text-center text-xs text-slate-500 font-semibold">
                      Nessuna provincia trovata per &quot;{provinceSearchQuery}&quot;
                    </div>
                  ) : provinceViewMode === 'alphabetical' || provinceSearchQuery.trim() !== '' ? (
                    filteredProvinces.map((p, idx) => {
                      const isSelected = p.sigla.toUpperCase() === selectedProvinceSigla.toUpperCase();
                      const isHighlighted = idx === highlightedProvinceIndex;

                      return (
                        <div
                          key={p.sigla}
                          data-index={idx}
                          role="option"
                          aria-selected={isSelected}
                          onClick={() => {
                            setSelectedProvinceSigla(p.sigla);
                            setIsProvinceOpen(false);
                            setProvinceSearchQuery('');
                          }}
                          onMouseEnter={() => setHighlightedProvinceIndex(idx)}
                          className={`p-2 rounded-xl flex items-center justify-between text-xs cursor-pointer transition-colors ${
                            isHighlighted
                              ? 'bg-amber-100 text-slate-950'
                              : 'hover:bg-slate-100 text-slate-700'
                          } ${isSelected ? 'border-2 border-slate-900 bg-emerald-100 font-bold' : ''}`}
                        >
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-black bg-slate-900 text-white px-1.5 py-0.5 rounded text-[11px]">
                              {p.sigla}
                            </span>
                            <span className="font-bold text-slate-900">{p.nome}</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] font-mono text-slate-500">
                              x{p.costCoefficient.toFixed(2)}
                            </span>
                            {isSelected && <Check className="w-3.5 h-3.5 text-emerald-700 stroke-[3]" />}
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    Object.entries(provincesByRegion).map(([regionName, provs]) => (
                      <div key={regionName} className="mb-2">
                        <div className="sticky top-0 bg-slate-100 py-1 px-2 text-[11px] font-black uppercase tracking-wider text-slate-700 flex items-center justify-between rounded-lg">
                          <span>{regionName}</span>
                          <span className="text-slate-500 font-mono">({provs.length})</span>
                        </div>
                        <div className="grid grid-cols-2 gap-1 pt-1">
                          {provs.map((p) => {
                            const isSelected = p.sigla.toUpperCase() === selectedProvinceSigla.toUpperCase();
                            return (
                              <div
                                key={p.sigla}
                                role="option"
                                aria-selected={isSelected}
                                onClick={() => {
                                  setSelectedProvinceSigla(p.sigla);
                                  setIsProvinceOpen(false);
                                  setProvinceSearchQuery('');
                                }}
                                className={`p-1.5 px-2 rounded-lg flex items-center justify-between text-xs cursor-pointer transition-colors ${
                                  isSelected
                                    ? 'bg-emerald-200 border border-slate-900 text-slate-950 font-bold'
                                    : 'hover:bg-amber-50 text-slate-700'
                                }`}
                              >
                                <div className="flex items-center gap-1.5 truncate">
                                  <span className="font-mono font-black text-slate-500 text-[11px]">
                                    {p.sigla}
                                  </span>
                                  <span className="font-semibold text-slate-900 truncate">{p.nome}</span>
                                </div>
                                {isSelected && <Check className="w-3 h-3 text-slate-900 shrink-0 stroke-[3]" />}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* COL 4: Preventivo € (2 cols on desktop) */}
        <div className="md:col-span-2 w-full">
          <label htmlFor="quote-input" className="h-5 text-[11px] uppercase font-black tracking-wider text-slate-700 flex items-center gap-1.5 mb-1.5 whitespace-nowrap">
            <span className="w-4 h-4 rounded-full bg-rose-200 border border-slate-900 text-slate-950 flex items-center justify-center text-[10px] font-black shrink-0">4</span>
            <span>Preventivo (€)</span>
          </label>
          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-700 font-black text-lg select-none">
              €
            </div>
            <input
              id="quote-input"
              type="text"
              inputMode="decimal"
              value={rawQuote}
              onChange={(e) => {
                setRawQuote(e.target.value);
                setQuoteTouched(true);
              }}
              placeholder="es. 480"
              className={`w-full h-[50px] bg-slate-50 focus:bg-white border-2 text-slate-950 font-mono font-bold text-lg rounded-2xl pl-8 pr-8 outline-none transition-all duration-150 shadow-sm ${
                quoteTouched && quoteError
                  ? 'border-red-600 bg-red-50'
                  : 'border-slate-900 focus:ring-2 focus:ring-amber-400'
              }`}
            />
            {rawQuote && (
              <button
                type="button"
                onClick={() => {
                  setRawQuote('');
                  setQuoteTouched(false);
                }}
                aria-label="Cancella importo"
                className="absolute inset-y-0 right-0 flex items-center pr-2.5 text-slate-400 hover:text-slate-900"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* COL 5: Submit CTA Button (2 cols on desktop) */}
        <div className="md:col-span-2 w-full">
          <div className="hidden md:block h-5 mb-1.5" aria-hidden="true" />
          <button
            type="submit"
            disabled={isCalculating}
            aria-label="Verifica Subito il Preventivo"
            title="Verifica Subito il Preventivo"
            className={`w-full h-[50px] px-4 rounded-2xl font-extrabold text-sm flex items-center justify-center gap-1.5 transition-all duration-150 border-2 border-slate-900 ${
              isFormValid
                ? 'bg-slate-900 hover:bg-slate-800 text-white shadow-md hover:shadow-lg cursor-pointer active:translate-y-0.5'
                : 'bg-slate-200 text-slate-500 cursor-not-allowed'
            }`}
          >
            <Calculator className="w-4 h-4 shrink-0" />
            <span>Verifica</span>
            <ArrowRight className="w-4 h-4 shrink-0" />
          </button>
        </div>
      </div>

      {/* Interactive Suggestion Drawer when "Altra categoria (Proponi tu)" is selected */}
      {isSuggestCategoryOpen && (
        <div className="mt-3 p-4 bg-slate-50 border-2 border-slate-900 rounded-2xl shadow-md animate-fade-in">
          <div className="flex items-start justify-between gap-2 mb-2.5">
            <div>
              <span className="inline-flex items-center gap-1 text-[10px] font-black uppercase tracking-wider bg-slate-900 text-white px-2.5 py-0.5 rounded-full mb-1">
                Nuove Categorie Community
              </span>
              <h4 className="text-sm sm:text-base font-extrabold text-slate-950 font-display">
                Manca una categoria o un servizio? Segnalalo e lo inseriremo nel sito.
              </h4>
            </div>
            <button
              type="button"
              onClick={() => setIsSuggestCategoryOpen(false)}
              className="text-slate-500 hover:text-slate-950 p-1 rounded-lg"
              aria-label="Chiudi box suggerimento"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {suggestionSent ? (
            <div className="p-3 bg-emerald-100 border border-emerald-500 rounded-xl flex items-center justify-between gap-3 text-emerald-950 font-bold text-xs sm:text-sm">
              <span>Grazie! La tua proposta è stata salvata e sarà valutata per i prossimi aggiornamenti.</span>
              <button
                type="button"
                onClick={() => {
                  setSuggestionSent(false);
                  setIsSuggestCategoryOpen(false);
                }}
                className="px-3 py-1 bg-white border border-slate-900 rounded-lg text-xs font-bold shrink-0"
              >
                Chiudi
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-12 gap-2.5 items-center">
              <div className="sm:col-span-5">
                <input
                  type="text"
                  value={suggestedCatName}
                  onChange={(e) => setSuggestedCatName(e.target.value)}
                  placeholder="Che categoria vorresti? (es. Avvocato, Palestra, Tech...)"
                  className="w-full h-[42px] bg-white border-2 border-slate-900 rounded-xl px-3 text-xs sm:text-sm font-bold text-slate-900 outline-none focus:ring-2 focus:ring-slate-400"
                />
              </div>
              <div className="sm:col-span-5">
                <input
                  type="text"
                  value={suggestedCatExample}
                  onChange={(e) => setSuggestedCatExample(e.target.value)}
                  placeholder="Quale servizio specifico? (es. Riparazione smartphone...)"
                  className="w-full h-[42px] bg-white border-2 border-slate-900 rounded-xl px-3 text-xs sm:text-sm font-semibold text-slate-900 outline-none focus:ring-2 focus:ring-slate-400"
                />
              </div>
              <div className="sm:col-span-2">
                <button
                  type="button"
                  onClick={handleSaveCategorySuggestion}
                  disabled={!suggestedCatName.trim()}
                  className={`w-full h-[42px] rounded-xl font-extrabold text-xs border-2 border-slate-900 transition-all flex items-center justify-center gap-1 ${
                    suggestedCatName.trim()
                      ? 'bg-slate-900 hover:bg-slate-800 text-white shadow-sm hover:shadow cursor-pointer active:translate-y-0.5'
                      : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                  }`}
                >
                  <span>Invia Proposta</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Custom Prestation Input Row (if 'custom' selected) */}
      {isCustomPrestation && (
        <div className="mt-3 p-3.5 bg-slate-50 border-2 border-slate-900 rounded-2xl animate-fade-in flex flex-col sm:flex-row sm:items-center gap-3">
          <label htmlFor="custom-prestation-desc" className="text-xs font-extrabold text-slate-900 shrink-0">
            Descrivi il lavoro:
          </label>
          <input
            id="custom-prestation-desc"
            type="text"
            value={customDescription}
            onChange={(e) => setCustomDescription(e.target.value)}
            placeholder="es. Sostituzione pompa acqua, impianto zigomatico..."
            className="flex-1 bg-white border-2 border-slate-900 text-sm font-semibold text-slate-900 rounded-xl py-2 px-3 outline-none"
          />
        </div>
      )}

      {/* Validation Error Message */}
      {quoteTouched && quoteError && (
        <div className="mt-2.5 text-red-600 font-bold text-xs flex items-center gap-1.5 animate-fade-in">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{quoteError}</span>
        </div>
      )}

      {/* Minimal Neutral Info Bar (no pre-revealed average price or range before clicking Verifica) */}
      <div className="mt-3 pt-2.5 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-500">
        <div className="flex items-center gap-1.5 min-w-0">
          <Info className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span className="truncate font-medium">
            {currentPrestation
              ? currentPrestation.description
              : 'Inserisci il preventivo ricevuto e premi Verifica per avviare l’analisi del Fregometro.'}
          </span>
        </div>
        <span className="text-[11px] font-bold text-slate-500 sm:shrink-0 leading-snug">
          107 Province ISTAT • Analisi istantanea su Verifica
        </span>
      </div>
    </form>
  );
};

export default CalculatorForm;
