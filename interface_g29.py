"""Interface HIL: le o Logitech G29 (pygame) e envia "throttle,clutch,gear\\n" ao ESP32.
Recebe telemetria "rpm,vss_hz,inj_us,ign_age_ms,gear" do ESP.

pip install pygame pyserial
"""
import time
import tkinter as tk
from tkinter import ttk

import pygame
import serial
import serial.tools.list_ports

# ---- Mapeamento padrao do G29 (ajuste pela interface se necessario) ----
DEFAULT_AXES = {"volante": 0, "acelerador": 2, "freio": 3, "embreagem": 1}
# Cambio H (botoes tipicos do G29 no Windows/DirectInput). Ajuste se diferir.
GEAR_BUTTONS = {12: 1, 13: 2, 14: 3, 15: 4, 16: 5, 17: 6}
PADDLE_UP, PADDLE_DOWN = 5, 4  # aletas: usadas se o cambio H nao estiver em marcha
SEND_HZ = 30


def axis_to_pct(v, invert):
    """Pedais G29: repouso = +1.0, pressionado = -1.0 (invert=True)."""
    p = (1 - v) / 2 if invert else (v + 1) / 2
    return max(0.0, min(1.0, p))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HIL G29 -> ESP32")
        self.geometry("560x560")
        pygame.init()
        pygame.joystick.init()
        self.js = None
        self.ser = None
        self.paddle_gear = 0
        self.prev_btn = {}
        self.axis_vars = {}
        self.inv_vars = {}
        self.rx = {"rpm": 0, "vss": 0, "inj": 0, "ign": 0, "gear": 0}
        self._build()
        self.after(100, self._tick)

    # ---------- UI ----------
    def _build(self):
        top = ttk.Frame(self); top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="Porta:").pack(side="left")
        self.port = ttk.Combobox(top, width=10, values=self._ports()); self.port.pack(side="left", padx=4)
        ttk.Button(top, text="↻", width=3, command=lambda: self.port.config(values=self._ports())).pack(side="left")
        self.btn_con = ttk.Button(top, text="Conectar", command=self._toggle_serial); self.btn_con.pack(side="left", padx=6)
        self.lbl_js = ttk.Label(top, text="G29: -"); self.lbl_js.pack(side="right")

        box = ttk.LabelFrame(self, text="Entradas do G29 (enviadas ao ESP)"); box.pack(fill="x", padx=8, pady=4)
        self.bars = {}
        for i, name in enumerate(["volante", "acelerador", "freio", "embreagem"]):
            ttk.Label(box, text=name.capitalize(), width=11).grid(row=i, column=0, sticky="w")
            pb = ttk.Progressbar(box, length=220, maximum=100); pb.grid(row=i, column=1, padx=4, pady=2)
            self.bars[name] = pb
            ttk.Label(box, text="eixo").grid(row=i, column=2)
            v = tk.IntVar(value=DEFAULT_AXES[name]); self.axis_vars[name] = v
            ttk.Spinbox(box, from_=0, to=9, width=3, textvariable=v).grid(row=i, column=3)
            inv = tk.BooleanVar(value=name != "volante"); self.inv_vars[name] = inv
            ttk.Checkbutton(box, text="inv", variable=inv).grid(row=i, column=4)
        self.lbl_raw = ttk.Label(box, text="eixos brutos: -", font=("Consolas", 8)); self.lbl_raw.grid(row=5, column=0, columnspan=5, sticky="w")
        self.lbl_gear = ttk.Label(self, text="Marcha: N", font=("Arial", 20, "bold")); self.lbl_gear.pack(pady=4)
        self.lbl_send = ttk.Label(self, text="TX: -", font=("Consolas", 10)); self.lbl_send.pack()

        fb = ttk.LabelFrame(self, text="Telemetria do ESP32"); fb.pack(fill="x", padx=8, pady=6)
        self.lbl_rpm = ttk.Label(fb, text="0 RPM", font=("Arial", 26, "bold")); self.lbl_rpm.pack()
        self.pb_rpm = ttk.Progressbar(fb, length=480, maximum=11500); self.pb_rpm.pack(pady=2)
        self.lbl_fb = ttk.Label(fb, text="-", font=("Consolas", 11)); self.lbl_fb.pack(pady=4)
        self.lbl_status = ttk.Label(self, text="Desconectado"); self.lbl_status.pack(anchor="w", padx=8)

    def _ports(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def _toggle_serial(self):
        if self.ser:
            self.ser.close(); self.ser = None
            self.btn_con.config(text="Conectar"); self.lbl_status.config(text="Desconectado"); return
        try:
            self.ser = serial.Serial(self.port.get(), 115200, timeout=0)
            self.btn_con.config(text="Desconectar"); self.lbl_status.config(text=f"Conectado em {self.port.get()}")
        except Exception as e:
            self.lbl_status.config(text=f"Erro: {e}")

    # ---------- Loop ----------
    def _find_js(self):
        if pygame.joystick.get_count() and self.js is None:
            self.js = pygame.joystick.Joystick(0); self.js.init()
            self.lbl_js.config(text=f"G29: {self.js.get_name()}")
        elif not pygame.joystick.get_count() and self.js is not None:
            self.js = None; self.lbl_js.config(text="G29: -")

    def _tick(self):
        pygame.event.pump()
        self._find_js()
        thr = clu = 0.0
        gear = self.paddle_gear
        if self.js:
            n = self.js.get_numaxes()
            raw = [self.js.get_axis(i) for i in range(n)]
            self.lbl_raw.config(text="eixos brutos: " + " ".join(f"{i}:{v:+.2f}" for i, v in enumerate(raw)))
            vals = {}
            for name, var in self.axis_vars.items():
                a = var.get()
                v = raw[a] if a < n else 0.0
                vals[name] = (v + 1) / 2 if name == "volante" else axis_to_pct(v, self.inv_vars[name].get())
                self.bars[name]["value"] = vals[name] * 100
            thr, clu = vals["acelerador"], vals["embreagem"]

            nb = self.js.get_numbuttons()
            h = [g for b, g in GEAR_BUTTONS.items() if b < nb and self.js.get_button(b)]
            for b in (PADDLE_UP, PADDLE_DOWN):
                pressed = b < nb and self.js.get_button(b)
                if pressed and not self.prev_btn.get(b):
                    self.paddle_gear = min(6, self.paddle_gear + 1) if b == PADDLE_UP else max(0, self.paddle_gear - 1)
                self.prev_btn[b] = pressed
            gear = h[0] if h else self.paddle_gear
        self.lbl_gear.config(text=f"Marcha: {'N' if gear == 0 else gear}")

        pkt = f"{int(thr * 255)},{int(clu * 255)},{gear}\n"
        self.lbl_send.config(text="TX: " + pkt.strip())
        if self.ser:
            try:
                self.ser.write(pkt.encode())
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
            if len(p) == 5 and all(x.lstrip("-").isdigit() for x in p):
                r, v, i, g, gr = map(int, p)
                self.lbl_rpm.config(text=f"{r} RPM"); self.pb_rpm["value"] = r
                self.lbl_fb.config(text=f"VSS: {v} Hz   Injeção: {i} µs   Ignição há: {g} ms   Marcha ESP: {gr}")
                break


if __name__ == "__main__":
    App().mainloop()
