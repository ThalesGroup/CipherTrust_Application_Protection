import { state, getDom } from "./state.js";
import {
  applyChartDefaults,
  syncThemeButton,
  setTheme,
  currentTheme,
} from "./theme.js";
import { fetchJSON, refreshStatus } from "./api.js";
import {
  setDashboardLoader,
  setDashboardChrome,
  openModal,
  closeModal,
  closeEditModal,
  submitEditForm,
  setApplianceMenuOpen,
  renderApplianceMenu,
  renderApplianceList,
  selectAppliance,
  showAppliancesTab,
  loadAppliances,
  handleApplianceAction,
  renderFleetHealth,
  pollDeleteNotifications,
} from "./appliances.js";
import {
  showHealthcheckTab,
  stopHealthcheckPoll,
  refreshHealthcheckStatus,
  syncHealthcheckReportTheme,
} from "./healthcheck.js";
import {
  groupForDashboard,
  persistTabChip,
  destroyCharts,
  syncWorkspaceChrome,
  showDashboardGroup,
  loadDashboard,
  setTimeRange,
  syncRangePicker,
  tick,
  schedule,
} from "./dashboard.js";

const dom = getDom();
const {
  primaryTabs,
  secondaryChips,
  btnApplianceCurrent,
  applianceMenu,
  applianceSelector,
  applianceTree,
  modal,
  form,
  formError,
  btnConnect,
  btnRefresh,
  autoRefresh,
  statusText,
} = dom;

setDashboardLoader(loadDashboard);
setDashboardChrome({ destroyCharts, syncWorkspaceChrome });

applyChartDefaults();
syncThemeButton();
state.groupId = groupForDashboard(state.dashboardId);

document.getElementById("btn-theme")?.addEventListener("click", () => {
  setTheme(currentTheme() === "light" ? "dark" : "light", {
    onRefreshCharts: () => {
      if (state.viewMode === "dashboard") {
        loadDashboard(state.dashboardId, { forceFull: true });
      } else if (state.viewMode === "appliances") {
        renderFleetHealth();
      } else if (state.viewMode === "healthcheck") {
        syncHealthcheckReportTheme();
      }
    },
  });
});

primaryTabs?.addEventListener("click", (e) => {
  const btn = e.target.closest(".primary-tab");
  if (!btn) return;
  const groupId = btn.dataset.group;
  if (!groupId) return;
  if (groupId === "appliances") {
    if (state.viewMode === "appliances") return;
    stopHealthcheckPoll();
    showAppliancesTab();
    return;
  }
  if (groupId === "healthcheck") {
    if (state.viewMode === "healthcheck") return;
    destroyCharts();
    showHealthcheckTab();
    syncWorkspaceChrome();
    return;
  }
  if (state.viewMode === "dashboard" && groupId === state.groupId) return;
  stopHealthcheckPoll();
  showDashboardGroup(groupId);
});

secondaryChips?.addEventListener("click", (e) => {
  const btn = e.target.closest(".secondary-chip");
  if (!btn) return;
  const id = btn.dataset.id;
  if (!id || id === state.dashboardId) return;
  persistTabChip(state.groupId, id);
  state.panelMeta = null;
  loadDashboard(id, { forceFull: true });
});

document.getElementById("range-picker")?.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-range]");
  if (!btn) return;
  const rangeId = btn.dataset.range;
  if (!rangeId || rangeId === state.rangeId) return;
  setTimeRange(rangeId, { reload: true });
});

document.getElementById("fleet-range-picker")?.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-range]");
  if (!btn) return;
  const rangeId = btn.dataset.range;
  if (!rangeId || rangeId === state.rangeId) return;
  setTimeRange(rangeId, { reload: true });
});

btnApplianceCurrent?.addEventListener("click", (e) => {
  e.stopPropagation();
  if (!state.menuOpen) renderApplianceMenu();
  setApplianceMenuOpen(!state.menuOpen);
});

