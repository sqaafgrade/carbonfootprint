# Security Policy & Disclosure Procedures

We take the security of the Carbon Footprint Awareness Platform seriously. This document details the reporting channels and security policies for this repository.

## Vulnerability Disclosure Policy
Please do not open GitHub issues for suspected security vulnerabilities. Instead, report them privately using the procedures detailed below.

### Reporting Channels
If you discover a security vulnerability, please send an email to:
* **Security Contact**: security@carbonfootprint-sakshi.com

We ask that you include:
1. A clear description of the vulnerability and its potential impact.
2. Steps to reproduce the issue (proof-of-concept scripts or API payloads).
3. Any mitigations or fixes you propose.

### Response Timeframe
* **Acknowledgement**: Within 48 hours.
* **Triage & Status**: Status updates every 7 days.
* **Remediation Target**: Fixes deployed within 30 days for high/critical vulnerabilities.

## Scope of Audited Elements
* **Core API Endpoint**: `/api/calculate` and `/api/insights`
* **Data Flow Protection**: BigQuery streaming, Firestore scoped queries
* **Input Validation**: Strict Zod constraints on the frontend, Pydantic v2 schemas on the backend
* **Security Headers**: HSTS, CSP, and CORS validation
