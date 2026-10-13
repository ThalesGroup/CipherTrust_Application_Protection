export const THEME_KEY = "cm-metrics-theme";
export const TAB_CHIP_KEY = "cm-metrics-tab-chips";
export const RANGE_KEY = "cm-metrics-range";

export const RANGE_OPTIONS = [
  { id: "5m", label: "5m", seconds: 300 },
  { id: "15m", label: "15m", seconds: 900 },
  { id: "30m", label: "30m", seconds: 1800 },
  { id: "1h", label: "1h", seconds: 3600 },
  { id: "6h", label: "6h", seconds: 21600 },
  { id: "24h", label: "24h", seconds: 86400 },
  { id: "7d", label: "7d", seconds: 604800 },
  { id: "30d", label: "30d", seconds: 2592000 },
];

export function loadSavedRange() {
  try {
    const raw = localStorage.getItem(RANGE_KEY);
    if (RANGE_OPTIONS.some((r) => r.id === raw)) return raw;
  } catch (_) { /* ignore */ }
  return "24h";
}

export function rangeSeconds(rangeId) {
  return RANGE_OPTIONS.find((r) => r.id === rangeId)?.seconds || 86400;
}

export const COLORS_DARK = [
  "#2dd4bf", "#60a5fa", "#fbbf24", "#f472b6", "#a78bfa", "#fb923c",
  "#34d399", "#38bdf8", "#f87171", "#c084fc",
];
export const COLORS_LIGHT = [
  "#0f766e", "#2563eb", "#d97706", "#db2777", "#7c3aed", "#ea580c",
  "#059669", "#0284c7", "#dc2626", "#6d28d9",
];

export function getDashboardGroups() {
  return window.CM_METRICS?.dashboardGroups || [
    { id: "overview", title: "Overview", dashboards: [{ id: "overview", title: "Overview" }] },
  ];
}
