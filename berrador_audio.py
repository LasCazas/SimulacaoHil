"""Motor de audio em tempo real no PC (inspirado no projeto Berrador).
Roda 100% no computador via sounddevice + numpy (zero carga no ESP32).

Suporta dois perfis sonoros:
1) "berrador": usa os samples reais (idle.wav, mid.wav, high.wav, pop.wav) com
   Pitch Shifting por interpolacao linear, crossfade suave entre faixas,
   modulacao de carga (TPS) e pipocos (pops & bangs) na desaceleracao.
2) "ktm390": sintese fisica harmonica de monocilindrico 4 tempos (Duke 390)
   com corte de giro e pipocos no escapamento.
"""
import os
import random
import wave

import numpy as np

try:
    import sounddevice as sd

    HAS_AUDIO = True
except Exception:
    sd = None
    HAS_AUDIO = False


def _load_wav_float(path):
    """Carrega um WAV 16-bit mono como float32 em [-1.0, 1.0]."""
    with wave.open(path, "rb") as wf:
        raw = wf.readframes(wf.getnframes())
        sr = wf.getframerate()
        ch = wf.getnchannels()
    arr = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    if ch > 1:
        arr = arr[::ch]
    return arr, sr


class EngineAudioPlayer:
    SAMPLE_RATE = 44100
    BLOCK_SIZE = 512

    def __init__(self, sounds_dir):
        self.sounds_dir = sounds_dir
        self.enabled = False
        self.volume = 0.55
        self.profile = "berrador"  # "berrador" ou "ktm390"

        # Estado alvo vindo da UI / ESP32
        self.target_rpm = 1400.0
        self.smooth_rpm = 1400.0
        self.throttle = 0.0
        self.prev_throttle = 0.0

        # Samples do Berrador
        self.samples = {}
        self.sample_sr = 22050
        self._load_samples()

        # Fases continuas entre callbacks (evita qualquer estalo/clique)
        self.ph_idle = 0.0
        self.ph_mid = 0.0
        self.ph_high = 0.0
        self.ph_synth = 0.0
        self.cut_timer = 0.0
        self.pop_pos = -1
        self.pop_gain = 0.0
        self.pop_cooldown = 0.0

        self.stream = None
        self.device = None  # None = saida padrao do Windows

    def _load_samples(self):
        for name in ("idle", "mid", "high", "pop"):
            p = os.path.join(self.sounds_dir, f"{name}.wav")
            if os.path.exists(p):
                try:
                    arr, sr = _load_wav_float(p)
                    if len(arr) > 64:
                        self.samples[name] = arr
                        self.sample_sr = sr
                except Exception:
                    pass

    @property
    def available(self):
        return HAS_AUDIO

    @staticmethod
    def list_output_devices():
        """Lista saidas de audio (via MME no Windows, que aceita qualquer sample rate).
        Retorna lista de (indice, nome)."""
        if not HAS_AUDIO:
            return []
        out = []
        try:
            apis = sd.query_hostapis()
            mme_idx = next((i for i, a in enumerate(apis) if a["name"] == "MME"), None)
            for i, d in enumerate(sd.query_devices()):
                if d["max_output_channels"] < 1:
                    continue
                if mme_idx is not None and d["hostapi"] != mme_idx:
                    continue
                if "Mapeador" in d["name"] or "Mapper" in d["name"]:
                    continue
                out.append((i, d["name"]))
        except Exception:
            pass
        return out

    def restart(self, device=None):
        """Reinicializa a PortAudio (relendo os dispositivos do Windows, ex: fone recem
        plugado) e reabre o stream no dispositivo escolhido (None = padrao do Windows)."""
        self.stop()
        self.device = device
        if HAS_AUDIO:
            try:
                sd._terminate()
                sd._initialize()
            except Exception:
                pass
        self.start()

    def start(self):
        if not HAS_AUDIO or self.stream is not None:
            return
        try:
            self.stream = sd.OutputStream(
                samplerate=self.SAMPLE_RATE,
                channels=1,
                dtype="float32",
                blocksize=self.BLOCK_SIZE,
                callback=self._callback,
                device=self.device,
            )
            self.stream.start()
        except Exception:
            self.stream = None

    def stop(self):
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

    def update_state(self, rpm, throttle_pct):
        """Atualiza RPM (ex: 1000..10500) e TPS (0.0..1.0)."""
        self.target_rpm = max(600.0, min(11500.0, float(rpm)))
        new_thr = max(0.0, min(1.0, float(throttle_pct)))

        # Dispara pipoco (pop) ao tirar o pe rapido em giro medio/alto
        if (
            self.prev_throttle > 0.25
            and new_thr < 0.06
            and self.smooth_rpm > 4200.0
            and self.pop_cooldown <= 0.0
        ):
            self.pop_pos = 0
            self.pop_gain = min(1.0, 0.55 + (self.smooth_rpm - 4200.0) / 8000.0)
            self.pop_cooldown = 0.35
        self.prev_throttle = new_thr
        self.throttle = new_thr

    def _read_loop_interp(self, buf_name, phase, step, n):
        """Le n amostras de um loop com interpolacao linear continua."""
        wav = self.samples.get(buf_name)
        if wav is None:
            return np.zeros(n, dtype=np.float32), 0.0
        L = len(wav)
        idx = (phase + step * np.arange(n, dtype=np.float64)) % L
        i0 = idx.astype(np.int32)
        frac = (idx - i0).astype(np.float32)
        i1 = (i0 + 1) % L
        out = wav[i0] * (1.0 - frac) + wav[i1] * frac
        next_phase = float((phase + step * n) % L)
        return out, next_phase

    def _callback(self, outdata, frames, _time_info, _status):
        if not self.enabled or self.volume <= 0.001:
            outdata.fill(0.0)
            return

        dt_block = frames / self.SAMPLE_RATE
        # Suavizacao EMA do RPM (igual filosofia do Berrador)
        alpha = min(1.0, dt_block * 14.0)
        self.smooth_rpm += alpha * (self.target_rpm - self.smooth_rpm)
        rpm = self.smooth_rpm
        thr = self.throttle

        if self.pop_cooldown > 0.0:
            self.pop_cooldown = max(0.0, self.pop_cooldown - dt_block)
        elif thr < 0.03 and rpm > 4800.0 and self.pop_pos < 0 and random.random() < 0.06:
            # Pipocos ocasionais no freio-motor em alta rotacao
            self.pop_pos = 0
            self.pop_gain = 0.45
            self.pop_cooldown = 0.22

        # Corte de giro (rev limiter ~10400 RPM)
        cut_env = 1.0
        if rpm >= 10350.0:
            self.cut_timer += dt_block * 22.0  # ~22 Hz de corte "ratatata"
            if int(self.cut_timer) % 2 == 1:
                cut_env = 0.12

        if self.profile == "berrador" and "idle" in self.samples:
            sig = self._render_berrador(frames, rpm, thr)
        else:
            sig = self._render_ktm390(frames, rpm, thr)

        sig *= cut_env

        # Mistura o pipoco (pop.wav) se ativo
        pop_wav = self.samples.get("pop")
        if self.pop_pos >= 0 and pop_wav is not None:
            ratio = self.sample_sr / self.SAMPLE_RATE
            idx = self.pop_pos + ratio * np.arange(frames, dtype=np.float32)
            valid = idx < (len(pop_wav) - 1)
            if np.any(valid):
                vi = idx[valid].astype(np.int32)
                sig[valid] += pop_wav[vi] * self.pop_gain * 0.95
                self.pop_pos += ratio * frames
            else:
                self.pop_pos = -1

        # Ganho de carga + volume master + soft-clipping (tanh) para nao distorcer
        load_gain = 0.58 + 0.42 * thr
        sig = np.tanh(sig * load_gain * 1.4) * float(self.volume)
        outdata[:, 0] = sig.astype(np.float32)

    def _render_berrador(self, frames, rpm, _thr):
        base_ratio = self.sample_sr / self.SAMPLE_RATE
        # Escala de pitch natural de 1000 a 10500 RPM
        norm = max(0.0, (rpm - 1100.0) / 9400.0)

        step_idle = base_ratio * (0.88 + 1.15 * norm)
        step_mid = base_ratio * (0.68 + 1.05 * norm)
        step_high = base_ratio * (0.58 + 0.95 * norm)

        # Pesos de crossfade suave entre Lenta, Media e Alta
        w_idle = max(0.0, 1.0 - norm * 2.5)
        w_mid = max(0.0, 1.0 - abs(norm - 0.48) * 2.4)
        w_high = max(0.0, (norm - 0.38) * 1.65)
        w_sum = max(0.001, w_idle + w_mid + w_high)

        out = np.zeros(frames, dtype=np.float32)
        if w_idle > 0.001:
            s_i, self.ph_idle = self._read_loop_interp("idle", self.ph_idle, step_idle, frames)
            out += s_i * (w_idle / w_sum)
        if w_mid > 0.001 and "mid" in self.samples:
            s_m, self.ph_mid = self._read_loop_interp("mid", self.ph_mid, step_mid, frames)
            out += s_m * (w_mid / w_sum)
        if w_high > 0.001 and "high" in self.samples:
            s_h, self.ph_high = self._read_loop_interp("high", self.ph_high, step_high, frames)
            out += s_h * (w_high / w_sum)
        return out * 2.2

    def _render_ktm390(self, frames, rpm, thr):
        """Sintese de monocilindrico 4 tempos (explosao a cada 2 voltas = RPM/120 Hz)."""
        f_fire = max(8.0, rpm / 120.0)
        dphi = 2.0 * np.pi * f_fire / self.SAMPLE_RATE
        phi = self.ph_synth + dphi * np.arange(frames, dtype=np.float32)
        self.ph_synth = float((self.ph_synth + dphi * frames) % (2.0 * np.pi))

        # Pulso assimetrico de escapamento 1 cilindro + harmonicos pares/impares
        sig = (
            0.55 * np.sin(phi)
            + 0.38 * np.sin(2.0 * phi + 0.4)
            + (0.24 + 0.20 * thr) * np.sin(3.0 * phi + 0.9)
            + (0.14 + 0.18 * thr) * np.sin(4.0 * phi)
            + 0.10 * np.sin(6.0 * phi)
        )
        # Sopro/inducao de admissao proporcional ao TPS
        if thr > 0.05:
            noise = np.random.uniform(-0.12, 0.12, frames).astype(np.float32) * thr
            sig = sig + noise
        return sig * 0.65
