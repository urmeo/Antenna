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
