with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('(property "Reference" "U3"')
# find second occurrence (instance)
pos2 = text.find('(property "Reference" "U3"', pos + 10)
print(text[pos2-150:pos2+1200])
