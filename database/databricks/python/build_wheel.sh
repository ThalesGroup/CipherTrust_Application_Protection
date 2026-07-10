#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${REPO_ROOT}/dist"

mkdir -p "${DIST_DIR}"

cd "${REPO_ROOT}"
if ! python -m build --wheel --no-isolation --outdir "${DIST_DIR}"; then
  python setup.py bdist_wheel --dist-dir "${DIST_DIR}"
fi
