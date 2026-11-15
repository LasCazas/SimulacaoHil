import subprocess

pcb_header = """(kicad_pcb
\t(version 20240108)
\t(generator "kicad_cli")
\t(generator_version "10.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(31 "B.Cu" signal)
\t\t(36 "B.SilkS" user "B.Silkscreen")
\t\t(37 "F.SilkS" user "F.Silkscreen")
\t\t(38 "B.Mask" user)
\t\t(39 "F.Mask" user)
\t\t(44 "Edge.Cuts" user)
\t)
\t(setup
\t\t(pad_to_mask_clearance 0.1)
\t)
\t(net 0 "")
\t(gr_rect (start 10 10) (end 110 90) (stroke (width 0.2) (type default)) (fill none) (layer "Edge.Cuts") (uuid "c1c2c3c4-0000-0000-0000-000000000001"))
)"""

with open('Circuito_HIL/test_board.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(pcb_header)

res = subprocess.run([
    r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe',
    'pcb', 'export', 'pdf',
    '--layers', 'Edge.Cuts',
    '--output', 'Circuito_HIL/test_board.pdf',
    'Circuito_HIL/test_board.kicad_pcb'
], capture_output=True, text=True)

print('Returncode:', res.returncode)
print('Stdout:', res.stdout)
print('Stderr:', res.stderr)
