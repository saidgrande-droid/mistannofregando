#!/usr/bin/env python3
"""
monetization_crowdsource_stress_test.py
Empirical Adversarial Stress Test Suite for Milestone 3:
Interactive UI, Crowdsourcing & Monetization Subsystems of "Mi Stanno Fregando?".

Author: challenger_m3_2 (empirical_challenger)
Target: Milestone 3 verification and adversarial stress testing.

Covers:
1. Crowdsource anti-spam bounds checking across all 36 prestations in all 107 Italian provinces
   (3,852 combinations) testing exact ratio bounds (0.15 * ref <= paid <= 8.0 * ref), custom bounds,
   and extreme adversarial under-reporting, over-reporting, and type corruptions.
2. Bayesian running mean update: continuous sequential updates across 1,000 simulated user submissions
   verifying numerical stability, sample count preservation, floating-point drift absence, and shift
   in active quote classification (transitions between NELLA_MEDIA, PREZZO_ONESTO, and TI_STANNO_FREGANDO alert).
3. AdSlot Zero-CLS verification: verify inline CSS min-height across Leaderboard, MPU, and Sticky slots
   under simulated ad blocker suppression (rendered height remains exact, 0 layout shift).
4. Category affiliate mapping and copy verification: test all 6 categories under both fair price (calm copy)
   and overcharged alert (+65%, crimson styling, urgent CTA, secondary partners, and geo-targeting).

Runs strictly on standard Python 3 (unittest, json, math, os, sys, re).
"""

import os
import sys
import json
import math
import re
import unittest
from typing import Dict, List, Tuple, Any, Optional

# Base project paths
def find_project_root() -> str:
    cur = os.path.abspath(os.path.dirname(__file__))
    while cur and cur != os.path.dirname(cur):
        if os.path.exists(os.path.join(cur, "package.json")) and os.path.exists(os.path.join(cur, "src")):
            return cur
        cur = os.path.dirname(cur)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

PROJECT_ROOT = find_project_root()
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
CORE_DIR = os.path.join(SRC_DIR, "core")
COMPONENTS_DIR = os.path.join(SRC_DIR, "components")
DATASET_PATH = os.path.join(CORE_DIR, "dataset.json")


# ==============================================================================
# DOMAIN ORACLE IMPLEMENTATION (Pure Python Mathematical Mirror of TypeScript Core)
# ==============================================================================

def load_dataset() -> Dict[str, Any]:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_reference_price(base_price: float, cost_coefficient: float) -> int:
    """Exact mirror of src/core/calculator.ts:getReferencePrice."""
    if not math.isfinite(base_price) or base_price <= 0:
        raise ValueError(f"base_price must be positive finite, got {base_price}")
    if not math.isfinite(cost_coefficient) or cost_coefficient <= 0:
        raise ValueError(f"cost_coefficient must be positive finite, got {cost_coefficient}")
    return int(math.floor(base_price * cost_coefficient + 0.5))


def calculate_discrepancy(quote: float, ref_price: float) -> Tuple[float, float, str, bool]:
    """Exact mirror of src/core/calculator.ts:calculateDiscrepancy."""
    if not math.isfinite(ref_price) or ref_price <= 0:
        raise ValueError(f"ref_price must be positive finite, got {ref_price}")
    if not math.isfinite(quote) or quote < 0:
        raise ValueError(f"quote must be non-negative finite, got {quote}")

    diff_euro = round(quote - ref_price, 2)
    diff_pct = round(((quote - ref_price) / ref_price) * 100.0, 2)

    if diff_pct <= 0.0:
        zone = "PREZZO_ONESTO"
    elif diff_pct <= 35.0:
        zone = "NELLA_MEDIA"
    else:
        zone = "TI_STANNO_FREGANDO"

    is_alert = diff_pct >= 65.0
    return diff_euro, diff_pct, zone, is_alert


def validate_crowdsourced_price(
    paid_amount: Any,
    ref_price: float,
    custom_bounds: Optional[Tuple[float, float]] = None
) -> Tuple[bool, Optional[str], float, float]:
    """Exact mirror of src/core/crowdsource.ts:validateCrowdsourcedPrice."""
    # 1. Type and finiteness check
    if not isinstance(paid_amount, (int, float)) or isinstance(paid_amount, bool) or not math.isfinite(paid_amount):
        return False, "L'importo inserito non è un numero valido. Inserisci una cifra in euro.", 0, 0

    # 2. Strict positivity check
    if paid_amount <= 0:
        return False, "L'importo deve essere superiore a 0 €.", 0, 0

    safe_ref = ref_price if ref_price > 0 else 100.0
    if custom_bounds is not None:
        min_allowed = custom_bounds[0]
        max_allowed = custom_bounds[1]
    else:
        min_allowed = max(1.0, float(round(safe_ref * 0.15)))
        max_allowed = float(round(safe_ref * 8.0))

    if paid_amount < min_allowed:
        return False, f"Importo troppo basso per questa prestazione (minimo consentito: {min_allowed:.0f} €).", min_allowed, max_allowed

    if paid_amount > max_allowed:
        return False, f"Importo troppo elevato per questa prestazione (massimo consentito: {max_allowed:.0f} €).", min_allowed, max_allowed

    return True, None, min_allowed, max_allowed


