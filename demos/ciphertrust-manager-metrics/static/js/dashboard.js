import { TAB_CHIP_KEY, RANGE_KEY, RANGE_OPTIONS, getDashboardGroups } from "./config.js";
import { state, getDom } from "./state.js";
import {
  escapeHtml,
  fmt,
  displayUnit,
  yTickCallback,
  truncateLabel,
  formatSeriesTooltip,
  tooltipTitle,
  tsLabel,
  panelSignature,
  isBytesUnit,
  isBytesRateUnit,
  fmtBytes,
} from "./format.js";
import { chartColors, cssVar } from "./theme.js";
import { fetchJSON, refreshStatus } from "./api.js";
import { loadAppliances, renderApplianceTree, openModal, renderFleetHealth } from "./appliances.js";

function chartXBounds() {
  const secs = RANGE_OPTIONS.find((r) => r.id === state.rangeId)?.seconds || 86400;
  const max = Date.now();
  return { min: max - secs * 1000, max };
}
export function groupForDashboard(dashboardId) {
  const groups = getDashboardGroups();
  for (const g of groups) {
    if ((g.dashboards || []).some((d) => d.id === dashboardId)) return g.id;
  }
  return groups[0]?.id || "overview";
}

export function dashboardsForGroup(groupId) {
  const g = getDashboardGroups().find((x) => x.id === groupId);
  return g?.dashboards || [];
}

export function persistTabChip(groupId, dashboardId) {
  state.tabChips[groupId] = dashboardId;
  try { localStorage.setItem(TAB_CHIP_KEY, JSON.stringify(state.tabChips)); } catch (_) { /* ignore */ }
}

export function syncRangePicker() {
  document.querySelectorAll(".range-picker").forEach((picker) => {
    picker.querySelectorAll("[data-range]").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.range === state.rangeId);
    });
  });
}

export function setTimeRange(rangeId, { reload = true } = {}) {
  if (!RANGE_OPTIONS.some((r) => r.id === rangeId)) return;
  if (rangeId === state.rangeId && !reload) {
    syncRangePicker();
    return;
  }
  state.rangeId = rangeId;
  try { localStorage.setItem(RANGE_KEY, rangeId); } catch (_) { /* ignore */ }
  syncRangePicker();
  state.panelMeta = null;
  if (reload && state.viewMode === "dashboard") {
    loadDashboard(state.dashboardId, { forceFull: true });
  }
  if (reload && state.viewMode === "appliances") {
    renderApplianceTree();
  }
}

export function defaultChipForGroup(groupId) {
  const chips = dashboardsForGroup(groupId);
  if (!chips.length) return "overview";
  const saved = state.tabChips[groupId];
  if (saved && chips.some((c) => c.id === saved)) return saved;
  return chips[0].id;
}

export function destroyCharts() {
  state.charts.forEach((c) => {
    try {
      c.chart.destroy();
    } catch (_) {
      /* already destroyed */
    }
  });
  state.charts = [];
}

function safeChartUpdate(chart) {
  if (!chart || chart.destroyed) return;
  try {
    chart.update("none");
  } catch (_) {
    /* ignore mid-destroy races */
  }
}

export function renderPrimaryTabs() {
  const { primaryTabs } = getDom();
  if (!primaryTabs) return;
  primaryTabs.querySelectorAll(".primary-tab").forEach((btn) => {
    let active = false;
    if (state.viewMode === "appliances") {
      active = btn.dataset.group === "appliances";
    } else if (state.viewMode === "healthcheck") {
      active = btn.dataset.group === "healthcheck";
    } else {
      active = btn.dataset.group === state.groupId;
    }
    btn.classList.toggle("active", active);
  });
}

