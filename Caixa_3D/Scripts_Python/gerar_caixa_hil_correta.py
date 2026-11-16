"""Modelador Paramétrico da Caixinha HIL em Posição Correta (In-Place).
A tampa fica com o teto FECHADO para cima, a cavidade para baixo e o logo 3D no topo!
"""

import cadquery as cq
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# ==================== PARÂMETROS ====================
placa_l = 180.0   # Comprimento (X) - fenolite 18 cm
placa_w = 75.0    # Largura (Y) - fenolite 7,5 cm
esp_saliente = 5.0 # ESP32 5mm pra fora da fenolite

folga_xy = 5.0
c_int = placa_l + 2 * folga_xy        # 190.0 mm
l_int = placa_w + esp_saliente + 7.0  # 87.0 mm
h_int = 30.0                          # 30.0 mm altura interna útil mínima

wall = 3.0
floor = 3.0
lid_thick = 3.0

c_ext = c_int + 2 * wall   # 196.0 mm
l_ext = l_int + 2 * wall   # 93.0 mm
# Standoffs têm 6 mm sobre fundo de 3 mm -> base da fenolite em Z = 9 mm.
# Partição em Z = 20,0 mm coincide exatamente com o degrau do conector frontal!
# O centro do ESP32 continua a 13 mm acima da fenolite (usb_z_center = 22,0 mm).
h_base = 20.0              # Z = 0 a 20 mm
h_tampa = 16.0             # Z = 20 a 36 mm (h_int = 30,0 mm + floor 3 + teto 3 = 36,0 mm)
z_split = h_base           # 20.0 mm
z_top = h_base + h_tampa   # 36.0 mm

# Conector Automotivo Retangular Deitado (26 x 12 mm nominal + 1,0 mm de margem de segurança = 27,0 x 13,0 mm)
iso_w = 27.0
iso_h = 13.0
z_iso_bot = 10.0
z_iso_top = z_iso_bot + iso_h                 # 23.0 mm
z_iso_center = (z_iso_bot + z_iso_top) / 2.0  # 16.5 mm

# Janela USB do ESP32 - DEITADO na lateral direita (-Y), centrado a 13 mm da fenolite (Z = 22,0 mm)
# Centro do furo próximo ao ESP32 em X = +75,0 mm -> 17,5 mm antes do furo = 57,5 mm (borda física USB a 13,0 mm do furo)
usb_w = 14.0
usb_h = 9.0
usb_x = 57.5
usb_z_center = 22.0

print(f"1. Modelando a Base (Z = 0 até {h_base} mm)...")

# ==================== 1. BASE (Z = 0 até 32) ====================
base = (
    cq.Workplane("XY")
    .box(c_ext, l_ext, h_base, centered=(True, True, False))
    .edges("|Z")
    .fillet(6.0)
)

cavidade_base = (
    cq.Workplane("XY")
    .workplane(offset=floor)
    .box(c_int, l_int, h_base - floor + 1.0, centered=(True, True, False))
    .edges("|Z")
    .fillet(3.0)
)
base = base.cut(cavidade_base)

# Torres internas de apoio da fenolite (entre-centros 150,0 x 55,0 mm -> 15,0 mm da borda da placa de 180 mm)
h_standoff = 6.0
pos_standoffs = [
    (150.0 / 2.0, 55.0 / 2.0),
    (150.0 / 2.0, -(55.0 / 2.0)),
    (-(150.0 / 2.0), 55.0 / 2.0),
    (-(150.0 / 2.0), -(55.0 / 2.0)),
]

for sx, sy in pos_standoffs:
    post = (
        cq.Workplane("XY")
        .workplane(offset=floor)
        .circle(4.0)
        .extrude(h_standoff)
    )
    furo_post = (
        cq.Workplane("XY")
        .workplane(offset=floor)
        .circle(1.3)
        .extrude(h_standoff + 1.0)
    )
    post = post.cut(furo_post).translate((sx, sy, 0))
    base = base.union(post)

# 4 Torres nos Cantos para fechamento com parafusos M3
pos_corner_posts = [
    (c_int / 2 - 4.0, l_int / 2 - 4.0),
    (c_int / 2 - 4.0, -(l_int / 2 - 4.0)),
    (-(c_int / 2 - 4.0), l_int / 2 - 4.0),
    (-(c_int / 2 - 4.0), -(l_int / 2 - 4.0)),
]

for cx, cy in pos_corner_posts:
    corner_post = (
        cq.Workplane("XY")
        .workplane(offset=floor)
        .circle(4.5)
        .extrude(h_base - floor)
    )
    furo_corner = (
        cq.Workplane("XY")
        .workplane(offset=floor + 3.0)
        .circle(1.4)
        .extrude(h_base - floor)
    )
    corner_post = corner_post.cut(furo_corner).translate((cx, cy, 0))
    base = base.union(corner_post)

