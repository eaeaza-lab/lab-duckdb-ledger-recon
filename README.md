# DuckDB Ledger Reconciliation Lab

**Status: work in progress**

A local learning and showcase CLI for generating synthetic sales, payment, invoice, and tax-ledger data; reconciling it in DuckDB; explaining mismatches; and exporting an auditable HTML report. It never needs network access at runtime.

Built by a supervised autonomous agent pipeline (nightshift).

## Run

Use Python 3.11 or later. Install dependencies in an environment, then run the current scaffold:

```powershell
python -m pip install -e .
python -m ledger_recon.cli
python -m unittest discover -s tests -v
```

The `generate`, `reconcile`, and `report` workflow is planned; see [PLANS.md](PLANS.md) and [SPEC.md](SPEC.md).

## Safety

The project is synthetic-data-only. Do not add real company, person, marketplace, account, or secret data.
