import { escapeHtml, appliancesSignature, tsLabel, formatCmUptime } from "./format.js";
import { fetchJSON, refreshStatus } from "./api.js";
import { state, getDom } from "./state.js";
import { cssVar } from "./theme.js";
import { RANGE_OPTIONS } from "./config.js";

let loadDashboard = async () => {};
let destroyCharts = () => {};
let syncWorkspaceChrome = () => {};

/** Inject dashboard helpers from main to avoid circular imports. */
export function setDashboardLoader(fn) {
  if (typeof fn === "function") loadDashboard = fn;
}

export function setDashboardChrome({ destroyCharts: dc, syncWorkspaceChrome: swc } = {}) {
  if (typeof dc === "function") destroyCharts = dc;
  if (typeof swc === "function") syncWorkspaceChrome = swc;
}

export function openModal() {
  const { modal, formError, form } = getDom();
  modal.hidden = false;
  formError.hidden = true;
  formError.textContent = "";
  form.querySelector("input[name=host]")?.focus();
}

export function closeModal() {
  getDom().modal.hidden = true;
}

export function openEditModal(appliance, target = "appliance") {
  const {
    editModal,
    editForm,
    editFormError,
    editModalTitle,
    editModalSub,
    editNameLabel,
    editLocationWrap,
  } = getDom();
  if (!editModal || !editForm || !appliance) return;
  const shortHost = shortHostOf(appliance);
  const isCluster = target === "cluster";
  if (editModalTitle) {
    editModalTitle.textContent = isCluster ? "Edit cluster" : "Edit appliance";
  }
  if (editModalSub) {
    editModalSub.textContent = isCluster
      ? "Update the cluster display name."
      : "Update the display name and location.";
  }
  if (editNameLabel) {
    const input = editNameLabel.querySelector("input");
    // Keep the input; rewrite only the label text node before it.
    editNameLabel.childNodes[0].textContent = isCluster ? "Cluster name " : "Display name ";
    if (input) {
      input.name = isCluster ? "cluster_display_name" : "display_name";
      input.placeholder = isCluster ? "Prod Cluster" : "Prod CM";
      input.value = isCluster
        ? clusterTitle(appliance)
        : (appliance.display_name || shortHost || "");
    }
  }
  if (editLocationWrap) {
    editLocationWrap.hidden = isCluster;
    const locInput = editLocationWrap.querySelector("input[name=location]");
    if (locInput) locInput.value = appliance.location || "";
  }
  editForm.querySelector("input[name=appliance_id]").value = String(appliance.id);
  editForm.querySelector("input[name=edit_target]").value = target;
  if (editFormError) {
    editFormError.hidden = true;
    editFormError.textContent = "";
  }
  editModal.hidden = false;
  editForm.querySelector("input[name=display_name], input[name=cluster_display_name]")?.focus();
}

export function closeEditModal() {
  const { editModal } = getDom();
  if (editModal) editModal.hidden = true;
}

export function groupAppliances(list) {
  const byId = new Map((list || []).map((a) => [a.id, a]));
  const children = new Map();
  const roots = [];
  (list || []).forEach((a) => {
    const parentId = a.parent_appliance_id != null ? Number(a.parent_appliance_id) : null;
    if (parentId && byId.has(parentId) && parentId !== a.id) {
      if (!children.has(parentId)) children.set(parentId, []);
      children.get(parentId).push(a);
    } else {
      roots.push(a);
    }
  });
  children.forEach((arr, parentId) => {
    const parent = byId.get(parentId);
    // Include primary as first node under the cluster heading
    const nodes = parent ? [parent, ...arr] : arr.slice();
    nodes.sort((x, y) => {
      const xr = x.cluster_role === "primary" || x.id === parentId ? 0 : 1;
      const yr = y.cluster_role === "primary" || y.id === parentId ? 0 : 1;
      if (xr !== yr) return xr - yr;
      return String(x.host || "").localeCompare(String(y.host || ""));
    });
    children.set(parentId, nodes.filter((n, i, all) => all.findIndex((x) => x.id === n.id) === i));
  });
  return { roots, children, byId };
}

