#!/usr/bin/env python3
"""
tests/test_seo_and_legal_compliance.py
Comprehensive verification suite for SEO readiness, structured data (JSON-LD),
crawling assets (robots.txt, sitemap.xml, favicon.svg), semantic heading hierarchy,
and GDPR/ePrivacy/AGCM legal footer + LegalModal compliance.
"""

import json
import os
import re
import unittest
import xml.etree.ElementTree as ET


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
COMP_DIR = os.path.join(SRC_DIR, "components")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestSEOMetadataAndCrawlers(unittest.TestCase):
    """Validates HTML SEO metadata, JSON-LD graph, favicon, robots.txt, and sitemap.xml."""

    def test_index_html_meta_tags_and_canonical(self):
        html = read_text(os.path.join(BASE_DIR, "index.html"))

        self.assertIn('<html lang="it">', html)
        self.assertIn('<link rel="canonical" href="https://mistannofregando.it/"', html)
        self.assertIn('<meta name="robots" content="index, follow', html)
        self.assertIn('<meta name="description"', html)
        self.assertIn('<meta name="keywords"', html)
        self.assertIn('<meta name="theme-color" content="#0F172A"', html)

        # Open Graph & Twitter Cards
        for prop in [
            'property="og:type"',
            'property="og:site_name"',
            'property="og:url"',
            'property="og:title"',
            'property="og:description"',
            'property="og:image"',
            'property="og:locale" content="it_IT"',
            'name="twitter:card" content="summary_large_image"',
            'name="twitter:title"',
            'name="twitter:description"',
            'name="twitter:image"',
        ]:
            self.assertIn(prop, html, f"Missing SEO meta attribute in index.html: {prop}")

    def test_json_ld_structured_data_graph_and_faq_sync(self):
        html = read_text(os.path.join(BASE_DIR, "index.html"))
        app_tsx = read_text(os.path.join(SRC_DIR, "App.tsx"))

        match = re.search(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(match, "Missing JSON-LD structured data script in index.html")
        payload = json.loads(match.group(1))

        self.assertEqual(payload.get("@context"), "https://schema.org")
        graph = payload.get("@graph", [])
        types = {node.get("@type"): node for node in graph}

        self.assertIn("Organization", types)
        self.assertIn("WebSite", types)
        self.assertIn("WebApplication", types)
        self.assertIn("FAQPage", types)

        self.assertEqual(types["Organization"].get("email"), "gadmediamanager@gmail.com")
        self.assertTrue(types["WebApplication"].get("isAccessibleForFree"))
        self.assertEqual(types["WebApplication"].get("offers", {}).get("price"), "0")

        faq_entities = types["FAQPage"].get("mainEntity", [])
        self.assertGreaterEqual(len(faq_entities), 5)

        # Every JSON-LD FAQ question must match visible FAQ_ITEMS in App.tsx
        for q_node in faq_entities:
            self.assertEqual(q_node.get("@type"), "Question")
            q_text = q_node.get("name", "")
            self.assertIn(
                q_text,
                app_tsx,
                f"JSON-LD FAQ question missing from visible App.tsx FAQ section: {q_text}",
            )

    def test_minimal_brandmark_svg_favicon(self):
        favicon_path = os.path.join(PUBLIC_DIR, "favicon.svg")
        self.assertTrue(os.path.isfile(favicon_path), "public/favicon.svg missing")
        svg = read_text(favicon_path)

        # Must be a clean geometric SVG without emoji characters
        self.assertIn("<svg", svg)
        self.assertIn("#0F172A", svg)
        self.assertIn("#10B981", svg)
        self.assertIn("#F59E0B", svg)
        self.assertIn("#F43F5E", svg)
        self.assertNotIn("🔍", svg)

        # Well-formed XML check
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))

    def test_robots_txt_and_sitemap_xml_valid(self):
        for directory in [BASE_DIR, PUBLIC_DIR]:
            robots_path = os.path.join(directory, "robots.txt")
            sitemap_path = os.path.join(directory, "sitemap.xml")

            self.assertTrue(os.path.isfile(robots_path), f"Missing robots.txt in {directory}")
            self.assertTrue(os.path.isfile(sitemap_path), f"Missing sitemap.xml in {directory}")

            robots_txt = read_text(robots_path)
            self.assertIn("User-agent: *", robots_txt)
            self.assertIn("Allow: /", robots_txt)
            self.assertIn("Sitemap: https://mistannofregando.it/sitemap.xml", robots_txt)

            sitemap_xml = read_text(sitemap_path)
            tree = ET.fromstring(sitemap_xml)
            locs = [
                elem.text
                for elem in tree.iter()
                if elem.tag.endswith("loc") and elem.text
            ]
            self.assertGreaterEqual(len(locs), 4)
            self.assertIn("https://mistannofregando.it/", locs)


