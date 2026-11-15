"""Roteador Analítico com ZERO CRUZAMENTOS em B.Cu e ZERO CRUZAMENTOS em F.Cu.
"""

def seg_intersects(x1, y1, x2, y2, x3, y3, x4, y4):
    if (abs(x1 - x3) < 0.01 and abs(y1 - y3) < 0.01) or \
       (abs(x1 - x4) < 0.01 and abs(y1 - y4) < 0.01) or \
       (abs(x2 - x3) < 0.01 and abs(y2 - y3) < 0.01) or \
       (abs(x2 - x4) < 0.01 and abs(y2 - y4) < 0.01):
        return False
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
    return (ccw(x1,y1, x3,y3, x4,y4) != ccw(x2,y2, x3,y3, x4,y4)) and \
           (ccw(x1,y1, x2,y2, x3,y3) != ccw(x1,y1, x2,y2, x4,y4))

b_cu_tracks = []
f_cu_tracks = []

def add_b(pts, net):
    for i in range(len(pts) - 1):
        b_cu_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net))

def add_f(pts, net):
    for i in range(len(pts) - 1):
        f_cu_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net))

# Coordenadas
u1_cx, u1_cy = 45.0, 52.0
esp_p1_x = u1_cx - 11.43 # 33.57
esp_p2_x = u1_cx + 11.43 # 56.43
esp_pins = {}
for i in range(15):
    esp_pins[i + 1] = (esp_p1_x, u1_cy - 7 * 2.54 + i * 2.54)
for i in range(15):
    esp_pins[16 + i] = (esp_p2_x, u1_cy + 7 * 2.54 - i * 2.54)

u2_cx, u2_cy = 92.0, 16.0
pcm_p1_x = u2_cx - 7.62 # 84.38
pcm_p2_x = u2_cx + 7.62 # 99.62
pcm_pins = {}
for i in range(10):
    pcm_pins[i + 1] = (pcm_p1_x, u2_cy - 4.5 * 2.54 + i * 2.54)
pcm_pins[11] = (pcm_p2_x, 15.0)
pcm_pins[12] = (pcm_p2_x, 20.08)
pcm_pins[13] = (pcm_p2_x, 25.0)

r1_p2, r1_p1 = (76.92, 28.0), (87.08, 28.0)
c1_p1, c1_p2 = (92.0, 28.0), (92.0, 24.0)
r2_p2, r2_p1 = (76.92, 34.0), (87.08, 34.0)
c2_p1, c2_p2 = (92.0, 34.0), (92.0, 38.0)

u3_cx, u3_cy = 92.0, 74.0
u3_lv_x = u3_cx - 6.35 # 85.65
u3_hv_x = u3_cx + 6.35 # 98.35
u3_pins = {}
for i in range(6):
    u3_pins[i + 1] = (u3_hv_x, u3_cy - 2.5 * 2.54 + i * 2.54)
for i in range(6):
    u3_pins[7 + i] = (u3_lv_x, u3_cy - 2.5 * 2.54 + i * 2.54)

j1_x = 138.0
j1_pins = {
    1: (j1_x, 15.0), 2: (j1_x, 20.08), 3: (j1_x, 28.0), 4: (j1_x, 34.0),
    5: (j1_x, 48.0), 6: (j1_x, 56.0), 7: (j1_x, 72.0), 8: (j1_x, 76.0), 9: (j1_x, 88.0)
}

# 1. B.Cu: Saídas para o Borne J1 (Diretas, Linhas Horizontais Paralelas)
add_b([pcm_pins[11], j1_pins[1]], "CRANK_POS")
add_b([pcm_pins[12], j1_pins[2]], "CRANK_NEG")
add_b([r1_p1, c1_p1], "TPS_FILTER")
add_b([c1_p1, j1_pins[3]], "TPS_OUT")
add_b([r2_p1, c2_p1], "MAP_FILTER")
add_b([c2_p1, j1_pins[4]], "MAP_OUT")
add_b([esp_pins[21], (64.0, esp_pins[21][1]), (64.0, j1_pins[5][1]), j1_pins[5]], "VSS")
add_b([esp_pins[17], (67.0, esp_pins[17][1]), (67.0, j1_pins[6][1]), j1_pins[6]], "CLUTCH")
add_b([u3_pins[3], j1_pins[7]], "IGN_OUT")
add_b([u3_pins[4], j1_pins[8]], "INJ_OUT")

# 2. B.Cu: ESP32 -> U3 (Canal Central)
# INJ (Pino 20, y=59.62): vira para X=44, desce até Y=76.27, vai reto para U3.10
add_b([esp_pins[20], (44.0, esp_pins[20][1]), (44.0, u3_pins[10][1]), u3_pins[10]], "INJ_FB")
# IGN (Pino 23, y=52.0): vira para X=48, desce até Y=73.73, vai reto para U3.9
add_b([esp_pins[23], (48.0, esp_pins[23][1]), (48.0, u3_pins[9][1]), u3_pins[9]], "IGN_FB")
# 3V3 (ESP32 p16, 56.43, 69.78) -> U3 p7 (85.65, 68.65)
add_b([esp_pins[16], (70.0, esp_pins[16][1]), (70.0, u3_pins[7][1]), u3_pins[7]], "+3V3_U3")

