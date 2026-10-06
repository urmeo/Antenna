import textwrap
import math

import pytest

from antenna.touchstone import Sweep, band_edges, read_s1p, resonance


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
    assert lo == pytest.approx(2.35)
    assert hi == pytest.approx(2.5375)


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


@pytest.mark.parametrize("header", ["# MHz S DB R 50", "# R 50 DB S MHz", "# MHz DB", "# DB MHz R 75"])
def test_reordered_and_partial_options(tmp_path, header):
    path = tmp_path / "options.s1p"
    path.write_text(header + "\n2450 -20 0\n")
    sweep = read_s1p(str(path))
    assert sweep.freqs_ghz == [2.45]
    assert sweep.s11_db == [-20]
    assert sweep.reference_ohms == (75 if "75" in header else 50)


def test_empty_option_line_uses_defaults_and_later_lines_are_ignored(tmp_path):
    path = tmp_path / "defaults.s1p"
    path.write_text("#\n2.4 0.1 0\n# MHz Z DB R -50\n2.5 0.2 0\n")
    sweep = read_s1p(str(path))
    assert sweep.freqs_ghz == [2.4, 2.5]
    assert sweep.s11_db == pytest.approx([-20, 20 * math.log10(.2)])


@pytest.mark.parametrize("header", ["# GHz Z RI R 50", "# GHz Y DB", "# THz S DB", "# GHz S DB R -50",
                                   "# GHz S DB R 0", "# GHz S DB R nan", "# R inf", "# R", "# R wrong",
                                   "# GHz MHz S DB", "# DB MA", "# S S", "# R 50 R 75"])
def test_rejects_unsupported_or_invalid_options(tmp_path, header):
    path = tmp_path / "bad-options.s1p"
    path.write_text(header + "\n2.45 0.1 0\n")
    with pytest.raises(ValueError):
        read_s1p(str(path))


@pytest.mark.parametrize("text", ["2.45 -20 0\n", "[Version] 2.0\n# GHz S DB\n2.45 -20 0\n",
                                  "# GHz S DB\n2.45 -20 0 1 0\n"])
def test_requires_v1_option_line_and_one_port_data(tmp_path, text):
    path = tmp_path / "unsupported.s1p"
    path.write_text(text)
    with pytest.raises(ValueError):
        read_s1p(str(path))


@pytest.mark.parametrize("row", ["nan -20 0", "inf -20 0", "2.45 nan 0", "2.45 -20 inf", "-2.45 -20 0"])
def test_rejects_invalid_data_values(tmp_path, row):
    path = tmp_path / "bad-data.s1p"
    path.write_text("# GHz S DB\n" + row + "\n")
    with pytest.raises(ValueError):
        read_s1p(str(path))


def test_ma_rejects_negative_magnitude_and_zero_reflection_is_valid(tmp_path):
    path = tmp_path / "magnitude.s1p"
    path.write_text("# GHz S MA\n2.45 -0.1 0\n")
    with pytest.raises(ValueError, match="nonnegative"):
        read_s1p(str(path))
    for fmt in ("MA", "RI"):
        path.write_text("# GHz S %s\n0 0 0\n2.45 .1 0\n" % fmt)
        sweep = read_s1p(str(path))
        assert sweep.s11_db == [-math.inf, -20]


@pytest.mark.parametrize("frequencies", [[2.45, 2.45], [2.5, 2.4]])
def test_requires_strictly_ascending_frequencies(tmp_path, frequencies):
    path = tmp_path / "order.s1p"
    path.write_text("# GHz S DB\n" + "".join("%s -20 0\n" % f for f in frequencies))
    with pytest.raises(ValueError, match="strictly increasing"):
        read_s1p(str(path))


@pytest.mark.parametrize("frequencies,values", [([], []), ([1, 2], [-20]), ([1], [math.nan]), ([1], [math.inf])])
def test_sweep_validates_direct_input(frequencies, values):
    with pytest.raises(ValueError):
        Sweep(frequencies, values)


def test_sweep_mutation_is_revalidated():
    sweep = Sweep([1, 2], [-5, -20])
    sweep.freqs_ghz.clear()
    for function in (resonance, band_edges):
        with pytest.raises(ValueError):
            function(sweep)


def test_disjoint_bands_are_not_merged():
    sweep = Sweep([1, 2, 3, 4, 5, 6, 7], [-5, -15, -5, -5, -20, -20, -5])
    assert band_edges(sweep) == pytest.approx((4 + 1 / 3, 6 + 2 / 3))


def test_exact_threshold_crossings_and_single_threshold_point():
    assert band_edges(Sweep([1, 2, 3, 4, 5], [-5, -10, -20, -10, -5])) == (2, 4)
    assert band_edges(Sweep([1, 2, 3], [-5, -10, -5])) == (2, 2)


@pytest.mark.parametrize("values", [[-20, -5, -5], [-5, -5, -20], [-20, -20, -20],
                                   [-10, -20, -5], [-5, -5, -5], [-5, -math.inf, -5]])
def test_missing_or_uninterpolatable_crossings_are_unavailable(values):
    assert band_edges(Sweep([1, 2, 3], values)) is None


def test_threshold_must_be_finite():
    with pytest.raises(ValueError):
        band_edges(Sweep([1, 2, 3], [-5, -20, -5]), math.nan)
