with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('Logic_Level_Converter_4CH_1_1')
chunk = text[pos:pos+4000]
import re
pins = re.findall(r'\(pin\s+(\w+)\s+(\w+)\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\s+(\d+)\)\s+\(length\s+[-\d\.]+\)\s+\(name\s+"(.*?)"\s+.*?\)\s+\(number\s+"(\d+)"', chunk, re.DOTALL)
for ptype, pshape, x, y, rot, pname, pnum in pins:
    print(f"Pin {pnum:>2}: {pname:<15} at ({x}, {y}) rot={rot} type={ptype}")
