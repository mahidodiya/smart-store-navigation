import heapq
import math
import random
import time
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from .models import NavNode, NavEdge, Product, Rack

Path = List[str]

# How often the simulated crowd levels "refresh" - within one window every
# request/rack gets a stable value (so the UI doesn't flicker), then it
# reshuffles like a real footfall sensor feed would.
CROWD_BUCKET_SECONDS = 25


def euclidean_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def get_crowd_levels(rack_ids: List[str]) -> Dict[str, float]:
    """Simulated live footfall per rack (0.0 = empty, 1.0 = packed).

    No real sensor hardware for a hackathon demo, so this derives a stable-but-
    shifting value per rack from the current time bucket - it behaves like a
    live feed (changes every CROWD_BUCKET_SECONDS) without needing external
    infrastructure, and is deterministic for a given bucket so concurrent
    requests agree on the same numbers.
    """
    bucket = int(time.time() // CROWD_BUCKET_SECONDS)
    levels = {}
    for rid in rack_ids:
        rnd = random.Random(f"{rid}-{bucket}")
        levels[rid] = round(rnd.uniform(0.05, 0.95), 2)
    return levels


def crowd_label(level: float) -> str:
    if level < 0.35:
        return "Low"
    if level < 0.7:
        return "Moderate"
    return "High"


def seconds_until_next_crowd_refresh() -> int:
    bucket = time.time() // CROWD_BUCKET_SECONDS
    next_refresh = (bucket + 1) * CROWD_BUCKET_SECONDS
    return max(1, int(next_refresh - time.time()))


def build_graph(db: Session, store_id: int) -> Tuple[Dict[str, NavNode], Dict[str, List[Tuple[str, float]]]]:
    nodes = db.query(NavNode).filter(NavNode.store_id == store_id).all()
    edges = db.query(NavEdge).filter(NavEdge.store_id == store_id).all()

    node_dict = {node.node_id: node for node in nodes}
    graph: Dict[str, List[Tuple[str, float]]] = {node.node_id: [] for node in nodes}

    for edge in edges:
        if edge.from_node in graph and edge.to_node in graph:
            graph[edge.from_node].append((edge.to_node, edge.distance))
            graph[edge.to_node].append((edge.from_node, edge.distance))  # Undirected network

    return node_dict, graph


def a_star_search(
    start_id: str,
    goal_id: str,
    nodes: Dict[str, NavNode],
    graph: Dict[str, List[Tuple[str, float]]],
    node_penalty: Optional[Dict[str, float]] = None
) -> Tuple[Path, float]:
    """Classic A* with a Euclidean-distance heuristic. Returns (node path, total distance).

    node_penalty (optional): rack-congestion multiplier per node_id, e.g. {"NODE_C2": 1.8}.
    When provided, edges touching a busy node cost more, so the search naturally
    routes around crowded aisles instead of through them - real distance walked
    still comes from the plain (unpenalized) edge weights, tracked separately below.
    """
    if start_id not in nodes or goal_id not in nodes:
        return [], 0.0
    if start_id == goal_id:
        return [start_id], 0.0

    goal_node = nodes[goal_id]

    def edge_cost(a: str, b: str, base_weight: float) -> float:
        if not node_penalty:
            return base_weight
        mult = (node_penalty.get(a, 1.0) + node_penalty.get(b, 1.0)) / 2.0
        return base_weight * mult

    open_set: List[Tuple[float, str]] = []
    heapq.heappush(open_set, (0.0, start_id))

    came_from: Dict[str, str] = {}
    g_score = {node_id: float('inf') for node_id in nodes}       # penalized cost (used for search)
    real_dist = {node_id: float('inf') for node_id in nodes}     # true walking distance (used for UI)
    g_score[start_id] = 0.0
    real_dist[start_id] = 0.0

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal_id:
            path = []
            step = current
            while step in came_from:
                path.append(step)
                step = came_from[step]
            path.append(start_id)
            path.reverse()
            return path, real_dist[goal_id]

        for neighbor, weight in graph.get(current, []):
            tentative_g = g_score[current] + edge_cost(current, neighbor, weight)
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                real_dist[neighbor] = real_dist[current] + weight
                h = euclidean_distance(nodes[neighbor].x_pos, nodes[neighbor].y_pos, goal_node.x_pos, goal_node.y_pos)
                heapq.heappush(open_set, (tentative_g + h, neighbor))

    return [], 0.0  # No route found (disconnected graph)


def build_distance_matrix(
    nodes: Dict[str, NavNode],
    graph: Dict[str, List[Tuple[str, float]]],
    node_list: List[str],
    node_penalty: Optional[Dict[str, float]] = None
) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], Path]]:
    """Runs A* between every pair of stops (a small set) so the TSP step below is cheap."""
    matrix: Dict[Tuple[str, str], float] = {}
    paths: Dict[Tuple[str, str], Path] = {}
    for src in node_list:
        for dst in node_list:
            if src == dst:
                matrix[(src, dst)] = 0.0
                paths[(src, dst)] = [src]
                continue
            path, dist = a_star_search(src, dst, nodes, graph, node_penalty)
            matrix[(src, dst)] = dist if path else float('inf')
            paths[(src, dst)] = path
    return matrix, paths


