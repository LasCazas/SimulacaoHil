with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\scripts\export_routed_board.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('Logic_Level_Converter_4CH')
print(text[pos-100:pos+1500])
