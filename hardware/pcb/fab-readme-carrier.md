# carrier board - PCBWay fabrication + assembly package

## Layer order (order form)

L1: F.Cu (top) / L2: In1.Cu (GND) / L3: In2.Cu (GND_PWR) / L4: B.Cu (bottom)

## Files

| File | Content |
|---|---|
| gerber/carrier-*.gbr | RS-274X, KiCad names, no X2, precision 6, 11 layers: F/In1/In2/B.Cu, F/B.Paste, F/B.Silkscreen, F/B.Mask, Edge.Cuts |
| gerber/carrier-PTH.drl, carrier-NPTH.drl, *-drl_map.pdf | Excellon, mm, decimal, plated and non-plated separate |
| carrier-top-pos.csv, carrier-bottom-pos.csv | Centroid, PCBWay sample columns (Designator, Footprint, Mid X, Mid Y, Ref X, Ref Y, Pad X, Pad Y, TB, Rotation, Comment). Units mm. SMD placed parts only (no test points, no THT-only, no DNP). |
| carrier-pcbway.csv | BOM, PCBWay template 9 columns. DNP rows: Type=DNS. Notes: Turnkey / Consigned |
| carrier-assembly-top.pdf, carrier-assembly-bottom.pdf | Assembly drawing (F.Fab / B.Fab, pad numbers, DNP crossed out; bottom mirrored) |
| carrier.step | 3D (origin = core centre, for enclosure work) |

- Origin: Gerber, drill and centroid share the auxiliary origin = board outline bottom-left (0,0), +Y up.
- Rotation: KiCad values, 0-360, top point of view for both sides, no X mirror, no package correction (R-010 S9). Please confirm rotations in the pre-production check.

## Order form options (reference, R-010 #12 / P-001)

4 layers, FR-4 TG150-160, 1.6 mm, min track/space 6/6 mil (0.15/0.16 mm), min hole 0.3 mm, ENIG 1u", outer/inner copper 1 oz, vias tented, impedance control: 100 ohm diff (CSI/MDI) and 90 ohm diff (USB) on L1/L4 over L2/L3 (to be reviewed at quote time).

## Panel (R-010 #11, P-002 B6)

Board size 40 x 54 mm is smaller than 50 x 100 mm -> assembly needs a panel. Chosen: PCBWay panelization with rails (3.5 mm+) and 3 fiducials on the rails, single-board design files here. Alternative (not used): customer V-score panel with 5 mm rails.

## X-ray (R-010 #13)

Bottom-terminated / exposed-pad parts: U2 (HTSSOP-16 exposed pad), U4/U5 (USON-10)

## Consigned parts and gates (R-010 #14, #15)

- Consigned parts are the BOM rows with "Consigned" in Notes.
- Do not order before gates: G1 (BTB mating with the real core module) and G2 (S401 holder fit). Files only; no upload, quote or order was made.
