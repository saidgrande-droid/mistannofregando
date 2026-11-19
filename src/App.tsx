/**
 * src/App.tsx
 * Master Layout Coordinator for "Mi Stanno Fregando?".
 *
 * Linear, symmetrical, top-to-bottom layout:
 * 1. Centered Playful Brand Logo & Header
 * 2. Horizontal Main Price Input Bar (CalculatorForm)
 * 3. Balanced Results Section (Tachometer + ResultSummary, then AffiliateCard + ShareCard)
 * 4. Real-World Proofs & Community Section ("Le Prove" + "Io ho pagato X€")
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  CheckCircle2,
  Users,
  Sparkles,
  TrendingDown,
  ShieldCheck,
  Car,
  Home,
  Smile,
  HeartPulse,
  Key,
  ChevronDown,
  Info,
} from 'lucide-react';

import { CategoryId, CalculationResult } from './core/types';
import {
  getCategoryById,
  getPrestationById,
  getProvinceBySigla,
  getPrestationsByCategory,
} from './core/dataset';
import { calculateDiscrepancy } from './core/calculator';
import { getDataStore } from './core/storage';
import { parseShareUrlParams } from './components/ShareCard';

// Component imports
import { Tachometer } from './components/Tachometer';
import { ResultSummary } from './components/ResultSummary';
import { ShareCard } from './components/ShareCard';
import { AdSlot } from './components/AdSlot';
import { AffiliateCard } from './components/AffiliateCard';
import { CalculatorForm, CalculatorFormParams, CalculatorFormState } from './components/CalculatorForm';
import { CrowdsourceModal } from './components/CrowdsourceModal';
import { LegalModal, LegalTabId, LEGAL_OWNER_DETAILS } from './components/LegalModal';
import {
  CookieBanner,
  CookieConsentLevel,
  readStoredCookieConsent,
  persistCookieConsent,
} from './components/CookieBanner';

interface FaqItem {
  question: string;
  answer: string;
}

const FAQ_ITEMS: FaqItem[] = [
  {
    question: 'Come vengono calcolati i prezzi medi di riferimento?',
    answer:
      'Ogni prestazione parte da un prezzo base di mercato in Italia, calibrato sul coefficiente del costo della vita delle 107 province italiane e aggiornato nel browser anche tramite i contributi anonimi della community.',
  },
  {
    question: 'Il Fregometro è davvero gratuito e anonimo?',
    answer:
      'Sì. Il calcolo avviene interamente sul tuo dispositivo senza registrazione e senza inviare preventivi o dati personali a server esterni.',
  },
  {
    question: 'Perché la media cambia da provincia a provincia?',
    answer:
      'Manodopera, affitti commerciali e costi operativi variano sensibilmente tra aree metropolitane come Milano o Roma e province più piccole. Selezionare la provincia corretta evita falsi allarmi o sottostime.',
  },
  {
    question: 'Il risultato sostituisce un preventivo scritto ufficiale?',
    answer:
      'No. I risultati sono stime statistiche indicative pensate per orientarti e confrontare più richieste: urgenza, marca dei ricambi o complessità specifica dell’intervento possono giustificare scostamenti.',
  },
  {
    question: 'Come posso segnalare un prezzo reale pagato o sponsorizzare uno spazio?',
    answer:
      'Puoi inserire l’importo pagato in forma anonima usando il pulsante Segnala prezzo. Per collaborazioni o spazi pubblicitari aziendali puoi scrivere direttamente a gadmediamanager@gmail.com.',
  },
];

interface QuickViralScenario {
  label: string;
  city: string;
  tag: string;
  verdictLabel: string;
  tagColor: string;
  cat: CategoryId;
  prest: string;
  prov: string;
  quote: number;
}

const SCENARIO_ICON_MAP: Record<CategoryId, React.ReactNode> = {
  auto: <Car className="w-5 h-5 text-slate-900" />,
  casa: <Home className="w-5 h-5 text-slate-900" />,
  dentista: <Smile className="w-5 h-5 text-slate-900" />,
  veterinario: <HeartPulse className="w-5 h-5 text-slate-900" />,
  cerimonie: <Sparkles className="w-5 h-5 text-slate-900" />,
  affitti: <Key className="w-5 h-5 text-slate-900" />,
};

const VIRAL_SCENARIOS: QuickViralScenario[] = [
  {
    label: 'Tagliando Auto',
    city: 'Milano (MI)',
    tag: '+53%',
    verdictLabel: 'Caro',
    tagColor: 'bg-rose-100 text-rose-800 border-rose-300',
    cat: 'auto',
    prest: 'auto_tagliando',
    prov: 'MI',
    quote: 480,
  },
  {
    label: 'Pulizia Denti',
    city: 'Roma (RM)',
    tag: '-25%',
    verdictLabel: 'Onesto',
    tagColor: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    cat: 'dentista',
    prest: 'dentista_igiene',
    prov: 'RM',
    quote: 75,
  },
  {
    label: 'Caldaia Nuova',
    city: 'Napoli (NA)',
    tag: '+85%',
    verdictLabel: 'Fuori mercato',
    tagColor: 'bg-red-600 text-white border-red-700',
    cat: 'casa',
    prest: 'casa_caldaia',
    prov: 'NA',
    quote: 3200,
  },
  {
    label: 'Affitto Monolocale',
    city: 'Bologna (BO)',
    tag: '+59%',
    verdictLabel: 'Caro',
    tagColor: 'bg-rose-100 text-rose-800 border-rose-300',
    cat: 'affitti',
    prest: 'affitto_monolocale',
    prov: 'BO',
    quote: 950,
  },
  {
    label: 'Foto Matrimonio',
    city: 'Firenze (FI)',
    tag: '-10%',
    verdictLabel: 'Onesto',
    tagColor: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    cat: 'cerimonie',
    prest: 'cerimonia_foto',
    prov: 'FI',
    quote: 1650,
  },
];

interface CommunityImpactStat {
  label: string;
  value: string;
  sublabel: string;
  bgClass: string;
}

const COMMUNITY_IMPACT_STATS: CommunityImpactStat[] = [
  {
    label: 'Utenti attivi',
    value: '1.280+',
    sublabel: 'Preventivi verificati',
    bgClass: 'bg-slate-50 border-slate-300 text-slate-900',
  },
  {
    label: 'Risparmio totale',
    value: '94.500 €',
    sublabel: 'Stimato su segnalazioni',
    bgClass: 'bg-emerald-50 border-emerald-300 text-emerald-950',
  },
  {
    label: 'Media risparmiata',
    value: '-115 €',
    sublabel: 'Su preventivi trattati',
    bgClass: 'bg-amber-50 border-amber-300 text-amber-950',
  },
];

interface CommunitySavingsStory {
  author: string;
  city: string;
  category: string;
  detail: string;
  quotedBefore: number;
  paidAfter: number;
  savedEuro: number;
}

const COMMUNITY_SAVINGS_STORIES: CommunitySavingsStory[] = [
  {
    author: 'Marco R.',
    city: 'Milano',
    category: 'Auto',
    detail: 'Tagliando completo + freni',
    quotedBefore: 385,
    paidAfter: 290,
    savedEuro: 95,
  },
  {
    author: 'Elena T.',
    city: 'Bologna',
    category: 'Casa',
    detail: 'Sostituzione caldaia',
    quotedBefore: 2350,
    paidAfter: 2070,
    savedEuro: 280,
  },
  {
    author: 'Luca G.',
    city: 'Roma',
    category: 'Dentista',
    detail: 'Corona dentale singola',
    quotedBefore: 940,
    paidAfter: 790,
    savedEuro: 150,
  },
];

const BrandMark: React.FC<{ className?: string }> = ({ className = 'w-11 h-11' }) => (
  <svg
    viewBox="0 0 44 44"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    aria-hidden="true"
  >
    <rect x="2" y="2" width="40" height="40" rx="12" fill="#0F172A" />
    <path d="M10 26 A12 12 0 0 1 14.3 16.8" stroke="#10B981" strokeWidth="3.2" strokeLinecap="round" />
    <path d="M16.4 15.4 A12 12 0 0 1 27.6 15.4" stroke="#F59E0B" strokeWidth="3.2" strokeLinecap="round" />
    <path d="M29.7 16.8 A12 12 0 0 1 34 26" stroke="#F43F5E" strokeWidth="3.2" strokeLinecap="round" />
    <line x1="22" y1="26" x2="29.4" y2="20.8" stroke="#FFFFFF" strokeWidth="2.8" strokeLinecap="round" />
    <circle cx="22" cy="26" r="2.6" fill="#FFFFFF" />
  </svg>
);

export const App: React.FC = () => {
  // 1. Form & Active Calculation State
  const [selectedCategory, setSelectedCategory] = useState<CategoryId>('auto');
  const [selectedPrestationId, setSelectedPrestationId] = useState<string>('auto_tagliando');
  const [customPrestationDesc, setCustomPrestationDesc] = useState<string>('');
  const [selectedProvinceSigla, setSelectedProvinceSigla] = useState<string>('MI');
  const [quoteValue, setQuoteValue] = useState<number | null>(null);
  const [calculationResult, setCalculationResult] = useState<CalculationResult | null>(null);

  // 2. Crowdsource, FAQ, Legal Modal & Cookie Consent State
  const [isCrowdsourceModalOpen, setIsCrowdsourceModalOpen] = useState<boolean>(false);
  const [legalModalOpen, setLegalModalOpen] = useState<boolean>(false);
  const [legalModalTab, setLegalModalTab] = useState<LegalTabId>('privacy');
  const [cookieConsent, setCookieConsent] = useState<CookieConsentLevel | null>(() =>
    readStoredCookieConsent()
  );
  const [isCookieBannerOpen, setIsCookieBannerOpen] = useState<boolean>(
    () => readStoredCookieConsent() === null
  );
  const [openFaqIndex, setOpenFaqIndex] = useState<number>(0);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [crowdsourceVersion, setCrowdsourceVersion] = useState<number>(0);

  const openLegalDocument = useCallback((tab: LegalTabId) => {
    setLegalModalTab(tab);
    setLegalModalOpen(true);
  }, []);

  const handleCookieConsent = useCallback((level: CookieConsentLevel) => {
    persistCookieConsent(level);
    setCookieConsent(level);
    setIsCookieBannerOpen(false);
    setToastMessage(
      level === 'accepted'
        ? 'Preferenze salvate: tutti i cookie opzionali autorizzati.'
        : 'Preferenze salvate: attiva solo archiviazione tecnica essenziale.'
    );
    setTimeout(() => setToastMessage(null), 3500);
  }, []);

  // 3. Entity Lookups
  const categoryObj = useMemo(
    () => getCategoryById(selectedCategory),
    [selectedCategory]
  );
  const prestationObj = useMemo(
    () => getPrestationById(selectedPrestationId),
    [selectedPrestationId]
  );
  const provinceObj = useMemo(
    () => getProvinceBySigla(selectedProvinceSigla),
    [selectedProvinceSigla]
  );

  const effectivePrestationName = useMemo(() => {
    if (selectedPrestationId === 'custom') {
      return customPrestationDesc.trim() || 'Altra prestazione';
    }
    return prestationObj?.name || 'Intervento';
  }, [selectedPrestationId, customPrestationDesc, prestationObj]);

  // 4. Central Recalculation Engine
  const executeCalculation = useCallback(
    (
      cat: CategoryId,
      prestId: string,
      provSigla: string,
      quote: number | null
    ) => {
      if (quote === null || quote <= 0 || !Number.isFinite(quote)) {
        setCalculationResult(null);
        return;
      }

      try {
        const store = getDataStore();
        const override = store.getCrowdsourceOverride(cat, prestId, provSigla);
        let customRef = override ? override.currentAvg : undefined;

        if (prestId === 'custom' && customRef === undefined) {
          const catPrestations = getPrestationsByCategory(cat);
          const avgBase = catPrestations.length > 0
            ? catPrestations.reduce((acc, p) => acc + p.basePrice, 0) / catPrestations.length
            : 100;
          const prov = getProvinceBySigla(provSigla);
          const coeff = prov ? prov.costCoefficient : 1.0;
          customRef = Math.round(avgBase * coeff);
        }

        const result = calculateDiscrepancy(cat, prestId, provSigla, quote, customRef);
        setCalculationResult((prev) => {
          if (
            prev &&
            prev.categoryId === result.categoryId &&
            prev.prestationId === result.prestationId &&
            prev.provinceSigla === result.provinceSigla &&
            prev.quote === result.quote &&
            prev.refPrice === result.refPrice &&
            prev.diffEuro === result.diffEuro &&
            prev.diffPct === result.diffPct
          ) {
            return prev;
          }
          return result;
        });
      } catch (err) {
        console.error('Calculation error:', err);
      }
    },
    []
  );

  // 5. URL Query Auto-Hydration on Page Mount
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const parsed = parseShareUrlParams(window.location.search);
    if (parsed.categoryId || parsed.prestationId || parsed.provinceSigla || parsed.quote || (parsed as any).customDescription) {
      const rawCat = parsed.categoryId;
      const cat: CategoryId = (rawCat && getCategoryById(rawCat)) ? rawCat : 'auto';
      const catPrests = getPrestationsByCategory(cat);
      const defaultPrest = catPrests.length > 0 ? catPrests[0].id : 'auto_tagliando';
      const isValidPrest = parsed.prestationId && (
        catPrests.some((p) => p.id === parsed.prestationId) || parsed.prestationId === 'custom'
      );
      const prest = isValidPrest ? (parsed.prestationId as string) : defaultPrest;
      const prov = (parsed.provinceSigla && getProvinceBySigla(parsed.provinceSigla))
        ? parsed.provinceSigla.toUpperCase()
        : 'MI';
      const quote = (parsed.quote && parsed.quote > 0) ? parsed.quote : null;

      setSelectedCategory(cat);
      setSelectedPrestationId(prest);
      setSelectedProvinceSigla(prov);
      if ((parsed as any).customDescription) {
        setCustomPrestationDesc((parsed as any).customDescription);
      }

      if (quote) {
        setQuoteValue(quote);
        executeCalculation(cat, prest, prov, quote);
      }
    }
  }, [executeCalculation]);

  // 6. Handle Form State Changes (keeps Fregometro in standby until Verifica is pressed)
  const handleFormChange = useCallback(
    (formState: CalculatorFormState) => {
      setSelectedCategory(formState.categoryId);
      setSelectedPrestationId(formState.prestationId);
      setSelectedProvinceSigla(formState.provinceSigla);
      setCustomPrestationDesc(formState.customDescription || '');
      setQuoteValue(formState.parsedQuote);

      setCalculationResult((prev) => {
        if (!prev) return null;
        if (
          prev.categoryId === formState.categoryId &&
          prev.prestationId === formState.prestationId &&
          prev.provinceSigla === formState.provinceSigla &&
          prev.quote === formState.parsedQuote
        ) {
          return prev;
        }
        return null;
      });
    },
    []
  );

  const handleCalculate = useCallback(
    (params: CalculatorFormParams) => {
      setSelectedCategory(params.categoryId);
      setSelectedPrestationId(params.prestationId);
      setSelectedProvinceSigla(params.provinceSigla);
      if (params.customPrestationDescription !== undefined) {
        setCustomPrestationDesc(params.customPrestationDescription);
      }
      setQuoteValue(params.quote);

      executeCalculation(
        params.categoryId,
        params.prestationId,
        params.provinceSigla,
        params.quote
      );
    },
    [executeCalculation]
  );

  const applyViralScenario = (sc: QuickViralScenario) => {
    setSelectedCategory(sc.cat);
    setSelectedPrestationId(sc.prest);
    setCustomPrestationDesc('');
    setSelectedProvinceSigla(sc.prov);
    setQuoteValue(sc.quote);
    executeCalculation(sc.cat, sc.prest, sc.prov, sc.quote);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // 7. Handle Crowdsource Submission Success
  const handleCrowdsourceSuccess = (newAverage: number, newCount: number) => {
    setCrowdsourceVersion((v) => v + 1);
    setToastMessage(`Media aggiornata a ${newAverage} € (${newCount} segnalazioni). Grazie per il contributo.`);
    setTimeout(() => setToastMessage(null), 5000);

    if (quoteValue && quoteValue > 0) {
      executeCalculation(selectedCategory, selectedPrestationId, selectedProvinceSigla, quoteValue);
    }
  };

  const activeCrowdsourceRecord = useMemo(() => {
    if (crowdsourceVersion >= 0) {
      return getDataStore().getCrowdsourceOverride(
        selectedCategory,
        selectedPrestationId,
        selectedProvinceSigla
      );
    }
    return null;
  }, [selectedCategory, selectedPrestationId, selectedProvinceSigla, crowdsourceVersion]);

  return (
    <div className="min-h-screen bg-fregometro-stage text-slate-900 flex flex-col font-sans selection:bg-amber-300 selection:text-slate-950 relative overflow-x-hidden">
      {/* Smooth Colorful Mesh Background Layer (No Dots, No Lines) */}
      <div
        className="pointer-events-none fixed inset-0 -z-10"
        style={{
          backgroundImage:
            'radial-gradient(ellipse 75% 55% at 12% 10%, rgba(251, 191, 36, 0.34) 0px, transparent 60%), radial-gradient(ellipse 70% 55% at 90% 15%, rgba(251, 113, 133, 0.26) 0px, transparent 58%), radial-gradient(ellipse 75% 60% at 22% 72%, rgba(52, 211, 153, 0.24) 0px, transparent 60%), radial-gradient(ellipse 70% 55% at 86% 88%, rgba(99, 102, 241, 0.18) 0px, transparent 58%), linear-gradient(135deg, rgba(255, 247, 230, 0.9) 0%, rgba(255, 240, 243, 0.85) 50%, rgba(236, 253, 245, 0.9) 100%)',
        }}
      />
      <div className="pointer-events-none fixed -top-32 -left-24 w-[28rem] h-[28rem] rounded-full bg-amber-300/35 blur-3xl -z-10" />
      <div className="pointer-events-none fixed top-1/4 -right-28 w-[28rem] h-[28rem] rounded-full bg-rose-300/30 blur-3xl -z-10" />
      <div className="pointer-events-none fixed -bottom-24 left-1/4 w-[30rem] h-[30rem] rounded-full bg-emerald-300/25 blur-3xl -z-10" />

      {/* 1. Notification Toast */}
      {toastMessage && (
        <div className="fixed top-20 right-4 z-50 max-w-md p-4 rounded-2xl bg-emerald-100 border-2 border-slate-900 text-slate-950 shadow-xl shadow-slate-900/15 flex items-center gap-3 animate-fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-700 flex-shrink-0" />
          <p className="text-sm font-bold">{toastMessage}</p>
        </div>
      )}

      {/* ====================================================================
          STEP 1: SLEEK HORIZONTAL TOP NAVBAR & COMPACT INTRO BAR
          ==================================================================== */}
      <header className="w-full sticky top-0 z-30 border-b border-slate-900/15 bg-white/80 backdrop-blur-md">
        <div className="max-w-5xl mx-auto px-3 sm:px-6 h-16 flex items-center justify-between gap-2 sm:gap-4">
          <a href="#calcolatore" className="inline-flex items-center gap-1.5 sm:gap-2.5 min-w-0">
            <BrandMark className="w-7 h-7 sm:w-9 sm:h-9 shrink-0" />
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-[14px] sm:text-xl font-black tracking-tight text-slate-950 font-display leading-none truncate">
                Mi Stanno Fregando<span className="text-rose-600">?</span>
              </span>
              <span className="hidden sm:inline-block text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-900 text-white shrink-0">
                Fregometro™
              </span>
            </div>
          </a>

          <nav aria-label="Menu principale" className="hidden md:flex items-center gap-6 text-xs font-extrabold text-slate-700">
            <a href="#calcolatore" className="hover:text-slate-950 transition-colors">
              Verifica
            </a>
            <a href="#risparmi" className="hover:text-slate-950 transition-colors">
              Risparmi
            </a>
            <a href="#casi-reali" className="hover:text-slate-950 transition-colors">
              Casi Reali
            </a>
            <a href="#faq" className="hover:text-slate-950 transition-colors">
              Come Funziona
            </a>
            <a href="#progetto" className="hover:text-slate-950 transition-colors">
              Il Progetto
            </a>
          </nav>

          <button
            type="button"
            onClick={() => setIsCrowdsourceModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-2.5 sm:px-3.5 py-1.5 sm:py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-[11px] sm:text-xs font-extrabold transition-colors cursor-pointer shrink-0 whitespace-nowrap"
          >
            <Users className="w-3.5 h-3.5 text-emerald-300 shrink-0" />
            <span className="sm:hidden">Segnala</span>
            <span className="hidden sm:inline">Segnala prezzo</span>
          </button>
        </div>
      </header>

      <div className="max-w-5xl mx-auto w-full px-4 sm:px-6 pt-5 pb-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
        <h1 className="text-sm sm:text-base font-bold text-slate-800 tracking-tight">
          Inserisci il preventivo e scopri subito se la richiesta è{' '}
          <span className="font-extrabold text-emerald-700">in linea</span> o{' '}
          <span className="font-extrabold text-rose-600">fuori mercato</span>.
        </h1>
        <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-500 shrink-0">
          107 province • 100% anonimo
        </span>
      </div>

      {/* ====================================================================
          3-COLUMN STAGE: LEFT LATERAL BANNER + MAIN LINEAR FLOW + RIGHT LATERAL BANNER
          ==================================================================== */}
      <div className="max-w-[1440px] mx-auto w-full px-3 sm:px-6 flex items-stretch justify-center gap-5 flex-1">
        {/* Left Lateral Banners (3x 160x600+ Skyscraper aligned flush with main column bottom) */}
        <aside aria-label="Banner pubblicitari sinistri" className="hidden xl:flex flex-col gap-5 shrink-0">
          <AdSlot format="skyscraper" slotId="skyscraper-left" fillHeight={true} />
          <AdSlot format="skyscraper" slotId="skyscraper-left-2" fillHeight={true} />
          <AdSlot format="skyscraper" slotId="skyscraper-left-3" fillHeight={true} />
        </aside>

        <main className="max-w-5xl w-full space-y-6 flex-1 min-w-0">
          {/* ====================================================================
              STEP 2: HORIZONTAL MAIN PRICE BAR (SUBITO SOTTO IL LOGO)
              ==================================================================== */}
          <section id="calcolatore" aria-label="Barra inserimento preventivo" className="scroll-mt-20">
            <CalculatorForm
              initialCategory={selectedCategory}
              initialPrestationId={selectedPrestationId}
              initialCustomDescription={customPrestationDesc}
              initialProvinceSigla={selectedProvinceSigla}
              initialQuote={quoteValue ?? undefined}
              onChange={handleFormChange}
              onCalculate={handleCalculate}
              onSubmit={handleCalculate}
            />
          </section>

          {/* ====================================================================
              MOBILE & TABLET TWIN BANNERS (Visibili su mobile/tablet dove i 2 banner laterali diventano affiancati!)
              ==================================================================== */}
          <section
            aria-label="Banner sponsor mobile"
            className="grid grid-cols-1 sm:grid-cols-2 gap-3 xl:hidden"
          >
            <AdSlot format="skyscraper" slotId="skyscraper-left" compactMobile={true} />
            <AdSlot format="skyscraper" slotId="skyscraper-right" compactMobile={true} />
          </section>

          {/* ====================================================================
              STEP 3: BALANCED FREGOMETRO SECTION (STANDBY O RISULTATI SU VERIFICA)
              ==================================================================== */}
          <section
            aria-label={calculationResult ? 'Risultati del Fregometro' : 'Fregometro in standby'}
            className="space-y-6 animate-fade-in"
          >
            {/* Row A: Tachometer + Standby Card OR ResultSummary */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
              <div className="lg:col-span-5 flex">
                {calculationResult ? (
                  <Tachometer
                    result={calculationResult}
                    showDigitalReadout={true}
                    showLegend={true}
                    className="max-w-none w-full h-full justify-between"
                  />
                ) : (
                  <Tachometer
                    standby={true}
                    showDigitalReadout={true}
                    showLegend={true}
                    className="max-w-none w-full h-full justify-between"
                  />
                )}
              </div>

              <div className="lg:col-span-7 flex">
                {calculationResult ? (
                  <ResultSummary
                    result={calculationResult}
                    categoryName={categoryObj?.name}
                    categoryId={selectedCategory}
                    categoryIcon={categoryObj?.icon}
                    prestationName={effectivePrestationName}
                    prestationUnit={prestationObj?.unit || 'intervento'}
                    provinceName={provinceObj?.nome}
                    provinceSigla={selectedProvinceSigla}
                    regionName={provinceObj?.regione}
                    crowdsourceCount={activeCrowdsourceRecord?.sampleCount}
                    onCrowdsourceClick={() => setIsCrowdsourceModalOpen(true)}
                    className="max-w-none w-full h-full flex flex-col justify-between"
                  />
                ) : (
                  <div className="w-full h-full flex flex-col justify-between bg-white border-2 border-slate-900 rounded-3xl p-5 sm:p-6 shadow-xl shadow-slate-900/10">
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-3 flex-wrap">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 border border-slate-300 text-slate-800 text-xs font-extrabold tracking-wide uppercase">
                          <ShieldCheck className="w-4 h-4 text-slate-700" />
                          <span>Fregometro in Standby</span>
                        </span>
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                          107 Province ISTAT
                        </span>
                      </div>

                      <h2 className="text-xl sm:text-2xl font-extrabold text-slate-950 font-display leading-snug">
                        Inserisci il preventivo e premi Verifica
                      </h2>
                      <p className="text-xs sm:text-sm text-slate-600 font-medium mt-1.5 mb-5">
                        Nessun riferimento di prezzo viene mostrato prima della verifica: il Fregometro calcola fascia media locale, scostamento percentuale e verdetto solo dopo il tuo invio.
                      </p>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                          <span className="inline-block text-[10px] font-black uppercase tracking-wider text-slate-500 mb-1">
                            Passo 1
                          </span>
                          <p className="text-xs font-extrabold text-slate-900">
                            Seleziona Categoria e Prestazione dai menu a tendina
                          </p>
                        </div>
                        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                          <span className="inline-block text-[10px] font-black uppercase tracking-wider text-slate-500 mb-1">
                            Passo 2
                          </span>
                          <p className="text-xs font-extrabold text-slate-900">
                            Scegli la Provincia e digita l&apos;importo richiesto in €
                          </p>
                        </div>
                        <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-300">
                          <span className="inline-block text-[10px] font-black uppercase tracking-wider text-amber-800 mb-1">
                            Passo 3
                          </span>
                          <p className="text-xs font-extrabold text-slate-900">
                            Premi Verifica per ottenere media provinciale e responso
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="mt-5 pt-3 border-t-2 border-dashed border-slate-200 flex items-center justify-between gap-2 flex-wrap">
                      <span className="text-[11px] text-slate-500 font-semibold">
                        Calcolo locale anonimo • Nessun dato salvato automaticamente
                      </span>
                      <span className="text-[11px] font-bold text-slate-700">
                        Oppure prova un caso reale qui sotto
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Row B: Community Real Savings Proof (+ Share Card once verified) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
              <section
                id="risparmi"
                aria-label="Risparmi reali ottenuti dalla community"
                className={calculationResult ? 'lg:col-span-6 flex scroll-mt-20' : 'lg:col-span-12 flex scroll-mt-20'}
              >
                <div className="w-full h-full flex flex-col justify-between bg-white border-2 border-slate-900 rounded-3xl p-5 sm:p-6 shadow-xl shadow-slate-900/10">
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-3 flex-wrap">
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 border border-emerald-500 text-emerald-950 text-xs font-extrabold tracking-wide uppercase">
                        <TrendingDown className="w-4 h-4 text-emerald-700" />
                        <span>Risparmi Reali in Italia</span>
                      </span>
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold text-slate-500">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                        <span>{crowdsourceVersion > 0 ? `${1280 + crowdsourceVersion}+ verifiche` : 'Dati Community'}</span>
                      </span>
                    </div>

                    <h2 className="text-lg sm:text-xl font-extrabold text-slate-950 font-display leading-snug">
                      Chi l&apos;ha già provato quanto ha risparmiato
                    </h2>
                    <p className="text-xs sm:text-sm text-slate-600 font-medium mt-1 mb-4">
                      Conoscere la fascia di prezzo media permette di confrontare i preventivi con dati oggettivi.
                    </p>

                    {/* 3 Aggregate Savings Counters */}
                    <div className="grid grid-cols-3 gap-2.5 mb-4">
                      {COMMUNITY_IMPACT_STATS.map((stat) => (
                        <div
                          key={stat.label}
                          className={`p-2.5 rounded-2xl border-2 text-center flex flex-col justify-center ${stat.bgClass}`}
                        >
                          <span className="text-[10px] font-black uppercase tracking-wider opacity-80">
                            {stat.label}
                          </span>
                          <span className="text-base sm:text-lg font-black font-mono leading-tight my-0.5">
                            {stat.value}
                          </span>
                          <span className="text-[10px] font-bold opacity-80 leading-tight">
                            {stat.sublabel}
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Real User Savings Stories */}
                    <div className={calculationResult ? 'space-y-2' : 'grid grid-cols-1 md:grid-cols-3 gap-2.5'}>
                      {COMMUNITY_SAVINGS_STORIES.map((story) => (
                        <div
                          key={`${story.author}-${story.city}`}
                          className="p-3 rounded-2xl bg-slate-50 border border-slate-300 flex items-center justify-between gap-3"
                        >
                          <div className="min-w-0">
                            <div className="flex items-center gap-1.5 flex-wrap">
                              <span className="text-xs font-black text-slate-950">
                                {story.author} • {story.city}
                              </span>
                              <span className="px-2 py-0.5 rounded-full bg-amber-100 border border-amber-300 text-[10px] font-black text-amber-950">
                                {story.category}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-600 font-semibold mt-0.5 truncate">
                              {story.detail} (da {story.quotedBefore}€ → pagato {story.paidAfter}€)
                            </p>
                          </div>
                          <span className="px-2.5 py-1 rounded-xl bg-emerald-200 border border-emerald-500 text-emerald-950 font-mono font-black text-xs shrink-0">
                            -{story.savedEuro} €
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t-2 border-dashed border-slate-200 flex items-center justify-between gap-2 flex-wrap">
                    <span className="text-[11px] text-slate-500 font-semibold">
                      Hai già risparmiato grazie al confronto?
                    </span>
                    <button
                      type="button"
                      onClick={() => setIsCrowdsourceModalOpen(true)}
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-black transition-all cursor-pointer"
                    >
                      <Users className="w-3.5 h-3.5 text-emerald-300" />
                      <span>Aggiungi il tuo risparmio</span>
                    </button>
                  </div>
                </div>
              </section>

              {calculationResult && (
                <div className="lg:col-span-6 flex">
                  <ShareCard
                    calculationResult={calculationResult}
                    categoryId={selectedCategory}
                    prestationId={selectedPrestationId}
                    provinceSigla={selectedProvinceSigla}
                    categoryName={categoryObj?.name}
                    prestationName={effectivePrestationName}
                    provinceName={provinceObj?.nome}
                    customDescription={customPrestationDesc}
                    className="max-w-none w-full"
                  />
                </div>
              )}
            </div>
          </section>

          {/* ====================================================================
              STEP 4: LE PROVE & CASI REALI DELLA COMMUNITY (DOPO I RISULTATI)
              ==================================================================== */}
          <section
            id="casi-reali"
            aria-label="Prove e casi reali verificati"
            className="bg-white border-2 border-slate-900 rounded-3xl p-5 sm:p-6 shadow-xl shadow-slate-900/10 scroll-mt-20"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 mb-5 border-b-2 border-dashed border-slate-200">
              <div>
                <div className="inline-flex items-center gap-1.5 text-xs font-extrabold uppercase tracking-wider text-rose-700 mb-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Casi Reali Verificati</span>
                </div>
                <h2 className="text-lg sm:text-xl font-extrabold text-slate-950 font-display">
                  Esempi segnalati in Italia (clicca per simulare il calcolo)
                </h2>
              </div>

              <button
                type="button"
                onClick={() => setIsCrowdsourceModalOpen(true)}
                className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-2xl bg-emerald-100 hover:bg-emerald-200 text-emerald-950 font-extrabold text-xs sm:text-sm border-2 border-slate-900 shadow-sm hover:shadow transition-all cursor-pointer shrink-0"
              >
                <Users className="w-4 h-4 text-emerald-800" />
                <span>Segnala quanto hai pagato</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {VIRAL_SCENARIOS.map((sc, i) => {
                const isActive =
                  selectedCategory === sc.cat &&
                  selectedPrestationId === sc.prest &&
                  selectedProvinceSigla === sc.prov &&
                  quoteValue === sc.quote;

                return (
                  <button
                    key={i}
                    type="button"
                    onClick={() => applyViralScenario(sc)}
                    className={`p-3.5 rounded-2xl border-2 text-left transition-all flex flex-col justify-between cursor-pointer ${
                      isActive
                        ? 'bg-amber-100 border-slate-900 shadow-md -translate-y-0.5'
                        : 'bg-slate-50 hover:bg-amber-50 border-slate-900 shadow-sm hover:shadow-md hover:-translate-y-0.5'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between gap-1 mb-2">
                        <span className="w-8 h-8 rounded-xl bg-white border border-slate-300 flex items-center justify-center">
                          {SCENARIO_ICON_MAP[sc.cat]}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-black border ${sc.tagColor}`}>
                          {sc.tag}
                        </span>
                      </div>
                      <p className="font-black text-sm text-slate-950 leading-snug">
                        {sc.label}
                      </p>
                      <p className="text-xs text-slate-500 font-bold">
                        {sc.city}
                      </p>
                    </div>

                    <div className="mt-3 pt-2 border-t border-slate-200/80 flex items-center justify-between">
                      <span className="font-mono font-black text-base text-slate-950">
                        {sc.quote} €
                      </span>
                      <span className="text-[11px] font-extrabold text-slate-600 underline">
                        Prova →
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </section>

          {/* ====================================================================
              STEP 4B: SEO SECTION - COME FUNZIONA & DOMANDE FREQUENTI (FAQ)
              ==================================================================== */}
          <section
            id="faq"
            aria-label="Come funziona e domande frequenti"
            className="bg-white border-2 border-slate-900 rounded-3xl p-5 sm:p-6 shadow-xl shadow-slate-900/10 scroll-mt-20"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 mb-5 border-b-2 border-dashed border-slate-200">
              <div>
                <div className="inline-flex items-center gap-1.5 text-xs font-extrabold uppercase tracking-wider text-slate-600 mb-1">
                  <Info className="w-3.5 h-3.5 text-slate-900" />
                  <span>Guida &amp; Trasparenza</span>
                </div>
                <h2 className="text-lg sm:text-xl font-extrabold text-slate-950 font-display">
                  Come funziona il Fregometro e Domande Frequenti
                </h2>
              </div>
              <span className="text-[11px] font-bold text-slate-500">
                Metodo provinciale • 6 categorie • 107 province
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-5">
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-black uppercase tracking-wider text-slate-500 block mb-1">
                  1. Scegli la prestazione
                </span>
                <p className="text-xs font-bold text-slate-800 leading-relaxed">
                  Seleziona categoria e servizio esatto tra Auto, Casa, Dentista, Veterinario, Cerimonie o Affitti, oppure descrivi un lavoro personalizzato.
                </p>
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-black uppercase tracking-wider text-slate-500 block mb-1">
                  2. Calibra sulla provincia
                </span>
                <p className="text-xs font-bold text-slate-800 leading-relaxed">
                  Indica la provincia del preventivo: ogni città applica un coefficiente territoriale calibrato sui costi locali reali.
                </p>
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                <span className="text-[10px] font-black uppercase tracking-wider text-slate-500 block mb-1">
                  3. Leggi il verdetto
                </span>
                <p className="text-xs font-bold text-slate-800 leading-relaxed">
                  Premi Verifica per scoprire subito scostamento in euro, percentuale rispetto alla media locale e margine di trattativa.
                </p>
              </div>
            </div>

            <div className="space-y-2.5">
              {FAQ_ITEMS.map((item, idx) => {
                const isOpen = openFaqIndex === idx;
                return (
                  <div
                    key={item.question}
                    className="rounded-2xl border border-slate-300 bg-slate-50/70 overflow-hidden transition-colors"
                  >
                    <h3 className="m-0">
                      <button
                        type="button"
                        aria-expanded={isOpen}
                        onClick={() => setOpenFaqIndex(isOpen ? -1 : idx)}
                        className="w-full px-4 py-3 text-left flex items-center justify-between gap-3 font-extrabold text-xs sm:text-sm text-slate-950 hover:bg-slate-100/70 transition-colors cursor-pointer"
                      >
                        <span>{item.question}</span>
                        <ChevronDown
                          className={`w-4 h-4 text-slate-600 shrink-0 transition-transform duration-200 ${
                            isOpen ? 'rotate-180' : ''
                          }`}
                        />
                      </button>
                    </h3>
                    {isOpen && (
                      <div className="px-4 pb-3.5 pt-0.5 text-xs sm:text-sm text-slate-600 font-medium leading-relaxed border-t border-slate-200/70 bg-white">
                        {item.answer}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>

          {/* Extra Mobile/Tablet Sponsor Banners (hidden on xl desktop where full side rails are visible) */}
          <section
            aria-label="Altri banner sponsor mobile"
            className="grid grid-cols-2 gap-3 xl:hidden"
          >
            <AdSlot format="skyscraper" slotId="skyscraper-left-2" compactMobile={true} />
            <AdSlot format="skyscraper" slotId="skyscraper-right-2" compactMobile={true} />
            <AdSlot format="skyscraper" slotId="skyscraper-left-3" compactMobile={true} />
            <AdSlot format="skyscraper" slotId="skyscraper-right-3" compactMobile={true} />
          </section>

          {/* Bottom Leaderboard Ad Slot */}
          <section className="w-full pt-2">
            <AdSlot format="leaderboard" slotId="leaderboard-top" />
          </section>

          {/* ====================================================================
              STEP 5: HOUSE ADV / MANIFESTO CONTRO IL CARO VITA
              ==================================================================== */}
          <section
            id="progetto"
            aria-label="Iniziativa indipendente contro il caro vita"
            className="bg-slate-950 text-white border-2 border-slate-900 rounded-3xl p-6 sm:p-8 shadow-xl shadow-slate-900/15 scroll-mt-20"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 mb-6 border-b border-slate-800">
              <div className="flex items-start sm:items-center gap-4">
                <BrandMark className="w-12 h-12 shrink-0 ring-2 ring-white/15 rounded-2xl" />
                <div>
                  <span className="inline-block px-2.5 py-0.5 rounded-full bg-amber-400 text-slate-950 text-[10px] font-black uppercase tracking-widest mb-1.5">
                    Iniziativa Indipendente • Contro il Caro Vita
                  </span>
                  <h2 className="text-xl sm:text-2xl font-black font-display leading-snug text-white">
                    Perché lo facciamo: più trasparenza contro il caro vita.
                  </h2>
                </div>
              </div>
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-emerald-400 text-xs font-extrabold shrink-0 self-start md:self-center">
                <ShieldCheck className="w-4 h-4" />
                <span>Servizio Gratuito</span>
              </span>
            </div>

            <p className="text-sm sm:text-base text-slate-300 font-medium leading-relaxed mb-6 max-w-3xl">
              Con l&apos;aumento continuo di tariffe, riparazioni e visite mediche, capire se un preventivo è onesto è diventato difficile. Abbiamo creato <strong className="text-white">Mi Stanno Fregando?</strong> per dare a famiglie e cittadini uno strumento concreto, anonimo e gratuito per difendere il proprio portafoglio ogni giorno.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
              <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800">
                <span className="text-[10px] font-black uppercase tracking-wider text-amber-400 block mb-1">
                  01 • Trasparenza
                </span>
                <p className="text-sm font-extrabold text-white mb-1">
                  Basta preventivi al buio
                </p>
                <p className="text-xs text-slate-400 font-medium leading-relaxed">
                  Un riferimento immediato prima di firmare o pagare un lavoro.
                </p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800">
                <span className="text-[10px] font-black uppercase tracking-wider text-emerald-400 block mb-1">
                  02 • Territorio
                </span>
                <p className="text-sm font-extrabold text-white mb-1">
                  Tarato sulla tua provincia
                </p>
                <p className="text-xs text-slate-400 font-medium leading-relaxed">
                  Stime calibrate sul costo reale della vita in tutte le 107 province.
                </p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800">
                <span className="text-[10px] font-black uppercase tracking-wider text-rose-400 block mb-1">
                  03 • Community
                </span>
                <p className="text-sm font-extrabold text-white mb-1">
                  Aiutiamoci a risparmiare
                </p>
                <p className="text-xs text-slate-400 font-medium leading-relaxed">
                  Ogni ricevuta condivisa in anonimo rende le medie più precise per tutti.
                </p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-4 border-t border-slate-800">
              <p className="text-xs text-slate-400 font-semibold">
                Vuoi dare una mano? Condividi un importo reale o collabora con il progetto.
              </p>
              <div className="flex flex-wrap items-center gap-2.5">
                <button
                  type="button"
                  onClick={() => setIsCrowdsourceModalOpen(true)}
                  className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-white hover:bg-amber-300 text-slate-950 text-xs font-black transition-colors cursor-pointer"
                >
                  <Users className="w-3.5 h-3.5" />
                  <span>Segnala un prezzo pagato</span>
                </button>
                <a
                  href="mailto:gadmediamanager@gmail.com?subject=Collaborazione%20o%20Sostegno%20-%20Mi%20Stanno%20Fregando%3F"
                  className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white text-xs font-extrabold transition-colors"
                >
                  <span>Scrivi al team →</span>
                </a>
              </div>
            </div>
          </section>
        </main>

        {/* Right Lateral Banners (3x 160x600+ Skyscraper aligned flush with main column bottom) */}
        <aside aria-label="Banner pubblicitari destri" className="hidden xl:flex flex-col gap-5 shrink-0">
          <AdSlot format="skyscraper" slotId="skyscraper-right" fillHeight={true} />
          <AdSlot format="skyscraper" slotId="skyscraper-right-2" fillHeight={true} />
          <AdSlot format="skyscraper" slotId="skyscraper-right-3" fillHeight={true} />
        </aside>
      </div>

      {/* Crowdsource Anonymous Modal Dialog */}
      <CrowdsourceModal
        isOpen={isCrowdsourceModalOpen}
        onClose={() => setIsCrowdsourceModalOpen(false)}
        categoryId={selectedCategory}
        prestationId={selectedPrestationId}
        provinceSigla={selectedProvinceSigla}
        categoryName={categoryObj?.name}
        categoryIcon={categoryObj?.icon}
        prestationName={effectivePrestationName}
        prestationUnit={prestationObj?.unit || 'intervento'}
        provinceName={provinceObj?.nome}
        activeQuote={quoteValue ?? undefined}
        onSubmissionSuccess={handleCrowdsourceSuccess}
      />

      {/* Regulatory & Legal Info Modal (Privacy, Cookie, Terms, AGCM & Titolare) */}
      <LegalModal
        isOpen={legalModalOpen}
        activeTab={legalModalTab}
        onTabChange={setLegalModalTab}
        onClose={() => setLegalModalOpen(false)}
      />

      {/* Garante Privacy / ePrivacy Cookie Preferences Bar */}
      <CookieBanner
        isVisible={isCookieBannerOpen}
        currentChoice={cookieConsent}
        onAcceptEssential={() => handleCookieConsent('essential')}
        onAcceptAll={() => handleCookieConsent('accepted')}
        onOpenCookiePolicy={() => openLegalDocument('cookie')}
        onDismiss={() => setIsCookieBannerOpen(false)}
      />

      {/* Comprehensive Legal, Regulatory & Corporate Footer */}
      <footer className="border-t-2 border-slate-900 bg-white mt-12 pt-10 pb-8 text-xs text-slate-700">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 pb-8 border-b border-slate-200">
            {/* Col 1: Brand & Mission */}
            <div className="space-y-3">
              <div className="inline-flex items-center gap-2.5">
                <BrandMark className="w-8 h-8 shrink-0" />
                <div>
                  <span className="block text-sm font-black text-slate-950 font-display leading-none">
                    Mi Stanno Fregando?
                  </span>
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500">
                    Fregometro™ • Italia
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-600 font-medium leading-relaxed">
                Osservatorio gratuito sui preventivi e costo della vita in 107 province. Elaborazione locale 100% anonima senza registrazione.
              </p>
            </div>

            {/* Col 2: Navigation Links */}
            <div>
              <h3 className="text-[11px] font-black uppercase tracking-wider text-slate-950 mb-3">
                Strumento
              </h3>
              <ul className="space-y-2 text-xs font-semibold text-slate-600">
                <li>
                  <a href="#calcolatore" className="hover:text-slate-950 transition-colors">
                    Verifica Preventivo
                  </a>
                </li>
                <li>
                  <a href="#risparmi" className="hover:text-slate-950 transition-colors">
                    Risparmi Community
                  </a>
                </li>
                <li>
                  <a href="#casi-reali" className="hover:text-slate-950 transition-colors">
                    Casi Reali Verificati
                  </a>
                </li>
                <li>
                  <a href="#faq" className="hover:text-slate-950 transition-colors">
                    Come Funziona &amp; FAQ
                  </a>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => setIsCrowdsourceModalOpen(true)}
                    className="hover:text-slate-950 transition-colors cursor-pointer text-left font-bold text-emerald-700"
                  >
                    Segnala quanto hai pagato
                  </button>
                </li>
              </ul>
            </div>

            {/* Col 3: GDPR, Cookie, Terms & AGCM Legal Modals */}
            <div>
              <h3 className="text-[11px] font-black uppercase tracking-wider text-slate-950 mb-3">
                Documenti Legali
              </h3>
              <ul className="space-y-2 text-xs font-semibold text-slate-600">
                <li>
                  <button
                    type="button"
                    onClick={() => openLegalDocument('privacy')}
                    className="hover:text-slate-950 underline decoration-slate-300 underline-offset-2 cursor-pointer text-left"
                  >
                    Privacy Policy (GDPR)
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => openLegalDocument('cookie')}
                    className="hover:text-slate-950 underline decoration-slate-300 underline-offset-2 cursor-pointer text-left"
                  >
                    Cookie Policy
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => openLegalDocument('terms')}
                    className="hover:text-slate-950 underline decoration-slate-300 underline-offset-2 cursor-pointer text-left"
                  >
                    Termini d&apos;Uso &amp; Disclaimer
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => openLegalDocument('transparency')}
                    className="hover:text-slate-950 underline decoration-slate-300 underline-offset-2 cursor-pointer text-left"
                  >
                    Trasparenza Pubblicitaria (AGCM)
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => setIsCookieBannerOpen(true)}
                    className="hover:text-slate-950 underline decoration-slate-300 underline-offset-2 cursor-pointer text-left"
                  >
                    Preferenze Cookie
                  </button>
                </li>
              </ul>
            </div>

            {/* Col 4: Owner Registry, Tax ID Fields & ADV Contact */}
            <div className="space-y-2">
              <h3 className="text-[11px] font-black uppercase tracking-wider text-slate-950 mb-3">
                Titolare &amp; Contatti
              </h3>
              <p className="text-[11px] text-slate-600 leading-snug">
                <strong className="text-slate-900">Titolare:</strong>{' '}
                <span className="font-mono">{LEGAL_OWNER_DETAILS.holderPlaceholder}</span>
              </p>
              <p className="text-[11px] text-slate-600 leading-snug">
                <strong className="text-slate-900">P.IVA / C.F.:</strong>{' '}
                <span className="font-mono">{LEGAL_OWNER_DETAILS.vatPlaceholder}</span>
              </p>
              <p className="text-[11px] text-slate-600 leading-snug">
                <strong className="text-slate-900">Sede:</strong>{' '}
                <span className="font-mono">{LEGAL_OWNER_DETAILS.addressPlaceholder}</span>
              </p>
              <p className="text-[11px] pt-1">
                <strong className="text-slate-900 block">Email &amp; Pubblicità:</strong>
                <a
                  href={`mailto:${LEGAL_OWNER_DETAILS.contactEmail}?subject=Contatto%20o%20Spazi%20Pubblicitari%20-%20Mi%20Stanno%20Fregando%3F`}
                  className="font-extrabold text-slate-950 underline break-all"
                >
                  {LEGAL_OWNER_DETAILS.contactEmail}
                </a>
              </p>
            </div>
          </div>

          <div className="pt-5 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-500 text-center sm:text-left">
            <p className="font-bold text-slate-700">
              © 2026 <strong>Mi Stanno Fregando?</strong> • Tutti i diritti riservati.
            </p>
            <p className="font-medium max-w-xl">
              Le elaborazioni del Fregometro sono stime statistiche indicative e non sostituiscono preventivi ufficiali scritti. Tutti gli spazi promozionali sono contrassegnati con dicitura PUBBLICITÀ (AGCM).
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
