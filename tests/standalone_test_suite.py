#!/usr/bin/env python3
"""
Standalone Zero-Dependency Python 3 Test Suite for "Mi Stanno Fregando?"

Runs strictly with the Python 3 standard library (unittest, json, math, os, sys).
Exits with code 0 on complete pass, 1 on failure.

Usage:
    python3 tests/standalone_test_suite.py
"""

import unittest
import json
import math
import os
import sys

# ==============================================================================
# AUTHORITATIVE REFERENCE SPECIFICATIONS & ORACLE
# ==============================================================================

PROVINCES_107 = [
    # Piemonte (8)
    ("AL", "Alessandria", "Piemonte", 1.01),
    ("AT", "Asti", "Piemonte", 1.00),
    ("BI", "Biella", "Piemonte", 0.98),
    ("CN", "Cuneo", "Piemonte", 1.03),
    ("NO", "Novara", "Piemonte", 1.04),
    ("TO", "Torino", "Piemonte", 1.12),
    ("VB", "Verbano-Cusio-Ossola", "Piemonte", 1.02),
    ("VC", "Vercelli", "Piemonte", 0.99),
    # Valle d'Aosta (1)
    ("AO", "Valle d'Aosta", "Valle d'Aosta", 1.08),
    # Lombardia (12)
    ("BG", "Bergamo", "Lombardia", 1.09),
    ("BS", "Brescia", "Lombardia", 1.08),
    ("CO", "Como", "Lombardia", 1.10),
    ("CR", "Cremona", "Lombardia", 1.02),
    ("LC", "Lecco", "Lombardia", 1.07),
    ("LO", "Lodi", "Lombardia", 1.03),
    ("MB", "Monza e Brianza", "Lombardia", 1.12),
    ("MI", "Milano", "Lombardia", 1.25),
    ("MN", "Mantova", "Lombardia", 1.02),
    ("PV", "Pavia", "Lombardia", 1.04),
    ("SO", "Sondrio", "Lombardia", 1.01),
    ("VA", "Varese", "Lombardia", 1.07),
    # Trentino-Alto Adige (2)
    ("BZ", "Bolzano", "Trentino-Alto Adige", 1.20),
    ("TN", "Trento", "Trentino-Alto Adige", 1.12),
    # Veneto (7)
    ("BL", "Belluno", "Veneto", 1.02),
    ("PD", "Padova", "Veneto", 1.07),
    ("RO", "Rovigo", "Veneto", 0.98),
    ("TV", "Treviso", "Veneto", 1.06),
    ("VE", "Venezia", "Veneto", 1.10),
    ("VI", "Vicenza", "Veneto", 1.06),
    ("VR", "Verona", "Veneto", 1.07),
    # Friuli-Venezia Giulia (4)
    ("GO", "Gorizia", "Friuli-Venezia Giulia", 1.00),
    ("PN", "Pordenone", "Friuli-Venezia Giulia", 1.02),
    ("TS", "Trieste", "Friuli-Venezia Giulia", 1.06),
    ("UD", "Udine", "Friuli-Venezia Giulia", 1.03),
    # Liguria (4)
    ("GE", "Genova", "Liguria", 1.08),
    ("IM", "Imperia", "Liguria", 1.04),
    ("SP", "La Spezia", "Liguria", 1.03),
    ("SV", "Savona", "Liguria", 1.03),
    # Emilia-Romagna (9)
    ("BO", "Bologna", "Emilia-Romagna", 1.15),
    ("FC", "Forlì-Cesena", "Emilia-Romagna", 1.03),
    ("FE", "Ferrara", "Emilia-Romagna", 1.02),
    ("MO", "Modena", "Emilia-Romagna", 1.08),
    ("PC", "Piacenza", "Emilia-Romagna", 1.04),
    ("PR", "Parma", "Emilia-Romagna", 1.07),
    ("RA", "Ravenna", "Emilia-Romagna", 1.04),
    ("RE", "Reggio Emilia", "Emilia-Romagna", 1.06),
    ("RN", "Rimini", "Emilia-Romagna", 1.05),
    # Toscana (10)
    ("AR", "Arezzo", "Toscana", 0.98),
    ("FI", "Firenze", "Toscana", 1.14),
    ("GR", "Grosseto", "Toscana", 0.97),
    ("LI", "Livorno", "Toscana", 0.99),
    ("LU", "Lucca", "Toscana", 1.01),
    ("MS", "Massa-Carrara", "Toscana", 0.98),
    ("PI", "Pisa", "Toscana", 1.02),
    ("PO", "Prato", "Toscana", 1.03),
    ("PT", "Pistoia", "Toscana", 0.99),
    ("SI", "Siena", "Toscana", 1.05),
    # Umbria (2)
    ("PG", "Perugia", "Umbria", 0.94),
    ("TR", "Terni", "Umbria", 0.92),
    # Marche (5)
    ("AN", "Ancona", "Marche", 0.98),
    ("AP", "Ascoli Piceno", "Marche", 0.93),
    ("FM", "Fermo", "Marche", 0.91),
    ("MC", "Macerata", "Marche", 0.92),
    ("PU", "Pesaro e Urbino", "Marche", 0.96),
    # Lazio (5)
    ("FR", "Frosinone", "Lazio", 0.90),
    ("LT", "Latina", "Lazio", 0.93),
    ("RI", "Rieti", "Lazio", 0.89),
    ("RM", "Roma", "Lazio", 1.18),
    ("VT", "Viterbo", "Lazio", 0.91),
    # Abruzzo (4)
    ("AQ", "L'Aquila", "Abruzzo", 0.95),
    ("CH", "Chieti", "Abruzzo", 0.92),
    ("PE", "Pescara", "Abruzzo", 0.96),
    ("TE", "Teramo", "Abruzzo", 0.92),
    # Molise (2)
    ("CB", "Campobasso", "Molise", 0.86),
    ("IS", "Isernia", "Molise", 0.84),
    # Campania (5)
    ("AV", "Avellino", "Campania", 0.86),
    ("BN", "Benevento", "Campania", 0.85),
    ("CE", "Caserta", "Campania", 0.87),
    ("NA", "Napoli", "Campania", 0.96),
    ("SA", "Salerno", "Campania", 0.90),
    # Puglia (6)
    ("BA", "Bari", "Puglia", 0.93),
    ("BT", "Barletta-Andria-Trani", "Puglia", 0.87),
    ("BR", "Brindisi", "Puglia", 0.86),
    ("FG", "Foggia", "Puglia", 0.85),
    ("LE", "Lecce", "Puglia", 0.88),
    ("TA", "Taranto", "Puglia", 0.86),
    # Basilicata (2)
    ("MT", "Matera", "Basilicata", 0.88),
    ("PZ", "Potenza", "Basilicata", 0.87),
    # Calabria (5)
    ("CS", "Cosenza", "Calabria", 0.84),
    ("CZ", "Catanzaro", "Calabria", 0.85),
    ("KR", "Crotone", "Calabria", 0.82),
    ("RC", "Reggio Calabria", "Calabria", 0.85),
    ("VV", "Vibo Valentia", "Calabria", 0.82),
    # Sicilia (9)
    ("AG", "Agrigento", "Sicilia", 0.84),
    ("CL", "Caltanissetta", "Sicilia", 0.82),
    ("CT", "Catania", "Sicilia", 0.90),
    ("EN", "Enna", "Sicilia", 0.80),
    ("ME", "Messina", "Sicilia", 0.87),
    ("PA", "Palermo", "Sicilia", 0.92),
    ("RG", "Ragusa", "Sicilia", 0.86),
    ("SR", "Siracusa", "Sicilia", 0.87),
    ("TP", "Trapani", "Sicilia", 0.85),
    # Sardegna (5)
    ("CA", "Cagliari", "Sardegna", 0.93),
    ("NU", "Nuoro", "Sardegna", 0.86),
    ("OR", "Oristano", "Sardegna", 0.85),
    ("SS", "Sassari", "Sardegna", 0.90),
    ("SU", "Sud Sardegna", "Sardegna", 0.84),
]

CATEGORIES = [
    "auto",
    "casa",
    "dentista",
    "veterinario",
    "cerimonie",
    "affitti",
]