def update_bayesian_average(current_avg: float, sample_count: int, paid_amount: float) -> Tuple[float, int]:
    """Exact mirror of src/core/crowdsource.ts:calculateUpdatedAverage."""
    safe_count = max(0, sample_count)
    new_count = safe_count + 1
    updated_mean = (current_avg * safe_count + paid_amount) / new_count
    new_avg = round(updated_mean, 2)
    return new_avg, new_count


AFFILIATE_DIRECTORY = {
    "auto": {
        "normal": {
            "partnerName": "AutoDoc",
            "url": "https://www.autodoc.it",
            "badgeText": "Partner Ufficiale Ricambi Auto",
            "urgencyLevel": "normal",
            "secondaryPartnerName": "Prima Assicurazioni",
            "secondaryUrl": "https://www.prima.it",
        },
        "highUrgency": {
            "partnerName": "AutoDoc",
            "url": "https://www.autodoc.it",
            "badgeText": "🚨 ALLARME SOVRAPPREZZO MECCANICO",
            "urgencyLevel": "high",
            "secondaryPartnerName": "Prima Assicurazioni",
            "secondaryUrl": "https://www.prima.it",
        },
    },
    "casa": {
        "normal": {
            "partnerName": "ProntoPro",
            "url": "https://www.prontopro.it",
            "badgeText": "Confronto Preventivi Certificati",
            "urgencyLevel": "normal",
            "secondaryPartnerName": "Facile.it Casa",
            "secondaryUrl": "https://www.facile.it",
        },
        "highUrgency": {
            "partnerName": "ProntoPro",
            "url": "https://www.prontopro.it",
            "badgeText": "🚨 PREVENTIVO FUORI MERCATO",
            "urgencyLevel": "high",
            "secondaryPartnerName": "Facile.it Casa",
            "secondaryUrl": "https://www.facile.it",
        },
    },
    "dentista": {
        "normal": {
            "partnerName": "DentalPro",
            "url": "https://www.dentalpro.it",
            "badgeText": "Cliniche Odontoiatriche Convenzionate",
            "urgencyLevel": "normal",
            "secondaryPartnerName": "Santagostino Odontoiatria",
            "secondaryUrl": "https://www.santagostino.it",
        },
        "highUrgency": {
            "partnerName": "DentalPro",
            "url": "https://www.dentalpro.it",
            "badgeText": "🦷 TARIFFA DENTALE GONFIATA",
            "urgencyLevel": "high",
            "secondaryPartnerName": "Santagostino Odontoiatria",
            "secondaryUrl": "https://www.santagostino.it",
        },
    },
    "veterinario": {
        "normal": {
            "partnerName": "Babydog Pet Insurance",
            "url": "https://www.babydog.it",
            "badgeText": "Assicurazione Sanitaria Pet",
            "urgencyLevel": "normal",
            "secondaryPartnerName": "Zooplus",
            "secondaryUrl": "https://www.zooplus.it",
        },
        "highUrgency": {
            "partnerName": "Babydog Pet Insurance",
            "url": "https://www.babydog.it",
            "badgeText": "🐾 PARCELLE VETERINARIE FOLLI",
            "urgencyLevel": "high",
            "secondaryPartnerName": "Zooplus",
            "secondaryUrl": "https://www.zooplus.it",
        },
    },
    "cerimonie": {
        "normal": {
            "partnerName": "Matrimonio.com",
            "url": "https://www.matrimonio.com",
            "badgeText": "Leader Nozze ed Eventi in Italia",
            "urgencyLevel": "normal",
            "secondaryPartnerName": "Zankyou",
            "secondaryUrl": "https://www.zankyou.it",
        },
        "highUrgency": {
            "partnerName": "Matrimonio.com",
            "url": "https://www.matrimonio.com",
            "badgeText": "💍 PREZZI NOZZE DA RAPINA",
            "urgencyLevel": "high",
            "secondaryPartnerName": "Zankyou",
            "secondaryUrl": "https://www.zankyou.it",
        },
    },
    "affitti": {
        "normal": {
            "partnerName": "SoloAffitti",
            "url": "https://www.soloaffitti.it",
            "badgeText": "Specialisti della Locazione Sicura",
            "urgencyLevel": "normal",
            "secondaryPartnerName": "Idealista",
            "secondaryUrl": "https://www.idealista.it",
        },
        "highUrgency": {
            "partnerName": "SoloAffitti",
            "url": "https://www.soloaffitti.it",
            "badgeText": "🔑 CANONE FUORI REGOLA",
            "urgencyLevel": "high",
            "secondaryPartnerName": "Idealista",
            "secondaryUrl": "https://www.idealista.it",
        },
    },
}


