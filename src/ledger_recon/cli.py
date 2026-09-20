"""Typer command-line workflow for the local synthetic ledger lab."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ledger_recon.reconcile import reconcile_to_file
from ledger_recon.report import render_report
from ledger_recon.synthetic import generate_data


app = typer.Typer(
    help="Generate, reconcile, and report on local synthetic ledgers.",
    no_args_is_help=True,
    add_completion=False,
)


def _input_directory(_: object, __: object, value: Path) -> Path:
    """Return an existing local directory or a clear CLI validation error."""
    if not value.is_dir():
        raise typer.BadParameter("must be an existing local directory")
    return value


def _output_directory(_: object, __: object, value: Path) -> Path:
    """Reject a file where a command needs a directory output."""
    if value.exists() and not value.is_dir():
        raise typer.BadParameter("must be a directory path, not an existing file")
    return value


def _input_file(_: object, __: object, value: Path) -> Path:
    """Return an existing local file or a clear CLI validation error."""
    if not value.is_file():
        raise typer.BadParameter("must be an existing local file")
    return value


def _output_file(_: object, __: object, value: Path) -> Path:
    """Reject an existing directory where a command needs a file output."""
    if value.exists() and value.is_dir():
        raise typer.BadParameter("must be a file path, not an existing directory")
    return value


@app.command()
def generate(
    seed: Annotated[int, typer.Option(help="Integer seed for reproducible synthetic data.")],
    output: Annotated[Path, typer.Option(help="Local directory for generated CSV and JSON files.", callback=_output_directory)],
) -> None:
    """Write deterministic, synthetic source ledgers and their rule manifest."""
    generate_data(output, seed)
    typer.echo(f"Generated synthetic ledgers in {output}")


@app.command()
def reconcile(
    input: Annotated[Path, typer.Option(help="Local directory created by generate.", callback=_input_directory)],
    output: Annotated[Path, typer.Option(help="Local JSON findings file to write.", callback=_output_file)],
) -> None:
    """Compare generated ledgers and write auditable reconciliation findings."""
    reconcile_to_file(input, output)
    typer.echo(f"Wrote reconciliation findings to {output}")


@app.command()
def report(
    findings: Annotated[Path, typer.Option(help="Local JSON findings file from reconcile.", callback=_input_file)],
    output: Annotated[Path, typer.Option(help="Local standalone HTML report to write.", callback=_output_file)],
) -> None:
    """Render reconciliation findings as a standalone local HTML audit report."""
    render_report(findings, output)
    typer.echo(f"Wrote HTML audit report to {output}")


def main() -> None:
    """Run the CLI application."""
    app()


if __name__ == "__main__":
    main()
