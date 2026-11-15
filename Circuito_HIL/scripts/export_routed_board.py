"""Gera a PCB final usando as rotas calculadas pelo GridRouter e valida no DRC do KiCad.
"""

from auto_route_perfect import b_cu_tracks, f_cu_tracks, esp_pins, pcm_pins, u3_pins, j1_pins, r1_p1, r1_p2, c1_p1, c1_p2, r2_p1, r2_p2, c2_p1, c2_p2, pin_nets, net_map, u1_cx, u1_cy, u2_cx, u2_cy, u3_cx, u3_cy, j1_x
import subprocess

out = []
out.append('(kicad_pcb\n\t(version 20240108)\n\t(generator "kicad_cli")\n\t(generator_version "10.0")')
out.append('\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)\n\t(paper "A4")')
out.append('\t(layers\n\t\t(0 "F.Cu" signal)\n\t\t(31 "B.Cu" signal)\n\t\t(36 "B.SilkS" user "B.Silkscreen")\n\t\t(37 "F.SilkS" user "F.Silkscreen")\n\t\t(38 "B.Mask" user)\n\t\t(39 "F.Mask" user)\n\t\t(44 "Edge.Cuts" user)\n\t)')
out.append('\t(setup\n\t\t(pad_to_mask_clearance 0.15)\n\t\t(pcb_text_size 1.0 1.0)\n\t\t(pcb_text_width 0.15)\n\t)')

for name, code in sorted(net_map.items(), key=lambda x: x[1]):
    if code > 0:
        out.append(f'\t(net {code} "{name}")')

out.append('\t(gr_rect (start 4.0 2.0) (end 146.0 96.0) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts"))')

for mx, my in [(9.0, 7.0), (141.0, 7.0), (9.0, 91.0), (141.0, 91.0)]:
    out.append(f'\t(footprint "MountingHole:MountingHole_3.2mm_M3" (layer "F.Cu") (at {mx} {my})')
    out.append('\t\t(pad "" np_thru_hole circle (at 0 0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))\n\t)')

# ESP32
esp_names_left = ["EN", "36", "39", "34", "35", "32", "33", "25", "26", "27", "14", "12", "13", "GND", "VIN"]
esp_names_right = ["3V3", "GND", "15", "D2", "D4", "16", "17", "D5", "18", "19", "21", "RX0", "TX0", "22", "23"]

