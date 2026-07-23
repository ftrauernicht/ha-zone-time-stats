# ha-zone-time-stats

Per-person "how long did I spend in each zone this month" statistics for Home Assistant — computed purely with the core `sql:` platform against the recorder database. No pyscript, no AppDaemon, no custom integration.

## How it works

Home Assistant already records every zone/state change in its recorder database. [`examples/sql_sensors.yaml`](examples/sql_sensors.yaml) queries that database directly: a window function (`LEAD() OVER (...)`) pairs each state change with the *next* one, turning a list of timestamped zone-change events into a list of "spent N seconds in zone X" durations, summed per zone via `json_group_object`. Four sensors cover 2 people × {this month, last month}.

Adding a third tracked person is 2 more sensors (same pattern, different `person.*` entity_id) — see the header comment in `sql_sensors.yaml`.

## The catch: these sensors only ever show a rolling window

"This month" and "last month" are all you get — nothing older is retained by the sensors themselves. [`examples/automations/monthly-archive.yaml`](examples/automations/monthly-archive.yaml) archives last month's numbers to a JSONL file on the 1st of every month, so history accumulates indefinitely.

The interesting part of that automation isn't the archiving — it's *safely getting a JSON payload (which contains embedded double quotes) through `shell_command:` without a shell-quoting bug*. The naive approaches all break in ways that can pass silently in casual testing and only fail later. The fix: hex-encode the payload before it crosses the shell boundary, so only `0-9a-f` characters are ever at risk of shell interpretation. See [`docs/home-assistant-setup.md`](docs/home-assistant-setup.md) for the full story, including what doesn't work and why.

## Dashboard example

[`examples/dashboard/time-in-zone-donut.yaml`](examples/dashboard/time-in-zone-donut.yaml) is an `apexcharts-card` donut chart of one person's current-month zone breakdown (requires the `apexcharts-card` HACS card).

## Setup

See [`docs/home-assistant-setup.md`](docs/home-assistant-setup.md) for the full step-by-step guide.

## Related

- [ha-sun-blind-automation](https://github.com/ftrauernicht/ha-sun-blind-automation) — a different repo in this toolkit that also needs to know "who/whether someone is home" (for its away-mode automation), though that's a live presence check rather than this repo's historical dwell-time tracking.

Part of the `ha-*` Home Assistant toolkit — see also [ha-dashboard-recipes](https://github.com/ftrauernicht/ha-dashboard-recipes).

## Contributing

All changes land via Pull Request — see [CONTRIBUTING.md](CONTRIBUTING.md). Direct pushes to `main` are blocked, including for the maintainer.

## License

[MIT](LICENSE).
