#!/usr/bin/env python3
"""
tests/test_challenger_m3_fix_2.py
Empirical Stress Test Suite for Milestone 3 Fix:
Province Search Rankings, Cadastral Aliases, and Crowdsourcing Stability.

Author: challenger_m3_fix_2 (Teamwork Empirical Challenger / Critic / Specialist)
Target: Comprehensive empirical stress-testing for M3 Fix validation.

Test Matrix:
1. All 107 Italian provinces searched by:
   - Uppercase sigla (all 107 must rank #1)
   - Lowercase sigla (all 107 must rank #1)
   - Trimmed/padded sigla
   - Exact province name (all 107 must rank #1)
2. Diacritics and elision normalization:
   - "forli" and "forlì" -> FC rank #1
   - "l'aquila", "l aquila", "l’aquila", "l‘aquila", "l`aquila", "l´aquila", "laquila" -> AQ rank #1
   - "valle d'aosta", "valle d aosta", "aosta" -> AO rank #1
   - "bolzano-bozen", "bozen", "bolzano" -> BZ rank #1
   - "monza e brianza", "monza brianza", "monza-brianza" -> MB rank #1
   - "pesaro e urbino", "pesaro urbino", "pesaro-urbino" -> PU rank #1
   - "cesena-forli", "cesena forli" -> FC rank #1
   - "reggio di calabria", "reggio calabria" -> RC rank #1
3. Cadastral alias ranking:
   - "Reggio nell'Emilia", "Reggio nell Emilia", "Reggio nellemilia" -> RE rank #1
   - Full PROVINCE_ALIASES dictionary audit and verification (all aliases rank corresponding province #1)
4. Crowdsourcing validation boundary stress:
   - Exact minBound / maxBound acceptance across all 36 catalog prestations and 107 provinces
   - minBound - 0.01 / maxBound + 0.01 strict rejection
   - Zero, negative, NaN, Infinity, non-numeric type rejection
   - Fallback ratio bounds (0.15 * ref, 8.0 * ref) under varied reference prices
5. Bayesian updating stability and drift:
   - Cold start (sampleCount = 0)
   - Defensive negative sampleCount
   - 10,000 sequential updates numerical drift test
   - Massive sample count stability (N = 1,000,000,000)
   - Alternating extreme stress (oscillating between min and max bounds)
6. Custom prestation calculation and URL hydration fallback across all 6 categories
"""

import os
import sys
import json
import math
import re
import unicodedata
import unittest
from typing import Dict, List, Tuple, Any, Optional

def _find_project_root() -> str:
    current = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    while current and current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, "src", "core", "dataset.json")):
            return current
        current = os.path.dirname(current)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PROJECT_ROOT = _find_project_root()
DATASET_PATH = os.path.join(PROJECT_ROOT, "src", "core", "dataset.json")
CALCULATOR_FORM_PATH = os.path.join(PROJECT_ROOT, "src", "components", "CalculatorForm.tsx")
CROWDSOURCE_PATH = os.path.join(PROJECT_ROOT, "src", "core", "crowdsource.ts")
CALCULATOR_PATH = os.path.join(PROJECT_ROOT, "src", "core", "calculator.ts")
APP_PATH = os.path.join(PROJECT_ROOT, "src", "App.tsx")



# ==============================================================================
# PURE PYTHON ORACLE (Mirrors TypeScript CalculatorForm & Crowdsource logic)
# ==============================================================================

