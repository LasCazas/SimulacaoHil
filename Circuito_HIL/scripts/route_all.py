import math
import heapq
from test_perfect_grid_router import SafeGridRouter

router = SafeGridRouter(145.0, 100.0, res=0.35)

u1_cx, u1_cy = 40.0, 50.0
u2_cx, u2_cy = 100.0, 20.0
u3_cx, u3_cy = 100.0, 68.0
j1_x = 135.0

# ESP32
esp_p1_x = u1_cx - 11.43
esp_p2_x = u1_cx + 11.43
esp_pins = {}
for i in range(15):
    esp_pins[i + 1] = (esp_p1_x, u1_cy - 7 * 2.54 + i * 2.54)
for i in range(15):
    esp_pins[16 + i] = (esp_p2_x, u1_cy + 7 * 2.54 - i * 2.54)

# PCM5102
pcm_p1_x = u2_cx - 7.62
pcm_p2_x = u2_cx + 7.62
pcm_pins = {}
for i in range(10):
    pcm_pins[i + 1] = (pcm_p1_x, u2_cy - 4.5 * 2.54 + i * 2.54)
pcm_pins[11] = (pcm_p2_x, 15.0)
pcm_pins[12] = (pcm_p2_x, 20.08)
pcm_pins[13] = (pcm_p2_x, 25.16)

# U3
u3_lv_x = u3_cx - 6.35
u3_hv_x = u3_cx + 6.35
u3_pins = {}
for i in range(6):
    u3_pins[i + 1] = (u3_hv_x, u3_cy - 2.5 * 2.54 + i * 2.54)
for i in range(6):
    u3_pins[7 + i] = (u3_lv_x, u3_cy - 2.5 * 2.54 + i * 2.54)

# J1
j1_pins = {}
for i in range(9):
    j1_pins[i + 1] = (j1_x, 15.0 + i * 5.08)

# Filtros RC colocados no corredor central alinhados com J1.3 e J1.4
r1_p2 = (60.0, 25.16) # entrada
r1_p1 = (70.0, 25.16) # saída
c1_p1 = (76.0, 25.16)
c1_p2 = (76.0, 20.0)  # gnd

r2_p2 = (60.0, 30.24) # entrada
r2_p1 = (70.0, 30.24) # saída
c2_p1 = (76.0, 30.24)
c2_p2 = (76.0, 35.0)  # gnd

# Registrar pads
all_pads = []
for p, pos in esp_pins.items():
    all_pads.append((pos[0], pos[1], 1.0, 0))
for p, pos in pcm_pins.items():
    all_pads.append((pos[0], pos[1], 1.0, 0))
for p, pos in u3_pins.items():
    all_pads.append((pos[0], pos[1], 1.0, 0))
for p, pos in j1_pins.items():
    all_pads.append((pos[0], pos[1], 1.6, 0))
for pos in [r1_p1, r1_p2, c1_p1, c1_p2, r2_p1, r2_p2, c2_p1, c2_p2]:
    all_pads.append((pos[0], pos[1], 1.0, 0))

# Borda obstáculo
for x in range(router.w):
    router.grid[x][0] = -1
    router.grid[x][router.h - 1] = -1
for y in range(router.h):
    router.grid[0][y] = -1
    router.grid[router.w - 1][y] = -1

for px, py, r, nid in all_pads:
    router.add_pad(px, py, r, nid)

# Conexões
connections = [
    # Topo: CRANK
    ("CRANK_VR_POS", pcm_pins[11], j1_pins[1], 5, 0.8),
    ("CRANK_VR_NEG", pcm_pins[12], j1_pins[2], 4, 0.8),

    # I2S pelo topo
    ("I2S_LCK", esp_pins[11], pcm_pins[5], 10, 0.8),
    ("I2S_BCK", esp_pins[10], pcm_pins[3], 8, 0.8),
    ("I2S_DIN", esp_pins[29], pcm_pins[4], 9, 0.8),

    # Filtros TPS e MAP
    ("D25_TO_R1", esp_pins[8], r1_p2, 17, 0.8),
    ("R1_TO_C1", r1_p1, c1_p1, 12, 0.8),
    ("C1_TO_J1_TPS", c1_p1, j1_pins[3], 12, 0.8),
    ("D26_TO_R2", esp_pins[9], r2_p2, 18, 0.8),
    ("R2_TO_C2", r2_p1, c2_p1, 11, 0.8),
    ("C2_TO_J1_MAP", c2_p1, j1_pins[4], 11, 0.8),

    # Sinais rápidos e controles
    ("VSS_PULSE", esp_pins[21], j1_pins[5], 15, 0.8),
    ("CLUTCH_SIG", esp_pins[17], j1_pins[6], 3, 0.8),
    ("FB_IGN", esp_pins[23], u3_pins[9], 6, 0.8),
    ("IGN_OUT", u3_pins[3], j1_pins[8], 13, 0.8),
    ("FB_INJ", esp_pins[20], u3_pins[10], 7, 0.8),
    ("INJ_OUT", u3_pins[4], j1_pins[7], 14, 0.8),

    # Alimentação
    ("+5V_U1_U3", esp_pins[15], u3_pins[1], 2, 1.0),
    ("+5V_U3_U2", u3_pins[1], pcm_pins[1], 2, 1.0),
    ("+3V3_U1_U3", esp_pins[16], u3_pins[7], 1, 0.8),
    ("+3V3_U3_U2", u3_pins[7], pcm_pins[7], 1, 0.8),

    # Terra
    ("GND_ESP_J1", esp_pins[14], j1_pins[9], 16, 1.2),
    ("GND_U3_LV", u3_pins[2], u3_pins[8], 16, 1.0),
    ("GND_U3_J1", u3_pins[2], j1_pins[9], 16, 1.0),
    ("GND_U3_U2", u3_pins[8], pcm_pins[10], 16, 0.8),
    ("GND_U2_9", pcm_pins[10], pcm_pins[9], 16, 0.8),
    ("GND_U2_8", pcm_pins[9], pcm_pins[8], 16, 0.8),
    ("GND_U2_6", pcm_pins[8], pcm_pins[6], 16, 0.8),
    ("GND_U2_2", pcm_pins[6], pcm_pins[2], 16, 0.8),
    ("GND_C1", c1_p2, pcm_pins[10], 16, 0.8),
    ("GND_C2", c2_p2, u3_pins[8], 16, 0.8),
]

routed_paths = {}
failed = []

for name, p1, p2, net_id, width in connections:
    router.clear_pad_for_net(p1[0], p1[1], 1.2, net_id)
    router.clear_pad_for_net(p2[0], p2[1], 1.2, net_id)
    path = router.route_two_points(p1, p2, net_id, track_width=width, clearance=0.35)
    if path:
        print(f"OK: {name} (comprimento: {len(path)} pts)")
        routed_paths[name] = (path, width, net_id)
    else:
        print(f"FALHA: {name}")
        failed.append(name)

print(f"\nResultado final: {len(routed_paths)} roteadas, {len(failed)} falhas.")
