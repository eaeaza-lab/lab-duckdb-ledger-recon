# DuckDB Ledger Reconciliation Lab

**Status: MVP complete**

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
a standalone HTML audit report with ledger totals, transaction findings, classifications, rules,
and source-row provenance. All commands validate the local input and output path type before
writing files; use `ledger-recon --help` or `ledger-recon <command> --help` for option details.

## Reproducibility

Use the same integer `--seed` to regenerate identical synthetic source ledgers. The example
above uses seed `42`; its files remain local under `tmp/` and can be removed when no longer needed.

## Safety

The project is synthetic-data-only. Do not add real company, person, marketplace, account, or secret data.
