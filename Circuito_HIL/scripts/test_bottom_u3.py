"""Teste Matemático da Configuração U3 no Rodapé.
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

# 1. Filtros à esquerda do ESP32 (saídas pelo topo)
add_path([(28.57, 52.54), (18.0, 52.54)], "D26_R2")
add_path([(12.0, 52.54), (6.0, 52.54), (6.0, 4.0), (135.0, 4.0), (135.0, 16.0)], "MAP_OUT")

add_path([(28.57, 50.00), (18.0, 50.00)], "D25_R1")
add_path([(12.0, 50.00), (9.0, 50.00), (9.0, 7.0), (132.0, 7.0), (132.0, 21.08)], "TPS_OUT")

# 2. PCM5102 (x=95, y=26)
add_path([(28.57, 57.62), (12.0, 57.62), (12.0, 10.0), (87.38, 10.0)], "I2S_LCK")
add_path([(28.57, 55.08), (15.0, 55.08), (15.0, 13.0), (87.38, 13.0)], "I2S_BCK")
add_path([(51.43, 34.76), (75.0, 34.76), (75.0, 16.0), (87.38, 16.0)], "I2S_DIN")

add_path([(102.62, 26.16), (135.0, 26.16)], "CRANK_POS")
add_path([(102.62, 31.24), (135.0, 31.24)], "CRANK_NEG")

# 3. VSS e CLUTCH (direto no centro, acima de U3)
add_path([(51.43, 55.08), (135.0, 55.08)], "VSS")
add_path([(51.43, 65.24), (135.0, 65.24)], "CLUTCH")

# 4. U3 no rodapé (x=95, y=78)
# Sinais entram pela esquerda de U3 descendo do ESP32
add_path([(51.43, 50.0), (70.0, 50.0), (70.0, 75.0), (88.65, 75.0)], "FB_IGN")
add_path([(51.43, 57.62), (73.0, 57.62), (73.0, 77.54), (88.65, 77.54)], "FB_INJ")

# Saídas de U3 para J1
add_path([(101.35, 75.0), (135.0, 75.0)], "SPEEDUINO_IGN")
add_path([(101.35, 77.54), (135.0, 77.54)], "SPEEDUINO_INJ")

# 5. Alimentação no Rodapé
# +3V3 (y = 80.0)
add_path([(51.43, 67.78), (51.43, 80.0), (88.65, 80.0)], "+3V3")

# +5V (y = 82.5)
add_path([(28.57, 67.78), (28.57, 82.5), (101.35, 82.5)], "+5V")

# GND (y = 86.0) -> atende U3 e J1.9
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
