with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# U1 is at (100.33, 139.7) rotated 180!
# When rotated 180:
# (x, y) -> (-x, -y) relative to origin (100.33, 139.7)
# Pin 16 is at (17.78, -17.78). Rotated 180: (-17.78, 17.78) relative to (100.33, 139.7):
# Abs coords of Pin 16: (100.33 - 17.78, 139.7 + 17.78) = (82.55, 157.48)!
# Wait, let's calculate all pin positions of U1 in the schematic!

u1_x, u1_y = 100.33, 139.7
# Let's verify with the screenshot uploaded_media_1794605486745.png
# In screenshot:
# Pin 16 is at the top left of the symbol box!
# Pin 30 is at the bottom left!
# Pin 15 is at top right!
# Pin 1 is at bottom right!
# Why? Because rotation 180 flips X and Y!
# Let's print the actual pins and any wires touching them.

import re
lines = text.splitlines()
for i, line in enumerate(lines):
    if 'CLUTCH_SIG' in line or 'FB_INJ_3V3' in line or 'VSS_PULSE' in line or 'FB_IGN_3V3' in line:
        print(f"Line {i}: {line}")
        # print surrounding lines
        for j in range(max(0, i-5), min(len(lines), i+6)):
            print(f"  {lines[j]}")
        print('-'*40)
