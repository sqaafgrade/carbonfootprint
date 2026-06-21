# Accessibility Compliance Report (WCAG 2.1 AA)

The Carbon Footprint Awareness Platform is designed from the ground up to follow **WCAG 2.1 Level AA** standards. Below are the specific code-level mechanisms implemented.

---

## 1. Keyboard Navigation & Bypass Blocks
* **Skip Link**: Implemented in [SkipLink.tsx](file:///d:/carboonramesh/carbon-platform/frontend/src/components/shared/SkipLink.tsx) to allow keyboard/screen-reader users to bypass repetitive header navigation and jump directly to `#main-content`.
* **Focus Indicator Styles**: Clear visible outlines are applied to all interactive controls (buttons, selects, inputs) in [accessibility.css](file:///d:/carboonramesh/carbon-platform/frontend/src/styles/accessibility.css).
* **Logical Tab Order**: Landmarks like `<header>`, `<main>`, and `<footer>` structure the pages to ensure logical focus movement.

---

## 2. Screen Reader Fallbacks & Semantic Markups
* **Category Chart Fallback Table**: Since SVG-based charts are decorative for screen readers, [CategoryChart.tsx](file:///d:/carboonramesh/carbon-platform/frontend/src/components/Calculator/CategoryChart.tsx) embeds a visually hidden `<table>` with appropriate `<caption>` and `scope="col"` headers using the `sr-only` class.
* **History Chart Narration**: [HistoryChart.tsx](file:///d:/carboonramesh/carbon-platform/frontend/src/components/History/HistoryChart.tsx) includes an invisible `<p>` block describing the data trend verbally.
* **Dynamic Announcements (ARIA Live)**:
  * [LoadingSpinner.tsx](file:///d:/carboonramesh/carbon-platform/frontend/src/components/shared/LoadingSpinner.tsx) uses `role="status"` to announce loading state transitions.
  * [InsightsList.tsx](file:///d:/carboonramesh/carbon-platform/frontend/src/components/Insights/InsightsList.tsx) uses `aria-live="polite"` to read newly loaded reduction tips.

---

## 3. Visual Adaptation (CSS Media Queries)
* **prefers-reduced-motion**: Configured in [accessibility.css](file:///d:/carboonramesh/carbon-platform/frontend/src/styles/accessibility.css) to disable transitions, translations, and scaling animations for vestibular-sensitive users.
* **prefers-contrast**: Tailored color variables to ensure a minimum contrast ratio of 4.5:1 (Level AA) or 7:1 (Level AAA) for text elements.
* **forced-colors**: Support for High Contrast / forced-colors operating system modes to render recognizable interactive control borders.

---

## 4. Accessibility Testing (axe-core)
Accessibility is validated programmatically using the `axe-core` suite in [accessibility.test.tsx](file:///d:/carboonramesh/carbon-platform/frontend/tests/accessibility.test.tsx).
This suite renders:
* `CarbonForm`
* `ResultsDisplay`
* `InsightsList`
* `SkipLink`
* `LoadingSpinner`

All tested components must maintain **0 axe-core violations** to pass the CI quality checks.
