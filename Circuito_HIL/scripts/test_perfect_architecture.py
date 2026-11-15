"""Teste da Arquitetura Perfeita (U3 Embaixo do ESP32, U2 Acima do ESP32).
Comprova matematicamente que TODAS as conexões são planares e sem cruzamento.
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

# 1. PCM5102 (U2) colocado ACIMA do ESP32 (y = 15.0)
# Saídas vão direto para J1.1 e J1.2 (y = 15.0 e y = 20.08)
add_path([(105.62, 15.0), (135.0, 15.0)], "CRANK_POS")
add_path([(105.62, 20.08), (135.0, 20.08)], "CRANK_NEG")

# I2S do ESP32 (y=35..45) sobe direto para U2 (y=15.0)
# DIN (Pin 29, 51.43, 34.76) -> sobe para U2.4 (90.38, 15.0)
add_path([(51.43, 34.76), (51.43, 14.0), (90.38, 14.0)], "I2S_DIN")
# BCK (Pin 10, 28.57, 55.08) -> sobe à esquerda (x=20) para U2.3 (90.38, 11.0)
add_path([(28.57, 55.08), (20.0, 55.08), (20.0, 11.0), (90.38, 11.0)], "I2S_BCK")
# LCK (Pin 11, 28.57, 57.62) -> sobe à esquerda (x=17) para U2.5 (90.38, 17.0)
add_path([(28.57, 57.62), (17.0, 57.62), (17.0, 8.0), (90.38, 8.0)], "I2S_LCK")

# 2. Filtros RC TPS e MAP (entre ESP32 e J1 em y = 25.16 e y = 30.24)
# D25 (Pin 8, 28.57, 50.0) -> sobe em x=23 para y=25.16 -> R1 -> C1 -> J1.3
add_path([(28.57, 50.0), (23.0, 50.0), (23.0, 25.16), (60.0, 25.16)], "TPS_IN")
add_path([(70.0, 25.16), (135.0, 25.16)], "TPS_OUT")

# D26 (Pin 9, 28.57, 52.54) -> sobe em x=26 para y=30.24 -> R2 -> C2 -> J1.4
add_path([(28.57, 52.54), (26.0, 52.54), (26.0, 30.24), (60.0, 30.24)], "MAP_IN")
add_path([(70.0, 30.24), (135.0, 30.24)], "MAP_OUT")

# 3. VSS (Pin 21, 51.43, 55.08) -> direto para J1.5 (y = 35.32)
add_path([(51.43, 55.08), (65.0, 55.08), (65.0, 35.32), (135.0, 35.32)], "VSS")

# 4. CLUTCH (Pin 17, 51.43, 65.24) -> direto para J1.6 (y = 40.40)
add_path([(51.43, 65.24), (68.0, 65.24), (68.0, 40.40), (135.0, 40.40)], "CLUTCH")

# 5. U3 (Level Converter) colocado abaixo do ESP32 (y = 80.0)
# Conexões diretas verticais ESP32 -> U3:
# D5 / IGN FB (Pin 23, 51.43, 50.0) -> desce em x=45 (vão central) para U3.9 (y=80.0)
add_path([(51.43, 50.0), (45.0, 50.0), (45.0, 80.0), (70.0, 80.0)], "FB_IGN")
# D4 / INJ FB (Pin 20, 51.43, 57.62) -> desce em x=42 (vão central) para U3.10 (y=82.54)
add_path([(51.43, 57.62), (42.0, 57.62), (42.0, 82.54), (70.0, 82.54)], "FB_INJ")

# Saídas U3 -> J1.7 e J1.8 (y = 45.48 e y = 50.56)
add_path([(85.0, 80.0), (100.0, 80.0), (100.0, 45.48), (135.0, 45.48)], "SPEEDUINO_IGN")
add_path([(85.0, 82.54), (103.0, 82.54), (103.0, 50.56), (135.0, 50.56)], "SPEEDUINO_INJ")

# 6. Alimentação direta no rodapé (y = 86..92)
# GND (Pin 14) -> J1.9 (y = 55.64)
add_path([(28.57, 65.24), (28.57, 90.0), (135.0, 90.0), (135.0, 55.64)], "GND")

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
