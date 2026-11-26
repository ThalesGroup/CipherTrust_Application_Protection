"""Run the CipherTrust Manager Metrics Viewer."""

from __future__ import annotations

import logging
import sys
import threading
from pathlib import Path

from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cm_metrics import create_app, scraper  # noqa: E402
from cm_metrics import db  # noqa: E402
from cm_metrics.config import Config  # noqa: E402
from cm_metrics.tls import ensure_self_signed_cert  # noqa: E402

logger = logging.getLogger(__name__)
app = create_app()


def main() -> None:
    db.init_db()
    ssl_context = None
    if Config.FLASK_HTTPS:
        cert_path, key_path = ensure_self_signed_cert(
            Config.SSL_CERT_PATH,
            Config.SSL_KEY_PATH,
        )
        ssl_context = (str(cert_path), str(key_path))

    # Dual mode: HTTPS on FLASK_PORT + plain HTTP on FLASK_HTTP_PORT (no redirect).
    dual_http = bool(Config.FLASK_HTTPS and Config.FLASK_HTTP and Config.FLASK_HTTP_PORT)
    if dual_http and Config.FLASK_HTTP_PORT == Config.FLASK_PORT:
        raise SystemExit(
            "FLASK_HTTP_PORT must differ from FLASK_PORT when dual HTTP+HTTPS is enabled"
        )

    bind_host = Config.FLASK_HOST
    open_host = "127.0.0.1" if bind_host in {"0.0.0.0", "::"} else bind_host

    print("=" * 60)
    print("  CipherTrust Manager Metrics Viewer")
    print("=" * 60)
    print(f"  Database   : {Config.DATABASE_PATH}")
    print(f"  Appliances : {db.appliance_count()}")
    print(f"  TLS verify : disabled (CM connections)")
    print(f"  Scrape every: {Config.SCRAPE_INTERVAL}s")
    print(f"  Bind        : {bind_host}")
    if Config.FLASK_HTTPS:
        print(f"  HTTPS       : on  → https://{open_host}:{Config.FLASK_PORT}")
        print(f"  Cert        : {Config.SSL_CERT_PATH}")
        print("  Note        : self-signed cert — accept the browser warning once")
    else:
        print("  HTTPS       : off")
        print(f"  HTTP        : on  → http://{open_host}:{Config.FLASK_PORT}")
    if dual_http:
        print(f"  HTTP        : on  → http://{open_host}:{Config.FLASK_HTTP_PORT} (no redirect)")
    print("=" * 60)

    scraper.start()

    if dual_http:
        # Two independent Werkzeug servers; HTTP never redirects to HTTPS.
        http_server = make_server(
            bind_host,
            Config.FLASK_HTTP_PORT,
            app,
            threaded=True,
        )
        https_server = make_server(
            bind_host,
            Config.FLASK_PORT,
            app,
            threaded=True,
            ssl_context=ssl_context,
        )
        threading.Thread(
            target=http_server.serve_forever,
            name="cm-metrics-http",
            daemon=True,
        ).start()
        logger.info("HTTP listening on %s:%s (no TLS, no redirect)", bind_host, Config.FLASK_HTTP_PORT)
        logger.info("HTTPS listening on %s:%s", bind_host, Config.FLASK_PORT)
        try:
            https_server.serve_forever()
        except KeyboardInterrupt:
            http_server.shutdown()
            https_server.shutdown()
        return

    # Single listener (HTTP-only or HTTPS-only).
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
        use_reloader=False,
        threaded=True,
        ssl_context=ssl_context,
    )


if __name__ == "__main__":
    main()
