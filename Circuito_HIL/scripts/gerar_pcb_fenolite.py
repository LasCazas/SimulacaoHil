"""Gerador do Layout PCB Face Simples (Single-Sided / Bottom-Only) para Fenolite.
Bancada Simulador Dinâmico HIL - Speeduino 48-Way & KTM Duke 390.
Equipe IF Betim Racing.

Todas as trilhas de cobre estão 100% na camada BOTTOM (B.Cu).
Lado superior (F.Cu) é exclusivo para montagem dos componentes (Through-Hole).
Ideal para confecção caseira em fenolite (transferência térmica / percloreto de ferro).
"""

import os
import subprocess

def generate_pcb():
    pcb = []
    pcb.append('(kicad_pcb')
    pcb.append('\t(version 20240108)')
    pcb.append('\t(generator "kicad_cli")')
    pcb.append('\t(generator_version "10.0")')
    pcb.append('\t(general')
    pcb.append('\t\t(thickness 1.6)')
    pcb.append('\t\t(legacy_teardrops no)')
    pcb.append('\t)')
    pcb.append('\t(paper "A4")')
    pcb.append('\t(layers')
    pcb.append('\t\t(0 "F.Cu" signal)')
    pcb.append('\t\t(31 "B.Cu" signal)')
    pcb.append('\t\t(36 "B.SilkS" user "B.Silkscreen")')
    pcb.append('\t\t(37 "F.SilkS" user "F.Silkscreen")')
    pcb.append('\t\t(38 "B.Mask" user)')
    pcb.append('\t\t(39 "F.Mask" user)')
    pcb.append('\t\t(44 "Edge.Cuts" user)')
    pcb.append('\t)')
    pcb.append('\t(setup')
    pcb.append('\t\t(pad_to_mask_clearance 0.15)')
    pcb.append('\t\t(pcbplotparams')
    pcb.append('\t\t\t(layerselection 0x00010fc_ffffffff)')
    pcb.append('\t\t\t(plot_on_all_layers_selection 0x0000000_00000000)')
    pcb.append('\t\t\t(disableapertmacros no)')
    pcb.append('\t\t\t(usegerberextensions no)')
    pcb.append('\t\t\t(usegerberattributes yes)')
    pcb.append('\t\t\t(usegerberadvancedattributes yes)')
    pcb.append('\t\t\t(creategerberjobfile yes)')
    pcb.append('\t\t\t(svguseinch no)')
    pcb.append('\t\t\t(svgprecision 4)')
    pcb.append('\t\t\t(excludeedgelayer no)')
    pcb.append('\t\t\t(plotframeref no)')
    pcb.append('\t\t\t(viasonmask no)')
    pcb.append('\t\t\t(mode 1)')
    pcb.append('\t\t\t(useauxorigin no)')
    pcb.append('\t\t\t(hpglpennumber 1)')
    pcb.append('\t\t\t(hpglpenspeed 20)')
    pcb.append('\t\t\t(hpglpendiameter 15.000000)')
    pcb.append('\t\t\t(pdf_front_fp_property_popups yes)')
    pcb.append('\t\t\t(pdf_back_fp_property_popups yes)')
    pcb.append('\t\t\t(dxfpolygonmode yes)')
    pcb.append('\t\t\t(dxfimperialunits no)')
    pcb.append('\t\t\t(dxfcontourdxfunit 0)')
    pcb.append('\t\t\t(outputformat 1)')
    pcb.append('\t\t\t(mirror no)')
    pcb.append('\t\t\t(drillshape 1)')
    pcb.append('\t\t\t(scaleselection 1)')
    pcb.append('\t\t\t(outputdirectory "")')
    pcb.append('\t\t)')
    pcb.append('\t)')

    # Lista de redes (Nets)
    nets = [
        (0, ""),
        (1, "+3V3"),
        (2, "+5V"),
        (3, "/CLUTCH_SIG"),
        (4, "/CRANK_VR_NEG"),
        (5, "/CRANK_VR_POS"),
        (6, "/FB_IGN_3V3"),
        (7, "/FB_INJ_3V3"),
        (8, "/I2S_BCK"),
        (9, "/I2S_DIN"),
        (10, "/I2S_LCK"),
        (11, "/NET_MAP_OUT"),
        (12, "/NET_TPS_OUT"),
        (13, "/SPEEDUINO_IGN"),
        (14, "/SPEEDUINO_INJ"),
        (15, "/VSS_PULSE"),
        (16, "GND"),
        (17, "Net-(U1-D25_(DAC_TPS))"),
        (18, "Net-(U1-D26_(DAC_MAP))"),
    ]
    for n_id, n_name in nets:
        pcb.append(f'\t(net {n_id} "{n_name}")')

    # Borda da Placa (Edge.Cuts): 110 mm x 85 mm (de X=15 Y=15 até X=125 Y=100)
    pcb.append('\t(gr_rect (start 15.0 15.0) (end 125.0 100.0) (stroke (width 0.25) (type solid)) (fill none) (layer "Edge.Cuts") (uuid "b0000000-0000-0000-0000-000000000001"))')

    # Textos da Serigrafia (F.SilkS)
    pcb.append('\t(gr_text "IF BETIM RACING - BANCADA HIL" (at 70.0 18.5) (layer "F.SilkS") (uuid "b0000000-0000-0000-0000-000000000002") (effects (font (size 1.8 1.8) (thickness 0.3) bold)))')
    pcb.append('\t(gr_text "SPEEDUINO 48-WAY & KTM DUKE 390" (at 70.0 22.0) (layer "F.SilkS") (uuid "b0000000-0000-0000-0000-000000000003") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    pcb.append('\t(gr_text "FACE SIMPLES - 100% BOTTOM COPPER" (at 70.0 97.0) (layer "F.SilkS") (uuid "b0000000-0000-0000-0000-000000000004") (effects (font (size 1.2 1.2) (thickness 0.2))))')

    # Identificação na camada de cobre inferior (B.Cu) espelhada para validação da corrosão
    pcb.append('\t(gr_text "IF BETIM RACING - B.Cu" (at 70.0 94.0) (layer "B.Cu") (uuid "b0000000-0000-0000-0000-000000000005") (effects (font (size 1.2 1.2) (thickness 0.2)) (justify mirror)))')

    # Furos de fixação nos 4 cantos (M3 - furo 3.2mm, pad 6.0mm)
    for corner_x, corner_y, cid in [(18.5, 18.5, "1"), (121.5, 18.5, "2"), (18.5, 96.5, "3"), (121.5, 96.5, "4")]:
        pcb.append(f'\t(footprint "MountingHole:MountingHole_3.2mm_M3" (layer "F.Cu") (uuid "m0000000-0000-0000-0000-00000000000{cid}") (at {corner_x} {corner_y})')
        pcb.append(f'\t\t(pad "1" thru_hole circle (at 0 0) (size 6.0 6.0) (drill 3.2) (layers "*.Cu" "*.Mask") (net 16 "GND"))')
        pcb.append('\t)')

    # ================= 1. FOOTPRINT U1: ESP32 DEVKIT V1 30 PINOS =================
    # Centro em (X=36.0, Y=56.0). Fileira Esquerda X=24.57, Fileira Direita X=47.43 (largura 22.86mm / 0.9")
    u1_x, u1_y = 36.0, 56.0
    u1_row_w = 22.86
    u1_lx = u1_x - u1_row_w / 2.0  # 24.57
    u1_rx = u1_x + u1_row_w / 2.0  # 47.43
    u1_y_start = u1_y - 7 * 2.54    # 38.22
    
    # Mapeamento de pinos do ESP32 para Nets
    # Pinos esquerda: 1 a 15
    u1_left_nets = [
        (1, "EN", 0), (2, "VP", 0), (3, "VN", 0), (4, "D34", 0), (5, "D35", 0),
        (6, "D32", 0), (7, "D33", 0), (8, "D25", 17), (9, "D26", 18), (10, "D27", 8),
        (11, "D14", 10), (12, "D12", 0), (13, "D13", 0), (14, "GND", 16), (15, "VIN", 2)
    ]
    # Pinos direita: 30 a 16 (de cima para baixo)
    u1_right_nets = [
        (30, "D23", 0), (29, "D22", 9), (28, "TX0", 0), (27, "RX0", 0), (26, "D21", 0),
        (25, "D19", 0), (24, "D18", 0), (23, "D5", 6), (22, "D17", 0), (21, "D16", 15),
        (20, "D4", 7), (19, "D0", 0), (18, "D2", 0), (17, "D15", 3), (16, "3V3", 1)
    ]

    pcb.append(f'\t(footprint "Module:ESP32_DevKit_V1_30Pin" (layer "F.Cu") (uuid "f1000000-0000-0000-0000-000000000001") (at {u1_x} {u1_y})')
    pcb.append(f'\t\t(property "Reference" "U1" (at 0 -20.0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    pcb.append(f'\t\t(property "Value" "ESP32_DevKit_V1" (at 0 20.0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_rect (start -13.0 -19.5) (end 13.0 19.5) (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS"))')
    pcb.append(f'\t\t(fp_text user "ESP32 DevKit V1" (at 0 0 90) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    
    # Pads esquerda
    for idx, (pnum, pname, pnet) in enumerate(u1_left_nets):
        py = -7 * 2.54 + idx * 2.54
        pad_shape = "roundrect (roundrect_rratio 0.25)" if pnum == 1 else "circle"
        pcb.append(f'\t\t(pad "{pnum}" thru_hole {pad_shape} (at -11.43 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')

    # Pads direita
    for idx, (pnum, pname, pnet) in enumerate(u1_right_nets):
        py = -7 * 2.54 + idx * 2.54
        pcb.append(f'\t\t(pad "{pnum}" thru_hole circle (at 11.43 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
    pcb.append('\t)')

    # ================= 2. FOOTPRINT U2: PCM5102A MODULE (GY-PCM5102) =================
    # Centro em (X=72.0, Y=36.0). Largura entre fileiras = 15.24 mm (600 mil)
    # Fileira esquerda: VCC(1), GND(2), BCK(3), DIN(4), LCK(5), SCK(6)
    # Fileira direita: XMT(7), FMT(8), FLT(9), DMP(10), LOUT(11), AGND(12), ROUT(13)
    u2_x, u2_y = 72.0, 36.0
    u2_nets_left = [
        (1, "VCC", 2), (2, "GND", 16), (3, "BCK", 8), (4, "DIN", 9), (5, "LCK", 10), (6, "SCK", 16)
    ]
    u2_nets_right = [
        (7, "XMT", 1), (8, "FMT", 16), (9, "FLT", 16), (10, "DMP", 16), (11, "LOUT", 5), (12, "AGND", 4), (13, "ROUT", 0)
    ]
    pcb.append(f'\t(footprint "Module:PCM5102A_Module" (layer "F.Cu") (uuid "f2000000-0000-0000-0000-000000000001") (at {u2_x} {u2_y})')
    pcb.append(f'\t\t(property "Reference" "U2" (at 0 -11.0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    pcb.append(f'\t\t(property "Value" "GY-PCM5102A" (at 0 11.0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_rect (start -10.0 -9.5) (end 10.0 9.5) (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS"))')
    pcb.append(f'\t\t(fp_text user "PCM5102A (I2S DAC)" (at 0 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    
    # Pads esquerda U2 (X = -7.62)
    for idx, (pnum, pname, pnet) in enumerate(u2_nets_left):
        py = -2.5 * 2.54 + idx * 2.54
        pad_shape = "roundrect (roundrect_rratio 0.25)" if pnum == 1 else "circle"
        pcb.append(f'\t\t(pad "{pnum}" thru_hole {pad_shape} (at -7.62 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')

    # Pads direita U2 (X = +7.62)
    for idx, (pnum, pname, pnet) in enumerate(u2_nets_right):
        py = -3.0 * 2.54 + idx * 2.54
        pcb.append(f'\t\t(pad "{pnum}" thru_hole circle (at 7.62 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
    pcb.append('\t)')

    # ================= 3. FOOTPRINT U3: LEVEL CONVERTER 4CH =================
    # Centro em (X=72.0, Y=68.0). Largura entre fileiras = 12.7 mm (500 mil)
    # Fileira esquerda (LV side): LV(7), GND(8), LV1(9), LV2(10), LV3(11), LV4(12)
    # Fileira direita (HV side): HV(1), GND(2), HV1(3), HV2(4), HV3(5), HV4(6)
    u3_x, u3_y = 72.0, 68.0
    u3_nets_left = [
        (7, "LV", 1), (8, "GND", 16), (9, "LV1", 6), (10, "LV2", 7), (11, "LV3", 0), (12, "LV4", 0)
    ]
    u3_nets_right = [
        (1, "HV", 2), (2, "GND", 16), (3, "HV1", 13), (4, "HV2", 14), (5, "HV3", 0), (6, "HV4", 0)
    ]
    pcb.append(f'\t(footprint "Module:Level_Converter_4CH" (layer "F.Cu") (uuid "f3000000-0000-0000-0000-000000000001") (at {u3_x} {u3_y})')
    pcb.append(f'\t\t(property "Reference" "U3" (at 0 -10.0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    pcb.append(f'\t\t(property "Value" "Level_Converter" (at 0 10.0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_rect (start -8.5 -8.5) (end 8.5 8.5) (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS"))')
    pcb.append(f'\t\t(fp_text user "LV (3V3) <-> HV (5V)" (at 0 0 90) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15))))')
    
    # Pads esquerda U3 (LV side, X = -6.35)
    for idx, (pnum, pname, pnet) in enumerate(u3_nets_left):
        py = -2.5 * 2.54 + idx * 2.54
        pcb.append(f'\t\t(pad "{pnum}" thru_hole circle (at -6.35 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')

    # Pads direita U3 (HV side, X = +6.35)
    for idx, (pnum, pname, pnet) in enumerate(u3_nets_right):
        py = -2.5 * 2.54 + idx * 2.54
        pad_shape = "roundrect (roundrect_rratio 0.25)" if pnum == 1 else "circle"
        pcb.append(f'\t\t(pad "{pnum}" thru_hole {pad_shape} (at 6.35 {py:.2f}) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
    pcb.append('\t)')

    # ================= 4. FOOTPRINT J1: BORNIER SPEEDUINO (9 PINOS, P5.08mm) =================
    # Colocado na borda direita: X = 114.0, Y = 58.0.
    # Pinos de 1 a 9 espaçados em 5.08 mm (Y de 37.68 até 78.32)
    j1_x, j1_y = 114.0, 58.0
    j1_nets = [
        (1, "CRANK+", 5),
        (2, "VR1-", 4),
        (3, "TPS", 12),
        (4, "MAP", 11),
        (5, "VSS", 15),
        (6, "CLUTCH", 3),
        (7, "INJ", 14),
        (8, "IGN", 13),
        (9, "GND", 16),
    ]
    pcb.append(f'\t(footprint "Connector_TerminalBlock:TerminalBlock_bornier-9_P5.08mm" (layer "F.Cu") (uuid "f4000000-0000-0000-0000-000000000001") (at {j1_x} {j1_y})')
    pcb.append(f'\t\t(property "Reference" "J1" (at 0 -24.0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))')
    pcb.append(f'\t\t(property "Value" "CHICOTE_SPEEDUINO" (at 0 24.0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_rect (start -4.5 -22.5) (end 4.5 22.5) (stroke (width 0.25) (type solid)) (fill none) (layer "F.SilkS"))')
    
    for idx, (pnum, pname, pnet) in enumerate(j1_nets):
        py = -4 * 5.08 + idx * 5.08
        pad_shape = "roundrect (roundrect_rratio 0.25)" if pnum == 1 else "circle"
        pcb.append(f'\t\t(pad "{pnum}" thru_hole {pad_shape} (at 0 {py:.2f}) (size 3.2 3.2) (drill 1.4) (layers "*.Cu" "*.Mask") (net {pnet} "{[n[1] for n in nets if n[0]==pnet][0]}"))')
        pcb.append(f'\t\t(fp_text user "{pname}" (at -7.0 {py:.2f}) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15)) (justify right)))')
    pcb.append('\t)')

    # ================= 5. COMPONENTES PASSIVOS: FILTROS RC (R1, C1, R2, C2) =================
    # Posicionados na parte inferior esquerda (abaixo do ESP32)
    # R1 (10k TPS): Centro (X=26.0, Y=86.0). Horizontal, pads a -3.81 e +3.81 (17.5 a 17 e 12)
    # P1 (X=22.19) -> Net 12 (NET_TPS_OUT), P2 (X=29.81) -> Net 17 (D25)
    r1_x, r1_y = 26.0, 86.0
    pcb.append(f'\t(footprint "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" (layer "F.Cu") (uuid "f5000000-0000-0000-0000-000000000001") (at {r1_x} {r1_y})')
    pcb.append(f'\t\t(property "Reference" "R1" (at 0 -2.5) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(property "Value" "10k (TPS)" (at 0 2.5) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_rect (start -4.0 -1.5) (end 4.0 1.5) (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS"))')
    pcb.append(f'\t\t(pad "1" thru_hole circle (at -5.08 0) (size 2.4 2.4) (drill 1.0) (layers "*.Cu" "*.Mask") (net 12 "/NET_TPS_OUT"))')
    pcb.append(f'\t\t(pad "2" thru_hole circle (at 5.08 0) (size 2.4 2.4) (drill 1.0) (layers "*.Cu" "*.Mask") (net 17 "Net-(U1-D25_(DAC_TPS))"))')
    pcb.append('\t)')

    # C1 (1uF TPS): Centro (X=26.0, Y=92.0). Horizontal, pads a -2.54 e +2.54
    # P1 (X=23.46) -> Net 12 (NET_TPS_OUT), P2 (X=28.54) -> Net 16 (GND)
    c1_x, c1_y = 26.0, 92.0
    pcb.append(f'\t(footprint "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" (layer "F.Cu") (uuid "f6000000-0000-0000-0000-000000000001") (at {c1_x} {c1_y})')
    pcb.append(f'\t\t(property "Reference" "C1" (at 0 -2.5) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(property "Value" "1uF (TPS)" (at 0 2.5) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_line (start -3.0 -1.0) (end 3.0 -1.0) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
    pcb.append(f'\t\t(pad "1" thru_hole circle (at -2.54 0) (size 2.4 2.4) (drill 1.0) (layers "*.Cu" "*.Mask") (net 12 "/NET_TPS_OUT"))')
    pcb.append(f'\t\t(pad "2" thru_hole circle (at 2.54 0) (size 2.4 2.4) (drill 1.0) (layers "*.Cu" "*.Mask") (net 16 "GND"))')
    pcb.append('\t)')

    # R2 (10k MAP): Centro (X=46.0, Y=86.0)
    # P1 (X=40.92) -> Net 11 (NET_MAP_OUT), P2 (X=51.08) -> Net 18 (D26)
    r2_x, r2_y = 46.0, 86.0
    pcb.append(f'\t(footprint "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" (layer "F.Cu") (uuid "f7000000-0000-0000-0000-000000000001") (at {r2_x} {r2_y})')
    pcb.append(f'\t\t(property "Reference" "R2" (at 0 -2.5) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(property "Value" "10k (MAP)" (at 0 2.5) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_rect (start -4.0 -1.5) (end 4.0 1.5) (stroke (width 0.2) (type solid)) (fill none) (layer "F.SilkS"))')
    pcb.append(f'\t\t(pad "1" thru_hole circle (at -5.08 0) (size 2.4 2.4) (drill 1.0) (layers "*.Cu" "*.Mask") (net 11 "/NET_MAP_OUT"))')
    pcb.append(f'\t\t(pad "2" thru_hole circle (at 5.08 0) (size 2.4 2.4) (drill 1.0) (layers "*.Cu" "*.Mask") (net 18 "Net-(U1-D26_(DAC_MAP))"))')
    pcb.append('\t)')

    # C2 (1uF MAP): Centro (X=46.0, Y=92.0)
    # P1 (X=43.46) -> Net 11 (NET_MAP_OUT), P2 (X=48.54) -> Net 16 (GND)
    c2_x, c2_y = 46.0, 92.0
    pcb.append(f'\t(footprint "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" (layer "F.Cu") (uuid "f8000000-0000-0000-0000-000000000001") (at {c2_x} {c2_y})')
    pcb.append(f'\t\t(property "Reference" "C2" (at 0 -2.5) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))')
    pcb.append(f'\t\t(property "Value" "1uF (MAP)" (at 0 2.5) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15))))')
    pcb.append(f'\t\t(fp_line (start -3.0 -1.0) (end 3.0 -1.0) (stroke (width 0.2) (type solid)) (layer "F.SilkS"))')
    pcb.append(f'\t\t(pad "1" thru_hole circle (at -2.54 0) (size 2.4 2.4) (drill 1.0) (layers "*.Cu" "*.Mask") (net 11 "/NET_MAP_OUT"))')
    pcb.append(f'\t\t(pad "2" thru_hole circle (at 2.54 0) (size 2.4 2.4) (drill 1.0) (layers "*.Cu" "*.Mask") (net 16 "GND"))')
    pcb.append('\t)')

    # ================= TRILHAS DE COBRE (100% NA CAMADA B.Cu) =================
    # Largura de trilha para sinais = 0.8 mm (fácil corrosão manual)
    # Largura de trilha para alimentação/GND = 1.2 mm
    tw_sig = 0.8
    tw_pwr = 1.2
    
    seg_id = 1
    def add_seg(x1, y1, x2, y2, net_id, width=tw_sig):
        nonlocal seg_id
        pcb.append(f'\t(segment (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (width {width}) (layer "B.Cu") (net {net_id}) (uuid "s0000000-0000-0000-0000-{seg_id:012d}"))')
        seg_id += 1

    # 1. R1.2 <-> U1.8 (DAC1_TPS - Net 17)
    # U1.8 está em (24.57, 56.00). R1.2 está em (31.08, 86.00)
    add_seg(24.57, 56.00, 20.00, 56.00, 17)
    add_seg(20.00, 56.00, 20.00, 82.00, 17)
    add_seg(20.00, 82.00, 31.08, 82.00, 17)
    add_seg(31.08, 82.00, 31.08, 86.00, 17)

    # 2. R2.2 <-> U1.9 (DAC2_MAP - Net 18)
    # U1.9 está em (24.57, 58.54). R2.2 está em (51.08, 86.00)
    add_seg(24.57, 58.54, 21.50, 58.54, 18)
    add_seg(21.50, 58.54, 21.50, 83.50, 18)
    add_seg(21.50, 83.50, 51.08, 83.50, 18)
    add_seg(51.08, 83.50, 51.08, 86.00, 18)

    # 3. NET_TPS_OUT (Net 12): R1.1(20.92, 86.0) <-> C1.1(23.46, 92.0) <-> J1.3(114.0, 47.84)
    add_seg(20.92, 86.00, 23.46, 86.00, 12)
    add_seg(23.46, 86.00, 23.46, 92.00, 12)
    # Segue pela margem inferior até J1.3
    add_seg(23.46, 92.00, 23.46, 94.50, 12)
    add_seg(23.46, 94.50, 107.00, 94.50, 12)
    add_seg(107.00, 94.50, 107.00, 47.84, 12)
    add_seg(107.00, 47.84, 114.00, 47.84, 12)

    # 4. NET_MAP_OUT (Net 11): R2.1(40.92, 86.0) <-> C2.1(43.46, 92.0) <-> J1.4(114.0, 52.92)
    add_seg(40.92, 86.00, 43.46, 86.00, 11)
    add_seg(43.46, 86.00, 43.46, 92.00, 11)
    add_seg(43.46, 92.00, 43.46, 96.00, 11)
    add_seg(43.46, 96.00, 109.00, 96.00, 11)
    add_seg(109.00, 96.00, 109.00, 52.92, 11)
    add_seg(109.00, 52.92, 114.00, 52.92, 11)

    # 5. I2S_BCK (Net 8): U1.10(24.57, 61.08) <-> U2.3(64.38, 34.73)
    add_seg(24.57, 61.08, 18.50, 61.08, 8)
    add_seg(18.50, 61.08, 18.50, 26.00, 8)
    add_seg(18.50, 26.00, 60.00, 26.00, 8)
    add_seg(60.00, 26.00, 60.00, 34.73, 8)
    add_seg(60.00, 34.73, 64.38, 34.73, 8)

    # 6. I2S_LCK (Net 10): U1.11(24.57, 63.62) <-> U2.5(64.38, 39.81)
    add_seg(24.57, 63.62, 17.00, 63.62, 10)
    add_seg(17.00, 63.62, 17.00, 24.50, 10)
    add_seg(17.00, 24.50, 58.50, 24.50, 10)
    add_seg(58.50, 24.50, 58.50, 39.81, 10)
    add_seg(58.50, 39.81, 64.38, 39.81, 10)

    # 7. I2S_DIN (Net 9): U1.29(47.43, 40.76) <-> U2.4(64.38, 37.27)
    add_seg(47.43, 40.76, 52.00, 40.76, 9)
    add_seg(52.00, 40.76, 52.00, 37.27, 9)
    add_seg(52.00, 37.27, 64.38, 37.27, 9)

    # 8. CRANK_VR_POS (Net 5): U2.11(79.62, 39.81) <-> J1.1(114.0, 37.68)
    add_seg(79.62, 39.81, 88.00, 39.81, 5)
    add_seg(88.00, 39.81, 88.00, 37.68, 5)
    add_seg(88.00, 37.68, 114.00, 37.68, 5)

    # 9. CRANK_VR_NEG (Net 4): U2.12(79.62, 42.35) <-> J1.2(114.0, 42.76)
    add_seg(79.62, 42.35, 90.00, 42.35, 4)
    add_seg(90.00, 42.35, 90.00, 42.76, 4)
    add_seg(90.00, 42.76, 114.00, 42.76, 4)

    # 10. VSS_PULSE (Net 15): U1.21(47.43, 61.08) <-> J1.5(114.0, 58.00)
    add_seg(47.43, 61.08, 54.00, 61.08, 15)
    add_seg(54.00, 61.08, 54.00, 55.00, 15)
    add_seg(54.00, 55.00, 105.00, 55.00, 15)
    add_seg(105.00, 55.00, 105.00, 58.00, 15)
    add_seg(105.00, 58.00, 114.00, 58.00, 15)

    # 11. CLUTCH_SIG (Net 3): U1.17(47.43, 71.24) <-> J1.6(114.0, 63.08)
    add_seg(47.43, 71.24, 56.00, 71.24, 3)
    add_seg(56.00, 71.24, 56.00, 79.50, 3)
    add_seg(56.00, 79.50, 103.00, 79.50, 3)
    add_seg(103.00, 79.50, 103.00, 63.08, 3)
    add_seg(103.00, 63.08, 114.00, 63.08, 3)

    # 12. FB_IGN_3V3 (Net 6): U1.23(47.43, 56.00) <-> U3.9(65.65, 66.73)
    add_seg(47.43, 56.00, 58.00, 56.00, 6)
    add_seg(58.00, 56.00, 58.00, 66.73, 6)
    add_seg(58.00, 66.73, 65.65, 66.73, 6)

    # 13. FB_INJ_3V3 (Net 7): U1.20(47.43, 63.62) <-> U3.10(65.65, 69.27)
    add_seg(47.43, 63.62, 60.00, 63.62, 7)
    add_seg(60.00, 63.62, 60.00, 69.27, 7)
    add_seg(60.00, 69.27, 65.65, 69.27, 7)

    # 14. SPEEDUINO_IGN (Net 13): U3.3(78.35, 66.73) <-> J1.8(114.0, 73.24)
    add_seg(78.35, 66.73, 88.00, 66.73, 13)
    add_seg(88.00, 66.73, 88.00, 73.24, 13)
    add_seg(88.00, 73.24, 114.00, 73.24, 13)

    # 15. SPEEDUINO_INJ (Net 14): U3.4(78.35, 69.27) <-> J1.7(114.0, 68.16)
    add_seg(78.35, 69.27, 86.00, 69.27, 14)
    add_seg(86.00, 69.27, 86.00, 68.16, 14)
    add_seg(86.00, 68.16, 114.00, 68.16, 14)

    # 16. ALIMENTAÇÃO +5V (Net 2): U1.15(24.57, 73.78) <-> U2.1(64.38, 29.65) <-> U3.1(78.35, 61.65)
    # Rota ao redor do ESP32 até U2.1 e U3.1 com trilha larga (1.2mm)
    add_seg(24.57, 73.78, 22.00, 73.78, 2, tw_pwr)
    add_seg(22.00, 73.78, 22.00, 27.50, 2, tw_pwr)
    add_seg(22.00, 27.50, 64.38, 27.50, 2, tw_pwr)
    add_seg(64.38, 27.50, 64.38, 29.65, 2, tw_pwr)
    # De (64.38, 27.50) desce pela lateral do U3.1
    add_seg(64.38, 27.50, 92.00, 27.50, 2, tw_pwr)
    add_seg(92.00, 27.50, 92.00, 61.65, 2, tw_pwr)
    add_seg(92.00, 61.65, 78.35, 61.65, 2, tw_pwr)

    # 17. ALIMENTAÇÃO +3V3 (Net 1): U1.16(47.43, 73.78) <-> U2.7(79.62, 29.65) <-> U3.7(65.65, 61.65)
    add_seg(47.43, 73.78, 52.00, 73.78, 1, tw_pwr)
    add_seg(52.00, 73.78, 52.00, 61.65, 1, tw_pwr)
    add_seg(52.00, 61.65, 65.65, 61.65, 1, tw_pwr)
    # Continua subindo até U2.7 (XMT)
    add_seg(52.00, 61.65, 52.00, 48.00, 1, tw_pwr)
    add_seg(52.00, 48.00, 76.00, 48.00, 1, tw_pwr)
    add_seg(76.00, 48.00, 76.00, 29.65, 1, tw_pwr)
    add_seg(76.00, 29.65, 79.62, 29.65, 1, tw_pwr)

    # 18. TERRA COMUM GND (Net 16):
    # Conecta C1.2, C2.2, U1.14, U2(2,6,8,9,10), U3(2,8), J1.9
    # Barramento de terra unificado na margem inferior e subindo entre os módulos
    add_seg(28.54, 92.00, 28.54, 88.00, 16, tw_pwr)
    add_seg(28.54, 88.00, 48.54, 88.00, 16, tw_pwr)
    add_seg(48.54, 88.00, 48.54, 92.00, 16, tw_pwr)
    # Liga U1.14 GND
    add_seg(24.57, 71.24, 28.54, 71.24, 16, tw_pwr)
    add_seg(28.54, 71.24, 28.54, 88.00, 16, tw_pwr)
    # Segue até J1.9 (GND sensores da Speeduino)
    add_seg(48.54, 88.00, 96.00, 88.00, 16, tw_pwr)
    add_seg(96.00, 88.00, 96.00, 78.32, 16, tw_pwr)
    add_seg(96.00, 78.32, 114.00, 78.32, 16, tw_pwr)
    # Sobe para U3.2 e U3.8 (GND conversor)
    add_seg(96.00, 78.32, 96.00, 64.19, 16, tw_pwr)
    add_seg(96.00, 64.19, 78.35, 64.19, 16, tw_pwr) # U3.2
    add_seg(78.35, 64.19, 65.65, 64.19, 16, tw_pwr) # U3.8
    # Sobe até U2 (GND pcm5102: pinos 2, 6, 8, 9, 10)
    add_seg(96.00, 64.19, 96.00, 32.19, 16, tw_pwr)
    add_seg(96.00, 32.19, 79.62, 32.19, 16, tw_pwr) # U2.8
    # Interliga pinos 8, 9, 10 do PCM5102 no lado direito
    add_seg(79.62, 32.19, 79.62, 37.27, 16, tw_pwr) # U2.8 -> U2.10
    # Liga pinos 2 e 6 do PCM5102 no lado esquerdo
    add_seg(79.62, 32.19, 64.38, 32.19, 16, tw_pwr) # U2.2
    add_seg(64.38, 32.19, 64.38, 42.35, 16, tw_pwr) # U2.2 -> U2.6

    pcb.append(')')
    return '\n'.join(pcb)

if __name__ == '__main__':
    pcb_content = generate_pcb()
    out_pcb = 'Circuito_HIL/Circuito_HIL.kicad_pcb'
    with open(out_pcb, 'w', encoding='utf-8') as f:
        f.write(pcb_content)
    print("Circuito_HIL.kicad_pcb gerado com sucesso!")