export function renderSecondaryChips() {
  const { secondaryChips } = getDom();
  if (!secondaryChips) return;
  if (state.viewMode === "appliances" || state.viewMode === "healthcheck") {
    secondaryChips.innerHTML = "";
    return;
  }
  const chips = dashboardsForGroup(state.groupId);
  if (chips.length <= 1) {
    secondaryChips.innerHTML = "";
    return;
  }
  secondaryChips.innerHTML = chips
    .map((d) => {
      const active = d.id === state.dashboardId ? " active" : "";
      return `<button type="button" class="secondary-chip${active}" data-id="${d.id}" title="${escapeHtml(d.description || d.title)}">${escapeHtml(d.title)}</button>`;
    })
    .join("");
}

export function syncWorkspaceChrome() {
  const { secondaryRow, appliancesView, panelsEl, fleetHealth, healthcheckView } = getDom();
  const appliancesMode = state.viewMode === "appliances";
  const healthcheckMode = state.viewMode === "healthcheck";
  if (secondaryRow) secondaryRow.classList.toggle("is-hidden", appliancesMode || healthcheckMode);
  if (appliancesView) appliancesView.hidden = !appliancesMode;
  if (panelsEl) panelsEl.hidden = appliancesMode || healthcheckMode;
  if (healthcheckView) {
    if (healthcheckMode) {
      healthcheckView.hidden = false;
    } else {
      // display:flex on .healthcheck-view overrides [hidden] unless we force-hide;
      // also tear down iframe/content so it cannot paint over other tabs.
      const iframe = healthcheckView.querySelector("#hc-iframe");
      if (iframe) iframe.src = "about:blank";
      if (healthcheckView.innerHTML) healthcheckView.innerHTML = "";
      healthcheckView.hidden = true;
    }
  }
  if (appliancesMode) {
    renderApplianceTree();
  } else {
    if (!healthcheckMode) {
      state.groupId = groupForDashboard(state.dashboardId);
    }
    if (fleetHealth) fleetHealth.hidden = true;
  }
  renderPrimaryTabs();
  renderSecondaryChips();
  syncRangePicker();
}

export function syncTabChrome() {
  if (state.viewMode === "appliances" || state.viewMode === "healthcheck") {
    syncWorkspaceChrome();
    return;
  }
  state.groupId = groupForDashboard(state.dashboardId);
  renderPrimaryTabs();
  renderSecondaryChips();
  syncRangePicker();
}

export function showDashboardGroup(groupId) {
  state.viewMode = "dashboard";
  state.groupId = groupId;
  const nextId = defaultChipForGroup(groupId);
  persistTabChip(groupId, nextId);
  state.panelMeta = null;
  syncWorkspaceChrome();
  loadDashboard(nextId, { forceFull: true });
}

function panelSpanClass(panel) {
  const span = Number(panel.span);
  if (Number.isFinite(span) && span >= 1 && span <= 12) return `span-${span}`;
  if (panel.wide || panel.type === "table") return "span-12";
  if (panel.type === "stat") return "span-3";
  if (panel.type === "timeseries" || panel.type === "bar") return "span-6";
  return "span-12";
}

function renderStat(panel, animate) {
  const el = document.createElement("article");
  const isText = typeof panel.value === "string";
  const tone = String(panel.tone || "").toLowerCase();
  const toneClass =
    tone === "fail" || tone === "warning" || tone === "pass" || tone === "info"
      ? ` tone-${tone}`
      : "";
  el.className = `panel stat${isText ? " text" : ""}${toneClass} ${panelSpanClass(panel)}${
    animate ? " enter" : ""
  }`;
  el.dataset.panelTitle = panel.title;
  el.dataset.panelType = "stat";
  if (toneClass) el.dataset.tone = tone;
  const unitText = isText ? "" : displayUnit(panel.unit, panel.value);
  el.innerHTML = `
    <h3 class="panel-title">${escapeHtml(panel.title)}</h3>
    <div class="stat-value"><span class="stat-num">${escapeHtml(fmt(panel.value, panel.unit))}</span>${
      unitText ? `<span class="stat-unit">${escapeHtml(unitText)}</span>` : ""
    }</div>
    ${panel.description ? `<div class="stat-desc">${escapeHtml(panel.description)}</div>` : ""}
  `;
  return el;
}

