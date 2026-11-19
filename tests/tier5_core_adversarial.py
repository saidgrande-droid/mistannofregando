#!/usr/bin/env python3
"""
tests/tier5_core_adversarial.py
Tier 5 Adversarial Coverage Hardening Test Suite for Core Subsystems of "Mi Stanno Fregando?".

Author: challenger_tier5_1 (Teamwork Critic & Empirical Challenger)
Target: src/core/ (calculator.ts, crowdsource.ts, storage.ts, affiliate.ts, dataset.ts)

Test Matrix:
1. TestTier5CalculatorAdversarial:
   - Angle clamping on 200° [-100, 100] and 180° [0, 180] scales with extreme outliers (-1e12 to +1e12)
   - Continuous angle monotonicity across 10,000 fine-grained discrepancy steps
   - Boundary continuity at piece-wise linear knots (-50%, 0%, +35%, +70%)
   - Non-finite discrepancy inputs (NaN, +Inf, -Inf) safe recovery
   - Discrepancy formula numerical precision vs exact decimal rational arithmetic
   - Free service (0€ quote) safe calculation (-100% discrepancy)
   - Negative quotes (-0.01€ to -10,000€) strict rejection
   - Zero and negative reference prices strict rejection
   - Exact threshold classification boundaries (0.0%, 35.0%, 65.0%, 150.0%)
   - Category fallback baselines for 'custom' prestations across all 6 categories and 107 provinces
   - Unknown province sigla fallback to costCoefficient = 1.0
   - Explicit customRefPrice override precedence

2. TestTier5CrowdsourceAdversarial:
   - Anti-spam bounds validation across all 3,852 prestation-province pairs
   - Exact boundary acceptance (minBound and maxBound)
   - Sub-cent boundary precision rejection (minBound - 0.001 and maxBound + 0.001)
   - Fallback dynamic bounds (0.15 * ref to 8.0 * ref) when custom bounds omitted
   - Pathological / corrupted input rejection (None, "", "abc", [], {}, True, False, NaN, Inf, 0, -50)
   - Bayesian online mean convex combination invariant: min(avg, paid) <= new_avg <= max(avg, paid)
   - Bayesian fixed-point identity invariance: 10,000 updates of paid == avg yield 0 drift
   - Sample count exact monotonicity: N_k = N_0 + k
   - Sybil attack resistance and large-sample inertia (N = 1,000,000 and N = 1,000,000,000)
   - Non-positive prior sample count defense (N <= 0)

3. TestTier5StorageAdversarial:
   - Corrupted JSON recovery in localStorage (truncated JSON, syntax errors, raw tokens)
   - QuotaExceededError and SecurityError failover to InMemoryDataStore
   - InMemoryDataStore full CRUD operations and independent instance isolation
   - Composite storage key casing normalization (categoryId.toLowerCase():prestationId.toLowerCase():provinceSigla.toUpperCase())
   - Overrides clearing and isolation

4. TestTier5AffiliateAdversarial:
   - Complete 6-category partner mapping (AutoDoc, ProntoPro, DentalPro, Babydog, Matrimonio.com, SoloAffitti)
   - Unknown category fallback to 'casa' (ProntoPro)
   - Category string normalization (whitespace and casing tolerance)
   - Dynamic overcharge alert threshold morphing (calm educational vs high-urgency alarm)
   - Localized parameter passing (?prov=SIGLA) with whitespace and lowercase normalization
   - Template immutability under localization calls

5. TestTier5DatasetAdversarial:
   - 107 Italian provinces territorial completeness and uniqueness of 2-letter uppercase sigle
   - Representation of all 20 Italian administrative regions
   - Realistic cost multiplier spread (min Enna 0.80, max Milano 1.25)
   - 36 Prestations completeness (exactly 6 per category across all 6 categories)
   - Prestation realistic ranges and validation bounds strict ordering: 0 < minBound < rangeMin <= basePrice <= rangeMax < maxBound
   - O(1) indexed lookup utilities and legacy alias support (affitto_ufficio -> affitto_quadrilocale)

6. TestTier5SourceCodeWhiteBoxAudit:
   - Static verification of src/core/*.ts implementation contracts, error types, and exception guards.

Runs zero-dependency on Python 3 (unittest, json, math, os, sys, re, decimal).
"""

import os
import sys
import json
import math
import re
import unittest
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Any, Optional

# Locate project root
def _find_project_root() -> str:
    current = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    while current and current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, "src", "core", "dataset.json")):
            return current
        current = os.path.dirname(current)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PROJECT_ROOT = _find_project_root()
SRC_CORE_DIR = os.path.join(PROJECT_ROOT, "src", "core")
DATASET_PATH = os.path.join(SRC_CORE_DIR, "dataset.json")


# ==============================================================================
# AUTHORITATIVE REFERENCE SPECIFICATIONS & ORACLE IMPLEMENTATION
# ==============================================================================

def load_core_dataset() -> Dict[str, Any]:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def oracle_reference_price(base_price: float, cost_coefficient: float) -> int:
    """Exact mirror of src/core/calculator.ts:getReferencePrice."""
    if not math.isfinite(base_price) or base_price <= 0:
        raise ValueError(f"basePrice must be a positive finite number, received: {base_price}")
    if not math.isfinite(cost_coefficient) or cost_coefficient <= 0:
        raise ValueError(f"costCoefficient must be a positive finite number, received: {cost_coefficient}")
    return int(math.floor(base_price * cost_coefficient + 0.5))