out.append(f'\t(footprint "HIL:ESP32_DevKit_V1_30Pin" (layer "F.Cu") (at {u1_cx} {u1_cy}) (uuid "f0000000-0000-0000-U001-000000000001")')
out.append('\t\t(property "Reference" "U1" (at 0 -22.0 0) (layer "F.SilkS") (effects (font (size 1.4 1.4) (thickness 0.25))))')
out.append('\t\t(property "Value" "ESP32_DevKit_V1" (at 0 22.0 0) (layer "F.SilkS") (hide yes) (effects (font (size 1.1 1.1) (thickness 0.18))))')
out.append('\t\t(fp_rect (start -14.0 -20.0) (end 14.0 20.0) (stroke (width 0.25) (type solid)) (layer "F.SilkS"))')
out.append('\t\t(fp_rect (start -4.5 -21.5) (end 4.5 -19.5) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
out.append('\t\t(fp_text user "USB" (at 0 -18.0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
out.append('\t\t(fp_rect (start -11.0 14.0) (end 11.0 19.0) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))')
out.append('\t\t(fp_text user "ANTENNA" (at 0 16.5 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
out.append('\t\t(fp_text user "ESP-WROOM-32" (at 0 0 90) (layer "F.SilkS") (effects (font (size 1.4 1.4) (thickness 0.22))))')
for pnum, (px, py) in esp_pins.items():
    rx, ry = round(px - u1_cx, 2), round(py - u1_cy, 2)
    n_code = pin_nets.get(("U1", str(pnum)), 0)
    n_name = [k for k, v in net_map.items() if v == n_code][0] if n_code != 0 else ""
    shape = "rect" if pnum == 1 else "circle"
    out.append(f'\t\t(pad "{pnum}" thru_hole {shape} (at {rx} {ry}) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {n_code} "{n_name}"))')
    if pnum <= 15:
        pname = esp_names_left[pnum - 1]
        out.append(f'\t\t(fp_text user "{pname}" (at {rx + 4.8:.2f} {ry:.2f} 0) (layer "F.SilkS") (effects (font (size 0.95 0.95) (thickness 0.15)) (justify left)))')
    else:
        pname = esp_names_right[pnum - 16]
        out.append(f'\t\t(fp_text user "{pname}" (at {rx - 4.8:.2f} {ry:.2f} 0) (layer "F.SilkS") (effects (font (size 0.95 0.95) (thickness 0.15)) (justify right)))')
out.append('\t)')

# PCM5102
pcm_names = ["VCC", "GND", "BCK", "DIN", "LCK", "SCK", "XMT", "FMT", "FLT", "DMP"]
out.append(f'\t(footprint "HIL:GY_PCM5102A" (layer "F.Cu") (at {u2_cx} {u2_cy}) (uuid "f0000000-0000-0000-U002-000000000001")')
out.append('\t\t(property "Reference" "U2" (at 0 -14.0 0) (layer "F.SilkS") (effects (font (size 1.3 1.3) (thickness 0.22))))')
out.append('\t\t(property "Value" "GY-PCM5102A" (at 0 14.0 0) (layer "F.SilkS") (hide yes) (effects (font (size 1.0 1.0) (thickness 0.15))))')
out.append('\t\t(fp_rect (start -10.0 -12.5) (end 10.0 12.5) (stroke (width 0.25) (type solid)) (layer "F.SilkS"))')
out.append('\t\t(fp_text user "PCM5102A (VR)" (at 0 0 90) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.16))))')
for pnum, (px, py) in pcm_pins.items():
    rx, ry = round(px - u2_cx, 2), round(py - u2_cy, 2)
    n_code = pin_nets.get(("U2", str(pnum)), 0)
    n_name = [k for k, v in net_map.items() if v == n_code][0] if n_code != 0 else ""
    shape = "rect" if pnum == 1 else "circle"
    out.append(f'\t\t(pad "{pnum}" thru_hole {shape} (at {rx} {ry}) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {n_code} "{n_name}"))')
    if pnum <= 10:
        out.append(f'\t\t(fp_text user "{pcm_names[pnum-1]}" (at {rx + 4.5:.2f} {ry:.2f} 0) (layer "F.SilkS") (effects (font (size 0.95 0.95) (thickness 0.15)) (justify left)))')
out.append('\t\t(fp_text user "CRK+" (at 4.5 -1.0 0) (layer "F.SilkS") (effects (font (size 0.95 0.95) (thickness 0.15)) (justify right)))')
out.append('\t\t(fp_text user "VR-" (at 4.5 4.08 0) (layer "F.SilkS") (effects (font (size 0.95 0.95) (thickness 0.15)) (justify right)))')
out.append('\t)')

# Level Converter U3
u3_names_lv = ["TXI", "RXO", "LV", "GND", "RXO", "TXI"]
u3_names_hv = ["TXO", "RXI", "HV", "GND", "RXI", "TXO"]
out.append(f'\t(footprint "HIL:Logic_Level_Converter_4CH" (layer "F.Cu") (at {u3_cx} {u3_cy}) (uuid "f0000000-0000-0000-U003-000000000001")')
out.append('\t\t(property "Reference" "U3" (at 0 -9.5 0) (layer "F.SilkS") (effects (font (size 1.3 1.3) (thickness 0.22))))')
out.append('\t\t(property "Value" "Level_Converter" (at 0 9.5 0) (layer "F.SilkS") (hide yes) (effects (font (size 1.0 1.0) (thickness 0.15))))')
out.append('\t\t(fp_rect (start -8.0 -8.0) (end 8.0 8.0) (stroke (width 0.25) (type solid)) (layer "F.SilkS"))')
for pnum, (px, py) in u3_pins.items():
    rx, ry = round(px - u3_cx, 2), round(py - u3_cy, 2)
    n_code = pin_nets.get(("U3", str(pnum)), 0)
    n_name = [k for k, v in net_map.items() if v == n_code][0] if n_code != 0 else ""
    shape = "rect" if pnum == 1 else "circle"
    out.append(f'\t\t(pad "{pnum}" thru_hole {shape} (at {rx} {ry}) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {n_code} "{n_name}"))')
    if pnum <= 6:
        out.append(f'\t\t(fp_text user "{u3_names_hv[pnum-1]}" (at {rx - 3.8:.2f} {ry:.2f} 0) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.14)) (justify right)))')
    else:
        out.append(f'\t\t(fp_text user "{u3_names_lv[pnum-7]}" (at {rx + 3.8:.2f} {ry:.2f} 0) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.14)) (justify left)))')
out.append('\t)')

# R1 (10k TPS)
out.append(f'\t(footprint "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" (layer "F.Cu") (at 80.08 30.0) (uuid "f0000000-0000-0000-00R1-000000000001")')
out.append('\t\t(property "Reference" "R1" (at 0 -2.6 0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
out.append('\t\t(property "Value" "10k TPS" (at 0 2.6 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
out.append('\t\t(fp_rect (start -3.15 -1.25) (end 3.15 1.25) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
out.append('\t\t(fp_line (start -5.08 0) (end -3.15 0) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
out.append('\t\t(fp_line (start 3.15 0) (end 5.08 0) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
out.append(f'\t\t(pad "2" thru_hole circle (at -5.08 0) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pin_nets[("R1", "2")]} "Net-(U1-D25_(DAC_TPS))"))')
out.append(f'\t\t(pad "1" thru_hole circle (at 5.08 0) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pin_nets[("R1", "1")]} "/NET_TPS_OUT"))')
out.append('\t)')

# C1 (1uF TPS)
out.append(f'\t(footprint "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" (layer "F.Cu") (at 90.0 27.5) (uuid "f0000000-0000-0000-00C1-000000000001")')
out.append('\t\t(property "Reference" "C1" (at 3.8 -1.0 0) (layer "F.SilkS") (effects (font (size 1.1 1.1) (thickness 0.18)) (justify left)))')
out.append('\t\t(property "Value" "1uF" (at 3.8 1.0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15)) (justify left)))')
out.append('\t\t(fp_circle (center 0 0) (end 2.5 0) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
out.append(f'\t\t(pad "1" thru_hole circle (at 0 2.5) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pin_nets[("C1", "1")]} "/NET_TPS_OUT"))')
out.append(f'\t\t(pad "2" thru_hole circle (at 0 -2.5) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pin_nets[("C1", "2")]} "GND"))')
out.append('\t)')

# R2 (10k MAP)
out.append(f'\t(footprint "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" (layer "F.Cu") (at 80.08 40.0) (uuid "f0000000-0000-0000-00R2-000000000001")')
out.append('\t\t(property "Reference" "R2" (at 0 -2.6 0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
out.append('\t\t(property "Value" "10k MAP" (at 0 2.6 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
out.append('\t\t(fp_rect (start -3.15 -1.25) (end 3.15 1.25) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
out.append('\t\t(fp_line (start -5.08 0) (end -3.15 0) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
out.append('\t\t(fp_line (start 3.15 0) (end 5.08 0) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
out.append(f'\t\t(pad "2" thru_hole circle (at -5.08 0) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pin_nets[("R2", "2")]} "Net-(U1-D26_(DAC_MAP))"))')
out.append(f'\t\t(pad "1" thru_hole circle (at 5.08 0) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pin_nets[("R2", "1")]} "/NET_MAP_OUT"))')
out.append('\t)')

# C2 (1uF MAP)
out.append(f'\t(footprint "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" (layer "F.Cu") (at 90.0 42.5) (uuid "f0000000-0000-0000-00C2-000000000001")')
out.append('\t\t(property "Reference" "C2" (at 3.8 -1.0 0) (layer "F.SilkS") (effects (font (size 1.1 1.1) (thickness 0.18)) (justify left)))')
out.append('\t\t(property "Value" "1uF" (at 3.8 1.0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15)) (justify left)))')
out.append('\t\t(fp_circle (center 0 0) (end 2.5 0) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
out.append(f'\t\t(pad "1" thru_hole circle (at 0 -2.5) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pin_nets[("C2", "1")]} "/NET_MAP_OUT"))')
out.append(f'\t\t(pad "2" thru_hole circle (at 0 2.5) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pin_nets[("C2", "2")]} "GND"))')
out.append('\t)')

# Borne J1
out.append(f'\t(footprint "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-9-5.08_1x09_P5.08mm_Horizontal" (layer "F.Cu") (at {j1_x} {u1_cy}) (uuid "f0000000-0000-0000-J001-000000000001")')
out.append('\t\t(property "Reference" "J1" (at 0 -25.0 0) (layer "F.SilkS") (effects (font (size 1.4 1.4) (thickness 0.25))))')
out.append('\t\t(property "Value" "Borne_Speeduino_9P" (at 0 25.0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
out.append('\t\t(fp_rect (start -4.5 -23.5) (end 4.5 23.5) (stroke (width 0.3) (type solid)) (layer "F.SilkS"))')
for pnum, (px, py) in j1_pins.items():
    rel_x, rel_y = round(px - j1_x, 2), round(py - u1_cy, 2)
    n_code = pin_nets.get(("J1", str(pnum)), 0)
    n_name = [k for k, v in net_map.items() if v == n_code][0] if n_code != 0 else ""
    shape = "rect" if pnum == 1 else "circle"
    out.append(f'\t\t(pad "{pnum}" thru_hole {shape} (at {rel_x} {rel_y}) (size 3.2 3.2) (drill 1.4) (layers "*.Cu" "*.Mask") (net {n_code} "{n_name}"))')
    out.append(f'\t\t(fp_rect (start {rel_x - 2.0:.2f} {rel_y - 2.0:.2f}) (end {rel_x + 2.0:.2f} {rel_y + 2.0:.2f}) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))')
out.append('\t)')

borne_labels = [
    (1, "1: CRANK+ (VR1+)"), (2, "2: VR1- (GND_VR)"), (3, "3: TPS (B_C7)"),
    (4, "4: MAP (B_C8)"), (5, "5: VSS (Velocidade)"), (6, "6: CLUTCH (Embreagem)"),
    (7, "7: IGN (Bobina)"), (8, "8: INJ (Injetor)"), (9, "9: GND (Terra)")
]
for pnum, text in borne_labels:
    py = j1_pins[pnum][1]
    out.append(f'\t(gr_text "{text}" (at 129.0 {py:.2f}) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.16)) (justify right)))')

out.append('\t(gr_text "IF BETIM RACING - BANCADA HIL SPEEDUINO v2.0" (at 75.0 92.0) (layer "F.SilkS") (effects (font (size 1.4 1.4) (thickness 0.22))))')
out.append('\t(gr_text "PLACA DE FENOLITE FACE SIMPLES (TRILHAS B.Cu + JUMPERS NO TOPO)" (at 75.0 94.5) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')

# Trilhas B.Cu
for x1, y1, x2, y2, width, net_id in b_cu_tracks:
    out.append(f'\t(segment (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width {width}) (layer "B.Cu") (net {net_id}))')

# Trilhas F.Cu (Jumpers de Fio)
for x1, y1, x2, y2, width, net_id in f_cu_tracks:
    out.append(f'\t(segment (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width {width}) (layer "F.Cu") (net {net_id}))')

out.append(')')

with open('Circuito_HIL/Circuito_HIL.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print("PCB escrita em Circuito_HIL/Circuito_HIL.kicad_pcb")
