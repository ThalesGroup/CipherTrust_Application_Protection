import { state, getDom } from "./state.js";
import { escapeHtml, tsLabel } from "./format.js";
import { fetchJSON } from "./api.js";
import { currentTheme } from "./theme.js";

let pollTimer = null;
let loadSeq = 0;

function stopPoll() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

export function stopHealthcheckPoll() {
  stopPoll();
}

function severityClass(sev) {
  const s = String(sev || "").toUpperCase();
  if (s === "FAIL") return "hc-sev-fail";
  if (s === "WARNING") return "hc-sev-warn";
  if (s === "INFO") return "hc-sev-info";
  if (s === "PASS") return "hc-sev-pass";
  return "hc-sev-idle";
}

function formatWhen(ts) {
  if (!ts) return "—";
  // tsLabel expects unix seconds
  return tsLabel(Number(ts));
}

function renderShell() {
  const { healthcheckView } = getDom();
  if (!healthcheckView) return;
  healthcheckView.innerHTML = `
    <div class="hc-toolbar">
      <div class="hc-toolbar-text">
        <h2 class="hc-title">Healthcheck</h2>
        <p class="muted hc-sub">Runs the CipherTrust diagnostic healthcheck (ksctl) using this appliance's stored credentials.</p>
      </div>
      <div class="hc-toolbar-actions">
        <a class="btn btn-sm" id="hc-open-report" href="#" target="_blank" rel="noopener" hidden>Open report</a>
        <button type="button" class="btn btn-primary btn-sm" id="hc-run-btn">Run healthcheck</button>
      </div>
    </div>
    <div class="hc-status-row" id="hc-status-row">
      <div class="hc-overall" id="hc-overall">
        <span class="hc-overall-badge hc-sev-idle" id="hc-overall-badge">IDLE</span>
        <div class="hc-overall-meta">
          <div id="hc-phase">Select an appliance and run a healthcheck.</div>
          <div class="muted" id="hc-times"></div>
        </div>
      </div>
      <div class="hc-report-status" id="hc-report-status" hidden>
        <span class="hc-report-status-label">Report</span>
        <span class="hc-overall-badge hc-sev-idle" id="hc-report-status-badge">—</span>
      </div>
    </div>
    <div class="hc-ksctl muted" id="hc-ksctl"></div>
    <div class="hc-error" id="hc-error" hidden></div>
    <div class="hc-sections" id="hc-sections" hidden></div>
    <div class="hc-body">
      <div class="hc-findings-wrap">
        <h3 class="hc-section-title">Findings</h3>
        <div class="hc-findings" id="hc-findings"><div class="muted">No findings yet.</div></div>
      </div>
      <div class="hc-report-wrap" id="hc-report-wrap" hidden>
        <div class="hc-report-head">
          <h3 class="hc-section-title">Full report</h3>
        </div>
        <iframe class="hc-iframe" id="hc-iframe" title="Healthcheck report" sandbox="allow-scripts allow-same-origin"></iframe>
      </div>
    </div>
  `;

  document.getElementById("hc-run-btn")?.addEventListener("click", () => runHealthcheck());
}

function clearReportFrame(iframe) {
  if (!iframe) return;
  iframe.src = "about:blank";
  delete iframe.dataset.src;
  delete iframe.dataset.theme;
}

function reportUrl(applianceId) {
  const theme = currentTheme();
  return `/api/appliances/${applianceId}/healthcheck/report?theme=${encodeURIComponent(theme)}&t=${Date.now()}`;
}

export function syncHealthcheckReportTheme() {
  if (state.viewMode !== "healthcheck") return;
  const iframe = document.getElementById("hc-iframe");
  if (!iframe || !iframe.contentWindow) return;
  const theme = currentTheme();
  try {
    iframe.contentWindow.postMessage({ type: "cm-metrics-theme", theme }, "*");
  } catch (_) {
    /* ignore cross-origin / unloaded */
  }
  // If the iframe was loaded under the other theme, reload with the new query.
  if (iframe.dataset.theme && iframe.dataset.theme !== theme && state.applianceId && iframe.dataset.src) {
    iframe.dataset.theme = theme;
    iframe.src = reportUrl(state.applianceId);
  }
}

