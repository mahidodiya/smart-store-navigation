"""
Auto-seeding for first boot.

Render (and most free Postgres hosts) hand you an *empty* database - there's
no way to run schema.sql by hand unless you open a shell. So on startup we
create the tables (via SQLAlchemy) and, if the `stores` table is empty,
populate it with the same demo dataset that ships in schema.sql. This makes
`git push` -> live demo work with zero manual DB steps.
"""

from sqlalchemy.orm import Session
from .models import Store, Rack, Product, NavNode, NavEdge


def seed_if_empty(db: Session) -> None:
    if db.query(Store).count() > 0:
        return  # Already seeded (or an admin has real data) - never overwrite.

    store = Store(store_id=1, name="SuperMart Express", address="123 Main Street", width=800, height=600)
    db.add(store)
    db.flush()

    racks_data = [
        ("A1", "Rack A1 - Breakfast & Oats", 150, 120, 100, 40),
        ("A2", "Rack A2 - Instant Noodles & Pasta", 350, 120, 100, 40),
        ("A3", "Rack A3 - Rice, Dal & Pulses", 550, 120, 100, 40),
        ("B1", "Rack B1 - Spices, Salt & Sugar", 150, 240, 100, 40),
        ("B2", "Rack B2 - Cooking Oil & Ghee", 350, 240, 100, 40),
        ("B3", "Rack B3 - Tea & Coffee", 550, 240, 100, 40),
        ("C1", "Rack C1 - Biscuits & Bakery", 150, 360, 100, 40),
        ("C2", "Rack C2 - Dairy & Cold Milk", 350, 360, 100, 40),
        ("C3", "Rack C3 - Snacks & Chips", 550, 360, 100, 40),
        ("D1", "Rack D1 - Soaps & Body Wash", 150, 480, 100, 40),
        ("D2", "Rack D2 - Detergents & Laundry", 350, 480, 100, 40),
        ("D3", "Rack D3 - Oral Care & Hygiene", 550, 480, 100, 40),
    ]
    for rack_id, label, x, y, w, h in racks_data:
        db.add(Rack(rack_id=rack_id, store_id=1, rack_label=label, x_pos=x, y_pos=y, width=w, height=h))
    db.flush()

    # Unique products only. image_url points to a clear photo of that product type.
    products_data = [
        # Dairy
        ("Amul Fresh Milk 500ml", "Dairy", "Amul", 30.00, 50, "C2",
         "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80"),
        ("Mother Dairy Toned Milk 1L", "Dairy", "Mother Dairy", 56.00, 40, "C2",
         "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80"),
        # Snacks
        ("Maggi 2-Minute Noodles 280g", "Snacks", "Nestle", 48.00, 120, "A2",
         "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=400&q=80"),
        ("Parle-G Glucose Biscuits 250g", "Snacks", "Parle", 25.00, 150, "C1",
         "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&q=80"),
        ("Lay's Classic Salted Chips 52g", "Snacks", "Lay's", 20.00, 100, "C3",
         "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400&q=80"),
        ("Britannia Good Day Cookies 200g", "Snacks", "Britannia", 30.00, 80, "C1",
         "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400&q=80"),
        # Grocery
        ("Tata Salt Vacuum Evaporated 1kg", "Grocery", "Tata", 28.00, 90, "B1",
         "https://images.unsplash.com/photo-1606914501449-5a96b8ce73d1?w=400&q=80"),
        ("Fortune Sunlite Sunflower Oil 1L", "Grocery", "Fortune", 135.00, 45, "B2",
         "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&q=80"),
        ("Aashirvaad Whole Wheat Atta 5kg", "Grocery", "Aashirvaad", 240.00, 55, "A3",
         "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&q=80"),
        ("Quaker Oats 1kg", "Grocery", "Quaker", 190.00, 30, "A1",
         "https://images.unsplash.com/photo-1517673400267-0251440c45dc?w=400&q=80"),
        ("Brooke Bond Red Label Tea 500g", "Grocery", "Red Label", 260.00, 40, "B3",
         "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=400&q=80"),
        ("Nescafe Classic Instant Coffee 100g", "Grocery", "Nescafe", 320.00, 25, "B3",
         "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400&q=80"),
        # Household
        ("Surf Excel Easy Wash Detergent 1kg", "Household", "Surf Excel", 140.00, 35, "D2",
         "https://images.unsplash.com/photo-1610557892470-55d9e80c0bce?w=400&q=80"),
        ("Dettol Original Soap 125g", "Household", "Dettol", 45.00, 70, "D1",
         "https://images.unsplash.com/photo-1584305574647-0cc949a2bb9f?w=400&q=80"),
        ("Colgate Strong Teeth Toothpaste 150g", "Household", "Colgate", 95.00, 60, "D3",
         "https://images.unsplash.com/photo-1622383563227-04401dc3e7e1?w=400&q=80"),
    ]
    for name, category, brand, price, stock, rack_id, image_url in products_data:
        db.add(Product(name=name, category=category, brand=brand, price=price,
                        stock=stock, rack_id=rack_id, image_url=image_url))

    nodes_data = [
        ("ENTRANCE", 400, 560, "ENTRANCE"),
        ("CHECKOUT", 680, 560, "CHECKOUT"),
        ("NODE_A1", 150, 80, "RACK_ACCESS"),
        ("NODE_A2", 350, 80, "RACK_ACCESS"),
        ("NODE_A3", 550, 80, "RACK_ACCESS"),
        ("NODE_B1", 150, 200, "RACK_ACCESS"),
        ("NODE_B2", 350, 200, "RACK_ACCESS"),
        ("NODE_B3", 550, 200, "RACK_ACCESS"),
        ("NODE_C1", 150, 320, "RACK_ACCESS"),
        ("NODE_C2", 350, 320, "RACK_ACCESS"),
        ("NODE_C3", 550, 320, "RACK_ACCESS"),
        ("NODE_D1", 150, 440, "RACK_ACCESS"),
        ("NODE_D2", 350, 440, "RACK_ACCESS"),
        ("NODE_D3", 550, 440, "RACK_ACCESS"),
        ("MAIN_AISLE_BOTTOM", 400, 500, "WAYPOINT"),
    ]
    for node_id, x, y, ntype in nodes_data:
        db.add(NavNode(node_id=node_id, store_id=1, x_pos=x, y_pos=y, node_type=ntype))
    db.flush()

    edges_data = [
        ("ENTRANCE", "MAIN_AISLE_BOTTOM", 60),
        ("MAIN_AISLE_BOTTOM", "NODE_D2", 60),
        ("MAIN_AISLE_BOTTOM", "CHECKOUT", 280),
        ("NODE_D1", "NODE_D2", 200),
        ("NODE_D2", "NODE_D3", 200),
        ("NODE_D1", "NODE_C1", 120),
        ("NODE_D2", "NODE_C2", 120),
        ("NODE_D3", "NODE_C3", 120),
        ("NODE_C1", "NODE_C2", 200),
        ("NODE_C2", "NODE_C3", 200),
        ("NODE_C1", "NODE_B1", 120),
        ("NODE_C2", "NODE_B2", 120),
        ("NODE_C3", "NODE_B3", 120),
        ("NODE_B1", "NODE_B2", 200),
        ("NODE_B2", "NODE_B3", 200),
        ("NODE_B1", "NODE_A1", 120),
        ("NODE_B2", "NODE_A2", 120),
        ("NODE_B3", "NODE_A3", 120),
        ("NODE_A1", "NODE_A2", 200),
        ("NODE_A2", "NODE_A3", 200),
        ("NODE_D3", "CHECKOUT", 170),
    ]
    for from_n, to_n, dist in edges_data:
        db.add(NavEdge(store_id=1, from_node=from_n, to_node=to_n, distance=dist))
        db.add(NavEdge(store_id=1, from_node=to_n, to_node=from_n, distance=dist))

    db.commit()
