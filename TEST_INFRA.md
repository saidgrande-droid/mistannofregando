# Test Infrastructure & Strategy: "Mi Stanno Fregando?"

## 1. Overview & Architecture

The testing infrastructure for "Mi Stanno Fregando?" is engineered as a dual-engine, 4-tier opaque-box test framework. It ensures 100% mathematical fidelity, geographical completeness, boundary safety, and user journey reliability across Italian consumer quote verification scenarios.

### Dual-Engine Design
1. **Zero-Dependency Python 3 Harness (`tests/standalone_test_suite.py`)**:
   - Built strictly with Python 3 standard library (`unittest`, `json`, `math`, `sys`).
   - Executes immediately in any environment without Node.js, npm, or network access.
   - Deterministic exit codes: `0` on pass, `1` on failure.
   - Provides complete mathematical, geographic, dataset, crowdsourcing, and persona verification.
2. **TypeScript / Vitest Test Suite (`tests/tier{1,2,3,4}_*.test.ts`)**:
   - Modern TypeScript test files co-located in `tests/`.
   - Directly imports interface contracts and core functions from `src/core/` and UI definitions.
   - Compatible with `vitest` or `jest` runners.

---

## 2. Test Execution Commands

### Primary Execution (Zero-Dependency Python 3)
```bash
python3 tests/standalone_test_suite.py
```
*Expected Output*:
```
...............................................................
----------------------------------------------------------------------
Ran 65 tests in 0.045s

OK (65/65 tests passed)
```

### TypeScript / Vitest Execution (When Node/Vitest environment is present)
```bash
# Run all tiers
npx vitest run

# Run specific tier
npx vitest run tests/tier1_features.test.ts
npx vitest run tests/tier2_boundaries.test.ts
npx vitest run tests/tier3_pairwise.test.ts
npx vitest run tests/tier4_e2e.test.ts
```

---

## 3. The 4-Tier Test Strategy

The test hierarchy is structured into 4 distinct verification tiers:

```
┌──────────────────────────────────────────────────────────┐
│ Tier 4: Real-World Scenarios (5 Italian Personas)        │
├──────────────────────────────────────────────────────────┤
│ Tier 3: Cross-Feature Combinations (Pairwise Matrices)   │
├──────────────────────────────────────────────────────────┤
│ Tier 2: Boundary & Corner Cases (>=5 per feature)        │
├──────────────────────────────────────────────────────────┤
│ Tier 1: Feature Coverage (>=5 per core capability)       │
└──────────────────────────────────────────────────────────┘
```

### Tier 1: Feature Coverage (>=5 test cases per feature)
Covers the happy-path behavior and contract adherence for all primary system capabilities:
1. **Calculator Discrepancy Engine**:
   - Exact percentage calculation `((quote - ref) / ref) * 100` for lower, equal, and higher quotes.
   - Euro difference calculation `quote - ref`.
   - Local reference price derivation `round(base * coeff)`.
   - Headline and subheadline generation in authentic Italian.
   - Proper return interface matching `CalculationResult`.
2. **Tachometer Gauge Visualization**:
   - Needle angle mapping within 200° arc: clamped to `[-100, 100]` degrees (or `[0, 180]` degrees).
   - Zone classification: `PREZZO_ONESTO` ($\le 0\%$), `NELLA_MEDIA` ($0\% < \Delta \le +35\%$), `TI_STANNO_FREGANDO` ($> +35\%$).
   - Alert trigger: `isAlert = true` if $\Delta_{\%} \ge 65\%$.
   - Color hex code assignment: Emerald Green `#10B981`, Amber `#F59E0B`, Crimson Red `#DC2626`.
   - Angle progression monotonicity across increasing quotes.
3. **Dataset & Geographic Lookup**:
   - Exhaustive coverage of all 107 Italian provinces with unique 2-letter sigle.
   - Multiplier bounds: minimum 0.80 (Enna), maximum 1.25 (Milano).
   - 6 categories (`auto`, `casa`, `dentista`, `veterinario`, `cerimonie`, `affitti`).
   - 36 standard prestations (6 per category) with positive base prices and realistic bounds.
   - Fallback behavior on province lookup.
4. **Crowdsourcing ("Io ho pagato X€")**:
   - Valid submission acceptance with `success: true`.
   - Bayesian online mean update: $N_{\text{new}} = N + 1$, $\text{avg}_{\text{new}} = \text{round}\left(\frac{\text{avg} \times N + \text{paid}}{N + 1}\right)$.
   - Storage persistence write event.
   - Multiple sequential submissions maintaining mathematical integrity.
   - Confirmation response structure matching `CrowdsourceResult`.
5. **Affiliate & Monetization Matching**:
   - Category-to-partner mapping (Auto $\rightarrow$ AutoDoc, Casa $\rightarrow$ ProntoPro, Dentista $\rightarrow$ DentalPro, etc.).
   - Standard CTA copy when price is honest or average.
   - High-urgency warning copy and red alert badge when `isOvercharged` is true.
   - Affiliate URL and tracking parameter inclusion.
   - Fallback partner handling.