function renderNote(panel, animate) {
  const el = document.createElement("aside");
  const tone = String(panel.tone || "").toLowerCase();
  const toneClass = tone === "fail" || tone === "warning" || tone === "pass" || tone === "info"
    ? ` note-${tone}`
    : "";
  el.className = `panel note span-12${toneClass}${animate ? " enter" : ""}`;
  el.dataset.panelType = "note";
  el.dataset.panelTitle = panel.title || "note";
  const title = panel.title
    ? `<strong class="note-title">${escapeHtml(panel.title)}</strong>`
    : "";
  el.innerHTML = `${title}<span class="note-text">${escapeHtml(panel.text || "")}</span>`;
  return el;
}

function makeLineChart(canvas, panel) {
  const COLORS = chartColors();
  const grid = cssVar("--chart-grid", "#1c2740");
  const unit = panel.unit || "";
  const xBounds = chartXBounds();
  // Truncate labels up-front. Do NOT override legend.generateLabels by calling
  // Chart.defaults...generateLabels — in Chart.js 4 that recurses forever.
  const datasets = (panel.series || []).map((s, i) => ({
    label: truncateLabel(s.name, 36),
    data: (s.points || []).map((p) => ({ x: p.t * 1000, y: p.v })),
    borderColor: COLORS[i % COLORS.length],
    backgroundColor: COLORS[i % COLORS.length] + "33",
    borderWidth: 1.5,
    pointRadius: 0,
    tension: 0.25,
  }));
  return new Chart(canvas, {
    type: "line",
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      parsing: false,
      layout: { padding: { top: 4, right: 8, bottom: 0, left: 0 } },
      interaction: { mode: "nearest", intersect: false },
      plugins: {
        legend: {
          display: datasets.length > 1 && datasets.length <= 8,
          position: "bottom",
          align: "start",
          labels: {
            boxWidth: 10,
            boxHeight: 10,
            padding: 12,
            font: { size: 10 },
          },
        },
        tooltip: {
          displayColors: true,
          callbacks: {
            title: tooltipTitle,
            label: (ctx) => formatSeriesTooltip(unit, ctx),
          },
        },
      },
      scales: {
        x: {
          type: "linear",
          min: xBounds.min,
          max: xBounds.max,
          ticks: {
            color: cssVar("--muted", "#8b9bb8"),
            callback: (v) => tsLabel(v / 1000, state.rangeId),
            autoSkip: true,
            autoSkipPadding: 12,
            maxTicksLimit: state.rangeId === "30d" ? 10 : state.rangeId === "7d" ? 7 : 8,
            maxRotation: 0,
            minRotation: 0,
            padding: 6,
          },
          grid: { color: grid, drawBorder: false },
          border: { display: false },
        },
        y: {
          grace: "5%",
          grid: { color: grid, drawBorder: false },
          border: { display: false },
          title: unit && !isBytesUnit(unit) && !isBytesRateUnit(unit) && unit !== "%"
            ? { display: true, text: unit, color: cssVar("--muted", "#8b9bb8"), font: { size: 10 } }
            : undefined,
          ticks: {
            padding: 8,
            maxTicksLimit: 6,
            callback: yTickCallback(unit) || (
              unit === "%"
                ? (v) => `${Number(v).toFixed(0)}%`
                : undefined
            ),
          },
        },
      },
    },
  });
}

