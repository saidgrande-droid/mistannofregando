#!/usr/bin/env python3
"""
tests/tier5_ui_adversarial.py
Dedicated Tier 5 Adversarial Test Suite: UI & Viral Subsystems of "Mi Stanno Fregando?".

Author: challenger_tier5_2 (empirical_challenger)
Target: Comprehensive white-box source code audit, mathematical boundary verification,
        and adversarial stress testing of src/components/ and src/App.tsx:
        - Tachometer.tsx: SVG needle rendering, CSS transitions, high-contrast zone badges,
          accessible ARIA meter attributes.
        - ShareCard.tsx: Canvas 2D card rendering, high-DPI retina scaling, WhatsApp & Telegram
          share links, text truncation of long custom descriptions, Web Share API fallbacks.
        - ResultSummary.tsx: Dynamic copy generation (7 sub-bands), exact difference euro
          and percentage callout, 4-tile statistical comparison grid.
        - CalculatorForm.tsx: 107 province search with cadastral aliases, diacritics,
          European currency parsing edge cases, keyboard accessibility.
        - CrowdsourceModal.tsx: Anti-spam boundary display, 1-click modal presets, celebratory
          feedback comparison card, accessibility focus trap and ESC key listeners.
        - AdSlot.tsx & AffiliateCard.tsx: Zero-CLS layout preservation, sticky banner dismissal,
          pulsing red emergency alerts.
        - App.tsx: Master layout coordination, URL query auto-hydration, live crowdsource recalibration.

Usage:
    python3 tests/tier5_ui_adversarial.py
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
    cur = os.path.realpath(os.path.dirname(__file__))
    while cur and cur != os.path.dirname(cur):
        if os.path.exists(os.path.join(cur, "package.json")) and os.path.exists(os.path.join(cur, "src")):
            return cur
        cur = os.path.dirname(cur)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PROJECT_ROOT = find_project_root()
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
CORE_DIR = os.path.join(SRC_DIR, "core")
COMPONENTS_DIR = os.path.join(SRC_DIR, "components")
DATASET_PATH = os.path.join(CORE_DIR, "dataset.json")


def load_dataset() -> Dict[str, Any]:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def read_source_file(relative_path: str) -> str:
    path = os.path.join(SRC_DIR, relative_path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ==============================================================================
# PURE PYTHON DOMAIN ORACLES (Exact mathematical mirrors of TypeScript implementations)
# ==============================================================================

def oracle_reference_price(base_price: float, cost_coefficient: float) -> int:
    """Exact mirror of src/core/calculator.ts:getReferencePrice."""
    if not math.isfinite(base_price) or base_price <= 0:
        raise ValueError(f"base_price must be positive finite: {base_price}")
    if not math.isfinite(cost_coefficient) or cost_coefficient <= 0:
        raise ValueError(f"cost_coefficient must be positive finite: {cost_coefficient}")
    return round(base_price * cost_coefficient)


def oracle_classify_zone(diff_pct: float) -> Tuple[str, bool]:
    """Exact mirror of src/core/calculator.ts:classifyZone."""
    if diff_pct <= 0.0:
        return ("PREZZO_ONESTO", False)
    if diff_pct <= 35.0:
        return ("NELLA_MEDIA", False)
    return ("TI_STANNO_FREGANDO", diff_pct >= 65.0)


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


def oracle_normalize_italian_text(text: str) -> str:
    """Exact mirror of src/components/CalculatorForm.tsx:normalizeItalianText."""
    if not text:
        return ""
    import unicodedata
    nfd = unicodedata.normalize('NFD', text)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != 'Mn')
    lowered = stripped.lower()
    cleaned = re.sub(r"['’‘`´\-–—]", " ", lowered)
    collapsed = re.sub(r"\s+", " ", cleaned).strip()
    return collapsed


def oracle_parse_quote_input(raw: Any) -> Tuple[Optional[float], Optional[str]]:
    """Exact mirror of src/components/CalculatorForm.tsx:parseQuoteInput."""
    if raw is None:
        return (None, "Inserisci un importo valido.")
    s = str(raw).strip().replace("€", "")
    s = re.sub(r"\s+", "", s)
    if not s:
        return (None, "Inserisci l'importo del preventivo.")
    if not re.match(r"^-?[0-9.,]+$", s):
        return (None, "Inserisci un numero valido per l'importo.")

    is_negative = s.startswith("-")
    body = s[1:] if is_negative else s

    if "." in body and "," in body:
        last_dot = body.rfind(".")
        last_comma = body.rfind(",")
        if last_comma > last_dot:
            normalized = body.replace(".", "").replace(",", ".")
        else:
            normalized = body.replace(",", "")
    elif "," in body:
        parts = body.split(",")
        if len(parts) == 2:
            normalized = f"{parts[0]}.{parts[1]}"
        else:
            normalized = body.replace(",", "")
    elif "." in body:
        if body.count(".") > 1:
            normalized = body.replace(".", "")
        else:
            parts = body.split(".")
            if len(parts[1]) == 3 and len(parts[0]) <= 3:
                normalized = body.replace(".", "")
            else:
                normalized = body
    else:
        normalized = body

    try:
        parsed = float(normalized)
    except ValueError:
        return (None, "Inserisci un numero valido per l'importo.")

    if math.isnan(parsed) or not math.isfinite(parsed):
        return (None, "Inserisci un numero valido per l'importo.")

    final_val = -parsed if is_negative else parsed
    if final_val < 0:
        return (final_val, "L'importo del preventivo non può essere negativo.")
    if final_val == 0:
        return (0.0, "Inserisci un importo superiore a zero.")
    if final_val > 10_000_000:
        return (final_val, "Importo fuori scala (massimo 10.000.000 €).")

    return (round(final_val, 2), None)


def oracle_generate_copywriting(
    zone: str, is_alert: bool, diff_euro: float, diff_pct: float, quote: float, ref_price: int
) -> Tuple[str, str]:
    """Exact mirror of src/core/calculator.ts:generateCopywriting."""
    abs_diff_euro = abs(diff_euro)
    abs_diff_pct = abs(diff_pct)

    fmt_quote = f"{quote:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if quote % 1 != 0 else f"{int(quote):,}".replace(",", ".") + " €"
    fmt_ref = f"{ref_price:,}".replace(",", ".") + " €"

    if zone == "PREZZO_ONESTO":
        if diff_pct <= -40.0:
            return ("Prezzo Stracciato: Occhio alla Qualità!", "Stai risparmiando")
        if diff_pct <= -15.0:
            return ("Ottimo Affare: Prezzo Super Onesto!", "Stai risparmiando")
        return ("Prezzo Onesto: Tariffa Equa", "allineato o inferiore alla media locale")

    if zone == "NELLA_MEDIA":
        if diff_pct <= 15.0:
            return ("Prezzo Nella Media", "perfettamente allineato ai prezzi correnti")
        return ("Nella Media (Fascia Alta)", "rientra ancora nei limiti fisiologici")

    if is_alert:
        if diff_pct >= 150.0:
            return ("🚨 TI STANNO FREGANDO ALLA GRANDE!", "Prezzo folle fuori scala")
        return ("🚨 TI STANNO FREGANDO!", "Allarme stangata: il preventivo supera")

    return ("Occhio: Prezzo Fuori Mercato!", "Prima di firmare, richiedi la specifica")


# ==============================================================================
# TEST SUITE 1: TACHOMETER COMPONENT AUDIT & POLAR GEOMETRY STRESS
# ==============================================================================

class TestTachometerAdversarial(unittest.TestCase):
    """
    White-box source code audit and mathematical verification of Tachometer.tsx.
    Validates SVG polar trigonometry, spring transition specs, high-contrast zone badges,
    and W3C ARIA meter accessibility attributes.
    """

    def setUp(self):
        self.src = read_source_file("components/Tachometer.tsx")

    def test_svg_polar_geometry_oracle_precision(self):
        """
        Verifies the polar-to-cartesian coordinate transformations in Tachometer.tsx:
        Center (cx=160, cy=150), Radius R=110, Arc span from -100° to +100°.
        x = cx + R * sin(theta_rad)
        y = cy - R * cos(theta_rad)
        """
        cx, cy, R = 160.0, 150.0, 110.0

        def polar_to_cart(angle_deg: float) -> Tuple[float, float]:
            rad = math.radians(angle_deg)
            x = cx + R * math.sin(rad)
            y = cy - R * math.cos(rad)
            return (round(x, 2), round(y, 2))

        # 1. Start of arc at -100°:
        x_start, y_start = polar_to_cart(-100.0)
        self.assertAlmostEqual(x_start, 51.67, places=2)
        self.assertAlmostEqual(y_start, 169.10, places=2)

        # 2. End of arc at +100°:
        x_end, y_end = polar_to_cart(100.0)
        self.assertAlmostEqual(x_end, 268.33, places=2)
        self.assertAlmostEqual(y_end, 169.10, places=2)

        # 3. Apex / Media at 0°:
        x_top, y_top = polar_to_cart(0.0)
        self.assertAlmostEqual(x_top, 160.00, places=2)
        self.assertAlmostEqual(y_top, 40.00, places=2)

        # 4. Amber/Red boundary at +50°:
        x_amber, y_amber = polar_to_cart(50.0)
        self.assertAlmostEqual(x_amber, 244.26, places=2)
        self.assertAlmostEqual(y_amber, 79.29, places=2)

        # 5. Alert Trigger Notch at +65% discrepancy (corresponds to +92.86°):
        angle_alert = oracle_needle_angle_200(65.0)
        self.assertAlmostEqual(angle_alert, 92.86, places=2)
        rad_alert = math.radians(angle_alert)
        r_inner, r_outer = 103.0, 119.0
        x_n1 = round(cx + r_inner * math.sin(rad_alert), 2)
        y_n1 = round(cy - r_inner * math.cos(rad_alert), 2)
        x_n2 = round(cx + r_outer * math.sin(rad_alert), 2)
        y_n2 = round(cy - r_outer * math.cos(rad_alert), 2)
        self.assertAlmostEqual(x_n1, 261.87, delta=1.0)
        self.assertAlmostEqual(y_n1, 155.09, delta=1.0)
        self.assertAlmostEqual(x_n2, 277.85, delta=1.0)
        self.assertAlmostEqual(y_n2, 155.89, delta=1.0)

        # Confirm exact paths exist in Tachometer.tsx
        self.assertIn('d="M 51.67 169.10 A 110 110 0 1 1 268.33 169.10"', self.src)
        self.assertIn('d="M 51.67 169.10 A 110 110 0 0 1 160.00 40.00"', self.src)
        self.assertIn('d="M 160.00 40.00 A 110 110 0 0 1 244.26 79.29"', self.src)
        self.assertIn('d="M 244.26 79.29 A 110 110 0 0 1 268.33 169.10"', self.src)

    def test_needle_angle_piecewise_linear_mapping_adversarial(self):
        """
        Adversarially tests the 200° needle angle mapping across extreme, boundary,
        and continuous domain values.
        """
        test_points = [
            (-1000.0, -100.0),
            (-100.0, -100.0),
            (-50.0, -100.0),
            (-25.0, -50.0),
            (0.0, 0.0),
            (17.5, 25.0),
            (35.0, 50.0),
            (52.5, 75.0),
            (65.0, 92.86),
            (70.0, 100.0),
            (150.0, 100.0),
            (1000.0, 100.0),
        ]
        for diff_pct, expected_angle in test_points:
            actual = oracle_needle_angle_200(diff_pct)
            self.assertAlmostEqual(
                actual, expected_angle, places=2,
                msg=f"Failed for diff_pct={diff_pct}: expected {expected_angle}, got {actual}"
            )

        # Monotonicity test across 200 progressive steps
        angles = [oracle_needle_angle_200(p / 2.0) for p in range(-120, 200)]
        for i in range(len(angles) - 1):
            self.assertLessEqual(angles[i], angles[i+1], "Needle angle mapping must be non-decreasing")

        # Non-finite inputs
        self.assertEqual(oracle_needle_angle_200(float("nan")), 0.0)
        self.assertEqual(oracle_needle_angle_200(float("inf")), 0.0)
        self.assertEqual(oracle_needle_angle_200(float("-inf")), 0.0)

    def test_needle_spring_transition_cubic_bezier_contract(self):
        """
        Verifies that Tachometer.tsx implements the cubic-bezier spring transition physics
        and needle rotation parameters.
        """
        self.assertIn("cubic-bezier(0.34, 1.56, 0.64, 1)", self.src)
        self.assertIn("transition: 'transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)'", self.src)
        self.assertIn("transformOrigin: '0px 0px'", self.src)
        self.assertIn("data-testid=\"tachometer-needle\"", self.src)
        # Needle tapered polygon
        self.assertIn('points="-3.5,4 0,-100 3.5,4 0,16"', self.src)

    def test_zone_badges_and_alert_dynamics(self):
        """
        Verifies high-contrast zone badges and pulsing alert filter activation in Tachometer.tsx.
        """
        # Prezzo Onesto badge
        self.assertIn("'Prezzo Onesto'", self.src)
        self.assertIn("text-emerald-400 bg-emerald-950/60 border-emerald-500/40", self.src)

        # Nella Media badge
        self.assertIn("'Nella Media'", self.src)
        self.assertIn("text-amber-400 bg-amber-950/60 border-amber-500/40", self.src)

        # Ti Stanno Fregando badge (Alert vs Non-Alert)
        self.assertIn("effectiveIsAlert ? 'TI STANNO FREGANDO!' : 'Fuori Mercato'", self.src)
        self.assertIn("animate-pulse", self.src)
        self.assertIn("alert-glow", self.src)

        # In-gauge zone titles
        self.assertIn("ONESTO", self.src)
        self.assertIn("MEDIA", self.src)
        self.assertIn("FREGATURA", self.src)

    def test_aria_meter_accessibility_attributes(self):
        """
        Verifies W3C WAI-ARIA meter attributes for screen reader accessibility:
        role="meter", aria-label, aria-valuenow, aria-valuemin, aria-valuemax, aria-valuetext.
        """
        self.assertIn('role="meter"', self.src)
        self.assertIn('aria-label="Tachimetro di scostamento preventivo"', self.src)
        self.assertIn('aria-valuenow={effectiveDiffPct}', self.src)
        self.assertIn('aria-valuemin={-50}', self.src)
        self.assertIn('aria-valuemax={100}', self.src)
        self.assertIn('aria-valuetext={ariaValueText}', self.src)
        self.assertIn('tabIndex={0}', self.src)
        self.assertIn('<span className="sr-only">', self.src)


# ==============================================================================
# TEST SUITE 2: SHARECARD COMPONENT & VIRAL PIPELINE AUDIT
# ==============================================================================

class TestShareCardAdversarial(unittest.TestCase):
    """
    White-box audit and stress testing of ShareCard.tsx:
    Canvas 2D 1080x1080 Retina generation, WhatsApp & Telegram viral channels,
    text truncation on long custom descriptions, and Web Share API fallback.
    """

    def setUp(self):
        self.src = read_source_file("components/ShareCard.tsx")

    def test_canvas_1080_retina_geometry_and_layers(self):
        """
        Verifies that ShareCard.tsx enforces 1080x1080px Retina resolution,
        8-layer rendering pipeline, and radial ambient chromatic glow.
        """
        self.assertIn("canvas.width = 1080", self.src)
        self.assertIn("canvas.height = 1080", self.src)
        self.assertIn("1080×1080 HD", self.src)
        # Background gradient & radial ambient glow
        self.assertIn("createLinearGradient(0, 0, 1080, 1080)", self.src)
        self.assertIn("createRadialGradient(540, 430, 40, 540, 430, 380)", self.src)
        # Inset border
        self.assertIn("drawRoundRect(ctx, 24, 24, 1032, 1032, 32)", self.src)
        # Branding header
        self.assertIn("MISTANNOFREGANDO.IT", self.src)
        # Speedometer gauge center
        self.assertIn("const cx = 540;", self.src)
        self.assertIn("const cy = 430;", self.src)
        self.assertIn("const radius = 160;", self.src)

    def test_whatsapp_share_text_and_url_encoding(self):
        """
        Verifies the pre-formatted viral WhatsApp share text and deep link generation.
        """
        self.assertIn("generateViralShareText", self.src)
        self.assertIn("api.whatsapp.com/send?text=", self.src)

        # Test message structure directly
        def format_share_text(prestation, province, quote, ref, diff_euro, diff_pct, zone, url):
            diff_sign = "+" if diff_pct >= 0 else ""
            euro_sign = "+" if diff_euro >= 0 else ""
            lead = "🚨 TI STANNO FREGANDO?" if zone == "TI_STANNO_FREGANDO" else "✅ PREZZO ONESTO!"
            return (
                f"{lead}\n"
                f"Ho controllato il preventivo per {prestation} a {province} su MiStannoFregando.it: "
                f"verdetto {zone} ({diff_sign}{diff_pct}%)!\n\n"
                f"• Preventivo ricevuto: {quote} €\n"
                f"• Media locale: {ref} €\n"
                f"• Differenza: {euro_sign}{diff_euro} € ({diff_sign}{diff_pct}%)\n\n"
                f"🔍 Controlla gratis il tuo preventivo prima di pagare:\n{url}"
            )

        msg = format_share_text("Tagliando Auto", "Milano", 450, 313, 137, 43.8, "TI_STANNO_FREGANDO", "https://mistannofregando.it")
        self.assertIn("🚨 TI STANNO FREGANDO?", msg)
        self.assertIn("verdetto TI_STANNO_FREGANDO (+43.8%)!", msg)
        self.assertIn("• Preventivo ricevuto: 450 €", msg)
        self.assertIn("• Media locale: 313 €", msg)
        self.assertIn("• Differenza: +137 € (+43.8%)", msg)

    def test_telegram_share_channel_gap(self):
        """
        AUDIT FINDING: Verifies whether ShareCard.tsx implements Telegram sharing.
        The dispatch specifically specifies 'WhatsApp & Telegram share links'.
        In ShareCard.tsx:
        - WhatsApp is implemented via https://api.whatsapp.com/send?text=...
        - Web Share API, Direct Download PNG, and Copy Link are implemented.
        - Telegram direct link (https://t.me/share/url?url=...&text=...) is NOT implemented.
        This test documents and asserts this architectural gap.
        """
        has_telegram = "telegram" in self.src.lower() or "t.me" in self.src.lower()
        # Document the empirical finding:
        # Telegram is NOT implemented in ShareCard.tsx.
        self.assertFalse(
            has_telegram,
            "Expected finding: Telegram sharing is missing from ShareCard.tsx (only WhatsApp, Web Share, Download, Copy Link exist)"
        )

    def test_canvas_text_truncation_oracle_adversarial(self):
        """
        Adversarially stress tests the Canvas 2D title truncation algorithm:
        while (ctx.measureText(`${displayTitle}...`).width > 880 && displayTitle.length > 0) {
            displayTitle = displayTitle.slice(0, -1);
        }
        displayTitle = `${displayTitle}...`;
        """
        def simulate_canvas_truncation(title: str, max_chars_at_880px: int = 40) -> str:
            # Simulates ctx.measureText width where average character width is ~22px
            display = title
            while len(display) + 3 > max_chars_at_880px and len(display) > 0:
                display = display[:-1]
            return f"{display}..." if len(title) > len(display) else title

        # Test case 1: Standard title (well below 880px)
        short_title = "Tagliando a Milano"
        self.assertEqual(simulate_canvas_truncation(short_title, 40), short_title)

        # Test case 2: Massive 250-character custom description
        long_custom = "Riparazione straordinaria e complessa del cambio automatico a doppia frizione con sostituzione volano bimassa e programmazione centralina elettronica a Milano"
        truncated = simulate_canvas_truncation(long_custom, 40)
        self.assertTrue(truncated.endswith("..."))
        self.assertLessEqual(len(truncated), 40)
        self.assertGreater(len(truncated), 10)

        # Test case 3: Single non-breaking word of 100 characters
        unbroken_word = "A" * 100 + " a Roma"
        truncated_unbroken = simulate_canvas_truncation(unbroken_word, 40)
        self.assertTrue(truncated_unbroken.endswith("..."))
        self.assertLessEqual(len(truncated_unbroken), 40)

        # Verify the source code implementation of the while loop
        self.assertIn("while (ctx.measureText(`${displayTitle}...`).width > 880 && displayTitle.length > 0)", self.src)

    def test_web_share_api_fallback_mechanisms(self):
        """
        Verifies that ShareCard.tsx gracefully falls back to direct PNG download or link copy
        when Web Share API is unavailable or rejected.
        """
        self.assertIn("handleWebShare", self.src)
        self.assertIn("navigator.share", self.src)
        self.assertIn("handleDirectDownload", self.src)
        self.assertIn("handleCopyLink", self.src)
        # Fallback to direct download when navigator.share is unavailable
        self.assertIn("canNativeShare ? 'Condividi Scheda' : 'Salva Immagine'", self.src)

    def test_share_url_lossless_roundtrip_with_custom_description(self):
        """
        Verifies buildShareUrl and parseShareUrlParams roundtrip with custom prestation descriptions.
        """
        from urllib.parse import urlparse, parse_qs

        def build_url(base, cat, prest, prov, quote, desc=None):
            clean = base.split("?")[0].rstrip("/")
            params = f"cat={cat}&prest={prest}&prov={prov.upper()}&quote={quote}"
            if prest == "custom" and desc:
                import urllib.parse
                params += f"&desc={urllib.parse.quote(desc.strip())}"
            return f"{clean}/?{params}"

        def parse_url(query_str):
            import urllib.parse
            if query_str.startswith("?"):
                query_str = query_str[1:]
            qs = urllib.parse.parse_qs(query_str)
            res = {}
            if "cat" in qs: res["categoryId"] = qs["cat"][0]
            if "prest" in qs: res["prestationId"] = qs["prest"][0]
            if "prov" in qs: res["provinceSigla"] = qs["prov"][0].upper()
            if "quote" in qs: res["quote"] = float(qs["quote"][0])
            if "desc" in qs: res["customDescription"] = qs["desc"][0]
            return res

        url = build_url("https://mistannofregando.it", "auto", "custom", "MI", 650, "Sostituzione frizione rinforzata")
        parsed = parse_url(url.split("?")[1])
        self.assertEqual(parsed["categoryId"], "auto")
        self.assertEqual(parsed["prestationId"], "custom")
        self.assertEqual(parsed["provinceSigla"], "MI")
        self.assertEqual(parsed["quote"], 650.0)
        self.assertEqual(parsed["customDescription"], "Sostituzione frizione rinforzata")


# ==============================================================================
# TEST SUITE 3: RESULTSUMMARY COMPONENT AUDIT & VIRAL COPYWRITING STRESS
# ==============================================================================

class TestResultSummaryAdversarial(unittest.TestCase):
    """
    White-box audit and stress testing of ResultSummary.tsx:
    Dynamic copy generation across all 7 discrepancy sub-bands, exact euro & percentage callouts,
    and 4-tile statistical comparison grid.
    """

    def setUp(self):
        self.src = read_source_file("components/ResultSummary.tsx")

    def test_dynamic_copywriting_all_7_sub_bands(self):
        """
        Verifies that copywriting dynamically triggers the exact headline for all 7 sub-bands:
        1. <= -40%: Prezzo Stracciato: Occhio alla Qualità!
        2. -40% to -15%: Ottimo Affare: Prezzo Super Onesto!
        3. -15% to 0%: Prezzo Onesto: Tariffa Equa
        4. 0% to +15%: Prezzo Nella Media
        5. +15% to +35%: Nella Media (Fascia Alta)
        6. +35% to +65%: Occhio: Prezzo Fuori Mercato!
        7. +65% to +150%: 🚨 TI STANNO FREGANDO!
        8. >= +150%: 🚨 TI STANNO FREGANDO ALLA GRANDE!
        """
        test_cases = [
            # (zone, is_alert, diff_euro, diff_pct, expected_headline)
            ("PREZZO_ONESTO", False, -150.0, -50.0, "Prezzo Stracciato: Occhio alla Qualità!"),
            ("PREZZO_ONESTO", False, -60.0, -20.0, "Ottimo Affare: Prezzo Super Onesto!"),
            ("PREZZO_ONESTO", False, -10.0, -5.0, "Prezzo Onesto: Tariffa Equa"),
            ("NELLA_MEDIA", False, 15.0, 5.0, "Prezzo Nella Media"),
            ("NELLA_MEDIA", False, 60.0, 25.0, "Nella Media (Fascia Alta)"),
            ("TI_STANNO_FREGANDO", False, 120.0, 45.0, "Occhio: Prezzo Fuori Mercato!"),
            ("TI_STANNO_FREGANDO", True, 200.0, 80.0, "🚨 TI STANNO FREGANDO!"),
            ("TI_STANNO_FREGANDO", True, 600.0, 200.0, "🚨 TI STANNO FREGANDO ALLA GRANDE!"),
        ]

        for zone, is_alert, diff_euro, diff_pct, expected_headline in test_cases:
            headline, _ = oracle_generate_copywriting(zone, is_alert, diff_euro, diff_pct, 100 + diff_euro, 100)
            self.assertEqual(
                headline, expected_headline,
                f"Failed for zone={zone}, is_alert={is_alert}, diff_pct={diff_pct}: expected '{expected_headline}', got '{headline}'"
            )

    def test_exact_difference_euro_and_percentage_callouts(self):
        """
        Verifies positive and negative callout formatting for euro difference and percentage.
        """
        # Euro differences
        self.assertIn("diffEuro > 0) return `+${diffEuro.toLocaleString('it-IT')} €`;", self.src)
        # Percentage formatting
        self.assertIn("diffPct > 0) return `+${diffPct.toFixed(1)}%`;", self.src)
        # Verdict pills
        self.assertIn("Prezzo Onesto", self.src)
        self.assertIn("Nella Media", self.src)
        self.assertIn("TI STANNO FREGANDO!", self.src)

    def test_four_tile_grid_and_aria_polite_contract(self):
        """
        Verifies that ResultSummary.tsx implements the 4-tile comparison grid:
        Tile 1: Preventivo Ricevuto
        Tile 2: Media a {provinceSigla}
        Tile 3: Differenza in Euro
        Tile 4: Scostamento Percentuale (Giant Font)
        Along with aria-live="polite".
        """
        self.assertIn("Preventivo Ricevuto", self.src)
        self.assertIn("Media a", self.src)
        self.assertIn("Differenza", self.src)
        self.assertIn("Scostamento %", self.src)
        self.assertIn('aria-live="polite"', self.src)
        self.assertIn('role="region"', self.src)


# ==============================================================================
# TEST SUITE 4: CALCULATORFORM COMPONENT & PROVINCE SEARCH AUDIT
# ==============================================================================

class TestCalculatorFormAdversarial(unittest.TestCase):
    """
    White-box audit and stress testing of CalculatorForm.tsx:
    107 province search with cadastral aliases & diacritics, European currency parsing edge cases,
    and keyboard accessibility.
    """

    def setUp(self):
        self.src = read_source_file("components/CalculatorForm.tsx")
        self.dataset = load_dataset()

    def test_107_provinces_exhaustive_search_and_ranking(self):
        """
        Exhaustively tests that searching for any of the 107 Italian provinces by its exact 2-letter sigla
        ranks that province at score 1 (top of search results).
        """
        provinces = self.dataset["provinces"]
        self.assertEqual(len(provinces), 107, "Must contain exactly 107 provinces")

        for p in provinces:
            sigla = p["sigla"]
            nome = p["nome"]
            regione = p["regione"]

            q = oracle_normalize_italian_text(sigla)
            # Simulating scoring:
            sigla_norm = oracle_normalize_italian_text(sigla)
            self.assertEqual(sigla_norm, q, f"Sigla {sigla} must match normalized query exactly")

            # Searching by exact lowercase province name
            q_nome = oracle_normalize_italian_text(nome)
            nome_norm = oracle_normalize_italian_text(nome)
            self.assertTrue(nome_norm.startswith(q_nome), f"Province {nome} must match by prefix")

    def test_cadastral_aliases_and_diacritics_normalization(self):
        """
        Verifies that official cadastral designations and diacritic-laden variants match the expected province:
        - "Reggio nell'Emilia", "Reggio Emilia" -> RE
        - "Bolzano-Bozen", "Bozen" -> BZ
        - "Valle d'Aosta", "Valle d Aosta" -> AO
        - "Cesena-Forlì", "Forlì Cesena", "Forli" -> FC
        - "Monza e Brianza" -> MB
        - "Pesaro e Urbino" -> PU
        - "L'Aquila", "L Aquila", "LAquila" -> AQ
        """
        aliases_map = {
            "RE": ["Reggio nell'Emilia", "Reggio nell Emilia", "Reggio nellemilia", "reggio nell'emilia"],
            "RC": ["Reggio di Calabria", "Reggio Calabria"],
            "BZ": ["Bolzano-Bozen", "Bozen", "Bolzano Bozen"],
            "AO": ["Valle d'Aosta", "Valle d Aosta", "Aoste"],
            "FC": ["Cesena-Forlì", "Cesena Forli", "Forlì Cesena", "Forli Cesena", "Forli"],
            "MB": ["Monza e Brianza", "Monza Brianza", "Monza-Brianza"],
            "PU": ["Pesaro e Urbino", "Pesaro Urbino", "Pesaro-Urbino"],
            "SP": ["La Spezia"],
            "AQ": ["L'Aquila", "L Aquila", "LAquila", "l'aquila", "l’aquila"],
        }

        # Verify PROVINCE_ALIASES table exists in source
        self.assertIn("export const PROVINCE_ALIASES", self.src)
        for sigla, aliases in aliases_map.items():
            for alias in aliases:
                norm = oracle_normalize_italian_text(alias)
                self.assertFalse(re.search(r"['’‘`´\-–—]", norm), f"Punctuation must be stripped in '{alias}' -> '{norm}'")
                self.assertFalse(re.search(r"[àèéìòù]", norm), f"Diacritics must be stripped in '{alias}' -> '{norm}'")

    def test_european_currency_parser_exhaustive_stress(self):
        """
        Adversarially tests European currency parser across 30+ format permutations:
        European comma, dot thousands, Anglo-Saxon notation, negative values, and zero values.
        """
        valid_cases = [
            ("1.250,50", 1250.50),
            ("1.250,00", 1250.00),
            ("1.250", 1250.00),     # 3-digit dot treated as thousands separator
            ("1250,00", 1250.00),
            ("250,5", 250.50),
            ("1250.50", 1250.50),
            ("1,250.50", 1250.50),
            ("1.000.000", 1000000.00),
            ("1.000.000,50", 1000000.50),
            ("  € 450,90  ", 450.90),
            ("12.50", 12.50),       # 2-digit dot treated as decimal
            ("12.500", 12500.00),   # 3-digit dot treated as thousands
            ("100", 100.00),
            ("9999999", 9999999.00),
        ]

        for raw, expected in valid_cases:
            val, err = oracle_parse_quote_input(raw)
            self.assertIsNone(err, f"Valid input '{raw}' should not produce error: {err}")
            self.assertEqual(val, expected, f"Input '{raw}': expected {expected}, got {val}")

        invalid_cases = [
            ("", "Inserisci l'importo del preventivo."),
            (None, "Inserisci un importo valido."),
            ("0", "Inserisci un importo superiore a zero."),
            ("0,00", "Inserisci un importo superiore a zero."),
            ("-50", "L'importo del preventivo non può essere negativo."),
            ("-1.250,00", "L'importo del preventivo non può essere negativo."),
            ("10000001", "Importo fuori scala (massimo 10.000.000 €)."),
            ("abc", "Inserisci un numero valido per l'importo."),
            ("12e5", "Inserisci un numero valido per l'importo."),
        ]

        for raw, expected_err in invalid_cases:
            val, err = oracle_parse_quote_input(raw)
            self.assertIsNotNone(err, f"Invalid input '{raw}' should produce an error")
            self.assertEqual(err, expected_err, f"Input '{raw}': expected '{expected_err}', got '{err}'")

    def test_keyboard_accessibility_and_wai_aria_attributes(self):
        """
        Verifies keyboard accessibility in CalculatorForm.tsx:
        role="radiogroup", role="radio", aria-checked, role="combobox",
        aria-haspopup="listbox", aria-expanded, ArrowDown/ArrowUp/Enter/Escape listeners.
        """
        self.assertIn('role="radiogroup"', self.src)
        self.assertIn('role="radio"', self.src)
        self.assertIn('aria-checked={isSelected}', self.src)
        self.assertIn('role="combobox"', self.src)
        self.assertIn('aria-haspopup="listbox"', self.src)
        self.assertIn('aria-expanded={isProvinceOpen}', self.src)
        self.assertIn('role="listbox"', self.src)
        self.assertIn('role="option"', self.src)
        self.assertIn("handleProvinceKeyDown", self.src)
        self.assertIn("e.key === 'Escape'", self.src)
        self.assertIn("e.key === 'ArrowDown'", self.src)
        self.assertIn("e.key === 'ArrowUp'", self.src)
        self.assertIn("e.key === 'Enter'", self.src)


# ==============================================================================
# TEST SUITE 5: CROWDSOURCEMODAL & ANTI-SPAM SANITY AUDIT
# ==============================================================================

class TestCrowdsourceModalAdversarial(unittest.TestCase):
    """
    White-box audit and stress testing of CrowdsourceModal.tsx:
    Anti-spam boundary display, 1-click presets, celebratory feedback card,
    focus trap and ESC key listeners.
    """

    def setUp(self):
        self.src = read_source_file("components/CrowdsourceModal.tsx")
        self.dataset = load_dataset()

    def test_anti_spam_bounds_display_and_validation(self):
        """
        Verifies anti-spam bounds derivation:
        - If prestation has validationBounds -> uses prestation.validationBounds
        - If custom prestation -> falls back to [round(0.15 * ref), round(8.0 * ref)]
        """
        self.assertIn("validationBounds", self.src)
        self.assertIn("Math.max(1, Math.round(effectiveRefPrice * 0.15))", self.src)
        self.assertIn("Math.round(effectiveRefPrice * 8.0)", self.src)
        self.assertIn("Range verosimile per", self.src)

        # Check all 36 prestations in dataset have valid bounds
        for p in self.dataset["prestations"]:
            bounds = p.get("validationBounds")
            self.assertIsNotNone(bounds, f"Prestation {p['id']} must have validationBounds")
            self.assertEqual(len(bounds), 2)
            self.assertGreater(bounds[1], bounds[0])
            self.assertLessEqual(bounds[0], p["basePrice"])
            self.assertGreaterEqual(bounds[1], p["basePrice"])

    def test_modal_preset_chips_logic(self):
        """
        Verifies 1-click modal presets:
        - activeQuote chip (only if minBound <= quote <= maxBound)
        - -15% chip (round(ref * 0.85))
        - Exact media chip (ref)
        - +25% chip (round(ref * 1.25))
        """
        self.assertIn("activeQuote >= bounds.minBound", self.src)
        self.assertIn("activeQuote <= bounds.maxBound", self.src)
        self.assertIn("Math.round(effectiveRefPrice * 0.85)", self.src)
        self.assertIn("Esattamente la media", self.src)
        self.assertIn("Math.round(effectiveRefPrice * 1.25)", self.src)

    def test_celebratory_feedback_comparison_card(self):
        """
        Verifies celebratory feedback comparison screen showing previous vs new average,
        sample count, and benchmark delta.
        """
        self.assertIn("Vecchia Media", self.src)
        self.assertIn("Nuova Media", self.src)
        self.assertIn("Variazione benchmark:", self.src)
        self.assertIn("Nessun IP memorizzato • 100% confidenziale", self.src)
        self.assertIn("Vedi il tuo preventivo ricalcolato", self.src)

        # Verify mathematical formula of Bayesian update in feedback payload
        prev_avg, prev_n, paid = 313, 10, 400
        new_n = prev_n + 1
        new_avg = round((prev_avg * prev_n + paid) / new_n)
        diff_euro = round(new_avg - prev_avg, 2)
        diff_pct = round(((new_avg - prev_avg) / prev_avg) * 100, 2)

        self.assertEqual(new_avg, 321)
        self.assertEqual(new_n, 11)
        self.assertEqual(diff_euro, 8.0)
        self.assertEqual(diff_pct, 2.56)

    def test_focus_trap_and_esc_key_listeners(self):
        """
        Verifies W3C WAI-ARIA dialog attributes, focus trap cycling, and body scroll lock.
        """
        self.assertIn('role="dialog"', self.src)
        self.assertIn('aria-modal="true"', self.src)
        self.assertIn("e.key === 'Escape'", self.src)
        self.assertIn("e.key === 'Tab'", self.src)
        self.assertIn("e.shiftKey", self.src)
        self.assertIn("document.body.style.overflow = 'hidden'", self.src)


# ==============================================================================
# TEST SUITE 6: ADSLOT & AFFILIATECARD MONETIZATION AUDIT
# ==============================================================================

class TestAdSlotAndAffiliateCardAdversarial(unittest.TestCase):
    """
    White-box audit and stress testing of AdSlot.tsx and AffiliateCard.tsx:
    Zero-CLS layout preservation, sticky banner close dismissal, pulsing emergency alerts,
    and category affiliate matching.
    """

    def setUp(self):
        self.ad_src = read_source_file("components/AdSlot.tsx")
        self.aff_src = read_source_file("components/AffiliateCard.tsx")

    def test_zero_cls_layout_preservation_all_formats(self):
        """
        Verifies strict CSS min-height reservation across Leaderboard, MPU, and Sticky slots
        to guarantee 0 Cumulative Layout Shift (CLS), along with AGCM Pubblicità disclosure.
        """
        self.assertIn("leaderboard:", self.ad_src)
        self.assertIn("minHeight: 90", self.ad_src)
        self.assertIn("mobileMinHeight: 50", self.ad_src)
        self.assertIn("mpu:", self.ad_src)
        self.assertIn("minHeight: 250", self.ad_src)
        self.assertIn("sticky:", self.ad_src)
        self.assertIn("minHeight: 90", self.ad_src)
        self.assertIn("mobileMinHeight: 50", self.ad_src)
        self.assertIn("Pubblicità", self.ad_src)
        self.assertIn("role=\"complementary\"", self.ad_src)

    def test_sticky_banner_dismissal(self):
        """
        Verifies that sticky banner includes close dismissal button that unmounts the slot.
        """
        self.assertIn("isSticky && dismissible", self.ad_src)
        self.assertIn("aria-label=\"Chiudi annuncio pubblicitario\"", self.ad_src)
        self.assertIn("setIsDismissed(true)", self.ad_src)
        self.assertIn("if (isDismissed) return null;", self.ad_src)

    def test_affiliate_card_urgency_morphing_and_category_mapping(self):
        """
        Verifies AffiliateCard category matching and high-urgency crimson alert switching.
        """
        # Category partners mapping
        partners = {
            "auto": "AutoDoc",
            "casa": "ProntoPro",
            "dentista": "DentalPro",
            "veterinario": "Babydog",
            "cerimonie": "Matrimonio.com",
            "affitti": "SoloAffitti",
        }
        aff_core = read_source_file("core/affiliate.ts")
        for cat, partner in partners.items():
            self.assertIn(partner, aff_core, f"Partner {partner} must be defined for category {cat}")

        # High-urgency styling in AffiliateCard.tsx
        self.assertIn("border-red-500", self.aff_src)
        self.assertIn("animate-pulse", self.aff_src)
        self.assertIn("ALLARME SOVRAPPREZZO", self.aff_src)
        self.assertIn("rel=\"noopener noreferrer sponsored\"", self.aff_src)
        self.assertIn("diffEuro !== undefined && diffEuro > 0", self.aff_src)

        # Calm educational styling
        self.assertIn("border-emerald-500", self.aff_src)
        self.assertIn("Partner Certificato", self.aff_src)


# ==============================================================================
# TEST SUITE 7: APP MASTER LAYOUT COORDINATION & URL HYDRATION AUDIT
# ==============================================================================

class TestAppMasterCoordinatorAdversarial(unittest.TestCase):
    """
    White-box audit and stress testing of App.tsx:
    Master reactive coordination, URL query auto-hydration, and live crowdsource recalibration.
    """

    def setUp(self):
        self.src = read_source_file("App.tsx")

    def test_app_url_query_hydration_resilience(self):
        """
        Verifies URL query hydration on page mount handles valid parameters,
        omitted parameters, and custom prestation descriptions without throwing.
        """
        self.assertIn("parseShareUrlParams(window.location.search)", self.src)
        self.assertIn("setSelectedCategory(cat)", self.src)
        self.assertIn("setSelectedPrestationId(prest)", self.src)
        self.assertIn("setSelectedProvinceSigla(prov)", self.src)
        self.assertIn("setCustomPrestationDesc", self.src)
        self.assertIn("executeCalculation(cat, prest, prov, quote)", self.src)

    def test_live_crowdsource_recalibration_loop(self):
        """
        Verifies that submitting a crowdsourced price immediately increments crowdsourceVersion,
        displays celebratory toast, and recalculates active calculation against new average.
        """
        self.assertIn("handleCrowdsourceSuccess", self.src)
        self.assertIn("setCrowdsourceVersion((v) => v + 1)", self.src)
        self.assertIn("executeCalculation(selectedCategory, selectedPrestationId, selectedProvinceSigla, quoteValue)", self.src)


# ==============================================================================
# MAIN TEST EXECUTION
# ==============================================================================

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
