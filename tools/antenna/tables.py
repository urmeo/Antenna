"""Render the README result tables from the canonical data file.

Every table a reader sees is produced here, so the numbers cannot drift from
``data/results.json``. Tables are injected into the README between
``<!-- BEGIN:name -->`` / ``<!-- END:name -->`` markers.
"""
from __future__ import annotations

import re
from typing import Dict, List, Sequence, Tuple

from . import fom
from .design import patch_area_mm2
from .results import Dataset, load

MINUS = "−"

# Transparent 1px spacers in the header row force every table to full page
# width with columns sized to their content (GitHub's stylesheet ignores the
# table width attribute but honours img width, shrinking it on small screens).
_SPACER = '<img src="images/spacer.png" width="%d" height="1">'
_SPACER_TOTAL = 1600
_SPACER_FLOOR = 60


def _column_spacers(columns: List[List[str]]) -> List[int]:
    lengths = [max(len(text) for text in column) for column in columns]
    scale = _SPACER_TOTAL / sum(lengths)
    return [max(_SPACER_FLOOR, round(length * scale)) for length in lengths]


def _num(value: float, decimals: int) -> str:
    text = "%.*f" % (decimals, abs(value))
    return (MINUS + text) if value < 0 else text


def _signed(value: float, decimals: int) -> str:
    text = "%.*f" % (decimals, abs(value))
    return ("+" + text) if value >= 0 else (MINUS + text)


def _table(headers: Sequence[str], rows: Sequence[Tuple[List[str], bool]]) -> str:
    def cell(text: str, bold: bool) -> str:
        return "<td><strong>%s</strong></td>" % text if bold else "<td>%s</td>" % text

    spacers = _column_spacers([[h] + [cells[i] for cells, _ in rows] for i, h in enumerate(headers)])
    head = "".join("<th>%s %s</th>" % (h, _SPACER % w) for h, w in zip(headers, spacers))
    body = "\n".join("<tr>%s</tr>" % "".join(cell(c, bold) for c in cells) for cells, bold in rows)
    return "<table>\n<thead><tr>" + head + "</tr></thead>\n<tbody>\n" + body + "\n</tbody>\n</table>"


def simulation_table(ds: Dataset) -> str:
    headers = ["Geometry", "S11 (dB)", "VSWR", "Bandwidth (%)", "Main Lobe (dB)", "Side Lobe (dB)"]
    rows = []
    for g in ds.geometries:
        s = g.simulation
        rows.append(([g.name, _num(s.s11_db, 2), _num(s.vswr, 3), _num(s.bandwidth_pct, 2),
                      _num(s.main_lobe_db, 2), _num(s.side_lobe_db, 1)], g.highlight))
    return _table(headers, rows)


def measurement_table(ds: Dataset) -> str:
    headers = ["Geometry", "S11 (dB)", "VSWR"]
    rows = []
    for g in ds.geometries:
        if g.measurement is None:
            continue
        m = g.measurement
        rows.append(([g.name, _num(m.s11_db, 2), _num(m.vswr, 3)], g.highlight))
    return _table(headers, rows)


def delta_table(ds: Dataset) -> str:
    headers = ["Geometry", "S11 sim (dB)", "S11 meas (dB)", "ΔS11 (dB)",
               "VSWR sim", "VSWR meas", "ΔVSWR"]
    rows = []
    for g in ds.geometries:
        if g.measurement is None:
            continue
        s, m = g.simulation, g.measurement
        rows.append(([g.name, _num(s.s11_db, 2), _num(m.s11_db, 2), _signed(m.s11_db - s.s11_db, 2),
                      _num(s.vswr, 3), _num(m.vswr, 3), _signed(m.vswr - s.vswr, 3)], False))
    return _table(headers, rows)


def figure_of_merit_table(ds: Dataset) -> str:
    headers = ["Geometry", "Footprint (mm²)", "Main Lobe (dB)",
               "Gain ÷ area (cm⁻²)", "Gain × BW"]
    rows = []
    for g in ds.geometries:
        s = g.simulation
        area = patch_area_mm2(g.key, g.dimensions_mm)
        rows.append(([g.name, _num(area, 0), _num(s.main_lobe_db, 2),
                      _num(fom.gain_per_area(s.main_lobe_db, area), 3),
                      _num(fom.gain_bandwidth_product(s.main_lobe_db, s.bandwidth_pct), 3)], g.highlight))
    return _table(headers, rows)


TABLES = {
    "sim-table": simulation_table,
    "measurement-table": measurement_table,
    "delta-table": delta_table,
    "fom-table": figure_of_merit_table,
}


def render_all(ds: Dataset) -> Dict[str, str]:
    return {name: fn(ds) for name, fn in TABLES.items()}


def inject(readme_path: str, ds: "Dataset | None" = None) -> List[str]:
    """Replace each marked block in the README. Returns the names updated."""
    ds = ds or load()
    with open(readme_path, "r", encoding="utf-8") as fh:
        original = text = fh.read()

    updated: List[str] = []
    for name, markdown in render_all(ds).items():
        pattern = re.compile(
            r"(<!-- BEGIN:%s -->\n).*?(\n<!-- END:%s -->)" % (re.escape(name), re.escape(name)),
            re.DOTALL,
        )
        if pattern.search(text):
            text = pattern.sub(lambda mo: mo.group(1) + markdown + mo.group(2), text)
            updated.append(name)

    if updated and text != original:
        with open(readme_path, "w", encoding="utf-8") as fh:
            fh.write(text)
    return updated
