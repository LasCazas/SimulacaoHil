import re

# 1. Update auto_route_perfect.py
arp_path = r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\scripts\auto_route_perfect.py'
with open(arp_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace U3 pin nets
old_u3_nets = '''    ("U3", "1"): 2, ("U3", "2"): 16, ("U3", "3"): 13, ("U3", "4"): 14,
    ("U3", "7"): 1, ("U3", "8"): 16, ("U3", "9"): 6, ("U3", "10"): 7,'''

new_u3_nets = '''    ("U3", "2"): 13, ("U3", "3"): 2, ("U3", "4"): 16, ("U3", "5"): 14,
    ("U3", "8"): 6, ("U3", "9"): 1, ("U3", "10"): 16, ("U3", "11"): 7,'''

text = text.replace(old_u3_nets, new_u3_nets)

# Replace U3 connections
text = text.replace('("IGN_OUT", u3_pins[3], j1_pins[7], 13, 0.8)', '("IGN_OUT", u3_pins[2], j1_pins[7], 13, 0.8)')
text = text.replace('("INJ_OUT", u3_pins[4], j1_pins[8], 14, 0.8)', '("INJ_OUT", u3_pins[5], j1_pins[8], 14, 0.8)')
text = text.replace('("IGN_FB", esp_pins[23], u3_pins[9], 6, 0.8)', '("IGN_FB", esp_pins[23], u3_pins[8], 6, 0.8)')
text = text.replace('("INJ_FB", esp_pins[20], u3_pins[10], 7, 0.8)', '("INJ_FB", esp_pins[20], u3_pins[11], 7, 0.8)')
text = text.replace('("+3V3_U3", esp_pins[16], u3_pins[7], 1, 1.0)', '("+3V3_U3", esp_pins[16], u3_pins[9], 1, 1.0)')
text = text.replace('("GND_U3_LV", esp_pins[14], u3_pins[8], 16, 1.0)', '("GND_U3_LV", esp_pins[14], u3_pins[10], 16, 1.0)')
text = text.replace('("GND_U3_HV", u3_pins[8], u3_pins[2], 16, 1.0)', '("GND_U3_HV", u3_pins[10], u3_pins[4], 16, 1.0)')

# Replace jumper fallback for INJ_FB if any
text = text.replace('u3_pins[10]', 'u3_pins[11]')

with open(arp_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("auto_route_perfect.py updated successfully!")

# 2. Update export_routed_board.py
erb_path = r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\scripts\export_routed_board.py'
with open(erb_path, 'r', encoding='utf-8') as f:
    erb_text = f.read()

# Update silkscreen names for U3
old_lv = 'u3_names_lv = ["LV", "GND", "D5", "D4", "NC", "NC"]'
new_lv = 'u3_names_lv = ["TXI", "RXO", "LV", "GND", "RXO", "TXI"]'

old_hv = 'u3_names_hv = ["HV", "GND", "IGN", "INJ", "NC", "NC"]'
new_hv = 'u3_names_hv = ["TXO", "RXI", "HV", "GND", "RXI", "TXO"]'

erb_text = erb_text.replace(old_lv, new_lv)
erb_text = erb_text.replace(old_hv, new_hv)

with open(erb_path, 'w', encoding='utf-8') as f:
    f.write(erb_text)

print("export_routed_board.py updated successfully!")
