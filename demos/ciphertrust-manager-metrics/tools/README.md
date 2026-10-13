# CipherTrust Manager CLI (`ksctl`) — not stored in git

Healthcheck needs `ksctl` on the machine (or inside the Docker image).

## Automatic download (preferred)

When you add a CipherTrust Manager appliance, CM Metrics downloads:

`https://<cm-host>/downloads/ksctl_images.zip`

That endpoint does **not** require authentication. The zip contains all three:

| Zip entry | Used on | Saved as |
|-----------|---------|----------|
| `ksctl-linux-amd64` | Linux | `tools/ksctl-linux-amd64` (+ `tools/ksctl` link) |
| `ksctl-darwin-amd64` | macOS | `tools/ksctl-darwin-amd64` |
| `ksctl-win-amd64.exe` | Windows | `tools/ksctl.exe` |

Only the binary for the **current OS** is extracted. Wrong-platform files in `tools/` are ignored.

If `ksctl` is still missing when you click **Run healthcheck**, the same download is attempted from that appliance’s host.

## Docker Hub image

[`sanyambassi/ciphertrust-metrics`](https://hub.docker.com/r/sanyambassi/ciphertrust-metrics) already
includes Linux `ksctl`, so no download is needed inside the published image.

## Manual install

1. Download `ksctl_images.zip` from any CM: `/downloads/ksctl_images.zip`
2. Place the binary here as `ksctl-linux-amd64`, `ksctl.exe`, etc.
3. Or install `ksctl` on your `PATH`
