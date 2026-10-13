import { THEME_KEY, COLORS_DARK, COLORS_LIGHT } from "./config.js";
import { state } from "./state.js";

export function currentTheme() {
  return document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
}

export function chartColors() {
  return currentTheme() === "light" ? COLORS_LIGHT : COLORS_DARK;
}

export function cssVar(name, fallback) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

export function applyChartDefaults() {
  Chart.defaults.color = cssVar("--chart-tick", "#8b9bb8");
  Chart.defaults.borderColor = cssVar("--border", "#243049");
  Chart.defaults.font.family = "'IBM Plex Sans', system-ui, sans-serif";
  Chart.defaults.animation = false;
}

export function syncThemeButton() {
  const btn = document.getElementById("btn-theme");
  if (!btn) return;
  const isLight = currentTheme() === "light";
  const title = isLight ? "Switch to dark mode" : "Switch to light mode";
  btn.title = title;
  btn.setAttribute("aria-label", title);
}

export function setTheme(theme, { persist = true, refreshCharts = true, onRefreshCharts } = {}) {
  const next = theme === "light" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  if (persist) {
    try { localStorage.setItem(THEME_KEY, next); } catch (_) { /* ignore */ }
  }
  syncThemeButton();
  applyChartDefaults();
  if (refreshCharts) {
    if (state.charts.length) {
      state.panelMeta = null;
      if (typeof onRefreshCharts === "function") {
        onRefreshCharts();
      }
    } else if (typeof onRefreshCharts === "function") {
      onRefreshCharts();
    }
  }
}

export function resizeChartsSoon() {
  requestAnimationFrame(() => {
    state.charts.forEach(({ chart }) => {
      try { chart.resize(); } catch (_) { /* ignore */ }
    });
    if (state.fleetHealthChart && !state.fleetHealthChart.destroyed) {
      try { state.fleetHealthChart.resize(); } catch (_) { /* ignore */ }
    }
  });
}
