with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

pos1 = text.find('(property "Reference" "U1"')
pos2 = text.find('(property "Reference" "U1"', pos1 + 1)
print("Second occurrence at:", pos2)
if pos2 != -1:
    print(text[pos2-150:pos2+1200])
