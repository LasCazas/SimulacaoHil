"""Interface HIL F1-Style — IF Betim Racing:
- Volante oficial da equipe girando em tempo real (Assets/VOlante.jfif)
- Pedais verticais interativos estilo telemetria Formula 1 (clique/arraste no modo Simulado ou leia do G29)
- Indicador de marcha + 15 LEDs de Shift Light estilo Formula 1
- Sintetizador/Player de som "Berrador" em tempo real no PC (zero carga no ESP32)
- Envia "throttle,clutch,gear,brake\\n" (30 Hz) e parametros de moto_duke390.json a 115200 bps.
"""
import json
import os
import time
import tkinter as tk
from tkinter import ttk

import numpy as np
import pygame
import serial
import serial.tools.list_ports
from PIL import Image, ImageTk

from berrador_audio import EngineAudioPlayer

# ---- Mapeamento padrao do G29 no Logitech G HUB ----
DEFAULT_AXES = {"volante": 0, "acelerador": 1, "freio": 2, "embreagem": 3}
GEAR_BUTTONS = {12: 1, 13: 2, 14: 3, 15: 4, 16: 5, 17: 6, 18: 7}  # 7 = Re
PADDLE_UP, PADDLE_DOWN = 5, 4
SEND_HZ = 30

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOTO_FILE = os.path.join(BASE_DIR, "moto_duke390.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config_g29.json")
LOGO_FILE = os.path.join(BASE_DIR, "SimulacaoComG29_ComOPCEEsp", "images", "logo.png")
WHEEL_CLEAN = os.path.join(BASE_DIR, "Assets", "volante_clean.png")
WHEEL_JFIF = os.path.join(BASE_DIR, "Assets", "VOlante.jfif")
SOUNDS_DIR = os.path.join(BASE_DIR, "Assets", "sounds")

CONTROLS = ["volante", "acelerador", "freio", "embreagem"]
PEDAL_SPECS = [
    ("acelerador", "ACEL", "#00c853", "#b9f6ca"),
    ("freio", "FREIO", "#ff1744", "#ffcdd2"),
    ("embreagem", "EMB", "#00b0ff", "#b3e5fc"),
]

GREEN_RACING = "#157a34"
RED_RACING = "#d32f2f"
BG_APP = "#f2f5f3"
BG_DARK = "#121619"


def axis_to_pct(v, invert):
    p = (1 - v) / 2 if invert else (v + 1) / 2
    return max(0.0, min(1.0, p))


def gear_label(g):
    return "N" if g == 0 else ("R" if g == 7 else str(g))


