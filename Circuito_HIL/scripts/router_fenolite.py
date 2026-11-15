"""Roteador A* Face Simples (Single Layer / Bottom-Only) para a Bancada HIL.
Gera trilhas 100% na camada B.Cu sem nenhum cruzamento de trilha (zero crossing).
"""

import math
import heapq
import json

class GridRouter:
    def __init__(self, width_mm, height_mm, res=0.5):
        self.res = res
        self.w = int(width_mm / res)
        self.h = int(height_mm / res)
        # 0 = livre, >0 = ocupado por net_id
        self.grid = [[0 for _ in range(self.h)] for _ in range(self.w)]
        self.fixed_obstacles = [[False for _ in range(self.h)] for _ in range(self.w)]

    def to_grid(self, x, y):
        gx = int(round(x / self.res))
        gy = int(round(y / self.res))
        gx = max(0, min(self.w - 1, gx))
        gy = max(0, min(self.h - 1, gy))
        return gx, gy

    def to_coord(self, gx, gy):
        return gx * self.res, gy * self.res

    def block_rect(self, x1, y1, x2, y2, clearance=1.0):
        gx1, gy1 = self.to_grid(x1 - clearance, y1 - clearance)
        gx2, gy2 = self.to_grid(x2 + clearance, y2 + clearance)
        for x in range(gx1, gx2 + 1):
            for y in range(gy1, gy2 + 1):
                self.fixed_obstacles[x][y] = True

    def block_circle(self, cx, cy, r, clearance=0.8):
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

    def route_net(self, start_pos, end_pos, net_id, clearance=0.8):
        sx, sy = self.to_grid(*start_pos)
        ex, ey = self.to_grid(*end_pos)

        # A* algorithm
        # heuristic: manhattan distance
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

                # Custo de passo (1.0 para ortogonal, 1.414 para diagonal)
                step_cost = 1.0 if (dx == 0 or dy == 0) else 1.414

                # Verificar obstáculo fixo
                if self.fixed_obstacles[nx][ny] and (nx, ny) != (ex, ey):
                    continue

                # Verificar outra net
                grid_net = self.grid[nx][ny]
                if grid_net != 0 and grid_net != net_id and (nx, ny) != (ex, ey):
                    continue

                new_cost = cost_so_far[(cx, cy)] + step_cost
                if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                    cost_so_far[(nx, ny)] = new_cost
                    priority = new_cost + h(nx, ny) * 1.1
                    heapq.heappush(frontier, (priority, nx, ny))
                    came_from[(nx, ny)] = (cx, cy)

        if not found:
            return None

        # Reconstruir caminho
        curr = (ex, ey)
        path = []
        while curr in came_from:
            path.append(self.to_coord(*curr))
            curr = came_from[curr]
        path.append(self.to_coord(sx, sy))
        path.reverse()

        # Marcar caminho no grid com clearance
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

        # Simplificar caminho (remover pontos colineares)
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

print("GridRouter carregado com sucesso!")
