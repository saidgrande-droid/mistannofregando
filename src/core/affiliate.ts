/**
 * src/core/affiliate.ts
 * Category affiliate partner mapping with dynamic high-urgency copywriting on overcharge.
 */

import { AffiliatePartner, CategoryId } from './types';

interface AffiliateCategoryConfig {
  normal: AffiliatePartner;
  highUrgency: AffiliatePartner;
}

export const AFFILIATE_DIRECTORY: Record<CategoryId, AffiliateCategoryConfig> = {
  auto: {
    normal: {
      categoryId: 'auto',
      partnerName: 'AutoDoc',
      partner: 'AutoDoc',
      headline: 'Risparmia sulla manutenzione auto con ricambi originali scontati',
      headline_honest: 'Risparmia sulla manutenzione auto con ricambi originali scontati',
      headline_alert: '🚨 Non farti spennare dal meccanico! Risparmia fino al 40% sui ricambi su AutoDoc',
      ctaText: 'Confronta prezzi ricambi',
      cta: 'Confronta prezzi ricambi',
      url: 'https://www.autodoc.it',
      badgeText: 'Partner Ufficiale Ricambi Auto',
      urgencyLevel: 'normal',
      secondaryPartnerName: 'Prima Assicurazioni',
      secondaryUrl: 'https://www.prima.it',
      discountCallout: 'Fino al 40% di risparmio sui ricambi originali',
    },
    highUrgency: {
      categoryId: 'auto',
      partnerName: 'AutoDoc',
      partner: 'AutoDoc',
      headline: '🚨 Non farti spennare dal meccanico! Risparmia fino al 40% sui ricambi su AutoDoc',
      headline_honest: 'Risparmia sulla manutenzione auto con ricambi originali scontati',
      headline_alert: '🚨 Non farti spennare dal meccanico! Risparmia fino al 40% sui ricambi su AutoDoc',
      ctaText: 'Risparmia fino al 40% sui ricambi originali e trova officine su AutoDoc →',
      cta: 'Confronta prezzi ricambi',
      url: 'https://www.autodoc.it',
      badgeText: '🚨 ALLARME SOVRAPPREZZO MECCANICO',
      urgencyLevel: 'high',
      secondaryPartnerName: 'Prima Assicurazioni',
      secondaryUrl: 'https://www.prima.it',
      discountCallout: 'Non farti fregare: confronta i ricambi prima di approvare il lavoro',
    },
  },
  casa: {
    normal: {
      categoryId: 'casa',
      partnerName: 'ProntoPro',
      partner: 'ProntoPro',
      headline: 'Trova professionisti qualificati per i lavori di casa',
      headline_honest: 'Trova professionisti qualificati per i lavori di casa',
      headline_alert: '🚨 Prezzo fuori mercato! Richiedi 3 preventivi gratuiti da artigiani verificati',
      ctaText: 'Ricevi 3 preventivi gratis',
      cta: 'Ricevi 3 preventivi gratis',
      url: 'https://www.prontopro.it',
      badgeText: 'Confronto Preventivi Certificati',
      urgencyLevel: 'normal',
      secondaryPartnerName: 'Facile.it Casa',
      secondaryUrl: 'https://www.facile.it',
      discountCallout: 'Confronta fino a 4 preventivi gratis senza impegno',
    },
    highUrgency: {
      categoryId: 'casa',
      partnerName: 'ProntoPro',
      partner: 'ProntoPro',
      headline: '🚨 Prezzo fuori mercato! Richiedi 3 preventivi gratuiti da artigiani verificati',
      headline_honest: 'Trova professionisti qualificati per i lavori di casa',
      headline_alert: '🚨 Prezzo fuori mercato! Richiedi 3 preventivi gratuiti da artigiani verificati',
      ctaText: 'Richiedi gratis e senza impegno 3 preventivi verificati su ProntoPro →',
      cta: 'Ricevi 3 preventivi gratis',
      url: 'https://www.prontopro.it',
      badgeText: '🚨 PREVENTIVO FUORI MERCATO',
      urgencyLevel: 'high',
      secondaryPartnerName: 'Facile.it Casa',
      secondaryUrl: 'https://www.facile.it',
      discountCallout: 'Risparmia fino al 35% scegliendo artigiani certificati',
    },
  },
  dentista: {
    normal: {
      categoryId: 'dentista',
      partnerName: 'DentalPro',
      partner: 'DentalPro',
      headline: 'Scopri i centri odontoiatrici con tariffe trasparenti vicino a te',
      headline_honest: 'Scopri i centri odontoiatrici con tariffe trasparenti vicino a te',
      headline_alert: '🦷 Tariffa esagerata? Prenota una prima visita di controllo con preventivo chiaro',
      ctaText: 'Prenota visita senza impegno',
      cta: 'Prenota visita senza impegno',
      url: 'https://www.dentalpro.it',
      badgeText: 'Cliniche Odontoiatriche Convenzionate',
      urgencyLevel: 'normal',
      secondaryPartnerName: 'Santagostino Odontoiatria',
      secondaryUrl: 'https://www.santagostino.it',
      discountCallout: 'Prima visita di controllo con piano di cura personalizzato',
    },
    highUrgency: {
      categoryId: 'dentista',
      partnerName: 'DentalPro',
      partner: 'DentalPro',
      headline: '🦷 Tariffa esagerata? Prenota una prima visita di controllo con preventivo chiaro',
      headline_honest: 'Scopri i centri odontoiatrici con tariffe trasparenti vicino a te',
      headline_alert: '🦷 Tariffa esagerata? Prenota una prima visita di controllo con preventivo chiaro',
      ctaText: 'Prenota prima visita senza impegno con piano di cura su DentalPro →',
      cta: 'Prenota visita senza impegno',
      url: 'https://www.dentalpro.it',
      badgeText: '🦷 TARIFFA DENTALE GONFIATA',
      urgencyLevel: 'high',
      secondaryPartnerName: 'Santagostino Odontoiatria',
      secondaryUrl: 'https://www.santagostino.it',
      discountCallout: 'Tariffario chiaro e bloccato senza sorprese',
    },
  },
  veterinario: {
    normal: {
      categoryId: 'veterinario',
      partnerName: 'Babydog Pet Insurance',
      partner: 'Babydog Pet Insurance',
      headline: "Proteggi la salute del tuo pet con un'assicurazione veterinaria",
      headline_honest: "Proteggi la salute del tuo pet con un'assicurazione veterinaria",
      headline_alert: '🐾 Evita salassi imprevisti dal veterinario: assicurazione completa da 9€/mese',
      ctaText: 'Calcola preventivo pet',
      cta: 'Calcola preventivo pet',
      url: 'https://www.babydog.it',
      badgeText: 'Assicurazione Sanitaria Pet',
      urgencyLevel: 'normal',
      secondaryPartnerName: 'Zooplus',
      secondaryUrl: 'https://www.zooplus.it',
      discountCallout: 'Copertura visite, interventi e farmaci veterinari',
    },
    highUrgency: {
      categoryId: 'veterinario',
      partnerName: 'Babydog Pet Insurance',
      partner: 'Babydog Pet Insurance',
      headline: '🐾 Evita salassi imprevisti dal veterinario: assicurazione completa da 9€/mese',
      headline_honest: "Proteggi la salute del tuo pet con un'assicurazione veterinaria",
      headline_alert: '🐾 Evita salassi imprevisti dal veterinario: assicurazione completa da 9€/mese',
      ctaText: "Rimborsa fino all'85% delle spese veterinarie con Babydog da 9€/mese →",
      cta: 'Calcola preventivo pet',
      url: 'https://www.babydog.it',
      badgeText: '🐾 PARCELLE VETERINARIE FOLLI',
      urgencyLevel: 'high',
      secondaryPartnerName: 'Zooplus',
      secondaryUrl: 'https://www.zooplus.it',
      discountCallout: "Rimborsi rapidi fino all'85% delle fatture veterinarie",
    },
  },
  cerimonie: {
    normal: {
      categoryId: 'cerimonie',
      partnerName: 'Matrimonio.com',
      partner: 'Matrimonio.com',
      headline: 'Organizza il tuo evento con i migliori fornitori recensiti',
      headline_honest: 'Organizza il tuo evento con i migliori fornitori recensiti',
      headline_alert: '💍 Nozze da sogno senza farsi dissanguare: confronta promozioni e sconti reali',
      ctaText: 'Trova fornitori scontati',
      cta: 'Trova fornitori scontati',
      url: 'https://www.matrimonio.com',
      badgeText: 'Leader Nozze ed Eventi in Italia',
      urgencyLevel: 'normal',
      secondaryPartnerName: 'Zankyou',
      secondaryUrl: 'https://www.zankyou.it',
      discountCallout: 'Sconti esclusivi fino al 20% su fotografi, abiti e location',
    },
    highUrgency: {
      categoryId: 'cerimonie',
      partnerName: 'Matrimonio.com',
      partner: 'Matrimonio.com',
      headline: '💍 Nozze da sogno senza farsi dissanguare: confronta promozioni e sconti reali',
      headline_honest: 'Organizza il tuo evento con i migliori fornitori recensiti',
      headline_alert: '💍 Nozze da sogno senza farsi dissanguare: confronta promozioni e sconti reali',
      ctaText: 'Confronta fornitori e ottieni lo sconto esclusivo su Matrimonio.com →',
      cta: 'Trova fornitori scontati',
      url: 'https://www.matrimonio.com',
      badgeText: '💍 PREZZI NOZZE DA RAPINA',
      urgencyLevel: 'high',
      secondaryPartnerName: 'Zankyou',
      secondaryUrl: 'https://www.zankyou.it',
      discountCallout: 'Non sprecare budget: blocca le offerte speciali prima che scadano',
    },
  },
  affitti: {
    normal: {
      categoryId: 'affitti',
      partnerName: 'SoloAffitti',
      partner: 'SoloAffitti',
      headline: 'Consulta annunci con canone verificato nella tua zona',
      headline_honest: 'Consulta annunci con canone verificato nella tua zona',
      headline_alert: '🔑 Canone troppo alto rispetto alla media? Calcola il canone concordato',
      ctaText: 'Verifica canone concordato',
      cta: 'Verifica canone concordato',
      url: 'https://www.soloaffitti.it',
      badgeText: 'Specialisti della Locazione Sicura',
      urgencyLevel: 'normal',
      secondaryPartnerName: 'Idealista',
      secondaryUrl: 'https://www.idealista.it',
      discountCallout: 'Contratti certificati a canone concordato con agevolazioni fiscali',
    },
    highUrgency: {
      categoryId: 'affitti',
      partnerName: 'SoloAffitti',
      partner: 'SoloAffitti',
      headline: '🔑 Canone troppo alto rispetto alla media? Calcola il canone concordato',
      headline_honest: 'Consulta annunci con canone verificato nella tua zona',
      headline_alert: '🔑 Canone troppo alto rispetto alla media? Calcola il canone concordato',
      ctaText: 'Calcola il canone concordato e trova affitti garantiti su SoloAffitti →',
      cta: 'Verifica canone concordato',
      url: 'https://www.soloaffitti.it',
      badgeText: '🔑 CANONE FUORI REGOLA',
      urgencyLevel: 'high',
      secondaryPartnerName: 'Idealista',
      secondaryUrl: 'https://www.idealista.it',
      discountCallout: 'Scopri se il proprietario ti sta chiedendo più del limite legale',
    },
  },
};

