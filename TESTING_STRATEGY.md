# Comprehensive Testing Strategy

This document outlines the testing methodologies used to ensure correctness, reliability, and WCAG compliance.

---

## 1. Backend Testing Suite (Pytest)
Our Python backend uses `pytest` with `pytest-cov` to track test coverage, configured inside [pyproject.toml](file:///d:/carboonramesh/carbon-platform/backend/pyproject.toml).

* **Unit Tests**: Test math formulas and category rankings in `test_calculator.py`.
* **Validation Tests**: Verify numeric bounds and Regex device ID sanitization in `test_validation.py`.
* **Redaction Tests**: Verify PII scrubbing (emails, phone numbers) in `test_safety.py`.
* **Services & Fallback Tests**: Verify Gemini API timeouts and rule-based fallback responses in `test_gemini_fallback.py` and `test_services.py`.
* **Integration Tests**: Verify API endpoints, status codes, and HTTP security headers in `test_routes.py`.

We maintain a strict quality threshold: **Total test coverage must exceed 90.0%**.

---

## 2. Frontend Testing Suite (Vitest & React Testing Library)
Our frontend tests run inside Vitest with the `jsdom` browser-like environment:

* **Store & Custom Hooks**: Verify Zustand store state modifications and async loading flags in `storeAndHooks.test.tsx`.
* **Client-side Validations**: Verify Zod schema constraint checks in `validators.test.ts`.
* **Component Rendering**: Verify layout rendering and screen-reader visual fallback elements in `components.test.tsx` and `ResultsDisplay.test.tsx`.

---

## 3. Accessibility Verification (Axe-Core)
We programmatically run WCAG audits using `jest-axe` in [accessibility.test.tsx](file:///d:/carboonramesh/carbon-platform/frontend/tests/accessibility.test.tsx).
Every key component is mounted and parsed by `axe-core`. Tests fail if any WCAG AA violations are detected, guaranteeing zero visual barriers for screen readers or keyboard navigators.

---

## 4. Offline Testing Guarantee
None of the unit tests make external network requests. All Google Cloud service dependencies (BigQuery, Pub/Sub, Firestore) and Gemini APIs are fully mocked using `unittest.mock` patch configurations, allowing tests to run in sandboxed or offline CI/CD pipelines.