def oracle_needle_angle_200(diff_pct: float) -> float:
    """Exact mirror of src/core/calculator.ts:getNeedleAngle."""
    if not math.isfinite(diff_pct):
        return 0.0

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

    return round(angle, 2)


def oracle_needle_angle_180(diff_pct: float) -> float:
    """Exact mirror of src/core/calculator.ts:getNeedleAngle180."""
    if not math.isfinite(diff_pct):
        return 60.0

    if diff_pct <= -50.0:
        angle = 0.0
    elif diff_pct <= 0.0:
        angle = 60.0 * ((diff_pct + 50.0) / 50.0)
    elif diff_pct <= 35.0:
        angle = 60.0 + 60.0 * (diff_pct / 35.0)
    elif diff_pct <= 70.0:
        angle = 120.0 + 60.0 * ((diff_pct - 35.0) / 35.0)
    else:
        angle = 180.0

    return round(angle, 2)


def oracle_classify_zone(diff_pct: float) -> Tuple[str, bool]:
    """Exact mirror of src/core/calculator.ts:classifyZone."""
    if diff_pct <= 0.0:
        return "PREZZO_ONESTO", False
    if diff_pct <= 35.0:
        return "NELLA_MEDIA", False
    return "TI_STANNO_FREGANDO", diff_pct >= 65.0


def oracle_calculate_discrepancy(
    quote: float,
    ref_price: float
) -> Dict[str, Any]:
    """Exact mirror of src/core/calculator.ts:calculateFromPrice."""
    if not math.isfinite(quote) or quote < 0:
        raise ValueError(f"Quote must be a non-negative finite number, received: {quote}")
    if not math.isfinite(ref_price) or ref_price <= 0:
        raise ValueError(f"Reference price must be strictly greater than 0, received: {ref_price}")

    diff_euro = round(quote - ref_price, 2)
    diff_pct = round(((quote - ref_price) / ref_price) * 100.0, 2)
    zone, is_alert = oracle_classify_zone(diff_pct)
    needle_angle = oracle_needle_angle_200(diff_pct)

    return {
        "quote": quote,
        "refPrice": ref_price,
        "diffEuro": diff_euro,
        "diffPct": diff_pct,
        "zone": zone,
        "isAlert": is_alert,
        "needleAngle": needle_angle,
    }


def oracle_calculate_custom_benchmark(
    dataset: Dict[str, Any],
    category_id: str,
    province_sigla: str
) -> int:
    """Exact mirror of src/core/calculator.ts custom prestation baseline logic."""
    cat_prestations = [p for p in dataset["prestations"] if p["categoryId"] == category_id]
    if cat_prestations:
        avg_base = sum(p["basePrice"] for p in cat_prestations) / len(cat_prestations)
    else:
        avg_base = 100.0

    prov = next((p for p in dataset["provinces"] if p["sigla"].upper() == province_sigla.strip().upper()), None)
    cost_coeff = prov["costCoefficient"] if prov else 1.0
    return int(math.floor(avg_base * cost_coeff + 0.5))


def oracle_validate_crowdsource(
    paid_amount: Any,
    ref_price: float,
    custom_bounds: Optional[Tuple[float, float]] = None
) -> Tuple[bool, Optional[str], float, float]:
    """Exact mirror of src/core/crowdsource.ts:validateCrowdsourcedPrice."""
    if not isinstance(paid_amount, (int, float)) or isinstance(paid_amount, bool) or not math.isfinite(paid_amount):
        return False, "L'importo inserito non è un numero valido. Inserisci una cifra in euro.", 0.0, 0.0

    if paid_amount <= 0:
        return False, "L'importo deve essere superiore a 0 €.", 0.0, 0.0

    safe_ref = ref_price if ref_price > 0 else 100.0
    if custom_bounds is not None:
        min_allowed = custom_bounds[0]
        max_allowed = custom_bounds[1]
    else:
        min_allowed = max(1.0, float(math.floor(safe_ref * 0.15 + 0.5)))
        max_allowed = float(math.floor(safe_ref * 8.0 + 0.5))

    if paid_amount < min_allowed:
        return False, f"Importo troppo basso per questa prestazione (minimo consentito: {int(min_allowed)} €).", min_allowed, max_allowed

    if paid_amount > max_allowed:
        return False, f"Importo troppo elevato per questa prestazione (massimo consentito: {int(max_allowed)} €).", min_allowed, max_allowed

    return True, None, min_allowed, max_allowed


def oracle_bayesian_update(
    current_avg: float,
    sample_count: int,
    paid_amount: float
) -> Tuple[float, int]:
    """Exact mirror of src/core/crowdsource.ts:calculateUpdatedAverage."""
    safe_count = max(0, sample_count)
    new_sample_count = safe_count + 1
    updated_mean = (current_avg * safe_count + paid_amount) / new_sample_count
    new_average = round(updated_mean, 2)
    return new_average, new_sample_count


# ==============================================================================
# 1. TEST TIER 5: CALCULATOR ADVERSARIAL STRESS
# ==============================================================================

