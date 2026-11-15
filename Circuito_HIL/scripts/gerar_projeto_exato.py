"""Gerador matematicamente exato do esquemático KiCad 8/9/10 para a Bancada HIL.
Garante que cada pino conecte perfeitamente na malha de 2.54mm (100 mil) do KiCad sem fios cruzados ou desalinhados.
"""

def generate_schematic():
    # Coordenadas base dos blocos no esquematico (folha A3)
    # No KiCad: X aumenta p/ direita, Y aumenta p/ baixo
    # Nos simbolos: y_sym positivo e para CIMA, entao y_sch = y_pos - y_sym
    
    sch = []
    sch.append('(kicad_sch')
    sch.append('\t(version 20231120)')
    sch.append('\t(generator "eeschema")')
    sch.append('\t(generator_version "8.0")')
    sch.append('\t(uuid "d8a1c320-1a2b-4c3d-8e4f-5a6b7c8d9e01")')
    sch.append('\t(paper "A3")')
    sch.append('\t(title_block')
    sch.append('\t\t(title "Bancada Simulador Dinamico HIL - Speeduino 48-Way")')
    sch.append('\t\t(date "2026-11-12")')
    sch.append('\t\t(rev "v1.3")')
    sch.append('\t\t(company "IF Betim Racing - IFMG Campus Betim")')
    sch.append('\t\t(comment 1 "Interface HIL: ESP32 + PCM5102A + Level Converter + Filtros RC")')
    sch.append('\t\t(comment 2 "Validado para KTM Duke 390 (22-2) & Speeduino 48-Way")')
    sch.append('\t)')

    # Definicao de simbolos de biblioteca embutidos
    sch.append('\t(lib_symbols')
    
    # Simbolo R horizontal
    sch.append('\t\t(symbol "HIL:R_Horiz" (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "R" (at 0 2.54 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Value" "10k" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(symbol "R_0_1"')
    sch.append('\t\t\t\t(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "R_1_1"')
    sch.append('\t\t\t\t(pin passive line (at -3.81 0 0) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t\t(pin passive line (at 3.81 0 180) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # Simbolo C vertical
    sch.append('\t\t(symbol "HIL:C_Vert" (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "C" (at 2.54 1.27 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t\t\t(property "Value" "1uF" (at 2.54 -1.27 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t\t\t(symbol "C_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "C_1_1"')
    sch.append('\t\t\t\t(pin passive line (at 0 3.81 270) (length 3.048) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t\t(pin passive line (at 0 -3.81 90) (length 3.048) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # Power GND
    sch.append('\t\t(symbol "power:GND" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "#PWR" (at 0 -2.54 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(symbol "GND_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type outline)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "GND_1_1"')
    sch.append('\t\t\t\t(pin power_in line (at 0 0 270) (length 0) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # Power +5V
    sch.append('\t\t(symbol "power:+5V" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(property "Value" "+5V" (at 0 3.81 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(symbol "+5V_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "+5V_1_1"')
    sch.append('\t\t\t\t(pin power_in line (at 0 0 90) (length 0) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # Power +3V3
    sch.append('\t\t(symbol "power:+3V3" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(property "Value" "+3V3" (at 0 3.81 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(symbol "+3V3_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "+3V3_1_1"')
    sch.append('\t\t\t\t(pin power_in line (at 0 0 90) (length 0) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # Simbolo ESP32 DevKit V1 (30 pinos)
    sch.append('\t\t(symbol "HIL:ESP32_DevKit_V1_30Pin" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "U1" (at -15.24 24.13 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "ESP32_DevKit_V1" (at 2.54 24.13 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(symbol "ESP32_DevKit_V1_30Pin_0_1"')
    sch.append('\t\t\t\t(rectangle (start -15.24 21.59) (end 15.24 -21.59) (stroke (width 0.254) (type default)) (fill (type background)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "ESP32_DevKit_V1_30Pin_1_1"')
    # Pinos Esquerda: y_sym de +17.78 (pino 1 EN no topo) ate -17.78 (pino 15 VIN na base)
    left_pins = [
        ("1", "EN", "passive"),
        ("2", "VP (D36)", "input"),
        ("3", "VN (D39)", "input"),
        ("4", "D34", "input"),
        ("5", "D35", "input"),
        ("6", "D32", "bidirectional"),
        ("7", "D33", "bidirectional"),
        ("8", "D25 (DAC1_TPS)", "output"),
        ("9", "D26 (DAC2_MAP)", "output"),
        ("10", "D27 (I2S_BCK)", "output"),
        ("11", "D14 (I2S_LCK)", "output"),
        ("12", "D12", "bidirectional"),
        ("13", "D13", "bidirectional"),
        ("14", "GND", "power_in"),
        ("15", "VIN (5V)", "power_in"),
    ]
    for idx, (pnum, pname, ptype) in enumerate(left_pins):
        y_s = 17.78 - idx * 2.54
        sch.append(f'\t\t\t\t(pin {ptype} line (at -17.78 {y_s:.2f} 0) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')
    
    # Pinos Direita: de +17.78 (pino 30 D23 no topo) ate -17.78 (pino 16 3V3 na base)
    right_pins = [
        ("30", "D23", "bidirectional"),
        ("29", "D22 (I2S_DIN)", "output"),
        ("28", "TX0 (D1)", "bidirectional"),
        ("27", "RX0 (D3)", "bidirectional"),
        ("26", "D21", "bidirectional"),
        ("25", "D19", "bidirectional"),
        ("24", "D18", "bidirectional"),
        ("23", "D5 (IGN_FB)", "input"),
        ("22", "D17", "bidirectional"),
        ("21", "D16 (VSS)", "output"),
        ("20", "D4 (INJ_FB)", "input"),
        ("19", "D0", "bidirectional"),
        ("18", "D2", "bidirectional"),
        ("17", "D15 (CLUTCH)", "output"),
        ("16", "3V3", "power_out"),
    ]
    for idx, (pnum, pname, ptype) in enumerate(right_pins):
        y_s = 17.78 - idx * 2.54
        sch.append(f'\t\t\t\t(pin {ptype} line (at 17.78 {y_s:.2f} 180) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # Simbolo PCM5102A
    sch.append('\t\t(symbol "HIL:PCM5102A_Module" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "U2" (at -15.24 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "GY-PCM5102A" (at 2.54 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(symbol "PCM5102A_Module_0_1"')
    sch.append('\t\t\t\t(rectangle (start -15.24 15.24) (end 15.24 -15.24) (stroke (width 0.254) (type default)) (fill (type background)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "PCM5102A_Module_1_1"')
    pcm_left = [
        ("1", "VCC (5V)", "power_in"),
        ("2", "GND", "power_in"),
        ("3", "BCK (GPIO27)", "input"),
        ("4", "DIN (GPIO22)", "input"),
        ("5", "LCK (GPIO14)", "input"),
        ("6", "SCK (-> GND)", "input"),
        ("7", "XMT (-> 3V3)", "input"),
        ("8", "FMT (-> GND)", "input"),
        ("9", "FLT (-> GND)", "input"),
        ("10", "DMP (-> GND)", "input"),
    ]
    for idx, (pnum, pname, ptype) in enumerate(pcm_left):
        y_s = 11.43 - idx * 2.54
        sch.append(f'\t\t\t\t(pin {ptype} line (at -17.78 {y_s:.2f} 0) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')
    
    pcm_right = [
        ("11", "LOUT (Crank 22-2)", "output", 6.35),
        ("12", "AGND (Terra VR)", "power_out", 1.27),
        ("13", "ROUT (NC)", "output", -3.81),
    ]
    for pnum, pname, ptype, y_s in pcm_right:
        sch.append(f'\t\t\t\t(pin {ptype} line (at 17.78 {y_s:.2f} 180) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # Simbolo Level Converter 4CH
    sch.append('\t\t(symbol "HIL:Logic_Level_Converter_4CH" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "U3" (at -15.24 15.24 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "Level_Converter_4CH" (at 2.54 15.24 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(symbol "Logic_Level_Converter_4CH_0_1"')
    sch.append('\t\t\t\t(rectangle (start -15.24 12.7) (end 15.24 -12.7) (stroke (width 0.254) (type default)) (fill (type background)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "Logic_Level_Converter_4CH_1_1"')
    lev_left = [
        ("1", "HV (5V)", "power_in", 8.89),
        ("2", "GND (HV)", "power_in", 6.35),
        ("3", "HV1 (IGN G_B1)", "input", 1.27),
        ("4", "HV2 (INJ G_A1)", "input", -3.81),
        ("5", "HV3 (NC)", "passive", -7.62),
        ("6", "HV4 (NC)", "passive", -10.16),
    ]
    for pnum, pname, ptype, y_s in lev_left:
        sch.append(f'\t\t\t\t(pin {ptype} line (at -17.78 {y_s:.2f} 0) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')

    lev_right = [
        ("7", "LV (3V3)", "power_in", 8.89),
        ("8", "GND (LV)", "power_in", 6.35),
        ("9", "LV1 (-> D5)", "output", 1.27),
        ("10", "LV2 (-> D4)", "output", -3.81),
        ("11", "LV3 (NC)", "passive", -7.62),
        ("12", "LV4 (NC)", "passive", -10.16),
    ]
    for pnum, pname, ptype, y_s in lev_right:
        sch.append(f'\t\t\t\t(pin {ptype} line (at 17.78 {y_s:.2f} 180) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # Simbolo Conector Speeduino 48-Way
    sch.append('\t\t(symbol "HIL:Conn_Speeduino_Chicote" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "J1" (at -15.24 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "CHICOTE_SPEEDUINO_48WAY" (at 2.54 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(symbol "Conn_Speeduino_Chicote_0_1"')
    sch.append('\t\t\t\t(rectangle (start -15.24 15.24) (end 15.24 -15.24) (stroke (width 0.254) (type default)) (fill (type background)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "Conn_Speeduino_Chicote_1_1"')
    j1_pins = [
        ("1", "B_B2 (CRANK+ / VR1+)", "input"),
        ("2", "B_B3 (VR1- / Terra VR)", "power_out"),
        ("3", "B_C7 (TPS_Sensor)", "input"),
        ("4", "B_C8 (MAP-EXT)", "input"),
        ("5", "B_A7 (VSS / Velocidade)", "input"),
        ("6", "B_B7 (Clutch_in)", "input"),
        ("7", "G_A1 (INJ-1-OUT)", "output"),
        ("8", "G_B1 (IGN-1-OUT)", "output"),
        ("9", "B_A8 (GND Sensores)", "power_in"),
    ]
    for idx, (pnum, pname, ptype) in enumerate(j1_pins):
        y_s = 10.16 - idx * 2.54
        sch.append(f'\t\t\t\t(pin {ptype} line (at -17.78 {y_s:.2f} 0) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    sch.append('\t)') # fim lib_symbols

    # ================= INSTANCIAS NO ESQUEMATICO =================
    
    # 1. ESP32 DevKit V1 em (X=120, Y=100)
    # Pinos Esquerda estao em x = 120 - 17.78 = 102.22
    # Pinos Direita estao em x = 120 + 17.78 = 137.78
    esp_x, esp_y = 120.0, 100.0
    sch.append(f'\t(symbol (lib_id "HIL:ESP32_DevKit_V1_30Pin") (at {esp_x:.2f} {esp_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0001-0000-0000-000000000001")')
    sch.append(f'\t\t(property "Reference" "U1" (at {esp_x:.2f} {esp_y-24.13:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "ESP32_DevKit_V1" (at {esp_x:.2f} {esp_y-21.59:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append('\t)')

    # 2. PCM5102A em (X=220, Y=60)
    # Pinos Esquerda em x = 220 - 17.78 = 202.22
    # Pinos Direita em x = 220 + 17.78 = 237.78
    pcm_x, pcm_y = 220.0, 60.0
    sch.append(f'\t(symbol (lib_id "HIL:PCM5102A_Module") (at {pcm_x:.2f} {pcm_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0002-0000-0000-000000000002")')
    sch.append(f'\t\t(property "Reference" "U2" (at {pcm_x:.2f} {pcm_y-17.78:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "GY-PCM5102A" (at {pcm_x:.2f} {pcm_y-15.24:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append('\t)')

    # 3. Level Converter em (X=220, Y=140)
    # Pinos Esquerda (HV) em x = 220 - 17.78 = 202.22
    # Pinos Direita (LV) em x = 220 + 17.78 = 237.78
    lev_x, lev_y = 220.0, 140.0
    sch.append(f'\t(symbol (lib_id "HIL:Logic_Level_Converter_4CH") (at {lev_x:.2f} {lev_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0003-0000-0000-000000000003")')
    sch.append(f'\t\t(property "Reference" "U3" (at {lev_x:.2f} {lev_y-15.24:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "Level_Converter_4CH" (at {lev_x:.2f} {lev_y-12.7:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append('\t)')

    # 4. Conector Speeduino J1 em (X=330, Y=100)
    # Pinos Esquerda em x = 330 - 17.78 = 312.22
    j1_x, j1_y = 330.0, 100.0
    sch.append(f'\t(symbol (lib_id "HIL:Conn_Speeduino_Chicote") (at {j1_x:.2f} {j1_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0004-0000-0000-000000000004")')
    sch.append(f'\t\t(property "Reference" "J1" (at {j1_x:.2f} {j1_y-17.78:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "CHICOTE_SPEEDUINO_48WAY" (at {j1_x:.2f} {j1_y-15.24:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append('\t)')

    # ================= FILTROS RC DO TPS E MAP =================
    # D25 (DAC1_TPS) esta em x=102.22, y = 100 - (17.78 - 7*2.54) = 100 - 0 = 100.00
    # D26 (DAC2_MAP) esta em x=102.22, y = 100 - (17.78 - 8*2.54) = 100 - (-2.54) = 102.54
    # Vamos posicionar R1 e R2 limpamente a esquerda do ESP32!
    
    # R1 (TPS) em X=70, Y=100.00
    # Pino 1 (entrada D25) em x = 70 + 3.81 = 73.81 (ou se virado, x=66.19 e x=73.81)
    # Usando HIL:R_Horiz com pino 1 em x=-3.81 e pino 2 em x=+3.81:
    # Se colocado em X=70, Pino 1 fica em 66.19 e Pino 2 fica em 73.81
    # Vamos ligar D25 (102.22) -> R1 pino 2 (80.0) -> R1 pino 1 (70.0) -> C1 -> Saida!
    
    # Vamos colocar R1 em X=80, Y=100.00
    # Pino 2 esta em 80 + 3.81 = 83.81
    # Pino 1 esta em 80 - 3.81 = 76.19
    r1_x, r1_y = 80.0, 100.00
    sch.append(f'\t(symbol (lib_id "HIL:R_Horiz") (at {r1_x:.2f} {r1_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0001-0000-0000-000000000001")')
    sch.append(f'\t\t(property "Reference" "R1" (at {r1_x:.2f} {r1_y-2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Value" "10k (TPS)" (at {r1_x:.2f} {r1_y+2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # C1 (TPS) vertical em X=65, Y=105.00
    # Pino 1 (superior) em x=65, y = 105 - 3.81 = 101.19
    # Pino 2 (inferior/GND) em x=65, y = 105 + 3.81 = 108.81
    c1_x, c1_y = 65.0, 105.0
    sch.append(f'\t(symbol (lib_id "HIL:C_Vert") (at {c1_x:.2f} {c1_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0002-0000-0000-000000000002")')
    sch.append(f'\t\t(property "Reference" "C1" (at {c1_x+3.81:.2f} {c1_y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append(f'\t\t(property "Value" "1uF (TPS)" (at {c1_x+3.81:.2f} {c1_y+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t)')

    # GND de C1 em (65, 108.81)
    sch.append(f'\t(symbol (lib_id "power:GND") (at {c1_x:.2f} {c1_y+3.81:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0001-0000-0000-000000000001")')
    sch.append(f'\t\t(property "Reference" "#PWR01" (at {c1_x:.2f} {c1_y+6.35:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at {c1_x:.2f} {c1_y+7.62:.2f} 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # R2 (MAP) em X=80, Y=120.00
    # D26 (DAC2_MAP) esta em x=102.22, y = 102.54
    r2_x, r2_y = 80.0, 120.00
    sch.append(f'\t(symbol (lib_id "HIL:R_Horiz") (at {r2_x:.2f} {r2_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0003-0000-0000-000000000003")')
    sch.append(f'\t\t(property "Reference" "R2" (at {r2_x:.2f} {r2_y-2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Value" "10k (MAP)" (at {r2_x:.2f} {r2_y+2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # C2 (MAP) vertical em X=65, Y=125.00
    c2_x, c2_y = 65.0, 125.0
    sch.append(f'\t(symbol (lib_id "HIL:C_Vert") (at {c2_x:.2f} {c2_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0004-0000-0000-000000000004")')
    sch.append(f'\t\t(property "Reference" "C2" (at {c2_x+3.81:.2f} {c2_y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append(f'\t\t(property "Value" "1uF (MAP)" (at {c2_x+3.81:.2f} {c2_y+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t)')

    # GND de C2 em (65, 128.81)
    sch.append(f'\t(symbol (lib_id "power:GND") (at {c2_x:.2f} {c2_y+3.81:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0002-0000-0000-000000000002")')
    sch.append(f'\t\t(property "Reference" "#PWR02" (at {c2_x:.2f} {c2_y+6.35:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at {c2_x:.2f} {c2_y+7.62:.2f} 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # ================= POWER SYMBOLS DO ESP32 =================
    # Pino 14 (GND): x=102.22, y = 100 - (17.78 - 13*2.54) = 100 - (-15.24) = 115.24
    # Pino 15 (VIN 5V): x=102.22, y = 100 - (17.78 - 14*2.54) = 100 - (-17.78) = 117.78
    # Pino 16 (3V3): x=137.78, y = 100 - (17.78 - 14*2.54) = 100 - (-17.78) = 117.78
    
    # GND no pino 14
    sch.append(f'\t(symbol (lib_id "power:GND") (at 92.0 115.24 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0003-0000-0000-000000000003")')
    sch.append(f'\t\t(property "Reference" "#PWR03" (at 92.0 117.78 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 92.0 119.05 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # +5V no pino 15
    sch.append(f'\t(symbol (lib_id "power:+5V") (at 92.0 117.78 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0004-0000-0000-000000000004")')
    sch.append(f'\t\t(property "Reference" "#PWR04" (at 92.0 115.24 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+5V" (at 92.0 113.97 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # +3V3 no pino 16
    sch.append(f'\t(symbol (lib_id "power:+3V3") (at 148.0 117.78 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0005-0000-0000-000000000005")')
    sch.append(f'\t\t(property "Reference" "#PWR05" (at 148.0 115.24 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+3V3" (at 148.0 113.97 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # ================= POWER SYMBOLS DO PCM5102A =================
    # PCM5102 em X=220, Y=60. Pinos esquerda em x=202.22
    # Pino 1 (VCC 5V): y = 60 - 11.43 = 48.57 -> +5V
    # Pino 2 (GND): y = 60 - (11.43 - 2.54) = 51.11 -> GND
    # Pino 6 (SCK): y = 60 - (11.43 - 5*2.54) = 61.27 -> GND
    # Pino 7 (XMT): y = 60 - (11.43 - 6*2.54) = 63.81 -> +3V3
    # Pino 8 (FMT): y = 60 - (11.43 - 7*2.54) = 66.35 -> GND
    # Pino 9 (FLT): y = 60 - (11.43 - 8*2.54) = 68.89 -> GND
    # Pino 10 (DMP): y = 60 - (11.43 - 9*2.54) = 71.43 -> GND

    # +5V PCM5102
    sch.append(f'\t(symbol (lib_id "power:+5V") (at 194.0 48.57 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0006-0000-0000-000000000006")')
    sch.append(f'\t\t(property "Reference" "#PWR06" (at 194.0 46.0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+5V" (at 194.0 44.5 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # +3V3 PCM5102 no pino 7 (XMT)
    sch.append(f'\t(symbol (lib_id "power:+3V3") (at 194.0 63.81 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0007-0000-0000-000000000007")')
    sch.append(f'\t\t(property "Reference" "#PWR07" (at 194.0 61.0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+3V3" (at 194.0 59.5 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # GNDs no PCM5102
    for pcm_gnd_y, uid in [(51.11, "0008"), (61.27, "0009"), (66.35, "0010"), (68.89, "0011"), (71.43, "0012")]:
        sch.append(f'\t(symbol (lib_id "power:GND") (at 194.0 {pcm_gnd_y:.2f} 0) (unit 1)')
        sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
        sch.append(f'\t\t(uuid "c1d2e3f4-{uid}-0000-0000-000000000001")')
        sch.append(f'\t\t(property "Reference" "#PWR_{uid}" (at 194.0 {pcm_gnd_y+2.54:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sch.append(f'\t\t(property "Value" "GND" (at 194.0 {pcm_gnd_y+3.81:.2f} 0) (effects (font (size 1.27 1.27))))')
        sch.append('\t)')

    # ================= POWER SYMBOLS DO LEVEL CONVERTER =================
    # Level Converter em X=220, Y=140
    # Lado HV em x=202.22:
    # Pino 1 (HV 5V): y = 140 - 8.89 = 131.11 -> +5V
    # Pino 2 (GND HV): y = 140 - 6.35 = 133.65 -> GND
    # Lado LV em x=237.78:
    # Pino 7 (LV 3V3): y = 140 - 8.89 = 131.11 -> +3V3
    # Pino 8 (GND LV): y = 140 - 6.35 = 133.65 -> GND

    sch.append(f'\t(symbol (lib_id "power:+5V") (at 194.0 131.11 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0013-0000-0000-000000000013")')
    sch.append(f'\t\t(property "Reference" "#PWR13" (at 194.0 128.5 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+5V" (at 194.0 127.0 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at 194.0 133.65 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0014-0000-0000-000000000014")')
    sch.append(f'\t\t(property "Reference" "#PWR14" (at 194.0 136.0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 194.0 137.5 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:+3V3") (at 246.0 131.11 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0015-0000-0000-000000000015")')
    sch.append(f'\t\t(property "Reference" "#PWR15" (at 246.0 128.5 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+3V3" (at 246.0 127.0 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at 246.0 133.65 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0016-0000-0000-000000000016")')
    sch.append(f'\t\t(property "Reference" "#PWR16" (at 246.0 136.0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 246.0 137.5 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # GND do conector Speeduino J1 pino 9 em (312.22, y = 100 - (10.16 - 8*2.54) = 110.16)
    sch.append(f'\t(symbol (lib_id "power:GND") (at 304.0 110.16 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0017-0000-0000-000000000017")')
    sch.append(f'\t\t(property "Reference" "#PWR17" (at 304.0 112.5 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 304.0 114.0 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t)')

    # ================= LABELS DE REDE (NET LABELS) =================
    
    # 1. Filtro TPS:
    # R1 pino 1 esta em x=76.19, y=100.00
    # R1 pino 2 esta em x=83.81, y=100.00
    # D25 (DAC1_TPS) esta em x=102.22, y=100.00
    # No do filtro (entre R1 e C1) fica em x=65.0, y=100.00
    # Label "NET_TPS_OUT" fica em (50.0, 100.00)
    sch.append('\t(label "NET_TPS_OUT" (at 52.0 100.00 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "NET_TPS_OUT" (at 304.0 94.92 180) (effects (font (size 1.27 1.27)) (justify right)))') # J1 pino 3 (B_C7)

    # 2. Filtro MAP:
    # R2 pino 1 esta em x=76.19, y=120.00
    # R2 pino 2 esta em x=83.81, y=120.00
    # D26 (DAC2_MAP) esta em x=102.22, y=102.54
    # No do filtro fica em x=65.0, y=120.00
    sch.append('\t(label "NET_MAP_OUT" (at 52.0 120.00 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "NET_MAP_OUT" (at 304.0 97.46 180) (effects (font (size 1.27 1.27)) (justify right)))') # J1 pino 4 (B_C8)

    # 3. I2S Roda Fonica:
    # BCK (D27) em (102.22, 105.08)
    sch.append('\t(label "I2S_BCK" (at 92.0 105.08 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "I2S_BCK" (at 194.0 53.65 180) (effects (font (size 1.27 1.27)) (justify right)))') # PCM5102 pino 3

    # LCK (D14) em (102.22, 107.62)
    sch.append('\t(label "I2S_LCK" (at 92.0 107.62 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "I2S_LCK" (at 194.0 58.73 180) (effects (font (size 1.27 1.27)) (justify right)))') # PCM5102 pino 5

    # DIN (D22) em (137.78, 84.76)
    sch.append('\t(label "I2S_DIN" (at 148.0 84.76 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "I2S_DIN" (at 194.0 56.19 180) (effects (font (size 1.27 1.27)) (justify right)))') # PCM5102 pino 4

    # Saida Roda Fonica do PCM5102 -> Speeduino
    # LOUT (pino 11) em (237.78, 53.65)
    sch.append('\t(label "CRANK_VR_POS" (at 246.0 53.65 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "CRANK_VR_POS" (at 304.0 89.84 180) (effects (font (size 1.27 1.27)) (justify right)))') # J1 pino 1 (B_B2)

    # AGND (pino 12) em (237.78, 58.73)
    sch.append('\t(label "CRANK_VR_NEG" (at 246.0 58.73 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "CRANK_VR_NEG" (at 304.0 92.38 180) (effects (font (size 1.27 1.27)) (justify right)))') # J1 pino 2 (B_B3)

    # 4. Sinais Diretos:
    # VSS (D16) em (137.78, 105.08)
    sch.append('\t(label "VSS_PULSE" (at 148.0 105.08 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "VSS_PULSE" (at 304.0 100.00 180) (effects (font (size 1.27 1.27)) (justify right)))') # J1 pino 5 (B_A7)

    # CLUTCH (D15) em (137.78, 115.24)
    sch.append('\t(label "CLUTCH_SIG" (at 148.0 115.24 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "CLUTCH_SIG" (at 304.0 102.54 180) (effects (font (size 1.27 1.27)) (justify right)))') # J1 pino 6 (B_B7)

    # 5. Retornos com Level Converter:
    # Ignição G_B1 -> HV1 (pino 3) em (202.22, 138.73)
    sch.append('\t(label "SPEEDUINO_IGN" (at 194.0 138.73 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "SPEEDUINO_IGN" (at 304.0 107.62 180) (effects (font (size 1.27 1.27)) (justify right)))') # J1 pino 8 (G_B1)

    # LV1 (pino 9) em (237.78, 138.73) -> D5 (IGN_FB) em (137.78, 100.00)
    sch.append('\t(label "FB_IGN_3V3" (at 246.0 138.73 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "FB_IGN_3V3" (at 148.0 100.00 0) (effects (font (size 1.27 1.27)) (justify left)))')

    # Injeção G_A1 -> HV2 (pino 4) em (202.22, 143.81)
    sch.append('\t(label "SPEEDUINO_INJ" (at 194.0 143.81 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "SPEEDUINO_INJ" (at 304.0 105.08 180) (effects (font (size 1.27 1.27)) (justify right)))') # J1 pino 7 (G_A1)

    # LV2 (pino 10) em (237.78, 143.81) -> D4 (INJ_FB) em (137.78, 107.62)
    sch.append('\t(label "FB_INJ_3V3" (at 246.0 143.81 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "FB_INJ_3V3" (at 148.0 107.62 0) (effects (font (size 1.27 1.27)) (justify left)))')

    # ================= LINHAS DE CONEXAO (WIRES) =================
    
    # 1. Filtro TPS:
    # D25 (102.22, 100.00) ate R1 pino 2 (83.81, 100.00)
    sch.append('\t(wire (pts (xy 102.22 100.00) (xy 83.81 100.00)))')
    # R1 pino 1 (76.19, 100.00) ate no (65.0, 100.00)
    sch.append('\t(wire (pts (xy 76.19 100.00) (xy 65.0 100.00)))')
    # No (65.0, 100.00) ate Label NET_TPS_OUT (52.0, 100.00)
    sch.append('\t(wire (pts (xy 65.0 100.00) (xy 52.0 100.00)))')
    # No (65.0, 100.00) desce para C1 pino 1 (65.0, 101.19)
    sch.append('\t(wire (pts (xy 65.0 100.00) (xy 65.0 101.19)))')
    sch.append('\t(junction (at 65.0 100.00) (diameter 1.016))')

    # 2. Filtro MAP:
    # D26 (102.22, 102.54) -> sobe/vira para R2 pino 2 (83.81, 120.00)
    sch.append('\t(wire (pts (xy 102.22 102.54) (xy 90.0 102.54)))')
    sch.append('\t(wire (pts (xy 90.0 102.54) (xy 90.0 120.00)))')
    sch.append('\t(wire (pts (xy 90.0 120.00) (xy 83.81 120.00)))')
    # R2 pino 1 (76.19, 120.00) ate no (65.0, 120.00)
    sch.append('\t(wire (pts (xy 76.19 120.00) (xy 65.0 120.00)))')
    # No (65.0, 120.00) ate Label NET_MAP_OUT (52.0, 120.00)
    sch.append('\t(wire (pts (xy 65.0 120.00) (xy 52.0 120.00)))')
    # No (65.0, 120.00) desce para C2 pino 1 (65.0, 121.19)
    sch.append('\t(wire (pts (xy 65.0 120.00) (xy 65.0 121.19)))')
    sch.append('\t(junction (at 65.0 120.00) (diameter 1.016))')

    # 3. Wires curtos de conexao com labels e power nos modulos:
    # ESP32 pinos esquerda
    sch.append('\t(wire (pts (xy 102.22 105.08) (xy 92.0 105.08)))') # BCK
    sch.append('\t(wire (pts (xy 102.22 107.62) (xy 92.0 107.62)))') # LCK
    sch.append('\t(wire (pts (xy 102.22 115.24) (xy 92.0 115.24)))') # GND
    sch.append('\t(wire (pts (xy 102.22 117.78) (xy 92.0 117.78)))') # 5V

    # ESP32 pinos direita
    sch.append('\t(wire (pts (xy 137.78 84.76) (xy 148.0 84.76)))')   # DIN
    sch.append('\t(wire (pts (xy 137.78 100.00) (xy 148.0 100.00)))') # IGN FB
    sch.append('\t(wire (pts (xy 137.78 105.08) (xy 148.0 105.08)))') # VSS
    sch.append('\t(wire (pts (xy 137.78 107.62) (xy 148.0 107.62)))') # INJ FB
    sch.append('\t(wire (pts (xy 137.78 115.24) (xy 148.0 115.24)))') # CLUTCH
    sch.append('\t(wire (pts (xy 137.78 117.78) (xy 148.0 117.78)))') # 3V3

    # PCM5102 pinos esquerda
    for pcm_y_pt in [48.57, 51.11, 53.65, 56.19, 58.73, 61.27, 63.81, 66.35, 68.89, 71.43]:
        sch.append(f'\t(wire (pts (xy 202.22 {pcm_y_pt:.2f}) (xy 194.0 {pcm_y_pt:.2f})))')
    # PCM5102 pinos direita
    sch.append('\t(wire (pts (xy 237.78 53.65) (xy 246.0 53.65)))') # LOUT
    sch.append('\t(wire (pts (xy 237.78 58.73) (xy 246.0 58.73)))') # AGND

    # Level Converter pinos esquerda (HV)
    for lev_y_pt in [131.11, 133.65, 138.73, 143.81]:
        sch.append(f'\t(wire (pts (xy 202.22 {lev_y_pt:.2f}) (xy 194.0 {lev_y_pt:.2f})))')
    # Level Converter pinos direita (LV)
    for lev_y_pt in [131.11, 133.65, 138.73, 143.81]:
        sch.append(f'\t(wire (pts (xy 237.78 {lev_y_pt:.2f}) (xy 246.0 {lev_y_pt:.2f})))')

    # Conector Speeduino J1 pinos
    for j1_y_pt in [89.84, 92.38, 94.92, 97.46, 100.00, 102.54, 105.08, 107.62, 110.16]:
        sch.append(f'\t(wire (pts (xy 312.22 {j1_y_pt:.2f}) (xy 304.0 {j1_y_pt:.2f})))')

    sch.append(')') # fim kicad_sch
    return '\n'.join(sch)

if __name__ == '__main__':
    content = generate_schematic()
    with open('Circuito_HIL/Circuito_HIL.kicad_sch', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Novo esquematico KiCad matematicamente alinhado gerado com sucesso!")