class App(tk.Tk):
    WHEEL_VIEW_PX = 215
    AUDIO_DEFAULT_LABEL = "Padrão do Windows"

    def __init__(self):
        super().__init__()
        self.title("IF Betim Racing — Simulador Dinâmico HIL")
        self.geometry("760x830")
        self.minsize(730, 790)
        self.configure(bg=BG_APP)

        pygame.init()
        pygame.joystick.init()
        self.js = None
        self.ser = None
        self.paddle_gear = 0
        self.manual_gear = 0
        self.param_q = []
        self.param_t0 = 0
        self.prev_btn = {}
        self.axis_vars = {}
        self.inv_vars = {}
        self.manual_vars = {}
        self.gear_btns = {}
        self.logo_icon = None
        self.logo_header = None
        self.wheel_base_pil = None
        self.wheel_tk = None
        self.last_wheel_deg = None

        # Estado local p/ previa de som e Shift Light quando ESP32 esta desconectado
        self.local_rpm = 1400.0
        self.local_vel_kmh = 0.0
        self.esp_rpm = 0
        self.esp_last_rx = 0.0
        self.shift_blink = False

        self.cfg = self._load_cfg()
        self.mode_var = tk.StringVar(value=self.cfg.get("mode", "g29"))
        self.audio_on_var = tk.BooleanVar(value=self.cfg.get("audio_on", True))
        self.audio_prof_var = tk.StringVar(value=self.cfg.get("audio_profile", "berrador"))
        self.audio_vol_var = tk.DoubleVar(value=float(self.cfg.get("audio_volume", 55.0)))

        # Inicializa player de som no PC (Berrador)
        self.audio = EngineAudioPlayer(SOUNDS_DIR)
        self.audio.enabled = self.audio_on_var.get()
        self.audio.profile = self.audio_prof_var.get()
        self.audio.volume = self.audio_vol_var.get() / 100.0
        self.audio.start()

        self._setup_style()
        self._load_assets()
        self._build()
        self._update_mode_ui()
        self._render_wheel(0.0)
        self._draw_pedals(0.0, 0.0, 0.0)
        self._draw_shift_lights(0)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(80, self._tick)

    def _setup_style(self):
        st = ttk.Style(self)
        if "clam" in st.theme_names():
            st.theme_use("clam")
        st.configure(".", background=BG_APP, font=("Segoe UI", 9))
        st.configure("TFrame", background=BG_APP)
        st.configure("TLabel", background=BG_APP, foreground="#1e2428")
        st.configure("TLabelframe", background=BG_APP, bordercolor="#cfd8dc")
        st.configure("TLabelframe.Label", background=BG_APP, foreground=GREEN_RACING, font=("Segoe UI", 9, "bold"))
        st.configure("TRadiobutton", background=BG_APP, font=("Segoe UI", 9))
        st.configure("TCheckbutton", background=BG_APP, font=("Segoe UI", 9))
        st.configure("Accent.TButton", background=GREEN_RACING, foreground="white", font=("Segoe UI", 9, "bold"))
        st.map("Accent.TButton", background=[("active", "#106229")])

    def _load_assets(self):
        if os.path.exists(LOGO_FILE):
            try:
                self.logo_icon = tk.PhotoImage(file=LOGO_FILE)
                self.iconphoto(True, self.logo_icon)
                self.logo_header = self.logo_icon.subsample(4, 4)
            except Exception:
                self.logo_header = None

        # Carrega volante da equipe (usa volante_clean.png ou normaliza VOlante.jfif na hora)
        src = WHEEL_CLEAN if os.path.exists(WHEEL_CLEAN) else WHEEL_JFIF
        if os.path.exists(src):
            try:
                im = Image.open(src).convert("RGB")
                if src == WHEEL_JFIF:
                    im.thumbnail((420, 420), Image.Resampling.LANCZOS)
                    arr = np.array(im, dtype=np.float32)
                    arr = np.clip((arr - 8.0) * (255.0 / 235.0), 0, 255).astype(np.uint8)
                    im = Image.fromarray(arr, mode="RGB")
                    side = int(max(im.width, im.height) * 1.06)
                    sq = Image.new("RGB", (side, side), (255, 255, 255))
                    sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
                    im = sq
                self.wheel_base_pil = im.resize(
                    (self.WHEEL_VIEW_PX, self.WHEEL_VIEW_PX), Image.Resampling.LANCZOS
                )
            except Exception:
                self.wheel_base_pil = None

    # ---------- UI ----------
    def _build(self):
        # 1) Cabecalho Branco com Logo da Equipe
        header = tk.Frame(self, bg="#ffffff", padx=14, pady=7)
        header.pack(fill="x")
        if self.logo_header:
            tk.Label(header, image=self.logo_header, bg="#ffffff").pack(side="left", padx=(0, 12))
        title_box = tk.Frame(header, bg="#ffffff")
        title_box.pack(side="left", fill="y")
        tk.Label(
            title_box,
            text="IF BETIM RACING — SIMULADOR HIL",
            bg="#ffffff",
            fg=GREEN_RACING,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text="Speeduino 48-Way  ·  KTM Duke 390 (22-2)  ·  ESP32 DevKit V1",
            bg="#ffffff",
            fg="#546e7a",
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        self.lbl_js = tk.Label(
            header, text="G29: não detectado", bg="#eef3f0", fg="#37474f", font=("Segoe UI", 8, "bold"), padx=9, pady=4
        )
        self.lbl_js.pack(side="right")

        tk.Frame(self, bg=GREEN_RACING, height=3).pack(fill="x")

        # 2) Barra de Conexao Serial
        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=(7, 3))
        ttk.Label(top, text="Porta COM:", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.port = ttk.Combobox(top, width=9, values=self._ports())
        self.port.set(self.cfg.get("port", ""))
        self.port.pack(side="left", padx=4)
        ttk.Button(top, text="↻", width=3, command=lambda: self.port.config(values=self._ports())).pack(side="left")
        self.btn_con = ttk.Button(top, text="Conectar", style="Accent.TButton", command=self._toggle_serial)
        self.btn_con.pack(side="left", padx=6)

        # Controles de Som no PC (linha propria, com barra de volume bem visivel + Mudo)
        snd_frame = ttk.LabelFrame(self, text="Som do Motor (PC)")
        snd_frame.pack(fill="x", padx=12, pady=3)
        ttk.Checkbutton(
            snd_frame, text="Ativar som", variable=self.audio_on_var, command=self._sync_audio_cfg
        ).pack(side="left", padx=(8, 6), pady=3)
        cb_prof = ttk.Combobox(
            snd_frame,
            width=12,
            state="readonly",
            values=["berrador", "ktm390"],
            textvariable=self.audio_prof_var,
        )
        cb_prof.pack(side="left", padx=3)
        cb_prof.bind("<<ComboboxSelected>>", lambda _e: self._sync_audio_cfg())
        self.btn_mute = tk.Button(
            snd_frame,
            text="🔊",
            width=3,
            relief="flat",
            bg="#e4e9e6",
            font=("Segoe UI", 9),
            cursor="hand2",
            command=self._toggle_mute,
        )
        self.btn_mute.pack(side="left", padx=(12, 4))
        ttk.Label(snd_frame, text="Volume:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(2, 4))
        ttk.Scale(
            snd_frame,
            from_=0,
            to=100,
            orient="horizontal",
            length=150,
            variable=self.audio_vol_var,
            command=lambda _v: self._sync_audio_cfg(),
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.lbl_vol = ttk.Label(snd_frame, text="", width=5, font=("Consolas", 9, "bold"))
        self.lbl_vol.pack(side="left", padx=(0, 8))
        # Seletor de saida de audio (alto-falante / fone) + recarregar dispositivos
        ttk.Label(snd_frame, text="Saída:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(4, 2))
        self.cb_dev = ttk.Combobox(snd_frame, width=22, state="readonly")
        self.cb_dev.pack(side="left", padx=2)
        self.cb_dev.bind("<<ComboboxSelected>>", lambda _e: self._apply_audio_device())
        ttk.Button(snd_frame, text="↻", width=3, command=self._refresh_audio_devices).pack(
            side="left", padx=(2, 8)
        )
        self._audio_devs = []
        self._fill_audio_devices(self.cfg.get("audio_device", self.AUDIO_DEFAULT_LABEL))
        self._vol_before_mute = None
        self._sync_audio_cfg()

        # 3) Seletor de Modo: Volante G29 vs Simulado na Interface
        mode_box = ttk.LabelFrame(self, text="Modo de Controle")
        mode_box.pack(fill="x", padx=12, pady=3)
        ttk.Radiobutton(
            mode_box,
            text="Volante Real (Logitech G29)",
            value="g29",
            variable=self.mode_var,
            command=self._update_mode_ui,
        ).pack(side="left", padx=14, pady=3)
        ttk.Radiobutton(
            mode_box,
            text="Simulado na Interface (Arraste Volante / Pedais ou digite %)",
            value="manual",
            variable=self.mode_var,
            command=self._update_mode_ui,
        ).pack(side="left", padx=14, pady=3)

        # Inicializa variaveis manuais (0..100%, volante 50% = centro 0 graus)
        for name in CONTROLS:
            self.manual_vars[name] = tk.DoubleVar(value=50.0 if name == "volante" else 0.0)

        # 4) Painel Visual Central: Volante da Equipe (Esquerda) + Pedais F1 (Direita)
        stage = tk.Frame(self, bg=BG_APP)
        stage.pack(fill="x", padx=12, pady=4)

        # --- Card Esquerdo: Volante Oficial IF Betim Racing ---
        wheel_card = tk.Frame(
            stage, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#cfd8dc", padx=10, pady=8
        )
        wheel_card.pack(side="left", fill="both", padx=(0, 6))
        wh_top = tk.Frame(wheel_card, bg="#ffffff")
        wh_top.pack(fill="x")
        tk.Label(
            wh_top, text="VOLANTE FÓRMULA", bg="#ffffff", fg=GREEN_RACING, font=("Segoe UI", 9, "bold")
        ).pack(side="left")
        self.lbl_steer_deg = tk.Label(
            wh_top, text="  0.0°", bg="#eef3f0", fg="#1e2428", font=("Consolas", 9, "bold"), padx=6
        )
        self.lbl_steer_deg.pack(side="right")

        self.wheel_canvas = tk.Canvas(
            wheel_card,
            width=self.WHEEL_VIEW_PX,
            height=self.WHEEL_VIEW_PX,
            bg="#ffffff",
            highlightthickness=0,
            cursor="hand2",
        )
        self.wheel_canvas.pack(pady=2)
        self.wheel_img_id = self.wheel_canvas.create_image(
            self.WHEEL_VIEW_PX // 2, self.WHEEL_VIEW_PX // 2, image=None
        )
        # Arrastar no volante no modo manual gira o volante; botao direito centraliza!
        self.wheel_canvas.bind("<Button-1>", self._on_wheel_drag)
        self.wheel_canvas.bind("<B1-Motion>", self._on_wheel_drag)
        self.wheel_canvas.bind("<Button-3>", lambda _e: self.manual_vars["volante"].set(50.0))

        wh_ctrl = tk.Frame(wheel_card, bg="#ffffff")
        wh_ctrl.pack(fill="x", pady=(2, 0))
        self.wheel_scale = ttk.Scale(
            wh_ctrl,
            from_=0.0,
            to=100.0,
            orient="horizontal",
            length=165,
            variable=self.manual_vars["volante"],
        )
        self.wheel_scale.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.btn_center_wh = tk.Button(
            wh_ctrl,
            text="0°",
            bg="#e4e9e6",
            fg="#1e2428",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            padx=6,
            cursor="hand2",
            command=lambda: self.manual_vars["volante"].set(50.0),
        )
        self.btn_center_wh.pack(side="right")

        # --- Card Direito: Pedais Verticais Estilo Telemetria F1 + Seletor de Marchas ---
        pedals_card = tk.Frame(
            stage, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#cfd8dc", padx=12, pady=8
        )
        pedals_card.pack(side="left", fill="both", expand=True)

        pd_top = tk.Frame(pedals_card, bg="#ffffff")
        pd_top.pack(fill="x")
        tk.Label(
            pd_top,
            text="PEDAIS — TELEMETRIA F1 (clique/arraste nas barras no modo Simulado)",
            bg="#ffffff",
            fg=GREEN_RACING,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

        self.pedals_canvas = tk.Canvas(
            pedals_card, width=430, height=175, bg="#ffffff", highlightthickness=0, cursor="hand2"
        )
        self.pedals_canvas.pack(fill="x", pady=(4, 2))
        self.pedals_canvas.bind("<Button-1>", self._on_pedal_mouse)
        self.pedals_canvas.bind("<B1-Motion>", self._on_pedal_mouse)

        # Caixinhas numericas precisas (%) p/ cada pedal + Zerar
        spin_row = tk.Frame(pedals_card, bg="#ffffff")
        spin_row.pack(fill="x", pady=(2, 4))
        self.pedal_spins = []
        for key, short_lbl, color_hex, _bg_hex in PEDAL_SPECS:
            cell = tk.Frame(spin_row, bg="#ffffff")
            cell.pack(side="left", expand=True)
            tk.Label(cell, text=f"{short_lbl}:", bg="#ffffff", fg=color_hex, font=("Segoe UI", 8, "bold")).pack(
                side="left", padx=(0, 3)
            )
            sp = ttk.Spinbox(
                cell,
                from_=0,
                to=100,
                increment=1,
                width=5,
                textvariable=self.manual_vars[key],
                command=lambda k=key: self._clamp_manual(k),
            )
            sp.pack(side="left")
            tk.Label(cell, text="%", bg="#ffffff", fg="#546e7a", font=("Segoe UI", 8)).pack(side="left")
            self.pedal_spins.append(sp)

        # Linha de Marchas Manuais (R, N, 1..6) + Botao Soltar Pedais
        self.manual_gear_bar = tk.Frame(pedals_card, bg="#f7faf8", padx=6, pady=5)
        self.manual_gear_bar.pack(fill="x", pady=(2, 0))
        tk.Label(
            self.manual_gear_bar, text="Marcha:", bg="#f7faf8", fg="#1e2428", font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(0, 6))
        for g_code, g_txt in [(7, "R"), (0, "N"), (1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6")]:
            b = tk.Button(
                self.manual_gear_bar,
                text=g_txt,
                width=3,
                relief="flat",
                cursor="hand2",
                command=lambda g=g_code: self._set_manual_gear(g),
            )
            b.pack(side="left", padx=2)
            self.gear_btns[g_code] = b
        tk.Button(
            self.manual_gear_bar,
            text="Soltar Pedais",
            bg="#e4e9e6",
            fg="#1e2428",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            padx=8,
            cursor="hand2",
            command=self._zero_pedals,
        ).pack(side="right", padx=2)
        self._highlight_gear_btns()

        # 5) Faixa Compacta de Calibracao de Eixos G29 (exibida apenas no Modo G29 Real)
        self.box_g29_cfg = ttk.LabelFrame(self, text="Calibração dos Eixos Logitech G29")
        cfg_row = ttk.Frame(self.box_g29_cfg)
        cfg_row.pack(fill="x", padx=8, pady=3)
        for name in CONTROLS:
            blk = ttk.Frame(cfg_row)
            blk.pack(side="left", expand=True)
            ttk.Label(blk, text=f"{name.capitalize()}:", font=("Segoe UI", 8, "bold")).pack(side="left", padx=2)
            v = tk.IntVar(value=self.cfg.get("axes", {}).get(name, DEFAULT_AXES[name]))
            self.axis_vars[name] = v
            ttk.Spinbox(blk, from_=0, to=9, width=2, textvariable=v).pack(side="left")
            inv = tk.BooleanVar(value=self.cfg.get("invert", {}).get(name, True))
            self.inv_vars[name] = inv
            ttk.Checkbutton(blk, text="inv", variable=inv).pack(side="left", padx=(2, 6))

        raw_row = ttk.Frame(self.box_g29_cfg)
        raw_row.pack(fill="x", padx=8, pady=(0, 4))
        self.lbl_raw = ttk.Label(raw_row, text="eixos: -", font=("Consolas", 8), foreground="#546e7a")
        self.lbl_raw.pack(side="left")
        self.lbl_btn = ttk.Label(raw_row, text="botões: -", font=("Consolas", 8), foreground="#546e7a")
        self.lbl_btn.pack(side="right")

        # 6) Visor de Telemetria Estilo Formula 1 (Shift Lights + Marcha Central + RPM + Velocidade)
        dash = tk.Frame(self, bg=BG_DARK, padx=16, pady=10, highlightthickness=1, highlightbackground="#cfd8dc")
        dash.pack(fill="x", padx=12, pady=5)

        # Barra de 15 LEDs de Shift Light estilo Formula 1 (Verde -> Vermelho -> Azul/Roxo)
        self.shift_canvas = tk.Canvas(dash, width=680, height=22, bg=BG_DARK, highlightthickness=0)
        self.shift_canvas.pack(fill="x", pady=(0, 6))

        # Linha principal estilo HUD F1: RPM (esq) | MARCHA GIGANTE (centro) | KM/H (dir)
        hud_row = tk.Frame(dash, bg=BG_DARK)
        hud_row.pack(fill="x")

        left_hud = tk.Frame(hud_row, bg=BG_DARK, width=220)
        left_hud.pack(side="left", fill="both", expand=True)
        tk.Label(left_hud, text="ENGINE RPM", bg=BG_DARK, fg="#78909c", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.lbl_rpm = tk.Label(left_hud, text="1400 RPM", bg=BG_DARK, fg="#ffffff", font=("Consolas", 24, "bold"))
        self.lbl_rpm.pack(anchor="w")

        center_hud = tk.Frame(hud_row, bg="#1d2429", padx=26, pady=2, highlightthickness=1, highlightbackground="#37474f")
        center_hud.pack(side="left", padx=12)
        tk.Label(center_hud, text="GEAR", bg="#1d2429", fg="#90a4ae", font=("Segoe UI", 8, "bold")).pack()
        self.lbl_gear = tk.Label(center_hud, text="N", bg="#1d2429", fg="#ffca28", font=("Consolas", 34, "bold"))
        self.lbl_gear.pack()

        right_hud = tk.Frame(hud_row, bg=BG_DARK, width=220)
        right_hud.pack(side="left", fill="both", expand=True)
        tk.Label(right_hud, text="SPEED", bg=BG_DARK, fg="#78909c", font=("Segoe UI", 8, "bold")).pack(anchor="e")
        self.lbl_kmh = tk.Label(right_hud, text="0.0 km/h", bg=BG_DARK, fg="#4dd0e1", font=("Consolas", 24, "bold"))
        self.lbl_kmh.pack(anchor="e")

        tk.Frame(dash, bg="#263238", height=1).pack(fill="x", pady=6)

        self.lbl_send = tk.Label(dash, text="TX: -", bg=BG_DARK, fg="#90a4ae", font=("Consolas", 9))
        self.lbl_send.pack(anchor="w")
        self.lbl_fb = tk.Label(
            dash,
            text="Prévia local ativa — conecte na porta COM para telemetria em malha fechada do ESP32",
            bg=BG_DARK,
            fg="#cfd8dc",
            font=("Consolas", 9),
            justify="left",
        )
        self.lbl_fb.pack(anchor="w", pady=(2, 0))

        # 7) Rodape
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=12, pady=(2, 6))
        self.lbl_status = ttk.Label(bottom, text="Desconectado (prévia local + som ativos)", foreground="#546e7a")
        self.lbl_status.pack(side="left")
        ttk.Button(bottom, text="Reenviar parâmetros (moto_duke390.json)", command=self._queue_params).pack(
            side="right"
        )

    # ---------- Desenho do Volante, Pedais F1 e Shift Light ----------
    def _render_wheel(self, steer_deg):
        """Gira a imagem do volante da equipe em tempo real (-450 a +450 graus)."""
        self.lbl_steer_deg.config(text=f"{steer_deg:+5.0f}°")
        if self.wheel_base_pil is None:
            return
        if self.last_wheel_deg is not None and abs(steer_deg - self.last_wheel_deg) < 0.6:
            return
        self.last_wheel_deg = steer_deg
        # No Tkinter/PIL, angulo positivo em rotate() gira no sentido anti-horario (esquerda),
        # entao invertemos o sinal para virar p/ direita quando steer_deg > 0!
        rotated = self.wheel_base_pil.rotate(
            -steer_deg, resample=Image.Resampling.BICUBIC, fillcolor=(255, 255, 255)
        )
        self.wheel_tk = ImageTk.PhotoImage(rotated)
        self.wheel_canvas.itemconfig(self.wheel_img_id, image=self.wheel_tk)

    def _draw_pedals(self, thr, brk, clu):
        """Desenha as 3 barras verticais estilo telemetria de Formula 1."""
        c = self.pedals_canvas
        c.delete("all")
        w = max(360, c.winfo_width())
        h = 172
        vals = {"acelerador": thr, "freio": brk, "embreagem": clu}
        slot_w = w / 3.0
        bar_w = 54
        top_y, bot_y = 26, h - 26
        bar_h = bot_y - top_y
        self._pedal_hitboxes = {}

        for idx, (key, label, col_main, col_bg) in enumerate(PEDAL_SPECS):
            cx = slot_w * idx + slot_w / 2.0
            x0, x1 = cx - bar_w / 2.0, cx + bar_w / 2.0
            pct = max(0.0, min(1.0, vals[key]))
            self._pedal_hitboxes[key] = (x0 - 16, top_y, x1 + 16, bot_y)

            # Porcentagem no topo
            c.create_text(cx, 12, text=f"{pct*100:3.0f}%", fill="#1e2428", font=("Consolas", 11, "bold"))

            # Trilho de fundo da barra + linhas de grade (25%, 50%, 75%)
            c.create_rectangle(x0, top_y, x1, bot_y, fill="#eef2f0", outline="#cfd8dc", width=1)
            for mark in (0.25, 0.50, 0.75):
                my = bot_y - bar_h * mark
                c.create_line(x0 + 2, my, x1 - 2, my, fill="#dfe5e2", dash=(2, 2))

            # Preenchimento colorido estilo F1 Telemetry
            if pct > 0.005:
                fy = bot_y - bar_h * pct
                c.create_rectangle(x0 + 2, fy, x1 - 2, bot_y - 1, fill=col_bg, outline="")
                c.create_rectangle(x0 + 4, fy, x1 - 4, bot_y - 1, fill=col_main, outline="")
                c.create_rectangle(x0 + 2, fy, x1 - 2, min(bot_y, fy + 4), fill="#ffffff", outline="")

            # Sapata/base estilizada do pedal + rotulo
            c.create_rectangle(x0 - 4, bot_y + 3, x1 + 4, bot_y + 9, fill="#37474f", outline="")
            c.create_text(cx, bot_y + 18, text=label, fill="#263238", font=("Segoe UI", 9, "bold"))

    def _draw_shift_lights(self, rpm):
        """Desenha os 15 LEDs de Shift Light padrao Formula 1."""
        c = self.shift_canvas
        c.delete("all")
        w = max(500, c.winfo_width())
        n_leds = 15
        pad = 12
        spacing = (w - 2 * pad) / n_leds
        r = 7
        # Acende de 4500 RPM ate 10200 RPM; acima de 10200 pisca tudo!
        blink_off = False
        if rpm >= 10200:
            self.shift_blink = not self.shift_blink
            blink_off = self.shift_blink

        active_count = int(round((rpm - 4500.0) / (10200.0 - 4500.0) * n_leds))
        active_count = max(0, min(n_leds, active_count))

        for i in range(n_leds):
            cx = pad + spacing * (i + 0.5)
            cy = 11
            if i < 5:
                on_col, off_col = "#00e676", "#1c2b22"
            elif i < 10:
                on_col, off_col = "#ff1744", "#2e1c20"
            else:
                on_col, off_col = "#2979ff", "#1a2233"

            is_on = (i < active_count) and not blink_off
            c.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                fill=on_col if is_on else off_col,
                outline="#455a64" if not is_on else "#ffffff",
                width=1,
            )

    # ---------- Interacao de Mouse no Modo Simulado ----------
    def _on_wheel_drag(self, event):
        if self.mode_var.get() != "manual":
            return
        pct = max(0.0, min(100.0, (event.x / max(1, self.WHEEL_VIEW_PX)) * 100.0))
        self.manual_vars["volante"].set(round(pct, 1))

    def _on_pedal_mouse(self, event):
        if self.mode_var.get() != "manual":
            return
        for key, (x0, y0, x1, y1) in getattr(self, "_pedal_hitboxes", {}).items():
            if x0 <= event.x <= x1:
                pct = (y1 - event.y) / max(1.0, (y1 - y0)) * 100.0
                self.manual_vars[key].set(round(max(0.0, min(100.0, pct)), 1))
                break

    def _clamp_manual(self, key):
        try:
            v = max(0.0, min(100.0, float(self.manual_vars[key].get())))
            self.manual_vars[key].set(round(v, 1))
        except tk.TclError:
            pass

    def _sync_audio_cfg(self):
        self.audio.enabled = bool(self.audio_on_var.get())
        self.audio.profile = self.audio_prof_var.get()
        vol_pct = max(0.0, min(100.0, float(self.audio_vol_var.get())))
        self.audio.volume = vol_pct / 100.0
        if hasattr(self, "lbl_vol"):
            self.lbl_vol.config(text=f"{vol_pct:3.0f}%")
            self.btn_mute.config(text="🔇" if vol_pct <= 0.5 else "🔊")

    def _fill_audio_devices(self, wanted_label):
        """Preenche o combo de saidas e abre o stream no dispositivo desejado."""
        self._audio_devs = EngineAudioPlayer.list_output_devices()
        labels = [self.AUDIO_DEFAULT_LABEL] + [name for _i, name in self._audio_devs]
        self.cb_dev.config(values=labels)
        self.cb_dev.set(wanted_label if wanted_label in labels else self.AUDIO_DEFAULT_LABEL)
        self._apply_audio_device(reinit=False)

    def _apply_audio_device(self, reinit=True):
        label = self.cb_dev.get()
        dev = next((i for i, name in self._audio_devs if name == label), None)
        if reinit:
            self.audio.restart(dev)
        elif dev != self.audio.device:
            self.audio.stop()
            self.audio.device = dev
            self.audio.start()

    def _refresh_audio_devices(self):
        """Rele os dispositivos do Windows (ex: fone recem plugado) e reabre o audio."""
        current = self.cb_dev.get()
        self.audio.restart(None)  # reinicializa a PortAudio p/ enxergar o novo dispositivo
        self._fill_audio_devices(current)

    def _toggle_mute(self):
        """Mudo rapido: zera o volume e restaura o valor anterior no segundo clique."""
        cur = float(self.audio_vol_var.get())
        if cur > 0.5:
            self._vol_before_mute = cur
            self.audio_vol_var.set(0.0)
        else:
            self.audio_vol_var.set(self._vol_before_mute or 55.0)
        self._sync_audio_cfg()

    def _set_manual_gear(self, g):
        self.manual_gear = g
        self._highlight_gear_btns()

    def _highlight_gear_btns(self):
        for g_code, btn in self.gear_btns.items():
            active = g_code == self.manual_gear
            btn.config(
                bg=GREEN_RACING if active else "#e4e9e6",
                fg="white" if active else "#1e2428",
                font=("Segoe UI", 9, "bold" if active else "normal"),
            )

    def _zero_pedals(self):
        for name in ("acelerador", "freio", "embreagem"):
            self.manual_vars[name].set(0.0)
        self.manual_vars["volante"].set(50.0)

    def _update_mode_ui(self):
        is_manual = self.mode_var.get() == "manual"
        state_manual = "normal" if is_manual else "disabled"
        for sp in self.pedal_spins:
            sp.config(state=state_manual)
        if is_manual:
            self.wheel_scale.state(["!disabled"])
            self.btn_center_wh.config(state="normal")
            self.box_g29_cfg.pack_forget()
            self.manual_gear_bar.pack(fill="x", pady=(2, 0))
        else:
            self.wheel_scale.state(["disabled"])
            self.btn_center_wh.config(state="disabled")
            self.manual_gear_bar.pack_forget()
            self.box_g29_cfg.pack(fill="x", padx=12, pady=2, before=self.shift_canvas.master)

    def _load_cfg(self):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}

    def _on_close(self):
        self.audio.stop()
        cfg = {
            "port": self.port.get(),
            "mode": self.mode_var.get(),
            "audio_on": bool(self.audio_on_var.get()),
            "audio_profile": self.audio_prof_var.get(),
            "audio_volume": round(float(self.audio_vol_var.get()), 1),
            "audio_device": self.cb_dev.get(),
            "axes": {k: v.get() for k, v in self.axis_vars.items()},
            "invert": {k: v.get() for k, v in self.inv_vars.items()},
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
                json.dump(cfg, fh, indent=2)
        except Exception:
            pass
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.destroy()

    def _queue_params(self):
        try:
            with open(MOTO_FILE, encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception as e:
            self.lbl_status.config(text=f"Erro no JSON da moto: {e}")
            return
        q = [f"P,{k},{v['valor']}\n" for k, v in d.get("parametros", {}).items() if not k.startswith("_")]
        for i, g in enumerate(d.get("relacoes_marcha", {}).get("valor", []), 1):
            q.append(f"P,g{i},{g}\n")
        curve = d.get("curva_torque_wot", {}).get("valor", [])[:16]
        for i, (r, nm) in enumerate(curve):
            q += [f"P,tqr{i},{r}\n", f"P,tqn{i},{nm}\n"]
        q.append(f"P,tq_n,{len(curve)}\n")
        self.param_q = q
        self.param_t0 = time.time() + 2.0
        self.lbl_status.config(text=f"Enviando {len(q)} parâmetros...")

    def _ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def _toggle_serial(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            self.btn_con.config(text="Conectar")
            self.lbl_status.config(text="Desconectado (prévia local + som ativos)")
            return
        try:
            self.ser = serial.Serial(self.port.get(), 115200, timeout=0)
            self.btn_con.config(text="Desconectar")
            self.lbl_status.config(text=f"Conectado em {self.port.get()}")
            self._queue_params()
        except Exception as e:
            self.lbl_status.config(text=f"Erro: {e}")

    # ---------- Loop Principal ----------
    def _find_js(self):
        if pygame.joystick.get_count() and self.js is None:
            self.js = pygame.joystick.Joystick(0)
            self.js.init()
            self.lbl_js.config(text=f"G29: {self.js.get_name()[:24]}", bg="#e8f5e9", fg=GREEN_RACING)
        elif not pygame.joystick.get_count() and self.js is not None:
            self.js = None
            self.lbl_js.config(text="G29: não detectado", bg="#eef3f0", fg="#37474f")

    def _read_manual_values(self):
        def pct(name):
            try:
                return max(0.0, min(1.0, float(self.manual_vars[name].get()) / 100.0))
            except tk.TclError:
                return 0.5 if name == "volante" else 0.0

        steer_deg = (pct("volante") - 0.5) * 360.0  # -180 a +180 graus no modo manual
        return steer_deg, pct("acelerador"), pct("embreagem"), pct("freio"), self.manual_gear

    def _read_g29_values(self):
        steer_deg = 0.0
        thr = clu = brk = 0.0
        gear = self.paddle_gear
        if self.js:
            n = self.js.get_numaxes()
            raw = [self.js.get_axis(i) for i in range(n)]
            self.lbl_raw.config(text="eixos: " + " ".join(f"{i}:{v:+.2f}" for i, v in enumerate(raw)))
            vals = {}
            for name, var in self.axis_vars.items():
                a = var.get()
                v = raw[a] if a < n else 0.0
                if name == "volante":
                    signed = -v if self.inv_vars[name].get() else v
                    steer_deg = signed * 450.0  # G29 = 900 graus (-450 a +450)
                    vals[name] = (signed + 1.0) / 2.0
                else:
                    vals[name] = axis_to_pct(v, self.inv_vars[name].get())
            thr, clu, brk = vals["acelerador"], vals["embreagem"], vals["freio"]

            nb = self.js.get_numbuttons()
            self.lbl_btn.config(
                text="botões: " + (" ".join(str(b) for b in range(nb) if self.js.get_button(b)) or "-")
            )
            h = [g for b, g in GEAR_BUTTONS.items() if b < nb and self.js.get_button(b)]
            for b in (PADDLE_UP, PADDLE_DOWN):
                pressed = b < nb and self.js.get_button(b)
                if pressed and not self.prev_btn.get(b):
                    self.paddle_gear = (
                        min(6, self.paddle_gear + 1) if b == PADDLE_UP else max(0, self.paddle_gear - 1)
                    )
                self.prev_btn[b] = pressed
            gear = h[0] if h else self.paddle_gear
        return steer_deg, thr, clu, brk, gear

    def _step_local_preview(self, thr, clu, brk, gear):
        """Simula RPM e km/h localmente quando o ESP32 nao esta conectado (para testar som e HUD!)."""
        dt = 1.0 / SEND_HZ
        ratios = {1: 2.71, 2: 1.88, 3: 1.41, 4: 1.14, 5: 0.96, 6: 0.84, 7: -2.71}
        free_rev = (gear == 0) or (clu > 0.65)
        target = 1400.0 + 9100.0 * thr
        tau = 0.22 if free_rev else (0.55 + 0.18 * (gear if gear <= 6 else 1))
        self.local_rpm += (target - self.local_rpm) * min(1.0, dt / tau)
        if not free_rev and gear in ratios:
            # Velocidade acoplada + frenagem
            v_coupled = (self.local_rpm / ( abs(ratios[gear]) * 2.9 * 3.0 )) * (2 * 3.1416 * 0.30) * 3.6 / 60.0
            self.local_vel_kmh += (v_coupled - self.local_vel_kmh) * min(1.0, dt * 3.0)
        else:
            # Desaceleracao inercial suave no neutro / embreagem acionada
            drag = 1.8 + 38.0 * brk
            self.local_vel_kmh = max(0.0, self.local_vel_kmh - drag * dt)
        if brk > 0.05 and not free_rev:
            self.local_vel_kmh = max(0.0, self.local_vel_kmh - 32.0 * brk * dt)
            self.local_rpm = max(1250.0, self.local_rpm - 2400.0 * brk * dt)

    def _tick(self):
        pygame.event.pump()
        self._find_js()

        if self.mode_var.get() == "manual":
            steer_deg, thr, clu, brk, gear = self._read_manual_values()
        else:
            steer_deg, thr, clu, brk, gear = self._read_g29_values()

        # Atualiza animacao do Volante e dos Pedais F1
        self._render_wheel(steer_deg)
        self._draw_pedals(thr, brk, clu)

        g_txt = gear_label(gear)
        g_color = "#ffca28" if g_txt == "N" else (RED_RACING if g_txt == "R" else "#00e676")
        self.lbl_gear.config(text=g_txt, fg=g_color)

        pkt = f"{int(round(thr * 255))},{int(round(clu * 255))},{gear},{int(round(brk * 255))}\n"
        self.lbl_send.config(
            text=f"TX: {pkt.strip():<14} |  TPS: {thr*100:5.1f}%   Emb: {clu*100:5.1f}%   Freio: {brk*100:5.1f}%"
        )

        esp_live = False
        if self.ser:
            try:
                self.ser.write(pkt.encode())
                if self.param_q and time.time() >= self.param_t0:
                    for _ in range(3):
                        if self.param_q:
                            self.ser.write(self.param_q.pop(0).encode())
                    if not self.param_q:
                        self.lbl_status.config(text="Parâmetros da moto enviados com sucesso!")
                self._read_serial()
                esp_live = (time.time() - self.esp_last_rx) < 1.0
            except Exception as e:
                self.lbl_status.config(text=f"Erro serial: {e}")

        if esp_live:
            active_rpm = self.esp_rpm
        else:
            self._step_local_preview(thr, clu, brk, gear)
            active_rpm = int(self.local_rpm)
            self.lbl_rpm.config(
                text=f"{active_rpm} RPM", fg="#ff5252" if active_rpm >= 9800 else "#ffffff"
            )
            self.lbl_kmh.config(text=f"{self.local_vel_kmh:5.1f} km/h")

        self._draw_shift_lights(active_rpm)
        self.audio.update_state(active_rpm, thr)

        self.after(int(1000 / SEND_HZ), self._tick)

    def _read_serial(self):
        data = self.ser.read(512).decode(errors="ignore")
        if not data:
            return
        self._buf = getattr(self, "_buf", "") + data
        *lines, self._buf = self._buf.split("\n")
        for ln in reversed(lines):
            p = ln.strip().split(",")
            if len(p) == 10 and all(x.lstrip("-").isdigit() for x in p):
                r, v, i, g, gr, kmh, tq, mp, ff, fb = map(int, p)
                self.esp_rpm = r
                self.esp_last_rx = time.time()
                self.lbl_rpm.config(text=f"{r} RPM", fg="#ff5252" if r >= 9800 else "#ffffff")
                self.lbl_kmh.config(text=f"{kmh/10:5.1f} km/h")
                self.lbl_fb.config(
                    text=(
                        f"VSS: {v:4d} Hz   |   Torque: {tq/10:4.1f} Nm   |   MAP: {mp/10:5.1f} kPa   |   "
                        f"Marcha ESP: {gear_label(gr)}\n"
                        f"Injeção: {i} µs ({'ECU ok' if fb else 'sem pulso'})   |   "
                        f"Fator comb.: {ff/100:.2f}   |   Ignição há: {g} ms"
                    )
                )
                break


if __name__ == "__main__":
    App().mainloop()
