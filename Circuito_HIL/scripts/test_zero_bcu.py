"""Teste do roteamento 100% planar sem cruzamentos em B.Cu.
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
def add_b(pts, net):
    for i in range(len(pts) - 1):
        b_cu_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net))

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

# 1. B.Cu Saídas para Borne J1
add_b([pcm_pins[11], j1_pins[1]], "CRANK_POS")
add_b([pcm_pins[12], j1_pins[2]], "CRANK_NEG")
add_b([r1_p1, c1_p1], "TPS_FILTER")
add_b([c1_p1, j1_pins[3]], "TPS_OUT")
add_b([r2_p1, c2_p1], "MAP_FILTER")
add_b([c2_p1, j1_pins[4]], "MAP_OUT")

# VSS e CLUTCH: saem para a direita em Y=48 e Y=56
add_b([esp_pins[21], (60.0, esp_pins[21][1]), (60.0, j1_pins[5][1]), j1_pins[5]], "VSS")
add_b([esp_pins[17], (63.0, esp_pins[17][1]), (63.0, j1_pins[6][1]), j1_pins[6]], "CLUTCH")

# IGN e INJ HV para Borne J1
add_b([u3_pins[3], j1_pins[7]], "IGN_OUT")
add_b([u3_pins[4], j1_pins[8]], "INJ_OUT")

# 2. ESP32 -> U3 (Nested L-shapes na direita de ESP32)
# Pin 23 (IGN): sai para X=66, desce até Y=73.73, entra em U3.9 (85.65, 73.73)
add_b([esp_pins[23], (66.0, esp_pins[23][1]), (66.0, u3_pins[9][1]), u3_pins[9]], "IGN_FB")
# Pin 20 (INJ): sai para X=69, desce até Y=76.27, entra em U3.10 (85.65, 76.27)
add_b([esp_pins[20], (69.0, esp_pins[20][1]), (69.0, u3_pins[10][1]), u3_pins[10]], "INJ_FB")
# 3V3 (ESP32 p16, 56.43, 69.78) -> U3 p7 (85.65, 68.65)
add_b([esp_pins[16], (72.0, esp_pins[16][1]), (72.0, u3_pins[7][1]), u3_pins[7]], "+3V3_U3")

# 3. Barramento GND (Y=86) e 5V (Y=90)
# GND ESP32 p14 desce em X=24 para Y=86, vai direto para J1.9
add_b([esp_pins[14], (24.0, esp_pins[14][1]), (24.0, 86.0), (j1_pins[9][0], 86.0), j1_pins[9]], "GND_RODAPE")
# U3 GND: interliga pino 8 e 2 pelo centro, desce pelo centro de U3 (X=92) até Y=86!
add_b([u3_pins[2], u3_pins[8]], "GND_U3_BRIDGE")
add_b([(92.0, 71.19), (92.0, 86.0)], "GND_U3_DROP")

# GND Esquerda: sobe em X=14 de Y=86 até Y=6, vai para X=80
add_b([(24.0, 86.0), (14.0, 86.0), (14.0, 6.0), (80.0, 6.0)], "GND_ESQ")
add_b([(80.0, 6.0), (80.0, 27.5)], "GND_PCM_BUS")
add_b([(80.0, pcm_pins[2][1]), pcm_pins[2]], "GND_P2")
add_b([(80.0, pcm_pins[6][1]), pcm_pins[6]], "GND_P6")
add_b([(80.0, pcm_pins[8][1]), pcm_pins[8]], "GND_P8")
add_b([(80.0, pcm_pins[9][1]), pcm_pins[9]], "GND_P9")
add_b([(80.0, pcm_pins[10][1]), pcm_pins[10]], "GND_P10")

# GND C1 e C2:
add_b([c1_p2, (80.0, c1_p2[1])], "GND_C1")
add_b([c2_p2, (80.0, c2_p2[1])], "GND_C2")

# 4. +5V (Y=90 na borda inferior, X=10 na borda esquerda)
add_b([esp_pins[15], (26.0, esp_pins[15][1]), (26.0, 90.0), (10.0, 90.0), (10.0, 4.57), (pcm_pins[1][0], 4.57)], "+5V_PCM")

# Testar se há QUALQUER interseção em B.Cu!
crossings = []
for i in range(len(b_cu_tracks)):
    for j in range(i + 1, len(b_cu_tracks)):
        t1, t2 = b_cu_tracks[i], b_cu_tracks[j]
        if t1[4] != t2[4]:
            if seg_intersects(t1[0], t1[1], t1[2], t1[3], t2[0], t2[1], t2[2], t2[3]):
                crossings.append((t1[4], t2[4], t1, t2))

print(f"Total de segmentos B.Cu testados: {len(b_cu_tracks)}")
print(f"TOTAL DE CRUZAMENTOS EM B.Cu: {len(crossings)}")
for c in crossings:
    print("Cruzamento:", c[0], "com", c[1])
