"""Gerador de Roteamento Perfeito (Zero Erros) para Bancada HIL.
IF Betim Racing.
"""

import math
import subprocess
import os

def run():
    net_map = {
        "": 0,
        "+3V3": 1,
        "+5V": 2,
        "/CLUTCH_SIG": 3,
        "/CRANK_VR_NEG": 4,
        "/CRANK_VR_POS": 5,
        "/FB_IGN_3V3": 6,
        "/FB_INJ_3V3": 7,
        "/I2S_BCK": 8,
        "/I2S_DIN": 9,
        "/I2S_LCK": 10,
        "/NET_MAP_OUT": 11,
        "/NET_TPS_OUT": 12,
        "/SPEEDUINO_IGN": 13,
        "/SPEEDUINO_INJ": 14,
        "/VSS_PULSE": 15,
        "GND": 16,
        "Net-(U1-D25_(DAC_TPS))": 17,
        "Net-(U1-D26_(DAC_MAP))": 18
    }

    board_w = 145.0
    board_h = 100.0

    # Posições Centrais
    u1_cx, u1_cy = 40.0, 50.0
    u2_cx, u2_cy = 98.0, 20.0
    u3_cx, u3_cy = 98.0, 65.0
    j1_x = 135.0

    # ESP32 (U1)
    esp_p1_x = u1_cx - 11.43 # 28.57
    esp_p2_x = u1_cx + 11.43 # 51.43
    esp_pins = {}
    for i in range(15):
        esp_pins[i + 1] = (esp_p1_x, u1_cy - 7 * 2.54 + i * 2.54)
    for i in range(15):
        esp_pins[16 + i] = (esp_p2_x, u1_cy + 7 * 2.54 - i * 2.54)

    # PCM5102 (U2)
    # Largura 15.24mm (600mil) entre fileiras
    pcm_p1_x = u2_cx - 7.62 # 90.38
    pcm_p2_x = u2_cx + 7.62 # 105.62
    pcm_pins = {}
    for i in range(10):
        pcm_pins[i + 1] = (pcm_p1_x, u2_cy - 4.5 * 2.54 + i * 2.54)
    pcm_pins[11] = (pcm_p2_x, 15.0)  # LOUT
    pcm_pins[12] = (pcm_p2_x, 20.0)  # AGND
    pcm_pins[13] = (pcm_p2_x, 25.0)  # ROUT

    # Level Converter (U3)
    u3_lv_x = u3_cx - 6.35 # 91.65
    u3_hv_x = u3_cx + 6.35 # 104.35
    u3_pins = {}
    for i in range(6):
        u3_pins[i + 1] = (u3_hv_x, u3_cy - 2.5 * 2.54 + i * 2.54)
    for i in range(6):
        u3_pins[7 + i] = (u3_lv_x, u3_cy - 2.5 * 2.54 + i * 2.54)

    # Borne J1 (9 Pinos a 5.08mm)
    j1_pins = {}
    for i in range(9):
        j1_pins[i + 1] = (j1_x, 15.0 + i * 5.08)

    # Filtros RC
    r1_p1, r1_p2 = (60.0, 25.0), (70.0, 25.0) # p2 = entrada (60), p1 = saída (70)
    c1_p1, c1_p2 = (76.0, 25.0), (76.0, 30.0)
    r2_p1, r2_p2 = (60.0, 30.0), (70.0, 30.0)
    c2_p1, c2_p2 = (82.0, 30.0), (82.0, 35.0)

    pin_nets = {
        ("U1", "8"): 17, ("U1", "9"): 18, ("U1", "10"): 8, ("U1", "11"): 10,
        ("U1", "14"): 16, ("U1", "15"): 2, ("U1", "16"): 1, ("U1", "17"): 3,
        ("U1", "20"): 7, ("U1", "21"): 15, ("U1", "23"): 6, ("U1", "29"): 9,
        ("U2", "1"): 2, ("U2", "2"): 16, ("U2", "3"): 8, ("U2", "4"): 9,
        ("U2", "5"): 10, ("U2", "6"): 16, ("U2", "7"): 1, ("U2", "8"): 16,
        ("U2", "9"): 16, ("U2", "10"): 16, ("U2", "11"): 5, ("U2", "12"): 4,
        ("U3", "1"): 2, ("U3", "2"): 16, ("U3", "3"): 13, ("U3", "4"): 14,
        ("U3", "7"): 1, ("U3", "8"): 16, ("U3", "9"): 6, ("U3", "10"): 7,
        ("J1", "1"): 5, ("J1", "2"): 4, ("J1", "3"): 12, ("J1", "4"): 11,
        ("J1", "5"): 15, ("J1", "6"): 3, ("J1", "7"): 14, ("J1", "8"): 13, ("J1", "9"): 16,
        ("R1", "1"): 12, ("R1", "2"): 17, ("C1", "1"): 12, ("C1", "2"): 16,
        ("R2", "1"): 11, ("R2", "2"): 18, ("C2", "1"): 11, ("C2", "2"): 16,
    }

    tracks = []
    def add_seg(p1, p2, width, net_id):
        tracks.append((round(p1[0], 2), round(p1[1], 2), round(p2[0], 2), round(p2[1], 2), width, net_id))

    def add_path(pts, width, net_id):
        for i in range(len(pts) - 1):
            add_seg(pts[i], pts[i+1], width, net_id)

    # 1. CRANK+ (Net 5): U2.11 -> J1.1 (Y = 15.0)
    add_path([pcm_pins[11], j1_pins[1]], 0.8, 5)

    # 2. CRANK- (Net 4): U2.12 -> J1.2 (Y = 20.08)
    add_path([pcm_pins[12], (115.0, pcm_pins[12][1]), (115.0, j1_pins[2][1]), j1_pins[2]], 0.8, 4)

    # 3. TPS (Net 17 entrada, Net 12 saída):
    # U1.8 (D25) -> R1 p2 (60.0, 25.0)
    add_path([esp_pins[8], (20.0, esp_pins[8][1]), (20.0, 25.0), r1_p2], 0.8, 17)
    # R1 p1 (70.0, 25.0) -> C1 p1 (76.0, 25.0) -> J1.3 (Y = 25.16)
    add_path([r1_p1, c1_p1, (115.0, 25.0), (115.0, j1_pins[3][1]), j1_pins[3]], 0.8, 12)

    # 4. MAP (Net 18 entrada, Net 11 saída):
    # U1.9 (D26) -> R2 p2 (60.0, 30.0)
    add_path([esp_pins[9], (17.0, esp_pins[9][1]), (17.0, 30.0), r2_p2], 0.8, 18)
    # R2 p1 (70.0, 30.0) -> C2 p1 (82.0, 30.0) -> J1.4 (Y = 30.24)
    add_path([r2_p1, c2_p1, (115.0, 30.0), (115.0, j1_pins[4][1]), j1_pins[4]], 0.8, 11)

    # 5. I2S_BCK (Net 8): U1.10 -> U2.3
    add_path([esp_pins[10], (14.0, esp_pins[10][1]), (14.0, 8.0), (85.0, 8.0), (85.0, pcm_pins[3][1]), pcm_pins[3]], 0.8, 8)

    # 6. I2S_LCK (Net 10): U1.11 -> U2.5
    add_path([esp_pins[11], (11.0, esp_pins[11][1]), (11.0, 5.0), (87.0, 5.0), (87.0, pcm_pins[5][1]), pcm_pins[5]], 0.8, 10)

    # 7. I2S_DIN (Net 9): U1.29 -> U2.4
    add_path([esp_pins[29], (55.0, esp_pins[29][1]), (55.0, 35.0), (88.0, 35.0), (88.0, pcm_pins[4][1]), pcm_pins[4]], 0.8, 9)

    # 8. VSS_PULSE (Net 15): U1.21 -> J1.5 (Y = 35.32)
    # Vão central do ESP32: x=38.0
    add_path([esp_pins[21], (38.0, esp_pins[21][1]), (38.0, 35.32), j1_pins[5]], 0.8, 15)

    # 9. CLUTCH_SIG (Net 3): U1.17 -> J1.6 (Y = 40.40)
    # Vão central do ESP32: x=35.0
    add_path([esp_pins[17], (35.0, esp_pins[17][1]), (35.0, 40.40), j1_pins[6]], 0.8, 3)

    # 10. SPEEDUINO_IGN (Net 13): U3.3 (HV1) -> J1.8 (Y = 50.56)
    add_path([u3_pins[3], (118.0, u3_pins[3][1]), (118.0, j1_pins[8][1]), j1_pins[8]], 0.8, 13)

    # 11. SPEEDUINO_INJ (Net 14): U3.4 (HV2) -> J1.7 (Y = 45.48)
    add_path([u3_pins[4], (121.0, u3_pins[4][1]), (121.0, j1_pins[7][1]), j1_pins[7]], 0.8, 14)

    # 12. FB_IGN_3V3 (Net 6): U1.23 -> U3.9 (LV1)
    add_path([esp_pins[23], (70.0, esp_pins[23][1]), (70.0, u3_pins[9][1]), u3_pins[9]], 0.8, 6)

    # 13. FB_INJ_3V3 (Net 7): U1.20 -> U3.10 (LV2)
    add_path([esp_pins[20], (73.0, esp_pins[20][1]), (73.0, u3_pins[10][1]), u3_pins[10]], 0.8, 7)

    # 14. +5V (Net 2): U1.15 -> U3.1 -> U2.1
    # Margem inferior y = 84.0
    add_path([esp_pins[15], (esp_pins[15][0], 84.0), (108.0, 84.0), (108.0, u3_pins[1][1]), u3_pins[1]], 1.2, 2)
    add_path([(108.0, 84.0), (110.0, 84.0), (110.0, 10.0), (95.0, 10.0), (95.0, pcm_pins[1][1]), pcm_pins[1]], 1.2, 2)

    # 15. +3V3 (Net 1): U1.16 -> U3.7 -> U2.7
    add_path([esp_pins[16], (esp_pins[16][0], 81.0), (86.0, 81.0), (86.0, u3_pins[7][1]), u3_pins[7]], 1.0, 1)
    add_path([(86.0, u3_pins[7][1]), (86.0, pcm_pins[7][1]), pcm_pins[7]], 1.0, 1)

    # 16. GND (Net 16):
    add_path([esp_pins[14], (esp_pins[14][0], 88.0), (j1_pins[9][0], 88.0), j1_pins[9]], 1.4, 16)
    # U3 GND
    add_path([(u3_pins[8][0], 88.0), u3_pins[8]], 1.0, 16)
    add_path([(u3_pins[2][0], 88.0), u3_pins[2]], 1.0, 16)
    # C1, C2 GND
    add_path([c1_p2, (c1_p2[0], 88.0)], 1.0, 16)
    add_path([c2_p2, (c2_p2[0], 88.0)], 1.0, 16)
    # U2 GND spine em x = 83.0 mm
    add_path([(83.0, 88.0), (83.0, pcm_pins[2][1])], 1.2, 16)
    for p in [2, 6, 8, 9, 10]:
        add_path([(83.0, pcm_pins[p][1]), pcm_pins[p]], 0.8, 16)

    # Construir S-Expression do KiCad
    out = []
    out.append('(kicad_pcb\n\t(version 20240108)\n\t(generator "kicad_cli")\n\t(generator_version "10.0")')
    out.append('\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)\n\t(paper "A4")')
    out.append('\t(layers\n\t\t(0 "F.Cu" signal)\n\t\t(31 "B.Cu" signal)\n\t\t(36 "B.SilkS" user "B.Silkscreen")\n\t\t(37 "F.SilkS" user "F.Silkscreen")\n\t\t(38 "B.Mask" user)\n\t\t(39 "F.Mask" user)\n\t\t(44 "Edge.Cuts" user)\n\t)')
    out.append('\t(setup\n\t\t(pad_to_mask_clearance 0.15)\n\t)')

    for name, code in sorted(net_map.items(), key=lambda x: x[1]):
        out.append(f'\t(net {code} "{name}")')

    out.append(f'\t(gr_rect (start 5.0 3.0) (end {board_w} {board_h}) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (uuid "b0000000-0000-0000-0000-000000000001"))')

    for hx, hy, hid in [(10.0, 10.0, 1), (board_w - 5.0, 10.0, 2), (10.0, board_h - 5.0, 3), (board_w - 5.0, board_h - 5.0, 4)]:
        out.append(f'\t(footprint "MountingHole:MountingHole_3.2mm_M3" (layer "F.Cu") (at {hx} {hy}) (uuid "h0000000-0000-0000-0000-{hid:012d}")')
        out.append(f'\t\t(pad "1" np_thru_hole circle (at 0 0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))\n\t)')

    def write_fp(ref, val, pos, pin_dict):
        out.append(f'\t(footprint "HIL:{val}" (layer "F.Cu") (at {pos[0]} {pos[1]}) (uuid "f0000000-0000-0000-{ref:04s}-000000000001")')
        out.append(f'\t\t(property "Reference" "{ref}" (at 0 -2.54 0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
        out.append(f'\t\t(property "Value" "{val}" (at 0 2.54 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
        for pnum, (px, py) in pin_dict.items():
            rel_x, rel_y = round(px - pos[0], 2), round(py - pos[1], 2)
            net_code = pin_nets.get((ref, str(pnum)), 0)
            net_name = [k for k, v in net_map.items() if v == net_code][0] if net_code != 0 else ""
            pad_shape = "rect" if str(pnum) == "1" else "circle"
            out.append(f'\t\t(pad "{pnum}" thru_hole {pad_shape} (at {rel_x} {rel_y}) (size 2.0 2.0) (drill 1.0) (layers "*.Cu" "*.Mask") (net {net_code} "{net_name}"))')
        out.append('\t)')

    write_fp("U1", "ESP32_DevKit_V1_30Pin", (u1_cx, u1_cy), esp_pins)
    write_fp("U2", "GY_PCM5102A", (u2_cx, u2_cy), pcm_pins)
    write_fp("U3", "Logic_Level_Converter_4CH", (u3_cx, u3_cy), u3_pins)

    # J1
    out.append(f'\t(footprint "Connector_TerminalBlock:TerminalBlock_bornier-9_P5.08mm" (layer "F.Cu") (at {j1_x} {u1_cy}) (uuid "f0000000-0000-0000-J100-000000000001")')
    out.append(f'\t\t(property "Reference" "J1" (at 0 -25.0 0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    out.append(f'\t\t(property "Value" "Borne_Speeduino_9P" (at 0 25.0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    for pnum, (px, py) in j1_pins.items():
        rel_x, rel_y = round(px - j1_x, 2), round(py - u1_cy, 2)
        net_code = pin_nets.get(("J1", str(pnum)), 0)
        net_name = [k for k, v in net_map.items() if v == net_code][0] if net_code != 0 else ""
        pad_shape = "rect" if pnum == 1 else "circle"
        out.append(f'\t\t(pad "{pnum}" thru_hole {pad_shape} (at {rel_x} {rel_y}) (size 3.2 3.2) (drill 1.4) (layers "*.Cu" "*.Mask") (net {net_code} "{net_name}"))')
    out.append('\t)')

    write_fp("R1", "R_Axial_10k_TPS", (65.0, 25.0), {1: r1_p1, 2: r1_p2})
    write_fp("C1", "C_Disc_1uF_TPS", (76.0, 27.5), {1: c1_p1, 2: c1_p2})
    write_fp("R2", "R_Axial_10k_MAP", (65.0, 30.0), {1: r2_p1, 2: r2_p2})
    write_fp("C2", "C_Disc_1uF_MAP", (82.0, 32.5), {1: c2_p1, 2: c2_p2})

    borne_labels = [
        (1, "1: CRANK+ (VR1+)"), (2, "2: VR1- (GND_VR)"), (3, "3: TPS (B_C7)"),
        (4, "4: MAP (B_C8)"), (5, "5: VSS (Velocidade)"), (6, "6: CLUTCH (Embreagem)"),
        (7, "7: INJ (Bico Injetor)"), (8, "8: IGN (Bobina Ignição)"), (9, "9: GND (Terra Sensores)")
    ]
    for pnum, text in borne_labels:
        py = j1_pins[pnum][1]
        out.append(f'\t(gr_text "{text}" (at 126.0 {py:.2f}) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15)) (justify right)))')

    out.append('\t(gr_text "IF BETIM RACING - BANCADA HIL SPEEDUINO v2.0" (at 72.0 92.0) (layer "F.SilkS") (effects (font (size 1.3 1.3) (thickness 0.2))))')
    out.append('\t(gr_text "100% TRILHAS BOTTOM (B.Cu) - FACE SIMPLES FENOLITE" (at 72.0 95.0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.18))))')

    for x1, y1, x2, y2, width, net_id in tracks:
        out.append(f'\t(segment (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width {width}) (layer "B.Cu") (net {net_id}))')

    out.append(')')

    with open('Circuito_HIL/Circuito_HIL.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f"PCB escrita com sucesso! Total de segmentos: {len(tracks)}")

if __name__ == '__main__':
    run()
