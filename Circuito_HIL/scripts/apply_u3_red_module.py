import re

sch_path = r'C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\Circuito_HIL\Circuito_HIL.kicad_sch'
with open(sch_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Symbol Definition in lib_symbols
# Find the symbol definition block of Logic_Level_Converter_4CH
sym_start = text.find('(symbol "HIL:Logic_Level_Converter_4CH"')
sym_end = text.find('\n\t\t)', sym_start)

new_u3_symbol = '''(symbol "HIL:Logic_Level_Converter_4CH"
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(in_pos_files yes)
			(duplicate_pin_numbers_are_jumpers no)
			(property "Reference" "U3"
				(at -15.24 15.24 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.524 1.524)
					)
					(justify left)
				)
			)
			(property "Value" "Level_Converter_SparkFun"
				(at 0 15.24 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.524 1.524)
					)
					(justify left)
				)
			)
			(property "Footprint" "Module:Level_Converter_SparkFun"
				(at 0 -15.24 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Description" ""
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(symbol "Logic_Level_Converter_4CH_0_1"
				(rectangle
					(start -15.24 12.7)
					(end 15.24 -12.7)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type background)
					)
				)
			)
			(symbol "Logic_Level_Converter_4CH_1_1"
				(pin passive line
					(at -17.78 7.62 0)
					(length 2.54)
					(name "TXO1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin input line
					(at -17.78 5.08 0)
					(length 2.54)
					(name "RXI1_(IGN)"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin power_in line
					(at -17.78 0 0)
					(length 2.54)
					(name "HV_(5V)"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "3"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin power_in line
					(at -17.78 -5.08 0)
					(length 2.54)
					(name "GND_(HV)"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "4"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin input line
					(at -17.78 -7.62 0)
					(length 2.54)
					(name "RXI2_(INJ)"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "5"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin passive line
					(at -17.78 -10.16 0)
					(length 2.54)
					(name "TXO2"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "6"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin passive line
					(at 17.78 7.62 180)
					(length 2.54)
					(name "TXI1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "7"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin output line
					(at 17.78 5.08 180)
					(length 2.54)
					(name "RXO1_(->_D5)"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "8"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin power_in line
					(at 17.78 0 180)
					(length 2.54)
					(name "LV_(3V3)"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "9"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin power_in line
					(at 17.78 -5.08 180)
					(length 2.54)
					(name "GND_(LV)"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "10"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin output line
					(at 17.78 -7.62 180)
					(length 2.54)
					(name "RXO2_(->_D4)"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "11"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin passive line
					(at 17.78 -10.16 180)
					(length 2.54)
					(name "TXI2"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "12"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
			)'''

# Replace symbol block
text = text[:sym_start] + new_u3_symbol + text[sym_end:]

# 2. Update Wires and Labels around U3
# In schematic:
# Pin 1 & 7 are at Y=165.10 (7.62 above center 172.72) -> now TXO1 / TXI1 -> add no_connect
# Pin 2 & 8 are at Y=167.64 (5.08 above center 172.72) -> now RXI1 (IGN) / RXO1 (D5) -> connect SPEEDUINO_IGN and FB_IGN_3V3
# Pin 3 & 9 are at Y=172.72 (center 172.72) -> now HV (5V) / LV (3V3) -> connect +5V and +3V3
# Pin 4 & 10 are at Y=177.80 (5.08 below center) -> now GND / GND -> connect GND
# Pin 5 & 11 are at Y=180.34 (7.62 below center) -> now RXI2 (INJ) / RXO2 (D4) -> connect SPEEDUINO_INJ and FB_INJ_3V3
# Pin 6 & 12 are at Y=182.88 (10.16 below center) -> now TXO2 / TXI2 -> add no_connect

# Let's update the coordinates of labels and power symbols around U3:
# Previously:
# +5V at (209.55, 165.1) -> move to (209.55, 172.72)
# +3V3 at (265.43, 165.1) -> move to (265.43, 172.72)
# GND at (209.55, 167.64) -> move to (209.55, 177.8)
# GND at (265.43, 167.64) -> move to (265.43, 177.8)
# SPEEDUINO_IGN at (209.55, 172.72) -> move to (209.55, 167.64)
# FB_IGN_3V3 at (265.43, 172.72) -> move to (265.43, 167.64)
# SPEEDUINO_INJ at (209.55, 177.8) -> move to (209.55, 180.34)
# FB_INJ_3V3 at (265.43, 177.8) -> move to (265.43, 180.34)

# And no_connects:
# Old no_connects were at:
# (219.71, 180.34), (255.27, 180.34)
# (219.71, 182.88), (255.27, 182.88)
# Move first pair to (219.71, 165.1), (255.27, 165.1) (pins 1 and 7)!
# Second pair remains at (219.71, 182.88), (255.27, 182.88) (pins 6 and 12)!

# Let's perform these swaps:
# We can use placeholder tokens to swap cleanly without cross-over
text = text.replace('(at 209.55 165.1 0)', '(at 209.55 PLACEHOLDER_172_72 0)')
text = text.replace('(at 265.43 165.1 0)', '(at 265.43 PLACEHOLDER_172_72 0)')

text = text.replace('(at 209.55 167.64 0)', '(at 209.55 PLACEHOLDER_177_80 0)')
text = text.replace('(at 265.43 167.64 0)', '(at 265.43 PLACEHOLDER_177_80 0)')

text = text.replace('(at 209.55 172.72 180)', '(at 209.55 167.64 180)')
text = text.replace('(at 265.43 172.72 0)', '(at 265.43 167.64 0)')

text = text.replace('(at 209.55 177.8 180)', '(at 209.55 180.34 180)')
text = text.replace('(at 265.43 177.8 0)', '(at 265.43 180.34 0)')

text = text.replace('PLACEHOLDER_172_72', '172.72')
text = text.replace('PLACEHOLDER_177_80', '177.8')

# Move no_connect from 180.34 to 165.1:
text = text.replace('(at 219.71 180.34)', '(at 219.71 165.1)')
text = text.replace('(at 255.27 180.34)', '(at 255.27 165.1)')

# Wires around U3:
# The wires connect (219.71, Y) to (209.55, Y) and (255.27, Y) to (265.43, Y):
# At Y=165.1, we had wires for +5V and +3V3. Since pins 1 and 7 are now NC, remove wires at 165.1 and add at 180.34!
# Let's adjust wire coordinates:
text = text.replace('(xy 219.71 165.1) (xy 209.55 165.1)', '(xy 219.71 180.34) (xy 209.55 180.34)')
text = text.replace('(xy 255.27 165.1) (xy 265.43 165.1)', '(xy 255.27 180.34) (xy 265.43 180.34)')

with open(sch_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Circuito_HIL.kicad_sch atualizado para o módulo SparkFun Vermelho!")
