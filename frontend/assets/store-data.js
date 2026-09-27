// ---------------------------------------------------------------------------
// EasyGo — shared config, layout & cart persistence
// Same-origin in production (FastAPI serves these files) and when running the
// backend locally on :8000. Falls back to localhost:8000 only when opened
// directly from disk (file://) for frontend-only development.
// ---------------------------------------------------------------------------
const API_BASE_URL = window.location.protocol === "file:" ? "http://localhost:8000" : "";

const ENTRANCE = { x: 400, y: 560 };
const CHECKOUT = { x: 680, y: 560 };

const RACK_LAYOUT = [
  { id: 'A1', label: 'Breakfast',     x: 150, y: 120, width: 100, height: 40 },
  { id: 'A2', label: 'Noodles',       x: 350, y: 120, width: 100, height: 40 },
  { id: 'A3', label: 'Rice & Pulses', x: 550, y: 120, width: 100, height: 40 },
  { id: 'B1', label: 'Spices & Salt', x: 150, y: 240, width: 100, height: 40 },
  { id: 'B2', label: 'Cooking Oil',   x: 350, y: 240, width: 100, height: 40 },
  { id: 'B3', label: 'Tea & Coffee',  x: 550, y: 240, width: 100, height: 40 },
  { id: 'C1', label: 'Biscuits',      x: 150, y: 360, width: 100, height: 40 },
  { id: 'C2', label: 'Dairy & Milk',  x: 350, y: 360, width: 100, height: 40 },
  { id: 'C3', label: 'Snacks',        x: 550, y: 360, width: 100, height: 40 },
  { id: 'D1', label: 'Body Care',     x: 150, y: 480, width: 100, height: 40 },
  { id: 'D2', label: 'Detergents',    x: 350, y: 480, width: 100, height: 40 },
  { id: 'D3', label: 'Hygiene',       x: 550, y: 480, width: 100, height: 40 }
];

const SNS_CART_KEY = 'sns_cart_v1';
const SNS_BUDGET_KEY = 'sns_budget_v1';
const SNS_ROUTEPREFS_KEY = 'sns_route_prefs_v1';

function getCart() {
  try { return JSON.parse(localStorage.getItem(SNS_CART_KEY)) || []; }
  catch (e) { return []; }
}
function setCart(cart) {
  try { localStorage.setItem(SNS_CART_KEY, JSON.stringify(cart)); } catch (e) { /* storage unavailable */ }
}
function getBudget() {
  const v = parseFloat(localStorage.getItem(SNS_BUDGET_KEY));
  return isNaN(v) ? null : v;
}
function setBudget(v) {
  if (v === null) localStorage.removeItem(SNS_BUDGET_KEY);
  else localStorage.setItem(SNS_BUDGET_KEY, String(v));
}
function getRoutePrefs() {
  try { return JSON.parse(localStorage.getItem(SNS_ROUTEPREFS_KEY)) || { avoid_crowds: false }; }
  catch (e) { return { avoid_crowds: false }; }
}
function setRoutePrefs(prefs) {
  try { localStorage.setItem(SNS_ROUTEPREFS_KEY, JSON.stringify(prefs)); } catch (e) {}
}

function cartTotal(cart) {
  return cart.reduce((sum, item) => sum + (Number(item.price) || 0), 0);
}

function crowdColor(level) {
  if (level < 0.35) return '#22C55E';
  if (level < 0.7) return '#F59E0B';
  return '#E23B32';
}
function crowdLabelFor(level) {
  if (level < 0.35) return 'Low';
  if (level < 0.7) return 'Moderate';
  return 'High';
}