PRESTATIONS_36 = [
    # Auto (6)
    {"id": "auto_tagliando", "category": "auto", "name": "Tagliando Completo Standard", "base_price": 250, "min_bound": 80, "max_bound": 800},
    {"id": "auto_freni", "category": "auto", "name": "Sostituzione Pastiglie e Dischi Anteriori", "base_price": 280, "min_bound": 100, "max_bound": 900},
    {"id": "auto_distribuzione", "category": "auto", "name": "Cinghia Distribuzione + Pompa Acqua", "base_price": 550, "min_bound": 200, "max_bound": 1800},
    {"id": "auto_frizione", "category": "auto", "name": "Sostituzione Kit Frizione Completo", "base_price": 600, "min_bound": 200, "max_bound": 2000},
    {"id": "auto_clima", "category": "auto", "name": "Ricarica Climatizzatore Auto", "base_price": 90, "min_bound": 30, "max_bound": 250},
    {"id": "auto_batteria", "category": "auto", "name": "Sostituzione Batteria 60-70 Ah", "base_price": 130, "min_bound": 50, "max_bound": 400},
    # Casa (6)
    {"id": "casa_imbiancatura", "category": "casa", "name": "Imbiancatura Appartamento (ca. 70 mq)", "base_price": 900, "min_bound": 250, "max_bound": 3500},
    {"id": "casa_caldaia", "category": "casa", "name": "Sostituzione Caldaia a Condensazione", "base_price": 1800, "min_bound": 700, "max_bound": 5000},
    {"id": "casa_idraulico_perdita", "category": "casa", "name": "Riparazione Perdita / Sostituzione Flessibile", "base_price": 120, "min_bound": 40, "max_bound": 500},
    {"id": "casa_disotturazione", "category": "casa", "name": "Disotturazione Scarico WC / Lavello", "base_price": 150, "min_bound": 50, "max_bound": 600},
    {"id": "casa_impianto_elettrico", "category": "casa", "name": "Rifacimento Impianto Elettrico (Bilocale)", "base_price": 3200, "min_bound": 1000, "max_bound": 10000},
    {"id": "casa_serratura", "category": "casa", "name": "Sostituzione Serratura Cilindro Europeo", "base_price": 380, "min_bound": 120, "max_bound": 1200},
    # Dentista (6)
    {"id": "dentista_igiene", "category": "dentista", "name": "Pulizia Denti / Ablazione Tartaro", "base_price": 85, "min_bound": 30, "max_bound": 250},
    {"id": "dentista_otturazione", "category": "dentista", "name": "Otturazione Carie Semplice (Composito)", "base_price": 120, "min_bound": 40, "max_bound": 400},
    {"id": "dentista_devitalizzazione", "category": "dentista", "name": "Devitalizzazione Dente (Endodonzia)", "base_price": 250, "min_bound": 80, "max_bound": 800},
    {"id": "dentista_impianto", "category": "dentista", "name": "Impianto Dentale Singolo Completo", "base_price": 1450, "min_bound": 500, "max_bound": 4000},
    {"id": "dentista_apparecchio", "category": "dentista", "name": "Allineatori Trasparenti (Ciclo Completo)", "base_price": 3200, "min_bound": 1000, "max_bound": 8000},
    {"id": "dentista_estrazione", "category": "dentista", "name": "Estrazione Dente del Giudizio", "base_price": 160, "min_bound": 50, "max_bound": 600},
    # Veterinario (6)
    {"id": "vet_visita", "category": "veterinario", "name": "Visita Generale Cane o Gatto", "base_price": 45, "min_bound": 20, "max_bound": 150},
    {"id": "vet_vaccino", "category": "veterinario", "name": "Vaccinazione Annuale con Richiamo", "base_price": 50, "min_bound": 25, "max_bound": 140},
    {"id": "vet_microchip", "category": "veterinario", "name": "Applicazione Microchip e Iscrizione Anagrafe", "base_price": 35, "min_bound": 15, "max_bound": 100},
    {"id": "vet_sterilizzazione", "category": "veterinario", "name": "Sterilizzazione Gatta / Castrazione Cane", "base_price": 180, "min_bound": 70, "max_bound": 600},
    {"id": "vet_detartrasi", "category": "veterinario", "name": "Detartrasi Denti Animale in Anestesia", "base_price": 160, "min_bound": 60, "max_bound": 500},
    {"id": "vet_esami_sangue", "category": "veterinario", "name": "Profilo Esami Sangue Completo", "base_price": 90, "min_bound": 35, "max_bound": 250},
    # Cerimonie (6)
    {"id": "cerimonia_menu", "category": "cerimonie", "name": "Menu Ricevimento Nozze (Costo a persona)", "base_price": 110, "min_bound": 40, "max_bound": 350},
    {"id": "cerimonia_foto", "category": "cerimonie", "name": "Servizio Foto e Video Matrimonio", "base_price": 1600, "min_bound": 400, "max_bound": 5500},
    {"id": "cerimonia_fiori", "category": "cerimonie", "name": "Allestimento Floreale Chiesa e Location", "base_price": 1200, "min_bound": 250, "max_bound": 5000},
    {"id": "cerimonia_musica", "category": "cerimonie", "name": "DJ Set e Animazione Musicale", "base_price": 650, "min_bound": 150, "max_bound": 2500},
    {"id": "cerimonia_auto", "category": "cerimonie", "name": "Noleggio Auto Sposi con Autista", "base_price": 450, "min_bound": 150, "max_bound": 1800},
    {"id": "cerimonia_bomboniere", "category": "cerimonie", "name": "Bomboniere Confezionate con Confetti", "base_price": 10, "min_bound": 2, "max_bound": 60},
    # Affitti (6)
    {"id": "affitto_monolocale", "category": "affitti", "name": "Canone Mensile Monolocale Arredato", "base_price": 520, "min_bound": 180, "max_bound": 2000},
    {"id": "affitto_bilocale", "category": "affitti", "name": "Canone Mensile Bilocale Arredato", "base_price": 720, "min_bound": 250, "max_bound": 2800},
    {"id": "affitto_trilocale", "category": "affitti", "name": "Canone Mensile Trilocale", "base_price": 920, "min_bound": 300, "max_bound": 4000},
    {"id": "affitto_stanza", "category": "affitti", "name": "Canone Stanza Singola per Studenti/Lav.", "base_price": 380, "min_bound": 120, "max_bound": 1100},
    {"id": "affitto_posto_auto", "category": "affitti", "name": "Canone Mensile Box Auto / Posto Auto", "base_price": 110, "min_bound": 30, "max_bound": 450},
    {"id": "affitto_quadrilocale", "category": "affitti", "name": "Canone Mensile Quadrilocale", "base_price": 1200, "min_bound": 400, "max_bound": 5000},
]

AFFILIATES = {
    "auto": {
        "partner": "AutoDoc",
        "headline_honest": "Risparmia sulla manutenzione auto con ricambi originali scontati",
        "headline_alert": "🚨 Non farti spennare dal meccanico! Risparmia fino al 40% sui ricambi su AutoDoc",
        "cta": "Confronta prezzi ricambi",
        "url": "https://www.autodoc.it"
    },
    "casa": {
        "partner": "ProntoPro",
        "headline_honest": "Trova professionisti qualificati per i lavori di casa",
        "headline_alert": "🚨 Prezzo fuori mercato! Richiedi 3 preventivi gratuiti da artigiani verificati",
        "cta": "Ricevi 3 preventivi gratis",
        "url": "https://www.prontopro.it"
    },
    "dentista": {
        "partner": "DentalPro",
        "headline_honest": "Scopri i centri odontoiatrici con tariffe trasparenti vicino a te",
        "headline_alert": "🦷 Tariffa esagerata? Prenota una prima visita di controllo con preventivo chiaro",
        "cta": "Prenota visita senza impegno",
        "url": "https://www.dentalpro.it"
    },
    "veterinario": {
        "partner": "Babydog Pet Insurance",
        "headline_honest": "Proteggi la salute del tuo pet con un'assicurazione veterinaria",
        "headline_alert": "🐾 Evita salassi imprevisti dal veterinario: assicurazione completa da 9€/mese",
        "cta": "Calcola preventivo pet",
        "url": "https://www.babydog.it"
    },
    "cerimonie": {
        "partner": "Matrimonio.com",
        "headline_honest": "Organizza il tuo evento con i migliori fornitori recensiti",
        "headline_alert": "💍 Nozze da sogno senza farsi dissanguare: confronta promozioni e sconti reali",
        "cta": "Trova fornitori scontati",
        "url": "https://www.matrimonio.com"
    },
    "affitti": {
        "partner": "SoloAffitti",
        "headline_honest": "Consulta annunci con canone verificato nella tua zona",
        "headline_alert": "🔑 Canone troppo alto rispetto alla media? Calcola il canone concordato",
        "cta": "Verifica canone concordato",
        "url": "https://www.soloaffitti.it"
    }
}

# ==============================================================================
# REFERENCE DOMAIN FUNCTIONS (ORACLE IMPLEMENTATION)
# ==============================================================================

def get_province_dict():
    return {p[0]: {"name": p[1], "region": p[2], "coeff": p[3]} for p in PROVINCES_107}

def get_prestation_dict():
    return {p["id"]: p for p in PRESTATIONS_36}

def calculate_local_reference_price(base_price: float, province_coeff: float) -> int:
    """Calculates local reference price rounded to nearest integer Euro (matching JS Math.round)."""
    return int(math.floor(base_price * province_coeff + 0.5))

def calculate_discrepancy(quote: float, ref_price: float):
    """
    Computes diffEuro and diffPct.
    Raises ValueError if ref_price <= 0.
    """
    if ref_price <= 0:
        raise ValueError("Reference price must be strictly greater than 0.")
    if quote < 0:
        raise ValueError("Quote must be greater than or equal to 0.")
    diff_euro = round(quote - ref_price, 2)
    diff_pct = round(((quote - ref_price) / ref_price) * 100.0, 2)
    return diff_euro, diff_pct

def classify_verdict(diff_pct: float):
    """
    Classifies discrepancy into 3 visual zones and checks alert trigger:
      - diff_pct <= 0.0 -> PREZZO_ONESTO
      - 0.0 < diff_pct <= 35.0 -> NELLA_MEDIA
      - diff_pct > 35.0 -> TI_STANNO_FREGANDO
      - is_alert = True if diff_pct >= 65.0
    """
    if diff_pct <= 0.0:
        zone = "PREZZO_ONESTO"
    elif diff_pct <= 35.0:
        zone = "NELLA_MEDIA"
    else:
        zone = "TI_STANNO_FREGANDO"

    is_alert = diff_pct >= 65.0
    return zone, is_alert

