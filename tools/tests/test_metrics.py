import math

import pytest

from antenna import metrics


def test_s11_vswr_roundtrip():
    for vswr in (1.05, 1.3, 2.0, 3.5):
        s11 = metrics.s11_db_from_vswr(vswr)
        assert abs(metrics.vswr_from_s11_db(s11) - vswr) < 1e-9


def test_known_pairs():
    assert abs(metrics.vswr_from_s11_db(-53.08) - 1.004) < 0.005
    assert abs(metrics.vswr_from_s11_db(-16.38) - 1.357) < 0.005
    assert abs(metrics.vswr_from_s11_db(-14.78) - 1.446) < 0.005


def test_bandwidth_from_edges():
    assert abs(metrics.fractional_bandwidth_pct(2.399, 2.4735) - 3.06) < 0.1
    assert abs(metrics.fractional_bandwidth_pct(2.399, 2.4735, reference=2.45) - 3.04) < 0.1


def test_total_reflection_is_infinite():
    assert metrics.vswr_from_s11_db(0.0) == float("inf")
    assert metrics.s11_db_from_vswr(1.0) == float("-inf")
    assert metrics.s11_db_from_vswr(float("inf")) == 0.0


@pytest.mark.parametrize("vswr", [.5, 0, -1, -math.inf, math.nan, True])
def test_rejects_invalid_vswr(vswr):
    with pytest.raises(ValueError):
        metrics.s11_db_from_vswr(vswr)


def test_near_unity_vswr_is_finite_and_positive_s11_does_not_overflow():
    assert math.isfinite(metrics.s11_db_from_vswr(math.nextafter(1, 2)))
    assert metrics.vswr_from_s11_db(1e300) == math.inf
    assert metrics.vswr_from_s11_db(-math.inf) == 1


@pytest.mark.parametrize("value", [math.nan, math.inf, True, "-20"])
def test_invalid_s11_is_rejected(value):
    for function in (metrics.vswr_from_s11_db, metrics.reflection_coefficient):
        with pytest.raises(ValueError):
            function(value)


@pytest.mark.parametrize("low,high,reference", [(3, 2, None), (-1, 2, None), (0, 0, None),
                                              (1, math.inf, None), (1, 2, 0), (1, 2, math.nan)])
def test_invalid_bandwidth_inputs(low, high, reference):
    with pytest.raises(ValueError):
        metrics.fractional_bandwidth_pct(low, high, reference)


def test_zero_width_band_and_dc_edge():
    assert metrics.fractional_bandwidth_pct(2, 2) == 0
    assert metrics.fractional_bandwidth_pct(0, 2) == 200
