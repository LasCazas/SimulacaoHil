# Simulador Dinâmico HIL — Logitech G29 + ESP32 DevKit V1 + Speeduino 48-Way

Bancada de simulação **Hardware-in-the-Loop (HIL)** orientada ao condutor desenvolvida pela equipe **IF Betim Racing (IFMG — Campus Betim)** para validação e calibração em malha fechada da ECU **Speeduino 48-Way**, modelando a dinâmica da motocicleta **KTM Duke 390** (~373 cm³, monocilíndrica, roda fônica **22-2**).

---

## Documentação e Mapa Base Oficial

- **Documentação Técnica Completa (PDF):** [`SimulacaoComG29_ComOPCEEsp.pdf`](./SimulacaoComG29_ComOPCEEsp.pdf) *(código-fonte LaTeX em [`SimulacaoComG29_ComOPCEEsp/`](./SimulacaoComG29_ComOPCEEsp/))*
- **Mapa Base da ECU e Configurações Completas (TunerStudio `.msq`):**  
  **[Acessar Pasta do Mapa Base no Google Drive](https://drive.google.com/drive/u/1/folders/1bbK6THQXaumvtmB5yQu2AqLAyRcFz2Z0)**

---

## Estrutura do Repositório

| Arquivo / Pasta | Descrição |
|---|---|
| [`HIL_Esp/HIL_Esp.ino`](./HIL_Esp/HIL_Esp.ino) | Firmware principal do **ESP32 DevKit V1 (30 pinos)**: roda fônica 22-2 via I2S/DMA no PCM5102A, dinâmica rotacional e longitudinal, DACs de TPS/MAP, PWM de VSS e ISRs de injeção/ignição. |
| [`interface_g29.py`](./interface_g29.py) | Interface gráfica em Python (`tkinter` + `pygame` + `pyserial`) para leitura do Logitech G29, envio de comandos a 30 Hz, parametrização remota e telemetria em tempo real. |
| [`moto_duke390.json`](./moto_duke390.json) | Parâmetros físicos e documentados da KTM Duke 390 (inércia, cilindrada, bico injetor, massa, aerodinâmica, embreagem, relações de marcha e curva de torque WOT). Enviado via Serial sem precisar regravar o ESP32. |
| [`config_g29.json`](./config_g29.json) | Preferências salvas automaticamente pela interface (porta COM, índices dos eixos e inversão dos pedais). |
| [`CodigoEsp/CodigoEsp.ino`](./CodigoEsp/CodigoEsp.ino) | Código base original de geração isolada da roda fônica 22-2 via I2S. |
| [`SimulacaoComG29_ComOPCEEsp/`](./SimulacaoComG29_ComOPCEEsp/) | Código-fonte LaTeX e imagens da documentação técnica. |

---

## Resumo de Pinagem (ESP32 DevKit V1 $\leftrightarrow$ Speeduino 48-Way)

| Sinal | Pino ESP32 | Condicionamento / Módulo | Pino Speeduino |
|---|---|---|---|
| **TPS** (Borboleta) | `GPIO 25` (`DAC1`) | Filtro RC ($10\text{ k}\Omega + 1\,\mu\text{F}$) | `B_C7` (`TPS_Sensor`) |
| **MAP** (Coletor) | `GPIO 26` (`DAC2`) | Filtro RC ($10\text{ k}\Omega + 1\,\mu\text{F}$) | `B_C8` (`MAP-EXT`) |
| **Crank 22-2** (`BCK`) | `GPIO 27` | Pino `BCK` do PCM5102A | `B_B2` (`CRANK-IN`) |
| **Crank 22-2** (`LCK`) | `GPIO 14` | Pino `LCK` do PCM5102A | *(saída analógica do PCM5102A)* |
| **Crank 22-2** (`DIN`) | `GPIO 22` | Pino `DIN` do PCM5102A (`SCK` no `GND`) | `B_B3` (`VR1-` $\leftarrow$ `GND` PCM5102A) |
| **VSS** (Velocidade) | `GPIO 16` (`PWM`) | Direto ($3{,}3\text{ V}$) | `B_A7` (`VSS`) |
| **Embreagem** | `GPIO 15` | Direto ($3{,}3\text{ V}$) | `B_B7` (`Clutch_in`) |
| **Feedback Injetor** | `GPIO 4` (`ISR`) | Conversor de Nível Lógico (`HV=5V` $\rightarrow$ `LV=3.3V`, Canal 2) | `G_A1` (`INJ-1-OUT`) |
| **Feedback Ignição** | `GPIO 5` (`ISR`) | Conversor de Nível Lógico (`HV=5V` $\rightarrow$ `LV=3.3V`, Canal 1) | `G_B1` (`IGN-1-OUT`) |
| **Terra Comum** | `GND` | Unificado entre ESP32, módulos e ECU | `B_A8` |

> **Nota sobre o Conversor de Nível Lógico:** Como na bancada HIL não são conectados bico injetor nem bobina de ignição físicos, não há picos indutivos (*flyback*). O próprio resistor de *pull-up* de $10\text{ k}\Omega$ do lado `HV` ($5\text{ V}$) do módulo conversor polariza a saída *open-drain* (`Low-Side`) do injetor na Speeduino e entrega pulsos limpos de $3{,}3\text{ V}$ ao ESP32.

---

## Como Reproduzir

1. **Speeduino / TunerStudio:** Baixe o mapa base (`.msq`) no [Google Drive](https://drive.google.com/drive/u/1/folders/1bbK6THQXaumvtmB5yQu2AqLAyRcFz2Z0), carregue na ECU e calibre o fim de escala de TPS ($0\text{--}3{,}3\text{ V}$).
2. **Firmware ESP32:** Grave [`HIL_Esp/HIL_Esp.ino`](./HIL_Esp/HIL_Esp.ino) na placa `ESP32 Dev Module` pela Arduino IDE.
3. **Interface no PC:**
   ```powershell
   git clone https://github.com/LasCazas/SimulacaoHil.git
   cd SimulacaoHil
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   python interface_g29.py
   ```
4. **Operação e Parametrização:** Conecte o Logitech G29 (com o Logitech G HUB aberto), selecione a porta `COM` do ESP32 e clique em **Conectar**. Para ajustar parâmetros da moto ou habilitar a realimentação de combustível (`"use_inj_feedback": 1`), edite [`moto_duke390.json`](./moto_duke390.json) e clique em **Reenviar parâmetros**.