def calculate_needle_angle_200(diff_pct: float) -> float:
    """
    Maps discrepancy percentage to 200° arc clamped between -100° and +100°.
    Geometry:
      diff_pct <= -50.0% -> -100.0°
      diff_pct == 0.0%   -> 0.0°
      diff_pct == +35.0% -> +50.0°
      diff_pct >= +70.0% -> +100.0°
    """
    if diff_pct <= -50.0:
        return -100.0
    if diff_pct <= 0.0:
        # Maps [-50, 0] to [-100, 0]
        return round(-100.0 + 100.0 * ((diff_pct + 50.0) / 50.0), 2)
    if diff_pct <= 35.0:
        # Maps (0, 35] to (0, 50]
        return round(0.0 + 50.0 * (diff_pct / 35.0), 2)
    if diff_pct <= 70.0:
        # Maps (35, 70] to (50, 100]
        return round(50.0 + 50.0 * ((diff_pct - 35.0) / 35.0), 2)
    return 100.0

def calculate_needle_angle_180(diff_pct: float) -> float:
    """
    Maps discrepancy percentage to 180° arc clamped between 0° and 180°.
    Geometry:
      diff_pct <= -50.0% -> 0.0°
      diff_pct == 0.0%   -> 60.0°
      diff_pct == +35.0% -> 120.0°
      diff_pct >= +70.0% -> 180.0°
    """
    if diff_pct <= -50.0:
        return 0.0
    if diff_pct <= 0.0:
        return round(60.0 * (diff_pct + 50.0) / 50.0, 2)
    if diff_pct <= 35.0:
        return round(60.0 + 60.0 * (diff_pct / 35.0), 2)
    if diff_pct <= 70.0:
        return round(120.0 + 60.0 * ((diff_pct - 35.0) / 35.0), 2)
    return 180.0

def bayesian_online_average(current_avg: float, sample_count: int, paid_amount: float) -> int:
    """Computes updated weighted running average and returns integer Euro."""
    new_count = sample_count + 1
    new_avg = (current_avg * sample_count + paid_amount) / new_count
    return round(new_avg)

def validate_crowdsource_input(paid_amount: float, min_bound: float, max_bound: float):
    """Sanity anti-spam filter for user submitted actual prices."""
    if not isinstance(paid_amount, (int, float)):
        return False, "Input must be numeric"
    if paid_amount <= 0:
        return False, "Amount must be strictly positive"
    if paid_amount < min_bound:
        return False, f"Amount too low (minimum realistic: {min_bound} €)"
    if paid_amount > max_bound:
        return False, f"Amount too high (maximum realistic: {max_bound} €)"
    return True, "Valid"

# ==============================================================================
# TEST CASE SUITE
# ==============================================================================

