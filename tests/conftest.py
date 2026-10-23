"""Suite-wide fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _no_obsidian_autoopen(monkeypatch):
    """vault.print_save_links opens each saved note in the real Obsidian app unless
    RESEARCH_AUTOOPEN=0. A test that saves a note must not launch it; a test that
    wants the opener sets the variable itself."""
    monkeypatch.setenv("RESEARCH_AUTOOPEN", "0")
