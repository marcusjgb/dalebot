# WhatsApp Integration

- Validate Meta's challenge and signature.
- Persist `event_id` before processing.
- Keep external payload isolated using adapters.
- Do not log tokens or full sensitive bodies.
- Handle duplicates, retries, and out-of-order events.
- Use approved templates when appropriate.
- Separate utility, service, and marketing messages.
