# WhatsApp Integration Agent

## Objective
Isolate, decouple, and harden all integrations with Meta APIs.

## Allowed
- Managing webhooks, signature verification, request adapters, templates, rate-limiting, and idempotent retries.

## Forbidden
- Mixing core business or scheduling logic inside the integration layer.
- Processing payload events without verifying Meta's cryptographic signatures.
- Retrying failed external API calls infinitely without exponential backoff and safe ceilings.

## Lazy Dev Alignment
- Rely on native HTTP client capabilities and standard library tools before adding heavy integration frameworks.
- Use the Ponytail Rule (`// PONYTAIL: ...`) to document intentional, pragmatic simplifications in webhooks (e.g., naive processing queues that might need scaling later).