arp_path = r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\scripts\auto_route_perfect.py'
with open(arp_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect connections list
# We can add direct clean routes for:
# 1. ESP Pin 14 GND to ESP Pin 17 GND:
# (28.57, 65.24) -> (51.43, 65.24)
# 2. U3 Pad 10 GND to U3 Pad 4 GND:
# (85.65, 77.27) -> (98.35, 77.27)
# 3. C2 Pad 2 GND to U3 Pad 10 GND:
# (90.0, 45.0) -> (85.65, 77.27) via (88.0, 45.0) -> (88.0, 77.27) -> (85.65, 77.27)

add_routes = '''
# Conexões diretas de GND sem bloqueio:
b_cu_tracks.append((esp_pins[14][0], esp_pins[14][1], esp_pins[17][0], esp_pins[17][1], 1.2, 16))
b_cu_tracks.append((u3_pins[10][0], u3_pins[10][1], u3_pins[4][0], u3_pins[4][1], 1.0, 16))
b_cu_tracks.append((c2_p2[0], c2_p2[1], 88.0, c2_p2[1], 1.0, 16))
b_cu_tracks.append((88.0, c2_p2[1], 88.0, u3_pins[10][1], 1.0, 16))
b_cu_tracks.append((88.0, u3_pins[10][1], u3_pins[10][0], u3_pins[10][1], 1.0, 16))
'''

if 'esp_pins[14][0], esp_pins[14][1], esp_pins[17][0]' not in text:
    target = 'print(f"\\nTotal B.Cu segmentos:'
    text = text.replace(target, add_routes + '\n' + target)

with open(arp_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("auto_route_perfect.py updated with direct GND routes!")
