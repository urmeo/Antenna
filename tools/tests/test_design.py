import math
import pytest

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
                      ("triangular", {"Tb": 37.6, "Th": 29.38}), ("hexagonal", {"Ha": 17.0}),
                      ("fshaped", {"W": 37.6, "L": 29.38, "Vw": 10, "Bh": 8, "Sh": 3, "Mw": 25})]:
        primary = design.PRIMARY_DIMENSION[key]
        d = design.synthesize_dimension(key, dims, 4.4, 1.4, 2.45)
        trial = dict(dims, **{primary: d})
        assert abs(design.resonant_frequency(key, trial, 4.4, 1.4) - 2.45) < 1e-3, key


def test_synth_rejects_unreachable_target():
    import pytest
    with pytest.raises(ValueError):
        design.synthesize_dimension("circular", {"R": 17.0}, 4.4, 1.4, 200.0)
    with pytest.raises(ValueError):
        design.synthesize_dimension("bowtie", {"R": 17.0}, 4.4, 1.4, 2.45)


@pytest.mark.parametrize("value", [-1, 0, math.nan, math.inf, True])
def test_physical_dimensions_and_material_are_validated(value):
    for function, args in [(design.circular_resonant_frequency, (value, 4.4, 1.4)),
                           (design.rectangular_resonant_frequency, (value, 29, 4.4, 1.4)),
                           (design.triangular_resonant_frequency, (value, 4.4)),
                           (design.hexagon_equivalent_radius, (value,)),
                           (design.effective_permittivity, (4.4, value, 29)),
                           (design.patch_area_mm2, ("square", {"S": value}))]:
        with pytest.raises(ValueError):
            function(*args)


def test_missing_dimensions_and_invalid_dielectric():
    with pytest.raises(ValueError, match="dimension Th"):
        design.patch_area_mm2("triangular", {"Tb": 37.6})
    with pytest.raises(ValueError):
        design.circular_resonant_frequency(17, .5, 1.4)


@pytest.mark.parametrize("changes", [{"Vw": 40}, {"Mw": 40}, {"L": 18}, {"Sh": -1}])
def test_invalid_f_layout_is_rejected(changes):
    dims = dict(W=37.6, L=29.38, Vw=10, Bh=8, Sh=3, Mw=25)
    dims.update(changes)
    for function, args in [(design.patch_area_mm2, ("fshaped", dims)),
                           (design.resonant_frequency, ("fshaped", dims, 4.4, 1.4))]:
        with pytest.raises(ValueError):
            function(*args)


def test_f_area_and_synthesis_respect_bar_layout():
    dims = dict(W=37.6, L=29.38, Vw=10, Bh=8, Sh=3, Mw=25)
    assert design.patch_area_mm2("fshaped", dims) == pytest.approx(634.6)
    length = design.synthesize_dimension("fshaped", dims, 4.4, 1.4, 2.45)
    assert length >= 19
    with pytest.raises(ValueError, match="outside"):
        design.synthesize_dimension("fshaped", dims, 4.4, 1.4, 20)


@pytest.mark.parametrize("target", [0, -1, math.nan, math.inf])
def test_invalid_synthesis_target_is_rejected(target):
    with pytest.raises(ValueError):
        design.synthesize_dimension("square", {"S": 29.38}, 4.4, 1.4, target)
