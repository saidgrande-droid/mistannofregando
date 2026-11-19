/**
 * src/core/calculator.ts
 * Mathematical discrepancy engine, classification, needle angle geometry, and copywriting.
 */

import { dataset, getPrestationById, getProvinceBySigla, getPrestationsByCategory } from './dataset';
import { CalculationResult, CategoryId, DiscrepancyZone, QuoteValidationResult } from './types';

/**
 * Calculates the local reference price benchmark based on national baseline and province cost coefficient.
 * refPrice = round(basePrice * costCoefficient)
 */
export function getReferencePrice(basePrice: number, costCoefficient: number): number {
  if (!Number.isFinite(basePrice) || basePrice <= 0) {
    throw new RangeError(`basePrice must be a positive finite number, received: ${basePrice}`);
  }
  if (!Number.isFinite(costCoefficient) || costCoefficient <= 0) {
    throw new RangeError(`costCoefficient must be a positive finite number, received: ${costCoefficient}`);
  }
  return Math.round(basePrice * costCoefficient);
}

/**
 * Classifies discrepancy percentage into one of three visual zones and evaluates alert trigger:
 * - diffPct <= 0.0%: PREZZO_ONESTO (isAlert: false)
 * - 0.0% < diffPct <= 35.0%: NELLA_MEDIA (isAlert: false)
 * - diffPct > 35.0%: TI_STANNO_FREGANDO (isAlert: true if diffPct >= 65.0%)
 */
export function classifyZone(diffPct: number): {
  zone: DiscrepancyZone;
  isAlert: boolean;
} {
  if (diffPct <= 0) {
    return { zone: 'PREZZO_ONESTO', isAlert: false };
  }
  if (diffPct <= 35) {
    return { zone: 'NELLA_MEDIA', isAlert: false };
  }
  return {
    zone: 'TI_STANNO_FREGANDO',
    isAlert: diffPct >= 65,
  };
}

// Backward and test compatibility alias
export const classifyVerdict = classifyZone;

/**
 * Maps discrepancy percentage onto a 200° speedometer arc [-100°, +100°].
 * - diffPct <= -50.0% -> -100.0°
 * - diffPct == 0.0%   -> 0.0°
 * - diffPct == +35.0% -> +50.0°
 * - diffPct >= +70.0% -> +100.0°
 */
export function getNeedleAngle(diffPct: number): number {
  if (!Number.isFinite(diffPct)) return 0;

  let angle: number;
  if (diffPct <= -50.0) {
    angle = -100.0;
  } else if (diffPct <= 0.0) {
    // Maps [-50, 0] to [-100, 0]
    angle = -100.0 + 100.0 * ((diffPct + 50.0) / 50.0);
  } else if (diffPct <= 35.0) {
    // Maps (0, 35] to (0, 50]
    angle = 50.0 * (diffPct / 35.0);
  } else if (diffPct <= 70.0) {
    // Maps (35, 70] to (50, 100]
    angle = 50.0 + 50.0 * ((diffPct - 35.0) / 35.0);
  } else {
    angle = 100.0;
  }

  return Math.round(angle * 100) / 100;
}

/**
 * Maps discrepancy percentage onto a 180° semi-circle speedometer arc [0°, 180°].
 * - diffPct <= -50.0% -> 0.0°
 * - diffPct == 0.0%   -> 60.0°
 * - diffPct == +35.0% -> 120.0°
 * - diffPct >= +70.0% -> 180.0°
 */
export function getNeedleAngle180(diffPct: number): number {
  if (!Number.isFinite(diffPct)) return 60;

  let angle: number;
  if (diffPct <= -50.0) {
    angle = 0.0;
  } else if (diffPct <= 0.0) {
    // Maps [-50, 0] to [0, 60]
    angle = 60.0 * ((diffPct + 50.0) / 50.0);
  } else if (diffPct <= 35.0) {
    // Maps (0, 35] to (60, 120]
    angle = 60.0 + 60.0 * (diffPct / 35.0);
  } else if (diffPct <= 70.0) {
    // Maps (35, 70] to (120, 180]
    angle = 120.0 + 60.0 * ((diffPct - 35.0) / 35.0);
  } else {
    angle = 180.0;
  }

  return Math.round(angle * 100) / 100;
}

