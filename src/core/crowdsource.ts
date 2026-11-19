/**
 * src/core/crowdsource.ts
 * Crowdsourcing validation, Bayesian online running mean update, and submission handling.
 */

import { getPrestationById, getProvinceBySigla } from './dataset';
import { getReferencePrice } from './calculator';
import { getDataStore } from './storage';
import {
  CrowdsourceRecord,
  CrowdsourceResult,
  CrowdsourceSubmission,
  CrowdsourceValidationResult,
  SubmitCrowdsourceOptions,
} from './types';

export const DEFAULT_BASELINE_SAMPLE_COUNT = 100;
export const FALLBACK_MIN_RATIO = 0.15; // 0.15 * refPrice (85% discount threshold)
export const FALLBACK_MAX_RATIO = 8.0;  // 8.0 * refPrice (800% rip-off threshold)

/**
 * Validates a crowdsourced paid amount against numerical and realistic boundary constraints.
 */
export function validateCrowdsourcedPrice(
  paidAmount: number,
  refPrice: number,
  customBounds?: { minBound: number; maxBound: number }
): CrowdsourceValidationResult {
  // 1. Guard against non-numeric, NaN, Infinity, null, undefined
  if (typeof paidAmount !== 'number' || isNaN(paidAmount) || !isFinite(paidAmount)) {
    return {
      isValid: false,
      error: "L'importo inserito non è un numero valido. Inserisci una cifra in euro.",
      minAllowed: 0,
      maxAllowed: 0,
    };
  }

  // 2. Guard against zero and negative amounts
  if (paidAmount <= 0) {
    return {
      isValid: false,
      error: "L'importo deve essere superiore a 0 €.",
      minAllowed: 0,
      maxAllowed: 0,
    };
  }

  // 3. Resolve bounds
  const safeRefPrice = refPrice > 0 ? refPrice : 100;
  const minAllowed = customBounds?.minBound !== undefined
    ? customBounds.minBound
    : Math.max(1, Math.round(safeRefPrice * FALLBACK_MIN_RATIO));
  const maxAllowed = customBounds?.maxBound !== undefined
    ? customBounds.maxBound
    : Math.round(safeRefPrice * FALLBACK_MAX_RATIO);

  // 4. Boundary checks (inclusive: exact bounds are valid)
  if (paidAmount < minAllowed) {
    return {
      isValid: false,
      error: `Importo troppo basso per questa prestazione (minimo consentito: ${minAllowed.toFixed(0)} €). Inserisci l'importo effettivamente fatturato.`,
      minAllowed,
      maxAllowed,
    };
  }

  if (paidAmount > maxAllowed) {
    return {
      isValid: false,
      error: `Importo troppo elevato per questa prestazione (massimo consentito: ${maxAllowed.toFixed(0)} €). Inserisci una cifra verosimile.`,
      minAllowed,
      maxAllowed,
    };
  }

  return {
    isValid: true,
    minAllowed,
    maxAllowed,
  };
}

/**
 * Direct validation adapter matching standalone test oracle signature.
 */
export function validateCrowdsourceInput(
  paidAmount: unknown,
  minBound: number,
  maxBound: number
): [boolean, string] {
  if (typeof paidAmount !== 'number' || isNaN(paidAmount) || !isFinite(paidAmount)) {
    return [false, 'Input must be numeric'];
  }
  if (paidAmount <= 0) {
    return [false, 'Amount must be strictly positive'];
  }
  if (paidAmount < minBound) {
    return [false, `Amount too low (minimum realistic: ${minBound} €)`];
  }
  if (paidAmount > maxBound) {
    return [false, `Amount too high (maximum realistic: ${maxBound} €)`];
  }
  return [true, 'Valid'];
}

export interface UpdatedAverageResult {
  newAverage: number;
  newSampleCount: number;
}

/**
 * Computes the new weighted average and sample count using online sample mean recurrence:
 * N_new = N + 1
 * avg_new = (avg_current * N + X) / (N + 1)
 */
export function calculateUpdatedAverage(
  currentAvg: number,
  sampleCount: number,
  paidAmount: number
): UpdatedAverageResult {
  const safeCount = Math.max(0, sampleCount);
  const newSampleCount = safeCount + 1;
  const updatedMean = (currentAvg * safeCount + paidAmount) / newSampleCount;
  const newAverage = Math.round(updatedMean * 100) / 100;

  return {
    newAverage,
    newSampleCount,
  };
}

/**
 * Direct Bayesian online average calculator returning rounded integer Euro.
 */
export function bayesianOnlineAverage(
  currentAvg: number,
  sampleCount: number,
  paidAmount: number
): number {
  const safeCount = Math.max(0, sampleCount);
  const newCount = safeCount + 1;
  const newAvg = (currentAvg * safeCount + paidAmount) / newCount;
  return Math.round(newAvg);
}

/**
 * Submits an anonymous crowdsourced price, validates bounds, updates the running average,
 * and persists the updated record to the data store.
 */
export function submitCrowdsourcedPrice(
  submission: CrowdsourceSubmission,
  options?: SubmitCrowdsourceOptions
): CrowdsourceResult {
  // 1. Structural validation of metadata
  if (!submission || !submission.categoryId || !submission.prestationId || !submission.provinceSigla) {
    return {
      success: false,
      error: 'Dati di sottomissione incompleti (categoria, prestazione o provincia mancante).',
    };
  }

  const categoryId = submission.categoryId;
  const prestationId = submission.prestationId;
  const provinceSigla = submission.provinceSigla.toUpperCase().trim();
  const store = options?.dataStore ?? getDataStore();

  // 2. Retrieve existing record or baseline
  const existingRecord = store.getCrowdsourceOverride(categoryId, prestationId, provinceSigla);

  let currentAvg: number;
  let currentSampleCount: number;
  let customBounds = options?.customBounds;

  if (existingRecord) {
    currentAvg = existingRecord.currentAvg;
    currentSampleCount = existingRecord.sampleCount;
  } else {
    // Resolve baseline from options or dataset
    if (options?.baselineRefPrice !== undefined && options.baselineRefPrice > 0) {
      currentAvg = options.baselineRefPrice;
    } else {
      const prestation = getPrestationById(prestationId);
      const province = getProvinceBySigla(provinceSigla);
      const coeff = province ? province.costCoefficient : 1.0;
      currentAvg = prestation ? getReferencePrice(prestation.basePrice, coeff) : 100;
      if (prestation && !customBounds) {
        customBounds = {
          minBound: prestation.validationBounds[0],
          maxBound: prestation.validationBounds[1],
        };
      }
    }
    currentSampleCount = options?.baselineSampleCount ?? DEFAULT_BASELINE_SAMPLE_COUNT;
  }

  // 3. Validate paid amount
  const validation = validateCrowdsourcedPrice(submission.paidAmount, currentAvg, customBounds);

  if (!validation.isValid) {
    return {
      success: false,
      error: validation.error,
    };
  }

  // 4. Calculate updated online average
  const { newAverage, newSampleCount } = calculateUpdatedAverage(
    currentAvg,
    currentSampleCount,
    submission.paidAmount
  );

  // 5. Build and persist record
  const recordToSave: CrowdsourceRecord = {
    categoryId,
    prestationId,
    provinceSigla,
    currentAvg: newAverage,
    sampleCount: newSampleCount,
    lastUpdated: new Date().toISOString(),
    submissionsCount: (existingRecord?.submissionsCount ?? 0) + 1,
  };

  store.saveCrowdsourceOverride(recordToSave);

  return {
    success: true,
    newAverage,
    newSampleCount,
  };
}
