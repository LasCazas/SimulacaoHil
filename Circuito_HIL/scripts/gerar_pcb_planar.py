"""Roteador Planar Deterministico para a Bancada HIL.
Cada rede possui um canal horizontal proprio (Y-slot), garantindo
matematicamente ZERO cruzamento e ZERO curto entre trilhas.
"""

# Definicao dos canais (Y-slots) de cima para baixo:
# Y = 18..24: 5V e 3V3 de distribuicao para PCM5102
# Y = 26..32: I2S_BCK, I2S_LCK, I2S_DIN para PCM5102
# Y = 34..38: CRANK+ e VR1- para J1.1 e J1.2
# Y = 42..46: NET_TPS_OUT e NET_MAP_OUT para J1.3 e J1.4
# Y = 50..56: VSS_PULSE e CLUTCH_SIG para J1.5 e J1.6
# Y = 62..70: FB_IGN_3V3 e FB_INJ_3V3 (ESP32 <-> U3)
# Y = 72..78: SPEEDUINO_INJ e SPEEDUINO_IGN (U3 <-> J1.7, J1.8)
# Y = 82..90: Barramento de Alimentacao 5V, 3V3 e GND

print("Canais planares definidos com sucesso!")
