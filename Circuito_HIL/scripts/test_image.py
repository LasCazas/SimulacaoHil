import base64
import subprocess

with open('C:/Programacao/projetos/RacingTeam/ecu/1_SImulacaoHil/EngenhariaEconomica/images/logoToRodaPe.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')

with open('Circuito_HIL/Circuito_HIL.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

# KiCad A3 sheet size: 420mm x 297mm.
# Bottom right corner is at X ~ 380, Y ~ 270.
img_str = f'''\t(image (at 300.00 270.00) (scale 0.5) (uuid "f1e2d3c4-0000-0000-0000-000000000099")
\t\t(data
\t\t\t"{b64}"
\t\t)
\t)
)'''

# Replace the last ')'
test_content = content.rstrip()
if test_content.endswith(')'):
    test_content = test_content[:-1] + img_str

with open('Circuito_HIL/test_img.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(test_content)

res = subprocess.run([
    r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe',
    'sch', 'export', 'pdf',
    '--output', 'Circuito_HIL/test_img.pdf',
    'Circuito_HIL/test_img.kicad_sch'
], capture_output=True, text=True)

print('CLI returncode:', res.returncode)
print('CLI stdout:', res.stdout)
print('CLI stderr:', res.stderr)
