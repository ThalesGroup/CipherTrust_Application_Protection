# CipherTrust Metrics

Standalone multi-appliance web app for **CipherTrust Manager** Prometheus metrics, REST ops snapshots, and an integrated **healthcheck** (ksctl).

- Add CM appliances with host / username / password (TLS verify disabled for CM connections)
- Dashboards for host, keys, licensing, interfaces, CTE, cluster, and more
- Interface / properties security posture from live REST data
- Built-in healthcheck tab (Linux `ksctl` bundled in the Docker image)
- SQLite history that survives restarts when you mount a volume

Docs: [Prometheus Metrics](https://docs-cybersec.thalesgroup.com/bundle/v2.21-cdsp-cm/page/admin/cm_admin/monitoring/metrics/index.html) · [REST Auth](https://docs-cybersec.thalesgroup.com/bundle/v2.21-cdsp-cm/page/admin/cm_admin/authentication/rest-api/index.html)

Looking for **Healthcheck only?** See Stephen O’Connor’s [CipherTrust Healthcheck Reporter](https://github.com/soconnor73/healthcheck) 

## Screenshots

Full set (dark + light): [`docs/screenshots/`](docs/screenshots/)

![Appliances / Fleet](docs/screenshots/01-appliances-fleet.png)

![Overview](docs/screenshots/02-overview.png)

![Ops · Interfaces security posture](docs/screenshots/06-ops-interfaces.png)

![Host metrics](docs/screenshots/04-host-metrics.png)

![CCKM / Cloud Keys](docs/screenshots/09-connectors-cckm.png)

![Overview (light theme)](docs/screenshots/11-overview-light.png)

---

## Deploy with Docker (recommended)

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) (Desktop, Rancher Desktop, or Docker Engine). No Python install required.

### Quick start

```bash
docker pull sanyambassi/ciphertrust-metrics:latest

docker run -d \
  --name ciphertrust-metrics \
  -p 5050:5050 \
  -v ciphertrust-metrics-data:/app/data \
  --restart unless-stopped \
  sanyambassi/ciphertrust-metrics:latest
```

Open **http://localhost:5050** → **Appliances** → add a CM (host, username, password).

| Item | Detail |
|------|--------|
| Image | [`sanyambassi/ciphertrust-metrics`](https://hub.docker.com/r/sanyambassi/ciphertrust-metrics) |
| Tags | `latest`, `1.0.0` |
| Port | `5050` (HTTP by default in the image) |
| Data volume | `/app/data` — SQLite DB, optional TLS certs, healthcheck reports |
| Platform | `linux/amd64` (Apple Silicon usually runs via emulation) |

### Persist encryption key (recommended)

Appliance passwords are encrypted with `SECRET_KEY`. Set it explicitly so recreating the container (same volume) keeps working:

```bash
docker run -d \
  --name ciphertrust-metrics \
  -p 5050:5050 \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -v ciphertrust-metrics-data:/app/data \
  --restart unless-stopped \
  sanyambassi/ciphertrust-metrics:latest
```

On Windows PowerShell you can use:

```powershell
$secret = -join ((1..64) | ForEach-Object { "{0:x}" -f (Get-Random -Max 16) })
docker run -d --name ciphertrust-metrics -p 5050:5050 `
  -e SECRET_KEY=$secret `
  -v ciphertrust-metrics-data:/app/data `
  --restart unless-stopped `
  sanyambassi/ciphertrust-metrics:latest
```

### Optional HTTPS inside the container

```bash
docker run -d \
  --name ciphertrust-metrics \
  -p 5050:5050 \
  -e FLASK_HTTPS=true \
  -v ciphertrust-metrics-data:/app/data \
  --restart unless-stopped \
  sanyambassi/ciphertrust-metrics:latest
```

Self-signed certs are written under `/app/data/certs` (browser warning expected).

### Docker Compose

From this repository:

```bash
git clone https://github.com/ThalesGroup/CipherTrust_Application_Protection.git
cd CipherTrust_Application_Protection/demos/ciphertrust-manager-metrics
docker compose up -d
```

Or pull only (no local build):

```bash
docker compose up -d
```

Edit `docker-compose.yml` to set `SECRET_KEY` or change the published port.

### Network requirements

The container must reach each CipherTrust Manager over HTTPS (typically port **443**). Healthcheck uses the same credentials via bundled `ksctl`.

### Upgrade

```bash
docker pull sanyambassi/ciphertrust-metrics:latest
docker stop ciphertrust-metrics && docker rm ciphertrust-metrics
# re-run the same docker run / compose command — keep the same volume name
```

---

## Local Python install (optional)

Use this only if you prefer not to use Docker.

```bash
git clone https://github.com/ThalesGroup/CipherTrust_Application_Protection.git
cd CipherTrust_Application_Protection/demos/ciphertrust-manager-metrics
python -m venv venv
# Windows: .\venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional
python run.py
```

Open https://127.0.0.1:5050 (HTTPS on by default for local runs).

**Healthcheck locally:** `ksctl` is **not** in this git repo. When you add the first
CipherTrust Manager, the app downloads `https://<cm-host>/downloads/ksctl_images.zip`
(no auth) and extracts the right OS binary into `tools/`. The Docker Hub image already
bundles Linux `ksctl`, so no download is needed there.

If you only need healthchecks (not metrics dashboards), use the independent project [soconnor73/healthcheck](https://github.com/soconnor73/healthcheck) instead.

See [`tools/README.md`](tools/README.md) for manual install / building the image from source.

---

## What happens on Connect

1. `POST /api/v1/auth/tokens/` with username/password (`-k` / verify=False)
2. Enable/fetch Prometheus token via `/system/metrics/prometheus/enable|status`
3. Scrape `/api/v1/system/metrics/prometheus`
4. Discover cluster peers from `/cluster/nodes` (and related endpoints) plus metric `host` labels
5. Optionally auto-add peer appliances using the same credentials
6. Persist samples to SQLite for historical charts across restarts

## API

| Endpoint | Description |
|---|---|
| `GET/POST /api/appliances` | List / add appliances |
| `GET/DELETE /api/appliances/<id>` | Detail / remove |
| `POST /api/appliances/<id>/scrape` | Force scrape |
| `POST /api/appliances/<id>/discover-cluster` | Re-run cluster discovery |
| `GET /api/dashboards/<id>?appliance_id=` | Dashboard panels |
| `GET /api/status` | All appliances scrape status |
| `POST /api/appliances/<id>/healthcheck` | Start healthcheck |
| `GET /api/appliances/<id>/healthcheck` | Healthcheck status |

Passwords are encrypted at rest with Fernet keyed from `SECRET_KEY` (auto-generated on first run if unset).

## License

This project is released under the [MIT License](LICENSE).
