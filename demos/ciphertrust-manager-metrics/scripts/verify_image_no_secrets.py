"""Fail the build if the image contains secret-like files or strings."""

from __future__ import annotations

import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

FORBIDDEN_PATHS = {
    "app/.env",
    "app/.env.local",
    "app/data/cm_metrics.db",
    "app/_deploy_ubuntu.py",
    "app/_redeploy_ubuntu.py",
    "app/tools/ksctl.exe",
}

# Credential-shaped material — not generic words like "password" in comments.
SECRET_RE = re.compile(
    r"("
    r"SECRET_KEY=[A-Za-z0-9_\-]{20,}|"
    r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|"
    r"sk-[a-zA-Z0-9]{20,}|"
    r"ghp_[A-Za-z0-9]{20,}|"
    r"xox[baprs]-[A-Za-z0-9-]{10,}|"
    r"password\s*=\s*['\"][^'\"]{8,}['\"]|"
    r"PASSWORD\s*=\s*['\"][^'\"]{8,}['\"]"
    r")",
    re.MULTILINE | re.IGNORECASE,
)

SKIP_SUFFIXES = {".so", ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".woff", ".woff2"}


def main() -> int:
    image = sys.argv[1] if len(sys.argv) > 1 else "sanyambassi/ciphertrust-metrics:latest"
    cid = subprocess.check_output(["docker", "create", image], text=True).strip()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tar_path = Path(tmp) / "img.tar"
            subprocess.check_call(["docker", "export", cid, "-o", str(tar_path)])
            extract = Path(tmp) / "root"
            extract.mkdir()
            with tarfile.open(tar_path, "r") as tar:
                members = {m.name.rstrip("/") for m in tar.getmembers()}
                for bad in FORBIDDEN_PATHS:
                    if bad in members or any(m == bad or m.startswith(bad + "/") for m in members):
                        print(f"FAIL: forbidden path in image: {bad}")
                        return 1
                # Extract only /app for content scan
                app_members = [m for m in tar.getmembers() if m.name.startswith("app/")]
                tar.extractall(extract, members=app_members)

            hits: list[str] = []
            for path in (extract / "app").rglob("*"):
                if not path.is_file() or path.suffix.lower() in SKIP_SUFFIXES:
                    continue
                if path.stat().st_size > 5_000_000:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if SECRET_RE.search(text):
                    hits.append(str(path.relative_to(extract)))
            if hits:
                print("FAIL: secret-like content in:")
                for h in hits:
                    print(f"  {h}")
                return 1
    finally:
        subprocess.call(["docker", "rm", "-f", cid], stdout=subprocess.DEVNULL)

    print(f"OK: no secrets found in {image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
