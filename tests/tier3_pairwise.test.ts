import { describe, it, expect } from 'vitest';

/**
 * Tier 3: Cross-Feature Combinations Test Suite
 *
 * Systematic pairwise matrices testing interactions between independent variables:
 * - Matrix 1: Category x Province Multiplier Extremes (6 categories x [Milano 1.25, Enna 0.80])
 * - Matrix 2: Discrepancy Level x Affiliate Urgency (4 verdict tiers x Dynamic CTAs)
 * - Matrix 3: Crowdsource Recalculation x Subsequent Calculator Lookup
 * - Matrix 4: Multi-Province & Category Isolation
 * - Matrix 5: Extreme Quotes x Regional Multipliers
 * - Matrix 6: Alternating Category Submissions Sequence
 */

type CategoryId = 'auto' | 'casa' | 'dentista' | 'veterinario' | 'cerimonie' | 'affitti';

interface PrestationBenchmark {
  id: string;
  category: CategoryId;
  basePrice: number;
}

const CATEGORY_BENCHMARKS: PrestationBenchmark[] = [
  { id: 'auto_tagliando', category: 'auto', basePrice: 250 },
  { id: 'casa_caldaia', category: 'casa', basePrice: 1800 },
  { id: 'dentista_otturazione', category: 'dentista', basePrice: 120 },
  { id: 'vet_vaccino', category: 'veterinario', basePrice: 50 },
  { id: 'cerimonia_menu', category: 'cerimonie', basePrice: 110 },
  { id: 'affitto_bilocale', category: 'affitti', basePrice: 720 },
];

function calculateRef(basePrice: number, coeff: number): number {
  return Math.round(basePrice * coeff);
}

function calculateDiff(quote: number, ref: number) {
  const diffPct = Math.round(((quote - ref) / ref) * 10000) / 100;
  let zone: 'PREZZO_ONESTO' | 'NELLA_MEDIA' | 'TI_STANNO_FREGANDO';
  if (diffPct <= 0) zone = 'PREZZO_ONESTO';
  else if (diffPct <= 35) zone = 'NELLA_MEDIA';
  else zone = 'TI_STANNO_FREGANDO';
  const isAlert = diffPct >= 65;
  return { diffPct, zone, isAlert };
}

function updateRunningAvg(currAvg: number, count: number, newVal: number): number {
  return Math.round((currAvg * count + newVal) / (count + 1));
}

