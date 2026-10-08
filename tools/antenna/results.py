"""Load the canonical results file into typed objects."""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from importlib.resources import files
from typing import Dict, List, Optional

from .design import validate_dimensions


@dataclass
class Substrate:
    name: str
    epsilon_r: float
    loss_tangent: float
    height_mm: float
    conductor: str
    conductor_height_mm: float


@dataclass
class Simulation:
    s11_db: float
    vswr: float
    bandwidth_pct: float
    band_edges_ghz: List[float]
    main_lobe_db: float
    side_lobe_db: float
    bandwidth_pending: bool = False


@dataclass
class Measurement:
    s11_db: float
    vswr: float
    read_at: str
    verified: bool


@dataclass
class Geometry:
    key: str
    name: str
    highlight: bool
    dimensions_mm: Dict[str, float]
    simulation: Simulation
    measurement: Optional[Measurement]


@dataclass
class Dataset:
    design_frequency_ghz: float
    substrate: Substrate
    ground_plane_mm: Dict[str, float]
    feed_mm: Dict[str, float]
    geometries: List[Geometry]


def load(path: "str | None" = None) -> Dataset:
    if path:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh, parse_constant=_invalid_constant, object_pairs_hook=_unique_object)
    else:
        raw = json.loads(files("antenna").joinpath("data/results.json").read_text(encoding="utf-8"),
                         parse_constant=_invalid_constant, object_pairs_hook=_unique_object)

    try:
        meta = raw["meta"]
        geometries = [
            Geometry(
                key=g["key"],
                name=g["name"],
                highlight=g.get("highlight", False),
                dimensions_mm=g["dimensions_mm"],
                simulation=Simulation(**g["simulation"]),
                measurement=Measurement(**g["measurement"]) if g.get("measurement") is not None else None,
            )
            for g in raw["geometries"]
        ]
        ds = Dataset(
            design_frequency_ghz=meta["design_frequency_ghz"],
            substrate=Substrate(**meta["substrate"]),
            ground_plane_mm=meta["ground_plane_mm"],
            feed_mm=meta["feed_mm"],
            geometries=geometries,
        )
    except (KeyError, TypeError) as exc:
        raise ValueError("invalid results structure: %s" % exc) from exc
    validate(ds)
    return ds


def validate(ds: Dataset) -> None:
    """Validate structure and domains before checking RF identities."""
    if not isinstance(ds, Dataset) or not isinstance(ds.substrate, Substrate):
        raise ValueError("results require a Dataset and Substrate")
    _number(ds.design_frequency_ghz, "design frequency", positive=True)
    substrate = ds.substrate
    _text(substrate.name, "substrate name")
    _text(substrate.conductor, "conductor")
    _number(substrate.epsilon_r, "relative permittivity", positive=True)
    if substrate.epsilon_r < 1:
        raise ValueError("relative permittivity must be at least 1")
    _number(substrate.loss_tangent, "loss tangent", nonnegative=True)
    _number(substrate.height_mm, "substrate height", positive=True)
    _number(substrate.conductor_height_mm, "conductor height", positive=True)
    _dimensions(ds.ground_plane_mm, ("width", "length"), "ground plane")
    _dimensions(ds.feed_mm, ("width", "patch_gap"), "feed", zero_allowed="patch_gap")
    if not isinstance(ds.geometries, list) or not ds.geometries:
        raise ValueError("geometries must be a nonempty list")
    keys = set()
    for g in ds.geometries:
        if not isinstance(g, Geometry):
            raise ValueError("geometry entries must be Geometry objects")
        _text(g.key, "geometry key")
        _text(g.name, "geometry name")
        _boolean(g.highlight, "%s highlight" % g.key)
        if g.key in keys:
            raise ValueError("duplicate geometry key: %s" % g.key)
        keys.add(g.key)
        validate_dimensions(g.key, g.dimensions_mm)
        sim = g.simulation
        if not isinstance(sim, Simulation):
            raise ValueError("%s requires a Simulation" % g.key)
        _reading(sim, "%s simulation" % g.key)
        _number(sim.bandwidth_pct, "%s bandwidth" % g.key, nonnegative=True)
        _boolean(sim.bandwidth_pending, "%s bandwidth_pending" % g.key)
        edges = sim.band_edges_ghz
        if not isinstance(edges, list) or len(edges) != 2:
            raise ValueError("%s band edges require exactly two frequencies" % g.key)
        for value in edges:
            _number(value, "%s band edge" % g.key, positive=True)
        if edges[0] > edges[1]:
            raise ValueError("%s band edges must be ordered" % g.key)
        _number(sim.main_lobe_db, "%s main lobe" % g.key)
        _number(sim.side_lobe_db, "%s side lobe" % g.key)
        if g.measurement is not None:
            if not isinstance(g.measurement, Measurement):
                raise ValueError("%s measurement must be a Measurement or null" % g.key)
            _reading(g.measurement, "%s measurement" % g.key)
            _text(g.measurement.read_at, "%s measurement read_at" % g.key)
            _boolean(g.measurement.verified, "%s measurement verified" % g.key)


def _reading(reading: "Simulation | Measurement", name: str) -> None:
    _number(reading.s11_db, "%s S11" % name)
    if reading.s11_db > 0:
        raise ValueError("%s S11 must be <= 0 dB for this passive antenna" % name)
    _number(reading.vswr, "%s VSWR" % name)
    if reading.vswr < 1:
        raise ValueError("%s VSWR must be at least 1" % name)


def _number(value: float, name: str, positive: bool = False, nonnegative: bool = False) -> None:
    try:
        finite = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError("%s must be a finite number" % name)
    if positive and value <= 0:
        raise ValueError("%s must be positive" % name)
    if nonnegative and value < 0:
        raise ValueError("%s must be nonnegative" % name)


def _text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s must be nonempty text" % name)


def _boolean(value: bool, name: str) -> None:
    if not isinstance(value, bool):
        raise ValueError("%s must be a boolean" % name)


def _dimensions(values: Dict[str, float], required: tuple, name: str, zero_allowed: str = "") -> None:
    if not isinstance(values, dict) or any(key not in values for key in required):
        raise ValueError("%s requires dimensions %s" % (name, ", ".join(required)))
    for key, value in values.items():
        _number(value, "%s %s" % (name, key), positive=key != zero_allowed, nonnegative=True)


def _invalid_constant(value: str) -> None:
    raise ValueError("JSON numbers must be finite: %s" % value)


def _unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: %s" % key)
        result[key] = value
    return result