function makeBarChart(canvas, panel) {
  const COLORS = chartColors();
  const grid = cssVar("--chart-grid", "#1c2740");
  const items = panel.items || [];
  const many = items.length > 8;
  const crowded = items.length > 14;
  // Keep axis labels readable; full name still available in tooltip.
  const axisMax = crowded ? 14 : many ? 20 : 28;
  const fullLabels = items.map((i) => String(i.label || ""));
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels: fullLabels.map((l) => truncateLabel(l, axisMax)),
      datasets: [{
        data: items.map((i) => i.value),
        backgroundColor: items.map((_, i) => COLORS[i % COLORS.length] + "cc"),
        borderColor: items.map((_, i) => COLORS[i % COLORS.length]),
        borderWidth: 1,
        borderRadius: 4,
        maxBarThickness: crowded ? 22 : many ? 32 : 48,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      // Extra bottom room so rotated category labels are not clipped.
      layout: { padding: { top: 4, right: 8, bottom: many ? 8 : 4, left: 4 } },
      // Show tooltip for the category under the cursor even when the bar is tiny
      // (hover anywhere in that vertical column, not only on the bar pixels).
      interaction: { mode: "index", intersect: false, axis: "x" },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (tipItems) => {
              const idx = tipItems[0]?.dataIndex;
              return idx != null ? (fullLabels[idx] || "") : "";
            },
            label: (ctx) => {
              const raw = ctx.parsed.y;
              if (isBytesUnit(panel.unit)) return fmtBytes(raw, false);
              if (isBytesRateUnit(panel.unit)) return fmtBytes(raw, true);
              const unit = panel.unit ? ` ${panel.unit}` : "";
              return `${fmt(raw, panel.unit)}${isBytesUnit(panel.unit) || isBytesRateUnit(panel.unit) ? "" : unit}`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { display: false, drawBorder: false },
          border: { display: false },
          ticks: {
            color: cssVar("--muted", "#8b9bb8"),
            // autoSkip was dropping most/all domain labels when rotated text
            // did not fit the fixed chart height — always show every category.
            autoSkip: false,
            maxRotation: many ? 60 : 45,
            minRotation: many ? 45 : 25,
            font: { size: crowded ? 9 : 10 },
            padding: 4,
          },
        },
        y: {
          beginAtZero: true,
          grace: "5%",
          grid: { color: grid, drawBorder: false },
          border: { display: false },
          ticks: {
            padding: 8,
            maxTicksLimit: 6,
            callback: yTickCallback(panel.unit),
          },
        },
      },
    },
  });
}

function renderTimeseries(panel, animate) {
  const el = document.createElement("article");
  el.className = `panel chart ${panelSpanClass(panel)}${panel.wide ? " wide" : ""}${animate ? " enter" : ""}`;
  el.dataset.panelTitle = panel.title;
  el.dataset.panelType = "timeseries";
  el.innerHTML = `
    <h3 class="panel-title">${escapeHtml(panel.title)}</h3>
    <div class="chart-wrap"><canvas></canvas></div>
  `;
  const chart = makeLineChart(el.querySelector("canvas"), panel);
  state.charts.push({ chart, type: "timeseries", title: panel.title });
  return el;
}

function renderBar(panel, animate) {
  const el = document.createElement("article");
  el.className = `panel chart ${panelSpanClass(panel)}${panel.wide ? " wide" : ""}${animate ? " enter" : ""}`;
  el.dataset.panelTitle = panel.title;
  el.dataset.panelType = "bar";
  el.innerHTML = `
    <h3 class="panel-title">${escapeHtml(panel.title)}</h3>
    <div class="chart-wrap"><canvas></canvas></div>
  `;
  const chart = makeBarChart(el.querySelector("canvas"), panel);
  state.charts.push({ chart, type: "bar", title: panel.title });
  return el;
}

function renderTable(panel, animate) {
  const el = document.createElement("article");
  el.className = `panel table wide ${panelSpanClass(panel)}${animate ? " enter" : ""}`;
  el.dataset.panelTitle = panel.title;
  el.dataset.panelType = "table";
  const cols = panel.columns || [];
  const rows = panel.rows || [];
  el.innerHTML = `
    <h3 class="panel-title">${escapeHtml(panel.title)}</h3>
    <div class="table-wrap">
      <table class="data">
        <thead><tr>${cols.map((c) => `<th>${escapeHtml(c)}</th>`).join("")}</tr></thead>
        <tbody>
          ${rows.map((r) => `<tr>${cols.map((c) => {
            const cls = c === "metric" || c === "labels" ? "mono" : "";
            return `<td class="${cls}">${escapeHtml(String(r[c] ?? ""))}</td>`;
          }).join("")}</tr>`).join("")}
        </tbody>
      </table>
    </div>
  `;
  return el;
}

