"""Flask application factory for multi-appliance CM Metrics Viewer."""

from __future__ import annotations

import logging
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from . import db
from . import appliance_delete
from .client import CMClientError
from .config import Config
from .dashboards import get_dashboard, list_dashboard_groups, list_dashboards
from . import healthcheck_runner
from .scraper import MetricsScraper
from .store import MetricsStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
store = MetricsStore()
scraper = MetricsScraper(store)


def create_app() -> Flask:
    db.init_db()
    app = Flask(
        __name__,
        template_folder=str(ROOT / "templates"),
        static_folder=str(ROOT / "static"),
    )
    app.secret_key = Config.SECRET_KEY

    @app.before_request
    def _ensure_scraper() -> None:
        scraper.start()
        appliance_delete.ensure_started()

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            dashboards=list_dashboards(),
            dashboard_groups=list_dashboard_groups(),
            scrape_interval=Config.SCRAPE_INTERVAL,
            appliance_count=db.appliance_count(),
        )

    # ---- Appliances -----------------------------------------------------

    @app.get("/api/appliances")
    def api_list_appliances():
        appliances = db.list_appliances()
        for a in appliances:
            a["peers"] = db.list_cluster_peers(int(a["id"]))
        return jsonify(appliances)

    @app.get("/api/notifications")
    def api_list_notifications():
        return jsonify(db.list_active_notifications())

    @app.post("/api/notifications/<int:notification_id>/dismiss")
    def api_dismiss_notification(notification_id: int):
        if not db.dismiss_notification(notification_id):
            return jsonify({"error": "not found"}), 404
        return jsonify({"ok": True})

    @app.post("/api/appliances")
    def api_add_appliance():
        payload = request.get_json(silent=True) or {}
        host = (payload.get("host") or "").strip()
        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""
        display_name = (payload.get("display_name") or "").strip() or None
        location = (payload.get("location") or "").strip() or None
        discover = bool(payload.get("discover_cluster", True))

        if not host or not username or not password:
            return jsonify({"error": "host, username, and password are required"}), 400

        try:
            result = scraper.connect_appliance(
                host=host,
                username=username,
                password=password,
                display_name=display_name,
                domain="",  # always root domain
                discover_cluster=discover,
                location=location,
            )
            return jsonify(result), 201
        except CMClientError as exc:
            logger.warning("Add appliance failed: %s", exc)
            body = {"error": str(exc), "status_code": exc.status_code}
            msg = str(exc).lower()
            if "cannot enable prometheus" in msg or "read-only" in msg:
                body["code"] = "prometheus_permission"
                body["hint"] = (
                    "Enable Prometheus metrics on the appliance (Admin Settings > Metrics), "
                    "then re-add it with a user that can read the metrics token."
                )
            return jsonify(body), 400
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:  # noqa: BLE001
            logger.exception("Add appliance unexpected error")
            return jsonify({"error": str(exc)}), 500

    @app.get("/api/appliances/<int:appliance_id>")
    def api_get_appliance(appliance_id: int):
        appliance = db.get_appliance(appliance_id)
        if not appliance:
            return jsonify({"error": "not found"}), 404
        appliance["peers"] = db.list_cluster_peers(appliance_id)
        snap = store.for_appliance(appliance_id).latest_snapshot()
        appliance["live_sample_count"] = len(snap.samples) if snap else 0
        appliance["live_source"] = snap.source if snap else None
        return jsonify(appliance)

    @app.delete("/api/appliances/<int:appliance_id>")
    def api_delete_appliance(appliance_id: int):
        """Remove appliance immediately from the UI; purge history in the background."""
        meta = db.begin_appliance_delete(appliance_id)
        if not meta:
            return jsonify({"error": "not found"}), 404
        scraper.invalidate_client(appliance_id)
        store.drop(appliance_id)
        job = appliance_delete.start_appliance_delete(appliance_id, meta)
        try:
            db.record_fleet_health_sample(force=True)
        except Exception:  # noqa: BLE001
            logger.debug("fleet health sample after delete failed", exc_info=True)
        label = job.get("label") or meta.get("display_name") or meta.get("host") or f"#{appliance_id}"
        return jsonify(
            {
                "ok": True,
                "async": True,
                "already_deleting": bool(meta.get("already_deleting") or job.get("already_running")),
                "appliance_id": appliance_id,
                "message": (
                    f'Removed "{label}" from the list. Metric history is being deleted in the background.'
                ),
            }
        )

    @app.post("/api/appliances/<int:appliance_id>/scrape")
    def api_scrape_appliance(appliance_id: int):
        # Manual refresh always forces a retry (clears offline / fail counter).
        force = request.args.get("force", "1").lower() not in {"0", "false", "no"}
        result = scraper.scrape_appliance(appliance_id, force=force)
        if result.get("skipped"):
            return jsonify(result), 200
        code = 200 if result.get("ok") or result.get("source") == "demo" else 400
        return jsonify(result), code

    @app.post("/api/appliances/<int:appliance_id>/discover-cluster")
    def api_discover_cluster(appliance_id: int):
        appliance = db.get_appliance(appliance_id, include_secrets=True)
        if not appliance:
            return jsonify({"error": "not found"}), 404
        try:
            result = scraper.connect_appliance(
                host=appliance["host"],
                username=appliance["username"],
                password=appliance["password"],
                display_name=appliance.get("display_name"),
                domain=appliance.get("domain") or "",
                discover_cluster=True,
            )
            return jsonify(result)
        except CMClientError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.patch("/api/appliances/<int:appliance_id>")
    def api_patch_appliance(appliance_id: int):
        payload = request.get_json(silent=True) or {}
        if not db.get_appliance(appliance_id):
            return jsonify({"error": "not found"}), 404
        if "enabled" in payload:
            db.set_appliance_enabled(appliance_id, bool(payload["enabled"]))
        updated = None
        if "cluster_display_name" in payload:
            updated = db.update_appliance_cluster_display_name(
                appliance_id, str(payload.get("cluster_display_name") or "")
            )
            if not updated:
                return jsonify({"error": "not found"}), 404
        if "display_name" in payload:
            updated = db.update_appliance_display_name(
                appliance_id, str(payload.get("display_name") or "")
            )
            if not updated:
                return jsonify({"error": "not found"}), 404
        if "location" in payload:
            updated = db.update_appliance_location(
                appliance_id, str(payload.get("location") or "")
            )
            if not updated:
                return jsonify({"error": "not found"}), 404
        appliance = updated or db.get_appliance(appliance_id)
        if not appliance:
            return jsonify({"error": "not found"}), 404
        return jsonify(appliance)

    # ---- Healthcheck ----------------------------------------------------

    @app.get("/api/healthcheck/ksctl")
    def api_healthcheck_ksctl():
        return jsonify(healthcheck_runner.ksctl_available())

    @app.get("/api/appliances/<int:appliance_id>/healthcheck")
    def api_healthcheck_status(appliance_id: int):
        if not db.get_appliance(appliance_id):
            return jsonify({"error": "not found"}), 404
        status = healthcheck_runner.get_status(appliance_id)
        analysis = None
        if status.get("status") == "done":
            analysis = healthcheck_runner.load_analysis(appliance_id)
        # Compact findings for the UI (cap per section).
        findings: list[dict] = []
        if isinstance(analysis, dict):
            for section, body in analysis.items():
                if section == "status" or not isinstance(body, dict):
                    continue
                for issue in (body.get("issues") or [])[:40]:
                    if not isinstance(issue, dict):
                        continue
                    findings.append(
                        {
                            "section": section,
                            "severity": issue.get("severity"),
                            "code": issue.get("code"),
                            "message": issue.get("message"),
                        }
                    )
            # Prefer FAIL then WARNING then INFO in the list.
            order = {"FAIL": 0, "WARNING": 1, "INFO": 2}
            findings.sort(key=lambda f: order.get(str(f.get("severity") or "").upper(), 9))
            findings = findings[:80]
        status["findings"] = findings
        status["section_status"] = {
            k: (v.get("status") if isinstance(v, dict) else None)
            for k, v in (analysis or {}).items()
            if k != "status"
        }
        return jsonify(status)

    @app.post("/api/appliances/<int:appliance_id>/healthcheck")
    def api_healthcheck_start(appliance_id: int):
        if not db.get_appliance(appliance_id):
            return jsonify({"error": "not found"}), 404
        result = healthcheck_runner.start_healthcheck(appliance_id)
        code = 200 if result.get("ok") else 400
        return jsonify(result), code

    @app.get("/api/appliances/<int:appliance_id>/healthcheck/report")
    def api_healthcheck_report(appliance_id: int):
        if not db.get_appliance(appliance_id):
            return jsonify({"error": "not found"}), 404
        path = healthcheck_runner.report_html_path(appliance_id)
        if not path:
            return jsonify({"error": "no report available — run a healthcheck first"}), 404
        from flask import Response

        from .healthcheck_theme import themed_report_html

        theme = (request.args.get("theme") or "dark").strip().lower()
        if theme not in {"light", "dark"}:
            theme = "dark"
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            return jsonify({"error": f"unable to read report: {exc}"}), 500
        html = themed_report_html(raw, theme=theme)
        return Response(html, mimetype="text/html; charset=utf-8")

    # ---- Dashboards / metrics ------------------------------------------

    @app.get("/api/status")
    def api_status():
        return jsonify(store.status_all())

    @app.get("/api/fleet-health")
    def api_fleet_health():
        """Online/offline fleet counts over time for the Appliances tab chart."""
        from .dashboards.catalog import parse_range

        range_id, range_seconds = parse_range(request.args.get("range") or "24h")
        since = time.time() - range_seconds
        # Ensure the chart has a current point even before the next scrape loop.
        try:
            db.record_fleet_health_sample()
        except Exception:  # noqa: BLE001
            logger.debug("fleet health sample on read failed", exc_info=True)
        points = db.load_fleet_health_series(since=since)
        latest = points[-1] if points else {
            "t": time.time(),
            "online": 0,
            "offline": 0,
            "other": 0,
            "total": 0,
        }
        return jsonify({
            "range": range_id,
            "range_seconds": range_seconds,
            "latest": latest,
            "points": points,
        })

    @app.get("/api/dashboards")
    def api_dashboards():
        return jsonify(list_dashboards())

    @app.get("/api/dashboard-groups")
    def api_dashboard_groups():
        return jsonify(list_dashboard_groups())

    @app.get("/api/dashboards/<dashboard_id>")
    def api_dashboard(dashboard_id: str):
        from .dashboards.catalog import parse_range

        appliance_id = request.args.get("appliance_id", type=int)
        if not appliance_id:
            appliances = db.list_appliances()
            if not appliances:
                return jsonify({"error": "no appliances configured", "needs_setup": True}), 400
            appliance_id = int(appliances[0]["id"])
        appliance = db.get_appliance(appliance_id)
        if appliance:
            snap = db.get_appliance_ops_snapshot(appliance_id)
            if snap:
                appliance["ops_snapshot"] = snap
        range_id, range_seconds = parse_range(request.args.get("range"))
        data = get_dashboard(
            dashboard_id,
            store.for_appliance(appliance_id),
            appliance,
            range_seconds=range_seconds,
            range_id=range_id,
        )
        if not data:
            return jsonify({"error": "dashboard not found"}), 404
        data["appliance"] = appliance
        return jsonify(data)

    @app.get("/api/metrics")
    def api_metrics():
        appliance_id = request.args.get("appliance_id", type=int)
        if not appliance_id:
            return jsonify({"error": "appliance_id required"}), 400
        prefix = request.args.get("prefix")
        name = request.args.get("name")
        limit = min(int(request.args.get("limit", 200)), 2000)
        samples = store.for_appliance(appliance_id).latest_samples()
        if name:
            samples = [s for s in samples if s.name == name]
        elif prefix:
            samples = [s for s in samples if s.name.startswith(prefix)]
        return jsonify({"count": len(samples), "samples": [s.to_dict() for s in samples[:limit]]})

    @app.get("/api/metrics/series")
    def api_series():
        appliance_id = request.args.get("appliance_id", type=int)
        name = request.args.get("name")
        if not appliance_id or not name:
            return jsonify({"error": "appliance_id and name are required"}), 400
        labels = {}
        for key, value in request.args.items():
            if key.startswith("label."):
                labels[key[6:]] = value
        series = store.for_appliance(appliance_id).series_by_name(name, labels or None, limit_series=50)
        return jsonify({"name": name, "series": series})

    @app.post("/api/scrape")
    def api_scrape_all():
        # Manual Refresh passes force=1 so offline appliances are retried.
        force = request.args.get("force", "0").lower() in {"1", "true", "yes"}
        # Default async for force refresh so browser reload / tab switches do not
        # cancel the server-side job. Pass async=0 for a blocking scrape.
        async_mode = request.args.get("async", "1" if force else "0").lower() not in {
            "0",
            "false",
            "no",
        }
        if force and async_mode:
            return jsonify(scraper.start_force_refresh())
        return jsonify({"results": scraper.scrape_all(force=force)})

    @app.get("/api/scrape/status")
    def api_scrape_status():
        return jsonify(scraper.force_refresh_status())

    @app.get("/api/health")
    def api_health():
        return jsonify({"ok": True, "appliances": db.appliance_count()})

    return app
