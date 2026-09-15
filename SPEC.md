# DuckDB Ledger Reconciliation Lab — Specification

## Problem

Reconciling sales, payments, invoices, and tax ledgers is difficult to learn and demonstrate without handling sensitive financial records. This local CLI creates deterministic synthetic ledgers, reconciles them in DuckDB, explains each intentional mismatch, and produces an auditable HTML report.

## Target user

Data engineers, analytics engineers, finance-operations learners, and portfolio reviewers who want a safe, local example of a reconciliation workflow.

## MVP scope

- Generate deterministic synthetic sales, payment, invoice, and tax-ledger data.
- Store and query generated data locally with DuckDB; use Polars for data preparation.
- Provide a Typer CLI to generate data, reconcile it, and export one HTML report.
- Reconcile documented keys and totals, classify mismatches, and include source-row identifiers and rules in the report.
- Run entirely offline and use only synthetic identifiers and values.

## Explicit non-goals

- Connecting to banks, marketplaces, tax authorities, accounting systems, or any remote service.
- Ingesting, transmitting, or representing real company, person, marketplace, or account data.
- Providing accounting, tax, legal, or compliance advice.
- Production authentication, multi-user hosting, a graphical UI, or automatic record correction.

## Acceptance criteria

Each criterion is verifiable from a clean checkout after installing project dependencies.

1. Package tests pass: `python -m unittest discover -s tests -v`.
2. CLI help works offline: `python -m ledger_recon.cli --help`.
3. Deterministic data generation works: `ledger-recon generate --seed 42 --output tmp/data`.
4. Reconciliation emits findings: `ledger-recon reconcile --input tmp/data --output tmp/findings.json`.
5. HTML report export works: `ledger-recon report --findings tmp/findings.json --output tmp/reconciliation-report.html`.
6. Project checks pass offline: `python -m unittest discover -s tests -v`.
