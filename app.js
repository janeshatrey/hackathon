const USGS = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson';
const EONET = 'https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=60';
const COLORS = ['var(--s0)', 'var(--s1)', 'var(--s2)', 'var(--s3)'];
const LABELS = ['Low', 'Moderate', 'High', 'Critical'];

// Offline fallback so the dashboard still renders when feeds are unreachable.
const SAMPLE = [
  { id: 's1', type: 'earthquake', title: 'M 6.1 - Sample: Pacific coast', lat: 38.3, lon: 142.4, sev: 2, time: Date.now() - 36e5 },
  { id: 's2', type: 'wildfire', title: 'Sample wildfire - California', lat: 39.7, lon: -121.6, sev: 2, time: Date.now() - 5e6 },
  { id: 's3', type: 'storm', title: 'Sample cyclone - Bay of Bengal', lat: 15.2, lon: 88.4, sev: 3, time: Date.now() - 9e6 },
  { id: 's4', type: 'volcano', title: 'Sample eruption - Iceland', lat: 63.9, lon: -22.3, sev: 1, time: Date.now() - 2e7 },
  { id: 's5', type: 'flood', title: 'Sample flooding - Bangladesh', lat: 23.8, lon: 90.4, sev: 1, time: Date.now() - 4e7 },
];

let events = [];
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const quakeSev = m => (m >= 7 ? 3 : m >= 6 ? 2 : m >= 4.5 ? 1 : 0);
function eonetType(cats) {
  const id = (cats[0] && cats[0].id) || '';
  if (id === 'wildfires') return 'wildfire';
  if (id === 'severeStorms') return 'storm';
  if (id === 'volcanoes') return 'volcano';
  if (id === 'floods') return 'flood';
  return 'other';
}

async function getJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(url + ' ' + r.status);
  return r.json();
}

async function load() {
  $('status').textContent = 'Loading…';
  const [q, e] = await Promise.allSettled([getJSON(USGS), getJSON(EONET)]);
  const out = [];
  const errors = [];
  if (q.status === 'fulfilled') {
    for (const f of q.value.features) {
      const [lon, lat] = f.geometry.coordinates;
      out.push({ id: f.id, type: 'earthquake', title: f.properties.title, lat, lon, sev: quakeSev(f.properties.mag || 0), time: f.properties.time });
    }
  } else errors.push('USGS');
  if (e.status === 'fulfilled') {
    for (const ev of e.value.events) {
      const g = ev.geometry[ev.geometry.length - 1];
      if (!g || g.type !== 'Point') continue;
      const type = eonetType(ev.categories);
      out.push({ id: ev.id, type, title: ev.title, lat: g.coordinates[1], lon: g.coordinates[0], sev: type === 'storm' ? 2 : 1, time: Date.parse(g.date) });
    }
  } else errors.push('NASA EONET');
  if (errors.length === 2) {
    events = SAMPLE;
    $('status').textContent = 'Live feeds unreachable — showing sample data.';
  } else {
    events = out;
    $('status').textContent = 'Updated ' + new Date().toLocaleTimeString() + (errors.length ? ' (failed: ' + errors.join(', ') + ')' : '') + ' · Sources: USGS, NASA EONET';
  }
  render();
}

function filtered() {
  const t = $('type').value, s = +$('sev').value;
  return events.filter(e => (t === 'all' || e.type === t) && e.sev >= s).sort((a, b) => b.sev - a.sev || b.time - a.time);
}

function render() {
  const list = filtered();
  $('count').textContent = '(' + list.length + ')';
  $('stats').innerHTML = [
    ['Total', list.length],
    ...LABELS.map((l, i) => [l, list.filter(e => e.sev === i).length]),
  ].map(([l, n]) => `<div class="stat"><b>${n}</b><span>${l}</span></div>`).join('');

  $('list').innerHTML = list.slice(0, 200).map(e =>
    `<li><span class="dot" style="background:${COLORS[e.sev]}"></span><div>${esc(e.title)}<div class="meta">${e.type} · ${LABELS[e.sev]} · ${new Date(e.time).toLocaleString()}</div></div></li>`
  ).join('') || '<li>No events match.</li>';

  const W = 360, H = 180;
  const pts = list.map(e => {
    const x = (e.lon + 180) / 360 * W, y = (90 - e.lat) / 180 * H;
    return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${2 + e.sev}" fill="${COLORS[e.sev]}" fill-opacity=".75"><title>${esc(e.title)}</title></circle>`;
  }).join('');
  let grid = '';
  for (let lon = -180; lon <= 180; lon += 30) grid += `<line x1="${(lon + 180) / 360 * W}" y1="0" x2="${(lon + 180) / 360 * W}" y2="${H}"/>`;
  for (let lat = -90; lat <= 90; lat += 30) grid += `<line x1="0" y1="${(90 - lat) / 180 * H}" x2="${W}" y2="${(90 - lat) / 180 * H}"/>`;
  $('map').innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Event map"><g stroke="currentColor" stroke-opacity=".15" stroke-width=".3">${grid}</g>${pts}</svg>`;
}

$('type').onchange = $('sev').onchange = render;
$('refresh').onclick = load;
load();
setInterval(load, 5 * 60 * 1000);
