# Airports Visited (site/airports/) — build tools, not published

`refresh.py` rebuilds `site/airports/index.html` from ForeFlight logbook pages (connector
`list_logbook_entries` results saved as JSON). See its header for usage, files and limits.

- Monthly scheduled task (1st of each month): fetch entries from `state.json` last_run minus 60 days,
  run `refresh.py` with OurAirports' airports.csv, push to main.
- Start clean: pass every logbook page with `--full`.
- The repo is public: no flight dates are stored here, only first-visit years, flight counts and
  entry IDs already counted.
- `make_basemap.mjs` regenerates `geo.json` (npm world-atlas@2, us-atlas@3, topojson-client@3, d3-geo@3).
