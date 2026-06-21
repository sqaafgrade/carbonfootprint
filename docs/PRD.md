# Product Requirements Document (PRD)

## 1. Product Overview
The **Carbon Footprint Awareness Platform** is an educational tool designed to help users calculate, track, and reduce their daily carbon emissions.

## 2. Core User Flow (The Loop)
1. **Calculate (Understand)**: Users enter commute distance, diet, consumption habits, and utility metrics to calculate their annual CO₂ footprint.
2. **Track (History)**: Anonymous calculation history is stored locally (and optionally backed up to Firestore) using a random device ID, mapping trends over time.
3. **Reduce (Insights)**: The user receives custom, actionable reduction tips parsed from Gemini AI or rule-based recommendations.

## 3. Scope & Key Features
* **Interactive Calculator Form**: Accessible form fields paired with labels and assistive helper descriptions.
* **Results Visualizer**: Progress bars comparing user output vs global average (5.0 tonnes) and Paris agreement target (2.0 tonnes), along with category breakdown charts.
* **Reduction Insights**: Severity-badged tips categorized by impact (high, medium, low).
* **Trend Analysis**: Line graph displaying changes in emissions over successive calculations.

## 4. Compliance & Constraints
* **Privacy**: Strict GDPR/CCPA compliance; no personal info (names, emails, credentials) is ever stored. PII is scrubbed before processing.
* **Accessibility**: Strict WCAG 2.1 Level AA conformance.
* **Resilience**: Graceful degradation; if GCP database or AI APIs fail, the local offline rules take over immediately.
