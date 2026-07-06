# Microstrip Patch Antenna 2.45 GHz Benchmark: circular, F-shaped, triangular, square, hexagonal

**Which patch shape performs best at 2.45 GHz, the ISM band powering Wi-Fi, Bluetooth, ZigBee, RFID, and medical telemetry?** Five geometries (circular, F-shaped, triangular, square, hexagonal): designed, simulated in CST Studio Suite, fabricated on FR-4, measured on a Rohde & Schwarz VNA. **The circular patch wins in both simulation and measurement.**

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

- Same ranking in both; all five clear S11 < −10 dB
- Circular sits closest to 2.45 GHz with the deepest null
- Deltas: SMA parasitics, FR-4 εr spread, etching, solder

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

## Fabricated Antennas

Two samples per design (one measured), photolithography on FR-4, SMA-fed:

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

Set PatchShape in Main and run: [patch-antenna.bas](cst/patch-antenna.bas) builds substrate, ground plane, patch, feed, waveguide port, monitors, and solver from scratch.

| PatchShape | Patch construction |
|---|---|
| "circular" | Cylinder, R = 17.0 mm |
| "square" | Brick, S = 29.38 mm |
| "triangular" | Extruded isosceles triangle, base 37.60 mm, height 29.38 mm |
| "hexagonal" | Extruded regular hexagon, side 17.0 mm |
| "fshaped" | Boolean union of vertical bar + two horizontal bars |

- Annealed-copper conductors; Eps exposed for FR-4 tolerance sweeps
- Hex mesh, adaptive refinement, open boundaries, 6·Hs port
- Two feed expressions per shape: Ey (edge) and Fx (centre)
- Exports the solved sweep to s11.s1p for antenna ingest

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

## Figures

| Return loss: simulation vs measurement | CST S11 sweep: circular patch |
|:---:|:---:|
| ![S11 sim vs meas](images/plots/s11_sim_vs_meas.png) | ![CST S11 circular patch](images/plots/s11_circular_cst.png) |

- Left: measured S11 tracks the simulated ranking, all five below −10 dB
- Right: the winner's simulated S11 shows a −53.08 dB null at 2.434 GHz (Fig 4.2)
- Full CST outputs for all five shapes in [simulation-and-results.pdf](docs/simulation-and-results.pdf)

## Analysis Toolkit

<table>
<thead><tr><th>Module <img src="images/spacer.png" width="221" height="1"></th><th>What it does <img src="images/spacer.png" width="1379" height="1"></th></tr></thead>
<tbody>
<tr><td>metrics.py</td><td>Exact S11, reflection coefficient, and VSWR identities; bandwidth from band edges</td></tr>
<tr><td>design.py</td><td>Shape-correct resonance equations (Balanis, Garg) and patch footprint areas</td></tr>
<tr><td>fom.py</td><td>Area-normalised gain and gain-bandwidth product</td></tr>
<tr><td>check.py</td><td>Physics validator wired into CI</td></tr>
<tr><td>tables.py</td><td>Renders and injects every README table between marker comments</td></tr>
<tr><td>touchstone.py</td><td>Minimal .s1p reader (DB, MA, RI) for VNA and CST sweeps</td></tr>
<tr><td>plots.py</td><td>Publication-ready charts from the canonical data</td></tr>
</tbody>
</table>

## Applications

<table>
<thead><tr><th># <img src="images/spacer.png" width="60" height="1"></th><th>Application <img src="images/spacer.png" width="851" height="1"></th><th>Why 2.45 GHz patches fit <img src="images/spacer.png" width="734" height="1"></th></tr></thead>
<tbody>
<tr><td>1</td><td>Wi-Fi (802.11 b/g/n) access points and clients</td><td>Low profile, direct PCB integration</td></tr>
<tr><td>2</td><td>Bluetooth and BLE modules</td><td>Compact footprint on standard FR-4</td></tr>
<tr><td>3</td><td>ZigBee / IEEE 802.15.4 sensor networks</td><td>Cheap to mass-produce with node hardware</td></tr>
<tr><td>4</td><td>RFID readers (2.45 GHz ISM band)</td><td>Directional pattern suits gate and portal readers</td></tr>
<tr><td>5</td><td>Wireless medical telemetry</td><td>Conformal, lightweight, body-worn friendly</td></tr>
<tr><td>6</td><td>ISM-band industrial telemetry and microwave power transfer</td><td>Etchable, low cost, easily arrayed for higher gain</td></tr>
</tbody>
</table>

## Tech Stack

<table>
<thead><tr><th>Layer <img src="images/spacer.png" width="284" height="1"></th><th>Tool <img src="images/spacer.png" width="1316" height="1"></th></tr></thead>
<tbody>
<tr><td>EM simulation</td><td>CST Studio Suite (VBA macro, time-domain solver)</td></tr>
<tr><td>Model scripting</td><td>CST VBA</td></tr>
<tr><td>Analysis toolkit</td><td>Python 3.9+ (standard library core; matplotlib optional)</td></tr>
<tr><td>Testing</td><td>pytest (21 tests)</td></tr>
<tr><td>Mask design</td><td>CorelDraw</td></tr>
<tr><td>Fabrication</td><td>Photolithography: laminator, UV exposure, NaOH developer, chemical etching</td></tr>
<tr><td>Measurement</td><td>Rohde & Schwarz ZVH vector network analyzer</td></tr>
<tr><td>Substrate</td><td>FR-4, 1.4 mm, 0.036 mm copper</td></tr>
</tbody>
</table>

## Documentation

<table>
<thead><tr><th>Document <img src="images/spacer.png" width="605" height="1"></th><th>Contents <img src="images/spacer.png" width="995" height="1"></th></tr></thead>
<tbody>
<tr><td><a href="docs/methodology.pdf">methodology.pdf</a></td><td>Design parameters, substrate specs, VNA calibration</td></tr>
<tr><td><a href="docs/simulation-and-results.pdf">simulation-and-results.pdf</a></td><td>CST results: S11, VSWR, radiation patterns, gain</td></tr>
<tr><td><a href="docs/fabrication-and-measurement.pdf">fabrication-and-measurement.pdf</a></td><td>Step-by-step fabrication, VNA measurements</td></tr>
</tbody>
</table>

## References

1. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed. Hoboken, NJ: Wiley, 2016. Chapters 14.2-14.4: transmission-line and cavity models for rectangular and circular patches.
2. R. Garg, P. Bhartia, I. Bahl, and A. Ittipiboon, *Microstrip Antenna Design Handbook*. Norwood, MA: Artech House, 2001. Design curves and impedance matching for varied patch geometries.
3. D. M. Pozar, "Microstrip Antennas," *Proc. IEEE*, vol. 80, no. 1, pp. 79-91, Jan. 1992. Survey of microstrip theory, design methods, and feeding techniques.
4. K. F. Lee and K. M. Luk, *Microstrip Patch Antennas*. London: Imperial College Press, 2011. Geometry-specific analysis of triangular, circular, and polygonal patches.

## License

[MIT](LICENSE)
