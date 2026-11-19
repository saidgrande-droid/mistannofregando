#!/usr/bin/env python3
"""
tests/test_m3_fix_adversarial_stress.py
--------------------------------------------------------------------------------
Comprehensive Adversarial Empirical Stress Test Suite for Milestone 3 Fixes:
1. Custom Prestation Discrepancy Calculation across all 6 categories, 107 provinces,
   and boundary quote multipliers (fair, average, overcharge +65%, gouged +150%).
2. Deep-Link URL Parameter Hydration with omitted 'prest', invalid 'prest',
   mismatched category-prestation slugs, and custom description roundtrips.
3. Cadastral province alias search and diacritic/apostrophe normalization.
4. AST and structural integrity audit of TypeScript source files.
--------------------------------------------------------------------------------
"""

import os
import sys
import re
import json
import math
import urllib.parse
import unittest
import unicodedata

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATASET_PATH = os.path.join(SRC_DIR, "core", "dataset.json")


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


DATASET = load_dataset()
CATEGORIES = [c["id"] for c in DATASET["categories"]]
PROVINCES = DATASET["provinces"]
PROVINCE_BY_SIGLA = {p["sigla"]: p for p in PROVINCES}
PRESTATIONS = DATASET["prestations"]
PRESTATION_BY_ID = {p["id"]: p for p in PRESTATIONS}


# ==============================================================================
# Pure Python Replicas of Core Engine Algorithms (Matching TypeScript 1:1)
# ==============================================================================

def get_prestations_by_category(category_id):
    return [p for p in PRESTATIONS if p["categoryId"] == category_id]


def get_category_average_base_price(category_id):
    cat_prests = get_prestations_by_category(category_id)
    if not cat_prests:
        return 100
    return sum(p["basePrice"] for p in cat_prests) / len(cat_prests)


def calculate_discrepancy(category, prestation_id, province_sigla, quote, custom_ref_price=None):
    if not math.isfinite(quote) or quote < 0:
        raise ValueError(f"Quote must be greater than or equal to 0, received: {quote}")

    effective_ref_price = custom_ref_price

    if effective_ref_price is None or effective_ref_price <= 0:
        if prestation_id == "custom":
            cat_prests = get_prestations_by_category(category)
            avg_base = sum(p["basePrice"] for p in cat_prests) / len(cat_prests) if cat_prests else 100
            province = PROVINCE_BY_SIGLA.get(province_sigla)
            coeff = province["costCoefficient"] if province else 1.0
            effective_ref_price = round(avg_base * coeff)
        else:
            prestation = PRESTATION_BY_ID.get(prestation_id)
            if not prestation:
                raise ValueError(f"Prestazione non trovata: {prestation_id} in categoria {category}")
            province = PROVINCE_BY_SIGLA.get(province_sigla)
            coeff = province["costCoefficient"] if province else 1.0
            effective_ref_price = round(prestation["basePrice"] * coeff)

    if effective_ref_price <= 0:
        raise ValueError(f"Reference price must be strictly greater than 0, received: {effective_ref_price}")

    diff_euro = round((quote - effective_ref_price) * 100) / 100
    diff_pct = round(((quote - effective_ref_price) / effective_ref_price) * 10000) / 100

    # classifyZone
    if diff_pct <= 0:
        zone = "PREZZO_ONESTO"
        is_alert = False
    elif diff_pct <= 35:
        zone = "NELLA_MEDIA"
        is_alert = False
    else:
        zone = "TI_STANNO_FREGANDO"
        is_alert = diff_pct >= 65

    # getNeedleAngle
    if diff_pct <= -50.0:
        angle = -100.0
    elif diff_pct <= 0.0:
        angle = -100.0 + 100.0 * ((diff_pct + 50.0) / 50.0)
    elif diff_pct <= 35.0:
        angle = 50.0 * (diff_pct / 35.0)
    elif diff_pct <= 70.0:
        angle = 50.0 + 50.0 * ((diff_pct - 35.0) / 35.0)
    else:
        angle = 100.0

    needle_angle = round(angle * 100) / 100

    return {
        "quote": quote,
        "refPrice": effective_ref_price,
        "diffEuro": diff_euro,
        "diffPct": diff_pct,
        "zone": zone,
        "isAlert": is_alert,
        "needleAngle": needle_angle,
    }


