# Technical Security Architecture & Threat Model

This document outlines the technical security controls implemented in the Carbon Footprint Awareness Platform.

---

## 1. Security Headers Middleware
All HTTP responses from the backend API are intercepted by middleware configured in [security.py](file:///d:/carboonramesh/carbon-platform/backend/app/core/security.py) to inject strict security headers:

* **Content Security Policy (CSP)**: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none';` (blocks cross-site scripting and unauthorized iframe framing).
* **HTTP Strict Transport Security (HSTS)**: `max-age=63072000; includeSubDomains; preload` (enforces HTTPS browser-wide for 2 years).
* **X-Content-Type-Options**: `nosniff` (prevents MIME sniffing).
* **X-Frame-Options**: `DENY` (prevents clickjacking attacks).
* **X-XSS-Protection**: `1; mode=block` (forces browser to block pages with detected XSS).
* **Permissions-Policy**: Restricts camera, microphone, and geolocation access (`camera=(), microphone=(), geolocation=()`).
* **Cache-Control**: `no-store, max-age=0` (ensures browser history caching doesn't leak calculations).

---

## 2. PII Redaction & Safety Filter
To guarantee "No PII stored" under GDPR/CCPA guidelines, the platform utilizes a robust security component [safety.py](file:///d:/carboonramesh/carbon-platform/backend/app/core/safety.py) before dispatching context to Vertex AI or logs:

* **Regex-based Redaction**: Scans all request parameters and textual prompts for potential email addresses, phone numbers, and credentials.
* **Redaction Output**: Automatically replaces sensitive values with `<REDACTED_EMAIL>`, `<REDACTED_PHONE>`, or `<REDACTED_SECRET>` respectively.
* **Offline Processing**: All calculations and redactions happen locally without third-party API exposure.

---

## 3. Rate Limiting
To defend against denial-of-service (DoS) and API abuse, we configure the `slowapi` library in [rate_limit.py](file:///d:/carboonramesh/carbon-platform/backend/app/core/rate_limit.py):

* `/api/calculate` endpoint: Restricts clients to **30 requests per minute** via `@limiter.limit("30/minute")`.
* `/api/insights` endpoint: Restricts clients to **20 requests per minute** via `@limiter.limit("20/minute")`.
* Keying: Requests are scoped by client IP address.

---

## 4. Firestore Device-scoped Authorization
Data isolation is guaranteed through anonymous identifiers:

* **Input Validation**: `device_id` is validated against `r"^[a-zA-Z0-9\-]+$"` to prevent injection.
* **Firestore Rules**: Configured in `firestore.rules` to permit data writes but restrict document reading strictly to the matching authenticated device identifier query.
* **No Updates/Deletes**: Historical footprints are immutable. Only `create` and `get` operations are permitted.
