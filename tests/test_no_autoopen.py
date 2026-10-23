"""The test run must never launch the developer's Obsidian app.

`vault.print_save_links` auto-opens every saved note through `open` / `xdg-open`
unless RESEARCH_AUTOOPEN=0. A test that saves a note (the deep-research fallback
test does, under a fake HOME) therefore started the real Obsidian app on the
machine running pytest, pointed at a vault that is not the user's. These tests
put a recording opener on PATH and assert it is never called.
"""

from __future__ import annotations

import os
import stat
import sys

import pytest

from scripts.research.lib import vault

pytestmark = pytest.mark.skipif(os.name == "nt", reason="the stub openers are POSIX shell scripts")


@pytest.fixture
def opener_log(tmp_path, monkeypatch):
    """Recording stubs for every opener print_save_links can pick, first on PATH."""
    log = tmp_path / "opener.log"
    stubs = tmp_path / "stubs"
    stubs.mkdir()
    for name in ("open", "xdg-open"):
        stub = stubs / name
        stub.write_text(f'#!/bin/sh\necho "{name} $*" >> "{log}"\n', encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{stubs}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setattr(vault, "VAULT_PATH", tmp_path / "vault")
    (tmp_path / "vault").mkdir()
    return log


def _save_note(tmp_path):
    note = tmp_path / "vault" / "Research" / "note.md"
    note.parent.mkdir(parents=True)
    note.write_text("x", encoding="utf-8")
    vault.print_save_links(note, file=sys.stderr)


def test_the_suite_disables_autoopen_by_default():
    assert os.environ.get("RESEARCH_AUTOOPEN") == "0"


def test_saving_a_note_does_not_call_an_opener(tmp_path, opener_log):
    _save_note(tmp_path)
    assert not opener_log.exists(), opener_log.read_text(encoding="utf-8")


def test_the_recording_stub_does_see_an_enabled_autoopen(tmp_path, opener_log, monkeypatch):
    """Control: the stub would have caught a call, so the empty log above means something."""
    monkeypatch.setenv("RESEARCH_AUTOOPEN", "1")
    _save_note(tmp_path)
    assert "obsidian://open" in opener_log.read_text(encoding="utf-8")
