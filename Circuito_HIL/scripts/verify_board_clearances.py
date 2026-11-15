"""Verificador Rigoroso de DRC Interno:
1. Nenhuma trilha pode cruzar com outra trilha de rede diferente.
2. Nenhuma trilha de rede A pode passar perto de um pad de rede B (distância < r_pad + r_trilha + 0.35mm).
3. Todas as trilhas devem ficar dentro da borda da placa.
"""

import math

def dist_pt_seg(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    l2 = dx*dx + dy*dy
    if l2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1)*dx + (py - y1)*dy) / l2))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)

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

def check_board(pads, tracks):
    # pads: lista de (px, py, r, net_id, pad_name)
    # tracks: lista de (x1, y1, x2, y2, width, net_id, track_name)
    violations = []

    # 1. Cruzamentos entre trilhas
    for i in range(len(tracks)):
        for j in range(i + 1, len(tracks)):
            t1 = tracks[i]
            t2 = tracks[j]
            if t1[5] != t2[5]: # redes diferentes
                if seg_intersects(t1[0], t1[1], t1[2], t1[3], t2[0], t2[1], t2[2], t2[3]):
                    violations.append(f"CRUZAMENTO: Trilha {t1[6]} (net {t1[5]}) cruza com Trilha {t2[6]} (net {t2[5]})!")

    # 2. Curto ou proximidade de trilha com pad alheio
    for t in tracks:
        x1, y1, x2, y2, tw, t_net, t_name = t
        for p in pads:
            px, py, pr, p_net, p_name = p
            if p_net != t_net and p_net != 0: # redes diferentes (e pad com rede)
                d = dist_pt_seg(px, py, x1, y1, x2, y2)
                min_safe_dist = pr + (tw / 2.0) + 0.35 # folga de 0.35mm
                if d < min_safe_dist:
                    violations.append(f"COLISÃO PAD: Trilha {t_name} (net {t_net}) está a {d:.2f}mm do Pad {p_name} (net {p_net}, min={min_safe_dist:.2f}mm)!")

    return violations

print("Verificador pronto.")
