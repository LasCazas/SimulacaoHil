with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('(symbol "HIL:ESP32_DevKit_V1_30Pin"')
# find matching end of this symbol
end = text.find('(symbol "HIL:', start + 10)
if end == -1:
    end = text.find('(symbol "Device:', start + 10)

block = text[start:end]
print("Block length:", len(block))

import re
pins = re.findall(r'\(pin\s+(\w+)\s+(\w+)\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\s+(\d+)\)\s+\(length\s+[-\d\.]+\)\s+\(name\s+"(.*?)"\s+.*?\)\s+\(number\s+"(\d+)"', block, re.DOTALL)
for ptype, pshape, x, y, rot, pname, pnum in pins:
    print(f"Pin {pnum:>2}: {pname:<15} at ({x}, {y}) rot={rot} type={ptype}")