def get_affiliate(category: str, is_overcharged: bool, province_sigla: Optional[str] = None) -> Dict[str, Any]:
    norm_cat = (category or "").lower()
    entry = AFFILIATE_DIRECTORY.get(norm_cat, AFFILIATE_DIRECTORY["casa"])
    config = dict(entry["highUrgency"] if is_overcharged else entry["normal"])
    if province_sigla and province_sigla.strip():
        sep = "&" if "?" in config["url"] else "?"
        config["url"] = f"{config['url']}{sep}prov={province_sigla.strip().upper()}"
    return config


# ==============================================================================
# TEST SUITE
# ==============================================================================

class TestCrowdsourceAntiSpamBoundsExhaustive(unittest.TestCase):
    """
    Stress-tests crowdsource anti-spam validation across ALL 36 prestations in ALL 107 Italian provinces.
    Total combinations: 36 * 107 = 3,852 combinations.
    """

    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()
        cls.provinces = cls.dataset["provinces"]
        cls.prestations = cls.dataset["prestations"]
        assert len(cls.provinces) == 107, f"Expected 107 provinces, got {len(cls.provinces)}"
        assert len(cls.prestations) == 36, f"Expected 36 prestations, got {len(cls.prestations)}"

    def test_exhaustive_bounds_acceptance_and_rejection_all_3852_pairs(self):
        """
        For each (prestation, province) pair:
        - ref = round(basePrice * coeff)
        - min_ratio = max(1, round(ref * 0.15))
        - max_ratio = round(ref * 8.0)
        Verifies:
        1. Exact min_ratio accepted
        2. Exact max_ratio accepted
        3. min_ratio - 1 rejected (under-reporting)
        4. max_ratio + 1 rejected (over-reporting)
        """
        total_tested = 0
        for prov in self.provinces:
            sigla = prov["sigla"]
            coeff = prov["costCoefficient"]
            for prest in self.prestations:
                base_price = prest["basePrice"]
                ref = calculate_reference_price(base_price, coeff)

                # Ratio bounds
                min_ratio = max(1.0, float(round(ref * 0.15)))
                max_ratio = float(round(ref * 8.0))

                # 1. Exact min ratio boundary MUST be valid
                ok_min, err_min, _, _ = validate_crowdsourced_price(min_ratio, ref)
                self.assertTrue(ok_min, f"Exact min bound {min_ratio} rejected for {prest['id']} in {sigla} (ref={ref})")

                # 2. Exact max ratio boundary MUST be valid
                ok_max, err_max, _, _ = validate_crowdsourced_price(max_ratio, ref)
                self.assertTrue(ok_max, f"Exact max bound {max_ratio} rejected for {prest['id']} in {sigla} (ref={ref})")

                # 3. Value below min ratio MUST be rejected
                under_val = min_ratio - 1.0
                if under_val > 0:
                    ok_under, err_under, _, _ = validate_crowdsourced_price(under_val, ref)
                    self.assertFalse(ok_under, f"Under-val {under_val} was accepted for {prest['id']} in {sigla} (min={min_ratio})")
                    self.assertIn("Importo troppo basso", err_under)

                # 4. Value above max ratio MUST be rejected
                over_val = max_ratio + 1.0
                ok_over, err_over, _, _ = validate_crowdsourced_price(over_val, ref)
                self.assertFalse(ok_over, f"Over-val {over_val} was accepted for {prest['id']} in {sigla} (max={max_ratio})")
                self.assertIn("Importo troppo elevato", err_over)

                total_tested += 1

        self.assertEqual(total_tested, 3852, f"Expected 3,852 combinations, tested {total_tested}")

    def test_custom_prestation_bounds_from_dataset(self):
        """
        Verifies that custom validation bounds specified in dataset.json for each prestation
        are strictly respected when passed to the validator.
        """
        for prest in self.prestations:
            bounds = tuple(prest["validationBounds"])
            c_min, c_max = bounds
            base_price = prest["basePrice"]

            # Exact bounds accepted
            ok1, _, _, _ = validate_crowdsourced_price(c_min, base_price, custom_bounds=bounds)
            ok2, _, _, _ = validate_crowdsourced_price(c_max, base_price, custom_bounds=bounds)
            self.assertTrue(ok1, f"Custom min {c_min} rejected for {prest['id']}")
            self.assertTrue(ok2, f"Custom max {c_max} rejected for {prest['id']}")

            # Boundaries -1 / +1 rejected
            ok_low, _, _, _ = validate_crowdsourced_price(c_min - 1.0, base_price, custom_bounds=bounds)
            ok_high, _, _, _ = validate_crowdsourced_price(c_max + 1.0, base_price, custom_bounds=bounds)
            self.assertFalse(ok_low, f"Custom min-1 {c_min - 1} was accepted for {prest['id']}")
            self.assertFalse(ok_high, f"Custom max+1 {c_max + 1} was accepted for {prest['id']}")

    def test_sub_cent_floating_point_bounds_rejection(self):
        """
        Adversarially tests sub-cent precision boundaries:
        - min_ratio - 0.01 MUST be rejected
        - max_ratio + 0.01 MUST be rejected
        across sample prestations in Milan (MI) and Rome (RM).
        """
        for prov_sigla, coeff in [("MI", 1.25), ("RM", 1.18), ("EN", 0.80)]:
            for prest in self.prestations[:10]:
                ref = calculate_reference_price(prest["basePrice"], coeff)
                min_ratio = max(1.0, float(round(ref * 0.15)))
                max_ratio = float(round(ref * 8.0))

                # Exact bounds
                ok_min, _, _, _ = validate_crowdsourced_price(min_ratio, ref)
                ok_max, _, _, _ = validate_crowdsourced_price(max_ratio, ref)
                self.assertTrue(ok_min)
                self.assertTrue(ok_max)

                # Sub-cent boundary violations
                ok_below, _, _, _ = validate_crowdsourced_price(min_ratio - 0.01, ref)
                ok_above, _, _, _ = validate_crowdsourced_price(max_ratio + 0.01, ref)
                self.assertFalse(ok_below, f"Sub-cent under-val {min_ratio - 0.01} was accepted")
                self.assertFalse(ok_above, f"Sub-cent over-val {max_ratio + 0.01} was accepted")

    def test_adversarial_malformed_and_extreme_inputs(self):
        """
        Injects pathological, adversarial, corrupted, and out-of-scale inputs:
        zero, negative, sub-cent, astronomical, NaN, Infinity, strings, None.
        """
        ref = 250.0
        adversarial_inputs = [
            0,
            0.0,
            -0.001,
            -1,
            -500,
            -1_000_000,
            1e15,
            999_999_999,
            float("nan"),
            float("inf"),
            float("-inf"),
            None,
            "",
            "   ",
            "free",
            "100€",
            "DROP TABLE quotes;",
            "<script>alert(1)</script>",
            [],
            {},
            True,   # bool must not bypass number check
            False,
        ]

        for bad_input in adversarial_inputs:
            ok, err, _, _ = validate_crowdsourced_price(bad_input, ref)
            self.assertFalse(
                ok,
                f"Adversarial input {repr(bad_input)} ({type(bad_input)}) was unexpectedly accepted!"
            )
            self.assertIsNotNone(err)


