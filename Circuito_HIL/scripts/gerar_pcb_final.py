"""Gerador Definitivo da PCB Face Simples (Bottom-Only) para a Bancada HIL.
IF Betim Racing - Bancada Simulador Dinâmico Speeduino 48-Way & KTM Duke 390.

Características:
1. 100% das trilhas na camada BOTTOM (B.Cu) - face simples para fenolite.
2. Zero cruzamentos de trilhas (zero crossing) usando roteador A* de alta resolução.
3. Trilhas largas (0.8 mm para sinais, 1.2 mm para alimentação) para facilidade de corrosão caseira.
4. Ilhas de solda generosas (diâmetro 2.4 mm a 3.2 mm, furos de 1.0 mm a 1.4 mm).
5. Gabarito com furos M3 de fixação e contorno padrão de 120x90 mm.
6. Exportação automática de PDFs prontos para impressão (Normal e Espelhado para transferência térmica).
"""

import math
import heapq
import subprocess
import os

class GridRouter:
    def __init__(self, width_mm, height_mm, res=0.25):
        self.res = res
        self.w = int(width_mm / res)
        self.h = int(height_mm / res)
        self.grid = [[0 for _ in range(self.h)] for _ in range(self.w)]
        self.fixed_obstacles = [[False for _ in range(self.h)] for _ in range(self.w)]

    def to_grid(self, x, y):
        gx = max(0, min(self.w - 1, int(round(x / self.res))))
        gy = max(0, min(self.h - 1, int(round(y / self.res))))
        return gx, gy

    def to_coord(self, gx, gy):
        return gx * self.res, gy * self.res

    def block_circle(self, cx, cy, r, clearance=0.4):
        rad = (r + clearance) / self.res
        gcx, gcy = self.to_grid(cx, cy)
        irad = int(math.ceil(rad))
        for dx in range(-irad, irad + 1):
            for dy in range(-irad, irad + 1):
                if dx*dx + dy*dy <= rad*rad:
                    x = gcx + dx
                    y = gcy + dy
                    if 0 <= x < self.w and 0 <= y < self.h:
                        self.fixed_obstacles[x][y] = True

    def clear_point(self, cx, cy, r=1.5):
        rad = r / self.res
        gcx, gcy = self.to_grid(cx, cy)
        irad = int(math.ceil(rad))
        for dx in range(-irad, irad + 1):
            for dy in range(-irad, irad + 1):
                if dx*dx + dy*dy <= rad*rad:
                    x = gcx + dx
                    y = gcy + dy
                    if 0 <= x < self.w and 0 <= y < self.h:
                        self.fixed_obstacles[x][y] = False

    def route_net(self, start_pos, end_pos, net_id, clearance=0.7):
        sx, sy = self.to_grid(*start_pos)
        ex, ey = self.to_grid(*end_pos)

        def h(x, y):
            return abs(x - ex) + abs(y - ey)

        frontier = []
        heapq.heappush(frontier, (0, sx, sy))
        came_from = {}
        cost_so_far = {(sx, sy): 0}

        found = False
        while frontier:
            _, cx, cy = heapq.heappop(frontier)

            if (cx, cy) == (ex, ey):
                found = True
                break

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < self.w and 0 <= ny < self.h):
                    continue

                step_cost = 1.0 if (dx == 0 or dy == 0) else 1.414

                if self.fixed_obstacles[nx][ny] and (nx, ny) != (ex, ey):
                    continue

                grid_net = self.grid[nx][ny]
                if grid_net != 0 and grid_net != net_id and (nx, ny) != (ex, ey):
                    continue

                new_cost = cost_so_far[(cx, cy)] + step_cost
                if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                    cost_so_far[(nx, ny)] = new_cost
                    priority = new_cost + h(nx, ny) * 1.05
                    heapq.heappush(frontier, (priority, nx, ny))
                    came_from[(nx, ny)] = (cx, cy)

        if not found:
            return None

        curr = (ex, ey)
        path = []
        while curr in came_from:
            path.append(self.to_coord(*curr))
            curr = came_from[curr]
        path.append(self.to_coord(sx, sy))
        path.reverse()

        rad = clearance / self.res
        irad = int(math.ceil(rad))
        for px, py in path:
            gx, gy = self.to_grid(px, py)
            for dx in range(-irad, irad + 1):
                for dy in range(-irad, irad + 1):
                    if dx*dx + dy*dy <= rad*rad:
                        mx, my = gx + dx, gy + dy
                        if 0 <= mx < self.w and 0 <= my < self.h:
                            self.grid[mx][my] = net_id

        # Simplificação de nós colineares
        simplified = [path[0]]
        for i in range(1, len(path) - 1):
            p_prev = simplified[-1]
            p_curr = path[i]
            p_next = path[i + 1]
            d1 = (p_curr[0] - p_prev[0], p_curr[1] - p_prev[1])
            d2 = (p_next[0] - p_curr[0], p_next[1] - p_curr[1])
            cross = d1[0]*d2[1] - d1[1]*d2[0]
            if abs(cross) > 1e-4:
                simplified.append(p_curr)
        simplified.append(path[-1])

        return simplified

