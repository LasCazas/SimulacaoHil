import re

sch_path = r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch'
with open(sch_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Symbol Pins for ESP32 in HIL:ESP32_DevKit_V1_30Pin
# We need to replace Pin 17, 18, 19 in ESP32_DevKit_V1_30Pin_1_1
# Let's inspect the exact lines for pins 16..20 in the symbol:
old_pin17_pattern = r'(\(pin\s+output\s+line\s+\(at\s+17\.78\s+-15\.24\s+180\)\s+\(length\s+2\.54\)\s+\(name\s+"D15_\(CLUTCH\)"[\s\S]*?\(number\s+"17"[\s\S]*?\)\s*\))'
old_pin18_pattern = r'(\(pin\s+bidirectional\s+line\s+\(at\s+17\.78\s+-12\.7\s+180\)\s+\(length\s+2\.54\)\s+\(name\s+"D2"[\s\S]*?\(number\s+"18"[\s\S]*?\)\s*\))'
old_pin19_pattern = r'(\(pin\s+bidirectional\s+line\s+\(at\s+17\.78\s+-10\.16\s+180\)\s+\(length\s+2\.54\)\s+\(name\s+"D0"[\s\S]*?\(number\s+"19"[\s\S]*?\)\s*\))'

new_pin17 = '''(pin power_in line
					(at 17.78 -15.24 180)
					(length 2.54)
					(name "GND"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "17"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)'''

new_pin18 = '''(pin bidirectional line
					(at 17.78 -12.7 180)
					(length 2.54)
					(name "D15_(CLUTCH)"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "18"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)'''

new_pin19 = '''(pin bidirectional line
					(at 17.78 -10.16 180)
					(length 2.54)
					(name "D2"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "19"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)'''

text = re.sub(old_pin17_pattern, new_pin17, text)
text = re.sub(old_pin18_pattern, new_pin18, text)
text = re.sub(old_pin19_pattern, new_pin19, text)

# 2. Update CLUTCH_SIG label and wire at ESP32:
# Old: label at 72.39 124.46
# Wire: from 82.55 124.46 to 72.39 124.46
# Pin 18 is at Y = 127.00!
# We move the CLUTCH_SIG label to 72.39 127.00
# And wire from 82.55 127.00 to 72.39 127.00
text = text.replace('(at 72.39 124.46 180)', '(at 72.39 127 180)')
text = text.replace('(xy 82.55 124.46) (xy 72.39 124.46)', '(xy 82.55 127) (xy 72.39 127)')

# And for Pin 17 (GND at 82.55, 124.46):
# Wire from 82.55 124.46 to 77.47 124.46 and attach a GND power symbol or GND label!
# Let's add a GND power_in connection at 82.55 124.46:
gnd_conn = '''	(wire
		(pts
			(xy 82.55 124.46) (xy 72.39 124.46)
		)
		(stroke
			(width 0)
			(type default)
		)
		(uuid "c1a2b3c4-0017-0000-0000-000000000017")
	)
	(label "GND"
		(at 72.39 124.46 180)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify right)
		)
		(uuid "c1a2b3c4-0017-0000-0000-000000000018")
	)'''

if '000000000017' not in text:
    text += '\n' + gnd_conn

# For Pin 19 (D2 at 82.55, 129.54):
# Move the no_connect from 127.00 to 129.54:
text = text.replace('(at 82.55 127)', '(at 82.55 129.54)')

with open(sch_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Circuito_HIL.kicad_sch atualizado com sucesso!")