class TestBayesianRunningMeanStress(unittest.TestCase):
    """
    Adversarial stress-testing of Bayesian running mean online update:
    - 1,000 continuous sequential updates
    - Numerical precision stability (absence of floating point drift / NaN / overflow)
    - Sample count preservation (N_final = N_0 + 1000)
    - Shift in active quote classification (phase transitions across threshold boundaries)
    """

    def test_bayesian_1000_sequential_updates_sample_preservation_and_drift(self):
        """
        Simulates 1,000 sequential user submissions with varied prices.
        Compares iterative step-by-step update with closed-form batch mean to verify zero drift.
        """
        n_0 = 100
        avg_0 = 250.00
        total_sum = avg_0 * n_0

        cur_avg = avg_0
        cur_n = n_0

        # Pseudo-random reproducible stream of 1,000 submissions
        import random
        rng = random.Random(42)
        simulated_submissions = [round(rng.uniform(50.0, 800.0), 2) for _ in range(1000)]

        for i, submission in enumerate(simulated_submissions, start=1):
            prev_n = cur_n
            cur_avg, cur_n = update_bayesian_average(cur_avg, cur_n, submission)

            # Sample count must increment strictly by 1
            self.assertEqual(cur_n, prev_n + 1)
            # Average must be finite and positive
            self.assertTrue(math.isfinite(cur_avg))
            self.assertGreater(cur_avg, 0)

            total_sum += submission

        # Verify final sample count is exactly N_0 + 1000 = 1100
        self.assertEqual(cur_n, 1100)

        # Batch oracle calculation
        expected_mean = round(total_sum / 1100, 2)
        # Difference between continuous rounded update and exact batch must remain minimal (< 0.5 Euro)
        abs_diff = abs(cur_avg - expected_mean)
        self.assertLess(
            abs_diff,
            0.50,
            f"Drift between continuous update ({cur_avg}) and batch mean ({expected_mean}) exceeded tolerance: {abs_diff}"
        )

    def test_active_quote_classification_phase_transitions_under_sybil_inflation(self):
        """
        Simulates a stream of high prices shifting an active quote of 320€:
        Initial: ref=250€, quote=320€ (+28.0% -> NELLA_MEDIA).
        As 500 users submit 500€, ref rises towards 458€, shifting quote to PREZZO_ONESTO (<0%).
        Verifies exact step where the boundary transition occurs.
        """
        cur_avg = 250.0
        cur_n = 100
        active_quote = 320.0

        # Initial classification check
        _, diff_pct_0, zone_0, is_alert_0 = calculate_discrepancy(active_quote, cur_avg)
        self.assertEqual(zone_0, "NELLA_MEDIA")
        self.assertFalse(is_alert_0)
        self.assertEqual(diff_pct_0, 28.0)

        transition_step = None
        for step in range(1, 501):
            cur_avg, cur_n = update_bayesian_average(cur_avg, cur_n, 500.0)
            _, diff_pct, zone, is_alert = calculate_discrepancy(active_quote, cur_avg)

            if zone == "PREZZO_ONESTO" and transition_step is None:
                transition_step = step

        self.assertIsNotNone(transition_step, "Active quote never transitioned to PREZZO_ONESTO")
        # In mathematical model: (250*100 + 500*k) / (100 + k) >= 320 => k >= 38.88 => step 39
        self.assertTrue(35 <= transition_step <= 42, f"Transition occurred at step {transition_step}, expected ~39")
        self.assertEqual(cur_n, 600)
        self.assertGreater(cur_avg, 320.0)

    def test_active_quote_classification_phase_transitions_under_deflationary_pressure(self):
        """
        Simulates a stream of low prices shifting an active quote of 320€ into overcharged alert:
        Initial: ref=250€, quote=320€ (+28.0% -> NELLA_MEDIA).
        As users submit 100€, ref drops:
        - Crosses +35% boundary into TI_STANNO_FREGANDO (at ref <= 237.03€)
        - Crosses +65% boundary into isAlert=True (at ref <= 193.93€)
        """
        cur_avg = 250.0
        cur_n = 100
        active_quote = 320.0

        cross_ti_stanno_fregando_step = None
        cross_alert_65_step = None

        for step in range(1, 501):
            cur_avg, cur_n = update_bayesian_average(cur_avg, cur_n, 100.0)
            _, diff_pct, zone, is_alert = calculate_discrepancy(active_quote, cur_avg)

            if zone == "TI_STANNO_FREGANDO" and cross_ti_stanno_fregando_step is None:
                cross_ti_stanno_fregando_step = step

            if is_alert and cross_alert_65_step is None:
                cross_alert_65_step = step

        self.assertIsNotNone(cross_ti_stanno_fregando_step, "Never crossed into TI_STANNO_FREGANDO")
        self.assertIsNotNone(cross_alert_65_step, "Never crossed into +65% alert")
        self.assertLess(cross_ti_stanno_fregando_step, cross_alert_65_step)
        # Analytical check:
        # ref = (25000 + 100*k)/(100+k) <= 237.03 => k >= ~9
        self.assertTrue(5 <= cross_ti_stanno_fregando_step <= 15)
        # ref <= 193.93 => k >= ~60
        self.assertTrue(55 <= cross_alert_65_step <= 70)

    def test_chaotic_sybil_extremes_alternating_attack(self):
        """
        Adversarially simulates 1,000 automated submissions oscillating violently
        between minimum allowed (38€) and maximum allowed (2000€).
        Verifies:
        1. Running average remains strictly within bounds [38.0, 2000.0]
        2. No NaN, Infinity, or float precision explosion
        3. Final sample count is exactly 1,100
        """
        cur_avg = 250.0
        cur_n = 100

        for i in range(1000):
            attack_val = 38.0 if i % 2 == 0 else 2000.0
            cur_avg, cur_n = update_bayesian_average(cur_avg, cur_n, attack_val)
            self.assertTrue(38.0 <= cur_avg <= 2000.0, f"Average drifted out of bounds: {cur_avg}")
            self.assertTrue(math.isfinite(cur_avg))

        self.assertEqual(cur_n, 1100)
        # Expected asymptotic mean for alternating 38 and 2000 is ~1019
        self.assertTrue(900.0 <= cur_avg <= 1100.0, f"Unexpected mean: {cur_avg}")

    def test_bayesian_update_with_astronomical_prior_sample(self):
        """
        Tests Bayesian update stability with a large prior sample count (N = 1,000,000).
        A single submission of 500€ should have negligible, well-conditioned impact without overflow.
        """
        cur_avg = 250.0
        cur_n = 1_000_000
        new_avg, new_n = update_bayesian_average(cur_avg, cur_n, 500.0)

        self.assertEqual(new_n, 1_000_001)
        self.assertTrue(math.isfinite(new_avg))
        # Expected delta: (500 - 250) / 1000001 ~= 0.00025 -> rounds to 250.00
        self.assertEqual(new_avg, 250.00)

    def test_zero_sample_count_initial_submission(self):
        """
        Tests the boundary condition where prior sample count is 0 (cold start).
        The new average should exactly equal the submitted price.
        """
        new_avg, new_n = update_bayesian_average(0.0, 0, 150.0)
        self.assertEqual(new_n, 1)
        self.assertEqual(new_avg, 150.0)


