"""Testador de Roteamento por Grade A* Estrito (Zero Cruzamentos, Zero Curtos).
"""

import math
import heapq

class SafeGridRouter:
    def __init__(self, width_mm, height_mm, res=0.4):
        self.res = res
        self.w = int(math.ceil(width_mm / res))
        self.h = int(math.ceil(height_mm / res))
        # 0 = livre, -1 = obstáculo fixo, >0 = net_id
        self.grid = [[0 for _ in range(self.h)] for _ in range(self.w)]
        self.pads = [] # lista de (x, y, r, net_id)

    def to_grid(self, x, y):
        gx = max(0, min(self.w - 1, int(round(x / self.res))))
        gy = max(0, min(self.h - 1, int(round(y / self.res))))
        return gx, gy

    def to_coord(self, gx, gy):
        return gx * self.res, gy * self.res

    def add_pad(self, x, y, r, net_id):
        self.pads.append((x, y, r, net_id))
        gx, gy = self.to_grid(x, y)
        rad_cells = int(math.ceil((r + 0.4) / self.res))
        for dx in range(-rad_cells, rad_cells + 1):
            for dy in range(-rad_cells, rad_cells + 1):
                if dx*dx + dy*dy <= rad_cells*rad_cells:
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h:
                        self.grid[nx][ny] = -1

    def clear_pad_for_net(self, x, y, r, net_id):
        gx, gy = self.to_grid(x, y)
        rad_cells = int(math.ceil((r + 0.4) / self.res))
        for dx in range(-rad_cells, rad_cells + 1):
            for dy in range(-rad_cells, rad_cells + 1):
                if dx*dx + dy*dy <= rad_cells*rad_cells:
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h:
                        # Se estava bloqueado, libera para este net
                        if self.grid[nx][ny] == -1 or self.grid[nx][ny] == 0:
                            self.grid[nx][ny] = net_id

    def route_two_points(self, p1, p2, net_id, track_width=0.8, clearance=0.4):
        sx, sy = self.to_grid(*p1)
        ex, ey = self.to_grid(*p2)

        def h(x, y):
            return math.hypot(x - ex, y - ey)

        frontier = []
        heapq.heappush(frontier, (0, sx, sy, 0, 0))
        came_from = {(sx, sy): None}
        cost_so_far = {(sx, sy): 0}

        found = False
        while frontier:
            _, cx, cy, ldx, ldy = heapq.heappop(frontier)

            if (cx, cy) == (ex, ey):
                found = True
                break

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < self.w and 0 <= ny < self.h):
                    continue

                cell_val = self.grid[nx][ny]
                # Permitido se livre (0) ou se pertencer à mesma rede (net_id)
                if cell_val != 0 and cell_val != net_id:
                    if (nx, ny) != (ex, ey):
                        continue

                step_cost = 1.0 if (dx == 0 or dy == 0) else 1.414
                bend_cost = 0.3 if (ldx, ldy) != (0, 0) and (dx, dy) != (ldx, ldy) else 0.0

                new_cost = cost_so_far[(cx, cy)] + step_cost + bend_cost
                if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                    cost_so_far[(nx, ny)] = new_cost
                    priority = new_cost + h(nx, ny) * 1.05
                    heapq.heappush(frontier, (priority, nx, ny, dx, dy))
                    came_from[(nx, ny)] = (cx, cy)

        if not found:
            return None

        curr = (ex, ey)
        path = []
        while curr:
            path.append(self.to_coord(*curr))
            curr = came_from[curr]
        path.reverse()

        # Marcar caminho com clearance
        rad_cells = int(math.ceil((track_width / 2.0 + clearance) / self.res))
        for px, py in path:
            gx, gy = self.to_grid(px, py)
            for dx in range(-rad_cells, rad_cells + 1):
                for dy in range(-rad_cells, rad_cells + 1):
                    if dx*dx + dy*dy <= rad_cells*rad_cells:
                        nx, ny = gx + dx, gy + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h:
                            if self.grid[nx][ny] == 0:
                                self.grid[nx][ny] = net_id

        return path
