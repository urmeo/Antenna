from pathlib import Path

import pytest

from antenna import fom, tables
from antenna.results import load


def test_readme_tables_match_source():
    text = (Path(__file__).parents[2] / "README.md").read_text(encoding="utf-8")
    for name in ("results-table", "bandwidth-table"):
        actual = text.split("<!-- BEGIN:%s -->\n" % name)[1].split("\n<!-- END:%s -->" % name)[0]
        assert actual == tables.render_all(load())[name]


def test_reports_distinguish_recorded_and_derived_numbers():
    report = tables.results_table(load())
    assert "1.125" in report and "1.052" in report
    bands = tables.bandwidth_table(load())
    assert "3.12" in bands and "3.06" in bands
    assert "6.56" in bands


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf")])
def test_pattern_area_rejects_invalid_area(value):
    with pytest.raises(ValueError):
        fom.gain_per_area(5.54, value)


def test_pattern_proxy_is_not_labelled_verified_gain():
    report = tables.figure_of_merit_table(load())
    assert "Pattern proxy" in report and "Gain ÷ area" not in report
