# Future-session guide

## Commands

- Run the offline test suite: `python -m unittest discover -s tests -v`
- Run the CLI scaffold: `python -m ledger_recon.cli`
- Install locally after dependencies are available: `python -m pip install -e .`

## Rules

- Keep all data synthetic, deterministic when seeded, and local.
- Do not add real companies, people, marketplaces, account identifiers, secrets, credentials, remote integrations, or runtime network access.
- Keep rules auditable and retain synthetic source-row identifiers in findings.
- Add or update tests with behavioral changes; run the offline test command before handoff.
- Do not commit unless the user explicitly asks.
- Keep generated reports and local database files out of Git.
