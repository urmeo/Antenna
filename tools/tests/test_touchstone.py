import textwrap

from antenna.touchstone import read_s1p


def test_read_s1p_db_format(tmp_path):
    path = tmp_path / "sample.s1p"
    path.write_text(textwrap.dedent("""\
        ! circular patch measurement
        # GHz S DB R 50
        2.40 -12.0 -20
        2.45 -28.0 -30
        2.50 -11.0 -25
    """))
    sweep = read_s1p(str(path))
    assert sweep.freqs_ghz == [2.40, 2.45, 2.50]
    assert sweep.s11_db == [-12.0, -28.0, -11.0]


def test_resonance_and_band_edges(tmp_path):
    from antenna.touchstone import band_edges, resonance
    path = tmp_path / "sweep.s1p"
    path.write_text(textwrap.dedent("""\
        # GHz S DB R 50
        2.30 -6.0 0
        2.40 -14.0 0
        2.45 -32.0 0
        2.50 -13.0 0
        2.60 -5.0 0
    """))
    sweep = read_s1p(str(path))
    f_res, depth = resonance(sweep)
    assert f_res == 2.45 and depth == -32.0
    lo, hi = band_edges(sweep)
    assert lo == 2.40 and hi == 2.50


def test_ma_format_and_hz_scaling(tmp_path):
    path = tmp_path / "ma.s1p"
    path.write_text("# HZ S MA R 50\n2450000000 0.1 -20\n")
    sweep = read_s1p(str(path))
    assert sweep.freqs_ghz == [2.45]
    assert abs(sweep.s11_db[0] - (-20.0)) < 1e-9


def test_rejects_empty_and_malformed(tmp_path):
    import pytest
    empty = tmp_path / "empty.s1p"
    empty.write_text("! comments only\n# GHz S DB R 50\n")
    with pytest.raises(ValueError):
        read_s1p(str(empty))
    bad = tmp_path / "bad.s1p"
    bad.write_text("# GHz S DB R 50\n2.45 -20\n")
    with pytest.raises(ValueError):
        read_s1p(str(bad))
