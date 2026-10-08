"""Render and verify marked README tables from canonical data."""
from __future__ import annotations

import re
from typing import Dict, List, Sequence, Tuple

from . import fom, metrics
from .design import patch_area_mm2
from .results import Dataset, load

MINUS = "−"


def _num(value: float, decimals: int) -> str:
    text = "%.*f" % (decimals, abs(value))
    return (MINUS + text) if value < 0 else text


def _signed(value: float, decimals: int) -> str:
    text = "%.*f" % (decimals, abs(value))
    return ("+" + text) if value >= 0 else (MINUS + text)


def _table(headers: Sequence[str], rows: Sequence[Tuple[List[str], bool]]) -> str:
    def emphasise(cells: List[str], bold: bool) -> List[str]:
        cells = [c.replace("\\", "\\\\").replace("|", "\\|")
                  .replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
                 for c in cells]
        return ["**%s**" % c for c in cells] if bold else cells

    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(emphasise(cells, bold)) + " |" for cells, bold in rows]
    return "\n".join(lines)


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
               "Pattern proxy ÷ area (cm⁻²)", "Pattern proxy × reported BW"]
    rows = []
    for g in ds.geometries:
        s = g.simulation
        area = patch_area_mm2(g.key, g.dimensions_mm)
        rows.append(([g.name, _num(area, 0), _num(s.main_lobe_db, 2),
                      _num(fom.gain_per_area(s.main_lobe_db, area), 3),
                      _num(fom.gain_bandwidth_product(s.main_lobe_db, s.bandwidth_pct), 3)], g.highlight))
    return _table(headers, rows)


def results_table(ds: Dataset) -> str:
    headers = ["Shape", "Simulated S11 (dB)", "Measured S11 (dB)",
               "Reported VSWR", "VSWR from measured S11"]
    rows = []
    for g in ds.geometries:
        m = g.measurement
        rows.append(([g.name, _num(g.simulation.s11_db, 2),
                      _num(m.s11_db, 2) if m else "n/a",
                      _num(m.vswr, 3) if m else "n/a",
                      _num(metrics.vswr_from_s11_db(m.s11_db), 3) if m else "n/a"], g.highlight))
    return _table(headers, rows)


def bandwidth_table(ds: Dataset) -> str:
    headers = ["Shape", "Reported band (GHz)", "Reported BW (%)", "BW from edges (%)"]
    rows = []
    for g in ds.geometries:
        s = g.simulation
        low, high = s.band_edges_ghz
        rows.append(([g.name, "%s to %s" % (_num(low, 4), _num(high, 4)),
                      _num(s.bandwidth_pct, 2),
                      _num(metrics.fractional_bandwidth_pct(low, high), 2)], g.highlight))
    return _table(headers, rows)


TABLES = {
    "sim-table": simulation_table,
    "measurement-table": measurement_table,
    "delta-table": delta_table,
    "fom-table": figure_of_merit_table,
    "results-table": results_table,
    "bandwidth-table": bandwidth_table,
}


def render_all(ds: Dataset) -> Dict[str, str]:
    return {name: fn(ds) for name, fn in TABLES.items()}


def check(readme_path: str, ds: "Dataset | None" = None) -> List[str]:
    with open(readme_path, encoding="utf-8") as fh:
        text = fh.read()
    issues: List[str] = []
    found = 0
    for name, markdown in render_all(ds or load()).items():
        begin, end = "<!-- BEGIN:%s -->" % name, "<!-- END:%s -->" % name
        if begin not in text and end not in text:
            continue
        found += 1
        if text.count(begin) != 1 or text.count(end) != 1:
            issues.append("%s: missing or duplicate marker" % name)
            continue
        start, stop = text.index(begin) + len(begin), text.index(end)
        if stop < start or text[start:stop].strip() != markdown:
            issues.append("%s: table differs from source" % name)
    if not found:
        issues.append("no result table markers found")
    return issues


def inject(readme_path: str, ds: "Dataset | None" = None) -> List[str]:
    """Replace each marked block in the README. Returns the names updated."""
    ds = ds or load()
    with open(readme_path, "r", encoding="utf-8") as fh:
        original = text = fh.read()

    rendered = render_all(ds)
    blocks = []
    for name in rendered:
        begin, end = "<!-- BEGIN:%s -->" % name, "<!-- END:%s -->" % name
        if begin not in text and end not in text:
            continue
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError("%s: missing or duplicate marker" % name)
        if text.index(end) < text.index(begin) + len(begin):
            raise ValueError("%s: markers are out of order" % name)
        blocks.append((text.index(begin), text.index(end) + len(end)))
    blocks.sort()
    if any(start < previous_end for (_, previous_end), (start, _) in zip(blocks, blocks[1:])):
        raise ValueError("table marker blocks overlap")

    updated: List[str] = []
    for name, markdown in rendered.items():
        pattern = re.compile(
            r"(<!-- BEGIN:%s -->).*?(<!-- END:%s -->)" % (re.escape(name), re.escape(name)),
            re.DOTALL,
        )
        if pattern.search(text):
            text = pattern.sub(lambda mo: mo.group(1) + "\n" + markdown + "\n" + mo.group(2), text)
            updated.append(name)

    if updated and text != original:
        with open(readme_path, "w", encoding="utf-8") as fh:
            fh.write(text)
    return updated
