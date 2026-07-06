import textwrap

from antenna import tables
from antenna.results import load


def test_num_uses_unicode_minus():
    assert tables._num(-53.08, 2) == "−53.08"
    assert tables._num(3.12, 2) == "3.12"
    assert tables._signed(0.85, 2) == "+0.85"


def test_inject_is_idempotent(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(textwrap.dedent("""\
        # Title
        <!-- BEGIN:sim-table -->
        stale
        <!-- END:sim-table -->
        tail
    """))
    ds = load()
    assert tables.inject(str(readme), ds) == ["sim-table"]
    once = readme.read_text()
    tables.inject(str(readme), ds)
    assert readme.read_text() == once
    assert "stale" not in once and "tail" in once


def test_inject_without_markers_changes_nothing(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# No markers here\n")
    assert tables.inject(str(readme), load()) == []
    assert readme.read_text() == "# No markers here\n"
