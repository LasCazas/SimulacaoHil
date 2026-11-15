import re

with open(r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

# Let's inspect the pins of ESP32_DevKit_V1_30Pin in lib_symbols
sym_start = sch.find('(symbol "ESP32_DevKit_V1_30Pin"')
sym_end = sch.find('\n\t\t)', sym_start)
sym_block = sch[sym_start:sym_end]

print("Found symbol block of length:", len(sym_block))

# Find U1 instance
for m in re.finditer(r'\(symbol\s+\(lib_id "HIL:ESP32_DevKit_V1_30Pin"\)(.*?)\(uuid', sch, re.DOTALL):
    print("Instance header:", m.group(0)[:200])

# Find pins in the symbol block
pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+[\d\.\-]+\s+[\d\.\-]+\s+[\d\.\-]+\).*?\(number\s+"(\d+)".*?\)', sym_block, re.DOTALL)
print("Symbol pins count:", len(pins))