export function fullRender(data, animate = true) {
  const { panelsEl, titleEl, descEl } = getDom();
  destroyCharts();
  panelsEl.innerHTML = "";
  const appliance = data.appliance;
  const host = appliance ? (appliance.display_name || appliance.host) : "";
  titleEl.textContent = data.title + (host ? ` · ${host.replace(/^https?:\/\//, "")}` : "");
  descEl.textContent = data.description || "";

  const panels = data.panels || [];
  if (!panels.length) {
    panelsEl.innerHTML = `<div class="empty">No panels yet — waiting for metrics scrape.</div>`;
    state.panelMeta = null;
    return;
  }

  // Group consecutive same-type panels into rows so stats never sit beside charts.
  let row = null;
  let rowType = null;
  panels.forEach((panel) => {
    let node;
    if (panel.type === "stat") node = renderStat(panel, animate);
    else if (panel.type === "timeseries") node = renderTimeseries(panel, animate);
    else if (panel.type === "bar") node = renderBar(panel, animate);
    else if (panel.type === "table") node = renderTable(panel, animate);
    else if (panel.type === "note") node = renderNote(panel, animate);
    else {
      node = document.createElement("article");
      node.className = "panel wide span-12";
      node.textContent = `Unsupported panel: ${panel.type}`;
    }

    const groupType = panel.type === "timeseries" || panel.type === "bar" ? "chart" : panel.type;
    if (!row || rowType !== groupType) {
      row = document.createElement("div");
      row.className = `panel-row panel-row-${groupType}`;
      panelsEl.appendChild(row);
      rowType = groupType;
    }
    row.appendChild(node);
  });
  state.panelMeta = panelSignature(data);
}

