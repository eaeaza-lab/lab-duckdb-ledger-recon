# Execution Plan

## Milestones

- [x] **M0 setup** *(mvp)* — Create specification, planning files, offline test command, package scaffold, and first passing test. Acceptance: `python -m unittest discover -s tests -v`
- [x] **M1 synthetic ledgers** *(mvp)* — Add deterministic synthetic sales, payments, invoices, and tax-ledger generators with documented discrepancies. Acceptance: `ledger-recon generate --seed 42 --output tmp/data`
- [ ] **M2 DuckDB reconciliation** *(mvp)* — Load data into DuckDB and implement keyed and aggregate reconciliation findings. Acceptance: `ledger-recon reconcile --input tmp/data --output tmp/findings.json`
- [ ] **M3 mismatch explanations** *(mvp)* — Classify mismatches and preserve source-row identifiers plus the applicable rule. Acceptance: `python -m unittest discover -s tests -v`
- [ ] **M4 HTML audit report** *(mvp)* — Render a standalone Jinja2 report with totals, findings, and provenance. Acceptance: `ledger-recon report --findings tmp/findings.json --output tmp/reconciliation-report.html`
- [ ] **M5 CLI workflow and docs** *(mvp)* — Complete Typer commands, validation, examples, and end-to-end offline test. Acceptance: `python -m unittest discover -s tests -v`
- [ ] **M6 polish** *(polish)* — Add terminal output, report styling, edge-case coverage, and reproducibility notes. Acceptance: `python -m unittest discover -s tests -v`

## Progress log

- 2026-09-16 — M0 complete: initialized the package scaffold, project documents, offline check configuration, and a passing package test.
- 2026-09-16 — M1 complete: added seeded local CSV ledger generation, a documented discrepancy manifest, and deterministic generator coverage.

## Decision log

- 2026-09-16 — Use deterministic synthetic data only, controlled by an explicit seed, so examples are safe and reproducible.
- 2026-09-16 — Keep the initial automated check standard-library based; later milestones may add project dependencies but checks must remain offline.
- 2026-09-16 — Keep outputs local and ignored by Git (`reports/`, database files).
- 2026-09-16 — Write monetary amounts as two-decimal strings with the synthetic `SYN` currency so future DuckDB checks can use exact decimal casts and readable source files.
