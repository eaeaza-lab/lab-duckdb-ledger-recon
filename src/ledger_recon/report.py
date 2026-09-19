"""Standalone HTML audit reports for local reconciliation findings."""

from __future__ import annotations

import json
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
    :root { color-scheme: light; font-family: system-ui, sans-serif; color: #172033; background: #f5f7fb; }
    body { margin: 0; padding: 2rem; }
    main { max-width: 1100px; margin: auto; background: #fff; padding: 2rem; border-radius: .5rem; box-shadow: 0 1px 4px #17203322; }
    h1 { margin-top: 0; } .note { color: #4b5563; }
    table { width: 100%; border-collapse: collapse; margin: 1rem 0 2rem; font-size: .9rem; }
    th, td { padding: .65rem; border: 1px solid #d7ddea; text-align: left; vertical-align: top; }
    th { background: #eaf0fb; } .number { text-align: right; font-variant-numeric: tabular-nums; }
    code { white-space: nowrap; } .empty { color: #6b7280; }
  </style>
</head>
<body>
  <main>
    <h1>Synthetic ledger reconciliation audit report</h1>
    <p class="note">Local, synthetic data only. Currency: <strong>{{ currency }}</strong>.</p>

    <h2>Ledger totals</h2>
    <table>
      <thead><tr><th>Check</th><th>Expected total</th><th>Observed total</th><th>Difference</th></tr></thead>
      <tbody>
      {% for check in aggregate_checks %}
        <tr><td><code>{{ check.check_id }}</code></td><td class="number">{{ check.expected_total }}</td><td class="number">{{ check.observed_total }}</td><td class="number">{{ check.difference_amount }}</td></tr>
      {% else %}
        <tr><td colspan="4" class="empty">No aggregate checks were supplied.</td></tr>
      {% endfor %}
      </tbody>
    </table>

    <h2>Transaction findings</h2>
    <table>
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
    </table>
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


def render_report(findings_file: Path, output_file: Path) -> Path:
    """Render findings JSON to a self-contained, safely escaped HTML audit report."""
    findings = _read_findings(findings_file)
    environment = Environment(autoescape=select_autoescape(default_for_string=True), undefined=StrictUndefined)
    environment.filters["amount"] = _amount
    html = environment.from_string(REPORT_TEMPLATE).render(**findings)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html, encoding="utf-8")
    return output_file