# 4 Orelhas Externas de Fixação
pos_orelhas = [
    (c_ext / 4, l_ext / 2),
    (-c_ext / 4, l_ext / 2),
    (c_ext / 4, -l_ext / 2),
    (-c_ext / 4, -l_ext / 2),
]

for ox, oy in pos_orelhas:
    sinal_y = 1.0 if oy > 0 else -1.0
    orelha = (
        cq.Workplane("XY")
        .box(24.0, 16.0, 7.0, centered=(True, False, False))
        .edges("|Z")
        .fillet(4.0)
    )
    furo_orelha = (
        cq.Workplane("XY")
        .circle(2.3)
        .extrude(8.0)
        .translate((0, 8.0, 0))
    )
    rebaixo_orelha = (
        cq.Workplane("XY")
        .workplane(offset=3.5)
        .circle(4.5)
        .extrude(5.0)
        .translate((0, 8.0, 0))
    )
    orelha = orelha.cut(furo_orelha).cut(rebaixo_orelha)
    if sinal_y < 0:
        orelha = orelha.rotate((0, 0, 0), (0, 0, 1), 180)
    orelha = orelha.translate((ox, oy, 0))
    base = base.union(orelha)

# Zonas das janelas ISO e USB (com folga extra para bordas internas limpas sem invadir o lip)
zona_limpa_iso = (
    cq.Workplane("XY")
    .box(24.0, iso_w + 1.5, 20.0, centered=(True, True, True))
    .translate((-c_ext / 2, 0, z_split))
)
zona_limpa_usb = (
    cq.Workplane("XY")
    .box(usb_w + 1.0, 24.0, 20.0, centered=(True, True, True))
    .translate((usb_x, -l_ext / 2, usb_z_center))
)

# Borda Macho (Lip) de 1.8mm para vedação e travamento da tampa (ANTES dos recortes e sem invadir as janelas)
lip = (
    cq.Workplane("XY")
    .workplane(offset=h_base)
    .box(c_int + 1.2, l_int + 1.2, 1.8, centered=(True, True, False))
    .edges("|Z")
    .fillet(2.5)
)
lip_vazio = (
    cq.Workplane("XY")
    .workplane(offset=h_base - 1.0)
    .box(c_int - 1.6, l_int - 1.6, 4.0, centered=(True, True, False))
    .edges("|Z")
    .fillet(1.5)
)
lip = lip.cut(lip_vazio).cut(zona_limpa_iso).cut(zona_limpa_usb)
base = base.union(lip)

# Recorte Frontal Retangular Deitado (27,0 x 13,0 mm = 26x12 mm nominal + 1 mm folga, Z = 10,0 a 23,0 mm)
recorte_iso = (
    cq.Workplane("XY")
    .box(20.0, iso_w, iso_h, centered=(True, True, True))
    .translate((-c_ext / 2, 0.0, z_iso_center))
)
base = base.cut(recorte_iso)

# Janela Lateral para o ESP32 DEITADA (14 mm largura X x 9 mm altura Z, Lado DIREITO Y = -l_ext/2, centro em Z = 22 mm)
recorte_usb = (
    cq.Workplane("XY")
    .box(usb_w, 20.0, usb_h, centered=(True, True, True))
    .translate((usb_x, -l_ext / 2, usb_z_center))
)
base = base.cut(recorte_usb)

print("  -> Base concluída!")


# ==================== 2. TAMPA (Z = 22 até 36 mm) ====================
print(f"2. Modelando a Tampa montada por cima (Z = {z_split} até {z_top} mm)...")

# Corpo da tampa construído de Z = 32 até Z = 60
tampa = (
    cq.Workplane("XY")
    .workplane(offset=z_split)
    .box(c_ext, l_ext, h_tampa, centered=(True, True, False))
    .edges("|Z")
    .fillet(6.0)
)

# Chanfro no teto superior (Z = 60)
tampa = (
    tampa
    .faces(">Z")
    .edges()
    .chamfer(2.5)
)

# Cavidade interna da tampa (aberta embaixo em Z = 32, subindo até Z = 57)
# O teto fica sólido entre Z = 57 e Z = 60 (3mm de espessura de teto)
cavidade_tampa = (
    cq.Workplane("XY")
    .workplane(offset=z_split - 0.5)
    .box(c_int, l_int, h_tampa - lid_thick + 0.5, centered=(True, True, False))
    .edges("|Z")
    .fillet(3.0)
)
tampa = tampa.cut(cavidade_tampa)