function applyStatus(data) {
  const badge = document.getElementById("hc-overall-badge");
  const phase = document.getElementById("hc-phase");
  const times = document.getElementById("hc-times");
  const reportStatus = document.getElementById("hc-report-status");
  const reportBadge = document.getElementById("hc-report-status-badge");
  const errEl = document.getElementById("hc-error");
  const runBtn = document.getElementById("hc-run-btn");
  const openBtn = document.getElementById("hc-open-report");
  const ksctlEl = document.getElementById("hc-ksctl");
  const findingsEl = document.getElementById("hc-findings");
  const sectionsEl = document.getElementById("hc-sections");
  const reportWrap = document.getElementById("hc-report-wrap");
  const iframe = document.getElementById("hc-iframe");

  const status = data.status || "idle";
  const hasReport = Boolean(data.has_report);
  const reportOverall = String(data.overall || "").toUpperCase();
  // Badge = job status (not appliance finding severity — that lives in Findings/report).
  const runBadge =
    status === "running" ? "RUNNING"
      : status === "done" ? "DONE"
        : status === "error" ? "ERROR"
          : "IDLE";
  const runBadgeClass =
    status === "running" ? "hc-sev-info"
      : status === "done" ? "hc-sev-pass"
        : status === "error" ? "hc-sev-fail"
          : "hc-sev-idle";
  if (badge) {
    badge.textContent = runBadge;
    badge.className = `hc-overall-badge ${runBadgeClass}`;
  }
  if (phase) {
    phase.textContent = data.message || data.phase || status;
  }
  if (times) {
    const parts = [];
    if (data.started_at) parts.push(`Started ${formatWhen(data.started_at)}`);
    if (data.finished_at) parts.push(`Finished ${formatWhen(data.finished_at)}`);
    times.textContent = parts.join(" · ");
  }

  if (reportStatus && reportBadge) {
    const showReportOverall = status === "done" && (reportOverall === "PASS" || reportOverall === "WARNING" || reportOverall === "FAIL");
    if (showReportOverall) {
      reportStatus.hidden = false;
      reportBadge.textContent = reportOverall;
      reportBadge.className = `hc-overall-badge ${severityClass(reportOverall)}`;
    } else {
      reportStatus.hidden = true;
      reportBadge.textContent = "—";
      reportBadge.className = "hc-overall-badge hc-sev-idle";
    }
  }

  if (errEl) {
    if (data.error) {
      errEl.hidden = false;
      errEl.textContent = data.error;
    } else {
      errEl.hidden = true;
      errEl.textContent = "";
    }
  }

  if (runBtn) {
    const running = status === "running";
    runBtn.disabled = running || !state.applianceId;
    runBtn.textContent = running ? "Running…" : "Run healthcheck";
  }

  if (ksctlEl) {
    const k = data.ksctl || {};
    if (k.ok) {
      ksctlEl.textContent = `ksctl ready${k.path ? ` (${k.path})` : ""}`;
    } else if (k && k.error) {
      ksctlEl.textContent = `ksctl unavailable: ${k.error}`;
    } else {
      ksctlEl.textContent = "";
    }
  }

  const sections = data.section_status || {};
  if (sectionsEl) {
    const keys = Object.keys(sections).filter((k) => sections[k]);
    if (status === "done" && keys.length) {
      sectionsEl.hidden = false;
      sectionsEl.innerHTML = keys
        .map((k) => {
          const st = sections[k] || "—";
          return `<span class="hc-section-chip ${severityClass(st)}"><span class="hc-section-name">${escapeHtml(k)}</span> ${escapeHtml(st)}</span>`;
        })
        .join("");
    } else {
      sectionsEl.hidden = true;
      sectionsEl.innerHTML = "";
    }
  }

  const findings = Array.isArray(data.findings) ? data.findings : [];
  if (findingsEl) {
    if (!findings.length) {
      findingsEl.innerHTML = `<div class="muted">${status === "done" ? "No findings." : "No findings yet."}</div>`;
    } else {
      findingsEl.innerHTML = findings
        .map((f) => {
          const sev = f.severity || "";
          return `<div class="hc-finding ${severityClass(sev)}">
            <span class="hc-finding-sev">${escapeHtml(String(sev).toUpperCase())}</span>
            <span class="hc-finding-sec">${escapeHtml(f.section || "")}</span>
            <span class="hc-finding-msg">${escapeHtml(f.message || "")}</span>
          </div>`;
        })
        .join("");
    }
  }

  const aid = state.applianceId;
  if (openBtn && aid && hasReport && status === "done") {
    openBtn.hidden = false;
    openBtn.href = `/api/appliances/${aid}/healthcheck/report?theme=${encodeURIComponent(currentTheme())}`;
  } else if (openBtn) {
    openBtn.hidden = true;
    openBtn.removeAttribute("href");
  }

  if (reportWrap && iframe) {
    const theme = currentTheme();
    const reportKey = aid && hasReport && status === "done"
      ? `${aid}:${data.finished_at || ""}:${theme}`
      : "";
    if (reportKey) {
      reportWrap.hidden = false;
      if (iframe.dataset.src !== reportKey) {
        iframe.dataset.src = reportKey;
        iframe.dataset.theme = theme;
        iframe.src = reportUrl(aid);
      } else {
        syncHealthcheckReportTheme();
      }
    } else {
      // Drop previous appliance's report immediately (do not leave stale iframe).
      reportWrap.hidden = true;
      clearReportFrame(iframe);
    }
  }
}