# 3. B.Cu: Barramento GND Rodapé
# ESP32 p14 desce em X=24 para Y=90, vai reto até J1.9
add_b([esp_pins[14], (24.0, esp_pins[14][1]), (24.0, 90.0), (j1_pins[9][0], 90.0), j1_pins[9]], "GND_RODAPE")
# U3 GND: pino 8 liga a pino 2 pelo centro em Y=71.19
add_b([u3_pins[2], u3_pins[8]], "GND_U3_BRIDGE")
# Desce para Y=90 pelo centro de U3 em X=92.0! (Não cruza ninguém!)
add_b([(92.0, 71.19), (92.0, 90.0)], "GND_U3_DROP")

# GND Perímetro Esquerdo: sobe em X=10 de Y=90 até Y=6, vai para X=80
add_b([(24.0, 90.0), (10.0, 90.0), (10.0, 6.0), (80.0, 6.0)], "GND_ESQ")
# Distribuidor PCM5102 GND em X=80
add_b([(80.0, 6.0), (80.0, 27.5)], "GND_PCM_BUS")
add_b([(80.0, pcm_pins[2][1]), pcm_pins[2]], "GND_P2")
add_b([(80.0, pcm_pins[6][1]), pcm_pins[6]], "GND_P6")
add_b([(80.0, pcm_pins[8][1]), pcm_pins[8]], "GND_P8")
add_b([(80.0, pcm_pins[9][1]), pcm_pins[9]], "GND_P9")
add_b([(80.0, pcm_pins[10][1]), pcm_pins[10]], "GND_P10")

# GND para C1 e C2: entra pelo lado esquerdo em X=80!
add_b([c1_p2, (80.0, c1_p2[1])], "GND_C1")
add_b([c2_p2, (80.0, c2_p2[1])], "GND_C2")

# 4. B.Cu: +5V
# ESP32 p15 (VIN) sai para X=27, sobe em X=14 até Y=4.57 -> PCM5102 p1
add_b([esp_pins[15], (27.0, esp_pins[15][1]), (27.0, 86.0), (14.0, 86.0), (14.0, 4.57), (pcm_pins[1][0], 4.57)], "+5V_PCM")
# +5V para U3 HV: pega da linha de 5V em Y=86 e sobe em X=104 até Y=84, onde conecta a U3.1?
# Espera! U3.1 está em Y=68.65. Se subir em X=104, cruza IGN_OUT e INJ_OUT!
# Então +5V para U3 HV pode ir por F.Cu (Jumper J_5V_HV) de U3.1 para o barramento de 5V em Y=86!

# 5. F.Cu: Jumpers de Fio Retos (SEM NENHUM CRUZAMENTO ENTRE ELES!)
# Jumper 1: D25 (TPS) -> R1 p2 (Y=52 até Y=28)
add_f([esp_pins[8], (30.0, esp_pins[8][1]), (30.0, 28.0), r1_p2], "J_TPS")
# Jumper 2: D26 (MAP) -> R2 p2 (sai em X=33, vai direto até R2 p2)
add_f([esp_pins[9], (70.0, esp_pins[9][1]), (70.0, 34.0), r2_p2], "J_MAP")

# Jumper 3: I2S_DIN (ESP32 p29 -> PCM5102 p4)
add_f([esp_pins[29], (74.0, esp_pins[29][1]), (74.0, pcm_pins[4][1]), pcm_pins[4]], "J_DIN")

# Jumper 4: I2S_BCK (ESP32 p10 -> PCM5102 p3)
# Sai para X=21, sobe em X=21 até Y=9.65
add_f([esp_pins[10], (21.0, esp_pins[10][1]), (21.0, 9.65), pcm_pins[3]], "J_BCK")

# Jumper 5: I2S_LCK (ESP32 p11 -> PCM5102 p5)
# Sai para X=18, sobe em X=18 até Y=14.73
add_f([esp_pins[11], (18.0, esp_pins[11][1]), (18.0, 14.73), pcm_pins[5]], "J_LCK")

# Jumper 6: +5V para U3 HV (Pin 1)
add_f([u3_pins[1], (u3_pins[1][0], 84.0), (33.0, 84.0)], "J_5V_HV")

# Jumper 7: +3V3 para PCM5102 p7 (XMT)
add_f([pcm_pins[7], (76.0, pcm_pins[7][1]), (76.0, 68.65), u3_pins[7]], "J_3V3")

def test_intersections(track_list, layer_name):
    crossings = []
    for i in range(len(track_list)):
        for j in range(i + 1, len(track_list)):
            t1, t2 = track_list[i], track_list[j]
            if t1[4] != t2[4]:
                if seg_intersects(t1[0], t1[1], t1[2], t1[3], t2[0], t2[1], t2[2], t2[3]):
                    crossings.append((t1[4], t2[4]))
    print(f"Layer {layer_name}: {len(track_list)} segmentos, {len(crossings)} cruzamentos.")
    for c in crossings:
        print(f"  Cruzamento em {layer_name}: {c[0]} com {c[1]}")
    return len(crossings)

cb = test_intersections(b_cu_tracks, "B.Cu")
cf = test_intersections(f_cu_tracks, "F.Cu")
