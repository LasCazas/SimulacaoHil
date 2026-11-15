import os

with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\scripts\export_routed_board.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix esp_names_right
old_names = 'esp_names_right = ["3V3", "15", "D2", "D0", "D4", "16", "D5", "18", "19", "21", "RX0", "TX0", "22", "23", "EN2"]'
new_names = 'esp_names_right = ["3V3", "GND", "15", "D2", "D4", "16", "17", "D5", "18", "19", "21", "RX0", "TX0", "22", "23"]'

text = text.replace(old_names, new_names)

with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\scripts\export_routed_board.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("export_routed_board.py updated!")
