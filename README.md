# Disaster Dashboard

A real-time, browser-based dashboard that aggregates global disaster events (earthquakes, wildfires, severe storms, volcanoes, floods) from public data feeds onto one map, list and severity summary.

**Live prototype:** `https://janeshatrey.github.io/hackathon/` (GitHub Pages — no local install needed)
**Written explanation:** [docs/EXPLANATION.md](docs/EXPLANATION.md)

## Feature list
- Live earthquake data from the USGS GeoJSON feed (last 24 h, M2.5+)
- Live natural-event data (wildfires, storms, volcanoes, floods) from NASA EONET
- Severity classification (Low / Moderate / High / Critical) with colour coding
- Filter by event type and minimum severity
- Summary counters, world map (SVG) and a sortable-by-severity event list
- Auto-refresh every 5 minutes plus manual Refresh
- Graceful fallback to sample data if the feeds are unreachable
- Responsive layout, light/dark theme

## Technology stack
- Plain HTML, CSS and vanilla JavaScript (no build step, no dependencies)
- Data: USGS Earthquake Hazards API, NASA EONET v3 (both free, keyless, CORS-enabled)
- Hosting: GitHub Pages, deployed by GitHub Actions (`.github/workflows/pages.yml`)

## Setup instructions
```bash
git clone https://github.com/janeshatrey/hackathon.git
cd hackathon
cp .env.example .env     # optional – see below
python3 -m http.server 8080
# open http://localhost:8080
```
Any static file server works. Opening `index.html` directly may be blocked by browser fetch rules, so use a server.

## Environment variables
The current prototype uses only keyless public APIs, so **no variables are required**. `.env.example` lists placeholders for planned integrations (see roadmap); do not commit real secrets.

## Deployment
Push to `main` — the workflow publishes the repo root to GitHub Pages. One-time: Settings → Pages → Source: **GitHub Actions**.

## Project structure
```
index.html   page layout
styles.css   styling
app.js       data fetching, normalisation, filtering, rendering
docs/        written explanation
```

## Roadmap
See [docs/EXPLANATION.md](docs/EXPLANATION.md#future-roadmap).
