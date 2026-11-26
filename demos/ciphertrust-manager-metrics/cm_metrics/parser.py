"""Prometheus exposition text parser."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


LABEL_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="((?:\\.|[^"\\])*)"')
SAMPLE_RE = re.compile(
    r"^([a-zA-Z_:][a-zA-Z0-9_:]*)"
    r"(?:\{([^}]*)\})?"
    r"\s+"
    r"([-+]?(?:Inf|Nan|[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?))"
    r"(?:\s+(\d+))?"
    r"\s*$"
)


def _unescape(value: str) -> str:
    return value.replace(r"\\", "\\").replace(r"\"", '"').replace(r"\n", "\n")


def parse_labels(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    return {m.group(1): _unescape(m.group(2)) for m in LABEL_RE.finditer(raw)}


@dataclass
class Sample:
    name: str
    labels: dict[str, str] = field(default_factory=dict)
    value: float = 0.0
    timestamp_ms: int | None = None

    @property
    def fingerprint(self) -> str:
        parts = [f'{k}="{v}"' for k, v in sorted(self.labels.items())]
        return f"{self.name}{{{','.join(parts)}}}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "labels": self.labels,
            "value": self.value,
            "fingerprint": self.fingerprint,
        }


def parse_prometheus_text(text: str) -> list[Sample]:
    samples: list[Sample] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = SAMPLE_RE.match(line)
        if not match:
            continue
        name, labels_raw, value_raw, ts_raw = match.groups()
        try:
            if value_raw in {"+Inf", "Inf"}:
                value = float("inf")
            elif value_raw == "-Inf":
                value = float("-inf")
            elif value_raw.lower() == "nan":
                continue
            else:
                value = float(value_raw)
        except ValueError:
            continue
        samples.append(
            Sample(
                name=name,
                labels=parse_labels(labels_raw),
                value=value,
                timestamp_ms=int(ts_raw) if ts_raw else None,
            )
        )
    return samples


def labels_match(sample_labels: dict[str, str], required: dict[str, str] | None) -> bool:
    if not required:
        return True
    for key, expected in required.items():
        actual = sample_labels.get(key)
        if actual is None:
            return False
        if expected.startswith("!") and actual == expected[1:]:
            return False
        if not expected.startswith("!") and actual != expected:
            return False
    return True


def find_samples(
    samples: list[Sample],
    name: str,
    labels: dict[str, str] | None = None,
) -> list[Sample]:
    return [s for s in samples if s.name == name and labels_match(s.labels, labels)]


def sum_samples(samples: list[Sample], name: str, labels: dict[str, str] | None = None) -> float:
    return sum(s.value for s in find_samples(samples, name, labels))


def first_value(samples: list[Sample], name: str, labels: dict[str, str] | None = None) -> float | None:
    found = find_samples(samples, name, labels)
    return found[0].value if found else None
