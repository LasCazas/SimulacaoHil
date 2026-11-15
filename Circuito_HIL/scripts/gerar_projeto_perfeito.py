"""Gerador perfeito do esquemático KiCad para a Bancada HIL.
Implementa todas as melhorias solicitadas:
1. Pinos de alimentação sem o número '1' visível (pin_numbers hide).
2. Logo oficial IF Betim Racing incorporado no rodapé.
3. 100% dos componentes e fios na grade padrão de 2.54 mm (100 mil) e 1.27 mm (50 mil) - clique perfeito no mouse.
4. Símbolo 'Não Conectado' (no_connect com o 'X' azul clássico) em todos os pinos não utilizados.
5. Fim da poluição visual dos GNDs: barramento unificado com 1 único GND para pinos de config do PCM5102.
6. PCM5102 alargado para eliminar colisão de textos internos.
"""

import base64
import os

def generate_schematic():
    # Carregar logo da equipe
    logo_path = 'C:/Programacao/projetos\RacingTeam/ecu/1_SImulacaoHil/EngenhariaEconomica/images/logoToRodaPe.png'
    with open(logo_path, 'rb') as f:
        logo_b64 = base64.b64encode(f.read()).decode('ascii')

    sch = []
    sch.append('(kicad_sch')
    sch.append('\t(version 20231120)')
    sch.append('\t(generator "eeschema")')
    sch.append('\t(generator_version "8.0")')
    sch.append('\t(uuid "d8a1c320-1a2b-4c3d-8e4f-5a6b7c8d9e01")')
    sch.append('\t(paper "A3")')
    sch.append('\t(title_block')
    sch.append('\t\t(title "BANCADA HIL - SIMULADOR DINAMICO SPEEDUINO 48-WAY")')
    sch.append('\t\t(date "2026-11-12")')
    sch.append('\t\t(rev "v2.0")')
    sch.append('\t\t(company "IF Betim Racing - IFMG Campus Betim")')
    sch.append('\t\t(comment 1 "Interface HIL: ESP32 + PCM5102A + Level Converter + Filtros RC")')
    sch.append('\t\t(comment 2 "KTM Duke 390 (22-2) & Speeduino 48-Way")')
    sch.append('\t)')

    sch.append('\t(lib_symbols')
    
    # ------------------ Device:R ------------------
    # Resistor padrão 5.08mm entre pinos (2.54mm de cada lado) para encaixe perfeito na grade de 2.54mm
    sch.append('\t\t(symbol "Device:R" (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" (at 0 0 90) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "R_0_1"')
    sch.append('\t\t\t\t(rectangle (start -1.016 -1.778) (end 1.016 1.778) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "R_1_1"')
    sch.append('\t\t\t\t(pin passive line (at 0 2.54 270) (length 0.762) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)) hide)))')
    sch.append('\t\t\t\t(pin passive line (at 0 -2.54 90) (length 0.762) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)) hide)))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # ------------------ Device:C ------------------
    # Capacitor padrão com pinos a 2.54mm de distância
    sch.append('\t\t(symbol "Device:C" (pin_numbers hide) (pin_names (offset 0.254)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "C" (at 1.524 1.524 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t\t\t(property "Value" "C" (at 1.524 -1.524 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t\t\t(property "Footprint" "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "C_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy -2.032 -0.635) (xy 2.032 -0.635)) (stroke (width 0.508) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy -2.032 0.635) (xy 2.032 0.635)) (stroke (width 0.508) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "C_1_1"')
    sch.append('\t\t\t\t(pin passive line (at 0 2.54 270) (length 1.905) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)) hide)))')
    sch.append('\t\t\t\t(pin passive line (at 0 -2.54 90) (length 1.905) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)) hide)))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # ------------------ power:GND (sem numero de pino!) ------------------
    sch.append('\t\t(symbol "power:GND" (power) (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "#PWR" (at 0 -2.54 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "GND_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type outline)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "GND_1_1"')
    sch.append('\t\t\t\t(pin power_in line (at 0 0 270) (length 0) (name "~" (effects (font (size 1.27 1.27)) hide)) (number "1" (effects (font (size 1.27 1.27)) hide)))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # ------------------ power:+5V (sem numero de pino!) ------------------
    sch.append('\t\t(symbol "power:+5V" (power) (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(property "Value" "+5V" (at 0 3.81 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "+5V_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "+5V_1_1"')
    sch.append('\t\t\t\t(pin power_in line (at 0 0 90) (length 0) (name "~" (effects (font (size 1.27 1.27)) hide)) (number "1" (effects (font (size 1.27 1.27)) hide)))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # ------------------ power:+3V3 (sem numero de pino!) ------------------
    sch.append('\t\t(symbol "power:+3V3" (power) (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(property "Value" "+3V3" (at 0 3.81 0) (effects (font (size 1.27 1.27))))')
    sch.append('\t\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "+3V3_0_1"')
    sch.append('\t\t\t\t(polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t\t(polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "+3V3_1_1"')
    sch.append('\t\t\t\t(pin power_in line (at 0 0 90) (length 0) (name "~" (effects (font (size 1.27 1.27)) hide)) (number "1" (effects (font (size 1.27 1.27)) hide)))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # ------------------ ESP32 DevKit V1 30Pin ------------------
    # Caixa com largura 35.56 mm (14 * 2.54), pinos saindo a -17.78 e +17.78
    sch.append('\t\t(symbol "HIL:ESP32_DevKit_V1_30Pin" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "U1" (at -17.78 22.86 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "ESP32_DevKit_V1" (at 0 22.86 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Footprint" "Module:ESP32_DevKit_V1_30Pin" (at 0 -22.86 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "ESP32_DevKit_V1_30Pin_0_1"')
    sch.append('\t\t\t\t(rectangle (start -15.24 20.32) (end 15.24 -20.32) (stroke (width 0.254) (type default)) (fill (type background)))')
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
        ("8", "D25 (DAC_TPS)", "output"),
        ("9", "D26 (DAC_MAP)", "output"),
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

    # ------------------ PCM5102A Module (Largura Expandida para 45.72mm) ------------------
    # Caixa start -20.32 a 20.32, pinos a -22.86 e +22.86 (total 45.72 mm, SEM colisão de texto!)
    sch.append('\t\t(symbol "HIL:PCM5102A_Module" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "U2" (at -20.32 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "GY-PCM5102A" (at 0 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Footprint" "Module:PCM5102A_Module" (at 0 -17.78 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "PCM5102A_Module_0_1"')
    sch.append('\t\t\t\t(rectangle (start -20.32 15.24) (end 20.32 -15.24) (stroke (width 0.254) (type default)) (fill (type background)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "PCM5102A_Module_1_1"')
    pcm_left = [
        ("1", "VCC", "power_in"),
        ("2", "GND", "power_in"),
        ("3", "BCK", "input"),
        ("4", "DIN", "input"),
        ("5", "LCK", "input"),
        ("6", "SCK", "input"),
        ("7", "XMT", "input"),
        ("8", "FMT", "input"),
        ("9", "FLT", "input"),
        ("10", "DMP", "input"),
    ]
    for idx, (pnum, pname, ptype) in enumerate(pcm_left):
        y_s = 11.43 - idx * 2.54
        sch.append(f'\t\t\t\t(pin {ptype} line (at -22.86 {y_s:.2f} 0) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')
    
    pcm_right = [
        ("11", "LOUT (VR1+)", "output", 6.35),
        ("12", "AGND (VR1-)", "passive", 1.27),
        ("13", "ROUT (NC)", "output", -3.81),
    ]
    for pnum, pname, ptype, y_s in pcm_right:
        sch.append(f'\t\t\t\t(pin {ptype} line (at 22.86 {y_s:.2f} 180) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # ------------------ Level Converter 4CH ------------------
    sch.append('\t\t(symbol "HIL:Logic_Level_Converter_4CH" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "U3" (at -15.24 15.24 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "Level_Converter_4CH" (at 0 15.24 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Footprint" "Module:Level_Converter_4CH" (at 0 -15.24 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "Logic_Level_Converter_4CH_0_1"')
    sch.append('\t\t\t\t(rectangle (start -15.24 12.7) (end 15.24 -12.7) (stroke (width 0.254) (type default)) (fill (type background)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "Logic_Level_Converter_4CH_1_1"')
    lev_left = [
        ("1", "HV (5V)", "power_in", 7.62),
        ("2", "GND (HV)", "power_in", 5.08),
        ("3", "HV1 (IGN)", "input", 0.0),
        ("4", "HV2 (INJ)", "input", -5.08),
        ("5", "HV3 (NC)", "passive", -7.62),
        ("6", "HV4 (NC)", "passive", -10.16),
    ]
    for pnum, pname, ptype, y_s in lev_left:
        sch.append(f'\t\t\t\t(pin {ptype} line (at -17.78 {y_s:.2f} 0) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')

    lev_right = [
        ("7", "LV (3V3)", "power_in", 7.62),
        ("8", "GND (LV)", "power_in", 5.08),
        ("9", "LV1 (-> D5)", "output", 0.0),
        ("10", "LV2 (-> D4)", "output", -5.08),
        ("11", "LV3 (NC)", "passive", -7.62),
        ("12", "LV4 (NC)", "passive", -10.16),
    ]
    for pnum, pname, ptype, y_s in lev_right:
        sch.append(f'\t\t\t\t(pin {ptype} line (at 17.78 {y_s:.2f} 180) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    # ------------------ Conector Speeduino 48-Way (J1) ------------------
    sch.append('\t\t(symbol "HIL:Conn_Speeduino_Chicote" (in_bom yes) (on_board yes)')
    sch.append('\t\t\t(property "Reference" "J1" (at -17.78 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Value" "CHICOTE_SPEEDUINO_48WAY" (at 0 17.78 0) (effects (font (size 1.524 1.524)) (justify left)))')
    sch.append('\t\t\t(property "Footprint" "Connector_TerminalBlock:TerminalBlock_bornier-9_P5.08mm" (at 0 -17.78 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t\t\t(symbol "Conn_Speeduino_Chicote_0_1"')
    sch.append('\t\t\t\t(rectangle (start -17.78 15.24) (end 17.78 -15.24) (stroke (width 0.254) (type default)) (fill (type background)))')
    sch.append('\t\t\t)')
    sch.append('\t\t\t(symbol "Conn_Speeduino_Chicote_1_1"')
    j1_pins = [
        ("1", "B_B2 (CRANK+ / VR1+)", "input"),
        ("2", "B_B3 (VR1- / Terra VR)", "passive"),
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
        sch.append(f'\t\t\t\t(pin {ptype} line (at -20.32 {y_s:.2f} 0) (length 2.54) (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{pnum}" (effects (font (size 1.27 1.27)))))')
    sch.append('\t\t\t)')
    sch.append('\t\t)')

    sch.append('\t)') # fim lib_symbols

    # ================= POSICIONAMENTO RIGOROSAMENTE NA GRADE DE 2.54 MM =================
    # ESP32: Centro em (114.30, 101.60).
    # Pinos esquerda: X = 114.30 - 17.78 = 96.52 (38 * 2.54)
    # Pinos direita:  X = 114.30 + 17.78 = 132.08 (52 * 2.54)
    esp_x, esp_y = 114.30, 101.60
    sch.append(f'\t(symbol (lib_id "HIL:ESP32_DevKit_V1_30Pin") (at {esp_x:.2f} {esp_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0001-0000-0000-000000000001")')
    sch.append(f'\t\t(property "Reference" "U1" (at {esp_x:.2f} {esp_y-22.86:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "ESP32_DevKit_V1" (at {esp_x:.2f} {esp_y-20.32:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Footprint" "Module:ESP32_DevKit_V1_30Pin" (at {esp_x:.2f} {esp_y+22.86:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # PCM5102: Centro em (215.90, 63.50). (85 * 2.54, 25 * 2.54)
    # Pinos esquerda: X = 215.90 - 22.86 = 193.04 (76 * 2.54)
    # Pinos direita:  X = 215.90 + 22.86 = 238.76 (94 * 2.54)
    pcm_x, pcm_y = 215.90, 63.50
    sch.append(f'\t(symbol (lib_id "HIL:PCM5102A_Module") (at {pcm_x:.2f} {pcm_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0002-0000-0000-000000000002")')
    sch.append(f'\t\t(property "Reference" "U2" (at {pcm_x:.2f} {pcm_y-17.78:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "GY-PCM5102A" (at {pcm_x:.2f} {pcm_y-15.24:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Footprint" "Module:PCM5102A_Module" (at {pcm_x:.2f} {pcm_y+17.78:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # Level Converter: Centro em (215.90, 152.40). (85 * 2.54, 60 * 2.54)
    # Pinos esquerda: X = 215.90 - 17.78 = 198.12 (78 * 2.54)
    # Pinos direita:  X = 215.90 + 17.78 = 233.68 (92 * 2.54)
    lev_x, lev_y = 215.90, 152.40
    sch.append(f'\t(symbol (lib_id "HIL:Logic_Level_Converter_4CH") (at {lev_x:.2f} {lev_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0003-0000-0000-000000000003")')
    sch.append(f'\t\t(property "Reference" "U3" (at {lev_x:.2f} {lev_y-15.24:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "Level_Converter_4CH" (at {lev_x:.2f} {lev_y-12.7:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Footprint" "Module:Level_Converter_4CH" (at {lev_x:.2f} {lev_y+15.24:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # Conector Speeduino J1: Centro em (317.50, 101.60). (125 * 2.54, 40 * 2.54)
    # Pinos: X = 317.50 - 20.32 = 297.18 -> ajustado para X = 297.18 (multiplo de 2.54: 117 * 2.54 = 297.18)
    j1_x, j1_y = 317.50, 101.60
    sch.append(f'\t(symbol (lib_id "HIL:Conn_Speeduino_Chicote") (at {j1_x:.2f} {j1_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "a1b2c3d4-0004-0000-0000-000000000004")')
    sch.append(f'\t\t(property "Reference" "J1" (at {j1_x:.2f} {j1_y-17.78:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Value" "CHICOTE_SPEEDUINO_48WAY" (at {j1_x:.2f} {j1_y-15.24:.2f} 0) (effects (font (size 1.524 1.524))))')
    sch.append(f'\t\t(property "Footprint" "Connector_TerminalBlock:TerminalBlock_bornier-9_P5.08mm" (at {j1_x:.2f} {j1_y+17.78:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= FILTRO RC TPS (D25 - y = 101.60) =================
    # R1: Rotação 90 graus. Centro em (68.58, 101.60). (27 * 2.54, 40 * 2.54)
    # Pinos: p1 a (68.58 - 2.54 = 66.04), p2 a (68.58 + 2.54 = 71.12). 100% NA GRADE!
    r1_x, r1_y = 68.58, 101.60
    sch.append(f'\t(symbol (lib_id "Device:R") (at {r1_x:.2f} {r1_y:.2f} 90) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0001-0000-0000-000000000001")')
    sch.append(f'\t\t(property "Reference" "R1" (at {r1_x:.2f} {r1_y-2.54:.2f} 90) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Value" "10k (TPS)" (at {r1_x:.2f} {r1_y+2.54:.2f} 90) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at {r1_x:.2f} {r1_y:.2f} 90) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # C1: Centro em (53.34, 104.14). (21 * 2.54, 41 * 2.54)
    # Pinos: p1 a (104.14 - 2.54 = 101.60), p2 a (104.14 + 2.54 = 106.68). 100% NA GRADE!
    c1_x, c1_y = 53.34, 104.14
    sch.append(f'\t(symbol (lib_id "Device:C") (at {c1_x:.2f} {c1_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0002-0000-0000-000000000002")')
    sch.append(f'\t\t(property "Reference" "C1" (at {c1_x+3.81:.2f} {c1_y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append(f'\t\t(property "Value" "1uF (TPS)" (at {c1_x+3.81:.2f} {c1_y+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append(f'\t\t(property "Footprint" "" (at {c1_x:.2f} {c1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at {c1_x:.2f} 106.68 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0001-0000-0000-000000000001")')
    sch.append(f'\t\t(property "Reference" "#PWR01" (at {c1_x:.2f} 109.22 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at {c1_x:.2f} 110.49 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at {c1_x:.2f} 106.68 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= FILTRO RC MAP (D26 - y = 104.14 -> desce para y = 127.00) =================
    # R2: Centro em (68.58, 127.00). (27 * 2.54, 50 * 2.54)
    # Pinos: p1 a (66.04), p2 a (71.12). 100% NA GRADE!
    r2_x, r2_y = 68.58, 127.00
    sch.append(f'\t(symbol (lib_id "Device:R") (at {r2_x:.2f} {r2_y:.2f} 90) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0003-0000-0000-000000000003")')
    sch.append(f'\t\t(property "Reference" "R2" (at {r2_x:.2f} {r2_y-2.54:.2f} 90) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Value" "10k (MAP)" (at {r2_x:.2f} {r2_y+2.54:.2f} 90) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at {r2_x:.2f} {r2_y:.2f} 90) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # C2: Centro em (53.34, 129.54). (21 * 2.54, 51 * 2.54)
    # Pinos: p1 a (127.00), p2 a (132.08). 100% NA GRADE!
    c2_x, c2_y = 53.34, 129.54
    sch.append(f'\t(symbol (lib_id "Device:C") (at {c2_x:.2f} {c2_y:.2f} 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "b1c2d3e4-0004-0000-0000-000000000004")')
    sch.append(f'\t\t(property "Reference" "C2" (at {c2_x+3.81:.2f} {c2_y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append(f'\t\t(property "Value" "1uF (MAP)" (at {c2_x+3.81:.2f} {c2_y+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append(f'\t\t(property "Footprint" "" (at {c2_x:.2f} {c2_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at {c2_x:.2f} 132.08 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0002-0000-0000-000000000002")')
    sch.append(f'\t\t(property "Reference" "#PWR02" (at {c2_x:.2f} 134.62 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at {c2_x:.2f} 135.89 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at {c2_x:.2f} 132.08 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= ALIMENTAÇÃO ESP32 (GND p14 = 116.84, VIN p15 = 119.38, 3V3 p16 = 119.38) =================
    sch.append(f'\t(symbol (lib_id "power:GND") (at 86.36 116.84 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0003-0000-0000-000000000003")')
    sch.append(f'\t\t(property "Reference" "#PWR03" (at 86.36 119.38 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 86.36 120.65 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 86.36 116.84 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:+5V") (at 86.36 119.38 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0004-0000-0000-000000000004")')
    sch.append(f'\t\t(property "Reference" "#PWR04" (at 86.36 116.84 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+5V" (at 86.36 115.57 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 86.36 119.38 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:+3V3") (at 142.24 119.38 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0005-0000-0000-000000000005")')
    sch.append(f'\t\t(property "Reference" "#PWR05" (at 142.24 116.84 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+3V3" (at 142.24 115.57 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 142.24 119.38 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= ALIMENTAÇÃO PCM5102A (pcm_y = 63.50) =================
    # VCC (pin 1, y = 52.07), GND (pin 2, y = 54.61)
    sch.append(f'\t(symbol (lib_id "power:+5V") (at 182.88 52.07 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0006-0000-0000-000000000006")')
    sch.append(f'\t\t(property "Reference" "#PWR06" (at 182.88 49.53 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+5V" (at 182.88 48.26 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 182.88 52.07 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at 182.88 54.61 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0007-0000-0000-000000000007")')
    sch.append(f'\t\t(property "Reference" "#PWR07" (at 182.88 57.15 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 182.88 58.42 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 182.88 54.61 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # XMT (pin 7, y = 67.31) -> Vai ao +3V3 para desativar MUTE
    sch.append(f'\t(symbol (lib_id "power:+3V3") (at 182.88 67.31 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0008-0000-0000-000000000008")')
    sch.append(f'\t\t(property "Reference" "#PWR08" (at 182.88 64.77 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+3V3" (at 182.88 63.50 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 182.88 67.31 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # Pinos SCK (64.77), FMT (69.85), FLT (72.39), DMP (74.93)
    # UNIFICADOS NUM BARRAMENTO LIMPO COM 1 ÚNICO GND EMBAIXO!
    sch.append(f'\t(symbol (lib_id "power:GND") (at 182.88 77.47 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0009-0000-0000-000000000009")')
    sch.append(f'\t\t(property "Reference" "#PWR09" (at 182.88 80.01 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 182.88 81.28 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 182.88 77.47 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= ALIMENTAÇÃO LEVEL CONVERTER (lev_y = 152.40) =================
    # HV (p1, y = 144.78), GND_HV (p2, y = 147.32)
    sch.append(f'\t(symbol (lib_id "power:+5V") (at 187.96 144.78 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0010-0000-0000-000000000010")')
    sch.append(f'\t\t(property "Reference" "#PWR10" (at 187.96 142.24 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+5V" (at 187.96 140.97 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 187.96 144.78 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at 187.96 147.32 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0011-0000-0000-000000000011")')
    sch.append(f'\t\t(property "Reference" "#PWR11" (at 187.96 149.86 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 187.96 151.13 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 187.96 147.32 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # LV (p7, y = 144.78), GND_LV (p8, y = 147.32)
    sch.append(f'\t(symbol (lib_id "power:+3V3") (at 243.84 144.78 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0012-0000-0000-000000000012")')
    sch.append(f'\t\t(property "Reference" "#PWR12" (at 243.84 142.24 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "+3V3" (at 243.84 140.97 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 243.84 144.78 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    sch.append(f'\t(symbol (lib_id "power:GND") (at 243.84 147.32 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0013-0000-0000-000000000013")')
    sch.append(f'\t\t(property "Reference" "#PWR13" (at 243.84 149.86 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 243.84 151.13 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 243.84 147.32 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # GND Sensores Speeduino J1 (p9, y = 111.76)
    sch.append(f'\t(symbol (lib_id "power:GND") (at 287.02 111.76 0) (unit 1)')
    sch.append('\t\t(in_bom yes) (on_board yes) (dnp no)')
    sch.append('\t\t(uuid "c1d2e3f4-0014-0000-0000-000000000014")')
    sch.append(f'\t\t(property "Reference" "#PWR14" (at 287.02 114.30 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append(f'\t\t(property "Value" "GND" (at 287.02 115.57 0) (effects (font (size 1.27 1.27))))')
    sch.append(f'\t\t(property "Footprint" "" (at 287.02 111.76 0) (effects (font (size 1.27 1.27)) hide))')
    sch.append('\t)')

    # ================= LABELS DE REDE (ALINHADOS EM GRADE 2.54 MM) =================
    sch.append('\t(label "NET_TPS_OUT" (at 43.18 101.60 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "NET_TPS_OUT" (at 287.02 96.52 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "NET_MAP_OUT" (at 43.18 127.00 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "NET_MAP_OUT" (at 287.02 99.06 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "I2S_BCK" (at 86.36 106.68 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "I2S_BCK" (at 182.88 57.15 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "I2S_LCK" (at 86.36 109.22 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "I2S_LCK" (at 182.88 62.23 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "I2S_DIN" (at 142.24 86.36 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "I2S_DIN" (at 182.88 59.69 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "CRANK_VR_POS" (at 248.92 57.15 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "CRANK_VR_POS" (at 287.02 91.44 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "CRANK_VR_NEG" (at 248.92 62.23 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "CRANK_VR_NEG" (at 287.02 93.98 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "VSS_PULSE" (at 142.24 106.68 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "VSS_PULSE" (at 287.02 101.60 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "CLUTCH_SIG" (at 142.24 116.84 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "CLUTCH_SIG" (at 287.02 104.14 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "SPEEDUINO_IGN" (at 187.96 152.40 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "SPEEDUINO_IGN" (at 287.02 109.22 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "FB_IGN_3V3" (at 243.84 152.40 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "FB_IGN_3V3" (at 142.24 101.60 0) (effects (font (size 1.27 1.27)) (justify left)))')

    sch.append('\t(label "SPEEDUINO_INJ" (at 187.96 157.48 180) (effects (font (size 1.27 1.27)) (justify right)))')
    sch.append('\t(label "SPEEDUINO_INJ" (at 287.02 106.68 180) (effects (font (size 1.27 1.27)) (justify right)))')

    sch.append('\t(label "FB_INJ_3V3" (at 243.84 157.48 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sch.append('\t(label "FB_INJ_3V3" (at 142.24 109.22 0) (effects (font (size 1.27 1.27)) (justify left)))')

    # ================= PINOS NÃO CONECTADOS (no_connect - 'X' AZUL OFICIAL DO KICAD) =================
    # ESP32 pinos esquerdos não usados
    for esp_nc_y in [83.82, 86.36, 88.90, 91.44, 93.98, 96.52, 99.06, 111.76, 114.30]:
        sch.append(f'\t(no_connect (at 96.52 {esp_nc_y:.2f}) (uuid "e1e2e3e4-{int(esp_nc_y*100):04d}-0000-0000-000000000001"))')
    # ESP32 pinos direitos não usados
    for esp_nc_y in [83.82, 88.90, 91.44, 93.98, 96.52, 99.06, 104.14, 111.76, 114.30]:
        sch.append(f'\t(no_connect (at 132.08 {esp_nc_y:.2f}) (uuid "e1e2e3e4-{int(esp_nc_y*100):04d}-0000-0000-000000000002"))')

    # PCM5102 ROUT (NC)
    sch.append(f'\t(no_connect (at 238.76 67.31) (uuid "e1e2e3e4-6731-0000-0000-000000000003"))')

    # Level Converter HV3, HV4, LV3, LV4 (NC)
    sch.append(f'\t(no_connect (at 198.12 160.02) (uuid "e1e2e3e4-1600-0000-0000-000000000004"))') # HV3
    sch.append(f'\t(no_connect (at 198.12 162.56) (uuid "e1e2e3e4-1625-0000-0000-000000000005"))') # HV4
    sch.append(f'\t(no_connect (at 233.68 160.02) (uuid "e1e2e3e4-1601-0000-0000-000000000006"))') # LV3
    sch.append(f'\t(no_connect (at 233.68 162.56) (uuid "e1e2e3e4-1626-0000-0000-000000000007"))') # LV4

    # ================= WIRES (100% ALINHADOS NA GRADE DE 2.54 MM E 1.27 MM) =================
    # 1. Filtro TPS:
    # D25 (96.52, 101.60) -> R1 p2 (71.12, 101.60)
    sch.append('\t(wire (pts (xy 96.52 101.60) (xy 71.12 101.60)))')
    # R1 p1 (66.04, 101.60) -> No (53.34, 101.60)
    sch.append('\t(wire (pts (xy 66.04 101.60) (xy 53.34 101.60)))')
    # No (53.34, 101.60) -> Label (43.18, 101.60)
    sch.append('\t(wire (pts (xy 53.34 101.60) (xy 43.18 101.60)))')
    # No (53.34, 101.60) -> C1 p1 (53.34, 101.60)
    sch.append('\t(junction (at 53.34 101.60) (diameter 1.016))')
    # C1 p2 (53.34, 106.68) -> GND (53.34, 106.68)
    sch.append('\t(wire (pts (xy 53.34 106.68) (xy 53.34 106.68)))')

    # 2. Filtro MAP:
    # D26 (96.52, 104.14) -> desce para y=127.00 -> R2 p2 (71.12, 127.00)
    sch.append('\t(wire (pts (xy 96.52 104.14) (xy 83.82 104.14)))')
    sch.append('\t(wire (pts (xy 83.82 104.14) (xy 83.82 127.00)))')
    sch.append('\t(wire (pts (xy 83.82 127.00) (xy 71.12 127.00)))')
    # R2 p1 (66.04, 127.00) -> No (53.34, 127.00)
    sch.append('\t(wire (pts (xy 66.04 127.00) (xy 53.34 127.00)))')
    # No (53.34, 127.00) -> Label (43.18, 127.00)
    sch.append('\t(wire (pts (xy 53.34 127.00) (xy 43.18 127.00)))')
    # No (53.34, 127.00) -> C2 p1 (53.34, 127.00)
    sch.append('\t(junction (at 53.34 127.00) (diameter 1.016))')
    # C2 p2 (53.34, 132.08) -> GND (53.34, 132.08)
    sch.append('\t(wire (pts (xy 53.34 132.08) (xy 53.34 132.08)))')

    # ESP32 pinos esquerda
    sch.append('\t(wire (pts (xy 96.52 106.68) (xy 86.36 106.68)))') # BCK (D27)
    sch.append('\t(wire (pts (xy 96.52 109.22) (xy 86.36 109.22)))') # LCK (D14)
    sch.append('\t(wire (pts (xy 96.52 116.84) (xy 86.36 116.84)))') # GND (p14)
    sch.append('\t(wire (pts (xy 96.52 119.38) (xy 86.36 119.38)))') # VIN (p15)

    # ESP32 pinos direita
    sch.append('\t(wire (pts (xy 132.08 86.36) (xy 142.24 86.36)))')   # DIN (D22)
    sch.append('\t(wire (pts (xy 132.08 101.60) (xy 142.24 101.60)))') # IGN FB (D5)
    sch.append('\t(wire (pts (xy 132.08 106.68) (xy 142.24 106.68)))') # VSS (D16)
    sch.append('\t(wire (pts (xy 132.08 109.22) (xy 142.24 109.22)))') # INJ FB (D4)
    sch.append('\t(wire (pts (xy 132.08 116.84) (xy 142.24 116.84)))') # CLUTCH (D15)
    sch.append('\t(wire (pts (xy 132.08 119.38) (xy 142.24 119.38)))') # 3V3 (p16)

    # PCM5102 pinos esquerda
    sch.append('\t(wire (pts (xy 193.04 52.07) (xy 182.88 52.07)))') # VCC
    sch.append('\t(wire (pts (xy 193.04 54.61) (xy 182.88 54.61)))') # GND
    sch.append('\t(wire (pts (xy 193.04 57.15) (xy 182.88 57.15)))') # BCK
    sch.append('\t(wire (pts (xy 193.04 59.69) (xy 182.88 59.69)))') # DIN
    sch.append('\t(wire (pts (xy 193.04 62.23) (xy 182.88 62.23)))') # LCK
    sch.append('\t(wire (pts (xy 193.04 67.31) (xy 182.88 67.31)))') # XMT (-> 3V3)

    # BARRAMENTO LIMPO DE CONFIGURAÇÃO GND PARA PCM5102:
    # Liga SCK (64.77), FMT (69.85), FLT (72.39), DMP (74.93)
    # Linha vertical de barramento em X = 182.88 de Y = 64.77 até Y = 77.47 (onde fica o GND)
    sch.append('\t(wire (pts (xy 193.04 64.77) (xy 182.88 64.77)))') # SCK
    sch.append('\t(wire (pts (xy 193.04 69.85) (xy 182.88 69.85)))') # FMT
    sch.append('\t(wire (pts (xy 193.04 72.39) (xy 182.88 72.39)))') # FLT
    sch.append('\t(wire (pts (xy 193.04 74.93) (xy 182.88 74.93)))') # DMP
    sch.append('\t(wire (pts (xy 182.88 64.77) (xy 182.88 77.47)))') # Barramento vertical GND
    sch.append('\t(junction (at 182.88 64.77) (diameter 1.016))')
    sch.append('\t(junction (at 182.88 69.85) (diameter 1.016))')
    sch.append('\t(junction (at 182.88 72.39) (diameter 1.016))')
    sch.append('\t(junction (at 182.88 74.93) (diameter 1.016))')

    # PCM5102 pinos direita
    sch.append('\t(wire (pts (xy 238.76 57.15) (xy 248.92 57.15)))') # LOUT (VR1+)
    sch.append('\t(wire (pts (xy 238.76 62.23) (xy 248.92 62.23)))') # AGND (VR1-)

    # Level Converter pinos esquerda
    sch.append('\t(wire (pts (xy 198.12 144.78) (xy 187.96 144.78)))') # HV
    sch.append('\t(wire (pts (xy 198.12 147.32) (xy 187.96 147.32)))') # GND
    sch.append('\t(wire (pts (xy 198.12 152.40) (xy 187.96 152.40)))') # HV1 (IGN)
    sch.append('\t(wire (pts (xy 198.12 157.48) (xy 187.96 157.48)))') # HV2 (INJ)

    # Level Converter pinos direita
    sch.append('\t(wire (pts (xy 233.68 144.78) (xy 243.84 144.78)))') # LV
    sch.append('\t(wire (pts (xy 233.68 147.32) (xy 243.84 147.32)))') # GND
    sch.append('\t(wire (pts (xy 233.68 152.40) (xy 243.84 152.40)))') # LV1 (D5)
    sch.append('\t(wire (pts (xy 233.68 157.48) (xy 243.84 157.48)))') # LV2 (D4)

    # Speeduino J1 pinos
    for j1_idx, j1_y_pt in enumerate([91.44, 93.98, 96.52, 99.06, 101.60, 104.14, 106.68, 109.22, 111.76]):
        sch.append(f'\t(wire (pts (xy 297.18 {j1_y_pt:.2f}) (xy 287.02 {j1_y_pt:.2f})))')

    # ================= LOGO OFICIAL NO RODAPÉ =================
    # Posicionado acima do title_block no canto inferior direito
    sch.append(f'\t(image (at 335.00 240.00) (scale 0.45) (uuid "f1e2d3c4-0000-0000-0000-000000000099")')
    sch.append('\t\t(data')
    sch.append(f'\t\t\t"{logo_b64}"')
    sch.append('\t\t)')
    sch.append('\t)')

    sch.append(')')
    return '\n'.join(sch)

if __name__ == '__main__':
    content = generate_schematic()
    out_file = 'Circuito_HIL/Circuito_HIL.kicad_sch'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Novo esquemático perfeito gerado com sucesso!")