# 4 Torres internas nos cantos da tampa (descem do teto até Z = 32, unidas ANTES do canal_lip!)
for cx, cy in pos_corner_posts:
    post_tampa = (
        cq.Workplane("XY")
        .workplane(offset=z_split)
        .circle(4.5)
        .extrude(h_tampa - lid_thick)
        .translate((cx, cy, 0))
    )
    # Furo passante M3 (3.4mm) descendo do teto (Z = 60) até Z = 32
    furo_passante = (
        cq.Workplane("XY")
        .workplane(offset=z_split - 1.0)
        .circle(1.7)
        .extrude(h_tampa + 3.0)
        .translate((cx, cy, 0))
    )
    # Rebaixo para cabeça de parafuso Allen M3 no teto (Z = 60 para baixo 3mm)
    rebaixo_parafuso = (
        cq.Workplane("XY")
        .workplane(offset=z_top - 3.0)
        .circle(3.25)
        .extrude(4.0)
        .translate((cx, cy, 0))
    )
    tampa = tampa.union(post_tampa).cut(furo_passante).cut(rebaixo_parafuso)

# Canal fêmea na borda inferior da tampa (Z = 32 até 34.1) com folga radial e em Z para o Lip (Z = 32..33.8)
canal_lip = (
    cq.Workplane("XY")
    .workplane(offset=z_split - 0.5)
    .box(c_int + 2.0, l_int + 2.0, 2.6, centered=(True, True, False))
    .edges("|Z")
    .fillet(2.8)
)
canal_vazio = (
    cq.Workplane("XY")
    .workplane(offset=z_split - 1.0)
    .box(c_int - 2.4, l_int - 2.4, 3.8, centered=(True, True, False))
    .edges("|Z")
    .fillet(1.2)
)
canal_lip = canal_lip.cut(canal_vazio).cut(zona_limpa_iso).cut(zona_limpa_usb)
tampa = tampa.cut(canal_lip)

# Recorte Frontal Retangular Deitado (27,0 x 13,0 mm, Z = 10,0 a 23,0 mm -> complementa na tampa)
tampa = tampa.cut(recorte_iso)

# Recorte USB na lateral DEITADO (14 mm largura X x 9 mm altura Z, lado DIREITO Y = -l_ext/2, centro em Z = 22 mm)
tampa = tampa.cut(recorte_usb)


tampa_sem_logo = tampa

# ==================== 3. VETORIZAÇÃO E LOGO 3D NO TOPO (Z = 36 mm) ====================
print(f"3. Esculpindo o Logo IF Betim Racing no TOPO da caixa (Z = {z_top} mm)...")

def rdp(points, epsilon):
    dmax = 0.0
    index = 0
    end = len(points) - 1
    for i in range(1, end):
        p1 = np.array([points[0][0], points[0][1], 0.0])
        p2 = np.array([points[end][0], points[end][1], 0.0])
        pt = np.array([points[i][0], points[i][1], 0.0])
        if np.all(p1 == p2):
            d = np.linalg.norm(pt - p1)
        else:
            d = np.linalg.norm(np.cross(p2 - p1, p1 - pt)) / np.linalg.norm(p2 - p1)
        if d > dmax:
            index = i
            dmax = d
    if dmax > epsilon:
        rec1 = rdp(points[:index+1], epsilon)
        rec2 = rdp(points[index:], epsilon)
        return np.vstack((rec1[:-1], rec2))
    else:
        return np.array([points[0], points[end]])

logo_img_path = r'C:\Users\willi\.gemini\antigravity-cli\brain\fc6f5296-5fbe-475d-ab4c-aebd6c9bf1b7\.user_uploaded\uploaded_media_1794767874784.png'
img = Image.open(logo_img_path)
img_large = img.resize((img.width * 8, img.height * 8), Image.Resampling.LANCZOS)
arr = np.array(img_large)

red_mask = (arr[:, :, 0] > 140) & (arr[:, :, 1] < 100)
green_mask = (arr[:, :, 1] > 90) & (arr[:, :, 0] < 120)

fig, ax = plt.subplots()
cs_red = ax.contour(red_mask[::-1, :], levels=[0.5])
cs_green = ax.contour(green_mask[::-1, :], levels=[0.5])
red_paths = cs_red.allsegs[0]
green_paths = cs_green.allsegs[0]
plt.close()

all_pts = np.vstack(red_paths + green_paths)
min_x, max_x = all_pts[:, 0].min(), all_pts[:, 0].max()
min_y, max_y = all_pts[:, 1].min(), all_pts[:, 1].max()

orig_w = max_x - min_x
scale = 75.0 / orig_w  # 75mm de comprimento no teto
center_x = (min_x + max_x) / 2.0
center_y = (min_y + max_y) / 2.0