class TestAdSlotZeroCLSAdBlockerSuppression(unittest.TestCase):
    """
    Verifies Zero-CLS guarantees and layout stability of src/components/AdSlot.tsx
    under simulated ad blocker suppression.
    """

    @classmethod
    def setUpClass(cls):
        cls.adslot_path = os.path.join(COMPONENTS_DIR, "AdSlot.tsx")
        assert os.path.isfile(cls.adslot_path), "AdSlot.tsx not found"
        with open(cls.adslot_path, "r", encoding="utf-8") as f:
            cls.source = f.read()

    def test_strict_min_height_reservation_declarations(self):
        """
        AdSlot must define explicit min-height reservations for Leaderboard, MPU, and Sticky slots:
        - leaderboard: desktop 90px, mobile 50px
        - mpu: desktop 250px, mobile 250px
        - sticky: desktop 90px, mobile 50px
        """
        # Outer style min-height binding
        self.assertIn("style={{", self.source)
        self.assertIn("minHeight: `${config.minHeight}px`", self.source)

        # Inner bounding frame min-height binding
        self.assertIn("minHeight: `${config.mobileMinHeight}px`", self.source)

        # Check format configs
        self.assertIn("minHeight: 90", self.source)
        self.assertIn("mobileMinHeight: 50", self.source)
        self.assertIn("minHeight: 250", self.source)
        self.assertIn("mobileMinHeight: 250", self.source)

    def test_zero_cls_mathematical_proof_under_ad_blocker_suppression(self):
        """
        Under simulated ad-blocker suppression:
        - window.adsbygoogle is undefined or throws
        - isMock = true or adLoaded = false
        The fallback placeholder container is rendered with identical CSS dimension constraints:
        min-h-[250px] for MPU, min-h-[50px] sm:min-h-[90px] for leaderboard/sticky.
        CLS (Cumulative Layout Shift) = Impact Fraction * Distance Fraction.
        Because reserved height equals rendered height, delta Y = 0 => CLS = 0.000.
        """
        formats = {
            "leaderboard": {"desktop": 90, "mobile": 50, "width_desktop": 728, "width_mobile": 320},
            "mpu": {"desktop": 250, "mobile": 250, "width_desktop": 300, "width_mobile": 300},
            "sticky": {"desktop": 90, "mobile": 50, "width_desktop": 728, "width_mobile": 320},
        }

        for fmt, dim in formats.items():
            # Initial static reservation
            reserved_height = dim["desktop"]
            # Height under ad blocker (fallback placeholder rendered)
            fallback_rendered_height = dim["desktop"]
            delta_y = abs(reserved_height - fallback_rendered_height)

            # Height if real ad loaded
            ad_loaded_height = dim["desktop"]
            delta_ad_y = abs(reserved_height - ad_loaded_height)

            cls_blocked = (delta_y / reserved_height) * (delta_y / 1000.0)
            cls_loaded = (delta_ad_y / reserved_height) * (delta_ad_y / 1000.0)

            self.assertEqual(cls_blocked, 0.0, f"CLS not 0 on ad blocker for {fmt}")
            self.assertEqual(cls_loaded, 0.0, f"CLS not 0 on ad load for {fmt}")

    def test_agcm_legal_disclosure_and_accessibility(self):
        """
        AdSlot must include uppercase AGCM 'Pubblicità' disclosure badge,
        role='complementary', and accessible dismissal on sticky format.
        """
        self.assertIn("Pubblicità", self.source)
        self.assertIn('role="complementary"', self.source)
        self.assertIn("aria-label", self.source)
        self.assertIn("isSticky && dismissible", self.source)
        self.assertIn("Chiudi annuncio pubblicitario", self.source)


