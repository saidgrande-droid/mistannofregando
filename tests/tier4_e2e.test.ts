import { describe, it, expect } from 'vitest';

/**
 * Tier 4: Real-World Scenarios Test Suite
 *
 * Simulates complete end-to-end user journeys for 5 realistic Italian consumer personas:
 * 1. Marco from Milan (Car mechanic overcharge -> AutoDoc affiliate -> Viral share)
 * 2. Giulia from Rome (Fair dental treatment -> Green tachometer -> Crowdsource submission)
 * 3. Antonio from Naples (Emergency boiler scam -> Critical pulsing alert -> ProntoPro lead)
 * 4. Sara from Palermo (Routine cat vaccination -> Amber tachometer -> Steady benchmark)
 * 5. Matteo from Florence (Wedding photographer package -> Upper warning zone -> Negotiation prep)
 * 6. Giuseppe from Bari (Adversarial input typing: comma normalization, error recovery)
 */

interface PersonaJourneyResult {
  personaName: string;
  category: string;
  prestation: string;
  province: string;
  quote: number;
  localRefPrice: number;
  diffEuro: number;
  diffPct: number;
  verdict: 'PREZZO_ONESTO' | 'NELLA_MEDIA' | 'TI_STANNO_FREGANDO';
  isAlert: boolean;
  needleAngle: number;
  affiliatePartner: string;
  shareCardText: string;
}

function simulateUserJourney(params: {
  persona: string;
  category: string;
  prestation: string;
  province: string;
  coeff: number;
  basePrice: number;
  rawQuote: string | number;
  affiliatePartner: string;
}): PersonaJourneyResult {
  // Input sanitization
  let sanitizedQuote: number;
  if (typeof params.rawQuote === 'string') {
    const cleanStr = params.rawQuote.replace(/[^\d.,]/g, '').replace(',', '.');
    sanitizedQuote = parseFloat(cleanStr);
  } else {
    sanitizedQuote = params.rawQuote;
  }

  if (isNaN(sanitizedQuote) || sanitizedQuote <= 0) {
    throw new Error('Invalid quote input');
  }

  const localRefPrice = Math.round(params.basePrice * params.coeff);
  const diffEuro = Math.round((sanitizedQuote - localRefPrice) * 100) / 100;
  const diffPct = Math.round(((sanitizedQuote - localRefPrice) / localRefPrice) * 10000) / 100;

  let verdict: 'PREZZO_ONESTO' | 'NELLA_MEDIA' | 'TI_STANNO_FREGANDO';
  if (diffPct <= 0.0) verdict = 'PREZZO_ONESTO';
  else if (diffPct <= 35.0) verdict = 'NELLA_MEDIA';
  else verdict = 'TI_STANNO_FREGANDO';

  const isAlert = diffPct >= 65.0;

  // Tachometer Angle
  let needleAngle: number;
  if (diffPct <= -50) needleAngle = -100;
  else if (diffPct <= 0) needleAngle = Math.round((-100 + 100 * ((diffPct + 50) / 50)) * 10) / 10;
  else if (diffPct <= 35) needleAngle = Math.round((50 * (diffPct / 35)) * 10) / 10;
  else if (diffPct <= 70) needleAngle = Math.round((50 + 50 * ((diffPct - 35) / 35)) * 10) / 10;
  else needleAngle = 100;

  const shareCardText = `Ho controllato il preventivo per ${params.prestation} a ${params.province} su MiStannoFregando.it: verdetto ${verdict} (${diffPct >= 0 ? '+' : ''}${diffPct}%)!`;

  return {
    personaName: params.persona,
    category: params.category,
    prestation: params.prestation,
    province: params.province,
    quote: sanitizedQuote,
    localRefPrice,
    diffEuro,
    diffPct,
    verdict,
    isAlert,
    needleAngle,
    affiliatePartner: params.affiliatePartner,
    shareCardText,
  };
}

