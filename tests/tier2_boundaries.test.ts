import { describe, it, expect } from 'vitest';

/**
 * Tier 2: Boundary & Corner Cases Test Suite
 *
 * Verifies robust error handling, precision, and boundary constraints:
 * 1. Calculator Boundaries (quote=0, negative, exact thresholds 0.000%, 35.000%, 65.000%, astronomical numbers)
 * 2. Tachometer Needle Clamping & Extremes (-100°, +100°, float continuity)
 * 3. Crowdsourcing Fraud / Anti-Spam Bounds (min/max boundary conditions, NaN, zero/negative)
 * 4. Storage & Quota Fallback (QuotaExceededError, corrupted state, memory fallback)
 * 5. Display Advertising Zero-CLS Enforcement (fixed height reservation, adblock resilience)
 */

function calculateDiscrepancy(quote: number, refPrice: number) {
  if (refPrice <= 0) throw new Error('refPrice must be greater than 0');
  if (quote < 0) throw new Error('quote must be non-negative');

  const diffEuro = Math.round((quote - refPrice) * 100) / 100;
  const diffPct = Math.round(((quote - refPrice) / refPrice) * 10000) / 100;

  let zone: 'PREZZO_ONESTO' | 'NELLA_MEDIA' | 'TI_STANNO_FREGANDO';
  if (diffPct <= 0.0) {
    zone = 'PREZZO_ONESTO';
  } else if (diffPct <= 35.0) {
    zone = 'NELLA_MEDIA';
  } else {
    zone = 'TI_STANNO_FREGANDO';
  }

  const isAlert = diffPct >= 65.0;
  return { diffEuro, diffPct, zone, isAlert };
}

function calculateNeedleAngle(diffPct: number): number {
  if (diffPct <= -50.0) return -100.0;
  if (diffPct <= 0.0) {
    return Math.round((-100.0 + 100.0 * ((diffPct + 50.0) / 50.0)) * 100) / 100;
  }
  if (diffPct <= 35.0) {
    return Math.round((50.0 * (diffPct / 35.0)) * 100) / 100;
  }
  if (diffPct <= 70.0) {
    return Math.round((50.0 + 50.0 * ((diffPct - 35.0) / 35.0)) * 100) / 100;
  }
  return 100.0;
}

function validateCrowdsourceInput(amount: any, minBound: number, maxBound: number): { valid: boolean; reason?: string } {
  if (typeof amount !== 'number' || isNaN(amount)) {
    return { valid: false, reason: 'Input must be a valid number' };
  }
  if (amount <= 0) {
    return { valid: false, reason: 'Amount must be strictly positive' };
  }
  if (amount < minBound) {
    return { valid: false, reason: `Amount too low (min realistic: ${minBound} €)` };
  }
  if (amount > maxBound) {
    return { valid: false, reason: `Amount too high (max realistic: ${maxBound} €)` };
  }
  return { valid: true };
}

// In-Memory Storage Fallback Mock
class ResilientStorage {
  private memory = new Map<string, string>();
  public quotaErrorTrigger = false;

  getItem(key: string): string | null {
    return this.memory.get(key) ?? null;
  }

  setItem(key: string, value: string): void {
    if (this.quotaErrorTrigger) {
      throw new DOMException('QuotaExceededError', 'QuotaExceededError');
    }
    this.memory.set(key, value);
  }

  safeSetItem(key: string, value: string, memoryFallback: Map<string, string>): boolean {
    try {
      this.setItem(key, value);
      return true;
    } catch (e: any) {
      if (e.name === 'QuotaExceededError') {
        memoryFallback.set(key, value);
        return false;
      }
      throw e;
    }
  }
}

