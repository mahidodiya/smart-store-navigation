// ---------------------------------------------------------------------------
// EasyGo — lightweight i18n (English / Hindi)
// Usage: give any element data-i18n="key" (textContent) or
// data-i18n-placeholder="key" (input placeholder). Call initLanguage() on
// DOMContentLoaded and wireLanguageToggle('lang-toggle-btn-en','lang-toggle-btn-hi').
// ---------------------------------------------------------------------------

const SNS_TRANSLATIONS = {
  en: {
    brand_tagline: "Shop smarter. Find faster.",
    nav_shop: "Shop", nav_navigate: "Navigate", nav_dashboard: "Manager view",
    hero_title: "Find what you need — without the search",
    hero_sub: "Welcome to the store. Search for products, add them to your list, and we’ll show you the quickest path through the aisles — so you spend less time walking and more time shopping.",
    hero_cta: "Start shopping", hero_cta_sub: "Store Manager dashboard",
    feat_route_title: "Smartest path in store", feat_route_sub: "We plan the shortest walk so you hit every item without backtracking",
    feat_live_title: "Turn-by-turn guidance", feat_live_sub: "Clear step-by-step directions — with optional voice prompts",
    feat_crowd_title: "Avoid busy aisles", feat_crowd_sub: "Routes can skip crowded sections so you move faster",
    feat_budget_title: "Budget tracker", feat_budget_sub: "See your running total as you shop and set a spend limit",
    search_label: "Find products", search_placeholder: "Search milk, Maggi, Surf Excel, salt…",
    cat_all: "All", cat_dairy: "Dairy", cat_grocery: "Grocery", cat_snacks: "Snacks", cat_household: "Household",
    products_title: "Available products",
    cart_title: "Shopping list", cart_clear: "Clear all", cart_empty: "No products selected yet — tap products above to add them.",
    budget_title: "Budget", budget_set: "Set limit", budget_remaining: "remaining", budget_over: "over budget",
    find_route: "Find my optimized route",
    map_title: "Digital store map", map_sub: "SuperMart Express · floor plan view",
    legend_entrance: "Entrance", legend_checkout: "Checkout", legend_rack: "Rack in your list", legend_path: "Optimized path",
    legend_crowd: "Crowd level", avoid_crowds: "Avoid busy aisles",
    distance_label: "Distance", time_label: "Est. time", stops_label: "Stops",
    start_walk: "Start walking simulation", pause_walk: "Pause simulation", resume_walk: "Resume simulation",
    reset: "Reset", full_steps: "Full route steps", back_to_shop: "Back to shopping list",
    dash_title: "Store manager dashboard", dash_sub: "Aggregated, anonymized shopper-route analytics",
    dash_total_routes: "Routes computed", dash_saved: "Distance saved", dash_avg_saving: "Avg. savings",
    dash_avg_items: "Avg items / trip", dash_heatmap: "Rack popularity heatmap", dash_top_products: "Most requested products",
    dash_crowd_routes: "Trips using crowd-avoidance",
  },
  hi: {
    brand_tagline: "स्मार्ट खरीदारी। तेज़ खोज।",
    nav_shop: "खरीदारी", nav_navigate: "नेविगेट", nav_dashboard: "प्रबंधक दृश्य",
    hero_title: "जो चाहिए, बिना भटके पाएं",
    hero_sub: "स्टोर में आपका स्वागत है। उत्पाद खोजें, सूची में जोड़ें, और हम आपको गलियारों का सबसे छोटा रास्ता दिखाएंगे — कम चलें, ज़्यादा खरीदारी करें।",
    hero_cta: "खरीदारी शुरू करें", hero_cta_sub: "स्टोर मैनेजर डैशबोर्ड",
    feat_route_title: "स्टोर में सबसे अच्छा रास्ता", feat_route_sub: "हम सबसे छोटा रास्ता बनाते हैं ताकि आप बिना पीछे मुड़े हर सामान ले सकें",
    feat_live_title: "कदम-दर-कदम मार्गदर्शन", feat_live_sub: "साफ दिशा-निर्देश — आवाज़ के साथ भी",
    feat_crowd_title: "व्यस्त गलियारों से बचें", feat_crowd_sub: "भीड़ वाले हिस्से छोड़कर तेज़ी से आगे बढ़ें",
    feat_budget_title: "बजट ट्रैकर", feat_budget_sub: "खरीदारी के दौरान कुल राशि देखें और सीमा तय करें",
    search_label: "उत्पाद खोजें", search_placeholder: "दूध, मैगी, सर्फ एक्सेल, नमक खोजें…",
    cat_all: "सभी", cat_dairy: "डेयरी", cat_grocery: "किराना", cat_snacks: "स्नैक्स", cat_household: "घरेलू",
    products_title: "उपलब्ध उत्पाद",
    cart_title: "खरीदारी सूची", cart_clear: "सभी हटाएं", cart_empty: "अभी कोई उत्पाद नहीं चुना — जोड़ने के लिए ऊपर टैप करें।",
    budget_title: "बजट", budget_set: "सीमा तय करें", budget_remaining: "शेष", budget_over: "बजट से अधिक",
    find_route: "मेरा अनुकूलित रूट खोजें",
    map_title: "डिजिटल स्टोर मैप", map_sub: "सुपरमार्ट एक्सप्रेस · फ्लोर प्लान दृश्य",
    legend_entrance: "प्रवेश", legend_checkout: "चेकआउट", legend_rack: "आपकी सूची में रैक", legend_path: "अनुकूलित रास्ता",
    legend_crowd: "भीड़ स्तर", avoid_crowds: "व्यस्त गलियारों से बचें",
    distance_label: "दूरी", time_label: "अनुमानित समय", stops_label: "पड़ाव",
    start_walk: "वॉक सिमुलेशन शुरू करें", pause_walk: "रोकें", resume_walk: "फिर से शुरू करें",
    reset: "रीसेट", full_steps: "पूरा रूट चरण", back_to_shop: "खरीदारी सूची पर वापस जाएं",
    dash_title: "स्टोर मैनेजर डैशबोर्ड", dash_sub: "एकत्रित, गुमनाम खरीदार-रूट विश्लेषण",
    dash_total_routes: "गणना किए गए रूट", dash_saved: "बचाई गई दूरी", dash_avg_saving: "औसत बचत",
    dash_avg_items: "औसत आइटम / ट्रिप", dash_heatmap: "रैक लोकप्रियता हीटमैप", dash_top_products: "सर्वाधिक मांग वाले उत्पाद",
    dash_crowd_routes: "भीड़-बचाव वाले ट्रिप",
  }
};

function getLanguage() {
  return localStorage.getItem('sns_lang') || 'en';
}

function t(key) {
  const lang = getLanguage();
  return (SNS_TRANSLATIONS[lang] && SNS_TRANSLATIONS[lang][key]) || SNS_TRANSLATIONS.en[key] || key;
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.getAttribute('data-i18n'));
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.setAttribute('placeholder', t(el.getAttribute('data-i18n-placeholder')));
  });
  document.documentElement.lang = getLanguage() === 'hi' ? 'hi' : 'en';
  document.querySelectorAll('.lang-toggle button').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === getLanguage());
  });
}

function setLanguage(lang) {
  localStorage.setItem('sns_lang', lang);
  applyTranslations();
  if (typeof onLanguageChange === 'function') onLanguageChange(lang);
}

function initLanguage() {
  applyTranslations();
  document.querySelectorAll('.lang-toggle button').forEach(btn => {
    btn.addEventListener('click', () => setLanguage(btn.dataset.lang));
  });
}

document.addEventListener('DOMContentLoaded', initLanguage);
