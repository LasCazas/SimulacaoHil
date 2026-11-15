arp_path = r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\scripts\auto_route_perfect.py'
with open(arp_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the crossing vertical track at X=88
text = text.replace('b_cu_tracks.append((88.0, c2_p2[1], 88.0, u3_pins[10][1], 1.0, 16))', '# removed crossing')
text = text.replace('b_cu_tracks.append((c2_p2[0], c2_p2[1], 88.0, c2_p2[1], 1.0, 16))', '# removed')
text = text.replace('b_cu_tracks.append((88.0, u3_pins[10][1], u3_pins[10][0], u3_pins[10][1], 1.0, 16))', '# removed')

# Remove horizontal cut across ESP
text = text.replace('b_cu_tracks.append((esp_pins[14][0], esp_pins[14][1], esp_pins[17][0], esp_pins[17][1], 1.2, 16))', '# removed')

with open(arp_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Removed crossing tracks successfully!")
