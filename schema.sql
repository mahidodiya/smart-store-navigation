-- 1. STORES TABLE
CREATE TABLE IF NOT EXISTS stores (
    store_id SERIAL PRIMARY KEY,
    name VARCHAR(250) NOT NULL,
    address TEXT,
    width INT DEFAULT 800,
    height INT DEFAULT 600,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. RACKS TABLE
CREATE TABLE IF NOT EXISTS racks (
    rack_id VARCHAR(50) PRIMARY KEY,
    store_id INT NOT NULL REFERENCES stores(store_id) ON DELETE CASCADE,
    rack_label VARCHAR(100) NOT NULL,
    x_pos INT NOT NULL,
    y_pos INT NOT NULL,
    width INT DEFAULT 60,
    height INT DEFAULT 40
);

-- 3. PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    price NUMERIC(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    rack_id VARCHAR(50) NOT NULL REFERENCES racks(rack_id) ON DELETE CASCADE,
    image_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. NAVIGATION NODES TABLE
CREATE TABLE IF NOT EXISTS nav_nodes (
    node_id VARCHAR(50) PRIMARY KEY,
    store_id INT NOT NULL REFERENCES stores(store_id) ON DELETE CASCADE,
    x_pos INT NOT NULL,
    y_pos INT NOT NULL,
    node_type VARCHAR(20) CHECK (node_type IN ('ENTRANCE', 'CHECKOUT', 'WAYPOINT', 'RACK_ACCESS')) DEFAULT 'WAYPOINT'
);

-- 5. NAVIGATION EDGES TABLE
CREATE TABLE IF NOT EXISTS nav_edges (
    edge_id SERIAL PRIMARY KEY,
    store_id INT NOT NULL REFERENCES stores(store_id) ON DELETE CASCADE,
    from_node VARCHAR(50) NOT NULL REFERENCES nav_nodes(node_id) ON DELETE CASCADE,
    to_node VARCHAR(50) NOT NULL REFERENCES nav_nodes(node_id) ON DELETE CASCADE,
    distance FLOAT NOT NULL
);

-- 6. ROUTE LOGS TABLE (powers the store-manager analytics dashboard)
CREATE TABLE IF NOT EXISTS route_logs (
    log_id SERIAL PRIMARY KEY,
    store_id INT NOT NULL REFERENCES stores(store_id) ON DELETE CASCADE,
    product_ids TEXT NOT NULL,
    rack_ids TEXT NOT NULL,
    total_distance FLOAT NOT NULL,
    naive_distance FLOAT NOT NULL DEFAULT 0,
    estimated_time_seconds INT NOT NULL DEFAULT 0,
    avoid_crowds INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- ========================================================
-- SEED DATA
-- ========================================================

-- Insert Store
INSERT INTO stores (store_id, name, address, width, height) 
VALUES (1, 'SuperMart Express', '123 Main Street', 800, 600)
ON CONFLICT (store_id) DO UPDATE SET name = EXCLUDED.name;

-- Insert Racks
INSERT INTO racks (rack_id, store_id, rack_label, x_pos, y_pos, width, height) VALUES
('A1', 1, 'Rack A1 - Breakfast & Oats', 150, 120, 100, 40),
('A2', 1, 'Rack A2 - Instant Noodles & Pasta', 350, 120, 100, 40),
('A3', 1, 'Rack A3 - Rice, Dal & Pulses', 550, 120, 100, 40),
('B1', 1, 'Rack B1 - Spices, Salt & Sugar', 150, 240, 100, 40),
('B2', 1, 'Rack B2 - Cooking Oil & Ghee', 350, 240, 100, 40),
('B3', 1, 'Rack B3 - Tea & Coffee', 550, 240, 100, 40),
('C1', 1, 'Rack C1 - Biscuits & Bakery', 150, 360, 100, 40),
('C2', 1, 'Rack C2 - Dairy & Cold Milk', 350, 360, 100, 40),
('C3', 1, 'Rack C3 - Snacks & Chips', 550, 360, 100, 40),
('D1', 1, 'Rack D1 - Soaps & Body Wash', 150, 480, 100, 40),
('D2', 1, 'Rack D2 - Detergents & Laundry', 350, 480, 100, 40),
('D3', 1, 'Rack D3 - Oral Care & Hygiene', 550, 480, 100, 40)
ON CONFLICT (rack_id) DO NOTHING;

-- Insert Products (unique set; matches seed.py)
INSERT INTO products (name, category, brand, price, stock, rack_id, image_url) VALUES
('Amul Fresh Milk 500ml', 'Dairy', 'Amul', 30.00, 50, 'C2', 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80'),
('Mother Dairy Toned Milk 1L', 'Dairy', 'Mother Dairy', 56.00, 40, 'C2', 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),
('Maggi 2-Minute Noodles 280g', 'Snacks', 'Nestle', 48.00, 120, 'A2', 'https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=400&q=80'),
('Parle-G Glucose Biscuits 250g', 'Snacks', 'Parle', 25.00, 150, 'C1', 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&q=80'),
('Lay''s Classic Salted Chips 52g', 'Snacks', 'Lay''s', 20.00, 100, 'C3', 'https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400&q=80'),
('Britannia Good Day Cookies 200g', 'Snacks', 'Britannia', 30.00, 80, 'C1', 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400&q=80'),
('Tata Salt Vacuum Evaporated 1kg', 'Grocery', 'Tata', 28.00, 90, 'B1', 'https://images.unsplash.com/photo-1606914501449-5a96b8ce73d1?w=400&q=80'),
('Fortune Sunlite Sunflower Oil 1L', 'Grocery', 'Fortune', 135.00, 45, 'B2', 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&q=80'),
('Aashirvaad Whole Wheat Atta 5kg', 'Grocery', 'Aashirvaad', 240.00, 55, 'A3', 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&q=80'),
('Quaker Oats 1kg', 'Grocery', 'Quaker', 190.00, 30, 'A1', 'https://images.unsplash.com/photo-1517673400267-0251440c45dc?w=400&q=80'),
('Brooke Bond Red Label Tea 500g', 'Grocery', 'Red Label', 260.00, 40, 'B3', 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=400&q=80'),
('Nescafe Classic Instant Coffee 100g', 'Grocery', 'Nescafe', 320.00, 25, 'B3', 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400&q=80'),
('Surf Excel Easy Wash Detergent 1kg', 'Household', 'Surf Excel', 140.00, 35, 'D2', 'https://images.unsplash.com/photo-1610557892470-55d9e80c0bce?w=400&q=80'),
('Dettol Original Soap 125g', 'Household', 'Dettol', 45.00, 70, 'D1', 'https://images.unsplash.com/photo-1584305574647-0cc949a2bb9f?w=400&q=80'),
('Colgate Strong Teeth Toothpaste 150g', 'Household', 'Colgate', 95.00, 60, 'D3', 'https://images.unsplash.com/photo-1622383563227-04401dc3e7e1?w=400&q=80');

-- Insert Navigation Nodes
INSERT INTO nav_nodes (node_id, store_id, x_pos, y_pos, node_type) VALUES
('ENTRANCE', 1, 400, 560, 'ENTRANCE'),
('CHECKOUT', 1, 680, 560, 'CHECKOUT'),
('NODE_A1', 1, 150, 80, 'RACK_ACCESS'),
('NODE_A2', 1, 350, 80, 'RACK_ACCESS'),
('NODE_A3', 1, 550, 80, 'RACK_ACCESS'),
('NODE_B1', 1, 150, 200, 'RACK_ACCESS'),
('NODE_B2', 1, 350, 200, 'RACK_ACCESS'),
('NODE_B3', 1, 550, 200, 'RACK_ACCESS'),
('NODE_C1', 1, 150, 320, 'RACK_ACCESS'),
('NODE_C2', 1, 350, 320, 'RACK_ACCESS'),
('NODE_C3', 1, 550, 320, 'RACK_ACCESS'),
('NODE_D1', 1, 150, 440, 'RACK_ACCESS'),
('NODE_D2', 1, 350, 440, 'RACK_ACCESS'),
('NODE_D3', 1, 550, 440, 'RACK_ACCESS'),
('MAIN_AISLE_BOTTOM', 1, 400, 500, 'WAYPOINT')
ON CONFLICT (node_id) DO NOTHING;

-- Insert Navigation Edges
INSERT INTO nav_edges (store_id, from_node, to_node, distance) VALUES
(1, 'ENTRANCE', 'MAIN_AISLE_BOTTOM', 60),
(1, 'MAIN_AISLE_BOTTOM', 'NODE_D2', 60),
(1, 'MAIN_AISLE_BOTTOM', 'CHECKOUT', 280),
(1, 'NODE_D1', 'NODE_D2', 200),
(1, 'NODE_D2', 'NODE_D3', 200),
(1, 'NODE_D1', 'NODE_C1', 120),
(1, 'NODE_D2', 'NODE_C2', 120),
(1, 'NODE_D3', 'NODE_C3', 120),
(1, 'NODE_C1', 'NODE_C2', 200),
(1, 'NODE_C2', 'NODE_C3', 200),
(1, 'NODE_C1', 'NODE_B1', 120),
(1, 'NODE_C2', 'NODE_B2', 120),
(1, 'NODE_C3', 'NODE_B3', 120),
(1, 'NODE_B1', 'NODE_B2', 200),
(1, 'NODE_B2', 'NODE_B3', 200),
(1, 'NODE_B1', 'NODE_A1', 120),
(1, 'NODE_B2', 'NODE_A2', 120),
(1, 'NODE_B3', 'NODE_A3', 120),
(1, 'NODE_A1', 'NODE_A2', 200),
(1, 'NODE_A2', 'NODE_A3', 200),
(1, 'NODE_D3', 'CHECKOUT', 170);