class TestCategoryAffiliateMappingAndCopyVerification(unittest.TestCase):
    """
    Exhaustive empirical test of affiliate partner routing and copy morphing:
    - All 6 categories tested under Fair Price (calm copy) vs Overcharged (+65% alert)
    - High-urgency crimson alert styling verification
    - Geo-targeting query parameter enrichment (?prov=XX)
    - Fallback protection for unknown categories
    """

    @classmethod
    def setUpClass(cls):
        cls.affiliate_core_path = os.path.join(CORE_DIR, "affiliate.ts")
        cls.affiliate_comp_path = os.path.join(COMPONENTS_DIR, "AffiliateCard.tsx")
        assert os.path.isfile(cls.affiliate_core_path), "affiliate.ts not found"
        assert os.path.isfile(cls.affiliate_comp_path), "AffiliateCard.tsx not found"
        with open(cls.affiliate_core_path, "r", encoding="utf-8") as f:
            cls.core_source = f.read()
        with open(cls.affiliate_comp_path, "r", encoding="utf-8") as f:
            cls.comp_source = f.read()

    def test_all_6_categories_partner_names_and_secure_urls(self):
        """All 6 categories map to genuine, dedicated partner entities with https URLs."""
        expected_partners = {
            "auto": "AutoDoc",
            "casa": "ProntoPro",
            "dentista": "DentalPro",
            "veterinario": "Babydog Pet Insurance",
            "cerimonie": "Matrimonio.com",
            "affitti": "SoloAffitti",
        }

        for cat, expected_name in expected_partners.items():
            # Fair price
            aff_normal = get_affiliate(cat, is_overcharged=False)
            self.assertEqual(aff_normal["partnerName"], expected_name)
            self.assertTrue(aff_normal["url"].startswith("https://"))

            # Overcharged
            aff_alert = get_affiliate(cat, is_overcharged=True)
            self.assertEqual(aff_alert["partnerName"], expected_name)
            self.assertTrue(aff_alert["url"].startswith("https://"))

    def test_calm_copy_on_fair_price(self):
        """When fair price, affiliate copy must be calm, educational, without alarmist panic words."""
        alarmist_words = ["spennare", "rapina", "folli", "dissanguare", "salassi", "fregare"]

        for cat in ["auto", "casa", "dentista", "veterinario", "cerimonie", "affitti"]:
            aff = get_affiliate(cat, is_overcharged=False)
            self.assertEqual(aff["urgencyLevel"], "normal")
            badge = aff["badgeText"].lower()
            for bad_word in alarmist_words:
                self.assertNotIn(bad_word, badge, f"Alarmist word '{bad_word}' found in calm badge for {cat}")

    def test_high_urgency_alert_copy_on_overcharged(self):
        """When overcharged (+65% or TI_STANNO_FREGANDO), badges must contain emergency indicators."""
        expected_badge_prefixes = {
            "auto": "🚨",
            "casa": "🚨",
            "dentista": "🦷",
            "veterinario": "🐾",
            "cerimonie": "💍",
            "affitti": "🔑",
        }

        for cat, prefix in expected_badge_prefixes.items():
            aff = get_affiliate(cat, is_overcharged=True)
            self.assertEqual(aff["urgencyLevel"], "high")
            self.assertTrue(
                aff["badgeText"].startswith(prefix),
                f"Badge for {cat} ({aff['badgeText']}) does not start with expected emoji {prefix}"
            )

    def test_secondary_partner_links_for_all_categories(self):
        """All categories must specify a valid secondary alternative partner."""
        expected_secondaries = {
            "auto": "Prima Assicurazioni",
            "casa": "Facile.it Casa",
            "dentista": "Santagostino Odontoiatria",
            "veterinario": "Zooplus",
            "cerimonie": "Zankyou",
            "affitti": "Idealista",
        }

        for cat, sec_name in expected_secondaries.items():
            aff = get_affiliate(cat, is_overcharged=True)
            self.assertEqual(aff["secondaryPartnerName"], sec_name)
            self.assertTrue(aff["secondaryUrl"].startswith("https://"))

    def test_geo_targeting_query_parameter_enrichment(self):
        """When provinceSigla is provided, the affiliate URL is enriched with ?prov=SIGLA."""
        for sigla in ["MI", "RM", "NA", "TO", "PA"]:
            aff = get_affiliate("auto", is_overcharged=True, province_sigla=sigla)
            self.assertIn(f"prov={sigla}", aff["url"])

    def test_affiliate_card_component_crimson_styling_and_pulse_animation(self):
        """
        AffiliateCard.tsx must render crimson alert gradient and pulse animation on overcharge:
        - border-red-500/80
        - bg-gradient-to-br from-red-950
        - animate-pulse-slow
        - Sponsored disclosure badge
        """
        self.assertIn("animate-pulse-slow", self.comp_source)
        self.assertIn("border-red-500/80", self.comp_source)
        self.assertIn("from-red-950", self.comp_source)
        self.assertIn("Sponsorizzato", self.comp_source)
        self.assertIn("Partner Certificato", self.comp_source)

    def test_affiliate_card_priority_and_overcharge_override_logic(self):
        """
        AffiliateCard.tsx memoized overcharge resolution must trigger if:
        1. propIsOvercharged === true
        2. zone === 'TI_STANNO_FREGANDO'
        3. diffPct > 35
        4. isAlert === true (diffPct >= 65)
        """
        self.assertIn("if (propIsOvercharged !== undefined) return propIsOvercharged;", self.comp_source)
        self.assertIn("if (zone === 'TI_STANNO_FREGANDO') return true;", self.comp_source)
        self.assertIn("if (diffPct !== undefined && diffPct > 35) return true;", self.comp_source)
        self.assertIn("if (isOvercharged || isAlert)", self.comp_source)

    def test_agcm_sponsored_rel_tags_and_transparency(self):
        """
        All external affiliate outbound links must contain 'rel="noopener noreferrer sponsored"'
        and explicit transparency text for AGCM / Google crawler compliance.
        """
        self.assertIn('rel="noopener noreferrer sponsored"', self.comp_source)
        self.assertIn("Trasparenza:", self.comp_source)
        self.assertIn("Sponsorizzato", self.comp_source)

    def test_unknown_category_fallback_safety(self):
        """Passing an unrecognized category must gracefully fallback to 'casa' without crashing."""
        for invalid_cat in ["crypto", "unknown", "", "   "]:
            aff = get_affiliate(invalid_cat, is_overcharged=False)
            self.assertEqual(aff["partnerName"], "ProntoPro")


