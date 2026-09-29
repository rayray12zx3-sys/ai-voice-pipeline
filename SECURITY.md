# Security

## Secrets

Never commit:

- `GEMINI_API_KEY`
- OAuth tokens
- cookies or session exports
- private customer/company scripts
- private voice reference or consent audio

The CLI reads `GEMINI_API_KEY` only from the environment and does not place it in receipts.

## Public repository boundary

This repository is currently public. Examples and fixtures must therefore be synthetic or explicitly safe to publish.

Generated media, receipts, `.env*`, and common local environment directories are ignored by Git.

## Voice replication

Voice replication is intentionally not implemented in R0. Any future implementation must require explicit consent/provenance handling and must not treat arbitrary reference audio as sufficient authorization.

## Reporting

For now, use a private GitHub security advisory for sensitive vulnerability reports rather than opening a public issue.
