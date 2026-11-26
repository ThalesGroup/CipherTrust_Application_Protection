import { state, getDom } from "./state.js";
import { relativeAge } from "./format.js";

export async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data.error || `${res.status} ${res.statusText}`);
    err.payload = data;
    err.status = res.status;
    throw err;
  }
  return data;
}

export function friendlyScrapeError(raw, appliance) {
  const msg = String(raw || "").trim();
  const host =
    (appliance?.host || "").replace(/^https?:\/\//, "") ||
    (msg.match(/host=['"]?([^'",\s)]+)/i) || [])[1] ||
    "appliance";

  if (!msg) return { short: "Offline", detail: "" };

  const lower = msg.toLowerCase();
  if (lower.startsWith("offline after") || appliance?.last_status === "offline") {
    return {
      short: `Offline · ${host}`,
      detail: msg || "Stopped auto-retrying after repeated failures. Click Refresh to try again.",
    };
  }
  if (
    lower.includes("connecttimeout") ||
    lower.includes("max retries exceeded") ||
    lower.includes("failed to establish") ||
    lower.includes("connection aborted") ||
    lower.includes("name or service not known") ||
    lower.includes("nodename nor servname") ||
    lower.includes("getaddrinfo failed")
  ) {
    return { short: `Unreachable · ${host}`, detail: msg };
  }
  if (lower.includes("connection refused") || lower.includes("actively refused")) {
    return { short: `Connection refused · ${host}`, detail: msg };
  }
  if (lower.includes("timed out") || lower.includes("timeout") || lower.includes("read timed out")) {
    return { short: `Timed out · ${host}`, detail: msg };
  }
  if (lower.includes("ssl") || lower.includes("certificate")) {
    return { short: `TLS error · ${host}`, detail: msg };
  }
  if (lower.includes("401") || lower.includes("unauthorized") || lower.includes("login failed")) {
    return { short: "Auth failed — reconnect", detail: msg };
  }
  if (lower.includes("403") || lower.includes("forbidden")) {
    return { short: "Forbidden — check permissions", detail: msg };
  }
  if (lower.includes("decrypt") || lower.includes("secret_key")) {
    return { short: "Credentials locked — reconnect", detail: msg };
  }
  if (lower.includes("no metrics token")) {
    return { short: "No metrics token — reconnect", detail: msg };
  }

  // Fallback: first line, truncated — never dump a full urllib exception into the pill
  const first = msg.split(/[\r\n]/)[0].replace(/^HTTPSConnectionPool\([^)]+\):\s*/i, "");
  const short = first.length > 48 ? `${first.slice(0, 45)}…` : first;
  return { short: short || "Offline", detail: msg };
}

function stopScrapeAgeTicker() {
  if (state.scrapeAgeTimer) {
    clearInterval(state.scrapeAgeTimer);
    state.scrapeAgeTimer = null;
  }
}

function paintOkStatus() {
  const { statusPill, statusText } = getDom();
  if (!statusPill || !statusText) return;
  const age = relativeAge(state.lastScrapeAt);
  statusPill.classList.remove("ok", "warn", "err");
  statusPill.classList.add("ok");
  statusText.textContent = age ? `scraped ${age}` : "online";
  if (state.lastScrapeAt) {
    statusPill.title = `Last scrape: ${new Date(state.lastScrapeAt * 1000).toLocaleString()}`;
  }
}

function startScrapeAgeTicker() {
  stopScrapeAgeTicker();
  if (state.lastScrapeAt == null) return;
  state.scrapeAgeTimer = setInterval(() => {
    const { statusPill } = getDom();
    if (!statusPill?.classList.contains("ok")) {
      stopScrapeAgeTicker();
      return;
    }
    paintOkStatus();
  }, 1000);
}

export async function refreshStatus() {
  const { statusPill, statusText } = getDom();
  try {
    const s = await fetchJSON("/api/status");
    const current = (s.appliances || []).find((a) => a.id === state.applianceId);
    statusPill.classList.remove("ok", "warn", "err");
    statusPill.removeAttribute("title");
    if (!s.appliance_count) {
      stopScrapeAgeTicker();
      state.lastScrapeAt = null;
      statusPill.classList.add("warn");
      statusText.textContent = "no appliances";
    } else if (current?.last_status === "ok") {
      state.lastScrapeAt = current.last_scrape_at ?? null;
      paintOkStatus();
      startScrapeAgeTicker();
    } else if (current?.last_status === "offline") {
      stopScrapeAgeTicker();
      state.lastScrapeAt = current.last_scrape_at ?? null;
      statusPill.classList.add("err");
      const { short, detail } = friendlyScrapeError(current.last_error, current);
      const age = relativeAge(state.lastScrapeAt);
      statusText.textContent = age ? `${short} · ${age}` : short;
      statusPill.title = detail || "Offline — click Refresh to retry";
    } else if (current?.last_status === "error") {
      stopScrapeAgeTicker();
      state.lastScrapeAt = current.last_scrape_at ?? null;
      statusPill.classList.add("err");
      const { short, detail } = friendlyScrapeError(current.last_error, current);
      const age = relativeAge(state.lastScrapeAt);
      statusText.textContent = age ? `${short} · ${age}` : short;
      if (detail) statusPill.title = detail;
    } else {
      stopScrapeAgeTicker();
      state.lastScrapeAt = null;
      statusPill.classList.add("warn");
      statusText.textContent = `${s.appliance_count} appliance(s)`;
    }
  } catch {
    stopScrapeAgeTicker();
    statusPill.classList.add("err");
    statusText.textContent = "status error";
  }
}
