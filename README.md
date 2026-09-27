# SmartStore Nav

Indoor store navigation web app: pick products, and get the shortest walking
route through the store (A* pathfinding + Nearest-Neighbor/2-opt route
optimization), shown live on an interactive floor-plan map — with crowd-aware
routing, a live budget tracker, voice search, Hindi/English support, and a
store-manager analytics dashboard.

## What's new in this version

- **Multi-page flow** — Landing → Shop → Navigate, instead of one crowded page.
  The map now lives on its own dedicated `/navigate.html` page.
- **Crowd-aware routing** — simulated live footfall per rack; toggle "Avoid
  busy aisles" and the A* engine re-routes around congested nodes.
- **Store-manager dashboard** (`/dashboard.html`) — a rack popularity heatmap,
  top-requested products, and aggregate distance/time savings across all
  shoppers, powered by a new `route_logs` table.
- **Budget tracker** — set a spend limit on the shop page and watch a live bar
  as you add items, with an over-budget warning.
- **Voice search** — tap the mic on the shop page's search box (uses the
  browser's Web Speech API).
- **Hindi / English toggle** — every page has an EN/हिं switch in the header.

## Project structure

```
backend/
  app/
    main.py         FastAPI app + routes (products, racks, route, crowd, analytics)
    models.py        SQLAlchemy models (+ RouteLog for analytics)
    schemas.py        Pydantic request/response models
    navigation.py     A* + Nearest-Neighbor + 2-opt route engine + crowd simulation
    seed.py            First-boot demo data seeding
    database.py        DB engine/session setup
  requirements.txt
  .env                 Local-only DB config (not used on Render)
frontend/
  index.html            Landing page
  shop.html             Product selection, cart, budget tracker, voice search
  navigate.html         Map, turn-by-turn directions, crowd overlay, walking sim
  dashboard.html        Store-manager analytics (heatmap, top products)
  assets/
    common.css          Shared design tokens & components
    i18n.js             English/Hindi translation dictionary + toggle
    store-data.js        Shared rack layout + cart/budget persistence (localStorage)
schema.sql             Reference schema/seed (kept for manual psql use too)
render.yaml            Render Blueprint: web service + free Postgres
```

## Running locally

```
cd backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://localhost:8000 — FastAPI serves the whole `frontend/`
directory (every page and the `assets/` folder), so no separate frontend
server or build step is needed.

### New API endpoints

- `GET /api/crowd?store_id=1` — simulated live congestion per rack.
- `POST /api/route` — now accepts `avoid_crowds: true` and logs the trip.
- `GET /api/analytics/summary?store_id=1` — aggregated dashboard data.

The cart, budget limit, and "avoid crowds" preference are kept in the
browser's `localStorage` (key names in `assets/store-data.js`) so they carry
across the Shop → Navigate page transition without needing a backend session.
