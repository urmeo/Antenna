import math

from antenna import design


def test_square_resonates_near_target():
    f = design.rectangular_resonant_frequency(29.38, 29.38, 4.4, 1.4)
    assert 2.35 < f < 2.5, f


def test_circular_resonates_near_target():
    f = design.circular_resonant_frequency(17.0, 4.4, 1.4)
    assert 2.30 < f < 2.50, f


def test_patch_areas():
    assert abs(design.patch_area_mm2("square", {"S": 29.38}) - 29.38 ** 2) < 1e-6
    assert abs(design.patch_area_mm2("circular", {"R": 17.0}) - math.pi * 17.0 ** 2) < 1e-6
    assert design.patch_area_mm2("triangular", {"Tb": 37.6, "Th": 29.38}) > 0
    assert design.patch_area_mm2("fshaped", {"W": 37.6, "L": 29.38, "Vw": 10, "Bh": 8, "Sh": 3, "Mw": 25}) > 0


def test_hexagon_equivalent_radius_smaller_than_side():
    assert design.hexagon_equivalent_radius(17.0) < 17.0


def test_synth_inverts_to_target():
    for key, dims in [("circular", {"R": 17.0}), ("square", {"S": 29.38}),
                      ("triangular", {"Tb": 37.6, "Th": 29.38}), ("hexagonal", {"Ha": 17.0})]:
        primary = design.PRIMARY_DIMENSION[key]
        d = design.synthesize_dimension(key, dims, 4.4, 1.4, 2.45)
        trial = dict(dims, **{primary: d})
        assert abs(design.resonant_frequency(key, trial, 4.4, 1.4) - 2.45) < 1e-3, key