/**
 * Generates viral Italian copywriting headlines and subheadlines.
 */
export function generateCopywriting(
  zone: DiscrepancyZone,
  isAlert: boolean,
  diffEuro: number,
  diffPct: number,
  quote: number,
  refPrice: number
): {
  headline: string;
  subheadline: string;
} {
  const absDiffEuro = Math.abs(diffEuro);
  const absDiffPct = Math.abs(diffPct);

  const fmtQuote = `${quote.toLocaleString('it-IT')} €`;
  const fmtRef = `${refPrice.toLocaleString('it-IT')} €`;
  const fmtAbsEuro = `${absDiffEuro.toLocaleString('it-IT')} €`;
  const fmtSignedEuro = diffEuro > 0 ? `+${diffEuro.toLocaleString('it-IT')} €` : `${diffEuro.toLocaleString('it-IT')} €`;
  const fmtSignedPct = diffPct > 0 ? `+${diffPct.toFixed(1)}%` : `${diffPct.toFixed(1)}%`;

  // Zone 1: PREZZO ONESTO
  if (zone === 'PREZZO_ONESTO') {
    if (diffPct <= -40) {
      return {
        headline: 'Prezzo Stracciato: Occhio alla Qualità!',
        subheadline: `Stai risparmiando ben ${fmtAbsEuro} (-${absDiffPct.toFixed(1)}%) rispetto alla media locale di ${fmtRef}. Prezzo eccezionale: accertati solo che il preventivo includa tutti i materiali a norma e garanzia scritta!`,
      };
    }
    if (diffPct <= -15) {
      return {
        headline: 'Ottimo Affare: Prezzo Super Onesto!',
        subheadline: `Stai risparmiando ${fmtAbsEuro} (-${absDiffPct.toFixed(1)}%) rispetto alla media locale di ${fmtRef}. Trattalo bene questo professionista: è una specie protetta in via d'estinzione!`,
      };
    }
    return {
      headline: 'Prezzo Onesto: Tariffa Equa',
      subheadline: `Il preventivo di ${fmtQuote} è allineato o inferiore alla media locale di ${fmtRef} (${fmtSignedPct}). Tariffa assolutamente corretta: puoi procedere con serenità.`,
    };
  }

  // Zone 2: NELLA MEDIA
  if (zone === 'NELLA_MEDIA') {
    if (diffPct <= 15) {
      return {
        headline: 'Prezzo Nella Media',
        subheadline: `Il preventivo di ${fmtQuote} è perfettamente allineato ai prezzi correnti della tua provincia (${fmtRef}, ${fmtSignedPct}). Non ti stanno regalando nulla, ma la tariffa è nello standard.`,
      };
    }
    return {
      headline: 'Nella Media (Fascia Alta)',
      subheadline: `Il preventivo di ${fmtQuote} supera la media di ${fmtRef} di ${fmtSignedEuro} (${fmtSignedPct}). Rientra ancora nei limiti fisiologici di mercato, ma potresti provare a chiedere un piccolo sconto.`,
    };
  }

  // Zone 3: TI STANNO FREGANDO
  if (isAlert) {
    if (diffPct >= 150) {
      return {
        headline: '🚨 TI STANNO FREGANDO ALLA GRANDE!',
        subheadline: `Prezzo folle fuori scala (+${diffPct.toFixed(1)}%): ti chiedono ${fmtSignedEuro} in più rispetto alla media locale (${fmtRef})! Con questa cifra compri più del doppio della prestazione. Ferma tutto e chiedi subito altri preventivi!`,
      };
    }
    return {
      headline: '🚨 TI STANNO FREGANDO!',
      subheadline: `Allarme stangata: il preventivo supera la media locale di ben ${fmtSignedEuro} (${fmtSignedPct} rispetto a ${fmtRef}). È un ricarico ingiustificato: confronta subito altre offerte prima di accettare!`,
    };
  }

  // Zone 3 Non-Alert (35% < diffPct < 65%)
  return {
    headline: 'Occhio: Prezzo Fuori Mercato!',
    subheadline: `Attenzione: il preventivo supera la media provinciale (${fmtRef}) di ${fmtSignedEuro} (${fmtSignedPct}). Prima di firmare, richiedi la specifica dettagliata delle voci o valuta un secondo parere.`,
  };
}

