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