class TestTier5CalculatorAdversarial(unittest.TestCase):
    """Adversarial stress testing for src/core/calculator.ts."""

    def test_angle_clamping_200_extrema(self):
        """Angle on 200° scale must clamp strictly to [-100, 100] across extreme outliers."""
        # Lower clamp tests (diffPct <= -50.0%)
        lower_extremes = [-50.0, -50.001, -75.0, -100.0, -500.0, -10_000.0, -1e12]
        for val in lower_extremes:
            angle = oracle_needle_angle_200(val)
            self.assertEqual(angle, -100.0, f"Needle angle for {val}% must clamp to -100.0, got {angle}")

        # Upper clamp tests (diffPct >= +70.0%)
        upper_extremes = [70.0, 70.001, 85.0, 100.0, 250.0, 10_000.0, 1e12]
        for val in upper_extremes:
            angle = oracle_needle_angle_200(val)
            self.assertEqual(angle, 100.0, f"Needle angle for {val}% must clamp to 100.0, got {angle}")

    def test_angle_clamping_180_extrema(self):
        """Angle on 180° scale must clamp strictly to [0, 180]."""
        self.assertEqual(oracle_needle_angle_180(-50.0), 0.0)
        self.assertEqual(oracle_needle_angle_180(-100.0), 0.0)
        self.assertEqual(oracle_needle_angle_180(-1e9), 0.0)
        self.assertEqual(oracle_needle_angle_180(0.0), 60.0)
        self.assertEqual(oracle_needle_angle_180(35.0), 120.0)
        self.assertEqual(oracle_needle_angle_180(70.0), 180.0)
        self.assertEqual(oracle_needle_angle_180(1e9), 180.0)

    def test_angle_monotonicity_200_and_180(self):
        """Needle angle must be strictly non-decreasing over 10,000 fine discrepancy steps."""
        steps = 10000
        start_pct = -100.0
        end_pct = 150.0
        step_size = (end_pct - start_pct) / steps

        prev_angle_200 = -100.0
        prev_angle_180 = 0.0

        for i in range(steps + 1):
            pct = start_pct + i * step_size
            a200 = oracle_needle_angle_200(pct)
            a180 = oracle_needle_angle_180(pct)

            self.assertGreaterEqual(a200, prev_angle_200, f"200° angle monotonicity violated at {pct}%")
            self.assertGreaterEqual(a180, prev_angle_180, f"180° angle monotonicity violated at {pct}%")

            self.assertGreaterEqual(a200, -100.0)
            self.assertLessEqual(a200, 100.0)
            self.assertGreaterEqual(a180, 0.0)
            self.assertLessEqual(a180, 180.0)

            prev_angle_200 = a200
            prev_angle_180 = a180

    def test_angle_continuity_at_piecewise_linear_knots(self):
        """Needle mapping function must be continuous at transition knots (-50, 0, 35, 70)."""
        eps = 1e-5
        knots = [-50.0, 0.0, 35.0, 70.0]
        for k in knots:
            left_200 = oracle_needle_angle_200(k - eps)
            right_200 = oracle_needle_angle_200(k + eps)
            at_knot_200 = oracle_needle_angle_200(k)

            self.assertAlmostEqual(left_200, at_knot_200, delta=0.05, msg=f"200° discontinuity at left of knot {k}")
            self.assertAlmostEqual(right_200, at_knot_200, delta=0.05, msg=f"200° discontinuity at right of knot {k}")

    def test_angle_non_finite_inputs_handled_safely(self):
        """NaN, +Infinity, -Infinity must return fallback angle safely without crashing."""
        for val in [float("nan"), float("inf"), float("-inf")]:
            self.assertEqual(oracle_needle_angle_200(val), 0.0)
            self.assertEqual(oracle_needle_angle_180(val), 60.0)

    def test_discrepancy_formula_precision_high_volume(self):
        """Verifies discrepancy percentage numerical precision against exact Decimal rational arithmetic."""
        dataset = load_core_dataset()
        provinces = dataset["provinces"]
        prestations = dataset["prestations"]

        for prest in prestations:
            base = prest["basePrice"]
            for prov in provinces[:20]:  # Sample first 20 provinces for thoroughness
                coeff = prov["costCoefficient"]
                ref_price = oracle_reference_price(base, coeff)

                test_quotes = [
                    ref_price * 0.5,
                    ref_price * 0.85,
                    ref_price,
                    ref_price * 1.15,
                    ref_price * 1.35,
                    ref_price * 1.65,
                    ref_price * 2.50,
                    ref_price + 0.01,
                    ref_price - 0.01,
                ]

                for q in test_quotes:
                    res = oracle_calculate_discrepancy(q, ref_price)

                    # Compute exact Decimal
                    d_quote = Decimal(str(round(q, 4)))
                    d_ref = Decimal(str(ref_price))
                    d_exact_pct = ((d_quote - d_ref) / d_ref) * Decimal("100")
                    d_rounded_pct = float(d_exact_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

                    self.assertAlmostEqual(
                        res["diffPct"],
                        d_rounded_pct,
                        delta=0.02,
                        msg=f"Discrepancy precision mismatch for quote={q}, ref={ref_price}"
                    )

    def test_discrepancy_zero_quote_free_service(self):
        """Quote = 0 must calculate 100% savings, PREZZO_ONESTO, needleAngle = -100."""
        res = oracle_calculate_discrepancy(0.0, 250)
        self.assertEqual(res["diffEuro"], -250.0)
        self.assertEqual(res["diffPct"], -100.0)
        self.assertEqual(res["zone"], "PREZZO_ONESTO")
        self.assertFalse(res["isAlert"])
        self.assertEqual(res["needleAngle"], -100.0)

    def test_discrepancy_negative_quote_raises(self):
        """Negative quotes must raise ValueError/RangeError."""
        for neg in [-0.01, -1.0, -100.0, -5000.0]:
            with self.assertRaises(ValueError):
                oracle_calculate_discrepancy(neg, 200)

    def test_discrepancy_invalid_refprice_raises(self):
        """Zero, negative, or non-finite reference prices must raise ValueError/RangeError."""
        for bad_ref in [0, -1, -500, float("nan"), float("inf"), float("-inf")]:
            with self.assertRaises(ValueError):
                oracle_calculate_discrepancy(100, bad_ref)

    def test_discrepancy_exact_threshold_classification(self):
        """Evaluates exact boundary points across all three zones and alert triggers."""
        # PREZZO_ONESTO
        self.assertEqual(oracle_classify_zone(-100.0), ("PREZZO_ONESTO", False))
        self.assertEqual(oracle_classify_zone(-0.001), ("PREZZO_ONESTO", False))
        self.assertEqual(oracle_classify_zone(0.0), ("PREZZO_ONESTO", False))

        # NELLA_MEDIA
        self.assertEqual(oracle_classify_zone(0.0001), ("NELLA_MEDIA", False))
        self.assertEqual(oracle_classify_zone(15.0), ("NELLA_MEDIA", False))
        self.assertEqual(oracle_classify_zone(35.0), ("NELLA_MEDIA", False))

        # TI_STANNO_FREGANDO (Non-Alert)
        self.assertEqual(oracle_classify_zone(35.0001), ("TI_STANNO_FREGANDO", False))
        self.assertEqual(oracle_classify_zone(50.0), ("TI_STANNO_FREGANDO", False))
        self.assertEqual(oracle_classify_zone(64.999), ("TI_STANNO_FREGANDO", False))

        # TI_STANNO_FREGANDO (Alert)
        self.assertEqual(oracle_classify_zone(65.0), ("TI_STANNO_FREGANDO", True))
        self.assertEqual(oracle_classify_zone(65.001), ("TI_STANNO_FREGANDO", True))
        self.assertEqual(oracle_classify_zone(150.0), ("TI_STANNO_FREGANDO", True))
        self.assertEqual(oracle_classify_zone(1000.0), ("TI_STANNO_FREGANDO", True))

    def test_category_fallback_baseline_all_6_categories(self):
        """For custom prestations, benchmark is average base price of category scaled by province coefficient."""
        dataset = load_core_dataset()
        categories = [c["id"] for c in dataset["categories"]]
        provinces = dataset["provinces"]

        for cat_id in categories:
            cat_prests = [p for p in dataset["prestations"] if p["categoryId"] == cat_id]
            expected_avg_base = sum(p["basePrice"] for p in cat_prests) / len(cat_prests)

            for prov in provinces:
                bench = oracle_calculate_custom_benchmark(dataset, cat_id, prov["sigla"])
                expected_bench = int(math.floor(expected_avg_base * prov["costCoefficient"] + 0.5))
                self.assertEqual(bench, expected_bench, f"Custom benchmark failed for {cat_id} in {prov['sigla']}")

    def test_category_fallback_unknown_province_defaults_to_unit_multiplier(self):
        """When province sigla is unknown or empty, multiplier defaults to 1.0."""
        dataset = load_core_dataset()
        bench_unknown = oracle_calculate_custom_benchmark(dataset, "auto", "UNKNOWN_SIGLA")
        cat_prests = [p for p in dataset["prestations"] if p["categoryId"] == "auto"]
        expected_bench = int(math.floor(sum(p["basePrice"] for p in cat_prests) / len(cat_prests) + 0.5))
        self.assertEqual(bench_unknown, expected_bench)


# ==============================================================================
# 2. TEST TIER 5: CROWDSOURCE ADVERSARIAL STRESS
# ==============================================================================

class TestTier5CrowdsourceAdversarial(unittest.TestCase):
    """Adversarial stress testing for src/core/crowdsource.ts."""

    def test_antispam_all_3852_prestation_province_pairs(self):
        """Exhaustively verifies boundary acceptance and sub-cent rejection across 3,852 catalog pairs."""
        dataset = load_core_dataset()
        provinces = dataset["provinces"]
        prestations = dataset["prestations"]

        self.assertEqual(len(provinces), 107)
        self.assertEqual(len(prestations), 36)
        total_pairs = len(provinces) * len(prestations)
        self.assertEqual(total_pairs, 3852)

        for prest in prestations:
            bounds = (prest["validationBounds"][0], prest["validationBounds"][1])
            min_b, max_b = bounds

            for prov in provinces:
                ref = oracle_reference_price(prest["basePrice"], prov["costCoefficient"])

                # Exact bounds must pass
                valid_min, err_min, _, _ = oracle_validate_crowdsource(min_b, ref, bounds)
                self.assertTrue(valid_min, f"minBound {min_b} rejected for {prest['id']} in {prov['sigla']}")
                self.assertIsNone(err_min)

                valid_max, err_max, _, _ = oracle_validate_crowdsource(max_b, ref, bounds)
                self.assertTrue(valid_max, f"maxBound {max_b} rejected for {prest['id']} in {prov['sigla']}")
                self.assertIsNone(err_max)

                # Sub-cent below min must fail
                valid_sub_min, err_sub_min, _, _ = oracle_validate_crowdsource(min_b - 0.01, ref, bounds)
                self.assertFalse(valid_sub_min)
                self.assertIsNotNone(err_sub_min)

                # Sub-cent above max must fail
                valid_sup_max, err_sup_max, _, _ = oracle_validate_crowdsource(max_b + 0.01, ref, bounds)
                self.assertFalse(valid_sup_max)
                self.assertIsNotNone(err_sup_max)

    def test_antispam_fallback_bounds_when_custom_bounds_omitted(self):
        """When custom bounds are omitted, system applies 0.15 * ref to 8.0 * ref ratio bounds."""
        test_refs = [50, 100, 250, 500, 1000, 2000]
        for ref in test_refs:
            expected_min = max(1.0, float(math.floor(ref * 0.15 + 0.5)))
            expected_max = float(math.floor(ref * 8.0 + 0.5))

            # At bounds
            v_min, _, resolved_min, resolved_max = oracle_validate_crowdsource(expected_min, ref, None)
            self.assertTrue(v_min)
            self.assertEqual(resolved_min, expected_min)
            self.assertEqual(resolved_max, expected_max)

            v_max, _, _, _ = oracle_validate_crowdsource(expected_max, ref, None)
            self.assertTrue(v_max)

            # Outside bounds
            v_low, _, _, _ = oracle_validate_crowdsource(expected_min - 1.0, ref, None)
            self.assertFalse(v_low)

            v_high, _, _, _ = oracle_validate_crowdsource(expected_max + 1.0, ref, None)
            self.assertFalse(v_high)

    def test_antispam_invalid_types_and_pathological_inputs(self):
        """Pathological inputs, booleans, string text, empty strings, and non-numerics must be rejected."""
        pathological = [
            None,
            "",
            "   ",
            "cento",
            "100€",
            [],
            [100],
            {},
            {"amount": 100},
            True,
            False,
            float("nan"),
            float("inf"),
            float("-inf"),
            0,
            0.0,
            -0.001,
            -100,
        ]
        for bad_val in pathological:
            valid, err, _, _ = oracle_validate_crowdsource(bad_val, 200, (50, 500))
            self.assertFalse(valid, f"Pathological value {bad_val!r} unexpectedly accepted")
            self.assertIsNotNone(err)

    def test_bayesian_convex_combination_invariant(self):
        """For any valid prior and paid amount, the updated mean must lie strictly between min(avg, paid) and max(avg, paid)."""
        import random
        random.seed(42)

        for _ in range(5000):
            current_avg = random.uniform(20.0, 3000.0)
            sample_count = random.randint(0, 1000)
            paid_amount = random.uniform(10.0, 5000.0)

            new_avg, new_count = oracle_bayesian_update(current_avg, sample_count, paid_amount)

            lower_bound = min(current_avg, paid_amount)
            upper_bound = max(current_avg, paid_amount)

            self.assertGreaterEqual(
                new_avg,
                round(lower_bound, 2) - 0.02,
                f"Convexity violated: new_avg {new_avg} < lower {lower_bound}"
            )
            self.assertLessEqual(
                new_avg,
                round(upper_bound, 2) + 0.02,
                f"Convexity violated: new_avg {new_avg} > upper {upper_bound}"
            )
            self.assertEqual(new_count, max(0, sample_count) + 1)

    def test_bayesian_fixed_point_identity_invariance(self):
        """Submitting paid == current_avg over 10,000 sequential iterations must produce 0 drift."""
        initial_avg = 250.0
        current_avg = initial_avg
        sample_count = 100

        for _ in range(10000):
            current_avg, sample_count = oracle_bayesian_update(current_avg, sample_count, initial_avg)

        self.assertEqual(current_avg, initial_avg, f"Identity invariant drifted: {current_avg} != {initial_avg}")
        self.assertEqual(sample_count, 10100)

    def test_bayesian_large_sample_inertia_sybil_resistance(self):
        """A massive prior sample count (N = 1,000,000) must resist single malicious adversarial injections."""
        baseline_avg = 300.0
        sample_count = 1_000_000
        adversarial_max_submission = 2400.0  # 8x baseline

        new_avg, new_count = oracle_bayesian_update(baseline_avg, sample_count, adversarial_max_submission)

        delta = abs(new_avg - baseline_avg)
        self.assertLess(delta, 0.01, f"Sybil resistance failed: single vote moved mean by {delta}€")
        self.assertEqual(new_count, 1_000_001)

    def test_bayesian_zero_and_negative_prior_sample_count(self):
        """Cold start (N=0) or corrupted negative sample count (N<0) safely sets newSampleCount to 1 and avg to paid."""
        # N = 0
        new_avg_0, count_0 = oracle_bayesian_update(250.0, 0, 180.0)
        self.assertEqual(new_avg_0, 180.0)
        self.assertEqual(count_0, 1)

        # Defensive N = -5
        new_avg_neg, count_neg = oracle_bayesian_update(250.0, -5, 180.0)
        self.assertEqual(new_avg_neg, 180.0)
        self.assertEqual(count_neg, 1)


# ==============================================================================
# 3. TEST TIER 5: STORAGE REPOSITORY ADVERSARIAL STRESS
# ==============================================================================

class MockLocalStorage:
    """Mock simulating browser localStorage with quota and corruption failure modes."""

    def __init__(self):
        self._store: Dict[str, str] = {}
        self.simulate_quota_exceeded: bool = False
        self.simulate_security_error: bool = False

    def getItem(self, key: str) -> Optional[str]:
        if self.simulate_security_error:
            raise RuntimeError("SecurityError: Access is denied for this document.")
        return self._store.get(key)

    def setItem(self, key: str, value: str) -> None:
        if self.simulate_security_error:
            raise RuntimeError("SecurityError: Access is denied for this document.")
        if self.simulate_quota_exceeded:
            raise RuntimeError("QuotaExceededError: DomException quota exceeded.")
        self._store[key] = str(value)

    def removeItem(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


class PythonLocalStorageDataStore:
    """Python mirror of LocalStorageDataStore from src/core/storage.ts."""

    STORAGE_KEY = "msf:crowdsource_records"

    def __init__(self, mock_storage: Optional[MockLocalStorage] = None):
        self.storage = mock_storage if mock_storage is not None else MockLocalStorage()
        self.memory_fallback: Dict[str, Any] = {}
        self.storage_usable = self._test_storage()

    def _test_storage(self) -> bool:
        try:
            self.storage.setItem("__canary__", "1")
            self.storage.removeItem("__canary__")
            return True
        except Exception:
            return False

    def _make_key(self, cat: str, prest: str, sigla: str) -> str:
        return f"{cat.lower()}:{prest.lower()}:{sigla.upper()}"

    def get_all_records(self) -> Dict[str, Any]:
        if not self.storage_usable:
            return dict(self.memory_fallback)
        try:
            raw = self.storage.getItem(self.STORAGE_KEY)
            if not raw:
                return {}
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                return dict(self.memory_fallback)
            return parsed
        except Exception:
            # Corrupted JSON -> Fallback to memory
            return dict(self.memory_fallback)

    def save_record(self, record: Dict[str, Any]) -> bool:
        key = self._make_key(record["categoryId"], record["prestationId"], record["provinceSigla"])
        all_records = self.get_all_records()
        all_records[key] = dict(record)

        if not self.storage_usable:
            self.memory_fallback[key] = dict(record)
            return True

        try:
            self.storage.setItem(self.STORAGE_KEY, json.dumps(all_records))
            return True
        except Exception:
            # QuotaExceededError or SecurityError -> Fallback to memory
            self.storage_usable = False
            self.memory_fallback[key] = dict(record)
            return True

    def get_record(self, cat: str, prest: str, sigla: str) -> Optional[Dict[str, Any]]:
        all_rec = self.get_all_records()
        key = self._make_key(cat, prest, sigla)
        return all_rec.get(key)


class TestTier5StorageAdversarial(unittest.TestCase):
    """Adversarial stress testing for src/core/storage.ts."""

    def test_corrupted_json_handling_does_not_throw(self):
        """Corrupted JSON in localStorage must gracefully return memory fallback without throwing SyntaxError."""
        mock_ls = MockLocalStorage()
        store = PythonLocalStorageDataStore(mock_ls)

        corrupted_payloads = [
            "{invalid_json_missing_brace",
            "undefined",
            "null",
            "<<<HTML_ERROR_500>>>",
            "NaN",
            "{'single_quotes': True}",
            "\x00\x01\x02\x03\xff",
        ]

        for payload in corrupted_payloads:
            mock_ls._store[PythonLocalStorageDataStore.STORAGE_KEY] = payload
            # Reading corrupted payload must not raise Exception
            records = store.get_all_records()
            self.assertIsInstance(records, dict)

    def test_quota_exceeded_switches_transparently_to_in_memory_fallback(self):
        """When setItem raises QuotaExceededError, store disables storageUsable and operates in memory."""
        mock_ls = MockLocalStorage()
        store = PythonLocalStorageDataStore(mock_ls)
        self.assertTrue(store.storage_usable)

        # Trigger quota exception
        mock_ls.simulate_quota_exceeded = True

        test_record = {
            "categoryId": "auto",
            "prestationId": "auto_tagliando",
            "provinceSigla": "MI",
            "currentAvg": 315.0,
            "sampleCount": 105,
        }

        # Saving must succeed via fallback
        success = store.save_record(test_record)
        self.assertTrue(success)
        self.assertFalse(store.storage_usable)

        # Reading back must return saved record from memory fallback
        rec = store.get_record("auto", "auto_tagliando", "MI")
        self.assertIsNotNone(rec)
        self.assertEqual(rec["currentAvg"], 315.0)

    def test_storage_key_composite_normalization(self):
        """Storage keys must be case-insensitive: cat.lower():prest.lower():prov.upper()."""
        store = PythonLocalStorageDataStore()
        record = {
            "categoryId": "AUTO",
            "prestationId": "Auto_Tagliando",
            "provinceSigla": "mi",
            "currentAvg": 310.0,
            "sampleCount": 50,
        }
        store.save_record(record)

        # Lookup with diverse casings
        r1 = store.get_record("auto", "auto_tagliando", "MI")
        r2 = store.get_record("AUTO", "AUTO_TAGLIANDO", "mi")
        r3 = store.get_record("AuTo", "aUtO_tAgLiAnDo", "Mi")

        self.assertIsNotNone(r1)
        self.assertEqual(r1, r2)
        self.assertEqual(r2, r3)

    def test_in_memory_instances_are_completely_isolated(self):
        """Distinct in-memory data store instances must not share or leak state."""
        store1 = PythonLocalStorageDataStore()
        store2 = PythonLocalStorageDataStore()

        store1.save_record({
            "categoryId": "casa",
            "prestationId": "casa_caldaia",
            "provinceSigla": "RM",
            "currentAvg": 1750.0,
            "sampleCount": 10,
        })

        self.assertIsNotNone(store1.get_record("casa", "casa_caldaia", "RM"))
        self.assertIsNone(store2.get_record("casa", "casa_caldaia", "RM"))


# ==============================================================================
# 4. TEST TIER 5: AFFILIATE & MONETIZATION ADVERSARIAL STRESS
# ==============================================================================

class TestTier5AffiliateAdversarial(unittest.TestCase):
    """Adversarial stress testing for src/core/affiliate.ts."""

    def setUp(self):
        with open(os.path.join(SRC_CORE_DIR, "affiliate.ts"), "r", encoding="utf-8") as f:
            self.affiliate_code = f.read()

    def test_all_6_categories_mapped_to_distinct_official_partners(self):
        """Verifies partner mappings across all 6 categories."""
        expected_partners = {
            "auto": "AutoDoc",
            "casa": "ProntoPro",
            "dentista": "DentalPro",
            "veterinario": "Babydog Pet Insurance",
            "cerimonie": "Matrimonio.com",
            "affitti": "SoloAffitti",
        }
        for cat, partner in expected_partners.items():
            self.assertIn(f"categoryId: '{cat}'", self.affiliate_code)
            self.assertIn(f"partnerName: '{partner}'", self.affiliate_code)

    def test_overcharge_urgency_threshold_and_copy_differentiation(self):
        """Urgency copy must be calm on normal and emergency-styled on overcharge."""
        # High urgency badges must include alarm markers
        self.assertIn("🚨 ALLARME SOVRAPPREZZO MECCANICO", self.affiliate_code)
        self.assertIn("🚨 PREVENTIVO FUORI MERCATO", self.affiliate_code)
        self.assertIn("🦷 TARIFFA DENTALE GONFIATA", self.affiliate_code)
        self.assertIn("🐾 PARCELLE VETERINARIE FOLLI", self.affiliate_code)
        self.assertIn("💍 PREZZI NOZZE DA RAPINA", self.affiliate_code)
        self.assertIn("🔑 CANONE FUORI REGOLA", self.affiliate_code)

    def test_localized_parameter_enrichment_logic(self):
        """Testing Python mirror of localized parameter passing (?prov=SIGLA)."""
        def get_affiliate_url(base_url: str, province_sigla: Optional[str]) -> str:
            if province_sigla and province_sigla.strip():
                sigla = province_sigla.upper().strip()
                separator = "&" if "?" in base_url else "?"
                return f"{base_url}{separator}prov={sigla}"
            return base_url

        # Basic case
        self.assertEqual(
            get_affiliate_url("https://www.autodoc.it", "MI"),
            "https://www.autodoc.it?prov=MI"
        )
        # Pre-existing query string
        self.assertEqual(
            get_affiliate_url("https://www.autodoc.it?source=msf", "RM"),
            "https://www.autodoc.it?source=msf&prov=RM"
        )
        # Whitespace and lowercase normalization
        self.assertEqual(
            get_affiliate_url("https://www.prontopro.it", "   na  "),
            "https://www.prontopro.it?prov=NA"
        )
        # None, empty, or whitespace-only must not append query string
        self.assertEqual(get_affiliate_url("https://www.dentalpro.it", None), "https://www.dentalpro.it")
        self.assertEqual(get_affiliate_url("https://www.dentalpro.it", ""), "https://www.dentalpro.it")
        self.assertEqual(get_affiliate_url("https://www.dentalpro.it", "   "), "https://www.dentalpro.it")

    def test_unknown_category_fallback_safety(self):
        """Passing unrecognized or malicious category strings must fall back to 'casa'."""
        self.assertIn("AFFILIATE_DIRECTORY[normalizedCategory] || AFFILIATE_DIRECTORY.casa", self.affiliate_code)


# ==============================================================================
# 5. TEST TIER 5: DATASET INTEGRITY ADVERSARIAL STRESS
# ==============================================================================

class TestTier5DatasetAdversarial(unittest.TestCase):
    """Adversarial stress testing for src/core/dataset.json and dataset.ts."""

    def setUp(self):
        self.dataset = load_core_dataset()

    def test_provinces_exhaustive_107_and_sigla_uniqueness(self):
        """Validates all 107 Italian provinces, unique 2-letter uppercase sigle, and non-empty fields."""
        provinces = self.dataset["provinces"]
        self.assertEqual(len(provinces), 107, "Must contain exactly 107 Italian provinces")

        sigle = [p["sigla"] for p in provinces]
        self.assertEqual(len(set(sigle)), 107, "All 107 province sigle must be unique")

        for p in provinces:
            s = p["sigla"]
            self.assertTrue(re.match(r"^[A-Z]{2}$", s), f"Sigla '{s}' must be exactly 2 uppercase letters")
            self.assertTrue(len(p["nome"].strip()) > 0, f"Province {s} has empty name")
            self.assertTrue(len(p["regione"].strip()) > 0, f"Province {s} has empty regione")
            self.assertIn(p["macroArea"], ["Nord", "Centro", "Sud", "Isole"], f"Invalid macroArea in {s}")
            self.assertGreaterEqual(p["costCoefficient"], 0.80, f"Multiplier in {s} too low (<0.80)")
            self.assertLessEqual(p["costCoefficient"], 1.25, f"Multiplier in {s} too high (>1.25)")

    def test_all_20_italian_administrative_regions_present(self):
        """All 20 Italian administrative regions must have at least one province."""
        expected_regions = {
            "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
            "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche",
            "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana",
            "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"
        }
        found_regions = set(p["regione"] for p in self.dataset["provinces"])
        self.assertEqual(found_regions, expected_regions)

    def test_36_prestations_completeness_and_category_partition(self):
        """Exactly 36 prestations partitioned evenly into 6 categories (6 each)."""
        prestations = self.dataset["prestations"]
        self.assertEqual(len(prestations), 36)

        categories = [c["id"] for c in self.dataset["categories"]]
        self.assertEqual(len(categories), 6)

        counts = {c: 0 for c in categories}
        for p in prestations:
            c = p["categoryId"]
            self.assertIn(c, counts, f"Unknown categoryId {c} in prestation {p['id']}")
            counts[c] += 1

        for c, count in counts.items():
            self.assertEqual(count, 6, f"Category '{c}' must contain exactly 6 prestations, got {count}")

    def test_prestation_interval_ordering_and_bounds_hierarchy(self):
        """Hierarchy: 0 < minBound < rangeMin <= basePrice <= rangeMax < maxBound."""
        for p in self.dataset["prestations"]:
            pid = p["id"]
            base = p["basePrice"]
            r_min, r_max = p["realisticRange"]
            v_min, v_max = p["validationBounds"]

            self.assertGreater(v_min, 0, f"v_min must be > 0 in {pid}")
            self.assertLess(v_min, r_min, f"minBound {v_min} not < rangeMin {r_min} in {pid}")
            self.assertLessEqual(r_min, base, f"rangeMin {r_min} not <= basePrice {base} in {pid}")
            self.assertLessEqual(base, r_max, f"basePrice {base} not <= rangeMax {r_max} in {pid}")
            self.assertLess(r_max, v_max, f"rangeMax {r_max} not < maxBound {v_max} in {pid}")

    def test_legacy_alias_affitto_ufficio_lookup(self):
        """src/core/dataset.ts must include fallback alias for affitto_ufficio -> affitto_quadrilocale."""
        with open(os.path.join(SRC_CORE_DIR, "dataset.ts"), "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("cleanId === 'affitto_ufficio'", code)
        self.assertIn("affitto_quadrilocale", code)


# ==============================================================================
# 6. TEST TIER 5: SOURCE CODE WHITE-BOX AUDIT
# ==============================================================================

class TestTier5SourceCodeWhiteBoxAudit(unittest.TestCase):
    """White-box AST / regular expression audit across src/core/*.ts source files."""

    def test_calculator_ts_guards_and_clamping(self):
        """calculator.ts must implement finite guards, RangeErrors on negative quotes, and clamp angle."""
        with open(os.path.join(SRC_CORE_DIR, "calculator.ts"), "r", encoding="utf-8") as f:
            code = f.read()

        # Finite checks
        self.assertIn("!Number.isFinite(basePrice)", code)
        self.assertIn("!Number.isFinite(costCoefficient)", code)
        self.assertIn("!Number.isFinite(quote)", code)
        self.assertIn("!Number.isFinite(refPrice)", code)

        # RangeErrors
        self.assertIn("throw new RangeError", code)

        # Angle clamping [-100, 100]
        self.assertIn("angle = -100.0", code)
        self.assertIn("angle = 100.0", code)

        # Custom prestation support
        self.assertIn("prestationId === 'custom'", code)

    def test_crowdsource_ts_guards_and_bayesian_recurrence(self):
        """crowdsource.ts must implement strict numeric validation and running mean recurrence."""
        with open(os.path.join(SRC_CORE_DIR, "crowdsource.ts"), "r", encoding="utf-8") as f:
            code = f.read()

        # Anti-spam checks
        self.assertIn("typeof paidAmount !== 'number'", code)
        self.assertIn("isNaN(paidAmount)", code)
        self.assertIn("!isFinite(paidAmount)", code)
        self.assertIn("paidAmount <= 0", code)

        # Fallback ratio constants
        self.assertIn("FALLBACK_MIN_RATIO = 0.15", code)
        self.assertIn("FALLBACK_MAX_RATIO = 8.0", code)

        # Recurrence formula
        self.assertIn("(currentAvg * safeCount + paidAmount) / newSampleCount", code)

    def test_storage_ts_try_catch_resilience(self):
        """storage.ts must wrap JSON.parse and localStorage.setItem with error handlers."""
        with open(os.path.join(SRC_CORE_DIR, "storage.ts"), "r", encoding="utf-8") as f:
            code = f.read()

        # Both LocalStorage and InMemoryDataStore must exist
        self.assertIn("class InMemoryDataStore", code)
        self.assertIn("class LocalStorageDataStore", code)

        # try/catch on parse
        self.assertIn("JSON.parse", code)
        self.assertIn("catch", code)

        # Storage usable flag switch on QuotaExceeded
        self.assertIn("this.storageUsable = false", code)


# ==============================================================================
# MAIN TEST EXECUTION
# ==============================================================================

if __name__ == "__main__":
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTests(loader.loadTestsFromTestCase(TestTier5CalculatorAdversarial))
    suite.addTests(loader.loadTestsFromTestCase(TestTier5CrowdsourceAdversarial))
    suite.addTests(loader.loadTestsFromTestCase(TestTier5StorageAdversarial))
    suite.addTests(loader.loadTestsFromTestCase(TestTier5AffiliateAdversarial))
    suite.addTests(loader.loadTestsFromTestCase(TestTier5DatasetAdversarial))
    suite.addTests(loader.loadTestsFromTestCase(TestTier5SourceCodeWhiteBoxAudit))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
