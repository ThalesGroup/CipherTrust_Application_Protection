"""Theme-aware HTML injection for stored healthcheck reports."""

from __future__ import annotations

# Appended into existing reports so light/dark works without regenerating.
REPORT_THEME_SNIPPET = r"""
<style id="cm-metrics-report-theme">
html[data-theme="light"] {
  --bg-color: #f4f7fb;
  --card-bg: rgba(255, 255, 255, 0.92);
  --card-border: rgba(21, 32, 51, 0.1);
  --text-primary: #152033;
  --text-secondary: #5b6b82;
  --accent-primary: #0f766e;
  --accent-hover: #0d9488;
  --pass-color: #059669;
  --warn-color: #b45309;
  --warning-color: #b45309;
  --fail-color: #dc2626;
}
html[data-theme="light"] body {
  background-image:
    radial-gradient(at 0% 0%, rgba(15, 118, 110, 0.08) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(37, 99, 235, 0.06) 0px, transparent 50%);
}
html[data-theme="light"] .tab-btn:hover { background: rgba(15, 118, 110, 0.08); }
html[data-theme="light"] .tab-btn.active { background: var(--accent-primary); color: #fff; }
html[data-theme="light"] .tab-btn .badge { color: #fff; }
html[data-theme="light"] .json-pre { background: rgba(15, 32, 51, 0.04); color: #0369a1; }
html[data-theme="light"] .detail-item {
  background: rgba(244, 247, 251, 0.9);
  border: 1px solid var(--card-border);
}
html[data-theme="light"] .sidebar-footer-link:hover { background: rgba(15, 118, 110, 0.08); }
html[data-theme="light"] .section-title {
  color: var(--text-primary);
  border-bottom-color: rgba(21, 32, 51, 0.12);
}
html[data-theme="light"] .severity-header {
  background: rgba(21, 32, 51, 0.03);
  color: var(--text-primary);
}
html[data-theme="light"] .severity-header:hover { background: rgba(21, 32, 51, 0.06); }
html[data-theme="light"] .issue-item.fail {
  background: rgba(220, 38, 38, 0.08);
  border-color: rgba(220, 38, 38, 0.28);
  color: #991b1b;
}
html[data-theme="light"] .issue-item.warning {
  background: rgba(180, 83, 9, 0.08);
  border-color: rgba(180, 83, 9, 0.28);
  color: #92400e;
}
html[data-theme="light"] .issue-item.info {
  background: rgba(37, 99, 235, 0.08);
  border-color: rgba(37, 99, 235, 0.28);
  color: #1e40af;
}
html[data-theme="light"] .issue-item strong,
html[data-theme="light"] .issue-item b,
html[data-theme="light"] .issue-item h1,
html[data-theme="light"] .issue-item h2,
html[data-theme="light"] .issue-item h3,
html[data-theme="light"] .issue-item h4 { color: inherit; }
html[data-theme="light"] .issue-item details summary,
html[data-theme="light"] .issue-item details ul,
html[data-theme="light"] .issue-item [style*="color: var(--text-secondary)"] {
  color: #5b6b82 !important;
}
html[data-theme="light"] .content-panel h1,
html[data-theme="light"] .content-panel h2,
html[data-theme="light"] .content-panel h3,
html[data-theme="light"] .content-panel h4,
html[data-theme="light"] .content-panel .section-title { color: var(--text-primary); }
</style>
<script id="cm-metrics-report-theme-js">
(function () {
  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme === "light" ? "light" : "dark");
  }
  try {
    var q = new URLSearchParams(window.location.search).get("theme");
    if (q === "light" || q === "dark") apply(q);
  } catch (e) {}
  window.addEventListener("message", function (ev) {
    var d = ev && ev.data;
    if (!d || d.type !== "cm-metrics-theme") return;
    if (d.theme === "light" || d.theme === "dark") apply(d.theme);
  });
})();
</script>
"""


def themed_report_html(raw: str, theme: str = "dark") -> str:
    """Inject theme CSS/JS into a stored report and set initial data-theme."""
    import re

    html = raw
    theme = "light" if theme == "light" else "dark"

    # Always refresh the injected theme block so contrast fixes apply to old reports.
    if 'id="cm-metrics-report-theme"' in html:
        html = re.sub(
            r'<style id="cm-metrics-report-theme">[\s\S]*?</style>\s*'
            r'(?:<script id="cm-metrics-report-theme-js">[\s\S]*?</script>\s*)?',
            REPORT_THEME_SNIPPET + "\n",
            html,
            count=1,
        )
    elif "</head>" in html:
        html = html.replace("</head>", REPORT_THEME_SNIPPET + "\n</head>", 1)
    else:
        html = REPORT_THEME_SNIPPET + html

    # Prefer setting theme on the <html> tag for first paint.
    lower = html[:200].lower()
    if "<html" in lower:

        def _set_theme(match: re.Match) -> str:
            tag = match.group(0)
            if "data-theme=" in tag:
                return re.sub(
                    r'data-theme\s*=\s*["\'][^"\']*["\']',
                    f'data-theme="{theme}"',
                    tag,
                    count=1,
                )
            if tag.endswith(">"):
                return tag[:-1] + f' data-theme="{theme}">'
            return tag

        html = re.sub(r"<html\b[^>]*>", _set_theme, html, count=1, flags=re.IGNORECASE)
    return html
