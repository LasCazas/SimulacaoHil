with open('Circuito_HIL/Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('(symbol "Device:R"')
if pos != -1:
    print(text[pos:pos+1500])

pos_c = text.find('(symbol "Device:C"')
if pos_c != -1:
    print(text[pos_c:pos_c+1500])
