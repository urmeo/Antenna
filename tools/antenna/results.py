"""Load the canonical results file into typed objects."""
from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from typing import Dict, List, Optional


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
    bandwidth_pending: bool = False  # stored % predates the band edges; awaiting re-simulation


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
            raw = json.load(fh)
    else:
        raw = json.loads(files("antenna").joinpath("data/results.json").read_text(encoding="utf-8"))

    meta = raw["meta"]
    geometries = [
        Geometry(
            key=g["key"],
            name=g["name"],
            highlight=g.get("highlight", False),
            dimensions_mm=g["dimensions_mm"],
            simulation=Simulation(**g["simulation"]),
            measurement=Measurement(**g["measurement"]) if g.get("measurement") else None,
        )
        for g in raw["geometries"]
    ]
    return Dataset(
        design_frequency_ghz=meta["design_frequency_ghz"],
        substrate=Substrate(**meta["substrate"]),
        ground_plane_mm=meta["ground_plane_mm"],
        feed_mm=meta["feed_mm"],
        geometries=geometries,
    )
