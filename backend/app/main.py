import os
from collections import Counter
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import engine, get_db, Base, SessionLocal
from .models import Product, Rack, Store, NavNode, RouteLog
from .schemas import (
    ProductResponse, RackResponse, RouteRequest, RouteResponse, StoreResponse, NavNodeResponse,
    CongestionResponse, CongestionItem, AnalyticsSummary, RackHeat, TopProduct
)
from .navigation import calculate_optimal_route, get_crowd_levels, crowd_label, seconds_until_next_crowd_refresh
from .seed import seed_if_empty

# Create database tables automatically if they don't exist
Base.metadata.create_all(bind=engine)

# Seed demo data on first boot (safe no-op if data already exists)
try:
    _db = SessionLocal()
    seed_if_empty(_db)
finally:
    _db.close()

app = FastAPI(
    title="Smart Store Navigation API",
    description="Backend API for managing store products, rack mappings, and graph-based route optimization.",
    version="2.0.0"
)

# Enable CORS (the frontend is served from the same origin in production,
# but this keeps local development - opening frontend/index.html directly - working too)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))


@app.get("/api/health")
def health_check():
    return {"status": "online", "message": "Smart Store Navigation API is healthy."}


# --- STORE ENDPOINTS ---

@app.get("/api/store", response_model=StoreResponse)
def get_default_store(db: Session = Depends(get_db)):
    """Fetch the active store's metadata (used to size the map on the frontend)."""
    store = db.query(Store).filter(Store.store_id == 1).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not configured.")
    return store


# --- PRODUCT ENDPOINTS ---

@app.get("/api/products/available", response_model=List[ProductResponse])
def get_available_products(db: Session = Depends(get_db)):
    """Fetch all available products in stock (deduped by name)."""
    rows = db.query(Product).filter(Product.stock > 0).order_by(Product.category, Product.name).all()
    seen = set()
    unique = []
    for p in rows:
        key = (p.name or "").strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


@app.get("/api/products/search", response_model=List[ProductResponse])
def search_products(
    q: Optional[str] = Query(None, description="Search term for product name, brand or category"),
    db: Session = Depends(get_db)
):
    """Search products by keyword."""
    if not q:
        return db.query(Product).all()

    search_pattern = f"%{q}%"
    results = db.query(Product).filter(
        (Product.name.ilike(search_pattern)) |
        (Product.category.ilike(search_pattern)) |
        (Product.brand.ilike(search_pattern))
    ).all()
    return results


@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """Fetch details of a single product."""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# --- RACK & STORE ENDPOINTS ---

@app.get("/api/racks", response_model=List[RackResponse])
def get_all_racks(db: Session = Depends(get_db)):
    """Fetch all store racks."""
    return db.query(Rack).all()


@app.get("/api/nav-nodes", response_model=List[NavNodeResponse])
def get_nav_nodes(store_id: int = 1, db: Session = Depends(get_db)):
    """Fetch entrance / checkout / waypoint markers so the frontend map
    never has to hardcode coordinates."""
    return db.query(NavNode).filter(NavNode.store_id == store_id).all()


# --- CROWD / CONGESTION ENDPOINT ---

@app.get("/api/crowd", response_model=CongestionResponse)
def get_crowd(store_id: int = 1, db: Session = Depends(get_db)):
    """Simulated live footfall per rack, used to draw the crowd-density overlay
    on the map and to power 'avoid busy aisles' routing."""
    rack_ids = [r.rack_id for r in db.query(Rack).filter(Rack.store_id == store_id).all()]
    levels = get_crowd_levels(rack_ids)
    return {
        "updated_in_seconds": seconds_until_next_crowd_refresh(),
        "racks": [
            {"rack_id": rid, "level": level, "label": crowd_label(level)}
            for rid, level in levels.items()
        ],
    }


# --- ROUTE GENERATION ENDPOINT ---

