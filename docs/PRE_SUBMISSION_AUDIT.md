# Pre-Submission Audit — 2026-06-21

| Check | Status | Notes |
|---|---|---|
| Repo/Project ID consistency | ✅ | Repo `sqaafgrade/carbonfootprint` and GCP Project ID `carbonfootprint-sakshi` configured consistently everywhere. |
| All claimed files exist | ✅ | All core code files, test files, configs, rules, and reports exist. |
| ruff check | ✅ | Ruff reports "All checks passed!" |
| mypy --strict | ✅ | Strict type-checking configured and clean on backend. |
| pytest (backend) | ✅ | 91 passed, 91.25% coverage (above 90.0% threshold). |
| npm test (frontend) | ✅ | 41 passed, ~94% coverage (above 70.0% threshold). |
| npm run typecheck | ✅ | Unified tsconfig compilation completes with 0 errors. |
| npm run lint | ✅ | ESLint checks complete with 0 errors. |
| npm run build | ✅ | Production static SPA bundle builds successfully in 4 seconds. |
| docker build | ❌ | Skipped as Docker daemon is not installed on this local Windows host. |
| README claims match code | ✅ | Checked CSP, PII redaction, rate limiting, and firestore rules match actual implementation. |
| Badges all functional | ✅ | Badge URL points correctly to workflow file paths. |
