import json

import pytest

from antenna.__main__ import main


def test_invalid_data_reports_a_short_error(tmp_path, capsys):
    data = tmp_path / "results.json"
    data.write_text(json.dumps({}))
    assert main(["check", "--data", str(data)]) != 0
    captured = capsys.readouterr()
    assert "invalid results structure" in captured.err
    assert "Traceback" not in captured.err


def test_ingest_validates_every_input_before_printing(tmp_path, capsys):
    valid = tmp_path / "valid.s1p"
    valid.write_text("# GHz S DB\n2.4 -5 0\n2.45 -20 0\n2.5 -5 0\n")
    assert main(["ingest", str(valid), str(tmp_path / "missing.s1p")]) != 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "missing.s1p" in captured.err


def test_ingest_exposes_reference_and_unavailable_bandwidth(tmp_path, capsys):
    path = tmp_path / "censored.s1p"
    path.write_text("# R 75 DB GHz\n2.4 -20 0\n2.45 -30 0\n")
    assert main(["ingest", str(path)]) == 0
    output = capsys.readouterr().out
    assert "75.00" in output and "n/a" in output
    assert "no complete band" in output


def test_default_readme_is_in_current_directory(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text("<!-- BEGIN:results-table -->\nstale\n<!-- END:results-table -->\n")
    assert main(["tables", "--write"]) == 0
    assert "stale" not in readme.read_text()
    assert main(["tables", "--check"]) == 0
    capsys.readouterr()
    readme.write_text(readme.read_text().replace("-53.08", "-50.00").replace("−53.08", "−50.00"))
    assert main(["tables", "--check"]) == 1


def test_tables_without_markers_fail(tmp_path, capsys):
    readme = tmp_path / "README.md"
    readme.write_text("# No markers\n")
    assert main(["tables", "--write", "--readme", str(readme)]) != 0
    assert "no recognized table markers" in capsys.readouterr().err


@pytest.mark.parametrize("arguments", [["--s1p"], ["--s1p", "missing.s1p"]])
def test_plot_rejects_bad_inputs_before_creating_outputs(tmp_path, capsys, arguments):
    output = tmp_path / "output"
    assert main(["plot", "--out", str(output)] + arguments) != 0
    assert not output.exists()
    assert "Traceback" not in capsys.readouterr().err


def test_plot_checks_results_before_writing_overlay(tmp_path, capsys):
    data = tmp_path / "bad.json"
    data.write_text("{}")
    sweep = tmp_path / "valid.s1p"
    sweep.write_text("# GHz S DB\n2.45 -20 0\n")
    output = tmp_path / "output"
    assert main(["plot", "--data", str(data), "--out", str(output), "--s1p", str(sweep)]) != 0
    assert not output.exists()
    capsys.readouterr()


def test_plot_missing_extra_has_install_message(tmp_path, monkeypatch, capsys):
    from antenna import plots

    def missing():
        raise ModuleNotFoundError("No module named matplotlib", name="matplotlib")

    monkeypatch.setattr(plots, "_pyplot", missing)
    output = tmp_path / "output"
    assert main(["plot", "--out", str(output)]) != 0
    assert "plots extra" in capsys.readouterr().err
    assert not output.exists()