### Tier 2: Boundary & Corner Cases (>=5 test cases per feature)
Tests the resilience of algorithms under extreme, adversarial, and degenerate inputs:
1. **Quote Boundaries**:
   - `quote = 0`: Handled gracefully (rejection or division guard).
   - Negative quotes (`quote = -100`): Rejected with validation error, no crash.
   - Exact threshold `diffPct = 0.000%`: Correctly classifies as `PREZZO_ONESTO`.
   - Exact threshold `diffPct = 35.000%`: Classified as `NELLA_MEDIA`, needle at boundary.
   - Exact threshold `diffPct = 65.000%`: Flags `isAlert = true`, classified as `TI_STANNO_FREGANDO`.
   - Astronomical quotes (`quote = 1,000,000 €`): Needle strictly clamped, diff calculated without integer overflow.
2. **Crowdsource Anti-Spam Bounds**:
   - Paid amount below lower bound (`paid < min_bound`): Rejected with validation error.
   - Paid amount above upper bound (`paid > max_bound`): Rejected with validation error.
   - Exact boundary values (`paid == min_bound`, `paid == max_bound`): Accepted.
   - Zero or negative paid amount: Rejected.
   - Non-numeric input strings: Sanitized or rejected without NaN contamination.
3. **Storage & Quota Resilience**:
   - Storage quota exceeded (simulate `QuotaExceededError`): Graceful fallback to memory store.
   - Corrupted JSON in localStorage: Safely recovered with default baseline dataset.
   - Missing localStorage API (SSR or private browsing): In-memory adapter functions seamlessly.
   - Concurrent/rapid consecutive storage writes: Atomic sample increments.
   - Key collision prevention: Distinct namespace keys per prestation and province.
4. **Display Advertising & Zero CLS**:
   - Fixed dimension constraints: Leaderboard `728x90` / `320x50`, MPU `300x250`, Sticky `320x50`.
   - Ad blocker active (scripts blocked): Container preserves aspect ratio without collapse or layout jump (Zero Cumulative Layout Shift).
   - Responsive viewport change: Layout adapts without shifting sibling content.

### Tier 3: Cross-Feature Combinations (Pairwise Matrices)
Tests non-linear interactions across independent variables:
- **Matrix 1**: Category $\times$ Province Multiplier Extremes (e.g., Dentista in Milano [1.25] vs Dentista in Enna [0.80]).
- **Matrix 2**: Quote Level $\times$ Affiliate CTA Urgency (Verifying CTA morphing across Green, Amber, Red).
- **Matrix 3**: Crowdsource Update $\times$ Subsequent Calculator Lookup (Submitting a high crowdsource price shifts subsequent reference price and needle angle).
- **Matrix 4**: Multi-Category Crowdsourcing Isolation (Updating `auto_tagliando` in `MI` does not affect `auto_tagliando` in `RM` or `casa_imbiancatura` in `MI`).
- **Matrix 5**: Extreme Geographic Pairings with Astronomical and Nominal Quotes.
- **Matrix 6**: Rapid Sequential Submissions across alternating categories.

### Tier 4: Real-World Scenarios (5 Realistic Italian Personas)
End-to-end simulations of actual consumer journeys from landing to viral sharing:
1. **Persona 1: Marco from Milan (Auto Tagliando Rip-Off)**:
   - Receives an expensive quote of 450 € for `auto_tagliando` (base 250 €, Milan ref 313 €).
   - Discrepancy is +43.8% (`TI_STANNO_FREGANDO`).
   - Receives high-urgency AutoDoc affiliate offer, triggers share card with Milan badge.
2. **Persona 2: Giulia from Rome (Dentist Filling Honest Deal)**:
   - Receives quote of 110 € for `dentista_otturazione` (base 120 €, Rome ref 142 €).
   - Discrepancy is -22.5% (`PREZZO_ONESTO`).
   - Speedometer needle stays in Green zone (calm copy), Giulia submits actual paid price of 110 € to crowdsource.
3. **Persona 3: Antonio from Naples (Home Boiler Emergency Overcharge)**:
   - Emergency replacement of boiler quoted at 3,200 € (base 1,800 €, Naples ref 1,728 €).
   - Discrepancy is +85.2% (`TI_STANNO_FREGANDO`, `isAlert = true`).
   - Red pulsing alert, viral WhatsApp copy generated ("SCAPPA! Ti stanno letteralmente fregando..."), ProntoPro 3-quote alternative shown.
4. **Persona 4: Sara from Palermo (Cat Vaccination Routine)**:
   - Quoted 48 € for `vet_vaccino` in Palermo (base 50 €, Palermo ref 46 €).
   - Discrepancy is +4.3% (`NELLA_MEDIA`).
   - Yellow amber needle, standard pet insurance affiliate box.
5. **Persona 5: Matteo from Florence (Wedding Photo Luxury Package)**:
   - Quoted 2,800 € for `cerimonia_foto` in Florence (base 1,600 €, Florence ref 1,824 €).
   - Discrepancy is +53.5% (`TI_STANNO_FREGANDO`).
   - Speedometer at upper warning band, Matrimonio.com alternative displayed.

---

## 4. Test Metric Goals

| Metric | Target | Verification Method |
|---|---|---|
| Total Automated Tests | $\ge 60$ tests | `python3 tests/standalone_test_suite.py` & Vitest |
| Province Coverage | 107/107 (100%) | Dataset integrity suite |
| Prestation Coverage | 36/36 (100%) | Dataset integrity suite |
| Category Coverage | 6/6 (100%) | Category enum suite |
| Mathematical Accuracy | $\Delta < 10^{-6}$ | Floating-point discrepancy unit checks |
| Exit Code Integrity | `0` = pass, `1` = fail | Shell return code validation |
