/**
 * src/core/types.ts
 * Core domain types and interface definitions for "Mi Stanno Fregando?".
 */

// ==========================================
// 1. Core Category & Geographic Literals
// ==========================================

export type CategoryId =
  | 'auto'
  | 'casa'
  | 'dentista'
  | 'veterinario'
  | 'cerimonie'
  | 'affitti';

export type MacroArea = 'Nord' | 'Centro' | 'Sud' | 'Isole';

export type DiscrepancyZone =
  | 'PREZZO_ONESTO'
  | 'NELLA_MEDIA'
  | 'TI_STANNO_FREGANDO';

// Backward and cross-module compatibility alias
export type VerdictZone = DiscrepancyZone;

// ==========================================
// 2. Reference Dataset Entities
// ==========================================

export interface Category {
  id: CategoryId;
  name: string;
  icon: string;
  description: string;
}

export interface Province {
  sigla: string;              // 2-letter uppercase ISTAT code (e.g., 'MI', 'RM', 'NA')
  nome: string;               // Full official Italian name (e.g., 'Milano', 'Roma')
  regione: string;            // Region name (e.g., 'Lombardia', 'Lazio')
  macroArea: MacroArea;       // 'Nord' | 'Centro' | 'Sud' | 'Isole'
  costCoefficient: number;    // Regional cost multiplier (0.80 to 1.25)
}

export interface Prestation {
  id: string;                                // Unique slug (e.g., 'auto_tagliando')
  categoryId: CategoryId;                    // Associated category
  name: string;                              // Consumer-friendly prestation title
  description: string;                       // Detailed scope of work / materials
  unit: string;                              // Unit of measurement ('intervento', 'ora', 'mese', etc.)
  basePrice: number;                         // National benchmark average in Euro (€)
  realisticRange: [number, number];          // Typical market range [min, max] in Euro (€)
  validationBounds: [number, number];        // Anti-spam validation bounds [min_bound, max_bound] in Euro (€)
}

export interface Dataset {
  categories: Category[];
  provinces: Province[];
  prestations: Prestation[];
}

// ==========================================
// 3. Calculator & Discrepancy Contracts
// ==========================================

export interface CalculationResult {
  quote: number;               // Clean parsed user quote in Euro (€)
  refPrice: number;            // Local reference benchmark in Euro (€): round(basePrice * costCoefficient)
  diffEuro: number;            // Absolute difference: quote - refPrice (€)
  diffPct: number;             // Percentage discrepancy: ((quote - refPrice) / refPrice) * 100 (%)
  zone: DiscrepancyZone;       // 'PREZZO_ONESTO' | 'NELLA_MEDIA' | 'TI_STANNO_FREGANDO'
  isAlert: boolean;            // true if diffPct >= 65.0% (Critical overcharge trigger)
  needleAngle: number;         // Tachometer needle angle clamped to [-100, 100] degrees
  headline: string;            // Viral Italian copy headline
  subheadline: string;         // Viral Italian explanation and advice
}

export interface QuoteValidationResult {
  isValid: boolean;
  value: number;
  error?: string;
}

// ==========================================
// 4. Crowdsourcing Contracts
// ==========================================

export interface CrowdsourceSubmission {
  categoryId: CategoryId;
  prestationId: string;
  provinceSigla: string;
  paidAmount: number;
}

export interface CrowdsourceResult {
  success: boolean;
  newAverage?: number;
  newSampleCount?: number;
  error?: string;
}

export interface CrowdsourceValidationResult {
  isValid: boolean;
  error?: string;
  minAllowed: number;
  maxAllowed: number;
}

export interface CrowdsourceRecord {
  categoryId: CategoryId;
  prestationId: string;
  provinceSigla: string;
  currentAvg: number;
  sampleCount: number;
  lastUpdated: string; // ISO 8601 string timestamp
  submissionsCount: number;
}

export interface SubmitCrowdsourceOptions {
  dataStore?: IDataStore;
  baselineRefPrice?: number;
  baselineSampleCount?: number;
  customBounds?: { minBound: number; maxBound: number };
}

// ==========================================
// 5. Storage Repository Pattern Contracts
// ==========================================

export interface IDataStore {
  // Low-level key-value API
  getItem<T = unknown>(key: string): T | null;
  setItem<T = unknown>(key: string, value: T): boolean;
  removeItem(key: string): boolean;
  clear(): void;
  isAvailable(): boolean;

  // Simple record accessors
  getRecord(prestationId: string, provinceSigla: string): CrowdsourceRecord | null;
  saveRecord(record: CrowdsourceRecord): void;
  getAllRecords(): Record<string, CrowdsourceRecord>;

  // Domain-specific Crowdsource Override API
  getCrowdsourceOverride(
    categoryId: string,
    prestationId: string,
    provinceSigla: string
  ): CrowdsourceRecord | null;
  saveCrowdsourceOverride(record: CrowdsourceRecord): boolean;
  getAllCrowdsourceOverrides(): Record<string, CrowdsourceRecord>;
  clearCrowdsourceOverrides(): void;
}

// ==========================================
// 6. Affiliate Monetization Contracts
// ==========================================

export interface AffiliatePartner {
  categoryId: CategoryId;
  partnerName: string;
  headline: string;
  ctaText: string;
  url: string;
  badgeText: string;
  urgencyLevel?: 'normal' | 'high';
  secondaryPartnerName?: string;
  secondaryUrl?: string;
  discountCallout?: string;
  partner?: string;            // Compatibility alias for partnerName
  cta?: string;                // Compatibility alias for ctaText
  headline_honest?: string;    // Compatibility headline for honest price
  headline_alert?: string;     // Compatibility headline for alert price
}