@app.post("/api/route", response_model=RouteResponse)
def generate_route(payload: RouteRequest, db: Session = Depends(get_db)):
    """Calculate the shortest optimized visiting route for a list of products
    using A* pathfinding plus a Nearest-Neighbor + 2-opt TSP heuristic."""
    if not payload.product_ids:
        raise HTTPException(status_code=400, detail="Shopping list cannot be empty.")

    route_data = calculate_optimal_route(
        db=db,
        store_id=payload.store_id,
        start_node=payload.start_node,
        end_node=payload.end_node,
        product_ids=payload.product_ids,
        avoid_crowds=payload.avoid_crowds
    )

    if not route_data.get("success"):
        raise HTTPException(status_code=422, detail="Could not compute a route for the given nodes.")

    # Best-effort analytics logging - never let this break the shopper's request.
    try:
        rack_ids = []
        for rid in route_data["visiting_sequence"]:
            if rid.startswith("NODE_"):
                rack_ids.append(rid.replace("NODE_", ""))
        db.add(RouteLog(
            store_id=payload.store_id,
            product_ids=",".join(str(p) for p in payload.product_ids),
            rack_ids=",".join(rack_ids),
            total_distance=route_data["total_distance"],
            naive_distance=route_data.get("naive_distance", 0.0),
            estimated_time_seconds=route_data["estimated_time_seconds"],
            avoid_crowds=1 if payload.avoid_crowds else 0,
        ))
        db.commit()
    except Exception:
        db.rollback()

    return route_data


# --- ANALYTICS ENDPOINT (store-manager dashboard) ---

@app.get("/api/analytics/summary", response_model=AnalyticsSummary)
def get_analytics_summary(store_id: int = 1, db: Session = Depends(get_db)):
    """Aggregates logged routes into the numbers the store-manager dashboard
    shows: popular racks (heatmap), top requested products, and how much
    walking distance the optimizer has saved shoppers overall."""
    logs = db.query(RouteLog).filter(RouteLog.store_id == store_id).all()

    if not logs:
        return {
            "total_routes": 0,
            "total_distance_saved_m": 0.0,
            "avg_savings_pct": 0.0,
            "avg_items_per_trip": 0.0,
            "rack_heatmap": [],
            "top_products": [],
            "routes_with_crowd_avoidance": 0,
        }

    rack_counter = Counter()
    product_counter = Counter()
    total_saved = 0.0
    savings_pcts = []
    total_items = 0
    crowd_routes = 0

    for log in logs:
        rack_ids = [r for r in log.rack_ids.split(",") if r]
        rack_counter.update(rack_ids)

        product_ids = [int(p) for p in log.product_ids.split(",") if p]
        product_counter.update(product_ids)
        total_items += len(product_ids)

        saved = max(0.0, (log.naive_distance or 0.0) - log.total_distance)
        total_saved += saved
        if log.naive_distance and log.naive_distance > 0:
            savings_pcts.append(saved / log.naive_distance * 100)

        if log.avoid_crowds:
            crowd_routes += 1

    racks = {r.rack_id: r for r in db.query(Rack).filter(Rack.store_id == store_id).all()}
    rack_heatmap = [
        RackHeat(rack_id=rid, rack_label=racks[rid].rack_label if rid in racks else rid, visits=count)
        for rid, count in rack_counter.most_common(12)
    ]

    top_product_ids = [pid for pid, _ in product_counter.most_common(8)]
    products = {p.product_id: p for p in db.query(Product).filter(Product.product_id.in_(top_product_ids)).all()}
    top_products = [
        TopProduct(product_id=pid, name=products[pid].name if pid in products else f"Product {pid}", requests=count)
        for pid, count in product_counter.most_common(8)
    ]

    return {
        "total_routes": len(logs),
        "total_distance_saved_m": round(total_saved, 1),
        "avg_savings_pct": round(sum(savings_pcts) / len(savings_pcts), 1) if savings_pcts else 0.0,
        "avg_items_per_trip": round(total_items / len(logs), 1),
        "rack_heatmap": rack_heatmap,
        "top_products": top_products,
        "routes_with_crowd_avoidance": crowd_routes,
    }


# --- FRONTEND STATIC FILE SERVING ---
# Mounted last so it never shadows the /api/* routes above. html=True lets it
# serve index.html at "/" and every other page (shop.html, navigate.html,
# dashboard.html) at its own path automatically.
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
