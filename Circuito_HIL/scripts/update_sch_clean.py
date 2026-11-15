sch_path = r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch'
with open(sch_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Exact target block for pin 17, 18, 19
old_block = '''				(pin output line
					(at 17.78 -15.24 180)
					(length 2.54)
					(name "D15_(CLUTCH)"
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
				)
				(pin bidirectional line
					(at 17.78 -12.7 180)
					(length 2.54)
					(name "D2"
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
				)
				(pin bidirectional line
					(at 17.78 -10.16 180)
					(length 2.54)
					(name "D0"
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

new_block = '''				(pin power_in line
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
				)
				(pin bidirectional line
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
				)
				(pin bidirectional line
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

if old_block in text:
    text = text.replace(old_block, new_block)
    print("Replaced symbol pins 17, 18, 19 successfully!")
else:
    print("WARNING: old_block not found!")

# Now check the wires outside U1:
# The label "CLUTCH_SIG" was at (72.39, 124.46).
# Since Pin 18 (D15_CLUTCH) is at Y=127.00, we move the CLUTCH_SIG label and wire to Y=127.00!
# And at Y=124.46 (Pin 17 GND), we attach a GND wire!
text = text.replace('(at 72.39 124.46 180)', '(at 72.39 127 180)')
text = text.replace('(xy 82.55 124.46) (xy 72.39 124.46)', '(xy 82.55 127) (xy 72.39 127)')

# Wire from 82.55 124.46 to 72.39 124.46 for GND:
# Find a place inside (kicad_sch ...) before the last closing parenthesis to insert GND wire and label:
last_paren = text.rfind(')')
gnd_entry = '''
	(wire
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
	)
'''
text = text[:last_paren] + gnd_entry + text[last_paren:]

# And for Pin 19 (D2 at 82.55, 129.54):
# Move the no_connect marker from 127 to 129.54:
text = text.replace('(at 82.55 127)', '(at 82.55 129.54)')

with open(sch_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Arquivo salvo com sucesso!")
