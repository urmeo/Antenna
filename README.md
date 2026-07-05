# Microstrip Patch Antenna: 2.45 GHz Geometry Comparison

**Which patch shape performs best at 2.45 GHz?** Five geometries — circular, F-shaped, triangular, square, hexagonal — designed, simulated in CST Studio Suite, fabricated on FR-4, measured on a Rohde & Schwarz VNA. **The circular patch wins in both simulation and measurement.**

![All five fabricated antenna geometries](images/antennas/all-five-geometries.jpg)

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

> *Main Lobe (dB)* is CST's far-field main-lobe magnitude; circular and hexagonal genuinely tie at 5.54 dB.

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

- Same ranking in simulation and hardware; every design clears S11 < −10 dB in both
- Circular resonates closest to 2.45 GHz and posts the deepest null in both
- Deltas trace to SMA parasitics, FR-4 εr spread (spec 4.2–4.8, simulated 4.4), etching tolerance, solder loss

### Figure of Merit

Different footprints, so normalise:

<!-- BEGIN:fom-table -->
| Geometry | Footprint (mm²) | Main Lobe (dB) | Gain ÷ area (cm⁻²) | Gain × BW |
|---|---|---|---|---|
| **Circular** | **908** | **5.54** | **0.394** | **0.112** |
| F-shaped | 635 | 4.11 | 0.406 | 0.077 |
| Triangular | 552 | 4.51 | 0.511 | 0.069 |
| Square | 863 | 3.00 | 0.231 | 0.048 |
| Hexagonal | 751 | 5.54 | 0.477 | 0.076 |
<!-- END:fom-table -->

- Link budget and bandwidth: **circular**. Tight board area: **triangular** or **hexagonal**.

## Graphs and Charts

| Return loss: simulation vs measurement | CST S11 sweep: circular patch |
|:---:|:---:|
| ![S11 sim vs meas](images/plots/s11_sim_vs_meas.png) | ![CST S11 circular patch](images/plots/s11_circular_cst.png) |

- Left: measured S11 tracks the simulated ranking, all five below −10 dB
- Right: the winner's simulated S11 — a −53.08 dB null at 2.434 GHz (Fig 4.2)
- Full CST outputs for all five shapes in [simulation-and-results.pdf](docs/simulation-and-results.pdf)

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

Set `PatchShape` in `Main` and run — [patch-antenna.bas](cst/patch-antenna.bas) builds substrate, ground plane, patch, feed, waveguide port, monitors, and solver from scratch.

| `PatchShape` | Patch construction |
|---|---|
| `"circular"` | Cylinder, R = 17.0 mm |
| `"square"` | Brick, S = 29.38 mm |
| `"triangular"` | Extruded isosceles triangle, base 37.60 mm, height 29.38 mm |
| `"hexagonal"` | Extruded regular hexagon, side 17.0 mm |
| `"fshaped"` | Boolean union of vertical bar + two horizontal bars |

- Annealed-copper conductors (finite conductivity); permittivity `Eps` exposed for FR-4 tolerance sweeps
- Hexahedral mesh at 20 steps/wavelength, adaptive refinement, expanded-open boundaries, 6·Hs waveguide port
- Each shape defines just two feed expressions — `Ey` (facing edge) and `Fx` (feed centre)
- Solves, then exports the sweep to `s11.s1p` for `python -m antenna ingest`

## Fabrication and Measurement

Full process in [fabrication-and-measurement.pdf](docs/fabrication-and-measurement.pdf):

- CorelDraw mask → laminated photoresist FR-4 → ~2 min UV exposure → NaOH developer → chemical etch
- SMA soldered to the 50 Ω feed; S-parameters on a Rohde & Schwarz ZVH

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

Every number above is a computed view of [results.json](tools/data/results.json) — tables cannot drift from the data, or from each other.

| Module | What it does |
|---|---|
| `metrics.py` | Exact S11, reflection coefficient, and VSWR identities; bandwidth from band edges |
| `design.py` | Shape-correct resonance equations (Balanis, Garg) and patch footprint areas |
| `fom.py` | Area-normalised gain and gain-bandwidth product |
| `check.py` | Physics validator wired into CI |
| `tables.py` | Renders and injects every README table between marker comments |
| `touchstone.py` | Minimal `.s1p` reader (DB, MA, RI) for VNA and CST sweeps |
| `plots.py` | Publication-ready charts from the canonical data |

- `tables --write` regenerates every table; GitHub Actions ([validate.yml](.github/workflows/validate.yml)) re-checks the physics on every push
- `ingest` extracts resonance, VSWR, and bandwidth from `.s1p` sweeps; `synth` sizes each shape for the target frequency
- 14 passing tests; standard library only — matplotlib optional, charts only

## Known Limitations

- Results tables come from the original PEC simulations; the macro now models copper and exports `s11.s1p` to regenerate them from real sweeps
- Measured S11 and VSWR were recorded independently and disagree slightly in all five rows (single sample, one of two units); CI flags each until raw traces land
- Four of five patches resonate below 2.45 GHz, mixing shape with detuning; `python -m antenna synth` gives corrected dimensions
- Closed-form and simulated band-edge resonance estimates disagree for triangle and hexagon; a direct S11 minimum from the exported sweep is the arbiter

## Roadmap

- Drop CST/VNA Touchstone exports into `tools/data/` — reader and overlay plotting already wired
- Measure realised gain on both samples per design
- Sweep `Eps` across FR-4's 4.2–4.8 spec band

## Applications

2.45 GHz ISM band: Wi-Fi (802.11 b/g/n), Bluetooth/BLE, ZigBee, RFID readers, wireless medical telemetry, industrial telemetry and microwave power transfer — low profile, cheap to etch, easily arrayed.

## Tech Stack

| Layer | Tool |
|---|---|
| EM simulation | CST Studio Suite — VBA macro, time-domain solver |
| Analysis | Python 3.9+ (stdlib core, matplotlib optional), pytest, GitHub Actions |
| Fabrication | CorelDraw mask, photolithography, NaOH developer, chemical etch |
| Measurement | Rohde & Schwarz ZVH vector network analyzer |
| Substrate | FR-4, 1.4 mm, 0.036 mm copper |

## Documentation

| Document | Contents |
|---|---|
| [methodology.pdf](docs/methodology.pdf) | Design parameters, substrate specs, VNA calibration |
| [simulation-and-results.pdf](docs/simulation-and-results.pdf) | CST results: S11, VSWR, radiation patterns, gain |
| [fabrication-and-measurement.pdf](docs/fabrication-and-measurement.pdf) | Step-by-step fabrication, VNA measurements |

## References

1. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed. Wiley, 2016 — ch. 14: transmission-line and cavity models.
2. R. Garg, P. Bhartia, I. Bahl, A. Ittipiboon, *Microstrip Antenna Design Handbook*. Artech House, 2001.
3. D. M. Pozar, "Microstrip Antennas," *Proc. IEEE*, vol. 80, no. 1, pp. 79-91, 1992.
4. K. F. Lee, K. M. Luk, *Microstrip Patch Antennas*. Imperial College Press, 2011.

## License

[CC BY 4.0](https://github.com/urme-b/Antenna/blob/main/LICENSE)