describe('Tier 4: Real-World Scenarios', () => {

  it('Journey 1: Marco from Milan - Auto Tagliando Overcharge', () => {
    const journey = simulateUserJourney({
      persona: 'Marco',
      category: 'auto',
      prestation: 'Tagliando Completo Standard',
      province: 'Milano',
      coeff: 1.25,
      basePrice: 250,
      rawQuote: '450 €',
      affiliatePartner: 'AutoDoc',
    });

    expect(journey.localRefPrice).toBe(313); // 250 * 1.25 = 312.5 -> 313
    expect(journey.diffEuro).toBe(137);
    expect(journey.diffPct).toBeCloseTo(43.77, 1);
    expect(journey.verdict).toBe('TI_STANNO_FREGANDO');
    expect(journey.isAlert).toBe(false); // 43.8% is between 35% and 65%
    expect(journey.needleAngle).toBeGreaterThan(50);
    expect(journey.affiliatePartner).toBe('AutoDoc');
    expect(journey.shareCardText).toContain('TI_STANNO_FREGANDO');
  });

  it('Journey 2: Giulia from Rome - Honest Dentist Filling', () => {
    const journey = simulateUserJourney({
      persona: 'Giulia',
      category: 'dentista',
      prestation: 'Otturazione Carie Semplice',
      province: 'Roma',
      coeff: 1.18,
      basePrice: 120,
      rawQuote: '110,00 €',
      affiliatePartner: 'DentalPro',
    });

    expect(journey.localRefPrice).toBe(142); // 120 * 1.18 = 141.6 -> 142
    expect(journey.diffEuro).toBe(-32);
    expect(journey.diffPct).toBeCloseTo(-22.54, 1);
    expect(journey.verdict).toBe('PREZZO_ONESTO');
    expect(journey.isAlert).toBe(false);
    expect(journey.needleAngle).toBeLessThan(0);
    expect(journey.shareCardText).toContain('PREZZO_ONESTO');
  });

  it('Journey 3: Antonio from Naples - Emergency Boiler Severe Rip-Off', () => {
    const journey = simulateUserJourney({
      persona: 'Antonio',
      category: 'casa',
      prestation: 'Sostituzione Caldaia a Condensazione',
      province: 'Napoli',
      coeff: 0.96,
      basePrice: 1800,
      rawQuote: '3200 €',
      affiliatePartner: 'ProntoPro',
    });

    expect(journey.localRefPrice).toBe(1728); // 1800 * 0.96 = 1728
    expect(journey.diffEuro).toBe(1472);
    expect(journey.diffPct).toBeCloseTo(85.19, 1);
    expect(journey.verdict).toBe('TI_STANNO_FREGANDO');
    expect(journey.isAlert).toBe(true); // >= 65% -> CRITICAL ALERT
    expect(journey.needleAngle).toBe(100); // Clamped at max
    expect(journey.affiliatePartner).toBe('ProntoPro');
  });

  it('Journey 4: Sara from Palermo - Routine Cat Vaccination', () => {
    const journey = simulateUserJourney({
      persona: 'Sara',
      category: 'veterinario',
      prestation: 'Vaccinazione Annuale con Richiamo',
      province: 'Palermo',
      coeff: 0.92,
      basePrice: 50,
      rawQuote: 48,
      affiliatePartner: 'Babydog Pet Insurance',
    });

    expect(journey.localRefPrice).toBe(46); // 50 * 0.92 = 46
    expect(journey.diffEuro).toBe(2);
    expect(journey.diffPct).toBeCloseTo(4.35, 1);
    expect(journey.verdict).toBe('NELLA_MEDIA');
    expect(journey.isAlert).toBe(false);
    expect(journey.needleAngle).toBeGreaterThan(0);
    expect(journey.needleAngle).toBeLessThan(50);
  });

  it('Journey 5: Matteo from Florence - Wedding Photographer Package', () => {
    const journey = simulateUserJourney({
      persona: 'Matteo',
      category: 'cerimonie',
      prestation: 'Servizio Foto e Video Matrimonio',
      province: 'Firenze',
      coeff: 1.14,
      basePrice: 1600,
      rawQuote: '2800 €',
      affiliatePartner: 'Matrimonio.com',
    });

    expect(journey.localRefPrice).toBe(1824); // 1600 * 1.14 = 1824
    expect(journey.diffEuro).toBe(976);
    expect(journey.diffPct).toBeCloseTo(53.51, 1);
    expect(journey.verdict).toBe('TI_STANNO_FREGANDO');
    expect(journey.isAlert).toBe(false); // between 35% and 65%
    expect(journey.needleAngle).toBeGreaterThan(50);
    expect(journey.affiliatePartner).toBe('Matrimonio.com');
  });

  it('Journey 6: Giuseppe from Bari - Input Sanitization & Recovery', () => {
    // Entering messy text input with currency symbols and Italian comma decimals
    const journey = simulateUserJourney({
      persona: 'Giuseppe',
      category: 'auto',
      prestation: 'Sostituzione Batteria',
      province: 'Bari',
      coeff: 0.93,
      basePrice: 130,
      rawQuote: 'EUR 135,50 €',
      affiliatePartner: 'AutoDoc',
    });

    expect(journey.quote).toBe(135.50);
    expect(journey.localRefPrice).toBe(121); // 130 * 0.93 = 120.9 -> 121
    expect(journey.diffEuro).toBe(14.5);
    expect(journey.verdict).toBe('NELLA_MEDIA');
  });

  it('Journey 7: Luca from Bologna - Apartment Rent Overcharge', () => {
    const journey = simulateUserJourney({
      persona: 'Luca',
      category: 'affitti',
      prestation: 'Canone Mensile Monolocale Arredato',
      province: 'Bologna',
      coeff: 1.15,
      basePrice: 520,
      rawQuote: '950 €',
      affiliatePartner: 'SoloAffitti',
    });

    expect(journey.localRefPrice).toBe(598); // 520 * 1.15 = 598
    expect(journey.diffEuro).toBe(352);
    expect(journey.diffPct).toBeCloseTo(58.86, 1);
    expect(journey.verdict).toBe('TI_STANNO_FREGANDO');
    expect(journey.isAlert).toBe(false); // 58.86% is between 35% and 65%
    expect(journey.needleAngle).toBeGreaterThan(50);
    expect(journey.affiliatePartner).toBe('SoloAffitti');
  });

  it('Journey 8: Elena from Turin - Veterinary Surgery Fair Price', () => {
    const journey = simulateUserJourney({
      persona: 'Elena',
      category: 'veterinario',
      prestation: 'Sterilizzazione Gatta / Castrazione Cane',
      province: 'Torino',
      coeff: 1.12,
      basePrice: 180,
      rawQuote: '180,00 €',
      affiliatePartner: 'Babydog Pet Insurance',
    });

    expect(journey.localRefPrice).toBe(202); // 180 * 1.12 = 201.6 -> 202
    expect(journey.diffEuro).toBe(-22);
    expect(journey.diffPct).toBeCloseTo(-10.89, 1);
    expect(journey.verdict).toBe('PREZZO_ONESTO');
    expect(journey.isAlert).toBe(false);
    expect(journey.needleAngle).toBeLessThan(0);
    expect(journey.affiliatePartner).toBe('Babydog Pet Insurance');
  });

  it('Journey 9: Sofia from Venice - Emergency Home Plumbing Overcharge', () => {
    const journey = simulateUserJourney({
      persona: 'Sofia',
      category: 'casa',
      prestation: 'Riparazione Perdita e Flessibili',
      province: 'Venezia',
      coeff: 1.10,
      basePrice: 120,
      rawQuote: '240 €',
      affiliatePartner: 'ProntoPro',
    });

    expect(journey.localRefPrice).toBe(132); // 120 * 1.10 = 132
    expect(journey.diffEuro).toBe(108);
    expect(journey.diffPct).toBeCloseTo(81.82, 1);
    expect(journey.verdict).toBe('TI_STANNO_FREGANDO');
    expect(journey.isAlert).toBe(true); // >= 65% -> CRITICAL ALERT
    expect(journey.needleAngle).toBe(100);
    expect(journey.affiliatePartner).toBe('ProntoPro');
  });

});