applianceMenu?.addEventListener("click", async (e) => {
  const link = e.target.closest("[data-action='open-appliances']");
  if (link) {
    e.preventDefault();
    setApplianceMenuOpen(false);
    showAppliancesTab();
    return;
  }
  const item = e.target.closest(".appliance-menu-item");
  if (!item) return;
  await selectAppliance(item.dataset.id);
});

document.addEventListener("click", (e) => {
  if (!state.menuOpen) return;
  if (applianceSelector?.contains(e.target)) return;
  setApplianceMenuOpen(false);
});

document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  if (state.menuOpen) setApplianceMenuOpen(false);
  if (editModal && !editModal.hidden) closeEditModal();
});

applianceTree?.addEventListener("click", async (e) => {
  if (await handleApplianceAction(e)) return;
  const select = e.target.closest(".tree-node-select, .tree-node");
  if (!select || e.target.closest(".tree-node-actions, .appliance-edit, .appliance-delete, .appliance-retry")) return;
  const node = select.closest(".tree-node") || select;
  const id = Number(node.dataset.id);
  if (!id) return;
  state.applianceId = id;
  state.panelMeta = null;
  setApplianceMenuOpen(false);
  renderApplianceList(true);
  // Open Overview for the selected node (leave Appliances fleet view).
  showDashboardGroup("overview");
  refreshStatus();
});

document.getElementById("btn-add")?.addEventListener("click", openModal);
document.getElementById("btn-add-tree")?.addEventListener("click", openModal);
document.getElementById("btn-cancel").addEventListener("click", closeModal);
modal.addEventListener("click", (e) => {
  if (e.target === modal) closeModal();
});

const editModal = document.getElementById("edit-modal");
const editForm = document.getElementById("edit-form");
document.getElementById("btn-edit-cancel")?.addEventListener("click", closeEditModal);
editModal?.addEventListener("click", (e) => {
  if (e.target === editModal) closeEditModal();
});
editForm?.addEventListener("submit", (e) => {
  submitEditForm(e);
});

/** Build https://host[:port] for CM connect. Empty port → default 443. */
function buildCmHost(rawHost, rawPort) {
  let host = String(rawHost || "").trim();
  if (!host) return "";
  const portStr = String(rawPort ?? "").trim();
  if (portStr) {
    const port = Number(portStr);
    if (!Number.isInteger(port) || port < 1 || port > 65535) {
      throw new Error("HTTPS port must be an integer between 1 and 65535.");
    }
    // If the host already includes a port (or full URL), replace/keep via URL parse.
    const withScheme = host.includes("://") ? host : `https://${host}`;
    try {
      const u = new URL(withScheme);
      if (port === 443) {
        u.port = "";
      } else {
        u.port = String(port);
      }
      // Prefer https for CM unless user explicitly typed http://
      if (!host.includes("://")) {
        u.protocol = "https:";
      }
      host = u.toString().replace(/\/$/, "");
    } catch {
      throw new Error("Invalid IP / hostname / URL.");
    }
  }
  return host;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.hidden = true;
  btnConnect.disabled = true;
  btnConnect.textContent = "Connecting…";
  const stillHint = window.setTimeout(() => {
    if (btnConnect.disabled) {
      btnConnect.textContent = "Still connecting… (large DB purge may slow this)";
    }
  }, 12000);
  const fd = new FormData(form);
  let host;
  try {
    host = buildCmHost(fd.get("host"), fd.get("port"));
  } catch (err) {
    window.clearTimeout(stillHint);
    btnConnect.disabled = false;
    btnConnect.textContent = "Connect";
    formError.hidden = false;
    formError.textContent = err.message || String(err);
    return;
  }
  const body = {
    host,
    username: fd.get("username"),
    password: fd.get("password"),
    display_name: fd.get("display_name") || undefined,
    location: fd.get("location") || undefined,
    discover_cluster: fd.get("discover_cluster") === "on",
  };
  try {
    const result = await fetchJSON("/api/appliances", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    form.reset();
    closeModal();
    state.panelMeta = null;
    await loadAppliances();
    state.applianceId = result.appliance?.id || state.applianceId;
    renderApplianceList(true);
    if (state.viewMode === "dashboard") {
      await loadDashboard(state.dashboardId, { forceFull: true });
    } else {
      showAppliancesTab();
    }
    await refreshStatus();
    if (result.auto_added?.length) {
      statusText.textContent = `added + ${result.auto_added.length} peer(s)`;
    }
  } catch (err) {
    formError.hidden = false;
    const payload = err.payload || {};
    if (payload.code === "prometheus_permission" || /cannot enable prometheus/i.test(err.message || "")) {
      formError.textContent =
        payload.error ||
        "This account cannot enable Prometheus metrics. Ask an admin to enable it under Admin Settings > Metrics, then re-add the appliance.";
    } else {
      formError.textContent = err.message || "Connection failed";
    }
  } finally {
    window.clearTimeout(stillHint);
    btnConnect.disabled = false;
    btnConnect.textContent = "Connect";
  }
});