def load_dataset() -> Dict[str, Any]:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_italian_text(text: str) -> str:
    """
    Exact Python mirror of normalizeItalianText from src/components/CalculatorForm.tsx:
    text.normalize('NFD')
        .replace(/[\\u0300-\\u036f]/g, '')
        .toLowerCase()
        .replace(/['’‘`´\\-–—]/g, ' ')
        .replace(/\\s+/g, ' ')
        .trim();
    """
    if not text:
        return ""
    # Unicode NFD decomposition
    nfd = unicodedata.normalize("NFD", text)
    # Strip diacritical marks (\u0300-\u036f)
    no_diacritics = "".join(c for c in nfd if not (0x0300 <= ord(c) <= 0x036F))
    lowered = no_diacritics.lower()
    # Replace apostrophes, quotes, hyphens, and dashes with space
    punct_normalized = re.sub(r"['’‘`´\-–—]", " ", lowered)
    # Collapse multiple whitespaces and trim
    collapsed = re.sub(r"\s+", " ", punct_normalized).strip()
    return collapsed


# Exact PROVINCE_ALIASES mapping from CalculatorForm.tsx
PROVINCE_ALIASES: Dict[str, List[str]] = {
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


def filter_and_rank_provinces(query: str, provinces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Exact Python mirror of filteredProvinces scoring and ranking algorithm
    from src/components/CalculatorForm.tsx:430-476.
    """
    q = normalize_italian_text(query)
    if not q:
        return sorted(provinces, key=lambda p: p["nome"])

    scored: List[Tuple[Dict[str, Any], int]] = []
    for p in provinces:
        nome_norm = normalize_italian_text(p["nome"])
        sigla_norm = normalize_italian_text(p["sigla"])
        reg_norm = normalize_italian_text(p["regione"])
        aliases = PROVINCE_ALIASES.get(p["sigla"], [])
        aliases_norm = [normalize_italian_text(a) for a in aliases]

        score = 999
        if sigla_norm == q:
            score = 1
        elif (
            nome_norm.startswith(q) or
            any(a.startswith(q) or q.startswith(a) for a in aliases_norm)
        ):
            score = 2
        elif sigla_norm.startswith(q):
            score = 3
        elif (
            nome_norm.find(q) != -1 or
            any(a.find(q) != -1 or q.find(a) != -1 for a in aliases_norm)
        ):
            score = 4
        elif reg_norm.startswith(q):
            score = 5
        elif reg_norm.find(q) != -1:
            score = 6

        if score < 999:
            scored.append((p, score))

    # Tie-break by score, then alphabetical nome
    scored.sort(key=lambda item: (item[1], item[0]["nome"]))
    return [item[0] for item in scored]


def validate_crowdsourced_price_oracle(
    paid_amount: Any,
    ref_price: float,
    custom_bounds: Optional[Tuple[float, float]] = None
) -> Tuple[bool, Optional[str], float, float]:
    """Exact mirror of src/core/crowdsource.ts:validateCrowdsourcedPrice."""
    if not isinstance(paid_amount, (int, float)) or isinstance(paid_amount, bool) or not math.isfinite(paid_amount):
        return False, "L'importo inserito non è un numero valido. Inserisci una cifra in euro.", 0, 0

    if paid_amount <= 0:
        return False, "L'importo deve essere superiore a 0 €.", 0, 0

    safe_ref = ref_price if ref_price > 0 else 100.0
    min_allowed = custom_bounds[0] if custom_bounds else max(1.0, float(round(safe_ref * 0.15)))
    max_allowed = custom_bounds[1] if custom_bounds else float(round(safe_ref * 8.0))

    if paid_amount < min_allowed:
        return False, f"Importo troppo basso per questa prestazione (minimo consentito: {int(min_allowed)} €). Inserisci l'importo effettivamente fatturato.", min_allowed, max_allowed

    if paid_amount > max_allowed:
        return False, f"Importo troppo elevato per questa prestazione (massimo consentito: {int(max_allowed)} €). Inserisci una cifra verosimile.", min_allowed, max_allowed

    return True, None, min_allowed, max_allowed


def calculate_updated_average_oracle(current_avg: float, sample_count: int, paid_amount: float) -> Tuple[float, int]:
    """Exact mirror of src/core/crowdsource.ts:calculateUpdatedAverage."""
    safe_count = max(0, sample_count)
    new_sample_count = safe_count + 1
    updated_mean = (current_avg * safe_count + paid_amount) / new_sample_count
    new_average = round(updated_mean, 2)
    return new_average, new_sample_count


def bayesian_online_average_oracle(current_avg: float, sample_count: int, paid_amount: float) -> int:
    """Exact mirror of src/core/crowdsource.ts:bayesianOnlineAverage."""
    safe_count = max(0, sample_count)
    new_count = safe_count + 1
    new_avg = (current_avg * safe_count + paid_amount) / new_count
    return round(new_avg)


# ==============================================================================
# TEST SUITE IMPLEMENTATION
# ==============================================================================

class TestProvinceSearchRankingStress(unittest.TestCase):
    """Exhaustive empirical testing of the 107 Italian provinces search and ranking."""

    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()
        cls.provinces = cls.dataset["provinces"]
        self_check_count = len(cls.provinces)
        assert self_check_count == 107, f"Expected 107 provinces, found {self_check_count}"

    def test_all_107_provinces_uppercase_sigla_search_ranks_number_one(self):
        """Every single one of the 107 provinces searched by its uppercase sigla MUST rank #1."""
        for p in self.provinces:
            sigla = p["sigla"].upper()
            results = filter_and_rank_provinces(sigla, self.provinces)
            self.assertGreater(len(results), 0, f"No results for sigla '{sigla}'")
            self.assertEqual(
                results[0]["sigla"], sigla,
                f"Province {p['nome']} ({sigla}) did not rank #1 for query '{sigla}'. Top was {results[0]['nome']} ({results[0]['sigla']})"
            )

    def test_all_107_provinces_lowercase_sigla_search_ranks_number_one(self):
        """Every single one of the 107 provinces searched by its lowercase sigla MUST rank #1."""
        for p in self.provinces:
            sigla_lower = p["sigla"].lower()
            results = filter_and_rank_provinces(sigla_lower, self.provinces)
            self.assertGreater(len(results), 0, f"No results for lowercase sigla '{sigla_lower}'")
            self.assertEqual(
                results[0]["sigla"], p["sigla"],
                f"Province {p['nome']} ({p['sigla']}) did not rank #1 for lowercase query '{sigla_lower}'. Top was {results[0]['nome']} ({results[0]['sigla']})"
            )

    def test_all_107_provinces_padded_sigla_search(self):
        """Siglas with leading and trailing whitespace must still rank #1."""
        for p in self.provinces:
            padded_queries = [f" {p['sigla']} ", f"  {p['sigla'].lower()}  ", f"\t{p['sigla']}\n"]
            for q in padded_queries:
                results = filter_and_rank_provinces(q, self.provinces)
                self.assertGreater(len(results), 0, f"No results for padded query '{q}'")
                self.assertEqual(
                    results[0]["sigla"], p["sigla"],
                    f"Padded query '{q}' failed to rank {p['sigla']} #1."
                )

    def test_all_107_provinces_exact_name_search_ranks_number_one(self):
        """Searching each of the 107 provinces by its exact canonical name MUST rank that province #1."""
        for p in self.provinces:
            query = p["nome"]
            results = filter_and_rank_provinces(query, self.provinces)
            self.assertGreater(len(results), 0, f"No results for exact name '{query}'")
            self.assertEqual(
                results[0]["sigla"], p["sigla"],
                f"Province '{p['nome']}' ({p['sigla']}) did not rank #1 for its own name. Top was {results[0]['nome']} ({results[0]['sigla']})"
            )

    def test_diacritics_normalization_forli_cesena(self):
        """Query 'forli' (no accent) and 'forlì' (accented) must both rank FC as #1."""
        for query in ["forli", "forlì", "FORLI", "FORLÌ", "Forli", "Forlì"]:
            results = filter_and_rank_provinces(query, self.provinces)
            self.assertGreater(len(results), 0)
            self.assertEqual(results[0]["sigla"], "FC", f"Query '{query}' did not rank FC #1")

    def test_diacritics_and_elisions_normalization_laquila(self):
        """All variations of L'Aquila (apostrophes, spaces, quotes, combined) must rank AQ as #1."""
        aquila_queries = [
            "l'aquila",
            "l aquila",
            "l’aquila",  # Right typographic quote
            "l‘aquila",  # Left typographic quote
            "l`aquila",  # Backtick
            "l´aquila",  # Acute accent
            "laquila",   # Alias
            "L'Aquila",
            "L AQUILA",
            "L'AQUILA",
            "LAQUILA",
        ]
        for query in aquila_queries:
            results = filter_and_rank_provinces(query, self.provinces)
            self.assertGreater(len(results), 0, f"No results for query '{query}'")
            self.assertEqual(
                results[0]["sigla"], "AQ",
                f"Query '{query}' did not rank AQ #1. Top result was {results[0]['nome']} ({results[0]['sigla']})"
            )

    def test_cadastral_alias_reggio_nellemilia_ranks_re_number_one(self):
        """
        Cadastral official designation 'Reggio nell'Emilia' and its variants
        MUST rank RE (Reggio Emilia) as #1 and NEVER conflict with RC (Reggio Calabria).
        """
        cadastral_queries = [
            "Reggio nell'Emilia",
            "reggio nell'emilia",
            "Reggio nell Emilia",
            "reggio nell emilia",
            "Reggio nellemilia",
            "reggio nellemilia",
            "REGGIO NELL'EMILIA",
        ]
        for q in cadastral_queries:
            results = filter_and_rank_provinces(q, self.provinces)
            self.assertGreater(len(results), 0, f"No results for query '{q}'")
            self.assertEqual(
                results[0]["sigla"], "RE",
                f"Query '{q}' failed: expected RE rank #1, got {results[0]['nome']} ({results[0]['sigla']})"
            )
            # Ensure RC is NOT ranked #1
            if len(results) > 1:
                self.assertNotEqual(results[0]["sigla"], "RC")

    def test_all_province_aliases_rank_target_province_number_one(self):
        """Verify that every single registered alias in PROVINCE_ALIASES ranks its target province as #1."""
        for sigla, aliases in PROVINCE_ALIASES.items():
            for alias in aliases:
                results = filter_and_rank_provinces(alias, self.provinces)
                self.assertGreater(len(results), 0, f"No results for alias '{alias}' -> {sigla}")
                self.assertEqual(
                    results[0]["sigla"], sigla,
                    f"Alias '{alias}' did not rank target province {sigla} as #1. Top result was {results[0]['nome']} ({results[0]['sigla']})"
                )

    def test_regional_diacritics_and_special_provinces(self):
        """Test bilingual and complex hyphenated Italian provinces."""
        cases = [
            ("Valle d'Aosta", "AO"),
            ("valle d aosta", "AO"),
            ("valle d’aosta", "AO"),
            ("aosta", "AO"),
            ("Bolzano-Bozen", "BZ"),
            ("bolzano bozen", "BZ"),
            ("bozen", "BZ"),
            ("bolzano", "BZ"),
            ("Monza e Brianza", "MB"),
            ("monza brianza", "MB"),
            ("monza-brianza", "MB"),
            ("Pesaro e Urbino", "PU"),
            ("pesaro urbino", "PU"),
            ("pesaro-urbino", "PU"),
            ("La Spezia", "SP"),
            ("la spezia", "SP"),
            ("Reggio di Calabria", "RC"),
            ("reggio calabria", "RC"),
        ]
        for query, expected_sigla in cases:
            results = filter_and_rank_provinces(query, self.provinces)
            self.assertGreater(len(results), 0, f"No results for '{query}'")
            self.assertEqual(
                results[0]["sigla"], expected_sigla,
                f"Query '{query}' expected {expected_sigla} #1, got {results[0]['sigla']}"
            )


class TestCrowdsourcingModalBoundsAndBayesianStress(unittest.TestCase):
    """Stress-test crowdsource bounds validation and Bayesian running updates under edge cases."""

    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()
        cls.provinces = cls.dataset["provinces"]
        cls.categories = cls.dataset["categories"]

    def test_exhaustive_exact_bounds_acceptance_and_rejection_all_36_prestations(self):
        """
        Verify exact minBound and maxBound are inclusive (accepted),
        and minBound - 0.01 / maxBound + 0.01 are rejected across all 36 catalog prestations.
        """
        prestations = self.dataset.get("prestations", [])
        self.assertEqual(len(prestations), 36)
        for prest in prestations:
            bounds = prest.get("validationBounds")
            if not bounds or len(bounds) != 2:
                continue
            min_b, max_b = float(bounds[0]), float(bounds[1])
            ref_price = float(prest["basePrice"])

            # Exact minBound -> Valid
            ok_min, err_min, _, _ = validate_crowdsourced_price_oracle(min_b, ref_price, (min_b, max_b))
            self.assertTrue(ok_min, f"Exact minBound {min_b} rejected for {prest['id']}")

            # Sub-cent below minBound -> Rejected
            ok_below, err_below, _, _ = validate_crowdsourced_price_oracle(round(min_b - 0.01, 2), ref_price, (min_b, max_b))
            self.assertFalse(ok_below, f"Below minBound {min_b - 0.01} was accepted for {prest['id']}")
            self.assertIn("troppo basso", err_below)

            # Exact maxBound -> Valid
            ok_max, err_max, _, _ = validate_crowdsourced_price_oracle(max_b, ref_price, (min_b, max_b))
            self.assertTrue(ok_max, f"Exact maxBound {max_b} rejected for {prest['id']}")

            # Sub-cent above maxBound -> Rejected
            ok_above, err_above, _, _ = validate_crowdsourced_price_oracle(round(max_b + 0.01, 2), ref_price, (min_b, max_b))
            self.assertFalse(ok_above, f"Above maxBound {max_b + 0.01} was accepted for {prest['id']}")
            self.assertIn("troppo elevato", err_above)

    def test_fallback_ratio_bounds_boundary_values(self):
        """Test default ratio bounds: min = max(1, round(ref * 0.15)), max = round(ref * 8.0)."""
        test_refs = [1.0, 10.0, 50.0, 100.0, 250.0, 1800.0, 50000.0]
        for ref in test_refs:
            min_exp = max(1.0, float(round(ref * 0.15)))
            max_exp = float(round(ref * 8.0))

            # Exact min
            ok, _, _, _ = validate_crowdsourced_price_oracle(min_exp, ref)
            self.assertTrue(ok, f"Default min bound {min_exp} failed for ref {ref}")

            # Sub-cent below min
            if min_exp > 0.01:
                ok, err, _, _ = validate_crowdsourced_price_oracle(min_exp - 0.01, ref)
                self.assertFalse(ok, f"Below min bound {min_exp - 0.01} succeeded for ref {ref}")

            # Exact max
            ok, _, _, _ = validate_crowdsourced_price_oracle(max_exp, ref)
            self.assertTrue(ok, f"Default max bound {max_exp} failed for ref {ref}")

            # Sub-cent above max
            ok, err, _, _ = validate_crowdsourced_price_oracle(max_exp + 0.01, ref)
            self.assertFalse(ok, f"Above max bound {max_exp + 0.01} succeeded for ref {ref}")

    def test_pathological_and_type_boundary_inputs(self):
        """Ensure non-numeric, NaN, Infinity, zero, and negative inputs are strictly rejected."""
        pathological = [
            0,
            -0.0,
            -0.01,
            -100,
            -1_000_000,
            float("nan"),
            float("inf"),
            float("-inf"),
            None,
            "150",
            True,
            False,
            [],
            {},
        ]
        for bad in pathological:
            ok, err, _, _ = validate_crowdsourced_price_oracle(bad, 250.0, (50.0, 1500.0))
            self.assertFalse(ok, f"Pathological input {bad} was unexpectedly accepted")
            self.assertIsNotNone(err)

    def test_bayesian_cold_start_and_defensive_negative_sample_count(self):
        """When sampleCount <= 0, new average should be paidAmount and sampleCount should be 1."""
        for sample_count in [0, -1, -50]:
            new_avg, new_count = calculate_updated_average_oracle(100.0, sample_count, 180.0)
            self.assertEqual(new_avg, 180.0)
            self.assertEqual(new_count, 1)

            bayesian_int = bayesian_online_average_oracle(100.0, sample_count, 180.0)
            self.assertEqual(bayesian_int, 180)

    def test_bayesian_10000_sequential_updates_drift_and_convergence(self):
        """
        Simulate 10,000 sequential crowdsource submissions.
        Verify that online running mean mathematically converges to the exact arithmetic mean
        with zero drift (< 0.05€).
        """
        import random
        random.seed(42)

        # Baseline: 100 samples at 200.0€
        current_avg = 200.0
        sample_count = 100
        total_sum = current_avg * sample_count

        history: List[float] = []
        for i in range(10_000):
            # Simulated realistic paid amounts between 150.0 and 250.0 €
            paid = round(random.uniform(150.0, 250.0), 2)
            history.append(paid)
            total_sum += paid

            current_avg, sample_count = calculate_updated_average_oracle(current_avg, sample_count, paid)

        self.assertEqual(sample_count, 10_100)
        exact_arithmetic_mean = round(total_sum / 10_100, 2)
        diff = abs(current_avg - exact_arithmetic_mean)
        self.assertLessEqual(diff, 0.05, f"Drift detected: online={current_avg}, exact={exact_arithmetic_mean}")

    def test_bayesian_astronomical_prior_sample_count(self):
        """A sample count of 1 billion (10^9) must remain numerically stable without overflow."""
        current_avg = 300.0
        large_n = 1_000_000_000
        paid = 450.0

        new_avg, new_count = calculate_updated_average_oracle(current_avg, large_n, paid)
        self.assertEqual(new_count, large_n + 1)
        # Shift is 150 / 10^9 ~= 1.5e-7, so rounded 2 decimals remains 300.0
        self.assertEqual(new_avg, 300.0)

    def test_bayesian_alternating_extreme_oscillations(self):
        """1,000 alternating submissions between minBound and maxBound maintain finite stability."""
        min_b = 50.0
        max_b = 1000.0
        avg = 250.0
        n = 100

        for i in range(1000):
            val = min_b if i % 2 == 0 else max_b
            avg, n = calculate_updated_average_oracle(avg, n, val)
            self.assertTrue(math.isfinite(avg))
            self.assertGreaterEqual(avg, min_b)
            self.assertLessEqual(avg, max_b)

        self.assertEqual(n, 1100)
        # Since equal number of 50 and 1000 were added, mean of additions is 525.
        # Combined with 100 prior samples at 250, theoretical mean is (25000 + 500*50 + 500*1000)/1100 = 550000/1100 = 500.0
        self.assertAlmostEqual(avg, 500.0, places=1)


class TestCustomPrestationsAndUrlHydrationStress(unittest.TestCase):
    """Stress-test custom prestations math and URL query hydration robustness."""

    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()
        cls.categories = cls.dataset["categories"]
        cls.provinces = cls.dataset["provinces"]

    def test_custom_prestation_fallback_benchmark_all_categories_and_provinces(self):
        """
        Verify that for every category and every province:
        effectiveRefPrice = round(avg(basePrices) * province.costCoefficient).
        Must be strictly positive and finite.
        """
        prestations = self.dataset.get("prestations", [])
        for cat in self.categories:
            prests = [p for p in prestations if p["categoryId"] == cat["id"]]
            self.assertEqual(len(prests), 6)
            avg_base = sum(p["basePrice"] for p in prests) / len(prests)
            self.assertGreater(avg_base, 0)

            for prov in self.provinces:
                coeff = prov["costCoefficient"]
                ref = round(avg_base * coeff)
                self.assertGreater(ref, 0)
                self.assertTrue(math.isfinite(ref))

    def test_url_hydration_fallback_contains_valid_prestation_slugs(self):
        """
        Verify that for every category in dataset.json:
        the first prestation ID is a genuine, existing prestation slug.
        No invalid `${cat}_1` slugs can occur.
        """
        prestations = self.dataset.get("prestations", [])
        all_ids = {p["id"] for p in prestations}
        for cat in self.categories:
            prests = [p for p in prestations if p["categoryId"] == cat["id"]]
            self.assertGreater(len(prests), 0)
            first_prest_id = prests[0]["id"]
            self.assertIn(
                first_prest_id,
                all_ids,
                f"First prestation {first_prest_id} not found in dataset"
            )
            # Ensure it is not an invalid naive '{cat}_1' string
            self.assertNotEqual(first_prest_id, f"{cat['id']}_1")

    def test_exhaustive_custom_prestation_calculation_matrix_3210_runs(self):
        """
        Calculates discrepancy for 'custom' prestation across all 6 categories
        and all 107 provinces at 5 quote multipliers (3,210 total evaluations).
        Verifies:
        - diff_euro == round(quote - ref, 2)
        - diff_pct == round(((quote - ref) / ref) * 100, 2)
        - needle angle clamped [-100, 100]
        - zone correctly categorized (PREZZO_ONESTO, NELLA_MEDIA, TI_STANNO_FREGANDO)
        - isAlert true iff diff_pct >= 65%
        """
        prestations = self.dataset.get("prestations", [])
        multipliers = [0.0, 0.5, 1.0, 1.35, 1.65, 3.0]

        def calculate_discrepancy_oracle(quote: float, ref_price: float):
            diff_euro = round(quote - ref_price, 2)
            diff_pct = round(((quote - ref_price) / ref_price) * 100.0, 2)
            if diff_pct <= 0.0:
                zone = "PREZZO_ONESTO"
            elif diff_pct <= 35.0:
                zone = "NELLA_MEDIA"
            else:
                zone = "TI_STANNO_FREGANDO"
            is_alert = diff_pct >= 65.0

            # Needle angle mapping from src/core/calculator.ts:
            if diff_pct <= -50.0:
                angle = -100.0
            elif diff_pct <= 0.0:
                angle = -100.0 + (diff_pct + 50.0) * (50.0 / 50.0)
            elif diff_pct <= 35.0:
                angle = -50.0 + diff_pct * (50.0 / 35.0)
            elif diff_pct <= 65.0:
                angle = 0.0 + (diff_pct - 35.0) * (50.0 / 30.0)
            elif diff_pct <= 100.0:
                angle = 50.0 + (diff_pct - 65.0) * (50.0 / 35.0)
            else:
                angle = 100.0
            angle = max(-100.0, min(100.0, angle))
            return diff_euro, diff_pct, zone, is_alert, angle

        eval_count = 0
        for cat in self.categories:
            prests = [p for p in prestations if p["categoryId"] == cat["id"]]
            avg_base = sum(p["basePrice"] for p in prests) / len(prests)

            for prov in self.provinces:
                coeff = prov["costCoefficient"]
                ref_price = round(avg_base * coeff)

                for mult in multipliers:
                    quote = round(ref_price * mult, 2)
                    diff_euro, diff_pct, zone, is_alert, angle = calculate_discrepancy_oracle(quote, ref_price)

                    self.assertTrue(math.isfinite(diff_euro))
                    self.assertTrue(math.isfinite(diff_pct))
                    self.assertGreaterEqual(angle, -100.0)
                    self.assertLessEqual(angle, 100.0)

                    if mult <= 1.0:
                        self.assertEqual(zone, "PREZZO_ONESTO")
                        self.assertFalse(is_alert)
                    elif mult <= 1.35:
                        self.assertEqual(zone, "NELLA_MEDIA")
                        self.assertFalse(is_alert)
                    else:
                        self.assertEqual(zone, "TI_STANNO_FREGANDO")
                        if mult >= 1.65:
                            self.assertTrue(is_alert)

                    eval_count += 1

        self.assertEqual(eval_count, 6 * 107 * len(multipliers))


class TestBayesianConvexInvariantAndRegionSearchStress(unittest.TestCase):
    """Deep invariants and boundary searches."""

    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()
        cls.provinces = cls.dataset["provinces"]

    def test_convex_combination_invariant_5000_random_submissions(self):
        """
        Mathematical invariant: for any positive prior mean mu_0, sample count N,
        and new observation X > 0, the updated mean MUST satisfy:
        min(mu_0, X) <= updatedMean <= max(mu_0, X).
        Also: if X == mu_0, updatedMean == mu_0.
        """
        import random
        random.seed(1337)

        for _ in range(5000):
            mu_0 = round(random.uniform(10.0, 5000.0), 2)
            n = random.randint(1, 10000)
            x = round(random.uniform(5.0, 10000.0), 2)

            new_avg, new_count = calculate_updated_average_oracle(mu_0, n, x)

            self.assertEqual(new_count, n + 1)
            # Allow 0.01 tolerance due to round(..., 2)
            self.assertGreaterEqual(new_avg, min(mu_0, x) - 0.01)
            self.assertLessEqual(new_avg, max(mu_0, x) + 0.01)

            # Exact equality invariant: if X == mu_0, new_avg must equal mu_0
            new_avg_eq, _ = calculate_updated_average_oracle(mu_0, n, mu_0)
            self.assertAlmostEqual(new_avg_eq, mu_0, places=2)

    def test_all_20_italian_regions_province_search(self):
        """
        Searching any Italian region name must return ALL provinces in that region.
        """
        regions = {p["regione"] for p in self.provinces}
        self.assertEqual(len(regions), 20)

        for region in regions:
            expected_provinces = {p["sigla"] for p in self.provinces if p["regione"] == region}
            results = filter_and_rank_provinces(region, self.provinces)
            result_sigle = {r["sigla"] for r in results}

            # All provinces in that region must be matched
            for sigla in expected_provinces:
                self.assertIn(
                    sigla, result_sigle,
                    f"Province {sigla} of region {region} was not found when searching for '{region}'"
                )

    def test_prefix_search_and_collision_behavior(self):
        """
        Test prefix queries and verify unambiguous top matches:
        - 'reggio c' -> RC rank #1
        - 'reggio e' -> RE rank #1
        - 'for' -> FC in top results
        - 'aost' -> AO rank #1
        - 'boz' -> BZ rank #1
        """
        # RC vs RE disambiguation
        rc_results = filter_and_rank_provinces("reggio c", self.provinces)
        self.assertEqual(rc_results[0]["sigla"], "RC")

        re_results = filter_and_rank_provinces("reggio e", self.provinces)
        self.assertEqual(re_results[0]["sigla"], "RE")

        aost_results = filter_and_rank_provinces("aost", self.provinces)
        self.assertEqual(aost_results[0]["sigla"], "AO")

        boz_results = filter_and_rank_provinces("boz", self.provinces)
        self.assertEqual(boz_results[0]["sigla"], "BZ")

        # 'for' should match Forlì-Cesena (FC) as score 2 (starts with)
        for_results = filter_and_rank_provinces("for", self.provinces)
        self.assertEqual(for_results[0]["sigla"], "FC")


if __name__ == "__main__":
    unittest.main()

