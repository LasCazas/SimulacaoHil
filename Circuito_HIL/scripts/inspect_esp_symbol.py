with open('Circuito_HIL/Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('ESP32_DevKit_V1_30Pin_1_1')
chunk = text[pos:pos+10000]
import re
pins = re.findall(r'\(name "(.*?)"\s+\(effects.*?\)\s+\)\s+\(number "(.*?)"', chunk, re.DOTALL)
for name, num in pins:
    print(f"Pin {num:>2}: {name}")
