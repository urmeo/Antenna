# Microstrip Patch Antenna: 2.45 GHz Geometry Comparison

![validate](https://github.com/urme-b/Antenna/actions/workflows/validate.yml/badge.svg)

**Which patch shape performs best at 2.45 GHz?** Five geometries (circular, F-shaped, triangular, square, hexagonal) were designed, simulated in CST Studio Suite, fabricated on FR-4, and measured on a Rohde & Schwarz VNA. Full loop: design, simulation, fabrication, measurement, analysis.

![All five fabricated antenna geometries](images/antennas/all-five-geometries.jpg)

## What This Is

- A head-to-head study of 5 patch shapes, all targeting 2.45 GHz on the same substrate, ground plane, and feed
- Every antenna was built twice on FR-4 via photolithography and etching; one of each pair characterized on a VNA
- One parametric CST VBA macro ([`cst/patch-antenna.bas`](cst/patch-antenna.bas)) builds any of the 5 models from scratch
- A dependency-free Python toolkit ([`tools/`](tools/)) ties every number below to one data file, verified in CI
- **Headline result: the circular patch wins in both simulation and measurement**

## Features

| Feature | Detail |
|---|---|
| Complete hardware loop | Design, CST simulation, photolithographic fabrication, VNA measurement |
| One macro, five antennas | Set `PatchShape` and run; re-running rebuilds the model cleanly |
| Single source of truth | [`results.json`](tools/data/results.json) drives every table and chart; nothing hand-typed |
| Physics validation in CI | S11, VSWR, and band-edge identities cross-checked on every push |
| Tested RF math | 14 unit tests; core toolkit runs on the Python standard library alone |
| Fair comparison metrics | Area-normalised gain and gain-bandwidth product across shapes |
| Full visual record | 13 lab photos plus charts generated straight from the data |

## Results

### Simulation (CST Studio Suite)

<!-- BEGIN:sim-table -->
| Geometry | S11 (dB) | VSWR | Bandwidth (%) | Main Lobe (dB) | Side Lobe (dB) |
|---|---|---|---|---|---|
| **Circular** | **−53.08** | **1.004** | **3.12** | **5.54** | **−3.7** |
| F-shaped | −30.02 | 1.065 | 2.98 | 4.11 | −1.6 |
| Triangular | −18.86 | 1.257 | 2.45 | 4.51 | −0.6 |
| Square | −16.38 | 1.357 | 2.41 | 3.00 | −6.7 |
| Hexagonal | −14.78 | 1.446 | 2.12 | 5.54 | −7.0 |
<!-- END:sim-table -->

> *Main Lobe (dB)* is CST's far-field main-lobe magnitude. Circular and hexagonal genuinely share a 5.54 dB main lobe.

### Measurement (VNA)

<!-- BEGIN:measurement-table -->
| Geometry | S11 (dB) | VSWR |
|---|---|---|
| **Circular** | **−31.99** | **1.125** |
| F-shaped | −16.98 | 1.167 |
| Triangular | −15.37 | 1.368 |
| Square | −14.46 | 1.536 |
| Hexagonal | −13.93 | 1.694 |
<!-- END:measurement-table -->

### Simulation vs. Measurement

<!-- BEGIN:delta-table -->
| Geometry | S11 sim (dB) | S11 meas (dB) | ΔS11 (dB) | VSWR sim | VSWR meas | ΔVSWR |
|---|---|---|---|---|---|---|
| Circular | −53.08 | −31.99 | +21.09 | 1.004 | 1.125 | +0.121 |
| F-shaped | −30.02 | −16.98 | +13.04 | 1.065 | 1.167 | +0.102 |
| Triangular | −18.86 | −15.37 | +3.49 | 1.257 | 1.368 | +0.111 |
| Square | −16.38 | −14.46 | +1.92 | 1.357 | 1.536 | +0.179 |
| Hexagonal | −14.78 | −13.93 | +0.85 | 1.446 | 1.694 | +0.248 |
<!-- END:delta-table -->

- Identical ranking in simulation and hardware: circular first through hexagonal fifth, across all five shapes
- Every design clears the S11 < −10 dB threshold in both simulation and measurement
- Circular resonates closest to the 2.45 GHz target and posts the deepest null in both worlds
- Sim-to-meas deltas trace to known, documented effects: SMA connector parasitics, FR-4 permittivity spread (spec 4.2-4.8, simulation 4.4), etching tolerance, solder losses

### Figure of Merit

The five patches occupy different footprints, so raw main-lobe magnitude is not a fair fight. Normalising sharpens the picture:

<!-- BEGIN:fom-table -->
| Geometry | Footprint (mm²) | Main Lobe (dB) | Gain ÷ area (cm⁻²) | Gain × BW |
|---|---|---|---|---|
| **Circular** | **908** | **5.54** | **0.394** | **0.112** |
| F-shaped | 635 | 4.11 | 0.406 | 0.077 |
| Triangular | 552 | 4.51 | 0.511 | 0.069 |
| Square | 863 | 3.00 | 0.231 | 0.048 |
| Hexagonal | 751 | 5.54 | 0.477 | 0.076 |
<!-- END:fom-table -->

- Best matching and gain-bandwidth product: circular; best gain per unit of copper: triangular
- Design guidance: pick circular for link budget and bandwidth, triangular or hexagonal when board area rules

## Graphs and Charts

Generated straight from the data by the toolkit:

| Return loss: simulation vs measurement | CST S11 sweep: circular patch |
|:---:|:---:|
| ![S11 sim vs meas](images/plots/s11_sim_vs_meas.png) | ![CST S11 circular patch](images/plots/s11_circular_cst.png) |

- Left: measured S11 tracks the simulated ranking bar for bar, all five below the −10 dB threshold
- Right: the winning circular patch's simulated S11 — a −53.08 dB null at 2.434 GHz (Fig 4.2)
- Full CST outputs for all five shapes (S11 curves, VSWR, radiation patterns, far-field views) in [`simulation-and-results.pdf`](docs/simulation-and-results.pdf)

## Fabricated Antennas

Two samples per design, photolithography on FR-4, SMA-fed:

| Circular (best performer) | F-shaped | Triangular |
|:---:|:---:|:---:|
| ![Circular](images/antennas/circular-patch.jpg) | ![F-shaped](images/antennas/f-shaped-patch.jpg) | ![Triangular](images/antennas/triangular-patch.jpg) |
| **Square** | **Hexagonal** | |
| ![Square](images/antennas/square-patch.jpg) | ![Hexagonal](images/antennas/hexagonal-patch.jpg) | |

## Design Parameters

### Common

| Parameter | Value |
|---|---|
| Operating frequency | 2.45 GHz |
| Substrate | FR-4 (εr ≈ 4.4, tan δ = 0.02) |
| Substrate height (Hs) | 1.4 mm |
| Conductor height (Ht) | 0.036 mm |
| Ground plane (Wg × Lg) | 75.20 × 58.76 mm |
| Feed line width (Fw) | 2.7 mm (50 Ω) |
| Feed-patch gap (Gpf) | 1 mm |

### Geometry-Specific

| Geometry | Dimensions |
|---|---|
| Circular | R = 17.0 mm |
| Square | S = 29.38 mm |
| Triangular | Tb = 37.60 mm, Th = 29.38 mm |
| Hexagonal | Ha = 17.0 mm |
| F-shaped | W = 37.60, L = 29.38, Vw = 10.0, Bh = 8.0, Sh = 3.0, Mw = 25.0 mm |

## Simulation

One macro, five antennas. Set `PatchShape` in `Main` and run; [`patch-antenna.bas`](cst/patch-antenna.bas) builds the substrate, ground plane, patch, feed, waveguide port, field monitors, and solver from scratch.

| `PatchShape` | Patch construction |
|---|---|
| `"circular"` | Cylinder, R = 17.0 mm |
| `"square"` | Brick, S = 29.38 mm |
| `"triangular"` | Extruded isosceles triangle, base 37.60 mm, height 29.38 mm |
| `"hexagonal"` | Extruded regular hexagon, side 17.0 mm |
| `"fshaped"` | Boolean union of vertical bar + two horizontal bars |

- Shared matched-feed logic: each shape defines just two expressions, `Ey` (patch edge facing the feed) and `Fx` (feed centre)
- Conductors modelled as annealed copper with finite conductivity; permittivity `Eps` exposed for FR-4 tolerance sweeps
- Hexahedral mesh at 20 steps per wavelength with adaptive refinement; expanded-open boundaries on all faces
- Waveguide port spans the canonical 6·Hs around the microstrip for clean mode launching
- After solving, the macro exports the reflection sweep to `s11.s1p` for `python -m antenna ingest`

## Fabrication and Measurement

Step-by-step process in [`fabrication-and-measurement.pdf`](docs/fabrication-and-measurement.pdf):

- Mask printed on transparent film in CorelDraw, laminated onto photoresist-coated FR-4
- UV exposure (~2 min), NaOH developer bath, then chemical etching strips the unmasked copper
- SMA connectors soldered to the 50 Ω microstrip feed
- S-parameters measured on a Rohde & Schwarz ZVH cable and antenna analyzer

| VNA (Smith chart) | Laminator | UV exposure unit |
|:---:|:---:|:---:|
| ![VNA](images/equipment/vna-smith-chart.jpg) | ![Laminator](images/equipment/laminator.jpg) | ![UV exposure](images/equipment/uv-exposure-open.jpg) |

| UV exposure (closed) | Etching machine |
|:---:|:---:|
| ![UV closed](images/equipment/uv-exposure-closed.jpg) | ![Etching](images/equipment/etching-machine.jpg) |

| Blank FR-4 substrate | Circular patch in NaOH developer bath |
|:---:|:---:|
| ![FR-4](images/fabrication/fr4-substrate-blank.jpg) | ![NaOH bath](images/fabrication/circular-patch-naoh-bath.jpg) |

## Analysis Toolkit

Every number in this README is a computed view of one file, [`tools/data/results.json`](tools/data/results.json). Tables cannot drift from the data, or from each other.

| Module | What it does |
|---|---|
| `metrics.py` | Exact S11, reflection coefficient, and VSWR identities; bandwidth from band edges |
| `design.py` | Shape-correct resonance equations (Balanis, Garg) and patch footprint areas |
| `fom.py` | Area-normalised gain and gain-bandwidth product |
| `check.py` | Physics validator wired into CI |
| `tables.py` | Renders and injects every README table between marker comments |
| `touchstone.py` | Minimal `.s1p` reader (DB, MA, RI) for VNA and CST sweeps |
| `plots.py` | Publication-ready charts from the canonical data |

- Regenerates every results table from the data file in one step, so the README stays exact
- Cross-checks S11, VSWR, and band-edge physics on every push via GitHub Actions ([`validate.yml`](.github/workflows/validate.yml))
- Reads Touchstone (`.s1p`) sweeps: `ingest` extracts resonance, VSWR, and bandwidth; `synth` sizes each shape for the target frequency
- 14 passing unit tests; matplotlib is the only optional dependency, used just for charts

## Known Limitations

- The results tables come from the original perfect-conductor (PEC) simulations; the macro now models copper and exports `s11.s1p` so they can be regenerated from real sweeps
- Measured S11 and VSWR were recorded independently and disagree slightly in all five rows; CI flags each until raw VNA traces replace them, and measurements are single-sample (one of two fabricated units)
- Four of five patches resonate below the 2.45 GHz target, so the comparison mixes shape with residual detuning; `python -m antenna synth` gives the corrected dimensions
- Closed-form and simulated band-edge resonance estimates disagree for the triangle and hexagon; a direct S11 minimum from the exported sweep is the arbiter

## Future Aspects

- **Raw S11 sweeps**: drop CST and VNA Touchstone exports into `tools/data/`; the reader and overlay plotting are already wired
- **Measured realised gain on both fabricated samples per design**: upgrades the figure of merit to hardware data with repeatability
- **FR-4 tolerance sweep**: run the macro's exposed `Eps` parameter across the 4.2-4.8 spec band to quantify substrate variation

## Applications

| # | Application | Why 2.45 GHz patches fit |
|---|---|---|
| 1 | Wi-Fi (802.11 b/g/n) access points and clients | Low profile, direct PCB integration |
| 2 | Bluetooth and BLE modules | Compact footprint on standard FR-4 |
| 3 | ZigBee / IEEE 802.15.4 sensor networks | Cheap to mass-produce with node hardware |
| 4 | RFID readers (2.45 GHz ISM band) | Directional pattern suits gate and portal readers |
| 5 | Wireless medical telemetry | Conformal, lightweight, body-worn friendly |
| 6 | ISM-band industrial telemetry and microwave power transfer | Etchable, low cost, easily arrayed for higher gain |

## Tech Stack

| Layer | Tool |
|---|---|
| EM simulation | CST Studio Suite (VBA macro, time-domain solver) |
| Model scripting | CST VBA ([`cst/patch-antenna.bas`](cst/patch-antenna.bas)) |
| Analysis toolkit | Python 3.9+ (standard library core; matplotlib optional) |
| Testing | pytest (14 tests) |
| CI | GitHub Actions ([`validate.yml`](.github/workflows/validate.yml)) |
| Mask design | CorelDraw |
| Fabrication | Photolithography: laminator, UV exposure, NaOH developer, chemical etching |
| Measurement | Rohde & Schwarz ZVH vector network analyzer |
| Substrate | FR-4, 1.4 mm, 0.036 mm copper |

## Documentation

| Document | Contents |
|---|---|
| [`methodology.pdf`](docs/methodology.pdf) | Design parameters, substrate specs, VNA calibration |
| [`simulation-and-results.pdf`](docs/simulation-and-results.pdf) | CST results: S11 plots, VSWR, radiation patterns, gain |
| [`fabrication-and-measurement.pdf`](docs/fabrication-and-measurement.pdf) | Step-by-step fabrication, VNA measurements |

## Citing This Work

GitHub's "Cite this repository" button uses [`CITATION.cff`](CITATION.cff), or use BibTeX directly:

```bibtex
@misc{bose2018microstrip,
  author = {Bose, Urme},
  title  = {Microstrip Patch Antenna: 2.45 GHz Geometry Comparison},
  year   = {2018},
  url    = {https://github.com/urme-b/Antenna}
}
```

## References

1. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed. Hoboken, NJ: Wiley, 2016. Chapters 14.2-14.4: transmission-line and cavity models for rectangular and circular patches.
2. R. Garg, P. Bhartia, I. Bahl, and A. Ittipiboon, *Microstrip Antenna Design Handbook*. Norwood, MA: Artech House, 2001. Design curves and impedance matching for varied patch geometries.
3. D. M. Pozar, "Microstrip Antennas," *Proc. IEEE*, vol. 80, no. 1, pp. 79-91, Jan. 1992. Survey of microstrip theory, design methods, and feeding techniques.
4. K. F. Lee and K. M. Luk, *Microstrip Patch Antennas*. London: Imperial College Press, 2011. Geometry-specific analysis of triangular, circular, and polygonal patches.

## License

[CC BY 4.0](https://github.com/urme-b/Antenna/blob/main/LICENSE)