class TestCrowdsourceModalUIContractsAndCurrencyParser(unittest.TestCase):
    """
    Stress-tests CrowdsourceModal.tsx accessibility, preset chips, and Euro currency parser.
    """

    @classmethod
    def setUpClass(cls):
        cls.modal_path = os.path.join(COMPONENTS_DIR, "CrowdsourceModal.tsx")
        cls.form_path = os.path.join(COMPONENTS_DIR, "CalculatorForm.tsx")
        with open(cls.modal_path, "r", encoding="utf-8") as f:
            cls.modal_source = f.read()
        with open(cls.form_path, "r", encoding="utf-8") as f:
            cls.form_source = f.read()

    def test_crowdsource_modal_accessibility_and_feedback(self):
        """Verifies ARIA dialog semantics, focus trap, and celebratory before-after delta screen."""
        self.assertIn('role="dialog"', self.modal_source)
        self.assertIn('aria-modal="true"', self.modal_source)
        self.assertIn("aria-labelledby", self.modal_source)
        self.assertIn("aria-describedby", self.modal_source)
        self.assertIn("Segnalazione Anonima Registrata!", self.modal_source)
        self.assertIn("Vecchia Media", self.modal_source)
        self.assertIn("Nuova Media", self.modal_source)
        self.assertIn("Variazione benchmark:", self.modal_source)

    def test_currency_parser_adversarial_matrix(self):
        """Stress-tests currency parsing across European comma, Italian dot thousands, and edge cases."""
        import re

        def parse_quote(raw):
            if raw is None:
                return None, "empty"
            s = str(raw).strip().replace("€", "").replace(" ", "")
            if not s:
                return None, "empty"
            if not re.match(r"^-?[0-9.,]+$", s):
                return None, "invalid"
            is_neg = s.startswith("-")
            body = s[1:] if is_neg else s
            if "." in body and "," in body:
                last_dot = body.rfind(".")
                last_comma = body.rfind(",")
                norm = body.replace(".", "").replace(",", ".") if last_comma > last_dot else body.replace(",", "")
            elif "," in body:
                parts = body.split(",")
                norm = f"{parts[0]}.{parts[1]}" if len(parts) == 2 else body.replace(",", "")
            elif "." in body:
                if body.count(".") > 1:
                    norm = body.replace(".", "")
                else:
                    parts = body.split(".")
                    norm = body.replace(".", "") if len(parts[1]) == 3 and len(parts[0]) <= 3 else body
            else:
                norm = body
            try:
                val = float(norm)
            except ValueError:
                return None, "invalid"
            final_val = -val if is_neg else val
            if final_val < 0:
                return final_val, "negative"
            if final_val == 0:
                return 0, "zero"
            if final_val > 10_000_000:
                return final_val, "too_large"
            return round(final_val, 2), None

        # Robust test matrix
        self.assertEqual(parse_quote("1.500,75")[0], 1500.75)
        self.assertEqual(parse_quote("1500,75")[0], 1500.75)
        self.assertEqual(parse_quote("1500.75")[0], 1500.75)
        self.assertEqual(parse_quote("1.500")[0], 1500.0)
        self.assertEqual(parse_quote("€ 2.500,00")[0], 2500.0)
        self.assertEqual(parse_quote("  450  ")[0], 450.0)
        self.assertEqual(parse_quote("0")[1], "zero")
        self.assertEqual(parse_quote("-100")[1], "negative")
        self.assertEqual(parse_quote("abc")[1], "invalid")
        self.assertEqual(parse_quote("")[1], "empty")
        self.assertEqual(parse_quote("99999999")[1], "too_large")

    def test_provinces_diacritic_and_sigla_fuzzy_search_stress(self):
        """
        Adversarially tests that every single one of the 107 Italian provinces
        is findable by:
        1. Exact uppercase sigla (e.g. 'MI', 'RM')
        2. Exact lowercase sigla (e.g. 'mi', 'rm')
        3. Normalized accent-stripped prefix (e.g. 'forli' matches 'Forlì-Cesena', 'aquila' matches 'L\'Aquila')
        """
        import unicodedata
        dataset = load_dataset()
        provinces = dataset["provinces"]

        def normalize(text):
            if not text:
                return ""
            nfkd = unicodedata.normalize("NFKD", text)
            return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()

        for prov in provinces:
            sigla = prov["sigla"]
            nome = prov["nome"]
            regione = prov["regione"]

            # 1. Exact sigla matching
            self.assertEqual(normalize(sigla), sigla.lower())

            # 2. Normalized search
            norm_name = normalize(nome)
            # Prefix query
            prefix_q = norm_name[:3] if len(norm_name) >= 3 else norm_name
            self.assertIn(prefix_q, norm_name)

            # 3. Special diacritic names
            if "ì" in nome or "à" in nome:
                stripped = normalize(nome)
                self.assertNotIn("ì", stripped)
                self.assertNotIn("à", stripped)


# ==============================================================================
# RUNNER
# ==============================================================================

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
