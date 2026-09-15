"""Command-line entry point for the local synthetic-ledger workflow."""

import argparse
from pathlib import Path

from ledger_recon.synthetic import generate_data


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
    args = parser.parse_args()
    if args.command == "generate":
        generate_data(args.output, args.seed)
        print(f"Generated synthetic ledgers in {args.output}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
