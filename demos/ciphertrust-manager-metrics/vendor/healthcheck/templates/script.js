function switchTab(evt, tabId) {
    const panels = document.querySelectorAll('.content-panel');
    panels.forEach(p => p.classList.remove('active'));

    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(b => b.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    evt.currentTarget.classList.add('active');
}

function toggleSeverityGroup(groupId) {
    const content = document.getElementById(groupId);
    const header = content.previousElementSibling;
    content.classList.toggle('active');
    header.classList.toggle('collapsed');
}

function applyReportTheme(theme) {
    const next = theme === 'light' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
}

(function initReportTheme() {
    try {
        const params = new URLSearchParams(window.location.search);
        const fromQuery = params.get('theme');
        if (fromQuery === 'light' || fromQuery === 'dark') {
            applyReportTheme(fromQuery);
        }
    } catch (_) { /* ignore */ }
    window.addEventListener('message', (event) => {
        const data = event && event.data;
        if (!data || data.type !== 'cm-metrics-theme') return;
        if (data.theme === 'light' || data.theme === 'dark') {
            applyReportTheme(data.theme);
        }
    });
})();

