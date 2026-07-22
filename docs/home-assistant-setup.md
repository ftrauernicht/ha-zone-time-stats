# Home Assistant Setup Guide

## Prerequisites

- Home Assistant Core/OS with YAML config access.
- The default SQLite recorder database (the SQL in `sql_sensors.yaml` uses SQLite-specific functions — `strftime`, `json_group_object`, window functions; adjust if you run a different recorder backend).
- For the dashboard example: [apexcharts-card](https://github.com/RomRider/apexcharts-card) via HACS.

## Step 1: the SQL sensors

Add [`examples/sql_sensors.yaml`](../examples/sql_sensors.yaml) — 4 sensors (2 people × this-month/last-month). Each uses a `LEAD() OVER` window function to pair consecutive state-change timestamps into durations, then sums them per zone via `json_group_object`.

Each sensor's `state` is a JSON string like `{"Home": 2415600, "Zone 1": 86400}` (seconds per zone name) — parse it with `| from_json` wherever you consume it.

**Adding a third person**: duplicate the two sensors for an existing person, swap every `person.person_a`/`person.person_b` reference for the new person's entity_id, give the new sensors their own `unique_id`, and add them to the archive automation in Step 3.

## Step 2: recorder retention

Add [`examples/recorder.yaml`](../examples/recorder.yaml): `purge_keep_days: 40`. The default retention (10 days) is shorter than what "last month" needs to see reliably — the window function needs visibility back across the whole of last month, which can be nearly two months away from "now" if queried early in the current month.

**This one needs a full restart**, not a reload — recorder config isn't hot-reloadable.

## Step 3: the monthly archive automation

The SQL sensors only ever show "this month"/"last month" — nothing older is retained anywhere. [`examples/automations/monthly-archive.yaml`](../examples/automations/monthly-archive.yaml) archives last month's numbers to a JSONL file on the 1st of each month.

### What doesn't work (and why it's worth knowing)

> **Wrong approach 1 — `notify: platform: file`.** This integration doesn't exist in current Home Assistant versions. It shows up in old forum posts as the "obvious" way to write a sensor's state to disk, and no longer works.

> **Wrong approach 2 — assuming a `b64encode` Jinja filter exists.** It doesn't. We checked directly against a live Home Assistant instance's template API (`POST /api/template`): `base64_encode(...)` renders `UndefinedError: 'base64_encode' is undefined` on the version tested. Don't rely on a base64 filter being available.

> **Wrong approach 3 — naive quote-escaping.** The obvious next idea: escape the JSON payload's quotes and wrap it in a `shell_command` string like `some_command 'echo {{ payload }} >> file.jsonl'`. This breaks because the JSON payload's own embedded double quotes collide with the shell wrapper's outer quoting. **The dangerous part: this bug is payload-content-dependent.** A "nice" payload with no awkward characters can pass casual testing every time, and the bug only surfaces once a payload happens to contain the wrong combination of characters — by which point it's a production incident, not a code review comment.

### The fix that works

Encode the entire JSON payload so that **only hex digits (`0-9a-f`) ever cross the shell boundary** — no shell metacharacters, no quotes, nothing a shell could misinterpret:

```jinja
{{ payload.encode('utf-8').hex() }}
```

We verified this directly against a live Home Assistant instance's template API before writing it here — `payload.encode('utf-8').hex()` renders correctly under HA's sandboxed Jinja (confirmed on the version tested; if your HA version's sandbox behaves differently, `scripts/decode_archive_example.py` in this repo will tell you immediately, since it exercises the exact same logic).

Then decode it on the other side inside a `python3 -c "..."` one-liner — python3 is guaranteed present in the HA Core container — instead of letting the shell touch the payload at all:

```yaml
shell_command:
  append_zone_stats_archive: >-
    python3 -c "import sys, json;
    data = bytes.fromhex(sys.argv[1]).decode('utf-8');
    open('/config/zone_stats_archive.jsonl', 'a').write(data + chr(10))"
    {{ payload_hex }}
```

The full automation in `examples/automations/monthly-archive.yaml` wires this together: build the JSON payload from the two `_last_month` sensors, hex-encode it, call the shell command.

## Step 4: the dashboard chart

[`examples/dashboard/time-in-zone-donut.yaml`](../examples/dashboard/time-in-zone-donut.yaml) — an `apexcharts-card` donut chart of one person's current-month breakdown, parsing the sensor's JSON state directly in a `data_generator`.

## Adapting to your own zones/people

- Zone names come from whatever your own `zone.*` entities and `person.state` values already are — nothing to configure, the SQL just reflects what your zones are called.
- To track more people, repeat Step 1's pattern and extend Step 3's archive automation.

## Apply without a restart

- SQL sensors and automations: **Developer Tools → YAML → Check Configuration**, then reload the `sql` and `automation` domains individually.
- `shell_command:` changes: reload the `shell_command` domain, or restart if unsure.
- **Recorder changes (Step 2) are the one exception in this repo** — they require a full restart, not a reload, regardless of which reload service you try.
