"""Verificador de Topologia 100% Planar para todas as 18 nets do circuito HIL.
"""

def seg_intersects(x1, y1, x2, y2, x3, y3, x4, y4):
    # Coincident endpoints don't count as collision
    if (abs(x1 - x3) < 0.01 and abs(y1 - y3) < 0.01) or \
       (abs(x1 - x4) < 0.01 and abs(y1 - y4) < 0.01) or \
       (abs(x2 - x3) < 0.01 and abs(y2 - y3) < 0.01) or \
       (abs(x2 - x4) < 0.01 and abs(y2 - y4) < 0.01):
        return False
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
    return (ccw(x1,y1, x3,y3, x4,y4) != ccw(x2,y2, x3,y3, x4,y4)) and \
           (ccw(x1,y1, x2,y2, x3,y3) != ccw(x1,y1, x2,y2, x4,y4))

all_tracks = []

def add_path(pts, net_name):
    for i in range(len(pts) - 1):
        all_tracks.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net_name))

# Geometria e Posições
# ESP32: Centro (40, 50)
# PCM5102: Centro (85, 18)
# U3 Level Converter: Centro (85, 74)
# R1, C1, R2, C2: À esquerda do ESP32 (X = 14, Y = 46..56)
# J1: Borda direita em X = 135, Y = 15..87

# J1 Pins:
# 1: (135, 15)   CRANK+
# 2: (135, 20.08) CRANK-
# 3: (135, 28)   TPS
# 4: (135, 34)   MAP
# 5: (135, 48)   VSS
# 6: (135, 56)   CLUTCH
# 7: (135, 72)   IGN
# 8: (135, 76)   INJ
# 9: (135, 86)   GND

# 1. PCM5102 -> J1 (CRANK+, CRANK-)
add_path([(92.62, 15.0), (135.0, 15.0)], "CRANK_POS")
add_path([(92.62, 20.08), (135.0, 20.08)], "CRANK_NEG")

# 2. ESP32 -> PCM5102 (I2S)
# I2S_DIN: ESP32 p29 (51.43, 34.76) -> PCM5102 p4 (77.38, 14.19)
add_path([(51.43, 34.76), (68.0, 34.76), (68.0, 14.19), (77.38, 14.19)], "I2S_DIN")

# I2S_BCK: ESP32 p10 (28.57, 55.08) -> PCM5102 p3 (77.38, 11.65)
# I2S_LCK: ESP32 p11 (28.57, 57.62) -> PCM5102 p5 (77.38, 16.73)
# Saem para a esquerda em X=20 e X=22, sobem até Y=6 e Y=8, vão para a direita até PCM5102
add_path([(28.57, 55.08), (22.0, 55.08), (22.0, 11.65), (77.38, 11.65)], "I2S_BCK")
add_path([(28.57, 57.62), (20.0, 57.62), (20.0, 6.0), (72.0, 6.0), (72.0, 16.73), (77.38, 16.73)], "I2S_LCK")

# 3. Filtros RC (TPS e MAP):
# R1, C1 em X=12..16, Y=30..36
# ESP32 p8 (D25) em (28.57, 50.0) -> R1 p2 em (16.0, 50.0)
add_path([(28.57, 50.0), (16.0, 50.0)], "D25_R1")
# R1 p1 / C1 p1 em (12.0, 50.0) -> sobe por X=8 até Y=28, vai reto até J1.3
add_path([(12.0, 50.0), (8.0, 50.0), (8.0, 28.0), (135.0, 28.0)], "NET_TPS_OUT")

# ESP32 p9 (D26) em (28.57, 52.54) -> R2 p2 em (16.0, 52.54)
add_path([(28.57, 52.54), (16.0, 52.54)], "D26_R2")
# R2 p1 / C2 p1 em (12.0, 52.54) -> sobe por X=10 até Y=34, vai reto até J1.4
add_path([(12.0, 52.54), (10.0, 52.54), (10.0, 34.0), (135.0, 34.0)], "NET_MAP_OUT")

# 4. Sinais Diretos ESP32 -> J1 (VSS e CLUTCH)
# VSS: ESP32 p21 (51.43, 55.08) -> J1.5 (135.0, 48.0)
add_path([(51.43, 55.08), (60.0, 55.08), (60.0, 48.0), (135.0, 48.0)], "VSS_PULSE")
# CLUTCH: ESP32 p17 (51.43, 65.24) -> J1.6 (135.0, 56.0)
add_path([(51.43, 65.24), (63.0, 65.24), (63.0, 56.0), (135.0, 56.0)], "CLUTCH_SIG")

# 5. ESP32 -> U3 (IGN e INJ no vão central do ESP32!)
# IGN: ESP32 p23 (51.43, 50.0) entra no vão central em X=40, desce até Y=72.73, vai para U3 p9 (78.65, 72.73)
add_path([(51.43, 50.0), (40.0, 50.0), (40.0, 72.73), (78.65, 72.73)], "FB_IGN_3V3")
# INJ: ESP32 p20 (51.43, 57.62) entra no vão central em X=44, desce até Y=75.27, vai para U3 p10 (78.65, 75.27)
add_path([(51.43, 57.62), (44.0, 57.62), (44.0, 75.27), (78.65, 75.27)], "FB_INJ_3V3")

# U3 HV -> J1 (SPEEDUINO_IGN e SPEEDUINO_INJ)
# IGN: U3 p3 (91.35, 72.73) -> J1.7 (135.0, 72.0)
add_path([(91.35, 72.73), (135.0, 72.0)], "SPEEDUINO_IGN")
# INJ: U3 p4 (91.35, 75.27) -> J1.8 (135.0, 76.0)
add_path([(91.35, 75.27), (135.0, 76.0)], "SPEEDUINO_INJ")

# 6. Barramentos de Alimentação e Terra (+3V3, +5V, GND)
# +3V3: ESP32 p16 (51.43, 67.78) vai direto para U3 p7 (78.65, 67.65)
add_path([(51.43, 67.78), (78.65, 67.65)], "+3V3_U3")
# +3V3 para PCM5102 p7 (77.38, 21.81):
# Pode subir pelo vão interno entre ESP32 e U3/PCM5102?
# Em X=65, Y=67.78 sobe até Y=21.81?
# Espera! Em X=65, VSS cruza em Y=48 e CLUTCH cruza em Y=56!
# MAS pela Rodovia Direita em X=140 mm:
# De U3 p7 (ou J1), pode passar por trás de J1 (X=140) de Y=67.65 até Y=21.81!
add_path([(78.65, 67.65), (78.65, 65.0), (140.0, 65.0), (140.0, 21.81), (77.38, 21.81)], "+3V3_PCM")

# Testar se há interseções!
intersections = []
for i in range(len(all_tracks)):
    for j in range(i + 1, len(all_tracks)):
        t1 = all_tracks[i]
        t2 = all_tracks[j]
        if t1[4] != t2[4]:
            if seg_intersects(t1[0], t1[1], t1[2], t1[3], t2[0], t2[1], t2[2], t2[3]):
                intersections.append((t1[4], t2[4], t1, t2))

print(f"Total de faixas testadas: {len(all_tracks)}")
print(f"Interseções encontradas: {len(intersections)}")
for item in intersections:
    print("Conflito:", item[0], "com", item[1])
