# Contributing

## Development contract

- Python 3.11+
- Standard-library-only core
- Provider SDKs remain optional extras
- Tests must be offline by default
- Network/API calls require an explicit execution path
- Never add real secrets or private media to fixtures
- Provider-specific fields stay inside adapters when possible

## Validation

Run:

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
git diff --check
```

A real Gemini smoke test is separate evidence and must never be inferred from offline unit-test success.
