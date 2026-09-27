from sqlalchemy import Column, Integer, String, Numeric, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Store(Base):
    __tablename__ = "stores"

    store_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), nullable=False)
    address = Column(Text, nullable=True)
    width = Column(Integer, default=800)
    height = Column(Integer, default=600)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    racks = relationship("Rack", back_populates="store", cascade="all, delete-orphan")
    nav_nodes = relationship("NavNode", back_populates="store", cascade="all, delete-orphan")


class Rack(Base):
    __tablename__ = "racks"

    rack_id = Column(String(50), primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.store_id", ondelete="CASCADE"), nullable=False)
    rack_label = Column(String(100), nullable=False)
    x_pos = Column(Integer, nullable=False)
    y_pos = Column(Integer, nullable=False)
    width = Column(Integer, default=60)
    height = Column(Integer, default=40)

    store = relationship("Store", back_populates="racks")
    products = relationship("Product", back_populates="rack", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    brand = Column(String(100), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0)
    rack_id = Column(String(50), ForeignKey("racks.rack_id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rack = relationship("Rack", back_populates="products")


class NavNode(Base):
    __tablename__ = "nav_nodes"

    node_id = Column(String(50), primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.store_id", ondelete="CASCADE"), nullable=False)
    x_pos = Column(Integer, nullable=False)
    y_pos = Column(Integer, nullable=False)
    node_type = Column(String(20), default="WAYPOINT")

    store = relationship("Store", back_populates="nav_nodes")


class NavEdge(Base):
    __tablename__ = "nav_edges"

    edge_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.store_id", ondelete="CASCADE"), nullable=False)
    from_node = Column(String(50), ForeignKey("nav_nodes.node_id", ondelete="CASCADE"), nullable=False)
    to_node = Column(String(50), ForeignKey("nav_nodes.node_id", ondelete="CASCADE"), nullable=False)
    distance = Column(Float, nullable=False)


class RouteLog(Base):
    """One row per computed route - powers the store-manager analytics dashboard
    (popular racks / heatmap, top requested products, avg distance & time saved)."""
    __tablename__ = "route_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.store_id", ondelete="CASCADE"), nullable=False)
    product_ids = Column(Text, nullable=False)       # comma-separated product_id list
    rack_ids = Column(Text, nullable=False)          # comma-separated rack_id visiting sequence
    total_distance = Column(Float, nullable=False)
    naive_distance = Column(Float, nullable=False, default=0.0)
    estimated_time_seconds = Column(Integer, nullable=False, default=0)
    avoid_crowds = Column(Integer, nullable=False, default=0)  # 0/1 (kept as int for widest DB compatibility)
    created_at = Column(DateTime(timezone=True), server_default=func.now())