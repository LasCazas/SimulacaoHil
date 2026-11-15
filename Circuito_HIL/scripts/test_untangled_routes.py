"""Teste dos Pinos Saindo em Direções Opostas (Zero Cruzamentos).
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

segments = []
def add_path(pts, net_name):
    for i in range(len(pts) - 1):
        segments.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net_name))

# 1. Filtros à esquerda do ESP32
add_path([(28.57, 52.54), (18.0, 52.54)], "D26_R2")
add_path([(12.0, 52.54), (6.0, 52.54), (6.0, 4.0), (135.0, 4.0), (135.0, 16.0)], "MAP_OUT")

add_path([(28.57, 50.00), (18.0, 50.00)], "D25_R1")
add_path([(12.0, 50.00), (9.0, 50.00), (9.0, 7.0), (132.0, 7.0), (132.0, 21.08)], "TPS_OUT")

# 2. I2S para PCM5102
add_path([(28.57, 57.62), (12.0, 57.62), (12.0, 10.0), (87.38, 10.0)], "I2S_LCK")
add_path([(28.57, 55.08), (15.0, 55.08), (15.0, 13.0), (87.38, 13.0)], "I2S_BCK")
add_path([(51.43, 34.76), (75.0, 34.76), (75.0, 16.0), (87.38, 16.0)], "I2S_DIN")

add_path([(102.62, 26.16), (135.0, 26.16)], "CRANK_POS")
add_path([(102.62, 31.24), (135.0, 31.24)], "CRANK_NEG")

# 3. VSS e CLUTCH: saem para a DIREITA direto para J1
add_path([(51.43, 55.08), (135.0, 55.08)], "VSS")
add_path([(51.43, 65.24), (135.0, 65.24)], "CLUTCH")

# 4. IGN e INJ: saem para a ESQUERDA no vão central do ESP32!
# INJ (Pin 20, y=57.62): vira no vão central em x=45, desce até y=74.0, vai para U3.10
add_path([(51.43, 57.62), (45.0, 57.62), (45.0, 74.0), (88.65, 74.0)], "FB_INJ")

# IGN (Pin 23, y=50.0): vira no vão central em x=42, desce até y=77.54, vai para U3.9
add_path([(51.43, 50.0), (42.0, 50.0), (42.0, 77.54), (88.65, 77.54)], "FB_IGN")

# Saídas U3 para J1
add_path([(101.35, 74.0), (135.0, 74.0)], "SPEEDUINO_INJ")
add_path([(101.35, 77.54), (135.0, 77.54)], "SPEEDUINO_IGN")

# 5. Alimentação no Rodapé
# +3V3 (y = 71.0): Pin 16 desce em x=51.43 apenas de 67.78 para 71.0, vira à direita para U3 LV (88.65, 71.0)
add_path([(51.43, 67.78), (51.43, 71.0), (88.65, 71.0)], "+3V3")

# +5V (y = 82.5): Pin 15 desce em x=28.57 para y=82.5, vai para U3 HV (101.35, 82.5)
add_path([(28.57, 67.78), (28.57, 82.5), (101.35, 82.5)], "+5V")

# GND (y = 86.0): Pin 14 desce em x=24 para y=86, atende U3 e J1.9
add_path([(28.57, 65.24), (24.0, 65.24), (24.0, 86.0), (135.0, 86.0), (135.0, 80.0)], "GND")
add_path([(88.65, 86.0), (88.65, 82.54)], "GND_U3_LV")
add_path([(101.35, 86.0), (101.35, 82.54)], "GND_U3_HV")

intersections = []
for i in range(len(segments)):
    for j in range(i + 1, len(segments)):
        s1 = segments[i]
        s2 = segments[j]
        if s1[4] != s2[4]:
            if seg_intersects(s1[0], s1[1], s1[2], s1[3], s2[0], s2[1], s2[2], s2[3]):
                intersections.append((s1[4], s2[4], s1, s2))

print(f"Total de segmentos testados: {len(segments)}")
print(f"TOTAL DE INTERSEÇÕES: {len(intersections)}")
