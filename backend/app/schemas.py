from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# --- Store Schemas ---
class StoreResponse(BaseModel):
    store_id: int
    name: str
    address: Optional[str] = None
    width: int
    height: int

    class Config:
        from_attributes = True


# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str
    category: str
    brand: Optional[str] = None
    price: float
    stock: int
    rack_id: str
    image_url: Optional[str] = None


class ProductResponse(ProductBase):
    product_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Rack Schemas ---
class RackBase(BaseModel):
    rack_id: str
    rack_label: str
    x_pos: int
    y_pos: int
    width: int
    height: int


class RackResponse(RackBase):
    store_id: int

    class Config:
        from_attributes = True


# --- Nav Node Schema (entrance / checkout / waypoint markers for the map) ---
class NavNodeResponse(BaseModel):
    node_id: str
    x_pos: int
    y_pos: int
    node_type: str

    class Config:
        from_attributes = True


# --- Route Schemas ---
class RouteRequest(BaseModel):
    store_id: int = 1
    start_node: str = "ENTRANCE"
    end_node: str = "CHECKOUT"
    product_ids: List[int]
    avoid_crowds: bool = False


class RouteNodeInfo(BaseModel):
    node_id: str
    x_pos: int
    y_pos: int
    node_type: str
    stop_name: Optional[str] = None


class RouteResponse(BaseModel):
    success: bool
    total_distance: float
    naive_distance: float = 0.0
    estimated_time_seconds: int
    path_nodes: List[RouteNodeInfo]
    visiting_sequence: List[str]
    congested_racks_avoided: List[str] = []


# --- Crowd / congestion schemas ---
class CongestionItem(BaseModel):
    rack_id: str
    level: float          # 0.0 (empty) - 1.0 (packed)
    label: str            # Low / Moderate / High


class CongestionResponse(BaseModel):
    updated_in_seconds: int
    racks: List[CongestionItem]


# --- Analytics schemas (store-manager dashboard) ---
class RackHeat(BaseModel):
    rack_id: str
    rack_label: str
    visits: int


class TopProduct(BaseModel):
    product_id: int
    name: str
    requests: int


class AnalyticsSummary(BaseModel):
    total_routes: int
    total_distance_saved_m: float
    avg_savings_pct: float
    avg_items_per_trip: float
    rack_heatmap: List[RackHeat]
    top_products: List[TopProduct]
    routes_with_crowd_avoidance: int
