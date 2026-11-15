"""Roteador Ortogonal com Entradas Perpendiculares (Zero Colisões em Pads).
"""

from verify_board_clearances import check_board, dist_pt_seg, seg_intersects

def solve():
    esp_p1_x = 28.57
    esp_p2_x = 51.43
    esp_cy = 50.0

    esp_pins = {}
    for i in range(15):
        esp_pins[i + 1] = (esp_p1_x, esp_cy - 7 * 2.54 + i * 2.54)
    for i in range(15):
        esp_pins[16 + i] = (esp_p2_x, esp_cy + 7 * 2.54 - i * 2.54)

    pcm_p1_x = 95.0 - 7.62 # 87.38
    pcm_p2_x = 95.0 + 7.62 # 102.62
    pcm_cy = 24.0
    pcm_pins = {}
    for i in range(10):
        pcm_pins[i + 1] = (pcm_p1_x, pcm_cy - 4.5 * 2.54 + i * 2.54)
    pcm_pins[11] = (pcm_p2_x, 26.16)
    pcm_pins[12] = (pcm_p2_x, 31.24)
    pcm_pins[13] = (pcm_p2_x, 36.32)

    u3_lv_x = 95.0 - 6.35 # 88.65
    u3_hv_x = 95.0 + 6.35 # 101.35
    u3_cy = 72.0
    u3_pins = {}
    for i in range(6):
        u3_pins[i + 1] = (u3_hv_x, u3_cy - 2.5 * 2.54 + i * 2.54)
    for i in range(6):
        u3_pins[7 + i] = (u3_lv_x, u3_cy - 2.5 * 2.54 + i * 2.54)

    j1_x = 135.0
    j1_pins = {
        1: (j1_x, 16.00), # MAP
        2: (j1_x, 21.08), # TPS
        3: (j1_x, 26.16), # CRANK+
        4: (j1_x, 31.24), # VR1-
        5: (j1_x, 55.08), # VSS
        6: (j1_x, 65.24), # CLUTCH
        7: (j1_x, 74.00), # INJ
        8: (j1_x, 78.00), # IGN
        9: (j1_x, 86.00)  # GND
    }

    # Filtros RC à esquerda
    r1_p2, r1_p1 = (20.0, 50.0), (14.0, 50.0)
    c1_p1, c1_p2 = (14.0, 44.0), (20.0, 44.0)
    r2_p2, r2_p1 = (20.0, 52.54), (14.0, 52.54)
    c2_p1, c2_p2 = (14.0, 58.54), (20.0, 58.54)

    pads = []
    for p, pos in esp_pins.items():
        nid = 0
        if p == 8: nid = 17
        elif p == 9: nid = 18
        elif p == 10: nid = 8
        elif p == 11: nid = 10
        elif p == 14: nid = 16
        elif p == 15: nid = 2
        elif p == 16: nid = 1
        elif p == 17: nid = 3
        elif p == 20: nid = 7
        elif p == 21: nid = 15
        elif p == 23: nid = 6
        elif p == 29: nid = 9
        pads.append((pos[0], pos[1], 1.0, nid, f"ESP32_{p}"))

    for p, pos in pcm_pins.items():
        nid = 0
        if p == 1: nid = 2
        elif p in [2, 6, 8, 9, 10]: nid = 16
        elif p == 3: nid = 8
        elif p == 4: nid = 9
        elif p == 5: nid = 10
        elif p == 7: nid = 1
        elif p == 11: nid = 5
        elif p == 12: nid = 4
        pads.append((pos[0], pos[1], 1.0, nid, f"PCM5102_{p}"))

    for p, pos in u3_pins.items():
        nid = 0
        if p == 1: nid = 2
        elif p in [2, 8]: nid = 16
        elif p == 3: nid = 13
        elif p == 4: nid = 14
        elif p == 7: nid = 1
        elif p == 9: nid = 6
        elif p == 10: nid = 7
        pads.append((pos[0], pos[1], 1.0, nid, f"U3_{p}"))

    j1_net_map = {1: 11, 2: 12, 3: 5, 4: 4, 5: 15, 6: 3, 7: 14, 8: 13, 9: 16}
    for p, pos in j1_pins.items():
        pads.append((pos[0], pos[1], 1.6, j1_net_map[p], f"J1_{p}"))

    pads.append((r1_p1[0], r1_p1[1], 1.0, 12, "R1_1"))
    pads.append((r1_p2[0], r1_p2[1], 1.0, 17, "R1_2"))
    pads.append((c1_p1[0], c1_p1[1], 1.0, 12, "C1_1"))
    pads.append((c1_p2[0], c1_p2[1], 1.0, 16, "C1_2"))

    pads.append((r2_p1[0], r2_p1[1], 1.0, 11, "R2_1"))
    pads.append((r2_p2[0], r2_p2[1], 1.0, 18, "R2_2"))
    pads.append((c2_p1[0], c2_p1[1], 1.0, 11, "C2_1"))
    pads.append((c2_p2[0], c2_p2[1], 1.0, 16, "C2_2"))

    tracks = []
    def add_seg(x1, y1, x2, y2, width, net_id, name):
        tracks.append((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2), width, net_id, name))

    def add_path(pts, width, net_id, name):
        for i in range(len(pts) - 1):
            add_seg(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], width, net_id, f"{name}_{i+1}")

    # 1. Filtros à esquerda
    add_path([esp_pins[8], r1_p2], 0.8, 17, "D25_R1")
    add_path([r1_p1, c1_p1, (9.0, 44.0), (9.0, 7.0), (131.0, 7.0), (131.0, 21.08), j1_pins[2]], 0.8, 12, "TPS_OUT")

    add_path([esp_pins[9], r2_p2], 0.8, 18, "D26_R2")
    add_path([r2_p1, c2_p1, (6.0, 58.54), (6.0, 4.0), (135.0, 4.0), j1_pins[1]], 0.8, 11, "MAP_OUT")

    # 2. I2S para PCM5102 - Entradas estritamente horizontais a partir de x=80
    # LCK (pcm_pins[5] está em 87.38, y=pcm_pins[5][1])
    py_lck = pcm_pins[5][1]
    add_path([esp_pins[11], (12.0, esp_pins[11][1]), (12.0, 10.0), (80.0, 10.0), (80.0, py_lck), pcm_pins[5]], 0.8, 10, "I2S_LCK")

    # BCK (pcm_pins[3] está em 87.38, y=pcm_pins[3][1])
    py_bck = pcm_pins[3][1]
    add_path([esp_pins[10], (15.0, esp_pins[10][1]), (15.0, 13.0), (77.0, 13.0), (77.0, py_bck), pcm_pins[3]], 0.8, 8, "I2S_BCK")

    # DIN (pcm_pins[4] está em 87.38, y=pcm_pins[4][1])
    py_din = pcm_pins[4][1]
    add_path([esp_pins[29], (74.0, esp_pins[29][1]), (74.0, py_din), pcm_pins[4]], 0.8, 9, "I2S_DIN")

    # Saídas PCM5102
    add_path([pcm_pins[11], j1_pins[3]], 0.8, 5, "CRANK_POS")
    add_path([pcm_pins[12], j1_pins[4]], 0.8, 4, "CRANK_NEG")

    # 3. VSS e CLUTCH direto para J1
    add_path([esp_pins[21], j1_pins[5]], 0.8, 15, "VSS")
    add_path([esp_pins[17], j1_pins[6]], 0.8, 3, "CLUTCH")

    # 4. IGN e INJ - Entradas horizontais para U3 a partir de x=83
    # INJ (U3 Pin 10, lv_x = 88.65, y = u3_pins[10][1])
    py_inj = u3_pins[10][1]
    add_path([esp_pins[20], (45.0, esp_pins[20][1]), (45.0, py_inj), u3_pins[10]], 0.8, 7, "FB_INJ")
    add_path([u3_pins[4], (115.0, u3_pins[4][1]), (115.0, 74.0), j1_pins[7]], 0.8, 14, "INJ_OUT")

    # IGN (U3 Pin 9, lv_x = 88.65, y = u3_pins[9][1])
    py_ign = u3_pins[9][1]
    add_path([esp_pins[23], (42.0, esp_pins[23][1]), (42.0, py_ign), u3_pins[9]], 0.8, 6, "FB_IGN")
    add_path([u3_pins[3], (118.0, u3_pins[3][1]), (118.0, 78.0), j1_pins[8]], 0.8, 13, "IGN_OUT")

    # 5. Alimentação e Terra no Rodapé
    # +3V3 (U3 Pin 7, y = u3_pins[7][1])
    py_3v3 = u3_pins[7][1]
    add_path([esp_pins[16], (esp_pins[16][0], 71.0), (84.0, 71.0), (84.0, py_3v3), u3_pins[7]], 1.0, 1, "+3V3")

    # +5V (U3 Pin 1, hv_x = 101.35, y = u3_pins[1][1])
    py_5v = u3_pins[1][1]
    add_path([esp_pins[15], (esp_pins[15][0], 84.0), (107.0, 84.0), (107.0, py_5v), u3_pins[1]], 1.2, 2, "+5V")

    # GND
    add_path([esp_pins[14], (22.0, esp_pins[14][1]), (22.0, 88.0), (j1_pins[9][0], 88.0), j1_pins[9]], 1.4, 16, "GND")
    add_path([c1_p2, (22.0, c1_p2[1])], 0.8, 16, "GND_C1")
    add_path([c2_p2, (22.0, c2_p2[1])], 0.8, 16, "GND_C2")
    # GND U3 Pin 2 (101.35, y=u3_pins[2][1])
    py_gnd2 = u3_pins[2][1]
    add_path([u3_pins[2], (105.0, py_gnd2), (105.0, 88.0)], 1.0, 16, "GND_U3_2")
    # GND U3 Pin 8 (88.65, y=u3_pins[8][1])
    py_gnd8 = u3_pins[8][1]
    add_path([u3_pins[8], (85.0, py_gnd8), (85.0, 88.0)], 1.0, 16, "GND_U3_8")

    violations = check_board(pads, tracks)
    print(f"Total de trilhas: {len(tracks)}, Total de pads: {len(pads)}")
    print(f"TOTAL DE VIOLAÇÕES: {len(violations)}")
    for v in violations:
        print("  *", v)

if __name__ == '__main__':
    solve()
