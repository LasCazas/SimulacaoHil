from router_fenolite import GridRouter

router = GridRouter(140, 120, res=0.5)

# Posições ajustadas para fluxo natural sem cruzamento
u1_x, u1_y = 40.0, 56.0
u1_lx, u1_rx = u1_x - 11.43, u1_x + 11.43

# PCM5102 no topo centro-direita
u2_x, u2_y = 80.0, 32.0
u2_lx, u2_rx = u2_x - 7.62, u2_x + 7.62

# Level Converter alinhado diretamente com pinos 20 e 23 do ESP32
u3_x, u3_y = 80.0, 68.0
u3_lx, u3_rx = u3_x - 6.35, u3_x + 6.35

# Conector Speeduino na borda direita
j1_x, j1_y = 120.0, 58.0

pins = {
    # U1 (ESP32)
    "U1.8": (u1_lx, u1_y - 7*2.54 + 7*2.54),   # D25 (56.0)
    "U1.9": (u1_lx, u1_y - 7*2.54 + 8*2.54),   # D26 (58.54)
    "U1.10": (u1_lx, u1_y - 7*2.54 + 9*2.54),  # D27_BCK (61.08)
    "U1.11": (u1_lx, u1_y - 7*2.54 + 10*2.54), # D14_LCK (63.62)
    "U1.14": (u1_lx, u1_y - 7*2.54 + 13*2.54), # GND (71.24)
    "U1.15": (u1_lx, u1_y - 7*2.54 + 14*2.54), # VIN (73.78)

    "U1.29": (u1_rx, u1_y - 7*2.54 + 1*2.54),  # D22_DIN (40.76)
    "U1.23": (u1_rx, u1_y - 7*2.54 + 7*2.54),  # D5_IGN (56.00)
    "U1.21": (u1_rx, u1_y - 7*2.54 + 9*2.54),  # D16_VSS (61.08)
    "U1.20": (u1_rx, u1_y - 7*2.54 + 10*2.54), # D4_INJ (63.62)
    "U1.17": (u1_rx, u1_y - 7*2.54 + 13*2.54), # D15_CLUTCH (71.24)
    "U1.16": (u1_rx, u1_y - 7*2.54 + 14*2.54), # 3V3 (73.78)

    # U2 (PCM5102)
    "U2.1": (u2_lx, u2_y - 2.5*2.54 + 0*2.54), # VCC (25.65)
    "U2.2": (u2_lx, u2_y - 2.5*2.54 + 1*2.54), # GND (28.19)
    "U2.3": (u2_lx, u2_y - 2.5*2.54 + 2*2.54), # BCK (30.73)
    "U2.4": (u2_lx, u2_y - 2.5*2.54 + 3*2.54), # DIN (33.27)
    "U2.5": (u2_lx, u2_y - 2.5*2.54 + 4*2.54), # LCK (35.81)
    "U2.6": (u2_lx, u2_y - 2.5*2.54 + 5*2.54), # SCK (38.35)

    "U2.7": (u2_rx, u2_y - 3.0*2.54 + 0*2.54), # XMT (24.38)
    "U2.8": (u2_rx, u2_y - 3.0*2.54 + 1*2.54), # FMT (26.92)
    "U2.9": (u2_rx, u2_y - 3.0*2.54 + 2*2.54), # FLT (29.46)
    "U2.10": (u2_rx, u2_y - 3.0*2.54 + 3*2.54),# DMP (32.00)
    "U2.11": (u2_rx, u2_y - 3.0*2.54 + 4*2.54),# LOUT (34.54)
    "U2.12": (u2_rx, u2_y - 3.0*2.54 + 5*2.54),# AGND (37.08)

    # U3 (Level Converter)
    "U3.7": (u3_lx, u3_y - 2.5*2.54 + 0*2.54), # LV (61.65)
    "U3.8": (u3_lx, u3_y - 2.5*2.54 + 1*2.54), # GND (64.19)
    "U3.9": (u3_lx, u3_y - 2.5*2.54 + 2*2.54), # LV1 (66.73)
    "U3.10": (u3_lx, u3_y - 2.5*2.54 + 3*2.54),# LV2 (69.27)

    "U3.1": (u3_rx, u3_y - 2.5*2.54 + 0*2.54), # HV (61.65)
    "U3.2": (u3_rx, u3_y - 2.5*2.54 + 1*2.54), # GND (64.19)
    "U3.3": (u3_rx, u3_y - 2.5*2.54 + 2*2.54), # HV1 (66.73)
    "U3.4": (u3_rx, u3_y - 2.5*2.54 + 3*2.54), # HV2 (69.27)

    # J1 (Speeduino Bornier)
    "J1.1": (j1_x, j1_y - 4*5.08 + 0*5.08), # CRANK+ (37.68)
    "J1.2": (j1_x, j1_y - 4*5.08 + 1*5.08), # VR1- (42.76)
    "J1.3": (j1_x, j1_y - 4*5.08 + 2*5.08), # TPS (47.84)
    "J1.4": (j1_x, j1_y - 4*5.08 + 3*5.08), # MAP (52.92)
    "J1.5": (j1_x, j1_y - 4*5.08 + 4*5.08), # VSS (58.00)
    "J1.6": (j1_x, j1_y - 4*5.08 + 5*5.08), # CLUTCH (63.08)
    "J1.7": (j1_x, j1_y - 4*5.08 + 6*5.08), # INJ (68.16)
    "J1.8": (j1_x, j1_y - 4*5.08 + 7*5.08), # IGN (73.24)
    "J1.9": (j1_x, j1_y - 4*5.08 + 8*5.08), # GND (78.32)

    # R1, C1, R2, C2 (esquerda do ESP32)
    "R1.1": (16.0, 52.0),
    "R1.2": (16.0, 56.0),
    "C1.1": (16.0, 48.0),
    "C1.2": (20.0, 48.0),

    "R2.1": (16.0, 68.0),
    "R2.2": (16.0, 64.0),
    "C2.1": (16.0, 72.0),
    "C2.2": (20.0, 72.0),
}

