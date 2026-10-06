import json
import math
from dataclasses import asdict

import pytest

from antenna.check import consistency_issues
from antenna.results import load, validate


def _raw():
    ds = load()
    return {"meta": {key: value for key, value in asdict(ds).items() if key != "geometries"},
            "geometries": asdict(ds)["geometries"]}


def test_load_rejects_missing_fields_and_bad_structure(tmp_path):
    path = tmp_path / "results.json"
    for raw in ({}, [], {"meta": {}, "geometries": []}):
        path.write_text(json.dumps(raw))
        with pytest.raises(ValueError):
            load(str(path))


def test_json_nonfinite_and_duplicate_keys_are_rejected(tmp_path):
    path = tmp_path / "results.json"
    for text in ('{"meta": {}, "meta": {}}', '{"number": NaN}', '{"number": Infinity}'):
        path.write_text(text)
        with pytest.raises(ValueError):
            load(str(path))


def test_unrepresentable_json_integer_is_a_validation_error(tmp_path):
    raw = _raw()
    raw["meta"]["design_frequency_ghz"] = 10 ** 400
    path = tmp_path / "results.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="finite number"):
        load(str(path))


def test_empty_and_duplicate_geometry_lists_are_rejected():
    ds = load()
    ds.geometries.append(ds.geometries[0])
    with pytest.raises(ValueError, match="duplicate geometry"):
        validate(ds)
    ds.geometries.clear()
    assert consistency_issues(ds)[0].level == "error"


@pytest.mark.parametrize("field,value", [("s11_db", math.nan), ("vswr", math.inf), ("vswr", .5),
                                       ("bandwidth_pct", -1), ("bandwidth_pct", math.nan),
                                       ("band_edges_ghz", [3, 2]), ("band_edges_ghz", [2]),
                                       ("band_edges_ghz", [2, math.nan]), ("bandwidth_pending", "false"),
                                       ("main_lobe_db", math.nan), ("s11_db", 2)])
def test_invalid_simulation_is_an_error_even_when_bandwidth_pending(field, value):
    ds = load()
    ds.geometries[0].simulation.bandwidth_pending = True
    setattr(ds.geometries[0].simulation, field, value)
    issues = consistency_issues(ds)
    assert issues and issues[0].level == "error"
    assert issues[0].field == "validation"


@pytest.mark.parametrize("field,value", [("s11_db", math.nan), ("vswr", -1), ("verified", "false"), ("read_at", "")])
def test_invalid_unverified_measurement_is_an_error(field, value):
    ds = load()
    setattr(ds.geometries[0].measurement, field, value)
    assert consistency_issues(ds)[0].level == "error"


@pytest.mark.parametrize("field,value", [("design_frequency_ghz", math.nan), ("design_frequency_ghz", 0),
                                       ("ground_plane_mm", {"width": 75}), ("feed_mm", {"width": -1, "patch_gap": 1})])
def test_invalid_metadata_is_rejected(field, value):
    ds = load()
    setattr(ds, field, value)
    assert consistency_issues(ds)[0].level == "error"


def test_invalid_dimensions_and_nonboolean_flags_are_rejected():
    ds = load()
    ds.geometries[0].dimensions_mm = {}
    assert consistency_issues(ds)[0].level == "error"
    ds = load()
    ds.geometries[0].highlight = 1
    assert consistency_issues(ds)[0].level == "error"
    ds = load()
    ds.substrate.epsilon_r = math.nan
    assert consistency_issues(ds)[0].level == "error"


def test_load_retains_historical_values_and_pending_status(tmp_path):
    raw = _raw()
    path = tmp_path / "results.json"
    path.write_text(json.dumps(raw))
    ds = load(str(path))
    assert ds.geometries[0].simulation.bandwidth_pct == 3.12
    assert ds.geometries[0].measurement.vswr == 1.125
    issues = consistency_issues(ds)
    assert sum(issue.level == "warning" for issue in issues) == 8
    assert not any(issue.level == "error" for issue in issues)
