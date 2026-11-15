with open('Circuito_HIL/Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

for block in text.split('(symbol'):
    if any(k in block for k in ['"R1"', '"R2"', '"C1"', '"C2"']):
        print("SYMBOL:")
        lines = block.split('\n')[:15]
        print('\n'.join(lines))
        print('-'*30)
