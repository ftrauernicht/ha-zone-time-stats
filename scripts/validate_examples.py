#!/usr/bin/env python3
"""Validate every YAML example in examples/.

Only catches gross YAML/Jinja *syntax* errors, not undefined-variable or
missing-HA-filter errors -- doing that properly would require running a full
Home Assistant instance in CI, which is disproportionate for a docs repo.
"""
import re
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, TemplateSyntaxError

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "examples"

HA_TAGS = ["!secret", "!include", "!include_dir_list", "!include_dir_named", "!input"]


class HaTolerantLoader(yaml.SafeLoader):
    """A SafeLoader that treats HA-only YAML tags as opaque passthrough scalars."""


def _passthrough(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


for tag in HA_TAGS:
    HaTolerantLoader.add_constructor(tag, _passthrough)

JINJA_PATTERN = re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.DOTALL)


def check_jinja_syntax(value, path, errors):
    if not isinstance(value, str) or "{{" not in value and "{%" not in value:
        return
    env = Environment()
    try:
        env.parse(value)
    except TemplateSyntaxError as e:
        errors.append(f"{path}: Jinja syntax error: {e}")


def walk(value, path, errors):
    if isinstance(value, dict):
        for k, v in value.items():
            walk(v, path, errors)
    elif isinstance(value, list):
        for item in value:
            walk(item, path, errors)
    else:
        check_jinja_syntax(value, path, errors)


def main():
    yaml_files = sorted(EXAMPLES_DIR.rglob("*.yaml")) + sorted(EXAMPLES_DIR.rglob("*.yml"))
    errors = []

    for path in yaml_files:
        text = path.read_text(encoding="utf-8")
        try:
            data = yaml.load(text, Loader=HaTolerantLoader)
        except yaml.YAMLError as e:
            errors.append(f"{path}: YAML parse error: {e}")
            continue
        walk(data, path, errors)

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    print(f"OK: {len(yaml_files)} files validated")


if __name__ == "__main__":
    main()