export function shortHostOf(a) {
  return (a.host || "").replace(/^https?:\/\//, "");
}

function networkMetaHtml(a) {
  const hostname = (a.cm_hostname || a.cm_name || "").trim();
  const publicIp = (a.public_host || "").trim();
  const privateIp = (a.private_host || "").trim();
  const location = (a.location || "").trim();
  const rows = [];
  if (hostname) {
    rows.push(`<span class="tree-meta-row"><span class="tree-meta-label">CM hostname</span><span class="tree-meta-value">${escapeHtml(hostname)}</span></span>`);
  }
  if (publicIp) {
    rows.push(`<span class="tree-meta-row"><span class="tree-meta-label">Public IP</span><span class="tree-meta-value">${escapeHtml(publicIp)}</span></span>`);
  }
  if (privateIp) {
    rows.push(`<span class="tree-meta-row"><span class="tree-meta-label">Private IP</span><span class="tree-meta-value">${escapeHtml(privateIp)}</span></span>`);
  }
  if (location) {
    rows.push(`<span class="tree-meta-row"><span class="tree-meta-label">Location</span><span class="tree-meta-value">${escapeHtml(location)}</span></span>`);
  }
  if (!rows.length) {
    rows.push(`<span class="tree-meta-row"><span class="tree-meta-label">Connect</span><span class="tree-meta-value">${escapeHtml(shortHostOf(a))}</span></span>`);
  }
  return `<span class="tree-node-meta">${rows.join("")}</span>`;
}

export function clusterTitle(primary) {
  const clusterName = (primary.cluster_display_name || "").trim();
  if (clusterName) return clusterName;
  const name = (primary.display_name || "").trim();
  // Legacy: older data stored the cluster title in display_name
  if (name && !/^Node\s+\d+$/i.test(name)) return name;
  return `Cluster · ${shortHostOf(primary)}`;
}

export function nodeLabel(a, index, { isPrimary = false } = {}) {
  const name = (a.display_name || "").trim();
  if (/^Node\s+\d+$/i.test(name)) return name;
  if (name) return name;
  return `Node ${index}`;
}

export function applianceStatusBadge(a) {
  if (a.last_status === "ok") return { cls: "ok", text: "online" };
  if (a.last_status === "offline") return { cls: "offline", text: "offline" };
  if (a.last_status === "error") return { cls: "err", text: "error" };
  if (a.last_status === "delete_failed") return { cls: "err", text: "delete failed" };
  if (a.last_status === "pending") return { cls: "", text: "retrying" };
  return { cls: "", text: a.last_status || "pending" };
}

function nodeActionsHtml(a, { editTarget = "appliance", label = "" } = {}) {
  const offline = a.last_status === "offline";
  const syncTitle = offline ? "Retry contact" : "Sync this appliance";
  const syncLabel = offline ? `Retry ${label}` : `Sync ${label}`;
  const syncing = state.syncingApplianceIds?.has(a.id);
  return `
    <span class="tree-node-actions">
      <button type="button" class="appliance-retry${syncing ? " is-syncing" : ""}" data-id="${a.id}" title="${escapeHtml(syncTitle)}" aria-label="${escapeHtml(syncLabel)}"${syncing ? " disabled" : ""}>
        <svg class="icon-retry" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" focusable="false">
          <path fill="currentColor" d="M12 6V3L8 7l4 4V8c2.76 0 5 2.24 5 5a5 5 0 0 1-9.9 1H5.08A7 7 0 0 0 19 13c0-3.87-3.13-7-7-7z"/>
        </svg>
      </button>
      <button type="button" class="appliance-edit" data-id="${a.id}" data-edit-target="${editTarget}" title="Edit" aria-label="Edit ${escapeHtml(label)}">
        <svg class="icon-pencil" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" focusable="false">
          <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1.003 1.003 0 0 0 0-1.42l-2.34-2.34a1.003 1.003 0 0 0-1.42 0l-1.83 1.83 3.75 3.75 1.84-1.82z"/>
        </svg>
      </button>
      <button type="button" class="appliance-delete" data-id="${a.id}" title="Remove appliance" aria-label="Remove ${escapeHtml(label)}">
        <svg class="icon-trash" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" focusable="false">
          <path fill="currentColor" d="M9 3h6l1 2h4v2H4V5h4l1-2zm1 6h2v9h-2V9zm4 0h2v9h-2V9zM7 9h2v9H7V9zm-1 12h12a1 1 0 0 0 1-1V8H5v12a1 1 0 0 0 1 1z"/>
        </svg>
      </button>
    </span>`;
}

function treeNodeHtml(a, { nodeIndex = null, isPrimary = false, nested = false } = {}) {
  const active = a.id === state.applianceId ? " active" : "";
  const badge = applianceStatusBadge(a);
  const shortHost = shortHostOf(a);
  const label =
    nested && nodeIndex != null
      ? nodeLabel(a, nodeIndex, { isPrimary })
      : a.display_name || shortHost;
  const offline = a.last_status === "offline";
  const role =
    isPrimary || a.cluster_role === "primary"
      ? "primary"
      : nested
        ? "member"
        : "";
  const uptime =
    a.last_status === "ok" ? formatCmUptime(a.cm_uptime) : "";
  return `
    <div class="tree-node${active}${offline ? " is-offline" : ""}" data-id="${a.id}" role="treeitem" aria-selected="${a.id === state.applianceId}">
      <button type="button" class="tree-node-select" data-id="${a.id}" title="${escapeHtml(`${label} · ${shortHost}${uptime ? ` · up ${uptime}` : ""}`)}">
        <span class="tree-node-status ${badge.cls}" aria-hidden="true"></span>
        <span class="tree-node-body">
          <span class="tree-node-top">
            <span class="tree-node-name">${escapeHtml(label)}</span>
            ${role ? `<span class="tree-node-role">${role}</span>` : ""}
            ${uptime ? `<span class="tree-node-uptime" title="Uptime">${escapeHtml(uptime)}</span>` : ""}
          </span>
          ${networkMetaHtml(a)}
        </span>
        <span class="tree-node-badge ${badge.cls}">${escapeHtml(badge.text)}</span>
      </button>
      ${nodeActionsHtml(a, { editTarget: nested ? "node" : "appliance", label })}
    </div>`;
}

function clusterIconSvg() {
  return `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false">
    <path fill="currentColor" d="M12 2a3 3 0 0 1 3 3v1.1a7 7 0 0 1 3.9 3.9H20a3 3 0 1 1 0 6h-1.1a7 7 0 0 1-3.9 3.9V20a3 3 0 1 1-6 0v-1.1A7 7 0 0 1 5.1 15H4a3 3 0 1 1 0-6h1.1A7 7 0 0 1 9 5.1V5a3 3 0 0 1 3-3zm0 6a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/>
  </svg>`;
}

export function setApplianceMenuOpen(open) {
  const { btnApplianceCurrent, applianceMenu } = getDom();
  state.menuOpen = !!open;
  if (btnApplianceCurrent) btnApplianceCurrent.setAttribute("aria-expanded", state.menuOpen ? "true" : "false");
  if (applianceMenu) applianceMenu.hidden = !state.menuOpen;
}

export function currentAppliance() {
  return state.appliances.find((a) => a.id === state.applianceId) || null;
}

export function renderCurrentSelector() {
  const { btnApplianceCurrent, applianceCurrentLabel, applianceCurrentMeta } = getDom();
  if (!btnApplianceCurrent) return;
  const a = currentAppliance();
  const dot = btnApplianceCurrent.querySelector(".appliance-current-dot");
  if (!a) {
    if (applianceCurrentLabel) applianceCurrentLabel.textContent = "No appliance";
    if (applianceCurrentMeta) applianceCurrentMeta.textContent = "Add one to begin";
    if (dot) dot.className = "appliance-current-dot";
    return;
  }
  const badge = applianceStatusBadge(a);
  const shortHost = shortHostOf(a);
  const { roots, children, byId } = groupAppliances(state.appliances);
  let clusterHint = "";
  const parentId = a.parent_appliance_id != null ? Number(a.parent_appliance_id) : null;
  if (parentId && byId.has(parentId)) {
    clusterHint = clusterTitle(byId.get(parentId));
  } else if ((children.get(a.id) || []).length || a.is_clustered || a.cluster_role === "primary") {
    clusterHint = clusterTitle(a);
  }
  const label = a.display_name || shortHost;
  if (applianceCurrentLabel) applianceCurrentLabel.textContent = label;
  if (applianceCurrentMeta) {
    applianceCurrentMeta.textContent = clusterHint
      ? `${clusterHint} · ${shortHost}`
      : shortHost;
  }
  if (dot) dot.className = `appliance-current-dot ${badge.cls}`;
}

function menuItemHtml(a, { nested = false, nodeIndex = null, isPrimary = false } = {}) {
  const badge = applianceStatusBadge(a);
  const shortHost = shortHostOf(a);
  const label =
    nested && nodeIndex != null
      ? nodeLabel(a, nodeIndex, { isPrimary })
      : a.display_name || shortHost;
  const active = a.id === state.applianceId ? " active" : "";
  const role =
    isPrimary || a.cluster_role === "primary"
      ? "primary"
      : nested
        ? "node"
        : "";
  return `
    <button type="button" class="appliance-menu-item${active}${nested ? " nested" : ""}" data-id="${a.id}" role="option" aria-selected="${a.id === state.applianceId}">
      <span class="menu-dot ${badge.cls}" aria-hidden="true"></span>
      <span class="menu-text">
        <span class="menu-name">${escapeHtml(label)}</span>
        <span class="menu-host">${escapeHtml(shortHost)}</span>
      </span>
      ${role ? `<span class="menu-role">${role}</span>` : ""}
    </button>`;
}

export function renderApplianceMenu() {
  const { applianceMenu } = getDom();
  if (!applianceMenu) return;
  if (!state.appliances.length) {
    applianceMenu.innerHTML = `
      <div class="appliance-menu-empty">No appliances yet.</div>
      <div class="appliance-menu-footer">
        <button type="button" class="appliance-menu-link" data-action="open-appliances">Open Appliances tab</button>
      </div>`;
    return;
  }
  const { roots, children } = groupAppliances(state.appliances);
  const sections = roots
    .map((root) => {
      const members = children.get(root.id) || [];
      const isCluster = root.is_clustered || members.length > 1 || root.cluster_role === "primary";
      if (!isCluster || members.length === 0) {
        if (isCluster && members.length === 0) {
          return `
            <div class="appliance-menu-section">
              <div class="appliance-menu-heading">${escapeHtml(clusterTitle(root))}</div>
              ${menuItemHtml(root, { nested: true, nodeIndex: 1, isPrimary: true })}
            </div>`;
        }
        return `<div class="appliance-menu-section">${menuItemHtml(root)}</div>`;
      }
      return `
        <div class="appliance-menu-section">
          <div class="appliance-menu-heading">${escapeHtml(clusterTitle(root))}</div>
          ${members
            .map((m, i) =>
              menuItemHtml(m, {
                nested: true,
                nodeIndex: i + 1,
                isPrimary: m.id === root.id,
              })
            )
            .join("")}
        </div>`;
    })
    .join("");
  applianceMenu.innerHTML = `
    ${sections}
    <div class="appliance-menu-footer">
      <button type="button" class="appliance-menu-link" data-action="open-appliances">Manage in Appliances tab</button>
    </div>`;
}

function clusterHeadHtml(root, nodeCount) {
  return `
    <div class="tree-cluster-head">
      <div class="tree-cluster-mark">${clusterIconSvg()}</div>
      <div class="tree-cluster-meta">
        <div class="tree-cluster-kicker">Cluster</div>
        <div class="tree-cluster-name" title="${escapeHtml(clusterTitle(root))}">${escapeHtml(clusterTitle(root))}</div>
        <div class="tree-cluster-count">${nodeCount} node${nodeCount === 1 ? "" : "s"}</div>
      </div>
      <div class="tree-cluster-actions">
        <button type="button" class="appliance-edit" data-id="${root.id}" data-edit-target="cluster" title="Edit cluster" aria-label="Edit cluster">
          <svg class="icon-pencil" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" focusable="false">
            <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1.003 1.003 0 0 0 0-1.42l-2.34-2.34a1.003 1.003 0 0 0-1.42 0l-1.83 1.83 3.75 3.75 1.84-1.82z"/>
          </svg>
        </button>
      </div>
    </div>`;
}

function treeBranchHtml(nodes, rootId) {
  return `
    <ul class="tree-diagram" role="group">
      ${nodes
        .map((m, i) => {
          const last = i === nodes.length - 1;
          return `
            <li class="tree-diagram-item${last ? " is-last" : ""}">
              <span class="tree-diagram-guide" aria-hidden="true">
                <span class="tree-diagram-rail"></span>
                <span class="tree-diagram-elbow"></span>
              </span>
              ${treeNodeHtml(m, {
                nested: true,
                nodeIndex: i + 1,
                isPrimary: m.id === rootId || m.cluster_role === "primary",
              })}
            </li>`;
        })
        .join("")}
    </ul>`;
}

function destroyFleetHealthChart() {
  if (state.fleetHealthChart) {
    try { state.fleetHealthChart.destroy(); } catch (_) { /* ignore */ }
    state.fleetHealthChart = null;
  }
}

function fleetXBounds() {
  const secs = RANGE_OPTIONS.find((r) => r.id === state.rangeId)?.seconds || 86400;
  const max = Date.now();
  return { min: max - secs * 1000, max };
}

function fleetGridColor() {
  // Soft horizontal guides only — avoid the dense Excel-like lattice.
  const isLight = document.documentElement.getAttribute("data-theme") === "light";
  return isLight ? "rgba(15, 23, 42, 0.06)" : "rgba(148, 163, 184, 0.10)";
}

function fleetTooltipStyle() {
  // Explicit pairs so Online/Offline labels stay high-contrast in both themes.
  // (Do not use --muted for body text, and do not reference --panel — it does not exist.)
  const isLight = document.documentElement.getAttribute("data-theme") === "light";
  if (isLight) {
    return {
      backgroundColor: "#ffffff",
      titleColor: "#152033",
      bodyColor: "#152033",
      borderColor: "#d5dee8",
      borderWidth: 1,
      padding: 10,
      displayColors: true,
      multiKeyBackground: "#ffffff",
    };
  }
  return {
    backgroundColor: "#1a2740",
    titleColor: "#e8eef9",
    bodyColor: "#e8eef9",
    borderColor: "#3a4d6b",
    borderWidth: 1,
    padding: 10,
    displayColors: true,
    multiKeyBackground: "#1a2740",
  };
}

function paintFleetHealthChart(points) {
  const { fleetHealthChart: canvas } = getDom();
  if (!canvas || typeof Chart === "undefined") return;
  const okColor = cssVar("--ok", "#34d399");
  const offColor = cssVar("--danger", "#f87171");
  const muted = cssVar("--muted", "#8b9bb8");
  const tip = fleetTooltipStyle();
  const xBounds = fleetXBounds();
  const online = (points || []).map((p) => ({ x: p.t * 1000, y: p.online }));
  const offline = (points || []).map((p) => ({ x: p.t * 1000, y: p.offline }));
  const datasets = [
    {
      label: "Online",
      data: online,
      borderColor: okColor,
      backgroundColor: okColor + "28",
      borderWidth: 2.25,
      pointRadius: 0,
      pointHoverRadius: 3,
      tension: 0.35,
      fill: "origin",
      order: 2,
    },
    {
      label: "Offline",
      data: offline,
      borderColor: offColor,
      backgroundColor: offColor + "18",
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 3,
      tension: 0.35,
      fill: "origin",
      order: 1,
    },
  ];

  const scaleOpts = {
    x: {
      type: "linear",
      min: xBounds.min,
      max: xBounds.max,
      ticks: {
        color: muted,
        callback: (v) => tsLabel(v / 1000, state.rangeId),
        autoSkip: true,
        maxTicksLimit: 5,
        maxRotation: 0,
        padding: 8,
        font: { size: 10 },
      },
      grid: { display: false, drawBorder: false, drawTicks: false },
      border: { display: false },
    },
    y: {
      beginAtZero: true,
      grace: "8%",
      ticks: {
        color: muted,
        precision: 0,
        stepSize: 1,
        maxTicksLimit: 5,
        padding: 10,
        font: { size: 10 },
      },
      grid: {
        color: fleetGridColor(),
        lineWidth: 1,
        drawBorder: false,
        drawTicks: false,
      },
      border: { display: false },
    },
  };

  // Always recreate so theme switches (dark ↔ light) fully refresh tooltip colors.
  destroyFleetHealthChart();
  state.fleetHealthChart = new Chart(canvas, {
    type: "line",
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      parsing: false,
      layout: { padding: { top: 6, right: 10, bottom: 2, left: 2 } },
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          display: true,
          position: "bottom",
          align: "start",
          labels: {
            boxWidth: 8,
            boxHeight: 8,
            usePointStyle: true,
            pointStyle: "circle",
            padding: 14,
            font: { size: 11 },
            color: muted,
          },
        },
        tooltip: {
          ...tip,
          callbacks: {
            title: (items) => {
              const x = items[0]?.parsed?.x;
              return x == null ? "" : new Date(x).toLocaleString();
            },
            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y}`,
            labelTextColor: () => tip.bodyColor,
          },
        },
      },
      scales: scaleOpts,
    },
  });
}

export async function renderFleetHealth() {
  const { fleetHealth, fleetHealthSummary } = getDom();
  if (!fleetHealth) return;
  if (state.viewMode !== "appliances") {
    fleetHealth.hidden = true;
    destroyFleetHealthChart();
    return;
  }
  fleetHealth.hidden = false;
  try {
    const data = await fetchJSON(
      `/api/fleet-health?range=${encodeURIComponent(state.rangeId)}`
    );
    if (state.viewMode !== "appliances") return;
    const latest = data.latest || {};
    const online = latest.online ?? 0;
    const offline = latest.offline ?? 0;
    const total = latest.total ?? online + offline;
    if (fleetHealthSummary) {
      fleetHealthSummary.textContent =
        `${online} online · ${offline} offline · ${total} total · last ${data.range || state.rangeId}`;
    }
    paintFleetHealthChart(data.points || []);
  } catch (_) {
    if (fleetHealthSummary) {
      fleetHealthSummary.textContent = "Could not load fleet health history";
    }
  }
}

export function renderApplianceTree() {
  const { applianceTree } = getDom();
  if (!applianceTree) return;
  if (!state.appliances.length) {
    applianceTree.innerHTML = `<div class="tree-empty">No appliances yet — click <strong>Add appliance</strong> to connect a CipherTrust Manager.</div>`;
    renderFleetHealth();
    return;
  }
  const { roots, children } = groupAppliances(state.appliances);
  applianceTree.innerHTML = roots
    .map((root) => {
      const members = children.get(root.id) || [];
      const isCluster = root.is_clustered || members.length > 0 || root.cluster_role === "primary";
      if (!isCluster) {
        return `<div class="tree-standalone">${treeNodeHtml(root)}</div>`;
      }
      const nodes = members.length ? members : [root];
      return `
        <div class="tree-cluster" data-parent-id="${root.id}">
          ${clusterHeadHtml(root, nodes.length)}
          ${treeBranchHtml(nodes, root.id)}
        </div>`;
    })
    .join("");
  renderFleetHealth();
}

export function renderApplianceList(force = false) {
  const { applianceTree } = getDom();
  const nextSig = appliancesSignature(state.appliances);
  if (!force && nextSig === state._applianceSig) {
    renderCurrentSelector();
    if (state.viewMode === "appliances") {
      // Lightweight active-state refresh on tree
      applianceTree?.querySelectorAll(".tree-node").forEach((node) => {
        const id = Number(node.dataset.id);
        const a = state.appliances.find((x) => x.id === id);
        if (!a) return;
        node.classList.toggle("active", id === state.applianceId);
        node.classList.toggle("is-offline", a.last_status === "offline");
        node.setAttribute("aria-selected", id === state.applianceId ? "true" : "false");
        const badge = node.querySelector(".tree-node-badge");
        const status = node.querySelector(".tree-node-status");
        const info = applianceStatusBadge(a);
        if (badge) {
          badge.className = `tree-node-badge ${info.cls}`;
          badge.textContent = info.text;
        }
        if (status) status.className = `tree-node-status ${info.cls}`;
      });
      renderFleetHealth();
    }
    if (state.menuOpen) renderApplianceMenu();
    return;
  }
  state._applianceSig = nextSig;
  renderCurrentSelector();
  if (state.menuOpen) renderApplianceMenu();
  if (state.viewMode === "appliances") renderApplianceTree();
}

export async function selectAppliance(id, { load = true } = {}) {
  const next = Number(id);
  if (!next || next === state.applianceId) {
    setApplianceMenuOpen(false);
    return;
  }
  state.applianceId = next;
  state.panelMeta = null;
  setApplianceMenuOpen(false);
  renderApplianceList(true);
  if (load && state.viewMode === "dashboard") {
    await loadDashboard(state.dashboardId, { forceFull: true });
  } else if (load && state.viewMode === "healthcheck") {
    const { refreshHealthcheckStatus } = await import("./healthcheck.js");
    await refreshHealthcheckStatus();
  }
  refreshStatus();
}

export function showAppliancesTab() {
  state.viewMode = "appliances";
  setApplianceMenuOpen(false);
  destroyCharts();
  try {
    import("./healthcheck.js").then((m) => m.hideHealthcheckView?.());
  } catch (_) {
    /* ignore */
  }
  const { panelsEl, healthcheckView } = getDom();
  if (panelsEl) {
    panelsEl.innerHTML = "";
    panelsEl.hidden = true;
  }
  if (healthcheckView) {
    healthcheckView.innerHTML = "";
    healthcheckView.hidden = true;
  }
  state.panelMeta = null;
  syncWorkspaceChrome();
  renderApplianceList(true);
}

export async function loadAppliances({ force = false } = {}) {
  state.appliances = await fetchJSON("/api/appliances");
  if (!state.applianceId && state.appliances.length) {
    state.applianceId = state.appliances[0].id;
  }
  if (state.applianceId && !state.appliances.find((a) => a.id === state.applianceId)) {
    state.applianceId = state.appliances[0]?.id || null;
  }
  // Skip forced tree rebuild on Auto ticks — signature check avoids sidebar flash.
  renderApplianceList(force);
  return state.appliances;
}

export async function submitEditForm(e) {
  e?.preventDefault?.();
  const { editForm, editFormError, btnEditSave } = getDom();
  if (!editForm) return;
  if (editFormError) {
    editFormError.hidden = true;
    editFormError.textContent = "";
  }
  const fd = new FormData(editForm);
  const id = Number(fd.get("appliance_id"));
  const target = String(fd.get("edit_target") || "appliance");
  if (!id) return;
  const body = {};
  if (target === "cluster") {
    body.cluster_display_name = String(fd.get("cluster_display_name") || "").trim();
  } else {
    body.display_name = String(fd.get("display_name") || "").trim();
    body.location = String(fd.get("location") || "").trim();
  }
  if (btnEditSave) {
    btnEditSave.disabled = true;
    btnEditSave.textContent = "Saving…";
  }
  try {
    const updated = await fetchJSON(`/api/appliances/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const idx = state.appliances.findIndex((a) => a.id === id);
    if (idx >= 0) state.appliances[idx] = { ...state.appliances[idx], ...updated };
    state._applianceSig = null;
    closeEditModal();
    renderApplianceList(true);
    await loadAppliances();
    renderApplianceList(true);
    if (state.applianceId && state.viewMode === "dashboard") {
      await loadDashboard(state.dashboardId, { forceFull: true });
    }
  } catch (err) {
    if (editFormError) {
      editFormError.hidden = false;
      editFormError.textContent = err.message || "Failed to save changes";
    } else {
      window.alert(err.message || "Failed to save changes");
    }
  } finally {
    if (btnEditSave) {
      btnEditSave.disabled = false;
      btnEditSave.textContent = "Save";
    }
  }
}

export function showToast(message, { type = "ok", duration = 3200 } = {}) {
  let host = document.getElementById("toast-host");
  if (!host) {
    host = document.createElement("div");
    host.id = "toast-host";
    host.className = "toast-host";
    host.setAttribute("aria-live", "polite");
    document.body.appendChild(host);
  }
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = message;
  host.appendChild(el);
  requestAnimationFrame(() => el.classList.add("show"));
  window.setTimeout(() => {
    el.classList.remove("show");
    window.setTimeout(() => el.remove(), 280);
  }, duration);
}

const _seenNotificationIds = new Set();

/** Surface background appliance-delete failures (and dismiss after showing). */
export async function pollDeleteNotifications() {
  try {
    const notes = await fetchJSON("/api/notifications");
    if (!Array.isArray(notes) || !notes.length) return;
    for (const n of notes) {
      const id = Number(n.id);
      if (!id || _seenNotificationIds.has(id)) continue;
      _seenNotificationIds.add(id);
      const text = n.message || n.title || "A background task failed";
      showToast(text, { type: "err", duration: 14000 });
      // Also alert once so it is hard to miss if the toast is overlooked.
      if (n.kind === "appliance_delete_failed") {
        window.setTimeout(() => {
          window.alert(text);
        }, 200);
      }
      try {
        await fetchJSON(`/api/notifications/${id}/dismiss`, { method: "POST" });
      } catch {
        /* keep trying next poll */
        _seenNotificationIds.delete(id);
      }
    }
    // If a delete failed, appliance may reappear — refresh list.
    if (notes.some((n) => n.kind === "appliance_delete_failed")) {
      await loadAppliances({ force: true }).catch(() => null);
      renderApplianceList(true);
      await refreshStatus().catch(() => null);
    }
  } catch (err) {
    console.warn("notification poll failed:", err);
  }
}

export async function handleApplianceAction(e) {
  const { panelsEl, descEl } = getDom();
  const editBtn = e.target.closest(".appliance-edit");
  if (editBtn) {
    e.preventDefault();
    e.stopPropagation();
    const id = Number(editBtn.dataset.id);
    const appliance = state.appliances.find((a) => a.id === id);
    if (!appliance) return true;
    const target = editBtn.dataset.editTarget || "appliance";
    openEditModal(appliance, target);
    return true;
  }

  const delBtn = e.target.closest(".appliance-delete");
  if (delBtn) {
    e.preventDefault();
    e.stopPropagation();
    const id = Number(delBtn.dataset.id);
    const appliance = state.appliances.find((a) => a.id === id);
    const name = appliance?.display_name || appliance?.host || `#${id}`;
    if (!window.confirm(
      `Remove appliance "${name}"?\n\nIt disappears from the list immediately. Metric history is deleted in the background (may take several minutes on large databases).`
    )) {
      return true;
    }
    delBtn.disabled = true;
    try {
      const res = await fetchJSON(`/api/appliances/${id}`, { method: "DELETE" });
      // Optimistic UI update so the tree refreshes even if a later poll is slow.
      state.appliances = (state.appliances || []).filter((a) => a.id !== id);
      state._applianceSig = null;
      if (state.applianceId === id) {
        state.applianceId = state.appliances[0]?.id || null;
        state.panelMeta = null;
        destroyCharts();
        if (panelsEl) panelsEl.innerHTML = "";
        if (descEl) {
          descEl.textContent = "Select or add a CipherTrust Manager appliance to begin.";
        }
      }
      renderApplianceList(true);
      await loadAppliances();
      renderApplianceList(true);
      if (state.viewMode === "appliances") {
        await renderFleetHealth();
      } else if (state.applianceId && state.viewMode === "dashboard") {
        await loadDashboard(state.dashboardId, { forceFull: true });
      }
      await refreshStatus();
      showToast(res?.message || `Removed "${name}". History purge continues in the background.`, {
        type: "ok",
        duration: 5200,
      });
      // Keep watching for a background-delete failure notification.
      void pollDeleteNotifications();
    } catch (err) {
      window.alert(err.message || "Failed to remove appliance");
      await loadAppliances();
      renderApplianceList(true);
    } finally {
      delBtn.disabled = false;
    }
    return true;
  }

  const retryBtn = e.target.closest(".appliance-retry");
  if (retryBtn) {
    e.preventDefault();
    e.stopPropagation();
    const id = Number(retryBtn.dataset.id);
    if (state.syncingApplianceIds.has(id)) return true;
    const appliance = state.appliances.find((a) => a.id === id);
    const wasOffline = appliance?.last_status === "offline";
    const label =
      (appliance?.display_name || "").trim() ||
      (appliance?.host || "").replace(/^https?:\/\//, "") ||
      `#${id}`;
    state.syncingApplianceIds.add(id);
    state.applianceId = id;
    state.panelMeta = null;
    renderApplianceList(true);
    try {
      await fetchJSON(`/api/appliances/${id}/scrape?force=1`, { method: "POST" });
      await loadAppliances();
      await refreshStatus();
      if (state.viewMode === "dashboard") {
        await loadDashboard(state.dashboardId, { forceFull: true });
      }
      showToast(
        wasOffline ? `Retry complete · ${label}` : `Sync complete · ${label}`,
        { type: "ok" }
      );
    } catch (err) {
      await loadAppliances();
      await refreshStatus();
      showToast(
        err.message || (wasOffline ? `Retry failed · ${label}` : `Sync failed · ${label}`),
        { type: "err", duration: 4500 }
      );
    } finally {
      state.syncingApplianceIds.delete(id);
      renderApplianceList(true);
    }
    return true;
  }
  return false;
}
