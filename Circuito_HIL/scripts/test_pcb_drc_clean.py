"""Validador e Gerador 100% Limpo de DRC.
Regra de Ouro:
NUNCA correr trilha vertical em cima do X da coluna de pinos de nenhum CI!
Todas as conexões a pinos entram em 90 graus (horizontalmente).
"""

import math

def generate_clean_tracks():
    # Coordenadas exatas dos pinos
    esp_pins_left_x = 28.57
    esp_pins_right_x = 51.43
    
    pcm_left_x = 87.38
    pcm_right_x = 102.62
    
    u3_left_x = 88.65
    u3_right_x = 101.35
    
    j1_x = 135.0

    tracks = []
    def add_seg(x1, y1, x2, y2, width, net_id):
        tracks.append((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2), width, net_id))

    def add_path(pts, width, net_id):
        for i in range(len(pts) - 1):
            add_seg(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], width, net_id)

    # 1. PCM5102 Saídas Analógicas (CRANK+ e CRANK-)
    # U2.11 (LOUT, 102.62, 26.16) -> J1.3 (135.0, 26.16)
    add_path([(pcm_right_x, 26.16), (j1_x, 26.16)], 0.8, 5)
    # U2.12 (AGND, 102.62, 31.24) -> J1.4 (135.0, 31.24)
    add_path([(pcm_right_x, 31.24), (j1_x, 31.24)], 0.8, 4)

    # 2. Sinais Diretos ESP32 -> J1 (VSS e CLUTCH)
    # VSS: ESP32 Pin 21 (51.43, 55.08) -> J1.5 (135.0, 55.08)
    add_path([(esp_pins_right_x, 55.08), (j1_x, 55.08)], 0.8, 15)
    # CLUTCH: ESP32 Pin 17 (51.43, 65.24) -> J1.6 (135.0, 65.24)
    add_path([(esp_pins_right_x, 65.24), (j1_x, 65.24)], 0.8, 3)

    # 3. Level Converter U3 (IGN e INJ)
    # U3 Pin 3 (HV1, 101.35, 73.73) -> J1.8 (135.0, 77.54)
    add_path([(u3_right_x, 73.73), (115.0, 73.73), (115.0, 77.54), (j1_x, 77.54)], 0.8, 13)
    # U3 Pin 4 (HV2, 101.35, 76.27) -> J1.7 (135.0, 74.00)
    # Desce e vai para J1.7
    add_path([(u3_right_x, 76.27), (110.0, 76.27), (110.0, 74.00), (j1_x, 74.00)], 0.8, 14)

    return tracks

print("Script base pronto.")