class TestLegalComplianceAndSemanticFooter(unittest.TestCase):
    """Validates LegalModal.tsx, GDPR/Cookie/Terms/AGCM content, footer links, and bundle wiring."""

    def test_legal_modal_exists_exported_and_bundled(self):
        modal_path = os.path.join(COMP_DIR, "LegalModal.tsx")
        self.assertTrue(os.path.isfile(modal_path), "src/components/LegalModal.tsx missing")

        barrel = read_text(os.path.join(COMP_DIR, "index.ts"))
        self.assertIn("export * from './LegalModal'", barrel)

        builder = read_text(os.path.join(BASE_DIR, "build_bundle.py"))
        self.assertIn('"components/LegalModal.tsx"', builder)

    def test_legal_modal_regulatory_content_and_accessibility(self):
        src = read_text(os.path.join(COMP_DIR, "LegalModal.tsx"))

        # Accessibility modal contract
        self.assertIn('role="dialog"', src)
        self.assertIn('aria-modal="true"', src)
        self.assertIn('role="tablist"', src)
        self.assertIn('role="tab"', src)
        self.assertIn("Escape", src)

        # Required legal sections & regulatory mentions
        for token in [
            "Privacy Policy",
            "Cookie Policy",
            "Termini & Disclaimer",
            "AGCM & Titolare",
            "localStorage",
            "gadmediamanager@gmail.com",
            "Reg. UE 2016/679",
            "Google AdSense",
            "consenso",
            "PUBBLICITÀ",
            "Partita IVA / Codice Fiscale",
            "Titolare / Ragione Sociale",
            "Sede Legale",
        ]:
            self.assertIn(token, src, f"Missing legal/regulatory token in LegalModal.tsx: {token}")

    def test_app_semantic_headings_faq_and_legal_footer_wiring(self):
        app_tsx = read_text(os.path.join(SRC_DIR, "App.tsx"))

        # Semantic heading hierarchy: exactly one <h1> plus multiple <h2> & <h3>
        self.assertEqual(len(re.findall(r"<h1[\s>]", app_tsx)), 1, "App.tsx should render exactly one <h1>")
        self.assertGreaterEqual(len(re.findall(r"<h2[\s>]", app_tsx)), 4)
        self.assertGreaterEqual(len(re.findall(r"<h3[\s>]", app_tsx)), 4)

        # FAQ section & nav link
        self.assertIn('id="faq"', app_tsx)
        self.assertIn('href="#faq"', app_tsx)
        self.assertIn("Come funziona il Fregometro e Domande Frequenti", app_tsx)

        # Legal modal & footer buttons wiring
        self.assertIn("<LegalModal", app_tsx)
        self.assertIn("openLegalDocument('privacy')", app_tsx)
        self.assertIn("openLegalDocument('cookie')", app_tsx)
        self.assertIn("openLegalDocument('terms')", app_tsx)
        self.assertIn("openLegalDocument('transparency')", app_tsx)
        self.assertIn("Privacy Policy (GDPR)", app_tsx)
        self.assertIn("Cookie Policy", app_tsx)
        self.assertIn("Termini d&apos;Uso &amp; Disclaimer", app_tsx)
        self.assertIn("Trasparenza Pubblicitaria (AGCM)", app_tsx)
        self.assertIn("LEGAL_OWNER_DETAILS.vatPlaceholder", app_tsx)
        self.assertIn("LEGAL_OWNER_DETAILS.contactEmail", app_tsx)
        self.assertIn("Preferenze Cookie", app_tsx)
        self.assertIn("<CookieBanner", app_tsx)

    def test_og_preview_png_manifest_and_static_shell(self):
        import struct

        html = read_text(os.path.join(BASE_DIR, "index.html"))
        self.assertIn('<meta property="og:image:width" content="1200"', html)
        self.assertIn('<meta property="og:image:height" content="630"', html)
        self.assertIn('<link rel="manifest" href="./public/manifest.webmanifest"', html)
        self.assertIn("Semantic Static Pre-Hydration Shell", html)

        for directory in [BASE_DIR, PUBLIC_DIR]:
            og_path = os.path.join(directory, "og-preview.png")
            manifest_path = os.path.join(directory, "manifest.webmanifest")
            self.assertTrue(os.path.isfile(og_path), f"Missing og-preview.png in {directory}")
            self.assertTrue(os.path.isfile(manifest_path), f"Missing manifest.webmanifest in {directory}")

            with open(og_path, "rb") as f:
                header = f.read(24)
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            width, height = struct.unpack(">II", header[16:24])
            self.assertEqual((width, height), (1200, 630))

            manifest = json.loads(read_text(manifest_path))
            self.assertEqual(manifest.get("short_name"), "Fregometro")

    def test_cookie_banner_exported_bundled_and_compliant(self):
        banner_path = os.path.join(COMP_DIR, "CookieBanner.tsx")
        self.assertTrue(os.path.isfile(banner_path), "CookieBanner.tsx missing")
        src = read_text(banner_path)
        for token in [
            "COOKIE_CONSENT_STORAGE_KEY",
            "Solo essenziali",
            "Accetta tutti",
            "Leggi la Cookie Policy",
            "localStorage",
        ]:
            self.assertIn(token, src)

        barrel = read_text(os.path.join(COMP_DIR, "index.ts"))
        self.assertIn("export * from './CookieBanner'", barrel)
        builder = read_text(os.path.join(BASE_DIR, "build_bundle.py"))
        self.assertIn('"components/CookieBanner.tsx"', builder)


if __name__ == "__main__":
    unittest.main(verbosity=2)
