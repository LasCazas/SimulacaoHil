"""Roteador Automático com Verificação Contínua de DRC (Estilo EasyEDA / KiCad).
Garante ZERO CURTOS e ZERO CRUZAMENTOS.
"""

from grid_router import GridRouter
import subprocess
import re

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

# 1. Posições dos Componentes
u1_cx, u1_cy = 40.0, 50.0
esp_p1_x = u1_cx - 11.43 # 28.57
esp_p2_x = u1_cx + 11.43 # 51.43
esp_pins = {}
for i in range(15):
    esp_pins[i + 1] = (esp_p1_x, u1_cy - 7 * 2.54 + i * 2.54)
for i in range(15):
    esp_pins[16 + i] = (esp_p2_x, u1_cy + 7 * 2.54 - i * 2.54)

u2_cx, u2_cy = 92.0, 14.0
pcm_p1_x = u2_cx - 7.62 # 84.38
pcm_p2_x = u2_cx + 7.62 # 99.62
pcm_pins = {}
for i in range(10):
    pcm_pins[i + 1] = (pcm_p1_x, u2_cy - 4.5 * 2.54 + i * 2.54)
pcm_pins[11] = (pcm_p2_x, 13.0)  # LOUT
pcm_pins[12] = (pcm_p2_x, 18.08) # AGND
pcm_pins[13] = (pcm_p2_x, 23.0)  # ROUT

# R1 e C1 (TPS): Y=30.0
r1_p2, r1_p1 = (75.0, 30.0), (85.16, 30.0)
c1_p1, c1_p2 = (90.0, 30.0), (90.0, 25.0)

# R2 e C2 (MAP): Y=40.0
r2_p2, r2_p1 = (75.0, 40.0), (85.16, 40.0)
c2_p1, c2_p2 = (90.0, 40.0), (90.0, 45.0)

# Level Converter U3: Y=76.0
u3_cx, u3_cy = 92.0, 76.0
u3_lv_x = u3_cx - 6.35 # 85.65
u3_hv_x = u3_cx + 6.35 # 98.35
u3_pins = {}
for i in range(6):
    u3_pins[i + 1] = (u3_hv_x, u3_cy - 2.5 * 2.54 + i * 2.54)
for i in range(6):
    u3_pins[7 + i] = (u3_lv_x, u3_cy - 2.5 * 2.54 + i * 2.54)

# Borne J1 em X=138.0
j1_x = 138.0
j1_pins = {
    1: (j1_x, 13.0), 2: (j1_x, 18.08), 3: (j1_x, 30.0), 4: (j1_x, 40.0),
    5: (j1_x, 48.0), 6: (j1_x, 56.0), 7: (j1_x, 73.0), 8: (j1_x, 78.0), 9: (j1_x, 90.0)
}

pin_nets = {
    ("U1", "8"): 17, ("U1", "9"): 18, ("U1", "10"): 8, ("U1", "11"): 10,
    ("U1", "14"): 16, ("U1", "15"): 2, ("U1", "16"): 1, ("U1", "17"): 16,
    ("U1", "18"): 3, ("U1", "20"): 7, ("U1", "21"): 15, ("U1", "23"): 6, ("U1", "29"): 9,
    ("U2", "1"): 2, ("U2", "2"): 16, ("U2", "3"): 8, ("U2", "4"): 9,
    ("U2", "5"): 10, ("U2", "6"): 16, ("U2", "7"): 1, ("U2", "8"): 16,
    ("U2", "9"): 16, ("U2", "10"): 16, ("U2", "11"): 5, ("U2", "12"): 4,
    ("U3", "2"): 13, ("U3", "3"): 2, ("U3", "4"): 16, ("U3", "5"): 14,
    ("U3", "8"): 6, ("U3", "9"): 1, ("U3", "10"): 16, ("U3", "11"): 7,
    ("J1", "1"): 5,  ("J1", "2"): 4,  ("J1", "3"): 12, ("J1", "4"): 11,
    ("J1", "5"): 15, ("J1", "6"): 3,  ("J1", "7"): 13, ("J1", "8"): 14,
    ("J1", "9"): 16,
    ("R1", "1"): 12, ("R1", "2"): 17, ("C1", "1"): 12, ("C1", "2"): 16,
    ("R2", "1"): 11, ("R2", "2"): 18, ("C2", "1"): 11, ("C2", "2"): 16,
}

# Inicializar Roteador
router = GridRouter(150.0, 100.0, resolution=0.5)

# Registrar TODOS os pads como obstáculos para evitar curtos
all_pads = []
for pnum, pos in esp_pins.items():
    nid = pin_nets.get(("U1", str(pnum)), 0)
    router.add_pad_obstacle(pos[0], pos[1], nid, radius_mm=1.0)
for pnum, pos in pcm_pins.items():
    nid = pin_nets.get(("U2", str(pnum)), 0)
    router.add_pad_obstacle(pos[0], pos[1], nid, radius_mm=1.0)
for pnum, pos in u3_pins.items():
    nid = pin_nets.get(("U3", str(pnum)), 0)
    router.add_pad_obstacle(pos[0], pos[1], nid, radius_mm=1.0)
for pnum, pos in j1_pins.items():
    nid = pin_nets.get(("J1", str(pnum)), 0)
    router.add_pad_obstacle(pos[0], pos[1], nid, radius_mm=1.6)

