"""Command-line entry point (workflow commands will arrive in M1)."""

import argparse


def main() -> None:
    """Print scaffold status without accessing the network."""
    parser = argparse.ArgumentParser(
        prog="ledger-recon",
        description="Local synthetic-ledger reconciliation lab (work in progress).",
    )
    parser.parse_args()
    print("duckdb-ledger-recon: work in progress")


if __name__ == "__main__":
    main()