/** @returns {boolean} false when layout/charts are missing and a full redraw is needed */
export function updateInPlace(data) {
  const { panelsEl, titleEl } = getDom();
  if (!panelsEl) return false;
  const appliance = data.appliance;
  const host = appliance ? (appliance.display_name || appliance.host) : "";
  titleEl.textContent = data.title + (host ? ` · ${host.replace(/^https?:\/\//, "")}` : "");

  const panels = data.panels || [];
  for (const panel of panels) {
    if (panel.type === "stat") {
      const panelEl = panelsEl.querySelector(
        `.panel.stat[data-panel-title="${CSS.escape(panel.title)}"]`
      );
      if (!panelEl) return false;
      const numEl = panelEl.querySelector(".stat-num");
      if (numEl) numEl.textContent = fmt(panel.value, panel.unit);
      const tone = String(panel.tone || "").toLowerCase();
      panelEl.classList.remove("tone-fail", "tone-warning", "tone-pass", "tone-info");
      if (tone === "fail" || tone === "warning" || tone === "pass" || tone === "info") {
        panelEl.classList.add(`tone-${tone}`);
        panelEl.dataset.tone = tone;
      } else {
        delete panelEl.dataset.tone;
      }
      let unitEl = panelEl.querySelector(".stat-unit");
      const unitText = displayUnit(panel.unit, panel.value);
      if (unitText) {
        if (!unitEl) {
          unitEl = document.createElement("span");
          unitEl.className = "stat-unit";
          panelEl.querySelector(".stat-value")?.appendChild(unitEl);
        }
        unitEl.textContent = unitText;
      } else if (unitEl) {
        unitEl.remove();
      }
      continue;
    }

    if (panel.type === "timeseries") {
      const entry = state.charts.find((c) => c.type === "timeseries" && c.title === panel.title);
      const chart = entry?.chart;
      if (!entry || !chart || chart.destroyed) return false;
      const COLORS = chartColors();
      const series = panel.series || [];
      const xBounds = chartXBounds();
      chart.data.datasets = series.map((s, i) => ({
        label: truncateLabel(s.name, 36),
        data: (s.points || []).map((p) => ({ x: p.t * 1000, y: p.v })),
        borderColor: COLORS[i % COLORS.length],
        backgroundColor: COLORS[i % COLORS.length] + "33",
        borderWidth: 1.5,
        pointRadius: 0,
        tension: 0.25,
      }));
      if (chart.options?.scales?.x) {
        chart.options.scales.x.min = xBounds.min;
        chart.options.scales.x.max = xBounds.max;
        chart.options.scales.x.ticks = {
          ...chart.options.scales.x.ticks,
          callback: (v) => tsLabel(v / 1000, state.rangeId),
          maxTicksLimit: state.rangeId === "30d" ? 10 : state.rangeId === "7d" ? 7 : 8,
        };
      }
      // Keep tooltip callbacks from chart creation; only refresh data.
      safeChartUpdate(chart);
      continue;
    }

    if (panel.type === "bar") {
      const entry = state.charts.find((c) => c.type === "bar" && c.title === panel.title);
      const chart = entry?.chart;
      if (!entry || !chart || chart.destroyed) return false;
      const COLORS = chartColors();
      const items = panel.items || [];
      chart.data.labels = items.map((i) => i.label);
      if (!chart.data.datasets[0]) return false;
      chart.data.datasets[0].data = items.map((i) => i.value);
      chart.data.datasets[0].backgroundColor = items.map((_, i) => COLORS[i % COLORS.length] + "cc");
      chart.data.datasets[0].borderColor = items.map((_, i) => COLORS[i % COLORS.length]);
      safeChartUpdate(chart);
      continue;
    }

    if (panel.type === "table") {
      const el = panelsEl.querySelector(
        `.panel.table[data-panel-title="${CSS.escape(panel.title)}"] tbody`
      );
      if (!el) return false;
      const cols = panel.columns || [];
      const rows = panel.rows || [];
      el.innerHTML = rows.map((r) => `<tr>${cols.map((c) => {
        const cls = c === "metric" || c === "labels" ? "mono" : "";
        return `<td class="${cls}">${escapeHtml(String(r[c] ?? ""))}</td>`;
      }).join("")}</tr>`).join("");
      continue;
    }

    if (panel.type === "note") {
      const el = panelsEl.querySelector(
        `.panel.note[data-panel-title="${CSS.escape(panel.title || "note")}"] .note-text`
      );
      if (el) el.textContent = panel.text || "";
    }
  }
  return true;
}

export function applyDashboard(data, forceFull = false) {
  try {
    const sig = panelSignature(data);
    // Prefer in-place updates on Auto refresh — including table/stat-only boards
    // that have zero Chart.js instances (old charts.length check forced a flash).
    if (!forceFull && state.panelMeta === sig) {
      if (updateInPlace(data)) return;
      // Charts/DOM missing after a partial destroy — fall through to full render.
    }
    fullRender(data, Boolean(forceFull || !state.panelMeta));
  } catch (err) {
    // Recover from Chart.js / render failures (e.g. prior recursive legend bug)
    destroyCharts();
    state.panelMeta = null;
    throw err;
  }
}

export function showSetup() {
  const { titleEl, descEl, panelsEl } = getDom();
  destroyCharts();
  state.panelMeta = null;
  titleEl.textContent = "Connect an appliance";
  descEl.textContent = "Add a CipherTrust Manager host with username and password to start collecting metrics.";
  panelsEl.innerHTML = `
    <div class="empty">
      <p>No CipherTrust Manager appliances configured.</p>
      <p style="margin-top:12px"><button type="button" class="btn btn-primary" id="btn-empty-add">Add appliance</button></p>
    </div>`;
  document.getElementById("btn-empty-add")?.addEventListener("click", openModal);
}

function dashboardTitleHint(id) {
  for (const g of getDashboardGroups()) {
    const hit = (g.dashboards || []).find((d) => d.id === id);
    if (hit) return hit.title || id;
  }
  return id;
}