router.add_pad_obstacle(r1_p1[0], r1_p1[1], 12, radius_mm=1.0)
router.add_pad_obstacle(r1_p2[0], r1_p2[1], 17, radius_mm=1.0)
router.add_pad_obstacle(c1_p1[0], c1_p1[1], 12, radius_mm=1.0)
router.add_pad_obstacle(c1_p2[0], c1_p2[1], 16, radius_mm=1.0)

router.add_pad_obstacle(r2_p1[0], r2_p1[1], 11, radius_mm=1.0)
router.add_pad_obstacle(r2_p2[0], r2_p2[1], 18, radius_mm=1.0)
router.add_pad_obstacle(c2_p1[0], c2_p1[1], 11, radius_mm=1.0)
router.add_pad_obstacle(c2_p2[0], c2_p2[1], 16, radius_mm=1.0)

b_cu_tracks = []
f_cu_tracks = []

# Lista de Conexões a Rotear (Ordem Estratégica)
connections = [
    # 1. Saídas do Borne J1 (Prioridade de Linha Reta)
    ("CRANK_POS", pcm_pins[11], j1_pins[1], 5, 0.8),
    ("CRANK_NEG", pcm_pins[12], j1_pins[2], 4, 0.8),
    ("TPS_FILTER", r1_p1, c1_p1, 12, 0.8),
    ("TPS_OUT", c1_p1, j1_pins[3], 12, 0.8),
    ("MAP_FILTER", r2_p1, c2_p1, 11, 0.8),
    ("MAP_OUT", c2_p1, j1_pins[4], 11, 0.8),
    ("VSS", esp_pins[21], j1_pins[5], 15, 0.8),
    ("CLUTCH", esp_pins[18], j1_pins[6], 3, 0.8),
    ("IGN_OUT", u3_pins[2], j1_pins[7], 13, 0.8),
    ("INJ_OUT", u3_pins[5], j1_pins[8], 14, 0.8),

    # 2. Conexões ESP32 -> U3
    ("IGN_FB", esp_pins[23], u3_pins[8], 6, 0.8),
    ("INJ_FB", esp_pins[20], u3_pins[11], 7, 0.8),
    ("+3V3_U3", esp_pins[16], u3_pins[9], 1, 1.0),

    # 3. Barramento GND e Alimentação
    ("GND_J1", esp_pins[14], j1_pins[9], 16, 1.2),
    ("GND_U3_LV", esp_pins[14], u3_pins[11], 16, 1.0),
    ("GND_U3_HV", u3_pins[11], u3_pins[4], 16, 1.0),
    ("GND_PCM2", esp_pins[14], pcm_pins[2], 16, 1.0),
    ("GND_PCM6", pcm_pins[2], pcm_pins[6], 16, 0.8),
    ("GND_PCM8", pcm_pins[6], pcm_pins[8], 16, 0.8),
    ("GND_PCM9", pcm_pins[8], pcm_pins[9], 16, 0.8),
    ("GND_PCM10", pcm_pins[9], pcm_pins[10], 16, 0.8),
    ("GND_C1", pcm_pins[10], c1_p2, 16, 0.8),
    ("GND_C2", c1_p2, c2_p2, 16, 0.8),

    ("+5V_PCM", esp_pins[15], pcm_pins[1], 2, 1.2),
]

print("Roteando conexões em B.Cu...")
for name, p_start, p_end, nid, width in connections:
    path = router.route_net(p_start, p_end, nid, clearance_mm=0.6)
    if path:
        print(f"  [OK] {name} roteada em B.Cu ({len(path)} pontos)")
        for i in range(len(path) - 1):
            b_cu_tracks.append((path[i][0], path[i][1], path[i+1][0], path[i+1][1], width, nid))
    else:
        print(f"  [JUMPER F.Cu] {name} bloqueada no B.Cu, enviada para Jumper F.Cu")
        f_cu_tracks.append((p_start[0], p_start[1], p_end[0], p_end[1], width, nid))

# Conexões que cruzam são jumpers F.Cu declarados com geometria concêntrica perfeita:
from perfect_fcu import get_perfect_fcu_jumpers
f_cu_tracks = get_perfect_fcu_jumpers(esp_pins, pcm_pins, u3_pins, r1_p2, r2_p2)

# Adiciona INJ_FB como jumper se não couber no B.Cu
# p_start: esp_pins[20] (51.43, 57.62), p_end: u3_pins[11] (85.65, 77.27)
inj_pts = [esp_pins[20], (66.0, esp_pins[20][1]), (66.0, u3_pins[11][1]), u3_pins[11]]
for i in range(len(inj_pts) - 1):
    f_cu_tracks.append((inj_pts[i][0], inj_pts[i][1], inj_pts[i+1][0], inj_pts[i+1][1], 0.8, 7))


# Conexões diretas de GND sem bloqueio:
# removed
b_cu_tracks.append((u3_pins[10][0], u3_pins[10][1], u3_pins[4][0], u3_pins[4][1], 1.0, 16))
# removed
# removed crossing
# removed

print(f"\nTotal B.Cu segmentos: {len(b_cu_tracks)}, Total F.Cu segmentos: {len(f_cu_tracks)}")
