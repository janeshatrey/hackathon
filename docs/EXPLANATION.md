# Disaster Dashboard – Written Explanation

## Problem
When a disaster strikes, information is scattered across agency websites (seismology, fire, weather, volcano services), each with its own format. Responders, journalists, NGOs and ordinary people lose time stitching together a picture of "what is happening right now, and how bad is it?".

## Target users
- Emergency coordinators and NGO relief teams who need quick situational awareness
- Journalists and researchers tracking ongoing events
- Citizens and travellers checking for nearby hazards

## Solution
A single, zero-install web dashboard that pulls live data from authoritative public feeds (USGS, NASA EONET), normalises it into one event model (type, location, severity, time) and presents it as summary counters, a world map and a prioritised event list with filters.

## Implemented features
- Live USGS earthquakes and NASA EONET wildfires, storms, volcanoes, floods
- Unified severity model (earthquakes by magnitude; other events by category)
- Filtering by type and minimum severity; counters update with filters
- Interactive map with hover details; event list ordered by severity then recency
- Auto-refresh (5 min) and manual refresh; partial-failure reporting per source
- Offline/blocked-network fallback to sample data, clearly labelled
- Escaped output to avoid injection from feed text; responsive, theme-aware UI

## Architecture
Static front end. `app.js` fetches both feeds in parallel (`Promise.allSettled`, so one failing source does not break the other), maps them to a common event shape, then filters and renders. No backend, so it is cheap to host and always reflects live data.

## Future roadmap
1. Tile-based interactive map (Leaflet/MapLibre) with clustering and zoom
2. "Near me" alerts using geolocation and configurable radius
3. Additional sources: weather alerts, floods (GDACS), air quality
4. Push/webhook/email notifications for new critical events
5. Historical timeline and trend charts
6. Multilingual UI and accessibility audit
7. Optional backend cache to add rate-limit protection and shared state
