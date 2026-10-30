"""Interface HIL: suporta Logitech G29 real (pygame) OU Modo Simulado/Manual (sliders de 0 a 100%).
Envia "throttle,clutch,gear,brake\\n" ao ESP32 a 30 Hz, envia parametros de moto_duke390.json
("P,nome,valor\\n") ao conectar e exibe a telemetria retornada pelo ESP32 a 115200 bps.

pip install -r requirements.txt
"""
import json
import os
import time
import tkinter as tk
from tkinter import ttk

import pygame
import serial
import serial.tools.list_ports

# ---- Mapeamento padrao do G29 no Logitech G HUB (ajuste pela interface se necessario) ----
DEFAULT_AXES = {"volante": 0, "acelerador": 1, "freio": 2, "embreagem": 3}
# Cambio H (botoes tipicos do G29 no Windows/DirectInput). 7 = Re.
GEAR_BUTTONS = {12: 1, 13: 2, 14: 3, 15: 4, 16: 5, 17: 6, 18: 7}
PADDLE_UP, PADDLE_DOWN = 5, 4  # aletas: usadas se o cambio H nao estiver em marcha
SEND_HZ = 30

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOTO_FILE = os.path.join(BASE_DIR, "moto_duke390.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config_g29.json")
CONTROLS = ["volante", "acelerador", "freio", "embreagem"]


def axis_to_pct(v, invert):
    """Pedais G29: repouso = +1.0, pressionado = -1.0 (invert=True)."""
    p = (1 - v) / 2 if invert else (v + 1) / 2
    return max(0.0, min(1.0, p))


