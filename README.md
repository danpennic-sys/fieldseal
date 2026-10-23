# FieldSeal

**Local-first field job logger and QuantumGuard evidence pack generator for field operators.**

Offline. Deterministic. Pay once. Compatible with QuantumGuard CONTRACT-v1, VeriQuote, JobSeal, Evidence-Core, and Chaser.

## Why FieldSeal?

Field operators lose money when clients dispute completed work, authorization, or job details. FieldSeal captures the job (notes, status, location, media hashes) in the field or office, then seals it into a client-verifiable QuantumGuard evidence bundle.

- No SaaS. No subscription. Runs completely offline after key setup.
- Clients (or their auditors) verify the pack with the free QuantumGuard verifier (`qg verify` or HTTP).
- Pairs with VeriQuote for quoting, JobSeal for deeper media, LedgerLite/Chaser for invoicing and follow-up.
- Exports simple CSVs ready for Chaser import.

## Quick Start

```bash
# Optional but recommended for real Ed25519 signatures
pip install cryptography

python3 src/fieldseal.py --demo
python3 src/fieldseal.py --job samples/job-001.json --out sealed.json
```

Verify the output with the QuantumGuard CLI (from the quantumguard repo):

```bash
qg verify sealed.json
```

Expected verdict: PASS (when using real cryptography).

## What you can sell

| SKU       | Price | Includes                                      |
|-----------|-------|-----------------------------------------------|
| Operator  | $59   | CLI + HTML logger + key setup guide + 1-year email support |
| Command   | $179  | + batch mode + templates + reseller rights for client packs |
| Agency    | $449  | + white-label HTML + design partner onboarding |

Purchase / access: danpennic@gmail.com

Source remains free under Apache-2.0 OR MIT. Commercial Operator Pack sold separately.

## Stack Fit

- Python CLI (same family as VeriQuote, JobSeal, LedgerLite, PlanClose)
- Emits QuantumGuard CONTRACT-v1 bundles (Ed25519, deterministic hashing)
- Local key storage (PEM)
- Optional static HTML/JS logger for browser use (see static/)
- Ready for Chaser CSV export (next iteration)

## License

Apache-2.0 OR MIT
