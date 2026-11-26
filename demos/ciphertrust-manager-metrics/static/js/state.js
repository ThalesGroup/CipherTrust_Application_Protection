import { TAB_CHIP_KEY, loadSavedRange } from "./config.js";

export const state = {
  dashboardId: window.CM_METRICS?.initialDashboard || "overview",
  groupId: "overview",
  viewMode: "appliances", // "dashboard" | "appliances" | "healthcheck"
  applianceId: null,
  appliances: [],
  charts: [],
  panelMeta: null,
  timer: null,
  loading: false,
  /** When a tick is skipped because another is in flight, run one more after. */
  tickPending: null,
  loadSeq: 0,
  _applianceSig: null,
  menuOpen: false,
  tabChips: {},
  rangeId: loadSavedRange(),
  lastScrapeAt: null,
  scrapeAgeTimer: null,
  fleetHealthChart: null,
  /** Appliance ids currently syncing via per-node Sync button. */
  syncingApplianceIds: new Set(),
};

try {
  state.tabChips = JSON.parse(localStorage.getItem(TAB_CHIP_KEY) || "{}") || {};
} catch (_) {
  state.tabChips = {};
}

let _dom = null;

export function getDom() {
  if (_dom) return _dom;
  _dom = {
    panelsEl: document.getElementById("panels"),
    titleEl: document.getElementById("dash-title"),
    descEl: document.getElementById("dash-desc"),
    statusPill: document.getElementById("status-pill"),
    statusText: document.getElementById("status-text"),
    autoRefresh: document.getElementById("auto-refresh"),
    btnRefresh: document.getElementById("btn-refresh"),
    applianceSelector: document.getElementById("appliance-selector"),
    btnApplianceCurrent: document.getElementById("btn-appliance-current"),
    applianceMenu: document.getElementById("appliance-menu"),
    applianceCurrentLabel: document.getElementById("appliance-current-label"),
    applianceCurrentMeta: document.getElementById("appliance-current-meta"),
    applianceTree: document.getElementById("appliance-tree"),
    appliancesView: document.getElementById("appliances-view"),
    healthcheckView: document.getElementById("healthcheck-view"),
    fleetHealth: document.getElementById("fleet-health"),
    fleetHealthChart: document.getElementById("fleet-health-chart"),
    fleetHealthSummary: document.getElementById("fleet-health-summary"),
    secondaryRow: document.getElementById("secondary-row"),
    primaryTabs: document.getElementById("primary-tabs"),
    secondaryChips: document.getElementById("secondary-chips"),
    rangePicker: document.getElementById("range-picker"),
    modal: document.getElementById("modal"),
    form: document.getElementById("connect-form"),
    formError: document.getElementById("form-error"),
    btnConnect: document.getElementById("btn-connect"),
    editModal: document.getElementById("edit-modal"),
    editForm: document.getElementById("edit-form"),
    editFormError: document.getElementById("edit-form-error"),
    editModalTitle: document.getElementById("edit-modal-title"),
    editModalSub: document.getElementById("edit-modal-sub"),
    editNameLabel: document.getElementById("edit-name-label"),
    editLocationWrap: document.getElementById("edit-location-wrap"),
    btnEditCancel: document.getElementById("btn-edit-cancel"),
    btnEditSave: document.getElementById("btn-edit-save"),
  };
  return _dom;
}
