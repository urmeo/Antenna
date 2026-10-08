import json
from dataclasses import asdict

import pytest

from antenna.__main__ import main
from antenna.results import load, validate
from antenna.tables import render_all


@pytest.mark.parametrize("malformed", [
    "<!-- BEGIN:bandwidth-table -->\nstale\n",
    "<!-- END:bandwidth-table -->\n",
    "<!-- END:bandwidth-table -->\nstale\n<!-- BEGIN:bandwidth-table -->\n",
    "<!-- BEGIN:results-table -->\nduplicate\n<!-- END:results-table -->\n",
])
def test_write_rejects_malformed_markers_before_changing_any_table(tmp_path, capsys, malformed):
    readme = tmp_path / "README.md"
    original = "<!-- BEGIN:results-table -->\nstale\n<!-- END:results-table -->\n" + malformed
    readme.write_text(original)
    assert main(["tables", "--write", "--readme", str(readme)]) == 2
    assert readme.read_text() == original
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "marker" in captured.err
    assert "Traceback" not in captured.err


def test_write_rejects_overlapping_blocks_without_changing_readme(tmp_path, capsys):
    readme = tmp_path / "README.md"
    original = ("<!-- BEGIN:results-table -->\n<!-- BEGIN:bandwidth-table -->\n"
                "stale\n<!-- END:results-table -->\n<!-- END:bandwidth-table -->\n")
    readme.write_text(original)
    assert main(["tables", "--write", "--readme", str(readme)]) == 2
    assert readme.read_text() == original
    assert "overlap" in capsys.readouterr().err


def test_custom_geometry_labels_remain_in_one_markdown_cell():
    ds = load()
    ds.geometries[0].name = "Circular | alternate feed\r\nsecond line"
    validate(ds)
    for report in render_all(ds).values():
        assert len(report.splitlines()) == len(ds.geometries) + 2
        assert "Circular \\| alternate feed<br>second line" in report.splitlines()[2]


def test_backslash_before_pipe_preserves_a_literal_name():
    ds = load()
    ds.geometries[0].name = "Circular \\| feed"
    row = render_all(ds)["results-table"].splitlines()[2]
    assert "Circular " + "\\" * 3 + "| feed" in row


def test_custom_json_names_roundtrip_through_write_and_check(tmp_path, capsys):
    ds = load()
    ds.geometries[0].name = "Circular | alternate feed\nsecond line"
    raw = asdict(ds)
    geometries = raw.pop("geometries")
    data = tmp_path / "results.json"
    data.write_text(json.dumps({"meta": raw, "geometries": geometries}))
    readme = tmp_path / "README.md"
    readme.write_text("<!-- BEGIN:results-table -->\nstale\n<!-- END:results-table -->\n")
    args = ["tables", "--data", str(data), "--readme", str(readme)]
    assert main(args + ["--write"]) == 0
    assert main(args + ["--check"]) == 0
    assert "Circular \\| alternate feed<br>second line" in readme.read_text()
    capsys.readouterr()


@pytest.mark.parametrize("body", ["stale", "  \nstale\n  ", "\n"])
def test_write_normalizes_compact_marked_blocks_and_is_idempotent(tmp_path, capsys, body):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n<!-- BEGIN:results-table -->" + body + "<!-- END:results-table -->\ntail\n")
    args = ["tables", "--readme", str(readme)]
    assert main(args + ["--write"]) == 0
    assert main(args + ["--check"]) == 0
    expected = ("# Title\n<!-- BEGIN:results-table -->\n" + render_all(load())["results-table"] +
                "\n<!-- END:results-table -->\ntail\n")
    assert readme.read_text() == expected
    assert main(args + ["--write"]) == 0
    assert readme.read_text() == expected
    capsys.readouterr()
