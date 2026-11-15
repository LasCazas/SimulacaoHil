with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('(number "17"')
print(text[pos-100:pos+200])