def gear_label(g):
    return "N" if g == 0 else ("R" if g == 7 else str(g))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HIL Simulador Dinâmico — G29 / Manual -> ESP32")
        self.geometry("620x650")
        self.minsize(590, 620)

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
        self.pct_labels = {}
        self.gear_btns = {}

        self.cfg = self._load_cfg()
        self.mode_var = tk.StringVar(value=self.cfg.get("mode", "g29"))

        self._build()
        self._update_mode_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._tick)

    # ---------- UI ----------
    def _build(self):
        # Barra superior: conexao Serial + status G29
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=(8, 4))
        ttk.Label(top, text="Porta COM:").pack(side="left")
        self.port = ttk.Combobox(top, width=10, values=self._ports())
        self.port.set(self.cfg.get("port", ""))
        self.port.pack(side="left", padx=4)
        ttk.Button(top, text="↻", width=3, command=lambda: self.port.config(values=self._ports())).pack(side="left")
        self.btn_con = ttk.Button(top, text="Conectar", command=self._toggle_serial)
        self.btn_con.pack(side="left", padx=6)
        self.lbl_js = ttk.Label(top, text="G29: não detectado")
        self.lbl_js.pack(side="right")

        # Seletor de Modo: Volante G29 vs. Simulado (Sliders)
        mode_box = ttk.LabelFrame(self, text="Modo de Controle")
        mode_box.pack(fill="x", padx=10, pady=4)
        ttk.Radiobutton(
            mode_box,
            text="Volante Real (Logitech G29)",
            value="g29",
            variable=self.mode_var,
            command=self._update_mode_ui,
        ).pack(side="left", padx=12, pady=4)
        ttk.Radiobutton(
            mode_box,
            text="Simulado na Interface (Barrinhas % / Manual)",
            value="manual",
            variable=self.mode_var,
            command=self._update_mode_ui,
        ).pack(side="left", padx=12, pady=4)

        # Container que alterna entre os controles do G29 e os Sliders manuais
        self.input_container = ttk.Frame(self)
        self.input_container.pack(fill="x", padx=10, pady=4)

        # --- Painel 1: Logitech G29 ---
        self.box_g29 = ttk.LabelFrame(self.input_container, text="Entradas do Logitech G29 (enviadas ao ESP32)")
        self.bars = {}
        for i, name in enumerate(CONTROLS):
            ttk.Label(self.box_g29, text=name.capitalize(), width=11).grid(row=i, column=0, sticky="w", padx=(6, 2))
            pb = ttk.Progressbar(self.box_g29, length=230, maximum=100)
            pb.grid(row=i, column=1, padx=4, pady=3)
            self.bars[name] = pb
            lbl_p = ttk.Label(self.box_g29, text="  0%", width=5, font=("Consolas", 9, "bold"))
            lbl_p.grid(row=i, column=2, padx=2)
            self.pct_labels[f"g29_{name}"] = lbl_p
            ttk.Label(self.box_g29, text="eixo").grid(row=i, column=3, padx=(6, 2))
            v = tk.IntVar(value=self.cfg.get("axes", {}).get(name, DEFAULT_AXES[name]))
            self.axis_vars[name] = v
            ttk.Spinbox(self.box_g29, from_=0, to=9, width=3, textvariable=v).grid(row=i, column=4)
            inv = tk.BooleanVar(value=self.cfg.get("invert", {}).get(name, True))
            self.inv_vars[name] = inv
            ttk.Checkbutton(self.box_g29, text="inv", variable=inv).grid(row=i, column=5, padx=(4, 6))

        self.lbl_raw = ttk.Label(self.box_g29, text="eixos brutos: -", font=("Consolas", 8))
        self.lbl_raw.grid(row=5, column=0, columnspan=6, sticky="w", padx=6, pady=(4, 0))
        self.lbl_btn = ttk.Label(self.box_g29, text="botoes: -", font=("Consolas", 8))
        self.lbl_btn.grid(row=6, column=0, columnspan=6, sticky="w", padx=6, pady=(0, 4))

        # --- Painel 2: Modo Simulado / Manual (Sliders) ---
        self.box_manual = ttk.LabelFrame(
            self.input_container, text="Modo Simulado — Ajuste Manual de Pedais e Marchas (0% a 100%)"
        )
        for i, name in enumerate(CONTROLS):
            default_val = 50.0 if name == "volante" else 0.0
            mv = tk.DoubleVar(value=default_val)
            self.manual_vars[name] = mv
            ttk.Label(self.box_manual, text=name.capitalize(), width=11).grid(row=i, column=0, sticky="w", padx=(6, 2))
            sc = ttk.Scale(
                self.box_manual,
                from_=0.0,
                to=100.0,
                orient="horizontal",
                length=280,
                variable=mv,
                command=lambda _val, n=name: self._round_manual(n),
            )
            sc.grid(row=i, column=1, padx=6, pady=4, sticky="ew")
            sp = ttk.Spinbox(
                self.box_manual,
                from_=0,
                to=100,
                increment=1,
                width=5,
                textvariable=mv,
                command=lambda n=name: self._round_manual(n),
            )
            sp.grid(row=i, column=2, padx=4)
            ttk.Label(self.box_manual, text="%").grid(row=i, column=3, sticky="w", padx=(0, 6))

        # Seletor de marchas clicavel + botao de zerar pedais no modo manual
        gear_row = ttk.Frame(self.box_manual)
        gear_row.grid(row=5, column=0, columnspan=4, sticky="ew", padx=6, pady=(6, 6))
        ttk.Label(gear_row, text="Marcha:").pack(side="left", padx=(0, 6))
        for g_code, g_txt in [(7, "R"), (0, "N"), (1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6")]:
            b = tk.Button(
                gear_row,
                text=g_txt,
                width=3,
                relief="raised",
                command=lambda g=g_code: self._set_manual_gear(g),
            )
            b.pack(side="left", padx=2)
            self.gear_btns[g_code] = b
        ttk.Button(gear_row, text="Zerar Pedais", command=self._zero_pedals).pack(side="right", padx=4)
        self._highlight_gear_btns()

        # Indicador central de Marcha + pacote TX
        self.lbl_gear = ttk.Label(self, text="Marcha: N", font=("Arial", 20, "bold"))
        self.lbl_gear.pack(pady=(4, 2))
        self.lbl_send = ttk.Label(self, text="TX: -", font=("Consolas", 10))
        self.lbl_send.pack()

        # Telemetria recebida do ESP32
        fb = ttk.LabelFrame(self, text="Telemetria da Planta HIL (ESP32)")
        fb.pack(fill="x", padx=10, pady=6)
        self.lbl_rpm = ttk.Label(fb, text="0 RPM", font=("Arial", 26, "bold"))
        self.lbl_rpm.pack(pady=(2, 0))
        self.pb_rpm = ttk.Progressbar(fb, length=540, maximum=11500)
        self.pb_rpm.pack(padx=10, pady=4)
        self.lbl_fb = ttk.Label(fb, text="-", font=("Consolas", 10), justify="center")
        self.lbl_fb.pack(pady=4)

        # Rodape de status + reenviar JSON
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=(2, 8))
        self.lbl_status = ttk.Label(bottom, text="Desconectado")
        self.lbl_status.pack(side="left")
        ttk.Button(bottom, text="Reenviar parâmetros (moto_duke390.json)", command=self._queue_params).pack(
            side="right"
        )

    def _round_manual(self, name):
        try:
            v = max(0.0, min(100.0, float(self.manual_vars[name].get())))
            self.manual_vars[name].set(round(v, 1))
        except tk.TclError:
            pass

    def _set_manual_gear(self, g):
        self.manual_gear = g
        self._highlight_gear_btns()

    def _highlight_gear_btns(self):
        for g_code, btn in self.gear_btns.items():
            active = g_code == self.manual_gear
            btn.config(
                bg="#1e88e5" if active else "SystemButtonFace",
                fg="white" if active else "black",
                font=("Arial", 9, "bold" if active else "normal"),
            )

    def _zero_pedals(self):
        for name in ("acelerador", "freio", "embreagem"):
            self.manual_vars[name].set(0.0)
        self.manual_vars["volante"].set(50.0)

    def _update_mode_ui(self):
        if self.mode_var.get() == "manual":
            self.box_g29.pack_forget()
            self.box_manual.pack(fill="x")
        else:
            self.box_manual.pack_forget()
            self.box_g29.pack(fill="x")

    def _load_cfg(self):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}

    def _on_close(self):
        cfg = {
            "port": self.port.get(),
            "mode": self.mode_var.get(),
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
        """Le moto_duke390.json e enfileira linhas P,nome,valor (enviadas aos poucos)."""
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
        self.param_t0 = time.time() + 2.0  # ESP32 reinicia ao abrir a porta serial
        self.lbl_status.config(text=f"Enviando {len(q)} parâmetros...")

    def _ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def _toggle_serial(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            self.btn_con.config(text="Conectar")
            self.lbl_status.config(text="Desconectado")
            return
        try:
            self.ser = serial.Serial(self.port.get(), 115200, timeout=0)
            self.btn_con.config(text="Desconectar")
            self.lbl_status.config(text=f"Conectado em {self.port.get()}")
            self._queue_params()
        except Exception as e:
            self.lbl_status.config(text=f"Erro: {e}")

    # ---------- Loop ----------
    def _find_js(self):
        if pygame.joystick.get_count() and self.js is None:
            self.js = pygame.joystick.Joystick(0)
            self.js.init()
            self.lbl_js.config(text=f"G29: {self.js.get_name()[:28]}")
        elif not pygame.joystick.get_count() and self.js is not None:
            self.js = None
            self.lbl_js.config(text="G29: não detectado")

    def _read_manual_values(self):
        def pct(name):
            try:
                return max(0.0, min(1.0, float(self.manual_vars[name].get()) / 100.0))
            except tk.TclError:
                return 0.0

        return pct("acelerador"), pct("embreagem"), pct("freio"), self.manual_gear

    def _read_g29_values(self):
        thr = clu = brk = 0.0
        gear = self.paddle_gear
        if self.js:
            n = self.js.get_numaxes()
            raw = [self.js.get_axis(i) for i in range(n)]
            self.lbl_raw.config(text="eixos brutos: " + " ".join(f"{i}:{v:+.2f}" for i, v in enumerate(raw)))
            vals = {}
            for name, var in self.axis_vars.items():
                a = var.get()
                v = raw[a] if a < n else 0.0
                vals[name] = (
                    axis_to_pct(v, self.inv_vars[name].get()) if name != "volante" else (1 - v) / 2
                    if self.inv_vars[name].get()
                    else (v + 1) / 2
                )
                pct100 = vals[name] * 100.0
                self.bars[name]["value"] = pct100
                self.pct_labels[f"g29_{name}"].config(text=f"{pct100:3.0f}%")
            thr, clu, brk = vals["acelerador"], vals["embreagem"], vals["freio"]

            nb = self.js.get_numbuttons()
            self.lbl_btn.config(
                text="botoes: " + (" ".join(str(b) for b in range(nb) if self.js.get_button(b)) or "-")
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
        return thr, clu, brk, gear

    def _tick(self):
        pygame.event.pump()
        self._find_js()

        if self.mode_var.get() == "manual":
            thr, clu, brk, gear = self._read_manual_values()
            mode_tag = "MANUAL"
        else:
            thr, clu, brk, gear = self._read_g29_values()
            mode_tag = "G29"

        self.lbl_gear.config(text=f"Marcha: {gear_label(gear)}   ({mode_tag})")

        pkt = f"{int(round(thr * 255))},{int(round(clu * 255))},{gear},{int(round(brk * 255))}\n"
        self.lbl_send.config(
            text=f"TX: {pkt.strip()}   |   TPS: {thr*100:4.1f}%   Emb: {clu*100:4.1f}%   Freio: {brk*100:4.1f}%"
        )
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
            except Exception as e:
                self.lbl_status.config(text=f"Erro serial: {e}")
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
                self.lbl_rpm.config(text=f"{r} RPM")
                self.pb_rpm["value"] = r
                self.lbl_fb.config(
                    text=(
                        f"Velocidade: {kmh/10:5.1f} km/h   |   VSS: {v:4d} Hz   |   "
                        f"Torque: {tq/10:4.1f} Nm   |   MAP: {mp/10:5.1f} kPa\n"
                        f"Injeção: {i} µs ({'ECU ok' if fb else 'sem pulso'})   |   "
                        f"Fator comb.: {ff/100:.2f}   |   Ignição há: {g} ms   |   Marcha ESP: {gear_label(gr)}"
                    )
                )
                break


if __name__ == "__main__":
    App().mainloop()
