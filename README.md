# DuckDB Ledger Reconciliation Lab

**Status: Polish complete**

A local learning and showcase CLI for generating synthetic sales, payment, invoice, and tax-ledger data; reconciling it in DuckDB; explaining mismatches; and exporting an auditable HTML report. It never needs network access at runtime.

Built by a supervised autonomous agent pipeline (nightshift).

## Run

Use Python 3.11 or later. Install dependencies in an environment, then run the complete offline workflow:

```powershell
python -m pip install -e .
ledger-recon generate --seed 42 --output tmp/data
ledger-recon reconcile --input tmp/data --output tmp/findings.json
ledger-recon report --findings tmp/findings.json --output tmp/reconciliation-report.html
python -m unittest discover -s tests -v
```

`generate` writes four CSV files (`sales`, `payments`, `invoices`, and `tax_ledger`) and a
`discrepancies.json` manifest. The manifest documents four deliberate, synthetic differences.
`reconcile` uses DuckDB fixed-point decimal comparisons to write JSON with transaction-level
findings and ledger-total checks. Each finding includes the classification, documented rule,
plain-language rule description, and synthetic source-row identifiers needed to audit it. See
[PLANS.md](PLANS.md) and [SPEC.md](SPEC.md). `report` converts that portable findings JSON into
a standalone styled HTML audit report with a difference summary, ledger totals, transaction
findings, classifications, rules, and source-row provenance. The terminal confirms the generated
row counts and reconciliation/report finding totals. All commands validate the local input and
output path type before writing files; use `ledger-recon --help` or `ledger-recon <command> --help`
for option details.

## Demo

With the documented seed, the local workflow reports its auditable synthetic differences:

```text
Generated synthetic ledgers in tmp/data (12 sales, 11 payments, 12 invoices, 12 tax-ledger).
Wrote reconciliation findings to tmp/findings.json (4 transaction finding(s); 3 aggregate difference(s)).
Wrote HTML audit report to tmp/reconciliation-report.html (4 transaction finding(s)).
```

## Reproducibility

Use the same integer `--seed` to regenerate identical synthetic source ledgers. The example
above uses seed `42`; its files remain local under `tmp/` and can be removed when no longer needed.
The generated CSV and JSON content, reconciliation findings, and report content do not include a
timestamp, so rerunning the same workflow with the same seed produces comparable artifacts.

## Safety

The project is synthetic-data-only. Do not add real company, person, marketplace, account, or secret data.
