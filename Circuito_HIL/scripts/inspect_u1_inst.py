with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('(property "Reference" "U1"')
u1_block = text[pos-200:pos+2500]
print(u1_block[:2000])
