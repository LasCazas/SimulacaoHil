"""Visualizador e Auto-Mapeador 2D de Telemetria da ECU — IF Betim Racing
Exibe mapas bidimensionais coloridos (Heatmap) com estilo Motorsport (TunerStudio / MoTeC):
- Injeção: Retorno do pulso real do bico injetor (µs) lido no pino 4
- Ignição: Ponto de avanço da vela (° APDC / delay) lido no pino 5
- Eficiência Volumétrica (VE %) estimada
- Cursor de rastreamento em tempo real (bolinha e mira neon móvel)
- Auto-preenchimento (Auto-Tune / Learning) acumulativo em malha fechada
"""

import csv
import math
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Cores tema Dark Motorsport
BG_CANVAS = "#0d1117"
BG_PANEL = "#161b22"
BG_BORDER = "#30363d"
COLOR_ACCENT = "#00e5ff"  # Neon Cyan
COLOR_TEXT = "#e6edf3"
COLOR_TEXT_DIM = "#8b949e"

# Eixos padronizados para calibração de motos esportivas (KTM Duke 390 / Hornet 600)
RPM_BINS = [1200, 1800, 2600, 3600, 4800, 6200, 7500, 8800, 10000, 11500]
MAP_BINS = [105, 95, 85, 75, 65, 55, 45, 35, 25]  # De WOT até vácuo de desaceleração


def interpolate_color(val, vmin, vmax):
    """Gera um gradiente continuo Motorsport (Deep Blue -> Cyan -> Green -> Amber -> Red)."""
    if vmax <= vmin:
        norm = 0.5
    else:
        norm = max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))

    stops = [
        (0.00, (13, 71, 161)),    # Azul profundo #0d47a1
        (0.25, (0, 184, 212)),    # Ciano vibrante #00b8d4
        (0.50, (0, 200, 83)),     # Verde corrida #00c853
        (0.75, (255, 214, 0)),    # Amarelo/Âmbar #ffd600
        (1.00, (255, 23, 68)),    # Vermelho corrida #ff1744
    ]

    for i in range(len(stops) - 1):
        s0, c0 = stops[i]
        s1, c1 = stops[i + 1]
        if s0 <= norm <= s1:
            ratio = (norm - s0) / (s1 - s0)
            r = int(c0[0] + (c1[0] - c0[0]) * ratio)
            g = int(c0[1] + (c1[1] - c0[1]) * ratio)
            b = int(c0[2] + (c1[2] - c0[2]) * ratio)
            return f"#{r:02x}{g:02x}{b:02x}"

    return "#ff1744"


class ECUMapWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🗺️ Mapa Dinâmico de Telemetria da ECU — Injeção & Ignição")
        self.geometry("980x680")
        self.minsize(860, 560)
        self.configure(bg=BG_PANEL)

        self.current_mode = "inj"  # 'inj', 'ign', 've'
        self.auto_learn = True

        # Ponto de operação atual
        self.cur_rpm = 1400.0
        self.cur_map = 38.0
        self.cur_inj = 2400.0
        self.cur_ign = 12.0
        self.cur_ve = 52.0
        self.is_hw_live = False
        self.last_update_t = time.time()

        # Célula selecionada pelo usuário para inspeção
        self.selected_cell = (len(MAP_BINS) - 2, 0)

        # Inicializa matrizes de dados (MAP x RPM)
        self.nrows = len(MAP_BINS)
        self.ncols = len(RPM_BINS)

        self.grid_inj = [[0.0 for _ in range(self.ncols)] for _ in range(self.nrows)]
        self.grid_ign = [[0.0 for _ in range(self.ncols)] for _ in range(self.nrows)]
        self.grid_ve = [[0.0 for _ in range(self.ncols)] for _ in range(self.nrows)]
        self.grid_hits = [[0 for _ in range(self.ncols)] for _ in range(self.nrows)]

        # Preenche com os mapas base calculados
        self.reset_to_base_maps()

        self._build_ui()
        self._redraw_grid()
        self._update_loop()

    def reset_to_base_maps(self):
        """Inicializa as matrizes com valores calibrados da física da Duke 390 / Speeduino."""
        for r_idx, map_kpa in enumerate(MAP_BINS):
            load_factor = (map_kpa - 25.0) / 80.0  # 0.0 (vácuo) a 1.0 (WOT)
            load_factor = max(0.05, min(1.0, load_factor))

            for c_idx, rpm in enumerate(RPM_BINS):
                rpm_norm = (rpm - 1000.0) / 10500.0

                # Eficiência Volumétrica (%)
                # Pico de torque ao redor de 7000-8000 RPM
                ve_peak_factor = math.exp(-((rpm - 7500.0) / 3800.0) ** 2)
                ve = 45.0 + 40.0 * load_factor + 15.0 * ve_peak_factor * load_factor
                self.grid_ve[r_idx][c_idx] = round(max(30.0, min(105.0, ve)), 1)

                # Tempo de Injeção (µs)
                # Escala com RPM e VE * Carga
                inj_us = 1600.0 + (ve / 100.0) * (map_kpa / 101.3) * 7800.0
                self.grid_inj[r_idx][c_idx] = round(max(1400.0, min(12000.0, inj_us)))

                # Ponto de Ignição (° APDC)
                # Mais avanço em média carga/alto giro, menos avanço em WOT e marcha lenta
                ign_deg = 10.0 + 20.0 * rpm_norm - 8.0 * load_factor + (8.0 if 0.3 < load_factor < 0.7 else 0.0)
                self.grid_ign[r_idx][c_idx] = round(max(5.0, min(38.0, ign_deg)), 1)

                self.grid_hits[r_idx][c_idx] = 0

    def _build_ui(self):
        # 1. Barra superior: Título e Status de Telemetria
        top_bar = tk.Frame(self, bg=BG_PANEL, padx=12, pady=8)
        top_bar.pack(fill="x")

        # Título
        title_box = tk.Frame(top_bar, bg=BG_PANEL)
        title_box.pack(side="left")
        tk.Label(
            title_box,
            text="MAPA BIDIMENSIONAL DA ECU",
            bg=BG_PANEL,
            fg=COLOR_TEXT,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")
        self.lbl_src_status = tk.Label(
            title_box,
            text="● AGUARDANDO DADOS",
            bg=BG_PANEL,
            fg="#ffa726",
            font=("Consolas", 9, "bold"),
        )
        self.lbl_src_status.pack(anchor="w")

        # HUD com Leituras em Tempo Real
        live_hud = tk.Frame(top_bar, bg="#0d1117", padx=12, pady=4, highlightthickness=1, highlightbackground=BG_BORDER)
        live_hud.pack(side="right")

        self.lbl_live_rpm = tk.Label(live_hud, text="1400 RPM", bg="#0d1117", fg="#ffffff", font=("Consolas", 11, "bold"))
        self.lbl_live_rpm.pack(side="left", padx=8)

        self.lbl_live_map = tk.Label(live_hud, text="38.0 kPa", bg="#0d1117", fg="#4dd0e1", font=("Consolas", 11, "bold"))
        self.lbl_live_map.pack(side="left", padx=8)

        self.lbl_live_inj = tk.Label(live_hud, text="Inj: 2400 µs", bg="#0d1117", fg="#00e676", font=("Consolas", 11, "bold"))
        self.lbl_live_inj.pack(side="left", padx=8)

        self.lbl_live_ign = tk.Label(live_hud, text="Vela: 12.0°", bg="#0d1117", fg="#ffd600", font=("Consolas", 11, "bold"))
        self.lbl_live_ign.pack(side="left", padx=8)

        # 2. Barra de Seleção de Mapas e Ações
        tab_bar = tk.Frame(self, bg=BG_PANEL, padx=12, pady=4)
        tab_bar.pack(fill="x")

        btn_style = {"font": ("Segoe UI", 9, "bold"), "relief": "flat", "padx": 10, "pady": 4, "cursor": "hand2"}

        self.btn_tab_inj = tk.Button(
            tab_bar,
            text="🛢️ Retorno Bico Injetor (µs)",
            bg="#1f6feb",
            fg="white",
            command=lambda: self._set_mode("inj"),
            **btn_style,
        )
        self.btn_tab_inj.pack(side="left", padx=(0, 4))

        self.btn_tab_ign = tk.Button(
            tab_bar,
            text="⚡ Retorno Ignição/Vela (° APDC)",
            bg="#21262d",
            fg=COLOR_TEXT,
            command=lambda: self._set_mode("ign"),
            **btn_style,
        )
        self.btn_tab_ign.pack(side="left", padx=4)

        self.btn_tab_ve = tk.Button(
            tab_bar,
            text="📈 Eficiência Volumétrica (VE %)",
            bg="#21262d",
            fg=COLOR_TEXT,
            command=lambda: self._set_mode("ve"),
            **btn_style,
        )
        self.btn_tab_ve.pack(side="left", padx=4)

        # Botão Auto-Learn
        self.btn_learn = tk.Button(
            tab_bar,
            text="🟢 Auto-Preenchimento: ATIVO",
            bg="#238636",
            fg="white",
            command=self._toggle_learning,
            **btn_style,
        )
        self.btn_learn.pack(side="right", padx=(6, 0))

        # Botão Reset
        tk.Button(
            tab_bar,
            text="🔄 Limpar Aprendizado",
            bg="#21262d",
            fg=COLOR_TEXT,
            command=self._clear_learning,
            **btn_style,
        ).pack(side="right", padx=4)

        # Botão Restaurar Base
        tk.Button(
            tab_bar,
            text="📋 Restaurar Mapa Base",
            bg="#21262d",
            fg=COLOR_TEXT,
            command=self._restore_base,
            **btn_style,
        ).pack(side="right", padx=4)

        # Botão Exportar CSV
        tk.Button(
            tab_bar,
            text="💾 Exportar CSV",
            bg="#21262d",
            fg=COLOR_TEXT,
            command=self._export_csv,
            **btn_style,
        ).pack(side="right", padx=4)

        # 3. Área Central: Canvas Interativo do Heatmap
        canvas_frame = tk.Frame(self, bg=BG_CANVAS, padx=8, pady=8)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg=BG_CANVAS, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw_grid())
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # 4. Rodapé Informativo e Inspetor de Célula
        footer = tk.Frame(self, bg=BG_PANEL, padx=12, pady=6)
        footer.pack(fill="x")

        self.lbl_cell_info = tk.Label(
            footer,
            text="Célula selecionada: [MAP 35 kPa, 1200 RPM] — Inj: 2400 µs | Ignição: 12.0° | VE: 52% | Amostras: 0",
            bg=BG_PANEL,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9),
        )
        self.lbl_cell_info.pack(side="left")

        # Botões de ajuste fino da célula selecionada (+ / -)
        tune_box = tk.Frame(footer, bg=BG_PANEL)
        tune_box.pack(side="right")
        tk.Label(tune_box, text="Ajuste fino célula:", bg=BG_PANEL, fg=COLOR_TEXT_DIM, font=("Segoe UI", 8)).pack(
            side="left", padx=4
        )
        tk.Button(
            tune_box,
            text="-5%",
            bg="#21262d",
            fg=COLOR_TEXT,
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            command=lambda: self._nudge_selected(-0.05),
        ).pack(side="left", padx=2)
        tk.Button(
            tune_box,
            text="-1%",
            bg="#21262d",
            fg=COLOR_TEXT,
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            command=lambda: self._nudge_selected(-0.01),
        ).pack(side="left", padx=2)
        tk.Button(
            tune_box,
            text="+1%",
            bg="#21262d",
            fg=COLOR_TEXT,
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            command=lambda: self._nudge_selected(+0.01),
        ).pack(side="left", padx=2)
        tk.Button(
            tune_box,
            text="+5%",
            bg="#21262d",
            fg=COLOR_TEXT,
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            command=lambda: self._nudge_selected(+0.05),
        ).pack(side="left", padx=2)

    def _set_mode(self, mode):
        self.current_mode = mode
        # Atualiza cores das abas
        self.btn_tab_inj.config(bg="#1f6feb" if mode == "inj" else "#21262d")
        self.btn_tab_ign.config(bg="#1f6feb" if mode == "ign" else "#21262d")
        self.btn_tab_ve.config(bg="#1f6feb" if mode == "ve" else "#21262d")
        self._redraw_grid()

    def _toggle_learning(self):
        self.auto_learn = not self.auto_learn
        if self.auto_learn:
            self.btn_learn.config(text="🟢 Auto-Preenchimento: ATIVO", bg="#238636")
        else:
            self.btn_learn.config(text="⏸️ Auto-Preenchimento: PAUSADO", bg="#8b949e")

    def _clear_learning(self):
        for r in range(self.nrows):
            for c in range(self.ncols):
                self.grid_hits[r][c] = 0
        self._redraw_grid()
        self._update_cell_info()

    def _restore_base(self):
        if messagebox.askyesno("Restaurar Mapa Base", "Deseja resetar todos os mapas para a curva base da moto?"):
            self.reset_to_base_maps()
            self._redraw_grid()
            self._update_cell_info()

    def _nudge_selected(self, delta_pct):
        r, c = self.selected_cell
        grid = self.grid_inj if self.current_mode == "inj" else (self.grid_ign if self.current_mode == "ign" else self.grid_ve)
        old_val = grid[r][c]
        new_val = old_val * (1.0 + delta_pct)
        if self.current_mode == "inj":
            grid[r][c] = round(max(500.0, min(16000.0, new_val)))
        elif self.current_mode == "ign":
            grid[r][c] = round(max(0.0, min(50.0, new_val)), 1)
        else:
            grid[r][c] = round(max(10.0, min(150.0, new_val)), 1)
        self._redraw_grid()
        self._update_cell_info()

    def _export_csv(self):
        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar Tabela da ECU",
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv"), ("All files", "*.*")],
            initialfile=f"mapa_ecu_{self.current_mode}.csv",
        )
        if not filename:
            return

        grid = self.grid_inj if self.current_mode == "inj" else (self.grid_ign if self.current_mode == "ign" else self.grid_ve)
        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["MAP_kPa \\ RPM"] + RPM_BINS)
                for r_idx, map_kpa in enumerate(MAP_BINS):
                    writer.writerow([map_kpa] + grid[r_idx])
            messagebox.showinfo("Exportar", f"Tabela exportada com sucesso!\n{filename}")
        except Exception as e:
            messagebox.showerror("Erro ao Exportar", str(e))

    def feed_telemetry(self, rpm, map_kpa, inj_us, ign_deg_or_age, is_hw_live):
        """Recebe novos pontos de telemetria da interface principal."""
        self.cur_rpm = float(rpm)
        self.cur_map = float(map_kpa)
        self.cur_inj = float(inj_us)
        self.is_hw_live = bool(is_hw_live)
        self.last_update_t = time.time()

        # Se ign_deg_or_age vier em ms de idade, estima o avanço equivalente
        if self.is_hw_live:
            # Ponto de ignição Speeduino: aproximação da centelha
            rpm_norm = max(0.0, min(1.0, (rpm - 1000.0) / 10500.0))
            load_factor = max(0.0, min(1.0, (map_kpa - 25.0) / 80.0))
            self.cur_ign = round(10.0 + 20.0 * rpm_norm - 6.0 * load_factor, 1)
        else:
            self.cur_ign = float(ign_deg_or_age)

        # VE estimado atual
        load_f = max(0.0, min(1.0, (map_kpa - 25.0) / 80.0))
        ve_peak = math.exp(-((rpm - 7500.0) / 3800.0) ** 2)
        self.cur_ve = round(45.0 + 40.0 * load_f + 15.0 * ve_peak * load_f, 1)

        # Auto-aprendizado (Auto-tune / Learning)
        if self.auto_learn and rpm >= 800 and map_kpa >= 20:
            self._apply_learning(self.cur_rpm, self.cur_map, self.cur_inj, self.cur_ign, self.cur_ve)

    def _find_closest_cell(self, rpm, map_kpa):
        """Encontra a célula (r_idx, c_idx) mais próxima das coordenadas atuais."""
        c_idx = min(range(self.ncols), key=lambda i: abs(RPM_BINS[i] - rpm))
        r_idx = min(range(self.nrows), key=lambda i: abs(MAP_BINS[i] - map_kpa))
        return r_idx, c_idx

    def _apply_learning(self, rpm, map_kpa, inj_us, ign_deg, ve_val):
        r_idx, c_idx = self._find_closest_cell(rpm, map_kpa)
        # Filtro de média móvel exponencial (EMA) para suavizar
        hits = self.grid_hits[r_idx][c_idx]
        alpha = 0.25 if hits < 15 else 0.10

        if inj_us > 100:  # Ignora quando cortado por limitador
            self.grid_inj[r_idx][c_idx] = round(self.grid_inj[r_idx][c_idx] * (1 - alpha) + inj_us * alpha)
        self.grid_ign[r_idx][c_idx] = round(self.grid_ign[r_idx][c_idx] * (1 - alpha) + ign_deg * alpha, 1)
        self.grid_ve[r_idx][c_idx] = round(self.grid_ve[r_idx][c_idx] * (1 - alpha) + ve_val * alpha, 1)

        self.grid_hits[r_idx][c_idx] += 1

    def _on_canvas_click(self, event):
        coords = getattr(self, "_cell_coords", {})
        for (r, c), (x0, y0, x1, y1) in coords.items():
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self.selected_cell = (r, c)
                self._redraw_grid()
                self._update_cell_info()
                break

    def _update_cell_info(self):
        r, c = self.selected_cell
        map_val = MAP_BINS[r]
        rpm_val = RPM_BINS[c]
        inj = self.grid_inj[r][c]
        ign = self.grid_ign[r][c]
        ve = self.grid_ve[r][c]
        hits = self.grid_hits[r][c]
        self.lbl_cell_info.config(
            text=(
                f"Célula selecionada: [MAP {map_val} kPa, {rpm_val} RPM] — "
                f"Inj: {inj:.0f} µs | Ignição: {ign:.1f}° | VE: {ve:.1f}% | "
                f"Amostras aprendidas: {hits}"
            )
        )

    def _redraw_grid(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 100 or h < 100:
            return

        # Margens para cabeçalhos de eixos
        left_margin = 75
        top_margin = 35
        right_margin = 25
        bottom_margin = 35

        grid_w = w - left_margin - right_margin
        grid_h = h - top_margin - bottom_margin

        col_w = grid_w / self.ncols
        row_h = grid_h / self.nrows

        # Seleciona matriz e limites de escala
        if self.current_mode == "inj":
            grid = self.grid_inj
            vmin, vmax = 1800.0, 9500.0
            unit = "µs"
            fmt = "{:.0f}"
        elif self.current_mode == "ign":
            grid = self.grid_ign
            vmin, vmax = 8.0, 36.0
            unit = "°"
            fmt = "{:.1f}"
        else:
            grid = self.grid_ve
            vmin, vmax = 40.0, 105.0
            unit = "%"
            fmt = "{:.1f}"

        # Cabeçalho superior: Eixo RPM
        c.create_text(
            left_margin + grid_w / 2,
            12,
            text="ROTAÇÃO DO MOTOR (RPM)",
            fill=COLOR_TEXT_DIM,
            font=("Segoe UI", 9, "bold"),
        )
        # Cabeçalho lateral: Eixo MAP (kPa)
        c.create_text(
            35,
            top_margin + grid_h / 2,
            text="PRESSÃO\nMAP (kPa)",
            fill=COLOR_TEXT_DIM,
            font=("Segoe UI", 8, "bold"),
            justify="center",
        )

        self._cell_coords = {}
        active_r, active_c = self._find_closest_cell(self.cur_rpm, self.cur_map)

        # 1. Desenha células da tabela
        for r in range(self.nrows):
            y0 = top_margin + r * row_h
            y1 = y0 + row_h

            # Rótulo da linha (MAP kPa)
            c.create_text(
                left_margin - 8,
                (y0 + y1) / 2,
                text=f"{MAP_BINS[r]}",
                anchor="e",
                fill="#80cbc4",
                font=("Consolas", 9, "bold"),
            )

            for col in range(self.ncols):
                x0 = left_margin + col * col_w
                x1 = x0 + col_w
                self._cell_coords[(r, col)] = (x0, y0, x1, y1)

                val = grid[r][col]
                color = interpolate_color(val, vmin, vmax)
                hits = self.grid_hits[r][col]

                # Fundo da célula
                c.create_rectangle(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill=color, outline="#1f2937", width=1)

                # Destaque de célula selecionada pelo clique do mouse
                if (r, col) == self.selected_cell:
                    c.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2, outline="#ffffff", width=2)

                # Destaque da célula ativa da telemetria
                if (r, col) == (active_r, active_c):
                    c.create_rectangle(x0 + 1, y0 + 1, x1 - 1, y1 - 1, outline=COLOR_ACCENT, width=3)

                # Marca d'água / badge de aprendizado (se a célula recebeu dados reais)
                if hits > 0:
                    badge_col = "#ffffff" if hits > 15 else "#a7ffeb"
                    c.create_text(x1 - 5, y0 + 7, text="✓", fill=badge_col, font=("Segoe UI", 7, "bold"), anchor="e")

                # Valor numérico da célula
                txt = fmt.format(val)
                # Contraste de cor de fonte
                c.create_text(
                    (x0 + x1) / 2,
                    (y0 + y1) / 2,
                    text=txt,
                    fill="#ffffff",
                    font=("Consolas", 10, "bold"),
                )

        # Rótulos das colunas (RPM) no rodapé do grid
        for col in range(self.ncols):
            x0 = left_margin + col * col_w
            x1 = x0 + col_w
            c.create_text(
                (x0 + x1) / 2,
                top_margin + grid_h + 14,
                text=f"{RPM_BINS[col]}",
                fill="#80cbc4",
                font=("Consolas", 9, "bold"),
            )

        # 2. Desenha o cursor contínuo em tempo real (Bolinha / Mira Holográfica)
        # Interpolação suave de coordenadas no canvas
        min_rpm, max_rpm = RPM_BINS[0], RPM_BINS[-1]
        clamped_rpm = max(min_rpm, min(max_rpm, self.cur_rpm))
        norm_x = (clamped_rpm - min_rpm) / (max_rpm - min_rpm)
        cursor_x = left_margin + col_w * 0.5 + norm_x * (grid_w - col_w)

        # MAP vai de 105 (topo, row 0) até 25 (base, row max)
        min_map, max_map = MAP_BINS[-1], MAP_BINS[0]
        clamped_map = max(min_map, min(max_map, self.cur_map))
        norm_y = (max_map - clamped_map) / (max_map - min_map)  # Invertido: 105 kPa fica no topo
        cursor_y = top_margin + row_h * 0.5 + norm_y * (grid_h - row_h)

        # Anel externo pulsante / mira
        r_outer = 10
        c.create_oval(
            cursor_x - r_outer,
            cursor_y - r_outer,
            cursor_x + r_outer,
            cursor_y + r_outer,
            outline=COLOR_ACCENT,
            width=2,
        )
        # Linhas de mira cruzada
        c.create_line(cursor_x - 14, cursor_y, cursor_x - 6, cursor_y, fill=COLOR_ACCENT, width=2)
        c.create_line(cursor_x + 6, cursor_y, cursor_x + 14, cursor_y, fill=COLOR_ACCENT, width=2)
        c.create_line(cursor_x, cursor_y - 14, cursor_x, cursor_y - 6, fill=COLOR_ACCENT, width=2)
        c.create_line(cursor_x, cursor_y + 6, cursor_x, cursor_y + 14, fill=COLOR_ACCENT, width=2)

        # Bolinha central incandescente
        r_inner = 4
        c.create_oval(
            cursor_x - r_inner,
            cursor_y - r_inner,
            cursor_x + r_inner,
            cursor_y + r_inner,
            fill="#ffffff",
            outline=COLOR_ACCENT,
            width=1,
        )

    def _update_loop(self):
        """Loop de atualização de taxa rápida para manter o mapa vivo."""
        if not self.winfo_exists():
            return

        # Atualiza status da fonte de telemetria
        dt = time.time() - self.last_update_t
        if self.is_hw_live and dt < 1.0:
            self.lbl_src_status.config(text="● ONLINE: FEEDBACK SPEEDUINO/ESP32 ATIVO", fg="#00e676")
        elif dt < 1.0:
            self.lbl_src_status.config(text="● SIMULADO: PRÉVIA LOCAL ATIVA", fg="#4dd0e1")
        else:
            self.lbl_src_status.config(text="○ AGUARDANDO DADOS DO MOTOR", fg="#ffa726")

        # Atualiza os valores do HUD do mapa
        self.lbl_live_rpm.config(text=f"{int(self.cur_rpm)} RPM")
        self.lbl_live_map.config(text=f"{self.cur_map:4.1f} kPa")
        self.lbl_live_inj.config(text=f"Inj: {int(self.cur_inj)} µs")
        self.lbl_live_ign.config(text=f"Vela: {self.cur_ign:4.1f}°")

        self._redraw_grid()
        self._update_cell_info()

        # Roda a 25 Hz para fluidez visual sem sobrecarga
        self.after(40, self._update_loop)
