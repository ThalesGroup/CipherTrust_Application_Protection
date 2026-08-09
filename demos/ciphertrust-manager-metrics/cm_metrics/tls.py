"""HTTPS helpers — ensure a self-signed cert/key exist for the Flask app."""

from __future__ import annotations

import datetime as dt
import ipaddress
import logging
import os
import socket
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

logger = logging.getLogger(__name__)


def ensure_self_signed_cert(
    cert_path: Path,
    key_path: Path,
    *,
    common_name: str = "CM Metrics",
    days: int = 825,
    extra_ips: list[str] | None = None,
    extra_dns: list[str] | None = None,
    force: bool = False,
) -> tuple[Path, Path]:
    """
    Return (cert, key) paths, generating a self-signed certificate if either file is missing.

    Also picks up SSL_EXTRA_SANS from the environment (comma-separated IPs and/or DNS names)
    so public cloud IPs can be added without code changes.
    """
    cert_path = Path(cert_path)
    key_path = Path(key_path)
    if not force and cert_path.is_file() and key_path.is_file():
        return cert_path, key_path

    cert_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Generating self-signed TLS certificate at %s", cert_path)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CM Metrics"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
    )

    san_entries: list[x509.GeneralName] = [
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        x509.IPAddress(ipaddress.IPv6Address("::1")),
    ]
    seen: set[str] = {"localhost", "127.0.0.1", "::1"}

    def _add_dns(name: str) -> None:
        name = (name or "").strip().rstrip(".")
        if not name or name.lower() in seen:
            return
        # If it looks like an IP, treat as IP SAN instead of DNS
        try:
            ipaddress.ip_address(name)
            _add_ip(name)
            return
        except ValueError:
            pass
        seen.add(name.lower())
        san_entries.append(x509.DNSName(name))

    def _add_ip(raw: str) -> None:
        raw = (raw or "").strip()
        if not raw or raw in seen:
            return
        try:
            addr = ipaddress.ip_address(raw)
        except ValueError:
            return
        # Skip link-local / unspecified noise
        if addr.is_unspecified or addr.is_link_local:
            return
        seen.add(raw)
        san_entries.append(x509.IPAddress(addr))

    # Explicit extras (args + env SSL_EXTRA_SANS=ip,or,dns)
    for raw in list(extra_ips or []) + list(extra_dns or []):
        _add_dns(raw)  # routes IPs to _add_ip
    for raw in (os.getenv("SSL_EXTRA_SANS") or "").split(","):
        raw = raw.strip()
        if raw:
            _add_dns(raw)

    # If CN is an IP, include it as SAN IP as well (browsers ignore CN alone).
    try:
        ipaddress.ip_address(common_name.strip())
        _add_ip(common_name.strip())
    except ValueError:
        if common_name and common_name != "CM Metrics":
            _add_dns(common_name)

    # Hostname + FQDN
    try:
        hostname = socket.gethostname().strip()
        _add_dns(hostname)
        _add_dns(socket.getfqdn())
    except Exception:  # noqa: BLE001
        pass

    # Local interface IPs so https://10.x.x.x matches the cert SAN
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            _add_ip(info[4][0])
    except Exception:  # noqa: BLE001
        pass
    try:
        # UDP "connect" trick to discover the primary outbound IPv4 (often private on cloud VMs)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            _add_ip(s.getsockname()[0])
    except Exception:  # noqa: BLE001
        pass

    now = dt.datetime.now(dt.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=5))
        .not_valid_after(now + dt.timedelta(days=days))
        .add_extension(x509.SubjectAlternativeName(san_entries), critical=False)
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )

    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    logger.info(
        "TLS cert SANs: %s",
        ", ".join(
            (
                f"DNS:{n.value}"
                if isinstance(n, x509.DNSName)
                else f"IP:{n.value}"
            )
            for n in san_entries
        ),
    )
    return cert_path, key_path
