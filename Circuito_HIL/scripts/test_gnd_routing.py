import sys
sys.path.append('Circuito_HIL')
from test_autoroute import pins, nets_to_route
from router_fenolite import GridRouter

router = GridRouter(140, 120, res=0.25)
for name, pos in pins.items():
    router.block_circle(pos[0], pos[1], r=1.0, clearance=0.5)

all_nets = list(nets_to_route) + [
    ("C1.2", "C2.2", 16, "GND_FILTERS"),
    ("C2.2", "U1.14", 16, "GND_U1"),
    ("U2.2", "U2.6", 16, "GND_U2_L"),
    ("U2.8", "U2.10", 16, "GND_U2_R"),
    ("U3.2", "U3.8", 16, "GND_U3"),
    ("U3.8", "J1.9", 16, "GND_J1"),
]

routed = 0
for p1_name, p2_name, net_id, desc in all_nets:
    p1 = pins[p1_name]
    p2 = pins[p2_name]
    router.clear_point(p1[0], p1[1], r=1.5)
    router.clear_point(p2[0], p2[1], r=1.5)
    path = router.route_net(p1, p2, net_id, clearance=0.6)
    if path:
        routed += 1
        print(f"[OK] {desc:16s}")
    else:
        print(f"[FAIL] {desc:16s}")

print(f"\nTotal com GND: {routed}/{len(all_nets)}")
