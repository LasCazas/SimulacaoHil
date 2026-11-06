"""Motor de audio em tempo real no PC (inspirado no projeto Berrador).
Roda 100% no computador via sounddevice + numpy (zero carga no ESP32).

Suporta tres perfis sonoros:
1) "ktm390": sintese fisica de monocilindrico 4 tempos 373cc (KTM Duke 390) "So o Cano",
   com pulso de choque, ressonancia de cano aberto e pipocos secos.
2) "hornet": sintese fisica de 4 cilindros em linha 600cc (Honda CB 600F Hornet) 4x1 direto,
   com uivo estridente agudo em alta rotacao, ronco encorpado na lenta e corte metralhadora.
3) "berrador": usa os samples reais (idle.wav, mid.wav, high.wav, pop.wav) com
   Pitch Shifting por interpolacao linear, crossfade suave e modulacao de carga.
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
        self.profile = "ktm390"  # "ktm390" (Duke 390 Só o Cano) ou "berrador"

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
        self.ph_synth_hornet = 0.0
        self.cut_timer = 0.0

        # Gerador procedural de Pops & Bangs (tiros e estalos no escape direto)
        self.pop_time = -1.0
        self.pop_dur = 0.10
        self.pop_gain = 0.0
        self.pop_kind = "bang"
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

    def _trigger_pop(self, gain=0.8, kind="bang", dur=0.10):
        """Dispara proceduralmente um tiro/pipoco (pop/bang) sintetico no escape."""
        self.pop_time = 0.0
        self.pop_dur = float(dur)
        self.pop_gain = float(gain)
        self.pop_kind = kind

    def _render_pop_block(self, frames):
        """Gera proceduralmente a onda de choque e ressonancia de um pipoco (pop/bang) no escape."""
        if self.pop_time < 0.0:
            return None
        dt = 1.0 / self.SAMPLE_RATE
        t = self.pop_time + dt * np.arange(frames, dtype=np.float32)
        self.pop_time += frames * dt
        if self.pop_time >= self.pop_dur:
            self.pop_time = -1.0

        valid = t < self.pop_dur
        if not np.any(valid):
            return None

        tv = t[valid]
        # Onda de choque: subida instantanea e expansao explosiva
        decay = 95.0 if self.pop_kind == "bang" else 150.0
        shock = np.exp(-decay * tv) * (1.0 - np.exp(-1800.0 * tv))

        # Frequencias de ressonancia do escape da moto atual
        is_hornet = self.profile == "hornet"
        f1 = 360.0 if is_hornet else 260.0
        f2 = 2200.0 if is_hornet else 1450.0

        # Oscilacao acustica amortecida do gas no escape
        ring = (
            np.sin(2.0 * np.pi * f1 * tv) * np.exp(-40.0 * tv)
            + 0.65 * np.sin(2.0 * np.pi * f2 * tv) * np.exp(-70.0 * tv)
        )

        # Ruido de chamas / turbulencia da combustao
        noise_decay = 75.0 if self.pop_kind == "bang" else 120.0
        noise = np.random.uniform(-0.35, 0.35, len(tv)).astype(np.float32) * np.exp(-noise_decay * tv)

        sig_pop = (shock * 2.8 + ring * 1.3 + noise * 0.9) * float(self.pop_gain)
        sig_pop = np.tanh(sig_pop * 1.4)

        out = np.zeros(frames, dtype=np.float32)
        out[valid] = sig_pop
        return out

    def update_state(self, rpm, throttle_pct):
        """Atualiza RPM (ex: 1000..11500) e TPS (0.0..1.0)."""
        self.target_rpm = max(600.0, min(12500.0, float(rpm)))
        new_thr = max(0.0, min(1.0, float(throttle_pct)))

        # Dispara BANG seco de escape ao soltar o acelerador rapido em giro medio/alto
        min_pop_rpm = 3300.0 if self.profile in ("ktm390", "hornet") else 4200.0
        thr_drop = 0.16 if self.profile in ("ktm390", "hornet") else 0.25
        if (
            self.prev_throttle > thr_drop
            and new_thr < 0.07
            and self.smooth_rpm > min_pop_rpm
            and self.pop_cooldown <= 0.0
        ):
            pop_pwr = min(1.0, 0.75 + (self.smooth_rpm - min_pop_rpm) / 6500.0)
            self._trigger_pop(gain=pop_pwr, kind="bang", dur=0.11)
            self.pop_cooldown = 0.20 if self.profile == "hornet" else 0.26
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
        else:
            is_sport = self.profile in ("ktm390", "hornet")
            pop_min_rpm = 3400.0 if is_sport else 4800.0
            pop_chance = 0.22 if self.profile == "hornet" else 0.18
            if thr < 0.04 and rpm > pop_min_rpm and self.pop_time < 0.0 and random.random() < pop_chance:
                # Estalos em cascata no freio-motor (crackles procedurais de escape livre)
                self._trigger_pop(
                    gain=random.uniform(0.55, 0.90),
                    kind="crackle",
                    dur=random.uniform(0.05, 0.08)
                )
                self.pop_cooldown = random.uniform(0.08, 0.16)

        # Corte de giro (rev limiter)
        cut_env = 1.0
        cut_rpm = 10350.0
        cut_speed = 28.0 if self.profile == "hornet" else 24.0
        if rpm >= cut_rpm:
            self.cut_timer += dt_block * cut_speed  # Metralhadora rapida no corte
            if int(self.cut_timer) % 2 == 1:
                cut_env = 0.08

        if self.profile == "hornet":
            sig = self._render_hornet(frames, rpm, thr)
        elif self.profile == "berrador" and "idle" in self.samples:
            sig = self._render_berrador(frames, rpm, thr)
        else:
            sig = self._render_ktm390(frames, rpm, thr)

        sig *= cut_env

        # Mistura o pipoco procedural sintetico no escape (zero samples de pop.wav)
        pop_sig = self._render_pop_block(frames)
        if pop_sig is not None:
            sig += pop_sig

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
        """Sintese fisica de monocilindrico 4 tempos 373cc (KTM Duke 390) 'So o Cano'.

        Fidelidade real de monocilindrico esportivo com escape livre:
        - 1 disparo por ciclo de 720 deg (f_fire = RPM / 120 Hz)
        - Pulso de choque de alta pressao com ricochete de rarefacao (pistao de 89mm)
        - Ressonancia acustica do duto aberto (~260 Hz corpo grave, ~780 Hz presenca)
        - Soco ritmado e oco na lenta e grito estalado no giro alto
        """
        f_fire = max(8.0, rpm / 120.0)
        dphi = 2.0 * np.pi * f_fire / self.SAMPLE_RATE
        phi = self.ph_synth + dphi * np.arange(frames, dtype=np.float64)
        self.ph_synth = float((self.ph_synth + dphi * frames) % (2.0 * np.pi))

        tau = (phi % (2.0 * np.pi)) / (2.0 * np.pi)
        t_in_cycle = tau / f_fire

        # Onda de choque de combustao (pico inicial de alta pressao e retorno de vácuo)
        shock = np.sin(np.pi * np.clip(tau / 0.35, 0.0, 1.0)) * np.exp(-11.0 * tau)
        shock_crack = (np.exp(-22.0 * tau) - 0.45 * np.exp(-48.0 * tau)) * np.clip(1.0 - tau / 0.28, 0.0, 1.0)

        # Ressonancia de coluna de gas em tubo de aco (~85 cm direto)
        pipe_bass = np.sin(2.0 * np.pi * 260.0 * t_in_cycle) * np.exp(-110.0 * t_in_cycle)
        pipe_ring = np.sin(2.0 * np.pi * 780.0 * t_in_cycle) * np.exp(-220.0 * t_in_cycle)
        pipe_rasp = np.sin(2.0 * np.pi * 1850.0 * t_in_cycle) * np.exp(-340.0 * t_in_cycle)

        # Ronco mecanico de fundo do virabrequim (f_crank = 2 * f_fire)
        crank = 0.35 * np.sin(phi) + 0.28 * np.sin(2.0 * phi + 0.3) + 0.14 * np.sin(3.0 * phi)

        # Balanco dinamico com acelerador (carga/TPS)
        sig_pulse = (
            shock * 1.70
            + shock_crack * (1.10 + 2.10 * thr)
            + pipe_bass * 0.90
            + pipe_ring * (0.50 + 0.65 * thr)
            + pipe_rasp * (0.28 + 0.85 * thr)
        ) * (0.90 + 1.65 * thr)

        sig_raw = crank * (0.50 + 0.50 * thr) + sig_pulse * 1.35

        # Deformacao nao-linear de escape direto (estalo metalico raspado sem ruidos parasitas)
        sig_dist = sig_raw + 0.35 * np.maximum(0.0, sig_raw)**1.8 - 0.18 * np.minimum(0.0, sig_raw)**2

        sig_out = np.tanh(sig_dist * 0.78)
        return sig_out.astype(np.float32) * 1.55

    def _render_hornet(self, frames, rpm, thr):
        """Sintese fisica de 4 cilindros em linha 600cc (Honda CB 600F Hornet) 'So o Cano'.

        Mesma arquitetura fisica e harmonica da KTM Duke 390, adaptada para 4 cilindros:
        - 2 disparos por volta do virabrequim (f_fire = RPM / 30 Hz)
        - Pulso de choque de alta pressao com ricochete de rarefacao dos 4 cilindros
        - Ressonancia acustica de coletor 4 em 1 (~360 Hz corpo grave, ~890 Hz medio, ~2350 Hz screamer)
        - Ronco encorpado e gordo na lenta e berro rasgado agressivo em alta rotacao
        """
        f_fire = max(18.0, rpm / 30.0)
        dphi = 2.0 * np.pi * f_fire / self.SAMPLE_RATE
        phi = self.ph_synth_hornet + dphi * np.arange(frames, dtype=np.float64)
        self.ph_synth_hornet = float((self.ph_synth_hornet + dphi * frames) % (2.0 * np.pi))

        tau = (phi % (2.0 * np.pi)) / (2.0 * np.pi)
        t_in_cycle = tau / f_fire

        # Onda de choque de combustao de 4 cilindros (pico de alta pressao e retorno de vácuo)
        shock = np.sin(np.pi * np.clip(tau / 0.40, 0.0, 1.0)) * np.exp(-12.0 * tau)
        shock_crack = (np.exp(-24.0 * tau) - 0.50 * np.exp(-50.0 * tau)) * np.clip(1.0 - tau / 0.30, 0.0, 1.0)

        # Ressonancias de coluna de gas em coletor 4x1 de inox aberto
        pipe_bass = np.sin(2.0 * np.pi * 360.0 * t_in_cycle) * np.exp(-140.0 * t_in_cycle)
        pipe_ring = np.sin(2.0 * np.pi * 890.0 * t_in_cycle) * np.exp(-250.0 * t_in_cycle)
        pipe_scream = np.sin(2.0 * np.pi * 2350.0 * t_in_cycle) * np.exp(-380.0 * t_in_cycle)

        # Ronco mecanico de virabrequim do 4 cilindros (f_crank = RPM / 60 = 0.5 * f_fire)
        # Produz o peso grave gordo do 4 canecos na lenta
        crank = 0.32 * np.sin(0.5 * phi) + 0.22 * np.sin(phi + 0.3) + 0.12 * np.sin(1.5 * phi)

        # Balanco dinamico com acelerador (carga/TPS)
        sig_pulse = (
            shock * 1.65
            + shock_crack * (1.00 + 1.90 * thr)
            + pipe_bass * 0.85
            + pipe_ring * (0.45 + 0.60 * thr)
            + pipe_scream * (0.25 + 0.85 * thr)
        ) * (0.90 + 1.60 * thr)

        sig_raw = crank * (0.50 + 0.50 * thr) + sig_pulse * 1.30

        # Deformacao nao-linear de escape direto 4x1 (estalo metalico raspado sem ruidos parasitas)
        sig_dist = sig_raw + 0.32 * np.maximum(0.0, sig_raw)**1.8 - 0.16 * np.minimum(0.0, sig_raw)**2

        sig_out = np.tanh(sig_dist * 0.78)
        return sig_out.astype(np.float32) * 1.55
