from antenna import metrics
from antenna.check import consistency_issues
from antenna.results import load


def test_simulation_rows_are_self_consistent():
    ds = load()
    for g in ds.geometries:
        implied = metrics.vswr_from_s11_db(g.simulation.s11_db)
        assert abs(implied - g.simulation.vswr) < 0.01, g.name


def test_no_hard_errors_in_canonical_data():
    ds = load()
    errors = [i for i in consistency_issues(ds) if i.level == "error"]
    assert errors == [], errors


def test_checker_flags_measurement_discrepancy():
    ds = load()
    warnings = [i for i in consistency_issues(ds) if i.level == "warning" and i.field == "meas VSWR"]
    assert len(warnings) == 5  # every measured row currently disagrees with its S11
