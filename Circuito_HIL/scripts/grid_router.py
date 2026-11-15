"""Roteador Baseado em Grade (Lee / A*) com ZERO Cruzamentos Garantido.
Ultra-otimizado com lookups O(1) para roteamento instantâneo.
"""

import heapq
import math

class GridRouter:
    def __init__(self, width_mm=150.0, height_mm=100.0, resolution=0.5):
        self.res = resolution
        self.w = int(width_mm / resolution) + 1
        self.h = int(height_mm / resolution) + 1
        # grid: 0 = livre, >0 = ocupado por net_id
        self.grid = [[0 for _ in range(self.h)] for _ in range(self.w)]
        # obstacle_grid: cada célula contém o net_id do pad que a cobre (ou -1 se múltiplos)
        self.obstacle_grid = [[None for _ in range(self.h)] for _ in range(self.w)]

    def mm_to_grid(self, x, y):
        gx = max(0, min(self.w - 1, int(round(x / self.res))))
        gy = max(0, min(self.h - 1, int(round(y / self.res))))
        return gx, gy

    def grid_to_mm(self, gx, gy):
        return round(gx * self.res, 4), round(gy * self.res, 4)

    def add_pad_obstacle(self, x, y, net_id, radius_mm=1.0):
        gx, gy = self.mm_to_grid(x, y)
        r_grid = int(math.ceil((radius_mm + 0.5) / self.res))
        for dx in range(-r_grid, r_grid + 1):
            for dy in range(-r_grid, r_grid + 1):
                if dx*dx + dy*dy <= r_grid*r_grid:
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h:
                        curr = self.obstacle_grid[nx][ny]
                        if curr is None or curr == net_id:
                            self.obstacle_grid[nx][ny] = net_id
                        else:
                            self.obstacle_grid[nx][ny] = -1 # bloqueado para todos

    def route_net(self, start_xy, end_xy, net_id, clearance_mm=0.5):
        sx, sy = self.mm_to_grid(start_xy[0], start_xy[1])
        ex, ey = self.mm_to_grid(end_xy[0], end_xy[1])

        # A* Pathfinding
        # pq stores: (f, cost, x, y, parent)
        # We can reconstruct path with parent pointers to save memory and time
        pq = [(0, 0, sx, sy)]
        visited = {}
        parent = {}
        c_grid = max(1, int(math.ceil(clearance_mm / self.res)))

        found = False
        while pq:
            f, cost, x, y = heapq.heappop(pq)

            if (x, y) == (ex, ey):
                found = True
                break

            if (x, y) in visited and visited[(x, y)] <= cost:
                continue
            visited[(x, y)] = cost

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.w and 0 <= ny < self.h:
                    # 1. Checar colisão com outras trilhas
                    cell_net = self.grid[nx][ny]
                    if cell_net != 0 and cell_net != net_id:
                        continue
                    
                    # 2. Checar colisão com pads de outras redes
                    obs_net = self.obstacle_grid[nx][ny]
                    if obs_net is not None and obs_net != net_id:
                        continue

                    # Custo
                    h_dist = abs(nx - ex) + abs(ny - ey)
                    turn_penalty = 0
                    p = parent.get((x, y))
                    if p:
                        prev_dx = x - p[0]
                        prev_dy = y - p[1]
                        if (dx, dy) != (prev_dx, prev_dy):
                            turn_penalty = 2
                    nc = cost + 1 + turn_penalty
                    nf = nc + h_dist
                    if (nx, ny) not in visited or visited[(nx, ny)] > nc:
                        parent[(nx, ny)] = (x, y)
                        heapq.heappush(pq, (nf, nc, nx, ny))

        if not found:
            return None

        # Reconstruir caminho
        curr = (ex, ey)
        full_path = [curr]
        while curr != (sx, sy):
            curr = parent[curr]
            full_path.append(curr)
        full_path.reverse()

        # Marcar trilha no grid
        for px, py in full_path:
            for dx in range(-c_grid, c_grid + 1):
                for dy in range(-c_grid, c_grid + 1):
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h:
                        if self.grid[nx][ny] == 0:
                            self.grid[nx][ny] = net_id

        # Converter para mm simplificados
        mm_pts = [self.grid_to_mm(px, py) for px, py in full_path]
        return self.simplify_path(mm_pts)

    def simplify_path(self, pts):
        if len(pts) <= 2:
            return pts
        simplified = [pts[0]]
        for i in range(1, len(pts) - 1):
            x0, y0 = simplified[-1]
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            if (x0 == x1 == x2) or (y0 == y1 == y2):
                continue
            simplified.append((x1, y1))
        simplified.append(pts[-1])
        return simplified
