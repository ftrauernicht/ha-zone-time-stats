# CLAUDE.md

Guidance for Claude Code (or any AI coding agent) working in this repository.

## What this repo is

A reference implementation/template for Home Assistant per-person zone-dwell-time statistics via the core `sql:` platform, plus a monthly archival trick. It is pure documentation/example content — nothing here is live-polled by anything, unlike some other repos in this toolkit. There is no build step.

## Hard rules

- **Never commit directly to `main`.** Always work on a branch and open a Pull Request. Branch protection enforces this for everyone including the repo owner.
- `recorder:` config changes (see `examples/recorder.yaml`) typically require a **full Home Assistant restart** to take effect — unlike most domains in the broader `ha-*` toolkit, which can hot-reload. Never imply a reload service is sufficient for recorder changes.
- The archive automation's encode step (`payload.encode('utf-8').hex()` in `examples/automations/monthly-archive.yaml`) and the round-trip test in `scripts/decode_archive_example.py` must be kept in sync. Changing one without the other silently breaks the documented pipeline with no obvious error at the YAML level — the shell side and the HA side never round-trip-test each other in production, only in this repo's CI.
- Entity IDs and labels in examples must stay generic: `person.person_a`/`person.person_b` for people, numbered placeholders (`Zone 1`, `Zone 2`, `Home`) for zones if a zone name ever needs to appear literally in an example — never real names, real places, or real coordinates, in this repo or in any contributed PR.
- Run `python scripts/validate_examples.py` and `python scripts/decode_archive_example.py` after any YAML/script edit — both gate merging in CI.

## Repo layout

- `examples/sql_sensors.yaml` — the 4 SQL sensors.
- `examples/recorder.yaml` — retention tuning needed to support the SQL sensors.
- `examples/automations/monthly-archive.yaml` — the archival automation + its `shell_command:`.
- `examples/dashboard/time-in-zone-donut.yaml` — the apexcharts-card dashboard example.
- `scripts/validate_examples.py` — YAML/Jinja-syntax lint for everything under `examples/`.
- `scripts/decode_archive_example.py` — functional round-trip test for the hex-encode/decode trick.
- `.github/workflows/validate.yml` — CI job (`Validate examples`) required by branch protection before merge.
