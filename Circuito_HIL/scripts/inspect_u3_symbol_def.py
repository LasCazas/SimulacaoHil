with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect symbol definition Logic_Level_Converter_4CH
pos = text.find('(symbol "HIL:Logic_Level_Converter_4CH"')
end = text.find('(symbol "HIL:', pos + 10)
if end == -1:
    end = text.find('(symbol "Device:', pos + 10)
sym_block = text[pos:end]
print("Symbol block:")
print(sym_block[:2500])
