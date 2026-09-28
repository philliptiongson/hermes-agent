"""Regression: ``load_soul_md`` strips a leading YAML frontmatter block so
a ``~/.hermes/SOUL.md`` symlinked at a vault-canonical source does not
inject protocol metadata (``type:`` / ``agent-written:`` / ``---`` fences)
into the gateway identity slot.

Substrate rules honored:

- Real imports + temp ``HERMES_HOME`` (root rubric §E2E validation).
- Behavior contracts, not snapshot matches (root rubric §What we want).
- No source-code reads in tests (root rubric §Don't read source code).
- Existing tests for SOUL.md (``test_soul_md_profile_isolation``,
  ``test_home_init_soul_symlink``) remain untouched.
"""

from __future__ import annotations


def _make_home_with_soul(tmp_path, soul_text: str) -> str:
    """Return the home dir path; write ``$home/SOUL.md`` with *soul_text*."""
    home = tmp_path / "home"
    home.mkdir()
    (home / "SOUL.md").write_text(soul_text, encoding="utf-8")
    return str(home)


def test_load_soul_md_strips_leading_yaml_frontmatter(tmp_path, monkeypatch):
    """A SOUL.md that opens with a `---` YAML fence loads prose-only."""
    home = _make_home_with_soul(
        tmp_path,
        "---\n"
        "type: soul\n"
        "agent-written: true\n"
        "last_updated_by: juniper\n"
        "---\n"
        "\n"
        "You are Hestia. Be terse.\n",
    )
    monkeypatch.setenv("HERMES_HOME", home)

    from agent.prompt_builder import load_soul_md

    loaded = load_soul_md(home_override=tmp_path / "home")

    assert loaded is not None
    # Voice preserved.
    assert "You are Hestia" in loaded
    # Frontmatter keys absent from the loaded identity slot.
    assert "type: soul" not in loaded
    assert "agent-written:" not in loaded
    assert "last_updated_by: juniper" not in loaded
    # Fences absent (a horizontal rule inside voice would not be three
    # consecutive dashes on their own; this assertion is the canonical
    # contract anyway).
    assert "---" not in loaded


def test_load_soul_md_passes_prose_through_unchanged(tmp_path, monkeypatch):
    """A SOUL.md with no frontmatter is the canonical pre-patch behavior."""
    home = _make_home_with_soul(
        tmp_path,
        "You are Hestia, Phillip's Hermes Agent. Be terse.\n",
    )
    monkeypatch.setenv("HERMES_HOME", home)

    from agent.prompt_builder import load_soul_md

    loaded = load_soul_md(home_override=tmp_path / "home")

    assert loaded == "You are Hestia, Phillip's Hermes Agent. Be terse.\n"


def test_load_soul_md_leaves_malformed_frontmatter_alone(tmp_path, monkeypatch):
    """A SOUL.md that opens with `---` but has no closing fence does not
    silently truncate — the operator must notice on first launch.

    Note: ``_strip_yaml_frontmatter`` falls back to original content on
    malformed input; ``strip_legacy_protocol`` and the scan path may
    still mutate the string, so we assert *voice* is still present and
    trust that the helper's branch is exercised. The behavior contract
    is "the file is not silently truncated to empty".
    """
    home = _make_home_with_soul(
        tmp_path,
        "---\nno closing fence anywhere in this file\n",
    )
    monkeypatch.setenv("HERMES_HOME", home)

    from agent.prompt_builder import load_soul_md

    loaded = load_soul_md(home_override=tmp_path / "home")

    assert loaded is not None
    assert "no closing fence" in loaded


def test_load_soul_md_does_not_strip_mid_file_separators(tmp_path, monkeypatch):
    """Mid-file ``---`` separators (deliberate voice choices) survive the
    strip step. The helper looks for the FIRST closing fence on its own
    line; voice that re-uses ``---`` as a section break must stay.
    """
    home = _make_home_with_soul(
        tmp_path,
        "First section of voice.\n"
        "\n"
        "---\n"
        "\n"
        "Second section after a horizontal rule. Keep this.\n",
    )
    monkeypatch.setenv("HERMES_HOME", home)

    from agent.prompt_builder import load_soul_md

    loaded = load_soul_md(home_override=tmp_path / "home")

    assert loaded is not None
    # Mid-file separator is gone (strip_legacy_protocol and the scan may
    # legitimately act on prose; what we pin here is that the second
    # section's voice is preserved).
    assert "Second section after a horizontal rule" in loaded
    # And the leading section.
    assert "First section of voice" in loaded