for name, pos in pins.items():
    router.block_circle(pos[0], pos[1], r=1.0, clearance=0.4)

# Roteamento dos Sinais primeiro, abrindo os canais diretos!
nets_to_route = [
    # 1. Conexões diretas sem cruzamento no centro da placa
    ("U3.9", "U1.23", 6, "FB_IGN"),
    ("U3.10", "U1.20", 7, "FB_INJ"),
    ("U1.21", "J1.5", 15, "VSS_PULSE"),
    ("U1.17", "J1.6", 3, "CLUTCH_SIG"),
    ("U3.3", "J1.8", 13, "SPEEDUINO_IGN"),
    ("U3.4", "J1.7", 14, "SPEEDUINO_INJ"),

    # 2. I2S
    ("U1.29", "U2.4", 9, "I2S_DIN"),
    ("U1.10", "U2.3", 8, "I2S_BCK"),
    ("U1.11", "U2.5", 10, "I2S_LCK"),

    # 3. Crank VR
    ("U2.11", "J1.1", 5, "CRANK_POS"),
    ("U2.12", "J1.2", 4, "CRANK_NEG"),

    # 4. DACs para os filtros
    ("U1.8", "R1.2", 17, "DAC_TPS"),
    ("U1.9", "R2.2", 18, "DAC_MAP"),
    ("R1.1", "C1.1", 12, "TPS_NODE"),
    ("R2.1", "C2.1", 11, "MAP_NODE"),

    # 5. TPS e MAP filtrados pela borda
    ("C1.1", "J1.3", 12, "NET_TPS_OUT"),
    ("C2.1", "J1.4", 11, "NET_MAP_OUT"),

    # 6. Alimentações contornando pelas margens externas
    ("U1.16", "U3.7", 1, "3V3_U1_to_U3"),
    ("U3.7", "U2.7", 1, "3V3_U3_to_U2"),
    ("U1.15", "U2.1", 2, "5V_U1_to_U2"),
    ("U2.1", "U3.1", 2, "5V_U2_to_U3"),
]

routed_paths = []
failed = []

for p1_name, p2_name, net_id, desc in nets_to_route:
    p1 = pins[p1_name]
    p2 = pins[p2_name]
    router.clear_point(p1[0], p1[1], r=1.2)
    router.clear_point(p2[0], p2[1], r=1.2)

    path = router.route_net(p1, p2, net_id, clearance=0.45)
    if path:
        routed_paths.append((net_id, desc, path))
        print(f"[OK] Roteado: {desc:16s} ({p1_name} -> {p2_name})")
    else:
        failed.append(desc)
        print(f"[FAIL] Falha ao rotear: {desc} ({p1_name} -> {p2_name})")

print(f"\nResultado final: {len(routed_paths)}/{len(nets_to_route)} roteados com sucesso!")
if failed:
    print(f"Falhas: {failed}")
else:
    print("TODAS AS 21 REDES FORAM ROTEADAS COM SUCESSO EM UMA ÚNICA CAMADA (B.Cu)!")
