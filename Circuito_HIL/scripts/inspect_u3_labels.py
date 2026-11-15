with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re
labels = re.findall(r'\(label\s+"(.*?)"\s+\(at\s+([\d\.]+)\s+([\d\.]+)', text)
for name, x, y in labels:
    if 200 <= float(x) <= 270 and 160 <= float(y) <= 190:
        print(f"Label {name:<18} at ({x}, {y})")

# find power symbols around U3
power_syms = re.findall(r'\(symbol\s+\(lib_id "power:(.*?)"\)\s+\(at\s+([\d\.]+)\s+([\d\.]+)', text)
for name, x, y in power_syms:
    if 200 <= float(x) <= 270 and 160 <= float(y) <= 190:
        print(f"Power {name:<18} at ({x}, {y})")