/**
 * Parses and sanitizes raw quote input from string or number.
 */
export function parseAndValidateQuote(rawInput: unknown): QuoteValidationResult {
  if (rawInput === null || rawInput === undefined || rawInput === '') {
    return { isValid: false, value: 0, error: 'Inserisci un importo valido.' };
  }

  let numValue: number;

  if (typeof rawInput === 'number') {
    numValue = rawInput;
  } else if (typeof rawInput === 'string') {
    const cleaned = rawInput
      .replace(/€/g, '')
      .replace(/\s+/g, '')
      .replace(/\./g, '')
      .replace(',', '.');

    numValue = parseFloat(cleaned);
  } else {
    return { isValid: false, value: 0, error: 'Formato preventivo non valido.' };
  }

  if (!Number.isFinite(numValue) || isNaN(numValue)) {
    return { isValid: false, value: 0, error: "Inserisci un numero valido per l'importo." };
  }

  if (numValue < 0) {
    return { isValid: false, value: numValue, error: "L'importo del preventivo non può essere negativo." };
  }

  if (numValue > 10_000_000) {
    return { isValid: false, value: numValue, error: 'Importo fuori scala (massimo 10.000.000 €).' };
  }

  return { isValid: true, value: numValue };
}

/**
 * Pure calculation function from quote and reference price.
 */
export function calculateFromPrice(quote: number, refPrice: number): CalculationResult {
  if (!Number.isFinite(quote) || quote < 0) {
    throw new RangeError(`Quote must be a non-negative finite number, received: ${quote}`);
  }
  if (!Number.isFinite(refPrice) || refPrice <= 0) {
    throw new RangeError(`Reference price must be strictly greater than 0, received: ${refPrice}`);
  }

  const diffEuro = Math.round((quote - refPrice) * 100) / 100;
  const diffPct = Math.round(((quote - refPrice) / refPrice) * 10000) / 100;

  const { zone, isAlert } = classifyZone(diffPct);
  const needleAngle = getNeedleAngle(diffPct);
  const { headline, subheadline } = generateCopywriting(
    zone,
    isAlert,
    diffEuro,
    diffPct,
    quote,
    refPrice
  );

  return {
    quote,
    refPrice,
    diffEuro,
    diffPct,
    zone,
    isAlert,
    needleAngle,
    headline,
    subheadline,
  };
}

/**
 * High-level facade for discrepancy calculation from category, prestation, province and quote.
 */
export function calculateDiscrepancy(
  category: CategoryId,
  prestationId: string,
  provinceSigla: string,
  quote: number,
  customRefPrice?: number
): CalculationResult {
  if (!Number.isFinite(quote) || quote < 0) {
    throw new RangeError(`Quote must be greater than or equal to 0, received: ${quote}`);
  }

  let effectiveRefPrice = customRefPrice;

  if (effectiveRefPrice === undefined || effectiveRefPrice <= 0) {
    if (prestationId === 'custom') {
      const catPrestations = getPrestationsByCategory(category);
      const avgBase = catPrestations.length > 0
        ? catPrestations.reduce((acc, p) => acc + p.basePrice, 0) / catPrestations.length
        : 100;
      const province = getProvinceBySigla(provinceSigla);
      const costCoefficient = province ? province.costCoefficient : 1.0;
      effectiveRefPrice = Math.round(avgBase * costCoefficient);
    } else {
      const prestation = getPrestationById(prestationId);
      if (!prestation) {
        throw new Error(`Prestazione non trovata: ${prestationId} in categoria ${category}`);
      }

      const province = getProvinceBySigla(provinceSigla);
      const costCoefficient = province ? province.costCoefficient : 1.0;

      effectiveRefPrice = getReferencePrice(prestation.basePrice, costCoefficient);
    }
  }

  return calculateFromPrice(quote, effectiveRefPrice);
}
