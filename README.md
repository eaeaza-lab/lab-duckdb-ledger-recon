# DuckDB Ledger Reconciliation Lab

**Status: work in progress**

A local learning and showcase CLI for generating synthetic sales, payment, invoice, and tax-ledger data; reconciling it in DuckDB; explaining mismatches; and exporting an auditable HTML report. It never needs network access at runtime.

Built by a supervised autonomous agent pipeline (nightshift).

## Run

Use Python 3.11 or later. Install dependencies in an environment, then generate deterministic local data:

```powershell
python -m pip install -e .
ledger-recon generate --seed 42 --output tmp/data
python -m unittest discover -s tests -v
```

`generate` writes four CSV files (`sales`, `payments`, `invoices`, and `tax_ledger`) and a
`discrepancies.json` manifest. The manifest documents four deliberate, synthetic differences;
the reconciliation and report steps are planned next. See [PLANS.md](PLANS.md) and [SPEC.md](SPEC.md).

## Safety

The project is synthetic-data-only. Do not add real company, person, marketplace, account, or secret data.