h_relevo = 1.8 # Relevo subindo de Z = 60.0 até Z = 61.8 mm (visível no topo!)
logo_solids_z0 = []

for p in red_paths + green_paths:
    pts_s = rdp(p, epsilon=1.8)
    scaled_pts = [((pt[0] - center_x) * scale, (pt[1] - center_y) * scale) for pt in pts_s]
    if scaled_pts[0] != scaled_pts[-1]:
        scaled_pts.append(scaled_pts[0])
    poly_z0 = (
        cq.Workplane("XY")
        .polyline(scaled_pts[:-1])
        .close()
        .extrude(h_relevo)
    )
    logo_solids_z0.append(poly_z0.val())
    tampa = tampa.union(poly_z0.translate((0, 0, z_top)))

logo_separado = cq.Compound.makeCompound(logo_solids_z0)

print(f"  -> Logo 3D em relevo de {h_relevo}mm posicionado perfeitamente no TOPO (Z = {z_top} a {z_top + h_relevo} mm)!")


# ==================== 4. EXPORTAÇÃO (STEP + STL) ====================
caixa_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(caixa_dir, "Arquivos_Projeto")
os.makedirs(out_dir, exist_ok=True)

step_base = os.path.join(out_dir, "Base_Caixa_HIL.step")
step_tampa = os.path.join(out_dir, "Tampa_Caixa_HIL.step")
step_conjunto = os.path.join(out_dir, "Conjunto_Caixa_HIL_Montada.step")
step_explodida = os.path.join(out_dir, "Conjunto_Caixa_HIL_Vista_Explodida.step")

cq.exporters.export(base, step_base)
cq.exporters.export(tampa, step_tampa)

# Exportação da montagem como 2 PEÇAS SEPARADAS (NÃO unidas por union!)
# Assim no Onshape aparecem Base e Tampa como 2 corpos independentes (dá pra ocultar a tampa e ver dentro!)
assy = cq.Assembly()
assy.add(base, name="Base_Inferior", color=cq.Color(0.15, 0.15, 0.18))
assy.add(tampa, name="Tampa_Superior", color=cq.Color(0.38, 0.40, 0.44))
assy.export(step_conjunto)

# Exportação em Vista Explodida (Tampa deslocada +50 mm em Z para visualização imediata das 2 peças)
assy_explodida = cq.Assembly()
assy_explodida.add(base, name="Base_Inferior", color=cq.Color(0.15, 0.15, 0.18))
assy_explodida.add(tampa.translate((0, 0, 50.0)), name="Tampa_Superior", color=cq.Color(0.38, 0.40, 0.44))
assy_explodida.export(step_explodida)

# Exportação dos arquivos STL apoiados em Z = 0 para impressão 3D (malha fina)
stl_base = os.path.join(out_dir, "Base_Caixa_HIL.stl")
stl_tampa = os.path.join(out_dir, "Tampa_Caixa_HIL.stl")
stl_tampa_inv = os.path.join(out_dir, "Tampa_Sem_Logo_Invertida.stl")
stl_logo = os.path.join(out_dir, "Logo_IF_Separado.stl")

tampa_z0 = tampa.translate((0, 0, -z_split))
tampa_inv_z0 = tampa_sem_logo.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, z_top))

for shape, path in [
    (base, stl_base),
    (tampa_z0, stl_tampa),
    (tampa_inv_z0, stl_tampa_inv),
    (logo_separado, stl_logo),
]:
    cq.exporters.export(shape, path, tolerance=0.05, angularTolerance=0.1)

vol_base_cm3 = base.val().Volume() / 1000.0
vol_tampa_cm3 = tampa.val().Volume() / 1000.0
vol_total_cm3 = vol_base_cm3 + vol_tampa_cm3
inter = base.intersect(tampa)
vol_inter = inter.val().Volume()

with open(step_conjunto, "r", encoding="utf-8", errors="ignore") as f:
    step_txt = f.read()
n_solids = step_txt.count("MANIFOLD_SOLID_BREP")

print(f"\n[SUCESSO COMPLETO] Arquivos STEP e STL gerados!")
print(f"  - Volumes (cm3): Base = {vol_base_cm3:.2f} cm3 | Tampa = {vol_tampa_cm3:.2f} cm3 | Total = {vol_total_cm3:.2f} cm3")
print(f"  - Verificação colisão base.intersect(tampa): {vol_inter:.4f} mm3 | MANIFOLD_SOLID_BREP = {n_solids}")
print(f"  - {step_base}")
print(f"  - {step_tampa}")
print(f"  - {step_conjunto}")
print(f"  - {step_explodida}")
print(f"  - {stl_base}")
print(f"  - {stl_tampa}")
print(f"  - {stl_tampa_inv}")
print(f"  - {stl_logo}")
