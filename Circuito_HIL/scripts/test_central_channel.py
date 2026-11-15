"""Teste do roteamento 100% planar através do canal central do ESP32.
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

routes = []
def add_path(pts, net_name):
    for i in range(len(pts) - 1):
        routes.append((pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], net_name))

# 1. PCM5102 saídas analógicas para J1 (Crank VR)
add_path([(92.62, 15.0), (135.0, 15.0)], "CRANK_POS")
add_path([(92.62, 20.08), (135.0, 20.08)], "CRANK_NEG")

# 2. I2S DIN (Pin 29, 51.43, 34.76): sobe por X=70 até PCM5102 Pin 4 (77.38, 14.19)
add_path([(51.43, 34.76), (70.0, 34.76), (70.0, 14.19), (77.38, 14.19)], "I2S_DIN")

# 3. I2S BCK (Pin 10, 28.57, 55.08) e I2S LCK (Pin 11, 28.57, 57.62)
# Entram no canal central e sobem em X=32 e X=35
add_path([(28.57, 55.08), (32.0, 55.08), (32.0, 11.65), (77.38, 11.65)], "I2S_BCK")
add_path([(28.57, 57.62), (35.0, 57.62), (35.0, 8.0), (74.0, 8.0), (74.0, 16.73), (77.38, 16.73)], "I2S_LCK")

# 4. DAC1 TPS (Pin 8, 28.57, 50.0) e DAC2 MAP (Pin 9, 28.57, 52.54)
# Entram no canal central em X=26 e X=29, sobem até R1 e R2 em Y=24 e Y=28
add_path([(28.57, 50.0), (26.0, 50.0), (26.0, 24.0), (80.0, 24.0)], "D25_R1")
add_path([(80.0, 24.0), (135.0, 24.0)], "TPS_OUT")

add_path([(28.57, 52.54), (29.0, 52.54), (29.0, 28.0), (80.0, 28.0)], "D26_R2")
add_path([(80.0, 28.0), (135.0, 28.0)], "MAP_OUT")

# 5. Sinais Diretos ESP32 -> J1 (VSS e CLUTCH)
add_path([(51.43, 55.08), (135.0, 55.08)], "VSS_PULSE")
add_path([(51.43, 65.24), (135.0, 65.24)], "CLUTCH_SIG")

# 6. ESP32 -> U3 (IGN e INJ)
# IGN: ESP32 p23 (51.43, 50.0) entra no canal central em X=45, desce até Y=72.73, vai para U3 p9 (78.65, 72.73)
add_path([(51.43, 50.0), (45.0, 50.0), (45.0, 72.73), (78.65, 72.73)], "FB_IGN_3V3")
# INJ: ESP32 p20 (51.43, 57.62) entra no canal central em X=40, desce até Y=75.27, vai para U3 p10 (78.65, 75.27)
add_path([(51.43, 57.62), (40.0, 57.62), (40.0, 75.27), (78.65, 75.27)], "FB_INJ_3V3")

# U3 HV -> J1
add_path([(91.35, 72.73), (135.0, 72.73)], "SPEEDUINO_IGN")
add_path([(91.35, 75.27), (135.0, 75.27)], "SPEEDUINO_INJ")

# Testar se há interseções!
intersections = []
for i in range(len(routes)):
    for j in range(i + 1, len(routes)):
        t1 = routes[i]
        t2 = routes[j]
        if t1[4] != t2[4]:
            if seg_intersects(t1[0], t1[1], t1[2], t1[3], t2[0], t2[1], t2[2], t2[3]):
                intersections.append((t1[4], t2[4], t1, t2))

print(f"Total de faixas testadas: {len(routes)}")
print(f"Interseções encontradas: {len(intersections)}")
for item in intersections:
    print("Conflito:", item[0], "com", item[1])
