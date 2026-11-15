import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from grid_router import GridRouter
from auto_route_perfect import esp_pins, pcm_pins, u3_pins, j1_pins, r1_p1, r1_p2, c1_p1, c1_p2, r2_p1, r2_p2, c2_p1, c2_p2, pin_nets

router_fcu = GridRouter(150.0, 100.0, resolution=0.5)

# Add all pads as obstacles to F.Cu router
for pnum, pos in esp_pins.items():
    nid = pin_nets.get(("U1", str(pnum)), 0)
    router_fcu.add_pad_obstacle(pos[0], pos[1], nid, radius_mm=1.0)
for pnum, pos in pcm_pins.items():
    nid = pin_nets.get(("U2", str(pnum)), 0)
    router_fcu.add_pad_obstacle(pos[0], pos[1], nid, radius_mm=1.0)
for pnum, pos in u3_pins.items():
    nid = pin_nets.get(("U3", str(pnum)), 0)
    router_fcu.add_pad_obstacle(pos[0], pos[1], nid, radius_mm=1.0)
for pnum, pos in j1_pins.items():
    nid = pin_nets.get(("J1", str(pnum)), 0)
    router_fcu.add_pad_obstacle(pos[0], pos[1], nid, radius_mm=1.6)

router_fcu.add_pad_obstacle(r1_p1[0], r1_p1[1], 12, radius_mm=1.0)
router_fcu.add_pad_obstacle(r1_p2[0], r1_p2[1], 17, radius_mm=1.0)
router_fcu.add_pad_obstacle(c1_p1[0], c1_p1[1], 12, radius_mm=1.0)
router_fcu.add_pad_obstacle(c1_p2[0], c1_p2[1], 16, radius_mm=1.0)

router_fcu.add_pad_obstacle(r2_p1[0], r2_p1[1], 11, radius_mm=1.0)
router_fcu.add_pad_obstacle(r2_p2[0], r2_p2[1], 18, radius_mm=1.0)
router_fcu.add_pad_obstacle(c2_p1[0], c2_p1[1], 11, radius_mm=1.0)
router_fcu.add_pad_obstacle(c2_p2[0], c2_p2[1], 16, radius_mm=1.0)

jumpers_to_route = [
    # Sort order to avoid trapping:
    # 1. Long power lines on F.Cu: route outside at X=110 or X=65
    ("J_5V_U3", pcm_pins[1], u3_pins[1], 2, 1.0),
    ("J_3V3_PCM", u3_pins[7], pcm_pins[7], 1, 0.8),
    # 2. Signals
    ("INJ_FB", esp_pins[20], u3_pins[10], 7, 0.8),
    ("J_DIN", esp_pins[29], pcm_pins[4], 9, 0.8),
    ("J_LCK", esp_pins[11], pcm_pins[5], 10, 0.8),
    ("J_BCK", esp_pins[10], pcm_pins[3], 8, 0.8),
    ("J_MAP", esp_pins[9], r2_p2, 18, 0.8),
    ("J_TPS", esp_pins[8], r1_p2, 17, 0.8),
]

print("Roteando jumpers em F.Cu com GridRouter...")
fcu_paths = {}
for name, p_start, p_end, nid, width in jumpers_to_route:
    path = router_fcu.route_net(p_start, p_end, nid, clearance_mm=0.6)
    if path:
        print(f"  [OK] {name} roteada em F.Cu ({len(path)} pontos)")
        fcu_paths[name] = (path, width, nid)
    else:
        print(f"  [FALHA] {name} NÃO ENCONTROU CAMINHO no F.Cu!")