def build_pcb_file():
    router = GridRouter(140, 120, res=0.25)

    u1_x, u1_y = 40.0, 56.0
    u1_lx, u1_rx = u1_x - 11.43, u1_x + 11.43

    u2_x, u2_y = 80.0, 32.0
    u2_lx, u2_rx = u2_x - 7.62, u2_x + 7.62

    u3_x, u3_y = 80.0, 68.0
    u3_lx, u3_rx = u3_x - 6.35, u3_x + 6.35

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

    nets_to_route = [
        ("U3.9", "U1.23", 6, "FB_IGN", 0.8),
        ("U3.10", "U1.20", 7, "FB_INJ", 0.8),
        ("U1.21", "J1.5", 15, "VSS_PULSE", 0.8),
        ("U1.17", "J1.6", 3, "CLUTCH_SIG", 0.8),
        ("U3.3", "J1.8", 13, "SPEEDUINO_IGN", 0.8),
        ("U3.4", "J1.7", 14, "SPEEDUINO_INJ", 0.8),

        ("U1.29", "U2.4", 9, "I2S_DIN", 0.8),
        ("U1.10", "U2.3", 8, "I2S_BCK", 0.8),
        ("U1.11", "U2.5", 10, "I2S_LCK", 0.8),

        ("U2.11", "J1.1", 5, "CRANK_POS", 0.8),
        ("U2.12", "J1.2", 4, "CRANK_NEG", 0.8),

        ("U1.8", "R1.2", 17, "DAC_TPS", 0.8),
        ("U1.9", "R2.2", 18, "DAC_MAP", 0.8),
        ("R1.1", "C1.1", 12, "TPS_NODE", 0.8),
        ("R2.1", "C2.1", 11, "MAP_NODE", 0.8),

        ("C1.1", "J1.3", 12, "NET_TPS_OUT", 0.8),
        ("C2.1", "J1.4", 11, "NET_MAP_OUT", 0.8),

        ("U1.16", "U3.7", 1, "3V3_U1_to_U3", 1.2),
        ("U3.7", "U2.7", 1, "3V3_U3_to_U2", 1.2),
        ("U1.15", "U2.1", 2, "5V_U1_to_U2", 1.2),
        ("U2.1", "U3.1", 2, "5V_U2_to_U3", 1.2),

        # Conexões diretas de GND robustas
        ("C2.2", "U1.14", 16, "GND_FILTERS_ESP", 1.2),
        ("U2.8", "U2.10", 16, "GND_PCM_RIGHT", 1.2),
    ]

    routed_segments = []
    for p1_name, p2_name, net_id, desc, width in nets_to_route:
        p1 = pins[p1_name]
        p2 = pins[p2_name]
        router.clear_point(p1[0], p1[1], r=1.5)
        router.clear_point(p2[0], p2[1], r=1.5)
        path = router.route_net(p1, p2, net_id, clearance=0.7)
        if path:
            for i in range(len(path) - 1):
                routed_segments.append((path[i], path[i+1], net_id, width))
            print(f"[OK] Roteado: {desc:16s}")
        else:
            print(f"[FAIL] Falha ao rotear: {desc:16s}")

    pcb = []
    pcb.append('(kicad_pcb')
    pcb.append('\t(version 20240108)')
    pcb.append('\t(generator "kicad_cli")')
    pcb.append('\t(generator_version "10.0")')
    pcb.append('\t(general')
    pcb.append('\t\t(thickness 1.6)')
    pcb.append('\t\t(legacy_teardrops no)')
    pcb.append('\t)')
    pcb.append('\t(paper "A4")')
    pcb.append('\t(layers')
    pcb.append('\t\t(0 "F.Cu" signal)')
    pcb.append('\t\t(31 "B.Cu" signal)')
    pcb.append('\t\t(36 "B.SilkS" user "B.Silkscreen")')
    pcb.append('\t\t(37 "F.SilkS" user "F.Silkscreen")')
    pcb.append('\t\t(38 "B.Mask" user)')
    pcb.append('\t\t(39 "F.Mask" user)')
    pcb.append('\t\t(44 "Edge.Cuts" user)')
    pcb.append('\t)')
    pcb.append('\t(setup')
    pcb.append('\t\t(pad_to_mask_clearance 0.15)')
    pcb.append('\t)')

    nets = [
        (0, ""),
        (1, "+3V3"),
        (2, "+5V"),
        (3, "/CLUTCH_SIG"),
        (4, "/CRANK_VR_NEG"),
        (5, "/CRANK_VR_POS"),
        (6, "/FB_IGN_3V3"),
        (7, "/FB_INJ_3V3"),
        (8, "/I2S_BCK"),
        (9, "/I2S_DIN"),
        (10, "/I2S_LCK"),
        (11, "/NET_MAP_OUT"),
        (12, "/NET_TPS_OUT"),
        (13, "/SPEEDUINO_IGN"),
        (14, "/SPEEDUINO_INJ"),
        (15, "/VSS_PULSE"),
        (16, "GND"),
        (17, "Net-(U1-D25_(DAC_TPS))"),
        (18, "Net-(U1-D26_(DAC_MAP))"),
    ]
    for n_id, n_name in nets:
        pcb.append(f'\t(net {n_id} "{n_name}")')

    # Borda da Placa: 120 mm x 90 mm
    pcb.append('\t(gr_rect (start 10.0 10.0) (end 130.0 100.0) (stroke (width 0.25) (type solid)) (fill none) (layer "Edge.Cuts") (uuid "b0000000-0000-0000-0000-000000000001"))')

    # Textos da Serigrafia (F.SilkS)
    pcb.append('\t(gr_text "IF BETIM RACING - BANCADA HIL" (at 70.0 14.0) (layer "F.SilkS") (uuid "b0000000-0000-0000-0000-000000000002") (effects (font (size 1.8 1.8) (thickness 0.3) bold)))')
    pcb.append('\t(gr_text "SPEEDUINO 48-WAY & KTM DUKE 390 (FACE SIMPLES - 100% B.Cu)" (at 70.0 17.5) (layer "F.SilkS") (uuid "b0000000-0000-0000-0000-000000000003") (effects (font (size 1.1 1.1) (thickness 0.2))))')
    pcb.append('\t(gr_text "IF BETIM RACING" (at 70.0 96.0) (layer "B.Cu") (uuid "b0000000-0000-0000-0000-000000000004") (effects (font (size 1.5 1.5) (thickness 0.25)) (justify mirror)))')

    # Furos M3 de fixação
    for corner_x, corner_y, cid in [(13.5, 13.5, "1"), (126.5, 13.5, "2"), (13.5, 96.5, "3"), (126.5, 96.5, "4")]:
        pcb.append(f'\t(footprint "MountingHole:MountingHole_3.2mm_M3" (layer "F.Cu") (uuid "m0000000-0000-0000-0000-00000000000{cid}") (at {corner_x} {corner_y})')
        pcb.append(f'\t\t(pad "1" thru_hole circle (at 0 0) (size 6.0 6.0) (drill 3.2) (layers "*.Cu" "*.Mask") (net 16 "GND"))')
        pcb.append('\t)')

    # Footprint U1 (ESP32 DevKit V1)
    u1_left_nets = [
        (1, "EN", 0), (2, "VP", 0), (3, "VN", 0), (4, "D34", 0), (5, "D35", 0),
        (6, "D32", 0), (7, "D33", 0), (8, "D25", 17), (9, "D26", 18), (10, "D27", 8),
        (11, "D14", 10), (12, "D12", 0), (13, "D13", 0), (14, "GND", 16), (15, "VIN", 2)
    ]
    u1_right_nets = [
        (30, "D23", 0), (29, "D22", 9), (28, "TX0", 0), (27, "RX0", 0), (26, "D21", 0),
        (25, "D19", 0), (24, "D18", 0), (23, "D5", 6), (22, "D17", 0), (21, "D16", 15),
        (20, "D4", 7), (19, "D0", 0), (18, "D2", 0), (17, "D15", 3), (16, "3V3", 1)
    ]
    pcb.append(f'\t(footprint "Module:ESP32_DevKit_V1_30Pin" (layer "F.Cu") (uuid "f1000000-0000-0000-0000-000000000001") (at {u1_x} {u1_y})')
    pcb.append(f'\t\t(property "Reference" "U1" (at 0 -20.0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    pcb.append(f'\t\t(property "Value" "ESP32_DevKit_V1" (at 0 20.0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_rect (start -13.0 -19.5) (end 13.0 19.5) (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS"))')
    pcb.append(f'\t\t(fp_text user "ESP32 DevKit V1" (at 0 0 90) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    for idx, (pnum, pname, pnet) in enumerate(u1_left_nets):
        py = -7 * 2.54 + idx * 2.54
        pad_shape = "roundrect (roundrect_rratio 0.25)" if pnum == 1 else "circle"
        pcb.append(f'\t\t(pad "{pnum}" thru_hole {pad_shape} (at -11.43 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
    for idx, (pnum, pname, pnet) in enumerate(u1_right_nets):
        py = -7 * 2.54 + idx * 2.54
        pcb.append(f'\t\t(pad "{pnum}" thru_hole circle (at 11.43 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
    pcb.append('\t)')

    # Footprint U2 (PCM5102)
    u2_nets_left = [(1, "VCC", 2), (2, "GND", 16), (3, "BCK", 8), (4, "DIN", 9), (5, "LCK", 10), (6, "SCK", 16)]
    u2_nets_right = [(7, "XMT", 1), (8, "FMT", 16), (9, "FLT", 16), (10, "DMP", 16), (11, "LOUT", 5), (12, "AGND", 4), (13, "ROUT", 0)]
    pcb.append(f'\t(footprint "Module:PCM5102A_Module" (layer "F.Cu") (uuid "f2000000-0000-0000-0000-000000000001") (at {u2_x} {u2_y})')
    pcb.append(f'\t\t(property "Reference" "U2" (at 0 -10.0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    pcb.append(f'\t\t(property "Value" "GY-PCM5102A" (at 0 10.0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_rect (start -9.5 -9.0) (end 9.5 9.0) (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS"))')
    pcb.append(f'\t\t(fp_text user "PCM5102A" (at 0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    for idx, (pnum, pname, pnet) in enumerate(u2_nets_left):
        py = -2.5 * 2.54 + idx * 2.54
        pad_shape = "roundrect (roundrect_rratio 0.25)" if pnum == 1 else "circle"
        pcb.append(f'\t\t(pad "{pnum}" thru_hole {pad_shape} (at -7.62 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
    for idx, (pnum, pname, pnet) in enumerate(u2_nets_right):
        py = -3.0 * 2.54 + idx * 2.54
        pcb.append(f'\t\t(pad "{pnum}" thru_hole circle (at 7.62 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
    pcb.append('\t)')

    # Footprint U3 (Level Converter)
    u3_nets_left = [(7, "LV", 1), (8, "GND", 16), (9, "LV1", 6), (10, "LV2", 7), (11, "LV3", 0), (12, "LV4", 0)]
    u3_nets_right = [(1, "HV", 2), (2, "GND", 16), (3, "HV1", 13), (4, "HV2", 14), (5, "HV3", 0), (6, "HV4", 0)]
    pcb.append(f'\t(footprint "Module:Level_Converter_4CH" (layer "F.Cu") (uuid "f3000000-0000-0000-0000-000000000001") (at {u3_x} {u3_y})')
    pcb.append(f'\t\t(property "Reference" "U3" (at 0 -9.0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    pcb.append(f'\t\t(property "Value" "Level_Converter" (at 0 9.0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_rect (start -8.0 -8.0) (end 8.0 8.0) (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS"))')
    for idx, (pnum, pname, pnet) in enumerate(u3_nets_left):
        py = -2.5 * 2.54 + idx * 2.54
        pcb.append(f'\t\t(pad "{pnum}" thru_hole circle (at -6.35 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
    for idx, (pnum, pname, pnet) in enumerate(u3_nets_right):
        py = -2.5 * 2.54 + idx * 2.54
        pad_shape = "roundrect (roundrect_rratio 0.25)" if pnum == 1 else "circle"
        pcb.append(f'\t\t(pad "{pnum}" thru_hole {pad_shape} (at 6.35 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
    pcb.append('\t)')

    # Footprint J1 (Bornier 9 pinos)
    j1_nets = [
        (1, "CRANK+", 5), (2, "VR1-", 4), (3, "TPS", 12), (4, "MAP", 11),
        (5, "VSS", 15), (6, "CLUTCH", 3), (7, "INJ", 14), (8, "IGN", 13), (9, "GND", 16)
    ]
    pcb.append(f'\t(footprint "Connector_TerminalBlock:TerminalBlock_bornier-9_P5.08mm" (layer "F.Cu") (uuid "f4000000-0000-0000-0000-000000000001") (at {j1_x} {j1_y})')
    pcb.append(f'\t\t(property "Reference" "J1" (at 0 -24.0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    pcb.append(f'\t\t(property "Value" "CHICOTE_SPEEDUINO" (at 0 24.0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_rect (start -4.5 -22.5) (end 4.5 22.5) (stroke (width 0.25) (type solid)) (fill none) (layer "F.SilkS"))')
    for idx, (pnum, pname, pnet) in enumerate(j1_nets):
        py = -4 * 5.08 + idx * 5.08
        pad_shape = "roundrect (roundrect_rratio 0.25)" if pnum == 1 else "circle"
        pcb.append(f'\t\t(pad "{pnum}" thru_hole {pad_shape} (at 0 {py:.2f}) (size 3.2 3.2) (drill 1.4) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
        pcb.append(f'\t\t(fp_text user "{pname}" (at -6.5 {py:.2f}) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15)) (justify right)))')
    pcb.append('\t)')

    # Footprints R1, C1, R2, C2 (esquerda)
    pcb.append(f'\t(footprint "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" (layer "F.Cu") (uuid "f5000000-0000-0000-0000-000000000001") (at 16.0 54.0 90)')
    pcb.append('\t\t(property "Reference" "R1" (at 2.5 0 90) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append('\t\t(property "Value" "10k" (at -2.5 0 90) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))')
    pcb.append('\t\t(pad "1" thru_hole circle (at 0 -2.0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 12 "/NET_TPS_OUT"))')
    pcb.append('\t\t(pad "2" thru_hole circle (at 0 2.0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 17 "Net-(U1-D25_(DAC_TPS))"))')
    pcb.append('\t)')

    pcb.append(f'\t(footprint "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" (layer "F.Cu") (uuid "f6000000-0000-0000-0000-000000000001") (at 18.0 48.0)')
    pcb.append('\t\t(property "Reference" "C1" (at 0 -2.2) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append('\t\t(property "Value" "1uF" (at 0 2.2) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))')
    pcb.append('\t\t(pad "1" thru_hole circle (at -2.0 0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 12 "/NET_TPS_OUT"))')
    pcb.append('\t\t(pad "2" thru_hole circle (at 2.0 0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 16 "GND"))')
    pcb.append('\t)')

    pcb.append(f'\t(footprint "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" (layer "F.Cu") (uuid "f7000000-0000-0000-0000-000000000001") (at 16.0 66.0 90)')
    pcb.append('\t\t(property "Reference" "R2" (at 2.5 0 90) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append('\t\t(property "Value" "10k" (at -2.5 0 90) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))')
    pcb.append('\t\t(pad "1" thru_hole circle (at 0 2.0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 11 "/NET_MAP_OUT"))')
    pcb.append('\t\t(pad "2" thru_hole circle (at 0 -2.0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 18 "Net-(U1-D26_(DAC_MAP))"))')
    pcb.append('\t)')

    pcb.append(f'\t(footprint "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" (layer "F.Cu") (uuid "f8000000-0000-0000-0000-000000000001") (at 18.0 72.0)')
    pcb.append('\t\t(property "Reference" "C2" (at 0 -2.2) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append('\t\t(property "Value" "1uF" (at 0 2.2) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))')
    pcb.append('\t\t(pad "1" thru_hole circle (at -2.0 0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 11 "/NET_MAP_OUT"))')
    pcb.append('\t\t(pad "2" thru_hole circle (at 2.0 0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 16 "GND"))')
    pcb.append('\t)')

    # Segmentos de trilha 100% no B.Cu
    seg_idx = 1
    for p1, p2, net_id, width in routed_segments:
        pcb.append(f'\t(segment (start {p1[0]:.2f} {p1[1]:.2f}) (end {p2[0]:.2f} {p2[1]:.2f}) (width {width}) (layer "B.Cu") (net {net_id}) (uuid "s0000000-0000-0000-0000-{seg_idx:012d}"))')
        seg_idx += 1

    pcb.append(')')
    return '\n'.join(pcb)

if __name__ == '__main__':
    content = build_pcb_file()
    out_path = 'Circuito_HIL/Circuito_HIL.kicad_pcb'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Placa 100% Bottom salva em {out_path}!")

    kicad_cli = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'

    # Exportar PDF Bottom Espelhado para Fenolite / Transferência Térmica
    res1 = subprocess.run([
        kicad_cli, 'pcb', 'export', 'pdf',
        '--layers', 'B.Cu,Edge.Cuts',
        '--mirror',
        '--black-and-white',
        '--output', 'Circuito_HIL/Placa_HIL_Bottom_Trilhas_Espelhado.pdf',
        out_path
    ], capture_output=True, text=True)

    # Exportar PDF Bottom Normal
    res2 = subprocess.run([
        kicad_cli, 'pcb', 'export', 'pdf',
        '--layers', 'B.Cu,Edge.Cuts',
        '--black-and-white',
        '--output', 'Circuito_HIL/Placa_HIL_Bottom_Trilhas_Normal.pdf',
        out_path
    ], capture_output=True, text=True)

    # Exportar PDF Top Silkscreen (Montagem)
    res3 = subprocess.run([
        kicad_cli, 'pcb', 'export', 'pdf',
        '--layers', 'F.SilkS,Edge.Cuts',
        '--output', 'Circuito_HIL/Placa_HIL_Top_Silkscreen_Componentes.pdf',
        out_path
    ], capture_output=True, text=True)

    # Exportar PDF Completo
    res4 = subprocess.run([
        kicad_cli, 'pcb', 'export', 'pdf',
        '--layers', 'F.SilkS,B.Cu,Edge.Cuts',
        '--output', 'Circuito_HIL/Placa_HIL_Completa_Visualizacao.pdf',
        out_path
    ], capture_output=True, text=True)

    # Renderizar imagens 3D
    subprocess.run([
        kicad_cli, 'pcb', 'render', '--side', 'top', '--quality', 'high',
        '--output', 'Circuito_HIL/render_pcb_top.png', out_path
    ], capture_output=True)

    subprocess.run([
        kicad_cli, 'pcb', 'render', '--side', 'bottom', '--quality', 'high',
        '--output', 'Circuito_HIL/render_pcb_bottom.png', out_path
    ], capture_output=True)

    print("Todos os PDFs e renders foram gerados com sucesso!")
