# Contributing

## Ground rules

- All changes land via Pull Request. Direct pushes to `main` are blocked for everyone, including the maintainer.
- Keep PRs focused: one logical change per PR.
- The `Validate examples` CI check (YAML/Jinja lint + the hex encode/decode round-trip test) must pass before a PR can be merged.

## Before opening a PR

```bash
pip install pyyaml jinja2
python scripts/validate_examples.py
python scripts/decode_archive_example.py
```

Both must pass locally.

## Naming conventions

- Use generic placeholders only: `person.person_a` / `person.person_b` for people, numbered placeholders (`Zone 1`, `Zone 2`, `Home`) if a zone name needs to appear literally anywhere.
- Never contribute an example based on your own real config with real names/places left in — genericize before opening the PR.