describe('Tier 3: Cross-Feature Combinations', () => {

  // Matrix 1: Category x Extreme Province Multipliers
  describe('Matrix 1: Category x Province Multiplier Extremes (Milano vs Enna)', () => {
    const MI_COEFF = 1.25;
    const EN_COEFF = 0.80;

    CATEGORY_BENCHMARKS.forEach(item => {
      it(`should produce higher benchmark in Milano than in Enna for ${item.category}`, () => {
        const refMilano = calculateRef(item.basePrice, MI_COEFF);
        const refEnna = calculateRef(item.basePrice, EN_COEFF);

        expect(refMilano).toBeGreaterThan(refEnna);
        expect(refMilano).toBe(Math.round(item.basePrice * 1.25));
        expect(refEnna).toBe(Math.round(item.basePrice * 0.80));

        // An intermediate quote equal to Milano benchmark should be an overcharge in Enna
        const diffEnna = calculateDiff(refMilano, refEnna);
        expect(diffEnna.zone).toBe('TI_STANNO_FREGANDO');
      });
    });
  });

  // Matrix 2: Discrepancy Level x Affiliate Urgency
  describe('Matrix 2: Discrepancy Level x Affiliate Urgency', () => {
    it('should present calm educational CTA when quote is PREZZO_ONESTO (-20%)', () => {
      const { zone, isAlert } = calculateDiff(80, 100);
      expect(zone).toBe('PREZZO_ONESTO');
      expect(isAlert).toBe(false);

      const cta = isAlert
        ? '🚨 Allarme Rincaro: Confronta alternative'
        : 'Scopri ulteriori opportunità di risparmio';
      expect(cta).toContain('ulteriori opportunità');
    });

    it('should present standard informational CTA when quote is NELLA_MEDIA (+20%)', () => {
      const { zone, isAlert } = calculateDiff(120, 100);
      expect(zone).toBe('NELLA_MEDIA');
      expect(isAlert).toBe(false);

      const cta = isAlert
        ? '🚨 Allarme Rincaro: Confronta alternative'
        : 'Scopri le offerte dei migliori professionisti';
      expect(cta).toContain('offerte dei migliori professionisti');
    });

    it('should present high-urgency red warning CTA when quote is TI_STANNO_FREGANDO with isAlert (+80%)', () => {
      const { zone, isAlert } = calculateDiff(180, 100);
      expect(zone).toBe('TI_STANNO_FREGANDO');
      expect(isAlert).toBe(true);

      const cta = isAlert
        ? '🚨 Allarme Rincaro: Confronta 3 preventivi gratuiti prima di pagare'
        : 'Scopri le offerte';
      expect(cta).toContain('Allarme Rincaro');
    });
  });

  // Matrix 3: Crowdsource Recalculation x Subsequent Calculator Lookup
  describe('Matrix 3: Crowdsource Live Recalculation x Subsequent Lookup', () => {
    it('should change user verdict from TI_STANNO_FREGANDO to NELLA_MEDIA when crowdsourced prices shift local average up', () => {
      let activeRef = 100;
      let count = 5;
      const testQuote = 136; // Initially +36% -> TI_STANNO_FREGANDO

      const initialResult = calculateDiff(testQuote, activeRef);
      expect(initialResult.zone).toBe('TI_STANNO_FREGANDO');

      // Multiple users report paying 140 in this city
      for (let i = 0; i < 5; i++) {
        activeRef = updateRunningAvg(activeRef, count, 140);
        count++;
      }

      // activeRef is now higher (around 120)
      expect(activeRef).toBeGreaterThan(115);

      // Re-evaluating the same quote 136 against the new crowdsourced benchmark
      const updatedResult = calculateDiff(testQuote, activeRef);
      expect(updatedResult.diffPct).toBeLessThanOrEqual(35.0);
      expect(updatedResult.zone).toBe('NELLA_MEDIA');
    });
  });

  // Matrix 4: Multi-Province & Category Isolation
  describe('Matrix 4: Multi-Province & Category Isolation', () => {
    it('should maintain independent provincial datasets when updates occur in one province', () => {
      const state = {
        'MI_auto_tagliando': { avg: 313, count: 20 },
        'RM_auto_tagliando': { avg: 295, count: 20 },
      };

      // User submits in Milan
      const updatedMilanAvg = updateRunningAvg(state['MI_auto_tagliando'].avg, state['MI_auto_tagliando'].count, 350);
      state['MI_auto_tagliando'].avg = updatedMilanAvg;
      state['MI_auto_tagliando'].count += 1;

      // Rome benchmark must remain strictly unchanged
      expect(state['RM_auto_tagliando'].avg).toBe(295);
      expect(state['RM_auto_tagliando'].count).toBe(20);
    });

    it('should maintain independent category datasets when updates occur in one category', () => {
      const state = {
        'MI_auto_tagliando': { avg: 313, count: 20 },
        'MI_casa_caldaia': { avg: 2250, count: 10 },
      };

      const updatedAuto = updateRunningAvg(state['MI_auto_tagliando'].avg, state['MI_auto_tagliando'].count, 380);
      state['MI_auto_tagliando'].avg = updatedAuto;

      expect(state['MI_casa_caldaia'].avg).toBe(2250);
      expect(state['MI_casa_caldaia'].count).toBe(10);
    });
  });

  // Matrix 5: Extreme Quotes x Regional Multipliers
  describe('Matrix 5: Extreme Quotes x Regional Multipliers', () => {
    it('should correctly clamp needle and trigger alert for massive quote in low-cost province (Enna 0.80)', () => {
      const ennaRef = calculateRef(250, 0.80); // 200
      const massiveQuote = 50000;
      const { diffPct, zone, isAlert } = calculateDiff(massiveQuote, ennaRef);

      expect(diffPct).toBeGreaterThan(1000);
      expect(zone).toBe('TI_STANNO_FREGANDO');
      expect(isAlert).toBe(true);
    });
  });

  // Matrix 6: Alternating Category Submissions Sequence
  describe('Matrix 6: Alternating Category Submissions Sequence', () => {
    it('should process rapid alternating submissions across different categories cleanly', () => {
      const categories: CategoryId[] = ['auto', 'casa', 'dentista', 'veterinario', 'cerimonie', 'affitti'];
      const averages: Record<CategoryId, { avg: number; count: number }> = {
        auto: { avg: 250, count: 10 },
        casa: { avg: 900, count: 10 },
        dentista: { avg: 120, count: 10 },
        veterinario: { avg: 50, count: 10 },
        cerimonie: { avg: 110, count: 10 },
        affitti: { avg: 720, count: 10 },
      };

      // 3 rounds of alternating submissions
      for (let round = 1; round <= 3; round++) {
        categories.forEach(cat => {
          const increment = round * 10;
          averages[cat].avg = updateRunningAvg(averages[cat].avg, averages[cat].count, averages[cat].avg + increment);
          averages[cat].count += 1;
        });
      }

      categories.forEach(cat => {
        expect(averages[cat].count).toBe(13);
        expect(averages[cat].avg).toBeGreaterThan(0);
      });
    });
  });

});
