/**
 * src/components/LegalModal.tsx
 * Accessible Legal & Regulatory Documentation Modal for "Mi Stanno Fregando?".
 *
 * Covers:
 * - Privacy Policy (GDPR Reg. UE 2016/679, localStorage-only client computation, gadmediamanager@gmail.com)
 * - Cookie Policy (Technical localStorage vs third-party/AdSense cookies notice)
 * - Terms of Use & Disclaimer (Indicative statistical estimates, no contractual liability)
 * - Advertising Transparency (AGCM) & Owner/Fiscal Placeholder Registry
 */

import React, { useEffect, useRef } from 'react';
import {
  X,
  ShieldCheck,
  ShieldAlert,
  Info,
  CheckCircle2,
  Megaphone,
} from 'lucide-react';

export type LegalTabId = 'privacy' | 'cookie' | 'terms' | 'transparency';

export interface LegalModalProps {
  isOpen: boolean;
  activeTab: LegalTabId;
  onTabChange: (tab: LegalTabId) => void;
  onClose: () => void;
}

export const LEGAL_OWNER_DETAILS = {
  brandName: 'Mi Stanno Fregando? — Fregometro™',
  contactEmail: 'gadmediamanager@gmail.com',
  holderPlaceholder: '[Inserisci Nome / Ragione Sociale Titolare]',
  vatPlaceholder: '[Inserisci P.IVA / Codice Fiscale]',
  addressPlaceholder: '[Inserisci Indirizzo / Sede Legale]',
  pecPlaceholder: '[Inserisci PEC aziendale]',
  lastUpdated: '12 Novembre 2026',
};

const LEGAL_TABS: Array<{ id: LegalTabId; label: string }> = [
  { id: 'privacy', label: 'Privacy Policy' },
  { id: 'cookie', label: 'Cookie Policy' },
  { id: 'terms', label: 'Termini & Disclaimer' },
  { id: 'transparency', label: 'AGCM & Titolare' },
];

