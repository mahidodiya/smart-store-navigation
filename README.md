# SmartStore Navigation

Indoor store navigation web app. Shoppers pick products from a catalog and
get the shortest walking route through the store, shown on an interactive
floor-plan map. It combines a product-selection/cart flow, A*-based route
optimization with crowd-aware rerouting, a live budget tracker, voice
search, Hindi/English support, and a store-manager analytics dashboard.

## Why it helps

In a large store you usually know *what* you want but not *where* it is or
the fastest order to collect it all. This app solves that instead of just
showing a map:

- **Products are tagged with a rack location**, so a shopper always knows
  where an item lives.
- **The route engine plans the whole trip, not just one item** — A*
  pathfinding models the store as a graph, and Nearest-Neighbor + 2-opt
  decide the best *order* to visit every selected rack in, so the shopper
  walks the shortest total path instead of crisscrossing the store.
- **Crowd-aware rerouting** avoids congested aisles when possible, cutting
  down time lost waiting in busy spots.
- **The budget tracker** shows a running total against a set limit while
  items are added, so there are no checkout surprises.

## Project structure

```
backend/
  app/
    main.py           FastAPI app + routes (products, racks, route, crowd, analytics)
    models.py         SQLAlchemy models
    schemas.py         Pydantic request/response models
    navigation.py       Route engine (A*, Nearest-Neighbor, 2-opt) + crowd simulation
    seed.py               First-boot demo data seeding
    database.py           DB engine/session setup
  requirements.txt
  .env                     Local-only DB config
frontend/
  index.html                Landing page
  shop.html                 Product selection, cart, budget tracker, voice search
  navigate.html              Map, turn-by-turn directions, crowd overlay
  dashboard.html              Store-manager analytics (heatmap, top products)
  assets/
    common.css                 Shared design tokens & components
    i18n.js                    English/Hindi translation dictionary + toggle
    store-data.js               Shared rack layout + cart/budget persistence
schema.sql                Reference DB schema/seed
render.yaml                Render Blueprint (web service + Postgres)
```
