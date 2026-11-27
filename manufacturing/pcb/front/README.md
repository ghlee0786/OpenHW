# front board - PCBWay fabrication + assembly package

## Layer order (order form)

L1: F.Cu (top) / L2: In1.Cu (GND) / L3: In2.Cu (GND_PWR) / L4: B.Cu (bottom)

## Files

| File | Content |
|---|---|
| gerber/front-*.gbr | RS-274X, KiCad names, no X2, precision 6, 11 layers: F/In1/In2/B.Cu, F/B.Paste, F/B.Silkscreen, F/B.Mask, Edge.Cuts |
| gerber/front-PTH.drl, front-NPTH.drl, *-drl_map.pdf | Excellon, mm, decimal, plated and non-plated separate |
| front-top-pos.csv, front-bottom-pos.csv | Centroid, PCBWay sample columns (Designator, Footprint, Mid X, Mid Y, Ref X, Ref Y, Pad X, Pad Y, TB, Rotation, Comment). Units mm. SMD placed parts only (no test points, no THT-only, no DNP). |
| front-pcbway.csv | BOM, PCBWay template 9 columns. DNP rows: Type=DNS. Notes: Turnkey / Consigned |
| front-assembly-top.pdf, front-assembly-bottom.pdf | Assembly drawing (F.Fab / B.Fab, pad numbers, DNP crossed out; bottom mirrored) |
| front.step | 3D (origin = core centre, for enclosure work) |

- Origin: Gerber, drill and centroid share the auxiliary origin = board outline bottom-left (0,0), +Y up.
- Rotation: KiCad values, 0-360, top point of view for both sides, no X mirror, no package correction (R-010 S9). Please confirm rotations in the pre-production check.

## Order form options (reference, R-010 #12 / P-001)

4 layers, FR-4 TG150-160, 1.6 mm, min track/space 6/6 mil (0.15/0.16 mm), min hole 0.3 mm, ENIG 1u", outer/inner copper 1oz (1/1oz), via process: Tenting vias, impedance control: 100 ohm diff (CSI/MDI) and 90 ohm diff (USB) on L1/L4 over L2/L3 (stack-up to be confirmed with the manufacturer before fabrication).

Vias: 0.65/0.30 mm standard (plus 0.60/0.30 and 0.80/0.40); no hole smaller than 0.30 mm.

## Panel (R-010 #11, P-002 B6)

Board size 40 x 40 mm is smaller than 50 x 100 mm -> assembly needs a panel. Chosen: PCBWay panelization with rails (3.5 mm+) and 3 fiducials on the rails, single-board design files here. Alternative (not used): customer V-score panel with 5 mm rails.

## X-ray (R-010 #13)

Bottom-terminated / exposed-pad parts: U1 (WSON-8 EP), U2 (MSOP-8 EP), U3 (LTR-329 LGA-type), X1 (PQFN-4), D_IR_A1/A2/B1/B2 (VSMA1085600 thermal pad)

## Consigned parts and gates (R-010 #14, #15)

- Consigned parts are the BOM rows with "Consigned" in Notes.
- Do not order before gates: G1 (BTB mating with the real core module) and G2 (S401 holder fit). Files only; nothing was submitted to any manufacturer.