function setRefreshButtonBusy(busy) {
  const { btnRefresh } = getDom();
  if (!btnRefresh) return;
  btnRefresh.disabled = busy;
  btnRefresh.textContent = busy ? "Refreshing..." : "Refresh";
  btnRefresh.classList.toggle("is-refreshing", busy);
}

let refreshPollTimer = null;

async function pollForceRefreshUntilDone() {
  setRefreshButtonBusy(true);
  if (refreshPollTimer) {
    clearInterval(refreshPollTimer);
    refreshPollTimer = null;
  }

  const pollOnce = async () => {
    try {
      const st = await fetchJSON("/api/scrape/status");
      await loadAppliances({ force: true }).catch(() => null);
      if (state.viewMode === "appliances") {
        await renderFleetHealth().catch(() => null);
      } else if (state.viewMode === "dashboard" && state.applianceId) {
        await loadDashboard(state.dashboardId, { forceFull: false }).catch(() => null);
      }
      await refreshStatus().catch(() => null);
      if (!st?.running) {
        if (refreshPollTimer) {
          clearInterval(refreshPollTimer);
          refreshPollTimer = null;
        }
        setRefreshButtonBusy(false);
        // Final full paint so badges/uptime settle.
        await tick({ forceFull: true, scrape: false }).catch(() => null);
        return true;
      }
    } catch (err) {
      console.warn("Refresh poll failed:", err);
    }
    return false;
  };

  const done = await pollOnce();
  if (done) return;
  refreshPollTimer = setInterval(() => {
    void pollOnce();
  }, 1500);
}

btnRefresh.addEventListener("click", async () => {
  try {
    if (state.viewMode === "healthcheck") {
      setRefreshButtonBusy(true);
      await refreshHealthcheckStatus();
      setRefreshButtonBusy(false);
      return;
    }
    // Fire-and-forget on the server — survives tab switches and browser reload.
    await fetchJSON("/api/scrape?force=1", { method: "POST" });
    await pollForceRefreshUntilDone();
  } catch (err) {
    console.warn("Refresh scrape failed:", err);
    setRefreshButtonBusy(false);
    await tick({ forceFull: true, scrape: false }).catch(() => null);
  }
});

autoRefresh.addEventListener("change", schedule);

showAppliancesTab();
syncRangePicker();
loadAppliances()
  .then((list) => {
    if (!list.length) openModal();
  })
  .then(() => tick({ forceFull: true, scrape: false }))
  .then(schedule)
  .then(async () => {
    // Resume Refresh UI if a server-side force scrape is still running after reload.
    try {
      const st = await fetchJSON("/api/scrape/status");
      if (st?.running) await pollForceRefreshUntilDone();
    } catch (_) {
      /* ignore */
    }
    await pollDeleteNotifications();
    window.setInterval(() => {
      void pollDeleteNotifications();
    }, 12000);
  });

