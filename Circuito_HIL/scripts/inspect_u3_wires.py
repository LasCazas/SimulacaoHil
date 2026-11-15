with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# find labels around U3
lines = text.splitlines()
for i, line in enumerate(lines):
    if any(k in line for k in ['SPEEDUINO_IGN', 'SPEEDUINO_INJ', '237.49', '219.71', '255.27']):
        print(f"Line {i}: {line}")
