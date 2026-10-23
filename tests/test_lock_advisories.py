"""uv.lock must not pin a package below the version that fixes a Critical or High advisory."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

LOCK = Path(__file__).resolve().parents[1] / "uv.lock"

# (advisory, package, first fixed version) as reported by the Snyk forks scan and osv.dev.
FIXED_IN = [
    ("GHSA-6q48-6c7w-9gw2", "certifi", "2026.10.19"),
    ("GHSA-82r6-8w77-94w6", "anyio", "4.14.2"),
    ("GHSA-8988-9cw3-xx77", "urllib3", "2.8.0"),
    ("GHSA-vxq7-64xx-v4gw", "urllib3", "2.8.0"),
    ("GHSA-8ppf-4f7h-5ppj", "pyasn1", "0.6.4"),
    ("GHSA-hm4w-wwcw-mr6r", "pyasn1", "0.6.4"),
    ("GHSA-m4p7-r5rc-7g4j", "pyasn1", "0.6.4"),
    ("GHSA-j5g9-f88f-gfj3", "httplib2", "0.32.0"),
]


def _version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split("."))


def _locked(package: str) -> tuple[int, ...]:
    text = LOCK.read_text(encoding="utf-8")
    match = re.search(rf'^name = "{package}"\nversion = "([^"]+)"', text, re.MULTILINE)
    assert match, f"{package} is not in uv.lock"
    return _version(match.group(1))


@pytest.mark.parametrize(("advisory", "package", "fixed"), FIXED_IN)
def test_locked_version_includes_the_fix(advisory, package, fixed):
    assert _locked(package) >= _version(fixed), advisory
