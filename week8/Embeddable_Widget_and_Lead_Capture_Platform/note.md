0:00–0:40 — Introduction

“Hi, this is my FlyRank capstone project, an Embeddable Widget and Lead-Capture Platform.

The idea is that a customer can define a widget once, receive a single script tag, and embed that widget onto another website.

The platform then handles configuration, cross-origin rendering, validation, abuse protection, geo enrichment, persistence, notifications, and an owner dashboard.

The backend is built with FastAPI, with PostgreSQL for persistence and Redis for rate limiting.”

0:40–1:20 — Show the embed snippet

Run:

Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/widgets/a39a1f73-f9c6-4d48-a68b-213a9123d4a3/embed" `
    -Headers @{ "X-API-Key" = $apiKey }

Say:

“This is the authenticated owner endpoint.

The important part is this generated script tag.”

Point at:

<script src="http://localhost:8001/assets/widget.v1.js?id=380f2da6-d38d-4bcc-b3e3-53822a2faee4"></script>

“The customer does not need to copy HTML for every field. They only embed this one versioned JavaScript bundle.

The public widget ID tells the script which configuration to retrieve.”

1:20–2:10 — Show the external website

Switch to:

http://localhost:5500

Say:

“This is deliberately running on localhost:5500, while my API is running on localhost:8001, so this is a genuine second-origin browser flow.”

Point at the dynamically injected form.

“The form itself is not hard-coded into this website.

widget.v1.js loads from the backend, requests the public configuration, and dynamically renders the configured fields.

Here I have Name, Email and Message, along with the configured button text.”

Then enter:

Name: Phase Four Demo
Email: phase4demo@example.com
Message: Final capstone demonstration

Click Contact us.

Say:

“When the user submits this form, the JavaScript generates an idempotency key and sends the request cross-origin to the public submission API.”

2:10–3:00 — Explain the submission pipeline

While switching to dashboard or terminal, say:

“The submission then goes through the hardened public path.

First, the origin is checked against the widget’s allowed origins.

The request body has a hard size limit and is validated against the configured widget fields.

I also have a honeypot field for basic spam detection and Redis-based rate limiting.

If the submission passes those controls, the service attempts IP geo enrichment using a provider fallback strategy.

The submission is then stored in PostgreSQL, and a notification job is created separately.”

3:00–3:50 — Show the owner dashboard

Open:

http://localhost:8001/demo/dashboard

Connect with the API key and refresh.

Say:

“This is the authenticated owner dashboard.

All of these queries are tenant-scoped, so one tenant cannot simply retrieve another tenant’s submissions.”

Point at the metrics.

“At the top I show total submissions, submissions from the last 24 hours, and total widgets.”

Point at the table.

“The dashboard also exposes the stored payload, creation time, geo enrichment and provider information.”

Point out the newly submitted email if visible:

phase4demo@example.com

“This submission has come from the external website and is now visible to the widget owner.”

3:50–4:20 — Show analytics

Point at Geo breakdown.

“I also aggregate submissions geographically.

For example, these existing submissions show traffic from the United States.”

Then select Demo Contact Form from the widget dropdown.

Say:

“And analytics can also be scoped to an individual widget.”

You can mention your existing result:

2026-08-08 → 5 submissions
2026-08-09 → 1 submission

“The backend groups the widget submissions by day, which gives the owner a basic activity view.”

4:20–5:00 — Demonstrate resilience

I would use notification failure as your main resilience example.

Say:

“One design decision I focused on was ensuring that non-critical downstream failures do not break the lead-capture path.

For example, notification delivery runs asynchronously.”

Show, if prepared:

status = failed
attempts = 3
last_error = RuntimeError

Say:

“In this deliberate failure test, notification delivery failed three times and eventually moved to a failed state.

However, the original submission remained stored successfully.

So a notification outage does not cause the platform to lose the lead.”

Then briefly mention geo:

“I use the same principle for geo enrichment. If one provider fails, the service can fall back to another provider, and if both are unavailable, the submission is still stored without geo data.”

5:00–5:30 — Mention abuse controls

Say:

“The public endpoint is also designed with abuse controls in mind.

I tested oversized bodies returning 413, malformed submissions returning 422, honeypot spam being silently accepted but not stored, and repeated traffic being rate-limited.”

If you want to show the rate-limit result quickly:

202
202
202
202
202
429
Retry-After: 60

Say:

“The sixth request here is rejected with 429 Too Many Requests, including a Retry-After header.”

5:30–6:00 — Finish with tests and architecture

Show:

docker compose exec api pytest -q

Expected:

....................
20 passed

Say:

“The automated test suite is currently fully green with 20 passing tests.

Overall, the final architecture separates the critical submission path from optional integrations and background work.

The external website only needs one script tag, while the backend provides tenant authentication, dynamic configuration, CORS, validation, rate limiting, spam protection, provider fallback, persistence, background notifications and analytics.

That completes the capstone.”