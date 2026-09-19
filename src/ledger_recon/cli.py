"""Command-line entry point for the local synthetic-ledger workflow."""

import argparse
from pathlib import Path

from ledger_recon.synthetic import generate_data
from ledger_recon.reconcile import reconcile_to_file
from ledger_recon.report import render_report


def main() -> None:
    """Run a local-only CLI command."""
    parser = argparse.ArgumentParser(
        prog="ledger-recon",
        description="Local synthetic-ledger reconciliation lab (work in progress).",
    )
    subparsers = parser.add_subparsers(dest="command")
    generate_parser = subparsers.add_parser("generate", help="write deterministic synthetic ledgers")
    generate_parser.add_argument("--seed", type=int, required=True, help="integer seed for reproducible data")
    generate_parser.add_argument("--output", type=Path, required=True, help="local directory for CSV and JSON output")
    reconcile_parser = subparsers.add_parser("reconcile", help="compare generated ledgers with DuckDB")
    reconcile_parser.add_argument("--input", type=Path, required=True, help="local directory containing generated CSV files")
    reconcile_parser.add_argument("--output", type=Path, required=True, help="local JSON findings file")
    report_parser = subparsers.add_parser("report", help="render a standalone HTML audit report")
    report_parser.add_argument("--findings", type=Path, required=True, help="local JSON findings file")
    report_parser.add_argument("--output", type=Path, required=True, help="local HTML report file")
    args = parser.parse_args()
    if args.command == "generate":
        generate_data(args.output, args.seed)
        print(f"Generated synthetic ledgers in {args.output}")
    elif args.command == "reconcile":
        reconcile_to_file(args.input, args.output)
        print(f"Wrote reconciliation findings to {args.output}")
    elif args.command == "report":
        render_report(args.findings, args.output)
        print(f"Wrote HTML audit report to {args.output}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
