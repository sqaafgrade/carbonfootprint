# Code Quality & Structural Standards

This document establishes the architecture-level code quality principles applied to the Carbon Footprint Awareness Platform.

---

## 1. Strict Typing & Type Safety
* **TypeScript Strict Mode**: The frontend [tsconfig.json](file:///d:/carboonramesh/carbon-platform/frontend/tsconfig.json) enforces `"strict": true`, `"noImplicitAny": true`, and strict checks on nullable values.
* **Mypy Static Typing**: The backend app utilizes `mypy app/ --strict` to verify type annotations for all classes, methods, and functions.

---

## 2. Separation of Concerns & Decoupled Architecture
* **Pure Calculator**: The emission coefficients and formulas are fully contained in [factors.py](file:///d:/carboonramesh/carbon-platform/backend/app/factors.py) and [calculator.py](file:///d:/carboonramesh/carbon-platform/backend/app/calculator.py). They contain zero I/O imports or API client interactions, allowing safe offline unit testing.
* **Lazy Client Initializations**: Cloud services client connections (BigQuery, Firestore, Pub/Sub) are singleton structures initialized lazily on the first request. This guarantees the application boots cleanly even if external GCP credentials are not present (`USE_*=false`).
* **Zustand State Store**: All state and form updates are structured inside [carbonStore.ts](file:///d:/carboonramesh/carbon-platform/frontend/src/store/carbonStore.ts), separating state updates from UI React component templates.

---

## 3. Input Validation Consistency
* **Pydantic v2 Models**: Backend API routes validate payloads using models defined in [carbon.py](file:///d:/carboonramesh/carbon-platform/backend/app/models/carbon.py) and [insights.py](file:///d:/carboonramesh/carbon-platform/backend/app/models/insights.py), with precise numeric constraints (`ge`/`le`) and regular expression formatting.
* **Zod Client Schemas**: Frontend uses a Zod schema configured in [validators.ts](file:///d:/carboonramesh/carbon-platform/frontend/src/utils/validators.ts) which mirrors the backend constraints field-for-field. This ensures input issues are caught in the browser before dispatching network requests.

---

## 4. Linting & Static Security Auditing
* **Ruff Formatting**: Formatter rules are configured to replace traditional imports sort and flake8.
* **Bandit Scan**: Audits Python code for common security vulnerabilities (e.g. usage of unsafe parsing methods, hardcoded credentials).
* **Pip-Audit**: Checks backend library versions against known CVE databases.
