import sys
sys.path.append('Circuito_HIL')
from router_fenolite import GridRouter

router = GridRouter(145, 120, res=0.25)

u1_x, u1_y = 40.0, 56.0
u1_lx, u1_rx = u1_x - 11.43, u1_x + 11.43

u2_x, u2_y = 80.0, 32.0
u2_lx, u2_rx = u2_x - 7.62, u2_x + 7.62

u3_x, u3_y = 80.0, 68.0
u3_lx, u3_rx = u3_x - 6.35, u3_x + 6.35

j1_x, j1_y = 118.0, 58.0

# BLOQUEAR TODOS OS 30 PINOS DO ESP32 (ativos e não ativos)
for i in range(15):
    py = u1_y - 7*2.54 + i*2.54
    router.block_circle(u1_lx, py, r=1.2, clearance=0.4) # fileira esquerda
    router.block_circle(u1_rx, py, r=1.2, clearance=0.4) # fileira direita

# BLOQUEAR TODOS OS 12 PINOS DO PCM5102
for i in range(6):
    py_l = u2_y - 2.5*2.54 + i*2.54
    router.block_circle(u2_lx, py_l, r=1.2, clearance=0.4)
for i in range(7):
    py_r = u2_y - 3.0*2.54 + i*2.54
    router.block_circle(u2_rx, py_r, r=1.2, clearance=0.4)

# BLOQUEAR TODOS OS 12 PINOS DO LEVEL CONVERTER
for i in range(6):
    py = u3_y - 2.5*2.54 + i*2.54
    router.block_circle(u3_lx, py, r=1.2, clearance=0.4)
    router.block_circle(u3_rx, py, r=1.2, clearance=0.4)

# BLOQUEAR TODOS OS 9 PINOS DO BORNIER J1 (pads de 3.2mm -> r=1.6)
for i in range(9):
    py = j1_y - 4*5.08 + i*5.08
    router.block_circle(j1_x, py, r=1.7, clearance=0.5)

# Bloquear R1, C1, R2, C2
for px, py in [(16.0, 52.0), (16.0, 56.0), (18.0, 48.0), (18.0, 72.0), (16.0, 64.0), (16.0, 68.0)]:
    router.block_circle(px, py, r=1.2, clearance=0.4)

print("Todos os pinos físicos foram bloqueados como obstáculos com sucesso!")
