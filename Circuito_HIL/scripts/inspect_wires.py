with open('Circuito_HIL/Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re
lines = text.splitlines()
for i, line in enumerate(lines):
    if any(k in line for k in ['139.7', '142.24', '137.16', '134.62', '146.05', '143.51', '148.59', '161.29']):
        if '(wire' in line or '(pts' in line or '(xy' in line or '(junction' in line:
            print(f"{i}: {line}")
