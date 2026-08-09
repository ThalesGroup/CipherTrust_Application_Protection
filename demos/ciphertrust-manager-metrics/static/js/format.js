export function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function fmtDuration(seconds) {
  const total = Math.max(0, Math.floor(Number(seconds) || 0));
  const days = Math.floor(total / 86400);
  const hours = Math.floor((total % 86400) / 3600);
  const mins = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  if (days > 0) return `${days}d ${hours}h ${mins}m`;
  if (hours > 0) return `${hours}h ${mins}m`;
  if (mins > 0) return `${mins}m ${secs}s`;
  return `${secs}s`;
}

/** Compact CM /v1/system/info uptime, e.g. "6 days, 13 hours, 53 minutes" → "6d 13h 53m". */
export function formatCmUptime(raw) {
  const s = String(raw || "").trim();
  if (!s) return "";
  const compact = s
    .replace(/,\s*/g, " ")
    .replace(/\bdays?\b/gi, "d")
    .replace(/\bhours?\b/gi, "h")
    .replace(/\bminutes?\b/gi, "m")
    .replace(/\bseconds?\b/gi, "s")
    .replace(/\s+/g, " ")
    .trim();
  // "6 d 13 h 53 m" → "6d 13h 53m"
  return compact.replace(/\s*([dhms])\b/gi, "$1").replace(/(\d[dhms])\s+/g, "$1 ");
}

export function isBytesUnit(unit) {
  return unit === "B" || unit === "bytes" || unit === "byte";
}

export function isBytesRateUnit(unit) {
  return unit === "B/s" || unit === "bytes/s" || unit === "Bps";
}

export function fmtBytes(value, perSecond = false) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  const sign = n < 0 ? "-" : "";
  const abs = Math.abs(n);
  const units = perSecond
    ? ["B/s", "KiB/s", "MiB/s", "GiB/s", "TiB/s"]
    : ["B", "KiB", "MiB", "GiB", "TiB"];
  let idx = 0;
  let scaled = abs;
  while (scaled >= 1024 && idx < units.length - 1) {
    scaled /= 1024;
    idx += 1;
  }
  const text = scaled >= 100 || idx === 0
    ? scaled.toFixed(0)
    : scaled >= 10
      ? scaled.toFixed(1)
      : scaled.toFixed(2);
  return `${sign}${text} ${units[idx]}`;
}

export function fmtDurationSeconds(seconds) {
  const n = Number(seconds);
  if (!Number.isFinite(n)) return "—";
  const abs = Math.abs(n);
  const sign = n < 0 ? "-" : "";
  if (abs >= 1) return `${sign}${abs.toFixed(abs >= 10 ? 2 : 3)} s`;
  if (abs >= 0.001) return `${sign}${(abs * 1000).toFixed(abs * 1000 >= 10 ? 1 : 2)} ms`;
  if (abs >= 0.000001) return `${sign}${(abs * 1e6).toFixed(1)} µs`;
  return `${sign}${(abs * 1e9).toFixed(0)} ns`;
}

export function fmt(value, unit) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  if (typeof value === "string") return value;
  if (unit === "duration" || unit === "uptime") return fmtDuration(value);
  // Large plain-second gauges (e.g. uptime mistakenly labeled "s")
  if (unit === "s" && Number(value) >= 3600) return fmtDuration(value);
  // Sub-second latencies: show ms / µs instead of scientific notation
  if (unit === "s" && Number.isFinite(Number(value)) && Math.abs(Number(value)) < 1) {
    return fmtDurationSeconds(value);
  }
  if (isBytesUnit(unit)) return fmtBytes(value, false);
  if (isBytesRateUnit(unit)) return fmtBytes(value, true);
  const n = Number(value);
  if (Math.abs(n) >= 1e9) return (n / 1e9).toFixed(2) + "B";
  if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(2) + "M";
  if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(2) + "k";
  if (Math.abs(n) < 0.01 && n !== 0) return n.toExponential(2);
  return Number.isInteger(n) ? String(n) : n.toFixed(2);
}

export function displayUnit(unit, value) {
  if (!unit || unit === "duration" || unit === "uptime") return "";
  if (unit === "s" && Number(value) >= 3600) return "";
  // latency helper already includes ms/µs/s
  if (unit === "s" && Number.isFinite(Number(value)) && Math.abs(Number(value)) < 1) return "";
  // bytes helpers already include the unit suffix
  if (isBytesUnit(unit) || isBytesRateUnit(unit)) return "";
  return unit;
}

export function yTickCallback(unit) {
  if (isBytesUnit(unit)) return (v) => fmtBytes(v, false);
  if (isBytesRateUnit(unit)) return (v) => fmtBytes(v, true);
  return undefined;
}

export function truncateLabel(text, max = 36) {
  const s = String(text || "");
  return s.length > max ? `${s.slice(0, max - 1)}…` : s;
}

export function formatSeriesTooltip(unit, ctx) {
  let name = ctx.dataset.label || "";
  if (name.length > 40) name = `${name.slice(0, 37)}…`;
  const raw = ctx.parsed?.y;
  if (raw == null || Number.isNaN(raw)) return name;
  if (isBytesUnit(unit)) return `${name}: ${fmtBytes(raw, false)}`;
  if (isBytesRateUnit(unit)) return `${name}: ${fmtBytes(raw, true)}`;
  if (unit === "%") return `${name}: ${Number(raw).toFixed(2)}%`;
  const formatted = fmt(raw, unit);
  const suffix = displayUnit(unit, raw);
  return suffix ? `${name}: ${formatted} ${suffix}` : `${name}: ${formatted}`;
}

export function tooltipTitle(items) {
  if (!items.length) return "";
  const x = items[0].parsed?.x;
  if (x == null) return "";
  return new Date(x).toLocaleString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    month: "short",
    day: "numeric",
  });
}

export function tsLabel(t, rangeId = "24h") {
  const d = new Date(t * 1000);
  if (rangeId === "7d" || rangeId === "30d") {
    return d.toLocaleString([], {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }
  if (rangeId === "24h" || rangeId === "6h" || rangeId === "1h") {
    return d.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }
  // 5m / 15m / 30m — include seconds
  return d.toLocaleTimeString([], {
    hour: "2-digit", minute: "2-digit", second: "2-digit",
  });
}

/** Relative age for scrape status, e.g. "12s ago", "3m ago". */
export function relativeAge(tsSeconds) {
  if (tsSeconds == null || !Number.isFinite(Number(tsSeconds))) return null;
  const age = Math.max(0, Math.floor(Date.now() / 1000 - Number(tsSeconds)));
  if (age < 60) return `${age}s ago`;
  if (age < 3600) return `${Math.floor(age / 60)}m ago`;
  if (age < 86400) return `${Math.floor(age / 3600)}h ago`;
  return `${Math.floor(age / 86400)}d ago`;
}

export function appliancesSignature(list) {
  return JSON.stringify(
    (list || []).map((a) => [
      a.id,
      a.display_name,
      a.cluster_display_name,
      a.location,
      a.host,
      a.last_status,
      a.fail_count,
      a.is_clustered,
      a.parent_appliance_id,
      a.cluster_role,
      a.sample_count,
      a.cm_uptime || "",
    ])
  );
}

export function panelSignature(data) {
  const panels = data.panels || [];
  return JSON.stringify({
    id: data.id,
    appliance: data.appliance?.id,
    range: data.range || "",
    layout: panels.map((p) => [p.type, p.title, p.unit || "", p.span || "", !!p.wide]),
  });
}
