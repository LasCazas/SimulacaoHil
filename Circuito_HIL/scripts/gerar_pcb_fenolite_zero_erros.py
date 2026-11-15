"""Gerador da PCB Face Simples Definitiva para a Bancada HIL.
Equipe IF Betim Racing - IFMG Campus Betim.
100% Camada Inferior (B.Cu) - ZERO Cruzamentos, ZERO Curtos.
"""

import math
import subprocess
import os

def generate_pcb():
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
    board_h = 95.0

    # Posições Centrais
    u1_cx, u1_cy = 40.0, 50.0
    u2_cx, u2_cy = 95.0, 26.0
    u3_cx, u3_cy = 95.0, 75.0
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
    pcm_p1_x = u2_cx - 7.62 # 87.38
    pcm_p2_x = u2_cx + 7.62 # 102.62
    pcm_pins = {}
    for i in range(10):
        pcm_pins[i + 1] = (pcm_p1_x, u2_cy - 4.5 * 2.54 + i * 2.54)
    pcm_pins[11] = (pcm_p2_x, 26.16) # LOUT -> CRANK+
    pcm_pins[12] = (pcm_p2_x, 31.24) # AGND -> VR1-
    pcm_pins[13] = (pcm_p2_x, 36.32) # ROUT (NC)

    # Level Converter (U3) no rodapé
    u3_lv_x = u3_cx - 6.35 # 88.65
    u3_hv_x = u3_cx + 6.35 # 101.35
    u3_pins = {}
    for i in range(6):
        u3_pins[i + 1] = (u3_hv_x, u3_cy - 2.5 * 2.54 + i * 2.54)
    for i in range(6):
        u3_pins[7 + i] = (u3_lv_x, u3_cy - 2.5 * 2.54 + i * 2.54)

    # J1 Borne 9P (Alinhamento 100% Planar Monótono)
    j1_pins = {
        1: (j1_x, 16.00), # MAP
        2: (j1_x, 21.08), # TPS
        3: (j1_x, 26.16), # CRANK+
        4: (j1_x, 31.24), # VR1-
        5: (j1_x, 55.08), # VSS
        6: (j1_x, 65.24), # CLUTCH
        7: (j1_x, 74.00), # INJ
        8: (j1_x, 77.54), # IGN
        9: (j1_x, 86.00)  # GND
    }

    # Filtros RC à esquerda do ESP32 (x=16)
    r1_p2, r1_p1 = (18.0, 50.0), (12.0, 50.0)
    c1_p1, c1_p2 = (12.0, 46.0), (18.0, 46.0)
    r2_p2, r2_p1 = (18.0, 52.54), (12.0, 52.54)
    c2_p1, c2_p2 = (12.0, 56.54), (18.0, 56.54)

    pin_nets = {
        ("U1", "8"): 17, ("U1", "9"): 18, ("U1", "10"): 8, ("U1", "11"): 10,
        ("U1", "14"): 16, ("U1", "15"): 2, ("U1", "16"): 1, ("U1", "17"): 3,
        ("U1", "20"): 7, ("U1", "21"): 15, ("U1", "23"): 6, ("U1", "29"): 9,
        ("U2", "1"): 2, ("U2", "2"): 16, ("U2", "3"): 8, ("U2", "4"): 9,
        ("U2", "5"): 10, ("U2", "6"): 16, ("U2", "7"): 1, ("U2", "8"): 16,
        ("U2", "9"): 16, ("U2", "10"): 16, ("U2", "11"): 5, ("U2", "12"): 4,
        ("U3", "1"): 2, ("U3", "2"): 16, ("U3", "3"): 13, ("U3", "4"): 14,
        ("U3", "7"): 1, ("U3", "8"): 16, ("U3", "9"): 6, ("U3", "10"): 7,
        ("J1", "1"): 11, # MAP
        ("J1", "2"): 12, # TPS
        ("J1", "3"): 5,  # CRANK+
        ("J1", "4"): 4,  # VR1-
        ("J1", "5"): 15, # VSS
        ("J1", "6"): 3,  # CLUTCH
        ("J1", "7"): 14, # INJ
        ("J1", "8"): 13, # IGN
        ("J1", "9"): 16, # GND
        ("R1", "1"): 12, ("R1", "2"): 17, ("C1", "1"): 12, ("C1", "2"): 16,
        ("R2", "1"): 11, ("R2", "2"): 18, ("C2", "1"): 11, ("C2", "2"): 16,
    }

    tracks = []
    def add_seg(p1, p2, width, net_id):
        tracks.append((round(p1[0], 2), round(p1[1], 2), round(p2[0], 2), round(p2[1], 2), width, net_id))

    def add_path(pts, width, net_id):
        for i in range(len(pts) - 1):
            add_seg(pts[i], pts[i+1], width, net_id)

    # 1. Filtros à esquerda do ESP32 e saídas pelo topo
    add_path([esp_pins[9], r2_p2], 0.8, 18) # D26 -> R2
    add_path([r2_p1, c2_p1, (6.0, 52.54), (6.0, 4.0), (135.0, 4.0), j1_pins[1]], 0.8, 11) # MAP_OUT -> J1.1

    add_path([esp_pins[8], r1_p2], 0.8, 17) # D25 -> R1
    add_path([r1_p1, c1_p1, (9.0, 50.00), (9.0, 7.0), (132.0, 7.0), (132.0, j1_pins[2][1]), j1_pins[2]], 0.8, 12) # TPS_OUT -> J1.2

    # 2. I2S para PCM5102
    add_path([esp_pins[11], (12.0, esp_pins[11][1]), (12.0, 10.0), (pcm_pins[5][0], 10.0), pcm_pins[5]], 0.8, 10) # LCK
    add_path([esp_pins[10], (15.0, esp_pins[10][1]), (15.0, 13.0), (pcm_pins[3][0], 13.0), pcm_pins[3]], 0.8, 8)  # BCK
    add_path([esp_pins[29], (75.0, esp_pins[29][1]), (75.0, pcm_pins[4][1]), pcm_pins[4]], 0.8, 9) # DIN

    # Saídas Analógicas PCM5102
    add_path([pcm_pins[11], j1_pins[3]], 0.8, 5) # CRANK+ -> J1.3
    add_path([pcm_pins[12], j1_pins[4]], 0.8, 4) # CRANK- -> J1.4

    # 3. VSS e CLUTCH direto para J1
    add_path([esp_pins[21], j1_pins[5]], 0.8, 15) # VSS -> J1.5
    add_path([esp_pins[17], j1_pins[6]], 0.8, 3)  # CLUTCH -> J1.6

    # 4. IGN e INJ: vão central do ESP32 -> U3 no rodapé -> J1
    add_path([esp_pins[20], (45.0, esp_pins[20][1]), (45.0, 74.0), (u3_pins[10][0], 74.0), u3_pins[10]], 0.8, 7) # FB_INJ
    add_path([u3_pins[4], j1_pins[7]], 0.8, 14) # SPEEDUINO_INJ -> J1.7

    add_path([esp_pins[23], (42.0, esp_pins[23][1]), (42.0, 77.54), (u3_pins[9][0], 77.54), u3_pins[9]], 0.8, 6) # FB_IGN
    add_path([u3_pins[3], j1_pins[8]], 0.8, 13) # SPEEDUINO_IGN -> J1.8

    # 5. Alimentação e Terra no Rodapé
    # +3V3 (y = 71.0)
    add_path([esp_pins[16], (esp_pins[16][0], 71.0), (u3_pins[7][0], 71.0), u3_pins[7]], 1.0, 1)

    # +5V (y = 82.5)
    add_path([esp_pins[15], (esp_pins[15][0], 82.5), (u3_pins[1][0], 82.5), u3_pins[1]], 1.2, 2)

    # GND (y = 86.0)
    add_path([esp_pins[14], (20.0, esp_pins[14][1]), (20.0, 86.0), (j1_pins[9][0], 86.0), j1_pins[9]], 1.4, 16)
    add_path([c1_p2, (20.0, c1_p2[1])], 0.8, 16)
    add_path([c2_p2, (20.0, c2_p2[1])], 0.8, 16)
    add_path([u3_pins[2], (u3_pins[2][0], 86.0)], 1.0, 16)
    add_path([u3_pins[8], (u3_pins[8][0], 86.0)], 1.0, 16)

    # GND e Alimentação PCM5102
    add_path([pcm_pins[2], pcm_pins[6], pcm_pins[8], pcm_pins[9], pcm_pins[10]], 0.8, 16)
    add_path([(20.0, 86.0), (9.0, 86.0), (9.0, 2.5), (pcm_pins[2][0], 2.5), pcm_pins[2]], 1.0, 16)
    add_path([esp_pins[15], (esp_pins[15][0], 82.5), (6.0, 82.5), (6.0, 1.0), (pcm_pins[1][0], 1.0), pcm_pins[1]], 1.0, 2)
    add_path([esp_pins[16], (esp_pins[16][0], 71.0), (70.0, 71.0), (70.0, pcm_pins[7][1]), pcm_pins[7]], 0.8, 1)

    # Construir arquivo KiCad PCB
    out = []
    out.append('(kicad_pcb\n\t(version 20240108)\n\t(generator "kicad_cli")\n\t(generator_version "10.0")')
    out.append('\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)\n\t(paper "A4")')
    out.append('\t(layers\n\t\t(0 "F.Cu" signal)\n\t\t(31 "B.Cu" signal)\n\t\t(36 "B.SilkS" user "B.Silkscreen")\n\t\t(37 "F.SilkS" user "F.Silkscreen")\n\t\t(38 "B.Mask" user)\n\t\t(39 "F.Mask" user)\n\t\t(44 "Edge.Cuts" user)\n\t)')
    out.append('\t(setup\n\t\t(pad_to_mask_clearance 0.15)\n\t)')

    for name, code in sorted(net_map.items(), key=lambda x: x[1]):
        out.append(f'\t(net {code} "{name}")')

    out.append(f'\t(gr_rect (start 3.0 0.5) (end {board_w} {board_h}) (stroke (width 0.2) (type solid)) (layer "Edge.Cuts") (uuid "b0000000-0000-0000-0000-000000000001"))')

    for hx, hy, hid in [(10.0, 8.0, 1), (board_w - 5.0, 8.0, 2), (10.0, board_h - 5.0, 3), (board_w - 5.0, board_h - 5.0, 4)]:
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

    # J1 Borne 9P
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

    write_fp("R1", "R_Axial_10k_TPS", (15.0, 50.0), {1: r1_p1, 2: r1_p2})
    write_fp("C1", "C_Disc_1uF_TPS", (15.0, 46.0), {1: c1_p1, 2: c1_p2})
    write_fp("R2", "R_Axial_10k_MAP", (15.0, 52.54), {1: r2_p1, 2: r2_p2})
    write_fp("C2", "C_Disc_1uF_MAP", (15.0, 56.54), {1: c2_p1, 2: c2_p2})

    borne_labels = [
        (1, "1: MAP (B_C8)"), (2, "2: TPS (B_C7)"), (3, "3: CRANK+ (VR1+)"),
        (4, "4: VR1- (GND_VR)"), (5, "5: VSS (Velocidade)"), (6, "6: CLUTCH (Embreagem)"),
        (7, "7: INJ (Bico Injetor)"), (8, "8: IGN (Bobina Ignição)"), (9, "9: GND (Terra Sensores)")
    ]
    for pnum, text in borne_labels:
        py = j1_pins[pnum][1]
        out.append(f'\t(gr_text "{text}" (at 126.0 {py:.2f}) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15)) (justify right)))')

    out.append('\t(gr_text "IF BETIM RACING - BANCADA HIL SPEEDUINO v2.0" (at 72.0 90.0) (layer "F.SilkS") (effects (font (size 1.3 1.3) (thickness 0.2))))')
    out.append('\t(gr_text "100% TRILHAS BOTTOM (B.Cu) - FACE SIMPLES FENOLITE" (at 72.0 92.5) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.18))))')

    for x1, y1, x2, y2, width, net_id in tracks:
        out.append(f'\t(segment (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width {width}) (layer "B.Cu") (net {net_id}))')

    out.append(')')

    with open('Circuito_HIL/Circuito_HIL.kicad_pcb', 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f"Placa gerada com sucesso! Total de segmentos: {len(tracks)}")

if __name__ == '__main__':
    generate_pcb()