export const LegalModal: React.FC<LegalModalProps> = ({
  isOpen,
  activeTab,
  onTabChange,
  onClose,
}) => {
  const closeButtonRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', handleKeyDown);
    setTimeout(() => closeButtonRef.current?.focus(), 20);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="legal-modal-title"
        className="w-full max-w-3xl max-h-[88vh] flex flex-col bg-white border-2 border-slate-900 rounded-3xl shadow-2xl overflow-hidden animate-scale-in"
      >
        {/* Modal Header */}
        <div className="px-5 sm:px-6 py-4 border-b-2 border-slate-900 bg-slate-50 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="w-9 h-9 rounded-xl bg-slate-900 text-white flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </span>
            <div>
              <h2
                id="legal-modal-title"
                className="text-base sm:text-lg font-black text-slate-950 font-display leading-tight"
              >
                Informazioni Legali e Trasparenza
              </h2>
              <p className="text-[11px] font-semibold text-slate-500">
                Ultimo aggiornamento: {LEGAL_OWNER_DETAILS.lastUpdated}
              </p>
            </div>
          </div>

          <button
            ref={closeButtonRef}
            type="button"
            onClick={onClose}
            aria-label="Chiudi finestra informativa legale"
            className="p-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-100 text-slate-700 hover:text-slate-950 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Legal Section Tabs */}
        <div
          role="tablist"
          aria-label="Sezioni legali"
          className="px-5 sm:px-6 py-2.5 bg-white border-b border-slate-200 flex flex-wrap gap-2"
        >
          {LEGAL_TABS.map((tab) => {
            const isSelected = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={isSelected}
                onClick={() => onTabChange(tab.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-extrabold transition-all cursor-pointer border ${
                  isSelected
                    ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                    : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-300'
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Scrollable Legal Document Body */}
        <div className="p-5 sm:p-6 overflow-y-auto custom-scrollbar space-y-4 text-xs sm:text-sm text-slate-700 leading-relaxed">
          {activeTab === 'privacy' && (
            <section aria-label="Privacy Policy GDPR" className="space-y-4">
              <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-300 text-emerald-950 flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
                <p className="text-xs font-bold">
                  Elaborazione 100% locale: i preventivi inseriti nel Fregometro vengono calcolati direttamente nel tuo browser e non vengono trasmessi né archiviati su server esterni.
                </p>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-1">
                  1. Titolare del Trattamento (GDPR Reg. UE 2016/679)
                </h3>
                <p>
                  Il Titolare del trattamento per il progetto <strong>{LEGAL_OWNER_DETAILS.brandName}</strong> è{' '}
                  <span className="font-mono font-bold text-slate-900">{LEGAL_OWNER_DETAILS.holderPlaceholder}</span>, con sede in{' '}
                  <span className="font-mono font-bold text-slate-900">{LEGAL_OWNER_DETAILS.addressPlaceholder}</span> — P.IVA / C.F.{' '}
                  <span className="font-mono font-bold text-slate-900">{LEGAL_OWNER_DETAILS.vatPlaceholder}</span>.
                  Email di contatto privacy e gestione richieste:{' '}
                  <a
                    href={`mailto:${LEGAL_OWNER_DETAILS.contactEmail}`}
                    className="font-extrabold text-slate-950 underline"
                  >
                    {LEGAL_OWNER_DETAILS.contactEmail}
                  </a>.
                </p>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-1">
                  2. Dati trattati, finalità e uso di localStorage
                </h3>
                <ul className="list-disc pl-5 space-y-1.5">
                  <li>
                    <strong>Calcolo dei preventivi:</strong> gli importi, la categoria, la prestazione e la provincia selezionati restano esclusivamente nella memoria locale del dispositivo dell&apos;utente per produrre la stima statistica.
                  </li>
                  <li>
                    <strong>Archiviazione locale (localStorage):</strong> qualora l&apos;utente invii un contributo anonimo tramite il modulo community o una proposta di nuova categoria, il dato viene memorizzato esclusivamente nel <code className="px-1 py-0.5 bg-slate-100 rounded font-mono text-xs">localStorage</code> del browser per aggiornare le medie locali sul dispositivo stesso, senza identificativi personali.
                  </li>
                  <li>
                    <strong>Email volontarie:</strong> chi contatta volontariamente{' '}
                    <span className="font-mono font-bold text-slate-900">{LEGAL_OWNER_DETAILS.contactEmail}</span> per informazioni, segnalazioni o prenotazione spazi pubblicitari fornisce il proprio indirizzo email ai sensi dell&apos;art. 6.1 lett. b) e f) GDPR al solo scopo di evadere la richiesta, per il tempo strettamente necessario alla corrispondenza.
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-1">
                  3. Diritti dell&apos;Interessato (Artt. 15–22 GDPR)
                </h3>
                <p>
                  In qualsiasi momento l&apos;interessato può esercitare i diritti di accesso, rettifica, cancellazione, limitazione od opposizione al trattamento scrivendo a{' '}
                  <a
                    href={`mailto:${LEGAL_OWNER_DETAILS.contactEmail}`}
                    className="font-extrabold text-slate-950 underline"
                  >
                    {LEGAL_OWNER_DETAILS.contactEmail}
                  </a>{' '}
                  nonché proporre reclamo al Garante per la Protezione dei Dati Personali. I dati salvati in locale possono essere eliminati in autonomia svuotando cache e dati sito del browser.
                </p>
              </div>
            </section>
          )}

          {activeTab === 'cookie' && (
            <section aria-label="Cookie Policy" className="space-y-4">
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-300 flex items-start gap-2.5">
                <Info className="w-4 h-4 text-slate-700 shrink-0 mt-0.5" />
                <p className="text-xs font-bold text-slate-900">
                  Distinzione trasparente tra memoria tecnica locale (necessaria al funzionamento) ed eventuali cookie pubblicitari o di terze parti.
                </p>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-1">
                  1. Archiviazione Tecnica Locale (localStorage) — Esente da Consenso
                </h3>
                <p>
                  Il sito non installa cookie di profilazione di prima parte. Utilizza unicamente lo spazio tecnico <code className="px-1 py-0.5 bg-slate-100 rounded font-mono text-xs">localStorage</code> del browser per conservare sul tuo dispositivo le segnalazioni anonime di prezzo inserite e le preferenze dell&apos;interfaccia. Trattandosi di dati tecnici strettamente funzionali all&apos;uso richiesto dall&apos;utente, non è richiesto consenso preventivo ai sensi dell&apos;art. 122 Codice Privacy e delle Linee Guida del Garante.
                </p>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-1">
                  2. Cookie di Terze Parti e Circuiti Pubblicitari (es. Google AdSense)
                </h3>
                <p>
                  Attualmente gli spazi pubblicitari mostrano annunci/segnaposto diretti senza tracciamento comportamentale di terze parti. Qualora in futuro vengano attivati script di terze parti per pubblicità programmatica (come <strong>Google AdSense</strong>) o statistica aggregata, tali cookie non tecnici verranno caricati esclusivamente <strong>previo consenso esplicito dell&apos;utente</strong> tramite apposito banner di gestione del consenso (CMP) conforme alle Linee Guida Cookie del Garante Privacy.
                </p>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-1">
                  3. Come disabilitare cookie e storage locale dal browser
                </h3>
                <p>
                  È sempre possibile cancellare o bloccare cookie e dati di archiviazione locale dalle impostazioni di sicurezza/privacy del proprio browser (Chrome, Safari, Firefox, Edge).
                </p>
              </div>
            </section>
          )}

          {activeTab === 'terms' && (
            <section aria-label="Termini d'Uso e Disclaimer" className="space-y-4">
              <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-300 text-amber-950 flex items-start gap-2.5">
                <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                <p className="text-xs font-bold">
                  Disclaimer: tutte le medie e gli scostamenti percentuali hanno finalità esclusivamente statistica e informativa, non vincolante.
                </p>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-1">
                  1. Natura Indicativa delle Stime del Fregometro
                </h3>
                <p>
                  I valori di riferimento mostrati da <strong>{LEGAL_OWNER_DETAILS.brandName}</strong> derivano da medie nazionali calibrate tramite coefficienti provinciali del costo della vita ed eventuali contributi anonimi locali. Non costituiscono perizia tecnica, preventivo commerciale vincolante, parere legale o valutazione fiscale.
                </p>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-1">
                  2. Limitazione di Responsabilità
                </h3>
                <p>
                  Il costo reale di un lavoro o servizio può legittimamente discostarsi dalla media in base a marca dei materiali/ricambi, urgenza dell&apos;intervento, complessità del caso, garanzie offerte o specifiche condizioni locali. Il Gestore non risponde di decisioni, contestazioni o accordi commerciali intrapresi dall&apos;utente con professionisti terzi sulla base dei risultati del sito.
                </p>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-1">
                  3. Uso Consentito e Proprietà Intellettuale
                </h3>
                <p>
                  L&apos;utilizzo personale e gratuito dello strumento è sempre libero. È vietata la copia sistematica del database, lo scraping automatizzato o l&apos;inserimento deliberato di dati falsi nel modulo community. Grafica, marchio e struttura del sito appartengono al rispettivo Titolare.
                </p>
              </div>
            </section>
          )}

          {activeTab === 'transparency' && (
            <section aria-label="Trasparenza Pubblicitaria AGCM e Dati Titolare" className="space-y-4">
              <div className="p-3.5 rounded-2xl bg-slate-900 text-white flex items-start gap-2.5">
                <Megaphone className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <p className="text-xs font-bold">
                  Trasparenza AGCM: ogni spazio sponsorizzato riporta chiaramente la dicitura &quot;PUBBLICITÀ&quot;. Nessuno sponsor può modificare o influenzare le medie di prezzo calcolate dal Fregometro.
                </p>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-2">
                  1. Trasparenza Pubblicitaria e Indipendenza (AGCM / Codice del Consumo)
                </h3>
                <p>
                  Tutti i formati promozionali laterali e orizzontali presenti sulla pagina sono separati dall&apos;algoritmo di stima e contrassegnati dall&apos;etichetta obbligatoria <strong>PUBBLICITÀ</strong> in conformità alle regole sulla riconoscibilità della comunicazione commerciale.
                </p>
              </div>

              <div>
                <h3 className="text-sm sm:text-base font-black text-slate-950 mb-2">
                  2. Dati Societari / Titolare per Messa Online (Art. 2250 c.c. & Art. 35 DPR 633/72)
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 p-4 rounded-2xl bg-slate-50 border border-slate-300">
                  <div>
                    <span className="block text-[10px] font-black uppercase tracking-wider text-slate-500">
                      Titolare / Ragione Sociale
                    </span>
                    <span className="font-mono text-xs font-bold text-slate-900">
                      {LEGAL_OWNER_DETAILS.holderPlaceholder}
                    </span>
                  </div>
                  <div>
                    <span className="block text-[10px] font-black uppercase tracking-wider text-slate-500">
                      Partita IVA / Codice Fiscale
                    </span>
                    <span className="font-mono text-xs font-bold text-slate-900">
                      {LEGAL_OWNER_DETAILS.vatPlaceholder}
                    </span>
                  </div>
                  <div>
                    <span className="block text-[10px] font-black uppercase tracking-wider text-slate-500">
                      Sede Legale
                    </span>
                    <span className="font-mono text-xs font-bold text-slate-900">
                      {LEGAL_OWNER_DETAILS.addressPlaceholder}
                    </span>
                  </div>
                  <div>
                    <span className="block text-[10px] font-black uppercase tracking-wider text-slate-500">
                      PEC / Contatti Commerciali
                    </span>
                    <span className="font-mono text-xs font-bold text-slate-900 block">
                      {LEGAL_OWNER_DETAILS.pecPlaceholder}
                    </span>
                    <a
                      href={`mailto:${LEGAL_OWNER_DETAILS.contactEmail}`}
                      className="text-xs font-extrabold text-slate-950 underline"
                    >
                      {LEGAL_OWNER_DETAILS.contactEmail}
                    </a>
                  </div>
                </div>
              </div>
            </section>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-5 sm:px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex flex-wrap items-center justify-between gap-2">
          <a
            href={`mailto:${LEGAL_OWNER_DETAILS.contactEmail}?subject=Richiesta%20Informazioni%20Legali%20o%20Privacy`}
            className="text-xs font-extrabold text-slate-700 hover:text-slate-950 underline"
          >
            Contatta il gestore: {LEGAL_OWNER_DETAILS.contactEmail}
          </a>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-black transition-colors cursor-pointer"
          >
            Ho capito, chiudi
          </button>
        </div>
      </div>
    </div>
  );
};

export default LegalModal;
