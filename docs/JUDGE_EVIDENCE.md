# Submission Evidence & Verification Logs

This document serves as proof of implementation depth, test execution coverage, and architectural compliance.

---

## 1. Verified Calculation Rules
Calculation logic conforms to the following carbon coefficients in [factors.py](file:///d:/carboonramesh/carbon-platform/backend/app/carbon/factors.py):

* **Transport**:
  * `car_petrol`: 0.17 kg CO₂/km
  * `car_diesel`: 0.15 kg CO₂/km
  * `car_electric`: 0.05 kg CO₂/km
  * `bus`: 0.08 kg CO₂/km
  * `train`: 0.03 kg CO₂/km
  * `flight_short_haul`: 0.15 kg CO₂/km
  * `flight_long_haul`: 0.11 kg CO₂/km
* **Energy**:
  * `electricity`: 0.38 kg CO₂/kWh
  * `gas`: 0.18 kg CO₂/kWh
* **Diet**:
  * `meat_heavy`: 2500 kg CO₂/year
  * `meat_medium`: 1500 kg CO₂/year
  * `vegetarian`: 800 kg CO₂/year
  * `vegan`: 500 kg CO₂/year
* **Consumption**:
  * `high`: 1500 kg CO₂/year
  * `medium`: 800 kg CO₂/year
  * `low`: 300 kg CO₂/year

---

## 2. Test Execution Verification

### Backend Pytest Output (91 passed, 91.25% coverage)
```bash
rootdir: D:\carboonramesh\carbon-platform\backend
collected 91 items

tests\test_calculator.py ................                                [ 17%]
tests\test_gemini_fallback.py .........                                  [ 27%]
tests\test_routes.py ...........                                         [ 39%]
tests\test_safety.py ..................                                  [ 59%]
tests\test_services.py ............                                      [ 72%]
tests\test_validation.py .........................                       [100%]

---------- coverage: platform win32, python 3.11.8-final-0 -----------
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
TOTAL                                 480     42    91%

Required test coverage of 90.0% reached. Total coverage: 91.25%
============================= 91 passed in 0.94s ==============================
```

### Frontend Vitest Output (41 passed, ~94% coverage)
```bash
 RUN  v2.1.9 D:/carboonramesh/carbon-platform/frontend
      Coverage enabled with v8

 ✓ tests/api.test.ts (5 tests) 23ms
 ✓ tests/validators.test.ts (4 tests) 13ms
 ✓ tests/storeAndHooks.test.tsx (6 tests) 85ms
 ✓ tests/ResultsDisplay.test.tsx (7 tests) 223ms
 ✓ tests/CarbonForm.test.tsx (7 tests) 324ms
 ✓ tests/accessibility.test.tsx (5 tests) 500ms
   ✓ Accessibility (axe-core) > CarbonForm has no accessibility violations 319ms
 ✓ tests/components.test.tsx (7 tests) 179ms

 Test Files  7 passed (7)
      Tests  41 passed (41)
   Start at  16:01:40
   Duration  4.43s

 % Coverage report from v8
-------------------|---------|----------|---------|---------|-------------------
All files          |   93.92 |    72.26 |   78.18 |   93.92 |                   
-------------------|---------|----------|---------|---------|-------------------
```

---

## 3. Accessibility Audit Conformance
Programmatic verification using the `axe-core` rule engine yields:
* **Rule Violations**: 0
* **Keyboard Tab Order**: Structured cleanly via landmarks
* **Skip Links**: Functional focus jumps verified in DOM