/** Clear previous panels immediately so tab switches don't leave stale charts on screen. */
export function showDashboardLoading(id) {
  const { panelsEl, titleEl, descEl } = getDom();
  if (!panelsEl) return;
  destroyCharts();
  state.panelMeta = null;
  const title = dashboardTitleHint(id);
  if (titleEl) titleEl.textContent = title;
  if (descEl) descEl.textContent = "Loading...";
  panelsEl.innerHTML = `
    <div class="dash-loading" role="status" aria-live="polite" aria-busy="true">
      <span class="dash-loading-spinner" aria-hidden="true"></span>
      <span class="dash-loading-text">Loading ${escapeHtml(title)}...</span>
    </div>`;
}

export async function loadDashboard(id, { forceFull = false } = {}) {
  const { panelsEl } = getDom();
  if (state.viewMode === "appliances") return;
  if (state.viewMode === "healthcheck") return;
  const seq = ++state.loadSeq;
  state.dashboardId = id;
  state.groupId = groupForDashboard(id);
  syncTabChrome();
  // Tab / range switches: drop old panels right away (don't wait for the API).
  if (forceFull) {
    showDashboardLoading(id);
  }
  if (!state.applianceId) {
    if (seq === state.loadSeq) showSetup();
    return;
  }
  const applianceId = state.applianceId;
  try {
    const data = await fetchJSON(
      `/api/dashboards/${id}?appliance_id=${applianceId}&range=${encodeURIComponent(state.rangeId)}`
    );
    if (seq !== state.loadSeq) return;
    if (state.dashboardId !== id || state.applianceId !== applianceId) return;
    if (state.viewMode === "appliances") return;
    applyDashboard(data, forceFull);
  } catch (err) {
    if (seq !== state.loadSeq) return;
    if (err.payload?.needs_setup) {
      showSetup();
      return;
    }
    destroyCharts();
    panelsEl.innerHTML = `<div class="empty">Failed to load dashboard: ${escapeHtml(err.message)}</div>`;
    state.panelMeta = null;
  }
}

export async function tick({ forceFull = false, scrape = false } = {}) {
  // Don't drop auto ticks while a slow load is in flight — queue one follow-up.
  if (state.loading) {
    const prev = state.tickPending || { forceFull: false, scrape: false };
    state.tickPending = {
      forceFull: Boolean(forceFull || prev.forceFull),
      scrape: Boolean(scrape || prev.scrape),
    };
    return;
  }
  state.loading = true;
  try {
    // Manual Refresh / explicit scrape only — Auto relies on the background
    // scraper (SCRAPE_INTERVAL) so UI + loop don't race the same appliance.
    if (scrape && state.applianceId && state.viewMode === "dashboard") {
      await fetchJSON(`/api/appliances/${state.applianceId}/scrape?force=1`, {
        method: "POST",
      }).catch(() => null);
    }
    await loadAppliances({ force: forceFull });
    await refreshStatus();
    if (state.viewMode === "dashboard") {
      // Auto: in-place value updates (no full DOM rebuild / flash).
      // Manual Refresh / tab changes pass forceFull: true when needed.
      await loadDashboard(state.dashboardId, { forceFull });
    } else if (state.viewMode === "appliances") {
      await renderFleetHealth();
    }
    // healthcheck view refreshes via its own poll while running; Auto tick is a no-op there.
  } finally {
    state.loading = false;
    if (state.tickPending) {
      const pending = state.tickPending;
      state.tickPending = null;
      void tick(pending);
    }
  }
}

export function schedule() {
  const { autoRefresh } = getDom();
  if (state.timer) clearInterval(state.timer);
  if (autoRefresh.checked) {
    // UI poll only (no scrape) — matches background SCRAPE_INTERVAL (default 60s).
    // forceFull: false → updateInPlace when panel layout is unchanged.
    state.timer = setInterval(
      () => tick({ forceFull: false, scrape: false }),
      window.CM_METRICS.scrapeInterval || 60000
    );
  }
}
