"""Standalone HTML audit reports for local reconciliation findings."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from jinja2 import Environment, StrictUndefined, select_autoescape


REPORT_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Synthetic ledger reconciliation audit report</title>
  <style>
    :root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; color: #14213d; background: #edf3f8; }
    body { margin: 0; padding: clamp(1rem, 4vw, 3rem); }
    main { max-width: 1120px; margin: auto; background: #fff; padding: clamp(1.25rem, 4vw, 3rem); border-radius: 1rem; box-shadow: 0 14px 38px #14213d1a; }
    h1, h2 { letter-spacing: -.025em; } h1 { margin: 0; font-size: clamp(1.75rem, 5vw, 2.5rem); } h2 { margin: 2.5rem 0 .75rem; font-size: 1.25rem; }
    .eyebrow { margin: 0 0 .5rem; color: #087e8b; font-size: .75rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
    .note { color: #52627a; } .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: .9rem; margin: 1.75rem 0; }
    .card { padding: 1rem; border: 1px solid #d7e2ee; border-radius: .75rem; background: #f8fbfe; } .card strong { display: block; color: #087e8b; font-size: 1.7rem; }
    .card span { color: #52627a; font-size: .85rem; } .status { padding: .2rem .55rem; border-radius: 99px; background: #fff1d6; color: #874c00; font-size: .78rem; font-weight: 700; }
    .table-wrap { overflow-x: auto; } table { width: 100%; border-collapse: separate; border-spacing: 0; margin: .75rem 0 2rem; font-size: .9rem; }
    th, td { padding: .75rem; border-bottom: 1px solid #dce6ef; text-align: left; vertical-align: top; } th { background: #e7f3f5; color: #075965; font-size: .76rem; letter-spacing: .04em; text-transform: uppercase; }
    th:first-child { border-radius: .5rem 0 0 0; } th:last-child { border-radius: 0 .5rem 0 0; } .number { text-align: right; font-variant-numeric: tabular-nums; }
    code { white-space: nowrap; color: #293d61; } .empty { color: #6b7280; } @media (max-width: 640px) { body { padding: 0; } main { border-radius: 0; } }
  </style>
</head>
<body>
  <main>
    <p class="eyebrow">Local audit artifact</p>
    <h1>Synthetic ledger reconciliation audit report <span class="status">{{ status_label }}</span></h1>
    <p class="note">Local, synthetic data only. Currency: <strong>{{ currency }}</strong>.</p>

    <section class="summary" aria-label="Reconciliation summary">
      <div class="card"><strong>{{ finding_count }}</strong><span>transaction finding(s)</span></div>
      <div class="card"><strong>{{ aggregate_difference_count }}</strong><span>aggregate difference(s)</span></div>
      <div class="card"><strong>{{ aggregate_checks | length }}</strong><span>ledger comparison(s)</span></div>
    </section>

    <h2>Ledger totals</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>Check</th><th>Expected total</th><th>Observed total</th><th>Difference</th></tr></thead>
      <tbody>
      {% for check in aggregate_checks %}
        <tr><td><code>{{ check.check_id }}</code></td><td class="number">{{ check.expected_total }}</td><td class="number">{{ check.observed_total }}</td><td class="number">{{ check.difference_amount }}</td></tr>
      {% else %}
        <tr><td colspan="4" class="empty">No aggregate checks were supplied.</td></tr>
      {% endfor %}
      </tbody>
    </table></div>

    <h2>Transaction findings</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>Check / transaction</th><th>Expected / observed / difference</th><th>Classification and rule</th><th>Source-row identifiers</th></tr></thead>
      <tbody>
      {% for finding in findings %}
        <tr>
          <td><code>{{ finding.check_id }}</code><br><code>{{ finding.transaction_id }}</code></td>
          <td class="number">{{ finding.expected_amount | amount }} / {{ finding.observed_amount | amount }} / {{ finding.difference_amount | amount }}</td>
          <td><code>{{ finding.classification }}</code><br><code>{{ finding.rule_id }}</code><br>{{ finding.rule_description }}</td>
          <td>{% for row_id in finding.source_row_ids %}<code>{{ row_id }}</code>{% if not loop.last %}, {% endif %}{% else %}<span class="empty">None</span>{% endfor %}</td>
        </tr>
      {% else %}
        <tr><td colspan="4" class="empty">No transaction findings were supplied.</td></tr>
      {% endfor %}
      </tbody>
    </table></div>
  </main>
</body>
</html>
"""


def _amount(value: Any) -> str:
    """Render absent amounts plainly without changing auditable decimal strings."""
    return "Missing" if value is None else str(value)


def _read_findings(findings_file: Path) -> dict[str, Any]:
    """Load the portable findings JSON required by the report."""
    if not findings_file.is_file():
        raise FileNotFoundError(f"Missing findings file: {findings_file}")
    try:
        data = json.loads(findings_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Findings file is not valid JSON: {findings_file}") from error
    if not isinstance(data, dict):
        raise ValueError("Findings JSON must be an object")
    if not isinstance(data.get("currency"), str):
        raise ValueError("Findings JSON must contain a currency string")
    for field in ("aggregate_checks", "findings"):
        if not isinstance(data.get(field), list) or not all(isinstance(item, dict) for item in data[field]):
            raise ValueError(f"Findings JSON must contain a {field} list of objects")
    return data


def _has_difference(value: Any) -> bool:
    """Return whether a serialised amount represents a reconciliation difference."""
    if value is None:
        return True
    try:
        return Decimal(str(value)) != Decimal("0")
    except (InvalidOperation, ValueError):
        return True


def _report_context(findings: dict[str, Any]) -> dict[str, Any]:
    """Add deterministic presentation totals without changing the findings artifact."""
    aggregate_difference_count = sum(
        _has_difference(check.get("difference_amount")) for check in findings["aggregate_checks"]
    )
    finding_count = len(findings["findings"])
    return {
        **findings,
        "finding_count": finding_count,
        "aggregate_difference_count": aggregate_difference_count,
        "status_label": "Differences found" if finding_count or aggregate_difference_count else "Reconciled",
    }


def render_report(findings_file: Path, output_file: Path) -> Path:
    """Render findings JSON to a self-contained, safely escaped HTML audit report."""
    findings = _read_findings(findings_file)
    environment = Environment(autoescape=select_autoescape(default_for_string=True), undefined=StrictUndefined)
    environment.filters["amount"] = _amount
    html = environment.from_string(REPORT_TEMPLATE).render(**_report_context(findings))
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html, encoding="utf-8")
    return output_file