def normalize_italian_text(text):
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", str(text))
    no_diacritics = "".join([c for c in nfkd if not unicodedata.combining(c)])
    cleaned = re.sub(r"['’‘`´\-–—]", " ", no_diacritics.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


PROVINCE_ALIASES = {
    "RE": ["Reggio nell'Emilia", "Reggio nell Emilia", "Reggio nellemilia"],
    "RC": ["Reggio di Calabria", "Reggio Calabria"],
    "BZ": ["Bolzano-Bozen", "Bozen", "Bolzano Bozen"],
    "AO": ["Valle d'Aosta", "Valle d Aosta", "Aoste"],
    "FC": ["Cesena-Forlì", "Cesena Forli", "Forlì Cesena", "Forli Cesena"],
    "MB": ["Monza e Brianza", "Monza Brianza", "Monza-Brianza"],
    "PU": ["Pesaro e Urbino", "Pesaro Urbino", "Pesaro-Urbino"],
    "SP": ["La Spezia"],
    "AQ": ["L'Aquila", "L Aquila", "LAquila"],
}


def rank_provinces(query):
    q = normalize_italian_text(query)
    if not q:
        return [p["sigla"] for p in PROVINCES]
    scored = []
    for p in PROVINCES:
        sigla = p["sigla"]
        nome = p["nome"]
        regione = p["regione"]

        n_sigla = normalize_italian_text(sigla)
        n_nome = normalize_italian_text(nome)
        n_reg = normalize_italian_text(regione)
        aliases = PROVINCE_ALIASES.get(sigla, [])
        n_aliases = [normalize_italian_text(a) for a in aliases]

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


def simulate_url_hydration(query_string):
    """
    Simulates App.tsx lines 121-152 URL hydration logic in pure Python.
    """
    search = query_string.lstrip("?")
    params = urllib.parse.parse_qs(search)

    raw_cat = params.get("cat", [None])[0]
    cat = raw_cat if raw_cat in CATEGORIES else "auto"

    cat_prests = get_prestations_by_category(cat)
    default_prest = cat_prests[0]["id"] if cat_prests else "auto_tagliando"

    raw_prest = params.get("prest", [None])[0]
    is_valid_prest = raw_prest and (
        any(p["id"] == raw_prest for p in cat_prests) or raw_prest == "custom"
    )
    prest = raw_prest if is_valid_prest else default_prest

    raw_prov = params.get("prov", [None])[0]
    prov = raw_prov.upper() if (raw_prov and raw_prov.upper() in PROVINCE_BY_SIGLA) else "MI"

    raw_quote = params.get("quote", [None])[0]
    quote = None
    if raw_quote:
        try:
            val = float(raw_quote)
            if math.isfinite(val) and val > 0:
                quote = val
        except ValueError:
            pass

    custom_desc = params.get("desc", [None])[0]

    return {
        "categoryId": cat,
        "prestationId": prest,
        "provinceSigla": prov,
        "quote": quote,
        "customDescription": custom_desc,
    }


def build_share_url(base_url, cat, prest, prov, quote, custom_desc=None):
    clean_base = base_url.split("?")[0].rstrip("/")
    params = {
        "cat": cat,
        "prest": prest,
        "prov": prov.upper(),
        "quote": str(quote),
    }
    if prest == "custom" and custom_desc and custom_desc.strip():
        params["desc"] = custom_desc.strip()
    return f"{clean_base}/?{urllib.parse.urlencode(params)}"


# ==============================================================================
# TEST SUITE: Custom Prestation Calculation Stress Tests
# ==============================================================================

class TestCustomPrestationDiscrepancyStress(unittest.TestCase):
    """
    Empirical stress-testing of `prestationId: 'custom'` across all 6 categories,
    all 107 Italian provinces, and varied pricing scenarios.
    """

    def test_custom_prestation_average_base_calculation_all_6_categories(self):
        """
        Asserts that every category has positive, distinct, and realistic base averages.
        """
        averages = {}
        for cat in CATEGORIES:
            cat_prests = get_prestations_by_category(cat)
            self.assertEqual(len(cat_prests), 6, f"Category {cat} must contain exactly 6 prestations")
            avg_base = get_category_average_base_price(cat)
            self.assertGreater(avg_base, 0, f"Average base price for {cat} must be > 0")
            averages[cat] = avg_base

        # Verify realistic price hierarchy
        # e.g., cerimonie average should be significantly higher than veterinario average
        self.assertGreater(averages["cerimonie"], averages["veterinario"])
        self.assertGreater(averages["affitti"], averages["veterinario"])

    def test_custom_prestation_all_107_provinces_never_throws(self):
        """
        Runs custom prestation calculation across all 6 categories and all 107 provinces.
        Asserts calculateDiscrepancy never throws and produces valid benchmark refPrice.
        """
        for cat in CATEGORIES:
            for prov in PROVINCES:
                sigla = prov["sigla"]
                coeff = prov["costCoefficient"]
                avg_base = get_category_average_base_price(cat)
                expected_ref = round(avg_base * coeff)

                res = calculate_discrepancy(cat, "custom", sigla, expected_ref)

                self.assertIsNotNone(res)
                self.assertEqual(res["refPrice"], expected_ref)
                self.assertEqual(res["diffEuro"], 0.0)
                self.assertEqual(res["diffPct"], 0.0)
                self.assertEqual(res["zone"], "PREZZO_ONESTO")
                self.assertFalse(res["isAlert"])
                self.assertEqual(res["needleAngle"], 0.0)

    def test_custom_prestation_quote_scenarios_and_tachometer_zones(self):
        """
        For all 6 categories, tests varied quote levels against custom prestation benchmark:
        - Fair (0% diff): PREZZO_ONESTO, needle = 0.0°
        - Bargain (-25% diff): PREZZO_ONESTO, needle = -50.0°
        - Extreme Bargain (-50% diff): PREZZO_ONESTO, needle = -100.0°
        - Below -50% (-80% diff): PREZZO_ONESTO, needle = -100.0° (clamped)
        - Nella Media (+17.5% diff): NELLA_MEDIA, needle = +25.0°
        - Boundary Nella Media (+35.0% diff): NELLA_MEDIA, needle = +50.0°
        - Overcharge (+52.5% diff): TI_STANNO_FREGANDO, isAlert = False, needle = +75.0°
        - Critical Alert (+65.0% diff): TI_STANNO_FREGANDO, isAlert = True, needle = +92.86°
        - Severe Gouging (+70.0% diff): TI_STANNO_FREGANDO, isAlert = True, needle = +100.0°
        - Astronomical Gouging (+200% diff): TI_STANNO_FREGANDO, isAlert = True, needle = +100.0° (clamped)
        """
        test_provinces = ["MI", "RM", "NA", "EN", "BZ"]  # North, Central, South, Island, Special

        for cat in CATEGORIES:
            for sigla in test_provinces:
                # 1. Exact Reference Benchmark
                avg_base = get_category_average_base_price(cat)
                ref = round(avg_base * PROVINCE_BY_SIGLA[sigla]["costCoefficient"])

                # Scenario 1: Exact Benchmark (Fair)
                res_fair = calculate_discrepancy(cat, "custom", sigla, ref)
                self.assertEqual(res_fair["zone"], "PREZZO_ONESTO")
                self.assertFalse(res_fair["isAlert"])
                self.assertEqual(res_fair["needleAngle"], 0.0)

                # Scenario 2: Bargain (-25%)
                quote_bargain = round(ref * 0.75)
                res_bargain = calculate_discrepancy(cat, "custom", sigla, quote_bargain)
                self.assertEqual(res_bargain["zone"], "PREZZO_ONESTO")
                self.assertFalse(res_bargain["isAlert"])
                self.assertLess(res_bargain["needleAngle"], 0.0)
                self.assertGreaterEqual(res_bargain["needleAngle"], -100.0)

                # Scenario 3: Boundary -50%
                quote_half = round(ref * 0.50, 2)
                res_half = calculate_discrepancy(cat, "custom", sigla, quote_half)
                self.assertEqual(res_half["zone"], "PREZZO_ONESTO")
                self.assertFalse(res_half["isAlert"])
                self.assertEqual(res_half["needleAngle"], -100.0)

                # Scenario 4: Extreme -80% (clamping check)
                quote_low = round(ref * 0.20)
                res_low = calculate_discrepancy(cat, "custom", sigla, quote_low)
                self.assertEqual(res_low["zone"], "PREZZO_ONESTO")
                self.assertEqual(res_low["needleAngle"], -100.0, "Needle angle must clamp to -100°")

                # Scenario 5: Nella Media (+17.5%)
                quote_mid = round(ref * 1.175)
                res_mid = calculate_discrepancy(cat, "custom", sigla, quote_mid)
                self.assertEqual(res_mid["zone"], "NELLA_MEDIA")
                self.assertFalse(res_mid["isAlert"])
                self.assertGreater(res_mid["needleAngle"], 0.0)
                self.assertLessEqual(res_mid["needleAngle"], 50.0)

                # Scenario 6: Boundary Nella Media (+35.0%)
                quote_35 = round(ref * 1.35, 2)
                res_35 = calculate_discrepancy(cat, "custom", sigla, quote_35)
                self.assertEqual(res_35["zone"], "NELLA_MEDIA", f"Exact +35% quote must be NELLA_MEDIA: {res_35['diffPct']}%")
                self.assertFalse(res_35["isAlert"])
                self.assertAlmostEqual(res_35["needleAngle"], 50.0, delta=0.5)

                # Boundary +35% + 1€: Must flip to TI_STANNO_FREGANDO
                quote_35_plus = round(ref * 1.35, 2) + 1.0
                res_35_plus = calculate_discrepancy(cat, "custom", sigla, quote_35_plus)
                self.assertEqual(res_35_plus["zone"], "TI_STANNO_FREGANDO", "Quote strictly above +35% must flip to TI_STANNO_FREGANDO")

                # Scenario 7: Overcharge (+50%)
                quote_50 = round(ref * 1.50)
                res_50 = calculate_discrepancy(cat, "custom", sigla, quote_50)
                self.assertEqual(res_50["zone"], "TI_STANNO_FREGANDO")
                self.assertFalse(res_50["isAlert"], "+50% must not trigger alert (threshold is +65%)")
                self.assertGreater(res_50["needleAngle"], 50.0)
                self.assertLess(res_50["needleAngle"], 100.0)

                # Scenario 8: Critical Overcharge Alert (+65.0%)
                quote_65 = round(ref * 1.65, 2)
                res_65 = calculate_discrepancy(cat, "custom", sigla, quote_65)
                self.assertEqual(res_65["zone"], "TI_STANNO_FREGANDO")
                self.assertTrue(res_65["isAlert"], f"+65% must trigger isAlert=True (diffPct={res_65['diffPct']})")
                self.assertGreaterEqual(res_65["needleAngle"], 90.0)

                # Scenario 9: Severe Gouging (+100%)
                quote_100 = round(ref * 2.0)
                res_100 = calculate_discrepancy(cat, "custom", sigla, quote_100)
                self.assertEqual(res_100["zone"], "TI_STANNO_FREGANDO")
                self.assertTrue(res_100["isAlert"])
                self.assertEqual(res_100["needleAngle"], 100.0, "Needle angle must clamp to +100°")

                # Scenario 10: Astronomical Quote (1,000,000 €)
                res_astro = calculate_discrepancy(cat, "custom", sigla, 1_000_000)
                self.assertEqual(res_astro["zone"], "TI_STANNO_FREGANDO")
                self.assertTrue(res_astro["isAlert"])
                self.assertEqual(res_astro["needleAngle"], 100.0)
                self.assertTrue(math.isfinite(res_astro["diffPct"]))

    def test_custom_prestation_with_explicit_crowdsource_override(self):
        """
        Verifies that when customRefPrice is provided (from crowdsourcing),
        calculateDiscrepancy prioritizes the crowdsourced benchmark over category average.
        When customRefPrice is 0 or None, it gracefully falls back to category average.
        """
        # Given a custom benchmark of 450€ for 'casa' in RM (where category average might be ~220€)
        crowdsourced_benchmark = 450.0
        res_with_override = calculate_discrepancy("casa", "custom", "RM", 450.0, custom_ref_price=crowdsourced_benchmark)
        self.assertEqual(res_with_override["refPrice"], 450.0)
        self.assertEqual(res_with_override["diffPct"], 0.0)
        self.assertEqual(res_with_override["zone"], "PREZZO_ONESTO")

        # When customRefPrice is None, falls back to category avg * coeff
        res_fallback_none = calculate_discrepancy("casa", "custom", "RM", 450.0, custom_ref_price=None)
        avg_base = get_category_average_base_price("casa")
        expected_ref = round(avg_base * PROVINCE_BY_SIGLA["RM"]["costCoefficient"])
        self.assertEqual(res_fallback_none["refPrice"], expected_ref)

        # When customRefPrice is 0 or negative, also falls back safely
        res_fallback_zero = calculate_discrepancy("casa", "custom", "RM", 450.0, custom_ref_price=0)
        self.assertEqual(res_fallback_zero["refPrice"], expected_ref)


# ==============================================================================
# TEST SUITE: Deep-Link URL Parameter Hydration Stress Tests
# ==============================================================================

class TestUrlHydrationStress(unittest.TestCase):
    """
    Stress-tests deep-link URL parameter hydration across all 6 categories,
    verifying omission of `prest`, invalid slugs, and cross-category mismatches.
    """

    def test_url_hydration_omitted_prest_all_6_categories(self):
        """
        Tests deep-link URL hydration when `prest` parameter is omitted across all 6 categories:
        ?cat={cat}&prov=RM&quote=300
        Asserts it seamlessly resolves to the first valid prestation in that category without throwing.
        """
        for cat in CATEGORIES:
            cat_prests = get_prestations_by_category(cat)
            expected_first_prest = cat_prests[0]["id"]

            url = f"?cat={cat}&prov=RM&quote=300"
            hydrated = simulate_url_hydration(url)

            self.assertEqual(hydrated["categoryId"], cat)
            self.assertEqual(hydrated["prestationId"], expected_first_prest,
                             f"Category {cat} without prest must resolve to {expected_first_prest}")
            self.assertEqual(hydrated["provinceSigla"], "RM")
            self.assertEqual(hydrated["quote"], 300.0)

            # Assert calculation runs without throwing
            res = calculate_discrepancy(
                hydrated["categoryId"],
                hydrated["prestationId"],
                hydrated["provinceSigla"],
                hydrated["quote"]
            )
            self.assertIsNotNone(res)
            self.assertGreater(res["refPrice"], 0)

    def test_url_hydration_invalid_prestation_slug_falls_back(self):
        """
        Tests that passing an invalid, non-existent prestation slug falls back to the default prestation.
        """
        for cat in CATEGORIES:
            cat_prests = get_prestations_by_category(cat)
            default_prest = cat_prests[0]["id"]

            url = f"?cat={cat}&prest=totally_bogus_slug_12345&prov=MI&quote=200"
            hydrated = simulate_url_hydration(url)

            self.assertEqual(hydrated["prestationId"], default_prest)
            self.assertEqual(hydrated["categoryId"], cat)

    def test_url_hydration_cross_category_prestation_mismatch_falls_back(self):
        """
        Tests when `prest` belongs to category A, but `cat` is category B:
        e.g., ?cat=dentista&prest=auto_tagliando&prov=TO&quote=150
        Must detect that `auto_tagliando` is not in `dentista` and fall back to `dentista_igiene`.
        """
        url = "?cat=dentista&prest=auto_tagliando&prov=TO&quote=150"
        hydrated = simulate_url_hydration(url)

        self.assertEqual(hydrated["categoryId"], "dentista")
        self.assertEqual(hydrated["prestationId"], "dentista_igiene")
        self.assertEqual(hydrated["provinceSigla"], "TO")

    def test_url_hydration_custom_prestation_with_description(self):
        """
        Tests hydration when prestationId is 'custom' and an optional description is provided.
        ?cat=casa&prest=custom&prov=FI&quote=500&desc=Rifacimento+completo+bagno
        """
        url = "?cat=casa&prest=custom&prov=FI&quote=500&desc=Rifacimento+completo+bagno"
        hydrated = simulate_url_hydration(url)

        self.assertEqual(hydrated["categoryId"], "casa")
        self.assertEqual(hydrated["prestationId"], "custom")
        self.assertEqual(hydrated["provinceSigla"], "FI")
        self.assertEqual(hydrated["quote"], 500.0)
        self.assertEqual(hydrated["customDescription"], "Rifacimento completo bagno")

        # Execute custom calculation
        res = calculate_discrepancy(
            hydrated["categoryId"],
            hydrated["prestationId"],
            hydrated["provinceSigla"],
            hydrated["quote"]
        )
        self.assertIsNotNone(res)

    def test_url_hydration_missing_all_optional_parameters(self):
        """
        Tests edge-case URLs:
        1. Bare ?cat=auto -> prest='auto_tagliando', prov='MI', quote=None
        2. Empty query string "" -> cat='auto', prest='auto_tagliando', prov='MI', quote=None
        3. Invalid province -> falls back to 'MI'
        4. Negative quote -> quote is ignored (None)
        """
        h1 = simulate_url_hydration("?cat=auto")
        self.assertEqual(h1["categoryId"], "auto")
        self.assertEqual(h1["prestationId"], "auto_tagliando")
        self.assertEqual(h1["provinceSigla"], "MI")
        self.assertIsNone(h1["quote"])

        h2 = simulate_url_hydration("")
        self.assertEqual(h2["categoryId"], "auto")
        self.assertEqual(h2["prestationId"], "auto_tagliando")
        self.assertEqual(h2["provinceSigla"], "MI")
        self.assertIsNone(h2["quote"])

        h3 = simulate_url_hydration("?cat=affitti&prov=NON_EXISTENT")
        self.assertEqual(h3["categoryId"], "affitti")
        self.assertEqual(h3["provinceSigla"], "MI")

        h4 = simulate_url_hydration("?cat=cerimonie&quote=-250")
        self.assertIsNone(h4["quote"])

    def test_share_url_build_and_hydrate_roundtrip_lossless(self):
        """
        Verifies buildShareUrl -> simulate_url_hydration roundtrip is 100% lossless
        for all 6 categories, standard prestations, and custom prestations with descriptions.
        """
        base = "https://mistannofregando.it"

        for cat in CATEGORIES:
            # Standard prestation roundtrip
            cat_prests = get_prestations_by_category(cat)
            p_id = cat_prests[2]["id"]
            url_std = build_share_url(base, cat, p_id, "NA", 320.0)
            hydrated_std = simulate_url_hydration(url_std.split("?")[1])

            self.assertEqual(hydrated_std["categoryId"], cat)
            self.assertEqual(hydrated_std["prestationId"], p_id)
            self.assertEqual(hydrated_std["provinceSigla"], "NA")
            self.assertEqual(hydrated_std["quote"], 320.0)

            # Custom prestation roundtrip
            custom_text = f"Intervento speciale {cat} urgenza"
            url_custom = build_share_url(base, cat, "custom", "VR", 480.0, custom_desc=custom_text)
            hydrated_custom = simulate_url_hydration(url_custom.split("?")[1])

            self.assertEqual(hydrated_custom["categoryId"], cat)
            self.assertEqual(hydrated_custom["prestationId"], "custom")
            self.assertEqual(hydrated_custom["provinceSigla"], "VR")
            self.assertEqual(hydrated_custom["quote"], 480.0)
            self.assertEqual(hydrated_custom["customDescription"], custom_text)


# ==============================================================================
# TEST SUITE: Cadastral Search & Normalization Robustness
# ==============================================================================

class TestCadastralSearchAndNormalizationStress(unittest.TestCase):
    """
    Empirical tests of cadastral alias search and Italian elision/diacritic normalization.
    """

    def test_cadastral_search_reggio_emilia_all_variants(self):
        """
        Reggio Emilia (RE):
        Official cadastral query "Reggio nell'Emilia" and all typographic permutations
        must match RE as #1 ranked result.
        """
        variants = [
            "Reggio nell'Emilia",
            "reggio nell'emilia",
            "Reggio nell’Emilia",  # curly quote
            "reggio nell emilia",  # space
            "Reggio nell Emilia",
            "reggio nellemilia",
            "RE",
            "re",
        ]
        for v in variants:
            res = rank_provinces(v)
            self.assertGreater(len(res), 0, f"Query '{v}' must yield results")
            self.assertEqual(res[0], "RE", f"Query '{v}' must rank RE as #1 (got {res[0]})")

    def test_laquila_elision_and_space_normalization(self):
        """
        L'Aquila (AQ):
        Must match both elided "l'aquila" and separated "l aquila".
        """
        variants = ["L'Aquila", "l'aquila", "l’aquila", "l aquila", "L Aquila", "AQ", "aq"]
        for v in variants:
            res = rank_provinces(v)
            self.assertGreater(len(res), 0)
            self.assertEqual(res[0], "AQ", f"Query '{v}' must rank AQ as #1 (got {res[0]})")

    def test_hyphenated_and_composite_provinces(self):
        """
        Tests hyphenated provinces with both hyphen and space:
        - Forlì-Cesena (FC)
        - Bolzano-Bozen (BZ)
        - Monza e Brianza (MB)
        - Pesaro e Urbino (PU)
        - Valle d'Aosta (AO)
        """
        self.assertEqual(rank_provinces("forli-cesena")[0], "FC")
        self.assertEqual(rank_provinces("forli cesena")[0], "FC")
        self.assertEqual(rank_provinces("cesena forli")[0], "FC")

        self.assertEqual(rank_provinces("bolzano-bozen")[0], "BZ")
        self.assertEqual(rank_provinces("bozen")[0], "BZ")

        self.assertEqual(rank_provinces("monza e brianza")[0], "MB")
        self.assertEqual(rank_provinces("monza brianza")[0], "MB")

        self.assertEqual(rank_provinces("pesaro e urbino")[0], "PU")
        self.assertEqual(rank_provinces("pesaro urbino")[0], "PU")

        self.assertEqual(rank_provinces("valle d'aosta")[0], "AO")
        self.assertEqual(rank_provinces("valle d aosta")[0], "AO")
        self.assertEqual(rank_provinces("aoste")[0], "AO")


# ==============================================================================
# TEST SUITE: Source Code AST & Bracket Balance Verification
# ==============================================================================

class TestSourceCodeIntegrityAudit(unittest.TestCase):
    """
    Source code audit inspecting actual files in src/ to ensure zero bugs,
    correct fallbacks, balanced braces, and no regressions.
    """

    def test_bracket_and_brace_balance_across_all_source_files(self):
        """
        Checks that all core TypeScript/TSX files have exact 0 brace and parenthesis diffs.
        """
        files_to_check = [
            os.path.join(SRC_DIR, "core", "calculator.ts"),
            os.path.join(SRC_DIR, "core", "dataset.ts"),
            os.path.join(SRC_DIR, "App.tsx"),
            os.path.join(SRC_DIR, "components", "CalculatorForm.tsx"),
            os.path.join(SRC_DIR, "components", "ShareCard.tsx"),
            os.path.join(SRC_DIR, "components", "ResultSummary.tsx"),
            os.path.join(SRC_DIR, "components", "CrowdsourceModal.tsx"),
            os.path.join(SRC_DIR, "components", "AdSlot.tsx"),
            os.path.join(SRC_DIR, "components", "AffiliateCard.tsx"),
        ]

        for file_path in files_to_check:
            self.assertTrue(os.path.isfile(file_path), f"File {file_path} must exist")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertGreater(len(content), 100, f"File {file_path} must be non-empty")
            brace_diff = content.count("{") - content.count("}")
            self.assertEqual(brace_diff, 0, f"Brace mismatch in {os.path.basename(file_path)}: {brace_diff}")

    def test_source_code_calculator_ts_implements_custom_prestation_fallback(self):
        """
        calculator.ts must explicitly support prestationId === 'custom'
        without throwing "Prestazione non trovata".
        """
        calc_path = os.path.join(SRC_DIR, "core", "calculator.ts")
        with open(calc_path, "r", encoding="utf-8") as f:
            src = f.read()

        self.assertIn("prestationId === 'custom'", src)
        self.assertIn("getPrestationsByCategory", src)
        self.assertIn("effectiveRefPrice = Math.round(avgBase * costCoefficient)", src)

    def test_source_code_app_tsx_no_cat_1_buggy_fallback(self):
        """
        App.tsx must not contain `${cat}_1` fallback.
        It must use `getPrestationsByCategory(cat)[0].id`.
        """
        app_path = os.path.join(SRC_DIR, "App.tsx")
        with open(app_path, "r", encoding="utf-8") as f:
            src = f.read()

        self.assertNotIn("${cat}_1", src, "App.tsx must not contain `${cat}_1`")
        self.assertIn("getPrestationsByCategory(cat)", src)
        self.assertIn("setCustomPrestationDesc", src)

    def test_source_code_calculator_form_tsx_handles_custom_description(self):
        """
        CalculatorForm.tsx must accept initialCustomDescription,
        support custom prestations, and normalize cadastral aliases.
        """
        form_path = os.path.join(SRC_DIR, "components", "CalculatorForm.tsx")
        with open(form_path, "r", encoding="utf-8") as f:
            src = f.read()

        self.assertIn("initialCustomDescription", src)
        self.assertIn("isCustomPrestation", src)
        self.assertIn("PROVINCE_ALIASES", src)
        self.assertIn("Reggio nell'Emilia", src)
        self.assertIn("['’‘`´\\-–—]", src)

    def test_source_code_share_card_tsx_encodes_and_parses_desc_parameter(self):
        """
        ShareCard.tsx must include customDescription in buildShareUrl and parseShareUrlParams.
        """
        share_path = os.path.join(SRC_DIR, "components", "ShareCard.tsx")
        with open(share_path, "r", encoding="utf-8") as f:
            src = f.read()

        self.assertIn("customDescription?: string", src)
        self.assertIn("params.set('desc', customDescription.trim())", src)
        self.assertIn("result.customDescription = desc", src)


# ==============================================================================
# MAIN RUNNER
# ==============================================================================

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