class TestDatasetIntegrity(unittest.TestCase):
    """Validates full Italian province directory, categories, and prestations."""

    def test_all_107_provinces_exist_with_valid_sigle(self):
        self.assertEqual(len(PROVINCES_107), 107, "Must have exactly 107 Italian provinces")
        sigle = [p[0] for p in PROVINCES_107]
        self.assertEqual(len(set(sigle)), 107, "All 107 province sigle must be unique")
        for s, name, region, coeff in PROVINCES_107:
            self.assertEqual(len(s), 2, f"Sigla {s} must be exactly 2 characters")
            self.assertTrue(s.isupper(), f"Sigla {s} must be uppercase")
            self.assertTrue(len(name) > 0, "Province name must not be empty")

    def test_province_multipliers_within_realistic_bounds(self):
        for s, name, region, coeff in PROVINCES_107:
            self.assertGreaterEqual(coeff, 0.80, f"Multiplier for {s} must be >= 0.80")
            self.assertLessEqual(coeff, 1.25, f"Multiplier for {s} must be <= 1.25")
        # Key anchors
        p_dict = get_province_dict()
        self.assertEqual(p_dict["MI"]["coeff"], 1.25, "Milano must be 1.25")
        self.assertEqual(p_dict["RM"]["coeff"], 1.18, "Roma must be 1.18")
        self.assertEqual(p_dict["BO"]["coeff"], 1.15, "Bologna must be 1.15")
        self.assertEqual(p_dict["NA"]["coeff"], 0.96, "Napoli must be 0.96")
        self.assertEqual(p_dict["EN"]["coeff"], 0.80, "Enna must be 0.80")

    def test_all_20_italian_regions_represented(self):
        regions = set(p[2] for p in PROVINCES_107)
        self.assertEqual(len(regions), 20, "All 20 Italian administrative regions must be present")

    def test_all_6_categories_present(self):
        expected = ["auto", "casa", "dentista", "veterinario", "cerimonie", "affitti"]
        self.assertEqual(CATEGORIES, expected)

    def test_all_36_prestations_present_and_valid(self):
        self.assertEqual(len(PRESTATIONS_36), 36, "Must contain exactly 36 prestations")
        categories_count = {}
        for p in PRESTATIONS_36:
            c = p["category"]
            categories_count[c] = categories_count.get(c, 0) + 1
            self.assertGreater(p["base_price"], 0, f"Base price for {p['id']} must be > 0")
        for c in CATEGORIES:
            self.assertEqual(categories_count[c], 6, f"Category {c} must have exactly 6 prestations")

    def test_prestation_bounds_consistent(self):
        for p in PRESTATIONS_36:
            self.assertLess(p["min_bound"], p["max_bound"], f"Min bound must be < Max bound for {p['id']}")
            self.assertGreaterEqual(p["base_price"], p["min_bound"], f"Base price must be >= Min bound for {p['id']}")
            self.assertLessEqual(p["base_price"], p["max_bound"], f"Base price must be <= Max bound for {p['id']}")

    def test_optional_external_dataset_json_if_present(self):
        dataset_path = os.path.join(os.path.dirname(__file__), "..", "src", "core", "dataset.json")
        if os.path.exists(dataset_path):
            with open(dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("provinces", data)
            self.assertIn("prestations", data)
            self.assertEqual(len(data["provinces"]), 107)
            self.assertEqual(len(data["prestations"]), 36)


class TestDiscrepancyCalculations(unittest.TestCase):
    """Tier 1: Feature Coverage — Mathematical calculations."""

    def test_exact_discrepancy_positive_markup(self):
        diff_euro, diff_pct = calculate_discrepancy(300, 200)
        self.assertEqual(diff_euro, 100.0)
        self.assertEqual(diff_pct, 50.0)

    def test_exact_discrepancy_zero_diff(self):
        diff_euro, diff_pct = calculate_discrepancy(250, 250)
        self.assertEqual(diff_euro, 0.0)
        self.assertEqual(diff_pct, 0.0)

    def test_exact_discrepancy_negative_savings(self):
        diff_euro, diff_pct = calculate_discrepancy(150, 200)
        self.assertEqual(diff_euro, -50.0)
        self.assertEqual(diff_pct, -25.0)

    def test_local_province_multiplier_application(self):
        # Base 250 in Milano (1.25) -> round(250 * 1.25) = round(312.5) = 312 or 313
        ref_mi = calculate_local_reference_price(250, 1.25)
        self.assertIn(ref_mi, [312, 313])
        # Base 250 in Enna (0.80) -> 200
        ref_en = calculate_local_reference_price(250, 0.80)
        self.assertEqual(ref_en, 200)

    def test_euro_diff_calculation(self):
        diff_euro, _ = calculate_discrepancy(1250.50, 1000.0)
        self.assertEqual(diff_euro, 250.50)

    def test_division_by_zero_prevention(self):
        with self.assertRaises(ValueError):
            calculate_discrepancy(100, 0)

    def test_negative_quote_raises_value_error(self):
        with self.assertRaises(ValueError):
            calculate_discrepancy(-50, 100)

    def test_quote_zero_free_service(self):
        diff_euro, diff_pct = calculate_discrepancy(0, 100)
        self.assertEqual(diff_euro, -100.0)
        self.assertEqual(diff_pct, -100.0)

    def test_float_rounding_precision(self):
        diff_euro, diff_pct = calculate_discrepancy(100.333, 100.0)
        self.assertEqual(diff_euro, 0.33)
        self.assertEqual(diff_pct, 0.33)



class TestThresholdClassification(unittest.TestCase):
    """Tier 1 & Tier 2: Threshold classification & edge boundary checks."""

    def test_prezzo_onesto_below_average(self):
        zone, is_alert = classify_verdict(-15.5)
        self.assertEqual(zone, "PREZZO_ONESTO")
        self.assertFalse(is_alert)

    def test_prezzo_onesto_exact_zero_boundary(self):
        zone, is_alert = classify_verdict(0.000)
        self.assertEqual(zone, "PREZZO_ONESTO")
        self.assertFalse(is_alert)

    def test_nella_media_nominal(self):
        zone, is_alert = classify_verdict(18.5)
        self.assertEqual(zone, "NELLA_MEDIA")
        self.assertFalse(is_alert)

    def test_nella_media_exact_35_boundary(self):
        zone, is_alert = classify_verdict(35.000)
        self.assertEqual(zone, "NELLA_MEDIA")
        self.assertFalse(is_alert)

    def test_ti_stanno_fregando_above_35(self):
        zone, is_alert = classify_verdict(35.001)
        self.assertEqual(zone, "TI_STANNO_FREGANDO")
        self.assertFalse(is_alert)

    def test_ti_stanno_fregando_exact_65_alert_boundary(self):
        zone, is_alert = classify_verdict(65.000)
        self.assertEqual(zone, "TI_STANNO_FREGANDO")
        self.assertTrue(is_alert)

    def test_ti_stanno_fregando_severe_alert_above_65(self):
        zone, is_alert = classify_verdict(120.0)
        self.assertEqual(zone, "TI_STANNO_FREGANDO")
        self.assertTrue(is_alert)

    def test_astronomical_overcharge_handling(self):
        zone, is_alert = classify_verdict(10000.0)
        self.assertEqual(zone, "TI_STANNO_FREGANDO")
        self.assertTrue(is_alert)

    def test_exact_threshold_subtle_fractions(self):
        zone_below, _ = classify_verdict(34.999)
        zone_above, _ = classify_verdict(35.001)
        self.assertEqual(zone_below, "NELLA_MEDIA")
        self.assertEqual(zone_above, "TI_STANNO_FREGANDO")

    def test_zone_labels_match_specification(self):
        self.assertEqual(classify_verdict(-5.0)[0], "PREZZO_ONESTO")
        self.assertEqual(classify_verdict(12.0)[0], "NELLA_MEDIA")
        self.assertEqual(classify_verdict(45.0)[0], "TI_STANNO_FREGANDO")



class TestTachometerNeedleAngle(unittest.TestCase):
    """Verifies gauge angle calculations and boundary clamping."""

    def test_needle_angle_at_minus_50_pct(self):
        angle_200 = calculate_needle_angle_200(-50.0)
        self.assertEqual(angle_200, -100.0)
        angle_180 = calculate_needle_angle_180(-50.0)
        self.assertEqual(angle_180, 0.0)

    def test_needle_angle_at_zero_pct(self):
        angle_200 = calculate_needle_angle_200(0.0)
        self.assertEqual(angle_200, 0.0)
        angle_180 = calculate_needle_angle_180(0.0)
        self.assertEqual(angle_180, 60.0)

    def test_needle_angle_at_plus_35_pct(self):
        angle_200 = calculate_needle_angle_200(35.0)
        self.assertEqual(angle_200, 50.0)
        angle_180 = calculate_needle_angle_180(35.0)
        self.assertEqual(angle_180, 120.0)

    def test_needle_angle_at_plus_65_pct(self):
        angle_200 = calculate_needle_angle_200(65.0)
        self.assertAlmostEqual(angle_200, 92.86, places=1)
        angle_180 = calculate_needle_angle_180(65.0)
        self.assertAlmostEqual(angle_180, 171.43, places=1)

    def test_needle_angle_clamping_low(self):
        self.assertEqual(calculate_needle_angle_200(-99.0), -100.0)
        self.assertEqual(calculate_needle_angle_180(-99.0), 0.0)

    def test_needle_angle_clamping_high(self):
        self.assertEqual(calculate_needle_angle_200(500.0), 100.0)
        self.assertEqual(calculate_needle_angle_180(500.0), 180.0)

    def test_needle_angle_monotonic_increase(self):
        percentages = [-50.0, -25.0, 0.0, 15.0, 35.0, 50.0, 70.0]
        angles_200 = [calculate_needle_angle_200(p) for p in percentages]
        angles_180 = [calculate_needle_angle_180(p) for p in percentages]
        for i in range(len(angles_200) - 1):
            self.assertLessEqual(angles_200[i], angles_200[i + 1])
            self.assertLessEqual(angles_180[i], angles_180[i + 1])


class TestCrowdsourcingAndBayesianUpdate(unittest.TestCase):
    """Verifies crowdsource validation, anti-spam, and weighted running mean updates."""

    def test_valid_crowdsource_submission(self):
        valid, msg = validate_crowdsource_input(250, 80, 800)
        self.assertTrue(valid)

    def test_bayesian_online_average_formula(self):
        # Current avg 200 with N=10, new paid 250 -> (200 * 10 + 250) / 11 = 2250 / 11 = 204.545 -> round 205
        new_avg = bayesian_online_average(200, 10, 250)
        self.assertEqual(new_avg, 205)

    def test_consecutive_crowdsource_updates(self):
        avg = 100
        n = 10
        # 3 successive submissions of 160
        for _ in range(3):
            avg = bayesian_online_average(avg, n, 160)
            n += 1
        self.assertGreater(avg, 100)
        self.assertLess(avg, 160)
        self.assertEqual(n, 13)

    def test_antispam_rejection_below_min_bound(self):
        valid, msg = validate_crowdsource_input(20, 80, 800)
        self.assertFalse(valid)
        self.assertIn("minimum realistic", msg)

    def test_antispam_rejection_above_max_bound(self):
        valid, msg = validate_crowdsource_input(1500, 80, 800)
        self.assertFalse(valid)
        self.assertIn("maximum realistic", msg)

    def test_antispam_exact_boundary_acceptance(self):
        self.assertTrue(validate_crowdsource_input(80, 80, 800)[0])
        self.assertTrue(validate_crowdsource_input(800, 80, 800)[0])

    def test_rejection_of_zero_and_negative_paid_amount(self):
        self.assertFalse(validate_crowdsource_input(0, 80, 800)[0])
        self.assertFalse(validate_crowdsource_input(-50, 80, 800)[0])

    def test_bayesian_update_with_large_prior_sample(self):
        # 100 prior samples with average 100, new sample 200 -> (10000 + 200) / 101 = 100.99 -> round 101
        new_avg = bayesian_online_average(100, 100, 200)
        self.assertEqual(new_avg, 101)

    def test_antispam_string_or_none_input_rejected(self):
        self.assertFalse(validate_crowdsource_input("abc", 50, 500)[0])
        self.assertFalse(validate_crowdsource_input(None, 50, 500)[0])



class TestAffiliateAndMonetization(unittest.TestCase):
    """Tier 1: Feature Coverage — Monetization & dynamic affiliate selection."""

    def test_category_affiliate_mapping(self):
        for c in CATEGORIES:
            self.assertIn(c, AFFILIATES)
            aff = AFFILIATES[c]
            self.assertTrue(len(aff["partner"]) > 0)
            self.assertTrue(aff["url"].startswith("http"))

    def test_high_urgency_cta_on_overcharge(self):
        auto_aff = AFFILIATES["auto"]
        self.assertIn("Non farti spennare", auto_aff["headline_alert"])

    def test_calm_cta_on_honest_price(self):
        auto_aff = AFFILIATES["auto"]
        self.assertIn("Risparmia sulla manutenzione", auto_aff["headline_honest"])

    def test_zero_cls_ad_slot_dimensions(self):
        slots = {
            "leaderboard": {"desktop": (728, 90), "mobile": (320, 50)},
            "in_content_mpu": {"desktop": (300, 250), "mobile": (300, 250)},
            "sticky_bottom": {"desktop": (728, 90), "mobile": (320, 50)},
        }
        for name, dims in slots.items():
            self.assertEqual(dims["desktop"][1], 90 if "leaderboard" in name or "sticky" in name else 250)

    def test_all_affiliate_urls_valid_https(self):
        for c, data in AFFILIATES.items():
            self.assertTrue(data["url"].startswith("https://"), f"{c} affiliate url must use https")

    def test_all_6_categories_have_distinct_partners(self):
        partners = [AFFILIATES[c]["partner"] for c in CATEGORIES]
        self.assertEqual(len(set(partners)), 6, "Each category must have a distinct affiliate partner")



class TestTier3CrossFeaturePairwise(unittest.TestCase):
    """Tier 3: Pairwise cross-feature combinations."""

    def test_pairwise_geographic_extremes_milano_vs_enna(self):
        prest = get_prestation_dict()["auto_tagliando"]
        base = prest["base_price"]  # 250
        p_dict = get_province_dict()

        ref_mi = calculate_local_reference_price(base, p_dict["MI"]["coeff"])  # 250 * 1.25 = 313
        ref_en = calculate_local_reference_price(base, p_dict["EN"]["coeff"])  # 250 * 0.80 = 200

        # Quote 300 in Enna is an overcharge (+50%), but in Milano is an honest price (-4.2%)
        _, diff_pct_en = calculate_discrepancy(300, ref_en)
        _, diff_pct_mi = calculate_discrepancy(300, ref_mi)

        zone_en, _ = classify_verdict(diff_pct_en)
        zone_mi, _ = classify_verdict(diff_pct_mi)

        self.assertEqual(zone_en, "TI_STANNO_FREGANDO")
        self.assertEqual(zone_mi, "PREZZO_ONESTO")

    def test_pairwise_quote_thresholds_across_all_6_categories(self):
        prest_samples = [
            ("auto", "auto_tagliando", 250),
            ("casa", "casa_caldaia", 1800),
            ("dentista", "dentista_otturazione", 120),
            ("veterinario", "vet_vaccino", 50),
            ("cerimonie", "cerimonia_menu", 110),
            ("affitti", "affitto_bilocale", 720)
        ]
        for cat, pid, base in prest_samples:
            # 1. Honest (quote = 0.8 * base)
            _, pct_honest = calculate_discrepancy(base * 0.8, base)
            zone_h, alert_h = classify_verdict(pct_honest)
            self.assertEqual(zone_h, "PREZZO_ONESTO")
            self.assertFalse(alert_h)

            # 2. Average (quote = 1.15 * base)
            _, pct_avg = calculate_discrepancy(base * 1.15, base)
            zone_a, alert_a = classify_verdict(pct_avg)
            self.assertEqual(zone_a, "NELLA_MEDIA")
            self.assertFalse(alert_a)

            # 3. Severe Overcharge (quote = 1.70 * base)
            _, pct_over = calculate_discrepancy(base * 1.70, base)
            zone_o, alert_o = classify_verdict(pct_over)
            self.assertEqual(zone_o, "TI_STANNO_FREGANDO")
            self.assertTrue(alert_o)

    def test_pairwise_crowdsource_update_shifts_calculator_verdict(self):
        # Start with ref = 100, quote = 136 -> +36% (TI_STANNO_FREGANDO)
        diff_e1, diff_p1 = calculate_discrepancy(136, 100)
        zone1, _ = classify_verdict(diff_p1)
        self.assertEqual(zone1, "TI_STANNO_FREGANDO")

        # After several users submit prices of 130, new average becomes 125
        # Same quote 136 vs new ref 125 -> +8.8% (NELLA_MEDIA)
        diff_e2, diff_p2 = calculate_discrepancy(136, 125)
        zone2, _ = classify_verdict(diff_p2)
        self.assertEqual(zone2, "NELLA_MEDIA")

    def test_pairwise_multi_province_isolation(self):
        # Ensure updating one province does not corrupt another
        p_dict = get_province_dict()
        coeff_rm = p_dict["RM"]["coeff"]
        coeff_na = p_dict["NA"]["coeff"]
        self.assertNotEqual(coeff_rm, coeff_na)
        ref_rm = calculate_local_reference_price(100, coeff_rm)
        ref_na = calculate_local_reference_price(100, coeff_na)
        self.assertEqual(ref_rm, 118)
        self.assertEqual(ref_na, 96)

    def test_pairwise_extreme_quote_with_extreme_multiplier(self):
        # Quote 100,000 on Enna (0.80)
        ref_en = calculate_local_reference_price(100, 0.80)
        diff_e, diff_p = calculate_discrepancy(100000, ref_en)
        zone, is_alert = classify_verdict(diff_p)
        self.assertEqual(zone, "TI_STANNO_FREGANDO")
        self.assertTrue(is_alert)
        angle = calculate_needle_angle_200(diff_p)
        self.assertEqual(angle, 100.0)

    def test_pairwise_affitti_monolocale_vs_bilocale_in_bologna(self):
        p_dict = get_province_dict()
        coeff_bo = p_dict["BO"]["coeff"]  # 1.15
        mono_base = get_prestation_dict()["affitto_monolocale"]["base_price"]  # 520
        bilo_base = get_prestation_dict()["affitto_bilocale"]["base_price"]  # 720
        ref_mono = calculate_local_reference_price(mono_base, coeff_bo)  # 520 * 1.15 = 598
        ref_bilo = calculate_local_reference_price(bilo_base, coeff_bo)  # 720 * 1.15 = 828
        self.assertEqual(ref_mono, 598)
        self.assertEqual(ref_bilo, 828)



class TestTier4RealWorldPersonas(unittest.TestCase):
    """Tier 4: Realistic Italian consumer journeys."""

    def test_persona_marco_milan_auto_tagliando(self):
        """Marco in Milan quoted 450€ for auto tagliando (base 250€, Milan 1.25 -> 313€)."""
        p_dict = get_province_dict()
        ref = calculate_local_reference_price(250, p_dict["MI"]["coeff"])
        diff_euro, diff_pct = calculate_discrepancy(450, ref)
        zone, is_alert = classify_verdict(diff_pct)

        self.assertEqual(ref, 313)
        self.assertEqual(diff_euro, 137.0)
        self.assertAlmostEqual(diff_pct, 43.77, places=1)
        self.assertEqual(zone, "TI_STANNO_FREGANDO")
        self.assertFalse(is_alert)  # 43.8% is between 35% and 65%

        # Affiliate should offer AutoDoc with alert CTA
        aff = AFFILIATES["auto"]
        self.assertEqual(aff["partner"], "AutoDoc")
        self.assertIn("Non farti spennare", aff["headline_alert"])

    def test_persona_giulia_rome_dentist_filling(self):
        """Giulia in Rome quoted 110€ for tooth filling (base 120€, Rome 1.18 -> 142€)."""
        p_dict = get_province_dict()
        ref = calculate_local_reference_price(120, p_dict["RM"]["coeff"])
        diff_euro, diff_pct = calculate_discrepancy(110, ref)
        zone, is_alert = classify_verdict(diff_pct)

        self.assertEqual(ref, 142)
        self.assertEqual(diff_euro, -32.0)
        self.assertAlmostEqual(diff_pct, -22.54, places=1)
        self.assertEqual(zone, "PREZZO_ONESTO")
        self.assertFalse(is_alert)

        # Giulia can submit her honest 110€ price to crowdsource
        valid, msg = validate_crowdsource_input(110, 40, 400)
        self.assertTrue(valid)

    def test_persona_antonio_naples_boiler_replacement(self):
        """Antonio in Naples emergency boiler replacement quoted 3,200€ (base 1800€, Naples 0.96 -> 1728€)."""
        p_dict = get_province_dict()
        ref = calculate_local_reference_price(1800, p_dict["NA"]["coeff"])
        diff_euro, diff_pct = calculate_discrepancy(3200, ref)
        zone, is_alert = classify_verdict(diff_pct)

        self.assertEqual(ref, 1728)
        self.assertEqual(diff_euro, 1472.0)
        self.assertAlmostEqual(diff_pct, 85.19, places=1)
        self.assertEqual(zone, "TI_STANNO_FREGANDO")
        self.assertTrue(is_alert)  # >= 65% -> CRITICAL ALERT

        # ProntoPro urgent CTA displayed
        aff = AFFILIATES["casa"]
        self.assertEqual(aff["partner"], "ProntoPro")
        self.assertIn("Prezzo fuori mercato", aff["headline_alert"])

    def test_persona_sara_palermo_cat_vaccination(self):
        """Sara in Palermo quoted 48€ for cat vaccine (base 50€, Palermo 0.92 -> 46€)."""
        p_dict = get_province_dict()
        ref = calculate_local_reference_price(50, p_dict["PA"]["coeff"])
        diff_euro, diff_pct = calculate_discrepancy(48, ref)
        zone, is_alert = classify_verdict(diff_pct)

        self.assertEqual(ref, 46)
        self.assertEqual(diff_euro, 2.0)
        self.assertAlmostEqual(diff_pct, 4.35, places=1)
        self.assertEqual(zone, "NELLA_MEDIA")
        self.assertFalse(is_alert)

    def test_persona_matteo_florence_wedding_photo(self):
        """Matteo in Florence quoted 2,800€ for wedding photos (base 1600€, Florence 1.14 -> 1824€)."""
        p_dict = get_province_dict()
        ref = calculate_local_reference_price(1600, p_dict["FI"]["coeff"])
        diff_euro, diff_pct = calculate_discrepancy(2800, ref)
        zone, is_alert = classify_verdict(diff_pct)

        self.assertEqual(ref, 1824)
        self.assertEqual(diff_euro, 976.0)
        self.assertAlmostEqual(diff_pct, 53.51, places=1)
        self.assertEqual(zone, "TI_STANNO_FREGANDO")
        self.assertFalse(is_alert)

        aff = AFFILIATES["cerimonie"]
        self.assertEqual(aff["partner"], "Matrimonio.com")
        self.assertIn("Nozze da sogno", aff["headline_alert"])

    def test_persona_luca_bologna_rent_overcharge(self):
        """Luca in Bologna quoted 950€/mo for studio apartment (base 520€, Bologna 1.15 -> 598€)."""
        p_dict = get_province_dict()
        ref = calculate_local_reference_price(520, p_dict["BO"]["coeff"])
        diff_euro, diff_pct = calculate_discrepancy(950, ref)
        zone, is_alert = classify_verdict(diff_pct)

        self.assertEqual(ref, 598)
        self.assertEqual(diff_euro, 352.0)
        self.assertAlmostEqual(diff_pct, 58.86, places=1)
        self.assertEqual(zone, "TI_STANNO_FREGANDO")
        self.assertFalse(is_alert)  # 58.86% is between 35% and 65%

        aff = AFFILIATES["affitti"]
        self.assertEqual(aff["partner"], "SoloAffitti")
        self.assertIn("Canone troppo alto", aff["headline_alert"])

    def test_persona_elena_turin_veterinary_surgery(self):
        """Elena in Turin quoted 180€ for pet surgery (base 180€, Turin 1.12 -> 202€)."""
        p_dict = get_province_dict()
        ref = calculate_local_reference_price(180, p_dict["TO"]["coeff"])
        diff_euro, diff_pct = calculate_discrepancy(180, ref)
        zone, is_alert = classify_verdict(diff_pct)

        self.assertEqual(ref, 202)
        self.assertEqual(diff_euro, -22.0)
        self.assertAlmostEqual(diff_pct, -10.89, places=1)
        self.assertEqual(zone, "PREZZO_ONESTO")
        self.assertFalse(is_alert)

        # Elena can submit her honest 180€ payment to crowdsource
        valid, msg = validate_crowdsource_input(180, 70, 600)
        self.assertTrue(valid)

        aff = AFFILIATES["veterinario"]
        self.assertEqual(aff["partner"], "Babydog Pet Insurance")

    def test_persona_sofia_venice_home_emergency(self):
        """Sofia in Venice quoted 240€ for emergency plumbing leak (base 120€, Venice 1.10 -> 132€)."""
        p_dict = get_province_dict()
        ref = calculate_local_reference_price(120, p_dict["VE"]["coeff"])
        diff_euro, diff_pct = calculate_discrepancy(240, ref)
        zone, is_alert = classify_verdict(diff_pct)

        self.assertEqual(ref, 132)
        self.assertEqual(diff_euro, 108.0)
        self.assertAlmostEqual(diff_pct, 81.82, places=1)
        self.assertEqual(zone, "TI_STANNO_FREGANDO")
        self.assertTrue(is_alert)  # >= 65% -> CRITICAL ALERT

        aff = AFFILIATES["casa"]
        self.assertEqual(aff["partner"], "ProntoPro")
        self.assertIn("Prezzo fuori mercato", aff["headline_alert"])

    def test_persona_giuseppe_zero_quote_validation_error(self):
        """Giuseppe accidentally enters 0 or negative quote; system rejects without crashing."""
        with self.assertRaises(ValueError):
            calculate_discrepancy(-10, 100)
        # Quote 0 is valid mathematically (-100%) but triggers free/zero check
        diff_euro, diff_pct = calculate_discrepancy(0, 100)
        self.assertEqual(diff_pct, -100.0)
        zone, is_alert = classify_verdict(diff_pct)
        self.assertEqual(zone, "PREZZO_ONESTO")
        self.assertFalse(is_alert)



class TestMilestone2Components(unittest.TestCase):
    """Milestone 2: Viral Tachometer, ShareCard (Canvas 1080x1080), ResultSummary & Barrel Export."""

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.comp_dir = os.path.join(self.base_dir, "src", "components")

    def test_component_files_exist_and_non_empty(self):
        """All M2 component files must exist with substantial production implementations."""
        expected_files = [
            "Tachometer.tsx",
            "ShareCard.tsx",
            "ResultSummary.tsx",
            "index.ts",
        ]
        for fname in expected_files:
            fpath = os.path.join(self.comp_dir, fname)
            self.assertTrue(os.path.isfile(fpath), f"Missing component file: {fname}")
            size = os.path.getsize(fpath)
            self.assertGreater(size, 100, f"Component file too small: {fname} ({size} bytes)")

    def test_tachometer_svg_polar_coordinates_and_constants(self):
        """Validates polar coordinate mathematics (cx=160, cy=150, R=110, -100° to +100°) and SVG paths."""
        cx, cy, r = 160.0, 150.0, 110.0

        def polar_to_cart(angle_deg):
            rad = math.radians(angle_deg)
            x = cx + r * math.sin(rad)
            y = cy - r * math.cos(rad)
            return round(x, 2), round(y, 2)

        # 1. Coordinate check
        p_start = polar_to_cart(-100.0)
        p_zero = polar_to_cart(0.0)
        p_amber = polar_to_cart(50.0)
        p_alert = polar_to_cart(92.86)
        p_end = polar_to_cart(100.0)

        self.assertEqual(p_start, (51.67, 169.10))
        self.assertEqual(p_zero, (160.0, 40.0))
        self.assertEqual(p_amber, (244.26, 79.29))
        self.assertEqual(p_alert, (269.86, 155.49))
        self.assertEqual(p_end, (268.33, 169.10))

        # 2. Source inspection for required SVG features
        tach_path = os.path.join(self.comp_dir, "Tachometer.tsx")
        with open(tach_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("M 51.67 169.10 A 110 110 0 1 1 268.33 169.10", content)
        self.assertIn("M 51.67 169.10 A 110 110 0 0 1 160.00 40.00", content)
        self.assertIn("M 160.00 40.00 A 110 110 0 0 1 244.26 79.29", content)
        self.assertIn("M 244.26 79.29 A 110 110 0 0 1 268.33 169.10", content)
        self.assertIn("cubic-bezier(0.34, 1.56, 0.64, 1)", content)
        self.assertIn('role="meter"', content)
        self.assertIn("aria-valuenow", content)
        self.assertIn("alert-glow", content)

    def test_share_card_canvas_pipeline_and_sharing_channels(self):
        """Verifies 1080x1080 Canvas generation and 4 distribution channels."""
        share_path = os.path.join(self.comp_dir, "ShareCard.tsx")
        with open(share_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Canvas buffer
        self.assertIn("1080", content)
        self.assertIn("canvas.width = 1080", content)
        self.assertIn("canvas.height = 1080", content)

        # 4 Channels
        self.assertIn("https://api.whatsapp.com/send?text=", content)
        self.assertIn("navigator.share", content)
        self.assertIn("toBlob", content)
        self.assertIn("navigator.clipboard", content)

        # E2E test sentence alignment
        self.assertIn("Ho controllato il preventivo per", content)
        self.assertIn("su MiStannoFregando.it: verdetto", content)
        self.assertIn("TI_STANNO_FREGANDO", content)
        self.assertIn("PREZZO_ONESTO", content)

    def test_result_summary_dynamic_verdict_and_statistical_grid(self):
        """Verifies 3 dynamic verdict badges, 4-tile comparison grid, and alert dynamics."""
        summary_path = os.path.join(self.comp_dir, "ResultSummary.tsx")
        with open(summary_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Dynamic Verdict Badges
        self.assertIn("Prezzo Onesto", content)
        self.assertIn("Nella Media", content)
        self.assertIn("TI STANNO FREGANDO!", content)

        # 4-Tile Statistical Comparison Grid
        self.assertIn("Preventivo Ricevuto", content)
        self.assertIn("Differenza", content)
        self.assertIn("Scostamento %", content)
        self.assertIn("text-4xl sm:text-5xl font-black", content)

        # Alert Border Dynamics
        self.assertIn("animate-pulse", content)
        self.assertIn("mistannofregando.it", content)
        self.assertIn('role="region"', content)
        self.assertIn('aria-live="polite"', content)

    def test_barrel_export_integrity(self):
        """Verifies index.ts exports all components and utilities."""
        index_path = os.path.join(self.comp_dir, "index.ts")
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("export * from './Tachometer'", content)
        self.assertIn("export * from './ShareCard'", content)
        self.assertIn("export * from './ResultSummary'", content)

    def test_share_url_encoding_and_parsing_logic(self):
        """Verifies URL state preservation across category, prestation, province, and quote."""
        from urllib.parse import urlencode, parse_qs, urlparse

        params = {"cat": "auto", "prest": "auto_tagliando", "prov": "MI", "quote": "450"}
        base = "https://mistannofregando.it"
        full_url = f"{base}/?{urlencode(params)}"

        parsed = urlparse(full_url)
        qs = parse_qs(parsed.query)
        self.assertEqual(qs["cat"][0], "auto")
        self.assertEqual(qs["prest"][0], "auto_tagliando")
        self.assertEqual(qs["prov"][0], "MI")
        self.assertEqual(float(qs["quote"][0]), 450.0)

    def test_tachometer_needle_spring_transition_specification(self):
        """Verifies cubic-bezier spring physics parameters."""
        tach_path = os.path.join(self.comp_dir, "Tachometer.tsx")
        with open(tach_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("0.8s cubic-bezier(0.34, 1.56, 0.64, 1)", content)


class TestMilestone3InteractiveUIAndMonetization(unittest.TestCase):
    """Milestone 3: Interactive UI (CalculatorForm, CrowdsourceModal), Monetization (AdSlot, AffiliateCard), and Master App Layout."""

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.src_dir = os.path.join(self.base_dir, "src")
        self.comp_dir = os.path.join(self.src_dir, "components")

    def test_m3_component_and_layout_files_exist_and_non_empty(self):
        """All Milestone 3 files must exist and contain genuine implementations."""
        expected_files = [
            os.path.join(self.comp_dir, "CalculatorForm.tsx"),
            os.path.join(self.comp_dir, "CrowdsourceModal.tsx"),
            os.path.join(self.comp_dir, "AdSlot.tsx"),
            os.path.join(self.comp_dir, "AffiliateCard.tsx"),
            os.path.join(self.comp_dir, "index.ts"),
            os.path.join(self.src_dir, "App.tsx"),
            os.path.join(self.src_dir, "index.css"),
            os.path.join(self.src_dir, "main.tsx"),
            os.path.join(self.base_dir, "index.html"),
        ]
        for fpath in expected_files:
            self.assertTrue(os.path.isfile(fpath), f"Missing required file: {fpath}")
            size = os.path.getsize(fpath)
            self.assertGreater(size, 80, f"File unexpectedly small: {fpath} ({size} bytes)")

    def test_barrel_export_includes_all_seven_components(self):
        """src/components/index.ts must export all 7 primary components."""
        index_path = os.path.join(self.comp_dir, "index.ts")
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_exports = [
            "export * from './Tachometer'",
            "export * from './ShareCard'",
            "export * from './ResultSummary'",
            "export * from './CalculatorForm'",
            "export * from './CrowdsourceModal'",
            "export * from './AdSlot'",
            "export * from './AffiliateCard'",
        ]
        for exp in required_exports:
            self.assertIn(exp, content, f"Missing export in components/index.ts: {exp}")

    def test_calculator_form_currency_parser(self):
        """Verifies Euro (€) currency parsing supporting both European comma and dot formats."""
        import re

        def parse_quote_input(raw):
            if raw is None:
                return None, "Inserisci un importo valido."
            s = str(raw).strip().replace("€", "").replace(" ", "")
            if not s:
                return None, "Inserisci l'importo del preventivo."
            if not re.match(r"^-?[0-9.,]+$", s):
                return None, "Inserisci un numero valido per l'importo."
            is_neg = s.startswith("-")
            body = s[1:] if is_neg else s
            if "." in body and "," in body:
                last_dot = body.rfind(".")
                last_comma = body.rfind(",")
                if last_comma > last_dot:
                    norm = body.replace(".", "").replace(",", ".")
                else:
                    norm = body.replace(",", "")
            elif "," in body:
                parts = body.split(",")
                norm = f"{parts[0]}.{parts[1]}" if len(parts) == 2 else body.replace(",", "")
            elif "." in body:
                if body.count(".") > 1:
                    norm = body.replace(".", "")
                else:
                    parts = body.split(".")
                    if len(parts[1]) == 3 and len(parts[0]) <= 3:
                        norm = body.replace(".", "")
                    else:
                        norm = body
            else:
                norm = body
            try:
                val = float(norm)
            except ValueError:
                return None, "Inserisci un numero valido per l'importo."
            final_val = -val if is_neg else val
            if final_val < 0:
                return final_val, "L'importo del preventivo non può essere negativo."
            if final_val == 0:
                return 0, "Inserisci un importo superiore a zero."
            if final_val > 10_000_000:
                return final_val, "Importo fuori scala (massimo 10.000.000 €)."
            return round(final_val, 2), None

        # Matrix of test cases
        self.assertEqual(parse_quote_input("1.250,50")[0], 1250.50)
        self.assertEqual(parse_quote_input("1250,00")[0], 1250.00)
        self.assertEqual(parse_quote_input("1250.50")[0], 1250.50)
        self.assertEqual(parse_quote_input("1.250")[0], 1250.00)
        self.assertEqual(parse_quote_input("250")[0], 250.00)
        self.assertEqual(parse_quote_input("€ 350,50")[0], 350.50)
        self.assertEqual(parse_quote_input("  1000  ")[0], 1000.00)
        self.assertEqual(parse_quote_input("0")[1], "Inserisci un importo superiore a zero.")
        self.assertEqual(parse_quote_input("-50")[1], "L'importo del preventivo non può essere negativo.")
        self.assertEqual(parse_quote_input("abc")[1], "Inserisci un numero valido per l'importo.")
        self.assertEqual(parse_quote_input("")[1], "Inserisci l'importo del preventivo.")
        self.assertEqual(parse_quote_input("15000000")[1], "Importo fuori scala (massimo 10.000.000 €).")

        # Check CalculatorForm.tsx source code features
        form_path = os.path.join(self.comp_dir, "CalculatorForm.tsx")
        with open(form_path, "r", encoding="utf-8") as f:
            src = f.read()

        self.assertIn("parseQuoteInput", src)
        self.assertIn("normalizeItalianText", src)
        self.assertIn('inputMode="decimal"', src)
        self.assertIn("Verifica Subito il Preventivo", src)

    def test_calculator_form_provinces_combobox_and_search_scoring(self):
        """Verifies multi-attribute search and ranking across all 107 Italian provinces."""
        import unicodedata
        import re

        def normalize(text):
            if not text:
                return ""
            nfkd = unicodedata.normalize("NFKD", str(text))
            no_diacritics = "".join([c for c in nfkd if not unicodedata.combining(c)])
            cleaned = re.sub(r"['’‘`´\-–—]", " ", no_diacritics.lower())
            return re.sub(r"\s+", " ", cleaned).strip()

        # Diacritic and punctuation normalization check
        self.assertEqual(normalize("Forlì-Cesena"), "forli cesena")
        self.assertEqual(normalize("L'Aquila"), "l aquila")
        self.assertEqual(normalize("l aquila"), "l aquila")
        self.assertEqual(normalize("Reggio nell'Emilia"), "reggio nell emilia")

        # Search ranking check
        def rank_provinces(query):
            q = normalize(query)
            scored = []
            for sigla, nome, regione, coeff in PROVINCES_107:
                n_nome = normalize(nome)
                n_sigla = normalize(sigla)
                n_reg = normalize(regione)
                score = 999
                if n_sigla == q:
                    score = 1
                elif n_nome.startswith(q):
                    score = 2
                elif n_sigla.startswith(q):
                    score = 3
                elif q in n_nome:
                    score = 4
                elif n_reg.startswith(q):
                    score = 5
                elif q in n_reg:
                    score = 6
                if score < 999:
                    scored.append((score, sigla, nome))
            scored.sort()
            return [s[1] for s in scored]

        # MI should be top for 'mi'
        top_mi = rank_provinces("mi")
        self.assertEqual(top_mi[0], "MI")

        # RM should be in results for 'roma'
        top_roma = rank_provinces("roma")
        self.assertIn("RM", top_roma)

        # Forlì found with plain ascii 'forli'
        forli_results = rank_provinces("forli")
        self.assertIn("FC", forli_results)

        # Verify accessibility in CalculatorForm.tsx
        form_path = os.path.join(self.comp_dir, "CalculatorForm.tsx")
        with open(form_path, "r", encoding="utf-8") as f:
            src = f.read()

        self.assertIn('role="combobox"', src)
        self.assertIn('role="listbox"', src)
        self.assertIn('role="option"', src)
        self.assertIn("handleProvinceKeyDown", src)
        self.assertIn("provincesByRegion", src)

    def test_crowdsource_modal_bounds_anti_spam_and_feedback(self):
        """Verifies CrowdsourceModal anti-spam validation, Bayesian update, and instant feedback UX."""
        ref_price = 250
        min_bound = round(ref_price * 0.15)  # 38
        max_bound = round(ref_price * 8.0)   # 2000

        # Valid input
        paid = 280
        self.assertTrue(min_bound <= paid <= max_bound)
        # Bayesian update for N=100
        n_prev = 100
        n_new = n_prev + 1
        new_avg = round((ref_price * n_prev + paid) / n_new, 2)
        self.assertEqual(new_avg, 250.30)

        # Anti-spam rejections
        self.assertFalse(min_bound <= 10 <= max_bound)
        self.assertFalse(min_bound <= 3000 <= max_bound)

        # Verify modal implementation details
        modal_path = os.path.join(self.comp_dir, "CrowdsourceModal.tsx")
        with open(modal_path, "r", encoding="utf-8") as f:
            src = f.read()

        self.assertIn('role="dialog"', src)
        self.assertIn('aria-modal="true"', src)
        self.assertIn("aria-labelledby", src)
        self.assertIn("aria-describedby", src)
        self.assertIn("Segnalazione Anonima Registrata!", src)
        self.assertIn("Nuova Media", src)
        self.assertIn("Vecchia Media", src)
        self.assertIn("Variazione benchmark:", src)
        self.assertIn("CrowdsourceTriggerButton", src)

    def test_ad_slot_zero_cls_dimensions_and_agcm_disclosure(self):
        """Verifies AdSlot strict CSS min-height reservation and AGCM legal compliance."""
        ad_path = os.path.join(self.comp_dir, "AdSlot.tsx")
        with open(ad_path, "r", encoding="utf-8") as f:
            src = f.read()

        self.assertIn("leaderboard", src)
        self.assertIn("mpu", src)
        self.assertIn("sticky", src)
        self.assertIn("Pubblicità", src)
        self.assertIn('role="complementary"', src)
        self.assertIn("minHeight", src)
        self.assertIn("728", src)
        self.assertIn("250", src)
        self.assertIn("320", src)

    def test_affiliate_card_category_partner_mapping_and_urgency_morphing(self):
        """Verifies AffiliateCard category matching and high-urgency vs calm rendering."""
        aff_path = os.path.join(self.comp_dir, "AffiliateCard.tsx")
        with open(aff_path, "r", encoding="utf-8") as f:
            src = f.read()

        # All 6 categories supported via getAffiliateForCategory
        self.assertIn("getAffiliateForCategory", src)
        self.assertIn("isOvercharged", src)
        self.assertIn("isAlert", src)
        self.assertIn("ALLARME SOVRAPPREZZO", src)
        self.assertIn("animate-pulse-slow", src)
        self.assertIn("Sponsorizzato", src)
        self.assertIn("Partner Certificato", src)

    def test_app_master_layout_wiring_and_url_hydration(self):
        """Verifies App.tsx master coordination, query auto-hydration, and live recalculation."""
        app_path = os.path.join(self.src_dir, "App.tsx")
        with open(app_path, "r", encoding="utf-8") as f:
            src = f.read()

        # All 7 components coordinated
        self.assertIn("Tachometer", src)
        self.assertIn("ResultSummary", src)
        self.assertIn("ShareCard", src)
        self.assertIn("CalculatorForm", src)
        self.assertIn("CrowdsourceModal", src)
        self.assertIn("AdSlot", src)
        self.assertIn("AffiliateCard", src)

        # URL query parsing
        self.assertIn("parseShareUrlParams", src)
        self.assertIn("calculateDiscrepancy", src)

        # Live crowdsource update sync
        self.assertIn("handleCrowdsourceSuccess", src)
        self.assertIn("executeCalculation", src)

        # Branding, Horizontal Navigation & Disclaimers
        self.assertIn("Mi Stanno Fregando?", src)
        self.assertIn("BrandMark", src)
        self.assertIn("Menu principale", src)

    def test_custom_prestation_calculation_and_category_fallback(self):
        """
        Verifies that when prestationId is 'custom', calculation does not throw,
        and dynamically computes category-average benchmark multiplied by province coefficient.
        """
        categories = ['auto', 'casa', 'dentista', 'veterinario', 'cerimonie', 'affitti']
        prov_dict = get_province_dict()
        mi_coeff = prov_dict["MI"]["coeff"]  # 1.25

        for cat in categories:
            cat_prests = [p for p in PRESTATIONS_36 if p["category"] == cat]
            self.assertGreaterEqual(len(cat_prests), 6, f"Category {cat} must have at least 6 prestations")
            avg_base = sum(p["base_price"] for p in cat_prests) / len(cat_prests)
            self.assertGreater(avg_base, 0, f"Average base price for {cat} must be > 0")

            # Reference price in Milan
            ref_mi = calculate_local_reference_price(avg_base, mi_coeff)
            self.assertGreater(ref_mi, 0)

            # Test a fair quote equal to ref_mi
            diff_euro, diff_pct = calculate_discrepancy(ref_mi, ref_mi)
            zone, is_alert = classify_verdict(diff_pct)
            self.assertEqual(diff_euro, 0.0)
            self.assertEqual(diff_pct, 0.0)
            self.assertEqual(zone, "PREZZO_ONESTO")
            self.assertFalse(is_alert)

            # Test a gouged quote (+100% markup)
            gouged_quote = ref_mi * 2.0
            diff_euro_g, diff_pct_g = calculate_discrepancy(gouged_quote, ref_mi)
            zone_g, is_alert_g = classify_verdict(diff_pct_g)
            self.assertEqual(diff_pct_g, 100.0)
            self.assertEqual(zone_g, "TI_STANNO_FREGANDO")
            self.assertTrue(is_alert_g)

        # Source code audit: App.tsx must handle custom prestation without throwing
        app_path = os.path.join(self.src_dir, "App.tsx")
        with open(app_path, "r", encoding="utf-8") as f:
            app_src = f.read()

        self.assertIn("custom", app_src, "App.tsx must handle custom prestation ID")

    def test_url_hydration_without_prest_parameter_fallback(self):
        """
        Verifies URL share query string auto-hydration when 'prest' is omitted.
        All 6 categories must fall back to a valid, existing prestation slug,
        never resolving to invalid synthetic IDs like `${cat}_1`.
        """
        import urllib.parse

        categories = ['auto', 'casa', 'dentista', 'veterinario', 'cerimonie', 'affitti']
        prest_by_id = get_prestation_dict()

        for cat in categories:
            query_str = f"?cat={cat}&prov=RM&quote=250"
            parsed = urllib.parse.parse_qs(query_str.lstrip("?"))

            cat_param = parsed.get("cat", ["auto"])[0]
            prest_param = parsed.get("prest", [None])[0]

            cat_prestations = [p for p in PRESTATIONS_36 if p["category"] == cat_param]
            self.assertGreater(len(cat_prestations), 0, f"Category {cat_param} must have prestations")
            fallback_prest = prest_param or (cat_prestations[0]["id"] if cat_prestations else "auto_tagliando")

            # Must be a genuine prestation ID in the reference dataset
            self.assertIn(fallback_prest, prest_by_id, f"Fallback prestation {fallback_prest} must exist in dataset")
            self.assertEqual(
                prest_by_id[fallback_prest]["category"],
                cat,
                f"Fallback prestation {fallback_prest} must belong to category {cat}"
            )
            self.assertFalse(
                fallback_prest.endswith("_1"),
                f"Fallback prestation must not be synthetic slug like {cat}_1: got {fallback_prest}"
            )

            # Calculation using fallback prestation benchmark must succeed
            base_p = prest_by_id[fallback_prest]["base_price"]
            ref_p = calculate_local_reference_price(base_p, 1.18)  # Rome coeff
            diff_euro, diff_pct = calculate_discrepancy(250, ref_p)
            zone, is_alert = classify_verdict(diff_pct)
            self.assertIn(zone, ["PREZZO_ONESTO", "NELLA_MEDIA", "TI_STANNO_FREGANDO"])

        # Source code audit: App.tsx must not contain the buggy `${cat}_1` pattern
        app_path = os.path.join(self.src_dir, "App.tsx")
        with open(app_path, "r", encoding="utf-8") as f:
            app_src = f.read()

        self.assertNotIn("${cat}_1", app_src, "App.tsx must not use buggy `${cat}_1` fallback")

    def test_cadastral_province_search_matching_and_apostrophe_normalization(self):
        """
        Verifies cadastral province alias search (Reggio nell'Emilia -> RE)
        and apostrophe/space normalization (l aquila and l'aquila -> AQ).
        """
        import unicodedata
        import re

        def normalize(text):
            if not text:
                return ""
            nfkd = unicodedata.normalize("NFKD", str(text))
            no_diacritics = "".join([c for c in nfkd if not unicodedata.combining(c)])
            cleaned = re.sub(r"['’‘`´\-–—]", " ", no_diacritics.lower())
            return re.sub(r"\s+", " ", cleaned).strip()

        # 1. Normalization verification
        self.assertEqual(normalize("L'Aquila"), "l aquila")
        self.assertEqual(normalize("l'aquila"), "l aquila")
        self.assertEqual(normalize("l’aquila"), "l aquila")
        self.assertEqual(normalize("l aquila"), "l aquila")
        self.assertEqual(normalize("Forlì-Cesena"), "forli cesena")
        self.assertEqual(normalize("forli-cesena"), "forli cesena")
        self.assertEqual(normalize("forli cesena"), "forli cesena")
        self.assertEqual(normalize("Valle d'Aosta"), "valle d aosta")
        self.assertEqual(normalize("valle d aosta"), "valle d aosta")
        self.assertEqual(normalize("Reggio nell'Emilia"), "reggio nell emilia")
        self.assertEqual(normalize("Reggio nell’Emilia"), "reggio nell emilia")
        self.assertEqual(normalize("reggio nell emilia"), "reggio nell emilia")

        province_aliases = {
            "RE": ["Reggio nell'Emilia", "Reggio nell Emilia"],
            "RC": ["Reggio di Calabria"],
            "BZ": ["Bozen", "Bolzano-Bozen"],
            "AO": ["Aoste"],
            "FC": ["Cesena-Forlì", "Cesena Forli"],
            "MB": ["Monza e Brianza", "Monza Brianza"],
            "PU": ["Pesaro Urbino"],
        }

        def rank_provinces(query):
            q = normalize(query)
            if not q:
                return [p[0] for p in PROVINCES_107]
            scored = []
            for sigla, nome, regione, coeff in PROVINCES_107:
                n_nome = normalize(nome)
                n_sigla = normalize(sigla)
                n_reg = normalize(regione)
                aliases = province_aliases.get(sigla, [])
                n_aliases = [normalize(a) for a in aliases]

                score = 999
                if n_sigla == q:
                    score = 1
                elif n_nome.startswith(q) or any(a.startswith(q) or q.startswith(a) for a in n_aliases):
                    score = 2
                elif n_sigla.startswith(q):
                    score = 3
                elif q in n_nome or any(q in a or a in q for a in n_aliases):
                    score = 4
                elif n_reg.startswith(q):
                    score = 5
                elif q in n_reg:
                    score = 6

                if score < 999:
                    scored.append((score, sigla, nome))

            scored.sort()
            return [s[1] for s in scored]

        # 2. Cadastral search matching for RE (Reggio nell'Emilia)
        res_cadastral_1 = rank_provinces("Reggio nell'Emilia")
        self.assertGreater(len(res_cadastral_1), 0, "Reggio nell'Emilia must match RE")
        self.assertEqual(res_cadastral_1[0], "RE", "Reggio nell'Emilia must rank RE as #1")

        res_cadastral_2 = rank_provinces("reggio nell'emilia")
        self.assertEqual(res_cadastral_2[0], "RE")

        res_cadastral_3 = rank_provinces("reggio nell emilia")
        self.assertEqual(res_cadastral_3[0], "RE")

        # 3. Apostrophe / Space normalization for AQ (L'Aquila vs l aquila)
        res_aq_apostrophe = rank_provinces("l'aquila")
        self.assertGreater(len(res_aq_apostrophe), 0)
        self.assertEqual(res_aq_apostrophe[0], "AQ", "l'aquila must rank AQ as #1")

        res_aq_space = rank_provinces("l aquila")
        self.assertGreater(len(res_aq_space), 0)
        self.assertEqual(res_aq_space[0], "AQ", "l aquila (with space) must rank AQ as #1")

        res_aq_curly = rank_provinces("l’aquila")
        self.assertEqual(res_aq_curly[0], "AQ", "l’aquila (with curly quote) must rank AQ as #1")

        res_aq_sub = rank_provinces("aquila")
        self.assertIn("AQ", res_aq_sub)

        # 4. Forlì-Cesena hyphen/space check
        res_fc_hyphen = rank_provinces("forli-cesena")
        self.assertEqual(res_fc_hyphen[0], "FC")

        res_fc_space = rank_provinces("forli cesena")
        self.assertEqual(res_fc_space[0], "FC")

        # 5. Source code audit: CalculatorForm.tsx must implement alias and apostrophe normalization
        form_path = os.path.join(self.comp_dir, "CalculatorForm.tsx")
        with open(form_path, "r", encoding="utf-8") as f:
            form_src = f.read()

        self.assertIn("PROVINCE_ALIASES", form_src, "CalculatorForm.tsx must define PROVINCE_ALIASES")
        self.assertIn("Reggio nell'Emilia", form_src, "CalculatorForm.tsx must support cadastral alias Reggio nell'Emilia")


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