def _tour_length(start: str, order: List[str], end: str, matrix: Dict[Tuple[str, str], float]) -> float:
    total = 0.0
    prev = start
    for node in order:
        total += matrix[(prev, node)]
        prev = node
    total += matrix[(prev, end)]
    return total


def _nearest_neighbor_order(start: str, targets: List[str], matrix: Dict[Tuple[str, str], float]) -> List[str]:
    unvisited = targets.copy()
    order: List[str] = []
    current = start
    while unvisited:
        nxt = min(unvisited, key=lambda t: matrix[(current, t)])
        order.append(nxt)
        unvisited.remove(nxt)
        current = nxt
    return order


def _two_opt(start: str, order: List[str], end: str, matrix: Dict[Tuple[str, str], float]) -> List[str]:
    """Local-search refinement: repeatedly reverse a segment of the visiting order
    whenever doing so shortens the total tour. Standard 2-opt for a small TSP instance -
    cleans up the crossed-over legs that greedy Nearest-Neighbor tends to produce."""
    best = order[:]
    if len(best) < 2:
        return best

    best_len = _tour_length(start, best, end, matrix)
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                candidate = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                cand_len = _tour_length(start, candidate, end, matrix)
                if cand_len < best_len - 1e-9:
                    best, best_len = candidate, cand_len
                    improved = True
    return best


def calculate_optimal_route(
    db: Session,
    store_id: int,
    start_node: str,
    end_node: str,
    product_ids: List[int],
    avoid_crowds: bool = False
) -> Dict:
    nodes, graph = build_graph(db, store_id)

    if start_node not in nodes or end_node not in nodes:
        return {
            "success": False,
            "total_distance": 0.0,
            "naive_distance": 0.0,
            "estimated_time_seconds": 0,
            "path_nodes": [],
            "visiting_sequence": [],
            "congested_racks_avoided": [],
        }

    products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()

    target_nodes: List[str] = []
    node_stop_names: Dict[str, List[str]] = {}
    for prod in products:
        target_node_id = f"NODE_{prod.rack_id}"
        if target_node_id in nodes:
            if target_node_id not in target_nodes:
                target_nodes.append(target_node_id)
                node_stop_names[target_node_id] = []
            node_stop_names[target_node_id].append(prod.name)

    # ---- Crowd-density awareness: penalize busy racks so the optimizer routes
    #      around them when the shopper opts in ----
    node_penalty: Optional[Dict[str, float]] = None
    congested_racks_avoided: List[str] = []
    if avoid_crowds:
        all_rack_ids = [r.rack_id for r in db.query(Rack).filter(Rack.store_id == store_id).all()]
        crowd = get_crowd_levels(all_rack_ids)
        node_penalty = {f"NODE_{rid}": 1.0 + level * 1.6 for rid, level in crowd.items()}
        congested_racks_avoided = [rid for rid, level in crowd.items() if level >= 0.7]

    # ---- Step 1: distance matrix between start / stops / end (A*) ----
    node_set = [start_node] + target_nodes + [end_node]
    matrix, paths = build_distance_matrix(nodes, graph, node_set, node_penalty)

    # ---- Step 2: Nearest-Neighbor construction ----
    order = _nearest_neighbor_order(start_node, target_nodes, matrix)

    # ---- Step 3: 2-opt refinement (approximate TSP improvement) ----
    order = _two_opt(start_node, order, end_node, matrix)

    visit_sequence = [start_node] + order + [end_node]
    total_distance = _tour_length(start_node, order, end_node, matrix)

    # ---- Reconstruct the full walkable path node-by-node ----
    full_path_nodes: List[str] = []
    for a, b in zip(visit_sequence[:-1], visit_sequence[1:]):
        leg = paths.get((a, b), [])
        if not leg:
            continue
        full_path_nodes.extend(leg if not full_path_nodes else leg[1:])

    formatted_nodes = []
    for node_id in full_path_nodes:
        node_obj = nodes[node_id]
        stop_names = node_stop_names.get(node_id)
        stop_label = None
        if stop_names:
            rack_id = node_id.replace("NODE_", "")
            if len(stop_names) == 1:
                stop_label = f"Pick {stop_names[0]} (Rack {rack_id})"
            else:
                stop_label = f"Pick {len(stop_names)} items at Rack {rack_id}: " + ", ".join(stop_names)
        formatted_nodes.append({
            "node_id": node_id,
            "x_pos": node_obj.x_pos,
            "y_pos": node_obj.y_pos,
            "node_type": node_obj.node_type,
            "stop_name": stop_label,
        })

    # Estimated walk speed: ~1.2 meters/sec (average indoor shopping pace)
    estimated_time = int(total_distance / 1.2) if total_distance != float('inf') else 0

    # Naive comparison: visiting racks in the order products were added,
    # unoptimized - this is what the "% shorter" insight is measured against.
    naive_distance = _tour_length(start_node, target_nodes, end_node, matrix) if target_nodes else 0.0

    return {
        "success": True,
        "total_distance": round(total_distance, 2) if total_distance != float('inf') else 0.0,
        "naive_distance": round(naive_distance, 2) if naive_distance != float('inf') else 0.0,
        "estimated_time_seconds": estimated_time,
        "path_nodes": formatted_nodes,
        "visiting_sequence": visit_sequence,
        "congested_racks_avoided": congested_racks_avoided,
    }