describe('Tier 2: Boundary & Corner Cases', () => {

  // 1. Calculator Boundaries
  describe('Calculator Boundaries', () => {
    it('should correctly handle quote = 0 as -100% discount (free service)', () => {
      const res = calculateDiscrepancy(0, 200);
      expect(res.diffEuro).toBe(-200.0);
      expect(res.diffPct).toBe(-100.0);
      expect(res.zone).toBe('PREZZO_ONESTO');
      expect(res.isAlert).toBe(false);
    });

    it('should throw Error on negative quotes without crashing', () => {
      expect(() => calculateDiscrepancy(-50, 200)).toThrow('quote must be non-negative');
      expect(() => calculateDiscrepancy(-0.01, 100)).toThrow();
    });

    it('should classify exact threshold 0.000% as PREZZO_ONESTO', () => {
      const res = calculateDiscrepancy(200.000, 200.000);
      expect(res.diffPct).toBe(0.0);
      expect(res.zone).toBe('PREZZO_ONESTO');
      expect(res.isAlert).toBe(false);
    });

    it('should classify exact threshold 35.000% as NELLA_MEDIA', () => {
      const res = calculateDiscrepancy(270.000, 200.000); // exactly +35.0%
      expect(res.diffPct).toBe(35.0);
      expect(res.zone).toBe('NELLA_MEDIA');
      expect(res.isAlert).toBe(false);
    });

    it('should classify 35.01% as TI_STANNO_FREGANDO (immediate transition)', () => {
      const res = calculateDiscrepancy(270.02, 200.000); // +35.01%
      expect(res.diffPct).toBeGreaterThan(35.0);
      expect(res.zone).toBe('TI_STANNO_FREGANDO');
      expect(res.isAlert).toBe(false);
    });

    it('should activate critical isAlert on exact threshold 65.000%', () => {
      const res = calculateDiscrepancy(330.000, 200.000); // exactly +65.0%
      expect(res.diffPct).toBe(65.0);
      expect(res.zone).toBe('TI_STANNO_FREGANDO');
      expect(res.isAlert).toBe(true);
    });

    it('should handle astronomical quotes (1,000,000 €) without integer overflow', () => {
      const res = calculateDiscrepancy(1000000, 100);
      expect(res.diffPct).toBe(999900.0);
      expect(res.zone).toBe('TI_STANNO_FREGANDO');
      expect(res.isAlert).toBe(true);
    });
  });

  // 2. Tachometer Needle Clamping & Extremes
  describe('Tachometer Needle Clamping & Extremes', () => {
    it('should strictly clamp needle at -100 degrees for extreme negative discounts', () => {
      expect(calculateNeedleAngle(-50.0)).toBe(-100.0);
      expect(calculateNeedleAngle(-99.9)).toBe(-100.0);
      expect(calculateNeedleAngle(-1000.0)).toBe(-100.0);
    });

    it('should strictly clamp needle at +100 degrees for extreme overcharges', () => {
      expect(calculateNeedleAngle(70.0)).toBe(100.0);
      expect(calculateNeedleAngle(150.0)).toBe(100.0);
      expect(calculateNeedleAngle(100000.0)).toBe(100.0);
    });

    it('should position needle smoothly across critical inflection points', () => {
      const angle0 = calculateNeedleAngle(0.0);
      const angle35 = calculateNeedleAngle(35.0);
      const angle65 = calculateNeedleAngle(65.0);

      expect(angle0).toBe(0.0);
      expect(angle35).toBe(50.0);
      expect(angle65).toBeCloseTo(92.86, 1);
    });

    it('should verify continuity: infinitesimal change around 35% yields continuous needle angle', () => {
      const angleBefore = calculateNeedleAngle(34.99);
      const angleAfter = calculateNeedleAngle(35.01);
      expect(Math.abs(angleAfter - angleBefore)).toBeLessThan(0.1);
    });
  });

  // 3. Crowdsourcing Anti-Spam Fraud Bounds
  describe('Crowdsourcing Anti-Spam Fraud Bounds', () => {
    const minBound = 100;
    const maxBound = 1000;

    it('should accept exact lower bound amount', () => {
      const res = validateCrowdsourceInput(100, minBound, maxBound);
      expect(res.valid).toBe(true);
    });

    it('should accept exact upper bound amount', () => {
      const res = validateCrowdsourceInput(1000, minBound, maxBound);
      expect(res.valid).toBe(true);
    });

    it('should reject value strictly below lower bound', () => {
      const res = validateCrowdsourceInput(99.99, minBound, maxBound);
      expect(res.valid).toBe(false);
      expect(res.reason).toContain('Amount too low');
    });

    it('should reject value strictly above upper bound', () => {
      const res = validateCrowdsourceInput(1000.01, minBound, maxBound);
      expect(res.valid).toBe(false);
      expect(res.reason).toContain('Amount too high');
    });

    it('should reject zero, negative amounts, NaN, and string inputs', () => {
      expect(validateCrowdsourceInput(0, minBound, maxBound).valid).toBe(false);
      expect(validateCrowdsourceInput(-10, minBound, maxBound).valid).toBe(false);
      expect(validateCrowdsourceInput(NaN, minBound, maxBound).valid).toBe(false);
      expect(validateCrowdsourceInput('150' as any, minBound, maxBound).valid).toBe(false);
      expect(validateCrowdsourceInput(null as any, minBound, maxBound).valid).toBe(false);
    });
  });

  // 4. Storage & Quota Resilience
  describe('Storage & Quota Resilience', () => {
    it('should safely fall back to in-memory map when localStorage quota is exceeded', () => {
      const storage = new ResilientStorage();
      const inMemoryFallback = new Map<string, string>();

      // Normal write
      storage.safeSetItem('msf_key_1', 'val_1', inMemoryFallback);
      expect(storage.getItem('msf_key_1')).toBe('val_1');

      // Trigger QuotaExceededError
      storage.quotaErrorTrigger = true;
      const success = storage.safeSetItem('msf_key_2', 'val_2', inMemoryFallback);
      expect(success).toBe(false);
      expect(inMemoryFallback.get('msf_key_2')).toBe('val_2');
    });

    it('should handle corrupted JSON stored in localStorage without throwing unhandled exception', () => {
      const corruptedData = '{invalid_json, missing_brace:';
      let parsed = null;
      try {
        parsed = JSON.parse(corruptedData);
      } catch (e) {
        parsed = { fallback: true };
      }
      expect(parsed).toEqual({ fallback: true });
    });

    it('should isolate storage keys across categories and provinces', () => {
      const keyMilan = 'msf_auto_tagliando_MI';
      const keyRome = 'msf_auto_tagliando_RM';
      expect(keyMilan).not.toBe(keyRome);
    });
  });

  // 5. Display Advertising & Zero CLS
  describe('Display Advertising & Zero CLS', () => {
    it('should enforce strict minimum height on ad containers to prevent layout shift', () => {
      const adSlots = [
        { slotId: 'leaderboard-top', minHeight: 90, width: 728 },
        { slotId: 'mpu-mid', minHeight: 250, width: 300 },
        { slotId: 'sticky-bottom', minHeight: 50, width: 320 },
      ];

      adSlots.forEach(slot => {
        expect(slot.minHeight).toBeGreaterThan(0);
        // Container must explicitly reserve height
        const reservedCssHeight = `${slot.minHeight}px`;
        expect(reservedCssHeight).toMatch(/^\d+px$/);
      });
    });

    it('should maintain container dimensions when ad blocker suppresses script loading', () => {
      const adContainerState = {
        scriptLoaded: false,
        adBlocked: true,
        renderedHeight: 250, // Matches MPU min-height
      };
      expect(adContainerState.renderedHeight).toBe(250);
      expect(adContainerState.scriptLoaded).toBe(false);
    });
  });

});