// Test compatibility alias
export const AFFILIATES = {
  auto: AFFILIATE_DIRECTORY.auto.normal,
  casa: AFFILIATE_DIRECTORY.casa.normal,
  dentista: AFFILIATE_DIRECTORY.dentista.normal,
  veterinario: AFFILIATE_DIRECTORY.veterinario.normal,
  cerimonie: AFFILIATE_DIRECTORY.cerimonie.normal,
  affitti: AFFILIATE_DIRECTORY.affitti.normal,
};

/**
 * Returns the contextual affiliate partner card for a given category,
 * dynamically selecting between normal and high-urgency alarm styling.
 */
export function getAffiliateForCategory(
  category: CategoryId | string,
  isOvercharged: boolean,
  provinceSigla?: string
): AffiliatePartner {
  const normalizedCategory = (category || '').toLowerCase() as CategoryId;
  const entry = AFFILIATE_DIRECTORY[normalizedCategory] || AFFILIATE_DIRECTORY.casa;
  const partnerConfig = isOvercharged ? entry.highUrgency : entry.normal;

  const result: AffiliatePartner = { ...partnerConfig };

  if (provinceSigla && provinceSigla.trim()) {
    const sigla = provinceSigla.toUpperCase().trim();
    const separator = result.url.includes('?') ? '&' : '?';
    result.url = `${result.url}${separator}prov=${sigla}`;
  }

  return result;
}

export function getAllAffiliates(): Record<CategoryId, AffiliateCategoryConfig> {
  return JSON.parse(JSON.stringify(AFFILIATE_DIRECTORY));
}

export function getPartnerNameForCategory(category: CategoryId | string): string {
  const normalized = (category || '').toLowerCase() as CategoryId;
  const entry = AFFILIATE_DIRECTORY[normalized] || AFFILIATE_DIRECTORY.casa;
  return entry.normal.partnerName;
}