export async function refreshHealthcheckStatus() {
  const { healthcheckView } = getDom();
  if (!healthcheckView || state.viewMode !== "healthcheck") return;
  if (!state.applianceId) {
    applyStatus({
      status: "idle",
      message: "Select an appliance to run a healthcheck.",
      ksctl: null,
      findings: [],
      has_report: false,
      severity_counts: null,
      section_status: {},
    });
    return;
  }
  const aid = state.applianceId;
  const seq = ++loadSeq;
  // Clear previous appliance UI immediately so stale pills/report never linger
  // while the new appliance's status request is in flight.
  applyStatus({
    status: "idle",
    message: "Loading healthcheck status…",
    findings: [],
    has_report: false,
    severity_counts: null,
    section_status: {},
  });
  try {
    const data = await fetchJSON(`/api/appliances/${aid}/healthcheck`);
    if (seq !== loadSeq || state.viewMode !== "healthcheck" || state.applianceId !== aid) return;
    applyStatus(data);
    if (data.status === "running") {
      if (!pollTimer) {
        pollTimer = setInterval(() => {
          refreshHealthcheckStatus();
        }, 2500);
      }
    } else {
      stopPoll();
    }
  } catch (err) {
    if (seq !== loadSeq) return;
    applyStatus({
      status: "error",
      error: err.message || String(err),
      message: "Failed to load healthcheck status",
      findings: [],
    });
    stopPoll();
  }
}

export async function runHealthcheck() {
  if (!state.applianceId) return;
  const runBtn = document.getElementById("hc-run-btn");
  if (runBtn) {
    runBtn.disabled = true;
    runBtn.textContent = "Starting…";
  }
  try {
    await fetchJSON(`/api/appliances/${state.applianceId}/healthcheck`, { method: "POST" });
  } catch (err) {
    applyStatus({
      status: "error",
      error: err.message || String(err),
      message: "Failed to start healthcheck",
      findings: [],
    });
    if (runBtn) {
      runBtn.disabled = false;
      runBtn.textContent = "Run healthcheck";
    }
    return;
  }
  await refreshHealthcheckStatus();
}

export function hideHealthcheckView() {
  stopPoll();
  const { healthcheckView } = getDom();
  if (!healthcheckView) return;
  const iframe = healthcheckView.querySelector("#hc-iframe");
  if (iframe) iframe.src = "about:blank";
  healthcheckView.innerHTML = "";
  healthcheckView.hidden = true;
}

export function showHealthcheckTab() {
  state.viewMode = "healthcheck";
  stopPoll();
  const { panelsEl, healthcheckView } = getDom();
  if (panelsEl) {
    panelsEl.innerHTML = "";
    panelsEl.hidden = true;
  }
  if (healthcheckView) healthcheckView.hidden = false;
  // destroyCharts is called by caller via chrome sync
  renderShell();
  refreshHealthcheckStatus();
}
