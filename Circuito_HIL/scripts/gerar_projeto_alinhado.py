"""Gerador corrigido e alinhado do esquemático KiCad para a Bancada HIL.
Corrige todas as posições dos pinos, filtros RC, I2S e alimentações.
"""

def generate_clean_schematic():
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
    sch.append('\t\t(rev "v1.4")')
    sch.append('\t\t(company "IF Betim Racing - IFMG Campus Betim")')
    sch.append('\t\t(comment 1 "Interface HIL: ESP32 + PCM5102A + Level Converter + Filtros RC")')
    sch.append('\t\t(comment 2 "Validado para KTM Duke 390 (22-2) & Speeduino 48-Way")')
    sch.append('\t)')

    sch.append('\t(lib_symbols')
    
    # Device:R
    sch.append('\t\t(symbol "Device:R" (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Footprint" "" (at -1.778 0 90) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "R_0_1"')
    sch.append('\t\t\t\t(rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "R_1_1"')
    sch.append('\t\t\t\t(pin passive line (at 0 3.81 270) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t\t(pin passive line (at 0 -3.81 90) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # Device:C
    sch.append('\t\t(symbol "Device:C" (pin_numbers hide) (pin_names (offset 0.254)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "C" (at 1.524 1.524 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t\t\t(property "Value" "C" (at 1.524 -1.524 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t\t\t(property "Footprint" "" (at 0.9652 -3.81 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "C_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "C_1_1"')
    sch.append('\t\t\t\t(pin passive line (at 0 3.81 270) (length 3.048) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t\t(pin passive line (at 0 -3.81 90) (length 3.048) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # Power Symbols
    sch.append('\t\t(symbol "power:GND" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "#PWR" (at 0 -2.54 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "GND_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type outline)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "GND_1_1"')
    sch.append('\t\t\t\t(pin power_in line (at 0 0 270) (length 0) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    sch.append('\t\t(symbol "power:+5V" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(property "Value" "+5V" (at 0 3.81 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "+5V_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "+5V_1_1"')
    sch.append('\t\t\t\t(pin power_in line (at 0 0 90) (length 0) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    sch.append('\t\t(symbol "power:+3V3" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(property "Value" "+3V3" (at 0 3.81 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "+3V3_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "+3V3_1_1"')
    sch.append('\t\t\t\t(pin power_in line (at 0 0 90) (length 0) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # ESP32 DevKit V1 30Pin
    sch.append('\t\t(symbol "HIL:ESP32_DevKit_V1_30Pin" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "U1" (at -15.24 24.13 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "ESP32_DevKit_V1" (at 2.54 24.13 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Footprint" "Module:ESP32_DevKit_V1_30Pin" (at 0 -24.13 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "ESP32_DevKit_V1_30Pin_0_1"')
    sch.append('\t\t\t\t(rectangle (start -15.24 22.86) (end 15.24 -22.86) (stroke (width 0.254) (type default)) (fill (type background)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "ESP32_DevKit_V1_30Pin_1_1"')
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

    # PCM5102A Module
    sch.append('\t\t(symbol "HIL:PCM5102A_Module" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "U2" (at -15.24 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "GY-PCM5102A" (at 2.54 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Footprint" "Module:PCM5102A_Module" (at 0 -17.78 0) (effects (font (size 1.27 1.27)) hide))')
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

    # Level Converter 4CH
    sch.append('\t\t(symbol "HIL:Logic_Level_Converter_4CH" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "U3" (at -15.24 15.24 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "Level_Converter_4CH" (at 2.54 15.24 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Footprint" "Module:Level_Converter_4CH" (at 0 -15.24 0) (effects (font (size 1.27 1.27)) hide))')
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

    # Conector Speeduino 48-Way
    sch.append('\t\t(symbol "HIL:Conn_Speeduino_Chicote" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "J1" (at -15.24 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "CHICOTE_SPEEDUINO_48WAY" (at 2.54 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Footprint" "Connector_TerminalBlock:TerminalBlock_bornier-9_P5.08mm" (at 0 -17.78 0) (effects (font (size 1.27 1.27)) hide))')
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

    # ================= POSICIONAMENTO DOS COMPONENTES =================
    
    # 1. ESP32 DevKit V1 em (X=115.0, Y=101.60)
    esp_x, esp_y = 115.0, 101.60
    sch.append(f'\t(symbol (lib_id "HIL:ESP32_DevKit_V1_30Pin") (at {esp_x:.2f} {esp_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0001-0000-0000-000000000001")')
    sch.append(f'\t\t(property "Reference" "U1" (at {esp_x:.2f} {esp_y-24.13:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "ESP32_DevKit_V1" (at {esp_x:.2f} {esp_y-21.59:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Footprint" "Module:ESP32_DevKit_V1_30Pin" (at {esp_x:.2f} {esp_y+25:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # 2. PCM5102A em (X=215.0, Y=65.0)
    pcm_x, pcm_y = 215.0, 65.0
    sch.append(f'\t(symbol (lib_id "HIL:PCM5102A_Module") (at {pcm_x:.2f} {pcm_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0002-0000-0000-000000000002")')
    sch.append(f'\t\t(property "Reference" "U2" (at {pcm_x:.2f} {pcm_y-17.78:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "GY-PCM5102A" (at {pcm_x:.2f} {pcm_y-15.24:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Footprint" "Module:PCM5102A_Module" (at {pcm_x:.2f} {pcm_y+20:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # 3. Level Converter em (X=215.0, Y=145.0)
    lev_x, lev_y = 215.0, 145.0
    sch.append(f'\t(symbol (lib_id "HIL:Logic_Level_Converter_4CH") (at {lev_x:.2f} {lev_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0003-0000-0000-000000000003")')
    sch.append(f'\t\t(property "Reference" "U3" (at {lev_x:.2f} {lev_y-15.24:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "Level_Converter_4CH" (at {lev_x:.2f} {lev_y-12.7:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Footprint" "Module:Level_Converter_4CH" (at {lev_x:.2f} {lev_y+18:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # 4. Conector Speeduino J1 em (X=315.0, Y=105.0)
    j1_x, j1_y = 315.0, 105.0
    sch.append(f'\t(symbol (lib_id "HIL:Conn_Speeduino_Chicote") (at {j1_x:.2f} {j1_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0004-0000-0000-000000000004")')
    sch.append(f'\t\t(property "Reference" "J1" (at {j1_x:.2f} {j1_y-17.78:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "CHICOTE_SPEEDUINO_48WAY" (at {j1_x:.2f} {j1_y-15.24:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Footprint" "Connector_TerminalBlock:TerminalBlock_bornier-9_P5.08mm" (at {j1_x:.2f} {j1_y+20:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= FILTRO RC DO TPS =================
    r1_x, r1_y = 70.0, 101.60
    sch.append(f'\t(symbol (lib_id "Device:R") (at {r1_x:.2f} {r1_y:.2f} 90) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0001-0000-0000-000000000001")')
    sch.append(f'\t\t(property "Reference" "R1" (at {r1_x:.2f} {r1_y-2.54:.2f} 90) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Value" "10k (TPS)" (at {r1_x:.2f} {r1_y+2.54:.2f} 90) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at {r1_x:.2f} {r1_y:.2f} 90) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    c1_x, c1_y = 55.0, 107.62
    sch.append(f'\t(symbol (lib_id "Device:C") (at {c1_x:.2f} {c1_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0002-0000-0000-000000000002")')
    sch.append(f'\t\t(property "Reference" "C1" (at {c1_x+3.81:.2f} {c1_y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append(f'\t\t(property "Value" "1uF (TPS)" (at {c1_x+3.81:.2f} {c1_y+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append(f'\t\t(property "Footprint" "" (at {c1_x:.2f} {c1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at {c1_x:.2f} 115.0 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0001-0000-0000-000000000001")')
    sch.append(f'\t\t(property "Reference" "#PWR01" (at {c1_x:.2f} 117.54 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at {c1_x:.2f} 118.81 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at {c1_x:.2f} 115.0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= FILTRO RC DO MAP =================
    r2_x, r2_y = 70.0, 125.00
    sch.append(f'\t(symbol (lib_id "Device:R") (at {r2_x:.2f} {r2_y:.2f} 90) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0003-0000-0000-000000000003")')
    sch.append(f'\t\t(property "Reference" "R2" (at {r2_x:.2f} {r2_y-2.54:.2f} 90) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Value" "10k (MAP)" (at {r2_x:.2f} {r2_y+2.54:.2f} 90) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at {r2_x:.2f} {r2_y:.2f} 90) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    c2_x, c2_y = 55.0, 131.02
    sch.append(f'\t(symbol (lib_id "Device:C") (at {c2_x:.2f} {c2_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0004-0000-0000-000000000004")')
    sch.append(f'\t\t(property "Reference" "C2" (at {c2_x+3.81:.2f} {c2_y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append(f'\t\t(property "Value" "1uF (MAP)" (at {c2_x+3.81:.2f} {c2_y+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append(f'\t\t(property "Footprint" "" (at {c2_x:.2f} {c2_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at {c2_x:.2f} 138.0 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0002-0000-0000-000000000002")')
    sch.append(f'\t\t(property "Reference" "#PWR02" (at {c2_x:.2f} 140.54 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at {c2_x:.2f} 141.81 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at {c2_x:.2f} 138.0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= ALIMENTACAO ESP32 =================
    sch.append(f'\t(symbol (lib_id "power:GND") (at 88.0 116.84 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0003-0000-0000-000000000003")')
    sch.append(f'\t\t(property "Reference" "#PWR03" (at 88.0 119.38 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 88.0 120.65 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 88.0 116.84 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:+5V") (at 88.0 119.38 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0004-0000-0000-000000000004")')
    sch.append(f'\t\t(property "Reference" "#PWR04" (at 88.0 116.84 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+5V" (at 88.0 115.57 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 88.0 119.38 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:+3V3") (at 142.0 119.38 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0005-0000-0000-000000000005")')
    sch.append(f'\t\t(property "Reference" "#PWR05" (at 142.0 116.84 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+3V3" (at 142.0 115.57 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 142.0 119.38 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= ALIMENTACAO E JUMPERS DO PCM5102A =================
    sch.append(f'\t(symbol (lib_id "power:+5V") (at 190.0 53.57 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0006-0000-0000-000000000006")')
    sch.append(f'\t\t(property "Reference" "#PWR06" (at 190.0 51.0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+5V" (at 190.0 49.5 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 190.0 53.57 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:+3V3") (at 190.0 68.81 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0007-0000-0000-000000000007")')
    sch.append(f'\t\t(property "Reference" "#PWR07" (at 190.0 66.0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+3V3" (at 190.0 64.5 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 190.0 68.81 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    for pcm_gnd_y, uid in [(56.11, "0008"), (66.27, "0009"), (71.35, "0010"), (73.89, "0011"), (76.43, "0012")]:
        sch.append(f'\t(symbol (lib_id "power:GND") (at 190.0 {pcm_gnd_y:.2f} 0) (unit 1)')
        sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
        sch.append(f'\t\t(uuid "c1d2e3f4-{uid}-0000-0000-000000000001")')
        sch.append(f'\t\t(property "Reference" "#PWR_{uid}" (at 190.0 {pcm_gnd_y+2.54:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sch.append(f'\t\t(property "Value" "GND" (at 190.0 {pcm_gnd_y+3.81:.2f} 0) (effects (font (size 1.27 1.27))))')
        sch.append(f'\t\t(property "Footprint" "" (at 190.0 {pcm_gnd_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sch.append('\t)')

    # ================= ALIMENTACAO LEVEL CONVERTER =================
    sch.append(f'\t(symbol (lib_id "power:+5V") (at 190.0 136.11 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0013-0000-0000-000000000013")')
    sch.append(f'\t\t(property "Reference" "#PWR13" (at 190.0 133.5 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+5V" (at 190.0 132.0 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 190.0 136.11 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at 190.0 138.65 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0014-0000-0000-000000000014")')
    sch.append(f'\t\t(property "Reference" "#PWR14" (at 190.0 141.0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 190.0 142.5 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 190.0 138.65 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:+3V3") (at 240.0 136.11 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0015-0000-0000-000000000015")')
    sch.append(f'\t\t(property "Reference" "#PWR15" (at 240.0 133.5 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+3V3" (at 240.0 132.0 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 240.0 136.11 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at 240.0 138.65 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0016-0000-0000-000000000016")')
    sch.append(f'\t\t(property "Reference" "#PWR16" (at 240.0 141.0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 240.0 142.5 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 240.0 138.65 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at 290.0 115.16 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0017-0000-0000-000000000017")')
    sch.append(f'\t\t(property "Reference" "#PWR17" (at 290.0 117.5 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 290.0 119.0 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 290.0 115.16 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= LABELS DE REDE =================
    sch.append('\t(label "NET_TPS_OUT" (at 45.0 101.60 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "NET_TPS_OUT" (at 290.0 99.92 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "NET_MAP_OUT" (at 45.0 125.00 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "NET_MAP_OUT" (at 290.0 102.46 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "I2S_BCK" (at 88.0 106.68 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "I2S_BCK" (at 190.0 58.65 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "I2S_LCK" (at 88.0 109.22 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "I2S_LCK" (at 190.0 63.73 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "I2S_DIN" (at 142.0 86.36 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "I2S_DIN" (at 190.0 61.19 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "CRANK_VR_POS" (at 240.0 58.65 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "CRANK_VR_POS" (at 290.0 94.84 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "CRANK_VR_NEG" (at 240.0 63.73 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "CRANK_VR_NEG" (at 290.0 97.38 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "VSS_PULSE" (at 142.0 106.68 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "VSS_PULSE" (at 290.0 105.00 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "CLUTCH_SIG" (at 142.0 116.84 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "CLUTCH_SIG" (at 290.0 107.54 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "SPEEDUINO_IGN" (at 190.0 143.73 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "SPEEDUINO_IGN" (at 290.0 112.62 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "FB_IGN_3V3" (at 240.0 143.73 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "FB_IGN_3V3" (at 142.0 101.60 0) (effects (font (size 1.27 1.27)) (justify left)))')

    sch.append('\t(label "SPEEDUINO_INJ" (at 190.0 148.81 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "SPEEDUINO_INJ" (at 290.0 110.08 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "FB_INJ_3V3" (at 240.0 148.81 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "FB_INJ_3V3" (at 142.0 109.22 0) (effects (font (size 1.27 1.27)) (justify left)))')

    # ================= WIRES =================
    
    # 1. Filtro TPS:
    # D25 (97.22, 101.60) -> R1 p2 (73.81, 101.60)
    sch.append('\t(wire (pts (xy 97.22 101.60) (xy 73.81 101.60)))')
    # R1 p1 (66.19, 101.60) -> No (55.0, 101.60)
    sch.append('\t(wire (pts (xy 66.19 101.60) (xy 55.0 101.60)))')
    # No (55.0, 101.60) -> Label (45.0, 101.60)
    sch.append('\t(wire (pts (xy 55.0 101.60) (xy 45.0 101.60)))')
    # No (55.0, 101.60) -> C1 p1 (55.0, 103.81)
    sch.append('\t(wire (pts (xy 55.0 101.60) (xy 55.0 103.81)))')
    sch.append('\t(junction (at 55.0 101.60) (diameter 1.016))')
    # C1 p2 (55.0, 111.43) -> GND (55.0, 115.0)
    sch.append('\t(wire (pts (xy 55.0 111.43) (xy 55.0 115.0)))')

    # 2. Filtro MAP:
    # D26 (97.22, 104.14) -> desce para y=125.0 -> R2 p2 (73.81, 125.00)
    sch.append('\t(wire (pts (xy 97.22 104.14) (xy 85.0 104.14)))')
    sch.append('\t(wire (pts (xy 85.0 104.14) (xy 85.0 125.00)))')
    sch.append('\t(wire (pts (xy 85.0 125.00) (xy 73.81 125.00)))')
    # R2 p1 (66.19, 125.00) -> No (55.0, 125.00)
    sch.append('\t(wire (pts (xy 66.19 125.00) (xy 55.0 125.00)))')
    # No (55.0, 125.00) -> Label (45.0, 125.00)
    sch.append('\t(wire (pts (xy 55.0 125.00) (xy 45.0 125.00)))')
    # No (55.0, 125.00) -> C2 p1 (55.0, 127.21)
    sch.append('\t(wire (pts (xy 55.0 125.00) (xy 55.0 127.21)))')
    sch.append('\t(junction (at 55.0 125.00) (diameter 1.016))')
    # C2 p2 (55.0, 134.83) -> GND (55.0, 138.0)
    sch.append('\t(wire (pts (xy 55.0 134.83) (xy 55.0 138.0)))')

    # ESP32 pinos esquerda com labels e power
    sch.append('\t(wire (pts (xy 97.22 106.68) (xy 88.0 106.68)))') # BCK (D27)
    sch.append('\t(wire (pts (xy 97.22 109.22) (xy 88.0 109.22)))') # LCK (D14)
    sch.append('\t(wire (pts (xy 97.22 116.84) (xy 88.0 116.84)))') # GND (p14)
    sch.append('\t(wire (pts (xy 97.22 119.38) (xy 88.0 119.38)))') # VIN (p15)

    # ESP32 pinos direita com labels e power
    sch.append('\t(wire (pts (xy 132.78 86.36) (xy 142.0 86.36)))')   # DIN (D22)
    sch.append('\t(wire (pts (xy 132.78 101.60) (xy 142.0 101.60)))') # IGN FB (D5)
    sch.append('\t(wire (pts (xy 132.78 106.68) (xy 142.0 106.68)))') # VSS (D16)
    sch.append('\t(wire (pts (xy 132.78 109.22) (xy 142.0 109.22)))') # INJ FB (D4)
    sch.append('\t(wire (pts (xy 132.78 116.84) (xy 142.0 116.84)))') # CLUTCH (D15)
    sch.append('\t(wire (pts (xy 132.78 119.38) (xy 142.0 119.38)))') # 3V3 (p16)

    # PCM5102 pinos esquerda
    for pcm_y_pt in [53.57, 56.11, 58.65, 61.19, 63.73, 66.27, 68.81, 71.35, 73.89, 76.43]:
        sch.append(f'\t(wire (pts (xy 197.22 {pcm_y_pt:.2f}) (xy 190.0 {pcm_y_pt:.2f})))')
    # PCM5102 pinos direita
    sch.append('\t(wire (pts (xy 232.78 58.65) (xy 240.0 58.65)))') # LOUT
    sch.append('\t(wire (pts (xy 232.78 63.73) (xy 240.0 63.73)))') # AGND

    # Level Converter pinos esquerda
    for lev_y_pt in [136.11, 138.65, 143.73, 148.81]:
        sch.append(f'\t(wire (pts (xy 197.22 {lev_y_pt:.2f}) (xy 190.0 {lev_y_pt:.2f})))')
    # Level Converter pinos direita
    for lev_y_pt in [136.11, 138.65, 143.73, 148.81]:
        sch.append(f'\t(wire (pts (xy 232.78 {lev_y_pt:.2f}) (xy 240.0 {lev_y_pt:.2f})))')

    # Conector Speeduino J1 pinos
    for j1_y_pt in [94.84, 97.38, 99.92, 102.46, 105.00, 107.54, 110.08, 112.62, 115.16]:
        sch.append(f'\t(wire (pts (xy 297.22 {j1_y_pt:.2f}) (xy 290.0 {j1_y_pt:.2f})))')

    sch.append(')')
    return '\n'.join(sch)

if __name__ == '__main__':
    content = generate_clean_schematic()
    with open('Circuito_HIL/Circuito_HIL.kicad_sch', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Esquematico 100% alinhado gerado com sucesso!")
