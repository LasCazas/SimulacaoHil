"""Gerador de Desenho Técnico em PDF (Formato A3 ABNT) da Caixa HIL Betim Racing.

Gera um PDF vetorial de 2 páginas (versão revisada 180 × 75 mm × H_int 30 mm):
  - Folha 1/2: Vistas Ortográficas Cotadas (Superior, Frontal Conector, Lateral Direita USB e Corte A-A) + Carimbo ABNT com logo.png.
  - Folha 2/2: Vistas Isométricas (Montada, Explodida, Base Interna), Estimativa de Filamento (PLA), BOM e Carimbo ABNT.
"""

import os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import pymupdf


LOGO_CARIMBO_PATH = r"C:\Programacao\projetos\RacingTeam\ecu\1_SImulacaoHil\SimulacaoComG29_ComOPCEEsp\images\logo.png"
LOGO_TOP_RELEVO_PATH = r"C:\Users\willi\.gemini\antigravity-cli\brain\fc6f5296-5fbe-475d-ab4c-aebd6c9bf1b7\.user_uploaded\uploaded_media_1794767874784.png"

CAIXA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(CAIXA_DIR, "Imagens_e_PDF")
PDF_PATH = os.path.join(OUT_DIR, "Desenho_Tecnico_Caixa_HIL.pdf")

# Dimensões reais do modelo CAD (mm) — idênticas a gerar_caixa_hil_correta.py
PLACA_L = 180.0
PLACA_W = 75.0
C_EXT = 196.0
C_INT = 190.0
L_EXT = 93.0
L_INT = 87.0
L_TOTAL_ORELHAS = 125.0
WALL = 3.0
FLOOR = 3.0
LID_THICK = 3.0
H_BASE = 20.0
H_TAMPA = 16.0
H_TOTAL = 36.0
H_INT = 30.0
H_LOGO = 1.8
H_STANDOFF = 6.0

# Conector Automotivo Retangular Deitado (26 x 12 mm nominal + 1,0 mm margem de segurança):
ISO_W = 27.0
ISO_H = 13.0
ISO_Z_BOT = 10.0
ISO_Z_TOP = 23.0
ISO_Z_CENTER = 16.5

USB_W = 14.0
USB_H = 9.0
USB_X = 57.5            # Furo próximo em X=75,0 mm - 17,5 mm = 57,5 mm (borda USB a 13,0 mm do furo)
USB_Z_CENTER = 22.0     # Centrado a 13 mm da fenolite -> Z = 22,0 mm (17,5 a 26,5 mm)

SX, SY = 75.0, 27.5     # Entre-centros standoffs: 150,0 x 55,0 mm (a 15,0 mm das bordas de 180 mm)
CX, CY = 91.0, 39.5     # Entre-centros parafusos M3: 182,0 x 79,0 mm
OX, OY_HOLE = 49.0, 54.5  # Entre-centros orelhas M4: 98,0 x 109,0 mm


def autocrop_png(path: str, pad: int = 12) -> np.ndarray:
    """Recorta margens brancas excessivas das prévias isométricas."""
    im = Image.open(path).convert("RGB")
    arr = np.array(im)
    non_white = np.any(arr < 248, axis=2)
    ys, xs = np.where(non_white)
    if len(xs) == 0 or len(ys) == 0:
        return arr
    x0 = max(0, xs.min() - pad)
    x1 = min(arr.shape[1], xs.max() + pad)
    y0 = max(0, ys.min() - pad)
    y1 = min(arr.shape[0], ys.max() + pad)
    return arr[y0:y1, x0:x1]


def extract_logo_polygons(target_width_mm: float = 75.0) -> list:
    """Extrai polígonos simplificados do logo para plotagem na Vista Superior."""
    img = Image.open(LOGO_TOP_RELEVO_PATH)
    img_large = img.resize((img.width * 8, img.height * 8), Image.Resampling.LANCZOS)
    arr = np.array(img_large)
    red_mask = (arr[:, :, 0] > 140) & (arr[:, :, 1] < 100)
    green_mask = (arr[:, :, 1] > 90) & (arr[:, :, 0] < 120)

    fig, ax = plt.subplots()
    cs_r = ax.contour(red_mask[::-1, :], levels=[0.5])
    cs_g = ax.contour(green_mask[::-1, :], levels=[0.5])
    r_paths = cs_r.allsegs[0]
    g_paths = cs_g.allsegs[0]
    plt.close(fig)

    all_pts = np.vstack(r_paths + g_paths)
    min_x, max_x = all_pts[:, 0].min(), all_pts[:, 0].max()
    min_y, max_y = all_pts[:, 1].min(), all_pts[:, 1].max()
    scale = target_width_mm / (max_x - min_x)
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0

    polys = []
    for p, color in [(seg, "#c62828") for seg in r_paths] + [(seg, "#2e7d32") for seg in g_paths]:
        pts = np.column_stack(((p[:, 0] - cx) * scale, (p[:, 1] - cy) * scale))
        polys.append((pts, color))
    return polys


def setup_a3_sheet() -> tuple:
    """Cria uma figura em formato A3 Paisagem (420 x 297 mm) com sistema de coordenadas em mm."""
    fig = plt.figure(figsize=(420.0 / 25.4, 297.0 / 25.4), dpi=300)
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0.0, 420.0)
    ax.set_ylim(0.0, 297.0)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.add_patch(patches.Rectangle((0, 0), 420, 297, fc="white", ec="#cccccc", lw=0.4))
    ax.add_patch(patches.Rectangle((25, 10), 385, 277, fc="none", ec="#111111", lw=1.2))
    return fig, ax


def draw_title_block(ax, folha_str: str, titulo_vista: str) -> None:
    """Desenha o carimbo ABNT no canto inferior direito (x=235..410, y=10..58)."""
    x0, y0, w, h = 235.0, 10.0, 175.0, 48.0
    ax.add_patch(patches.Rectangle((x0, y0), w, h, fc="#fafafa", ec="#111111", lw=1.1, zorder=5))

    x_div = 290.0
    ax.plot([x_div, x_div], [y0, y0 + h], color="#111111", lw=0.9, zorder=6)
    for yh in [18.0, 28.0, 42.0]:
        ax.plot([x_div, x0 + w], [yh, yh], color="#111111", lw=0.6, zorder=6)
    ax.plot([332.0, 332.0], [10.0, 28.0], color="#111111", lw=0.6, zorder=6)
    ax.plot([370.0, 370.0], [10.0, 28.0], color="#111111", lw=0.6, zorder=6)

    logo_arr = np.array(Image.open(LOGO_CARIMBO_PATH).convert("RGBA"))
    imgbox = OffsetImage(logo_arr, zoom=0.145)
    ab = AnnotationBbox(imgbox, ((x0 + x_div) / 2.0, y0 + h / 2.0), frameon=False, zorder=7)
    ax.add_artist(ab)

    ax.text(292.5, 54.5, "PROJETO:", fontsize=5.5, color="#555555", va="top", zorder=7)
    ax.text(350.0, 47.0, "CAIXA PROTETORA ECU HIL — PLACA 180 × 75 mm",
            fontsize=8.2, fontweight="bold", color="#111111", ha="center", va="center", zorder=7)

    ax.text(292.5, 39.8, "CONTEÚDO:", fontsize=5.5, color="#555555", va="top", zorder=7)
    ax.text(350.0, 32.8, titulo_vista,
            fontsize=7.3, fontweight="bold", color="#1b5e20", ha="center", va="center", zorder=7)

    ax.text(292.5, 26.2, "MATERIAL:", fontsize=5.2, color="#555555", va="top", zorder=7)
    ax.text(311.0, 21.0, "PLA (Impr. 3D)", fontsize=6.8, fontweight="bold", ha="center", va="center", zorder=7)

    ax.text(334.0, 26.2, "UNIDADE:", fontsize=5.2, color="#555555", va="top", zorder=7)
    ax.text(351.0, 21.0, "Milímetros (mm)", fontsize=6.8, fontweight="bold", ha="center", va="center", zorder=7)

    ax.text(372.0, 26.2, "PROJEÇÃO:", fontsize=5.2, color="#555555", va="top", zorder=7)
    ax.text(390.0, 21.0, "1º Diedro ABNT", fontsize=6.6, fontweight="bold", ha="center", va="center", zorder=7)

    ax.text(292.5, 16.2, "EQUIPE:", fontsize=5.2, color="#555555", va="top", zorder=7)
    ax.text(311.0, 12.2, "Betim Racing (IFMG)", fontsize=6.3, fontweight="bold", ha="center", va="center", zorder=7)

    ax.text(334.0, 16.2, "DATA:", fontsize=5.2, color="#555555", va="top", zorder=7)
    ax.text(351.0, 12.2, "15/11/2026", fontsize=6.5, fontweight="bold", ha="center", va="center", zorder=7)

    ax.text(372.0, 16.2, "FOLHA:", fontsize=5.2, color="#555555", va="top", zorder=7)
    ax.text(390.0, 12.2, folha_str, fontsize=7.5, fontweight="bold", color="#b71c1c", ha="center", va="center", zorder=7)


def cota_h(ax, x1: float, x2: float, y_ref1: float, y_ref2: float, y_line: float,
           label: str, color: str = "#1565c0", fontsize: float = 6.8, text_dy: float = 1.6) -> None:
    """Desenha cota horizontal com linhas de extensão e setas."""
    ext_dir = 1.0 if y_line > max(y_ref1, y_ref2) else -1.0
    gap = 1.5 * ext_dir
    over = 2.0 * ext_dir
    ax.plot([x1, x1], [y_ref1 + gap, y_line + over], color=color, lw=0.45, zorder=4)
    ax.plot([x2, x2], [y_ref2 + gap, y_line + over], color=color, lw=0.45, zorder=4)
    ax.annotate("", xy=(x1, y_line), xytext=(x2, y_line),
                arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.65, mutation_scale=7.0), zorder=4)
    va = "bottom" if text_dy >= 0 else "top"
    ax.text((x1 + x2) / 2.0, y_line + text_dy, label, color=color, fontsize=fontsize,
            fontweight="bold", ha="center", va=va,
            bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.88), zorder=5)


def cota_v(ax, y1: float, y2: float, x_ref1: float, x_ref2: float, x_line: float,
           label: str, color: str = "#1565c0", fontsize: float = 6.6, text_dx: float = -1.7,
           outside_arrows: bool = False) -> None:
    """Desenha cota vertical com linhas de extensão e setas."""
    ext_dir = 1.0 if x_line > max(x_ref1, x_ref2) else -1.0
    gap = 1.5 * ext_dir
    over = 2.0 * ext_dir
    ax.plot([x_ref1 + gap, x_line + over], [y1, y1], color=color, lw=0.45, zorder=4)
    ax.plot([x_ref2 + gap, x_line + over], [y2, y2], color=color, lw=0.45, zorder=4)
    y_lo, y_hi = min(y1, y2), max(y1, y2)
    if outside_arrows:
        ax.plot([x_line, x_line], [y_lo, y_hi], color=color, lw=0.55, zorder=4)
        ax.annotate("", xy=(x_line, y_lo), xytext=(x_line, y_lo - 4.0),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=0.65, mutation_scale=6.5), zorder=4)
        ax.annotate("", xy=(x_line, y_hi), xytext=(x_line, y_hi + 4.0),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=0.65, mutation_scale=6.5), zorder=4)
        ax.text(x_line, y_hi + 4.6, label, color=color, fontsize=fontsize,
                fontweight="bold", ha="center", va="bottom", rotation=90,
                bbox=dict(boxstyle="square,pad=0.10", fc="white", ec="none", alpha=0.9), zorder=5)
    else:
        ax.annotate("", xy=(x_line, y1), xytext=(x_line, y2),
                    arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.65, mutation_scale=7.0), zorder=4)
        ax.text(x_line + text_dx, (y1 + y2) / 2.0, label, color=color, fontsize=fontsize,
                fontweight="bold", ha="center", va="center", rotation=90,
                bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.88), zorder=5)


def callout(ax, xy: tuple, xytext: tuple, text: str, ha: str = "left", color: str = "#333333") -> None:
    """Linha de chamada técnica com ponto de ancoragem."""
    ax.plot(xy[0], xy[1], marker="o", ms=2.2, color=color, zorder=6)
    ax.annotate(text, xy=xy, xytext=xytext,
                arrowprops=dict(arrowstyle="-", color=color, lw=0.55),
                fontsize=6.1, color=color, ha=ha, va="center",
                bbox=dict(boxstyle="square,pad=0.18", fc="white", ec="#dddddd", lw=0.4, alpha=0.95),
                zorder=6)


def draw_page_1_orthographic(pdf: PdfPages) -> None:
    """Gera a Folha 1/2 com as vistas ortográficas cotadas e corte técnico."""
    fig, ax = setup_a3_sheet()
    draw_title_block(ax, "1 / 2", "VISTAS ORTOGRÁFICAS COTADAS + CORTE INTERNO A–A (ESCALA 1:1,5)")

    k = 1.0 / 1.5  # Escala 1:1,5

    # ==================== 1. VISTA SUPERIOR (TOPO + FURAÇÕES) ====================
    vx1, vy1 = 132.0, 200.0
    ax.text(vx1, 279.0, "VISTA SUPERIOR — CORPO (196 × 93 mm), FURAÇÃO DA BASE E LOGO NO TOPO",
            fontsize=8.0, fontweight="bold", ha="center", va="center", color="#111111")

    def p1(x, y):
        return vx1 + x * k, vy1 + y * k

    ax.plot([vx1 - 108 * k, vx1 + 108 * k], [vy1, vy1], ls="-.", lw=0.45, color="#888888", zorder=1)
    ax.plot([vx1, vx1], [vy1 - 68 * k, vy1 + 68 * k], ls="-.", lw=0.45, color="#888888", zorder=1)

    ax.add_patch(patches.FancyBboxPatch(
        p1(-C_EXT / 2, -L_EXT / 2), C_EXT * k, L_EXT * k,
        boxstyle=f"round,pad=0,rounding_size={6.0 * k}", fc="#f7f9fb", ec="#111111", lw=1.0, zorder=2
    ))
    ax.add_patch(patches.FancyBboxPatch(
        p1(-C_INT / 2, -L_INT / 2), C_INT * k, L_INT * k,
        boxstyle=f"round,pad=0,rounding_size={3.0 * k}", fc="none", ec="#555555", lw=0.55, ls="--", zorder=2
    ))
    ax.add_patch(patches.Rectangle(
        p1(-PLACA_L / 2, -PLACA_W / 2), PLACA_L * k, PLACA_W * k,
        fc="none", ec="#2e7d32", lw=0.65, ls="-.", zorder=2
    ))

    # 4 Orelhas externas (24 x 16, furos Ø4,6 + rebaixo Ø9,0 em (±49, ±54,5))
    for ox in (-OX, OX):
        for oy_sign in (-1.0, 1.0):
            y_base = (L_EXT / 2.0) if oy_sign > 0 else -(L_EXT / 2.0 + 16.0)
            ax.add_patch(patches.FancyBboxPatch(
                p1(ox - 12.0, y_base), 24.0 * k, 16.0 * k,
                boxstyle=f"round,pad=0,rounding_size={4.0 * k}", fc="#eef2f6", ec="#111111", lw=0.9, zorder=1
            ))
            hx, hy = p1(ox, oy_sign * OY_HOLE)
            ax.add_patch(patches.Circle((hx, hy), 2.3 * k, fc="white", ec="#111111", lw=0.8, zorder=3))
            ax.add_patch(patches.Circle((hx, hy), 4.5 * k, fc="none", ec="#111111", lw=0.5, zorder=3))

    # 4 Torres dos cantos M3 em (±91, ±39,5)
    for cx in (-CX, CX):
        for cy in (-CY, CY):
            px, py = p1(cx, cy)
            ax.add_patch(patches.Circle((px, py), 4.5 * k, fc="none", ec="#666666", lw=0.5, ls="--", zorder=3))
            ax.add_patch(patches.Circle((px, py), 3.25 * k, fc="#ffffff", ec="#111111", lw=0.65, zorder=3))
            ax.add_patch(patches.Circle((px, py), 1.7 * k, fc="#e3f2fd", ec="#111111", lw=0.75, zorder=3))

    # 4 Standoffs da fenolite em (±80, ±27,5)
    for sx in (-SX, SX):
        for sy in (-SY, SY):
            px, py = p1(sx, sy)
            ax.add_patch(patches.Circle((px, py), 4.0 * k, fc="none", ec="#555555", lw=0.6, ls="--", zorder=3))
            ax.add_patch(patches.Circle((px, py), 1.3 * k, fc="none", ec="#555555", lw=0.5, ls="--", zorder=3))

    # Abertura frontal Conector Retangular (27,0 x 13,0 mm) e lateral direita ESP32 USB (14,0 mm em X=57,5)
    ax.add_patch(patches.Rectangle(
        p1(-C_EXT / 2, -ISO_W / 2), WALL * k, ISO_W * k,
        fc="#fff8e1", ec="#e65100", lw=0.9, zorder=3
    ))
    ax.add_patch(patches.Rectangle(
        p1(USB_X - USB_W / 2, -L_EXT / 2), USB_W * k, WALL * k,
        fc="#fff8e1", ec="#e65100", lw=0.9, zorder=3
    ))

    # Logo IF Betim no centro do teto
    for pts, col in extract_logo_polygons(75.0):
        poly_sheet = np.column_stack((vx1 + pts[:, 0] * k, vy1 + pts[:, 1] * k))
        ax.add_patch(patches.Polygon(poly_sheet, closed=True, fc=col, ec="#111111", lw=0.35, alpha=0.85, zorder=3))

    # Cotas Vista Superior
    cota_h(ax, p1(-PLACA_L / 2, SY)[0], p1(-SX, SY)[0], p1(-PLACA_L / 2, PLACA_W / 2)[1], p1(0, SY)[1], vy1 + 48.0, "15,0", fontsize=6.1)
    cota_h(ax, p1(-SX, SY)[0], p1(SX, SY)[0], p1(0, SY)[1], p1(0, SY)[1], vy1 + 48.0, "150,0 (Furos Placa Fenolite)")
    cota_h(ax, p1(-CX, CY)[0], p1(CX, CY)[0], p1(0, CY)[1], p1(0, CY)[1], vy1 + 55.5, "182,0 (Parafusos Tampa M3)")
    cota_h(ax, p1(-C_EXT / 2, L_EXT / 2)[0], p1(C_EXT / 2, L_EXT / 2)[0],
           p1(0, L_EXT / 2)[1], p1(0, L_EXT / 2)[1], vy1 + 63.0, "196,0 (Comprimento Externo)")

    cota_h(ax, p1(USB_X, -L_EXT / 2)[0], p1(C_EXT / 2, -L_EXT / 2)[0],
           p1(USB_X, -L_EXT / 2)[1], p1(C_EXT / 2, -L_EXT / 2)[1], vy1 - 44.0, "40,5 (Centro USB)")
    cota_h(ax, p1(-OX, -OY_HOLE)[0], p1(OX, -OY_HOLE)[0], p1(0, -62.5)[1], p1(0, -62.5)[1], vy1 - 51.5, "98,0 (Entre-centros Orelhas)")
    cota_h(ax, p1(-C_INT / 2, -L_INT / 2)[0], p1(C_INT / 2, -L_INT / 2)[0],
           p1(0, -L_INT / 2)[1], p1(0, -L_INT / 2)[1], vy1 - 59.0, "190,0 (Cavidade Interna)")

    cota_v(ax, p1(0, -L_INT / 2)[1], p1(0, L_INT / 2)[1],
           p1(-C_INT / 2, 0)[0], p1(-C_INT / 2, 0)[0], vx1 - 72.0, "87,0 (Cav. Int.)")
    cota_v(ax, p1(0, -L_EXT / 2)[1], p1(0, L_EXT / 2)[1],
           p1(-C_EXT / 2, 0)[0], p1(-C_EXT / 2, 0)[0], vx1 - 80.0, "93,0 (Corpo Ext.)")
    cota_v(ax, p1(0, -L_TOTAL_ORELHAS / 2)[1], p1(0, L_TOTAL_ORELHAS / 2)[1],
           p1(-OX, -62.5)[0], p1(-OX, 62.5)[0], vx1 - 88.0, "125,0 (Larg. c/ Orelhas)")

    cota_v(ax, p1(0, -SY)[1], p1(0, SY)[1],
           p1(SX, -SY)[0], p1(SX, SY)[0], vx1 + 72.0, "55,0 (Standoffs)")
    cota_v(ax, p1(0, -CY)[1], p1(0, CY)[1],
           p1(CX, -CY)[0], p1(CX, CY)[0], vx1 + 80.0, "79,0 (Cantos M3)")
    cota_v(ax, p1(0, -OY_HOLE)[1], p1(0, OY_HOLE)[1],
           p1(OX, -OY_HOLE)[0], p1(OX, OY_HOLE)[0], vx1 + 88.0, "109,0 (Orelhas M4)")

    callout(ax, p1(-SX, SY), (vx1 - 35.0, vy1 + 18.0), "4× Standoffs Ø8,0 / furo Ø2,6\n150 × 55 mm (a 15 mm da borda)", ha="left")
    callout(ax, p1(CX, CY), (vx1 + 18.0, vy1 + 19.0), "4× M3 Ø3,4 + Reb. Ø6,5 × 3,0", ha="left")
    callout(ax, p1(-OX, -OY_HOLE), (vx1 - 39.0, vy1 - 36.5), "4× Orelha 24×16×7 mm\nFuro Ø4,6 (M4) + Reb. Ø9,0×3,5", ha="right")

    # ==================== 2. VISTA LATERAL DIREITA (ESP32 USB) ====================
    vx2, vy2_bot = 132.0, 48.0
    ax.text(vx2, 102.0, "VISTA LATERAL DIREITA — FACE DO ESP32 USB (ALINHADA EM 1º DIEDRO)",
            fontsize=8.0, fontweight="bold", ha="center", va="center", color="#111111")

    def p2(x, z):
        return vx2 + x * k, vy2_bot + z * k

    ax.add_patch(patches.Rectangle(p2(-C_EXT / 2, 0.0), C_EXT * k, H_BASE * k, fc="#eef1f5", ec="#111111", lw=1.0, zorder=2))
    ax.add_patch(patches.Rectangle(p2(-C_EXT / 2, H_BASE), C_EXT * k, H_TAMPA * k, fc="#f9fafc", ec="#111111", lw=1.0, zorder=2))
    ax.plot([p2(-C_EXT / 2, H_TOTAL - 2.5)[0], p2(C_EXT / 2, H_TOTAL - 2.5)[0]],
            [p2(-C_EXT / 2, H_TOTAL - 2.5)[1], p2(C_EXT / 2, H_TOTAL - 2.5)[1]], color="#666666", lw=0.55, zorder=3)
    ax.add_patch(patches.Rectangle(p2(-37.5, H_TOTAL), 75.0 * k, H_LOGO * k, fc="#2e7d32", ec="#111111", lw=0.7, zorder=3))

    for ox in (-OX, OX):
        ax.add_patch(patches.Rectangle(p2(ox - 12.0, 0.0), 24.0 * k, 7.0 * k, fc="#dfe5ec", ec="#111111", lw=0.85, zorder=3))
        ax.plot([p2(ox, 0)[0], p2(ox, 7)[0]], [p2(ox, 0)[1], p2(ox, 7)[1]], ls="-.", lw=0.45, color="#666666", zorder=4)

    # Janela USB DEITADA (14 x 9 mm em X=57,5, Z=22 = 13mm acima da base da fenolite)
    ax.add_patch(patches.Rectangle(
        p2(USB_X - USB_W / 2, USB_Z_CENTER - USB_H / 2), USB_W * k, USB_H * k,
        fc="#fff8e1", ec="#b71c1c", lw=1.1, zorder=4
    ))
    ax.plot([p2(USB_X, 15)[0], p2(USB_X, 29)[0]], [p2(USB_X, 15)[1], p2(USB_X, 29)[1]], ls="-.", lw=0.45, color="#b71c1c", zorder=5)
    # Linha de centro do furo próximo da placa (X = +75,0 mm)
    ax.plot([p2(SX, 3.0)[0], p2(SX, 26.0)[0]], [p2(SX, 3.0)[1], p2(SX, 26.0)[1]], ls="-.", lw=0.5, color="#1565c0", zorder=4)

    # Cotas Vista Lateral Direita
    cota_h(ax, p2(USB_X - USB_W / 2, 0)[0], p2(USB_X + USB_W / 2, 0)[0],
           p2(0, USB_Z_CENTER + USB_H / 2)[1], p2(0, USB_Z_CENTER + USB_H / 2)[1], vy2_bot + H_TOTAL * k + 8.5, "14,0 (USB)", color="#b71c1c")
    cota_h(ax, p2(USB_X, 0)[0], p2(SX, 0)[0],
           p2(USB_X, 29.0)[1], p2(SX, 26.0)[1], vy2_bot + H_TOTAL * k + 17.5, "17,5 (Furo → USB)", color="#1565c0", fontsize=6.4)
    cota_h(ax, p2(-C_EXT / 2, 0)[0], p2(USB_X, 0)[0],
           p2(0, 0)[1], p2(0, 0)[1], vy2_bot - 9.0, "155,5 (Frente → Centro USB)")
    cota_h(ax, p2(USB_X, 0)[0], p2(C_EXT / 2, 0)[0],
           p2(0, 0)[1], p2(0, 0)[1], vy2_bot - 9.0, "40,5")
    cota_h(ax, p2(-OX - 12, 0)[0], p2(-OX + 12, 0)[0],
           p2(0, 0)[1], p2(0, 0)[1], vy2_bot - 17.5, "24,0 (Orelha)")

    cota_v(ax, p2(0, 0)[1], p2(0, H_BASE)[1], p2(-C_EXT / 2, 0)[0], p2(-C_EXT / 2, H_BASE)[0], vx2 - 73.0, "20,0 (Base)", fontsize=6.2)
    cota_v(ax, p2(0, H_BASE)[1], p2(0, H_TOTAL)[1], p2(-C_EXT / 2, H_BASE)[0], p2(-C_EXT / 2, H_TOTAL)[0], vx2 - 73.0, "16,0 (Tampa)", fontsize=6.2, outside_arrows=True)
    cota_v(ax, p2(0, 0)[1], p2(0, H_TOTAL)[1], p2(-C_EXT / 2, 0)[0], p2(-C_EXT / 2, H_TOTAL)[0], vx2 - 83.0, "36,0 (Corpo)")
    cota_v(ax, p2(0, USB_Z_CENTER - USB_H / 2)[1], p2(0, USB_Z_CENTER + USB_H / 2)[1],
           p2(C_EXT / 2, 0)[0], p2(C_EXT / 2, 0)[0], vx2 + 73.0, "9,0 (USB)", color="#b71c1c", outside_arrows=True)
    cota_v(ax, p2(0, 0)[1], p2(0, H_TOTAL + H_LOGO)[1],
           p2(37.5, H_TOTAL + H_LOGO)[0], p2(C_EXT / 2, 0)[0], vx2 + 84.0, "37,8 (c/ Logo)")

    callout(ax, p2(USB_X - USB_W / 2, USB_Z_CENTER - USB_H / 2), (vx2 + 12.0, vy2_bot + 7.5),
            "Janela ESP32 USB (14,0 × 9,0 mm)\n17,5 mm do furo (13 mm até borda USB)", ha="right", color="#b71c1c")

    # ==================== 3. VISTA FRONTAL (CONECTOR RETANGULAR DEITADO 26x12) ====================
    vx3, vy3_bot = 326.0, 210.0
    ax.text(vx3, 268.0, "VISTA FRONTAL — CONECTOR RETANGULAR DEITADO (26 × 12 mm + 1 mm FOLGA)",
            fontsize=7.7, fontweight="bold", ha="center", va="center", color="#111111")

    def p3(y, z):
        # Olhando de frente (-X -> +X): +Y fica à esquerda e -Y (lado ESP32) à direita
        return vx3 - y * k, vy3_bot + z * k

    ax.add_patch(patches.Rectangle(p3(L_EXT / 2, 0.0), L_EXT * k, H_BASE * k, fc="#eef1f5", ec="#111111", lw=1.0, zorder=2))
    ax.add_patch(patches.Rectangle(p3(L_EXT / 2, H_BASE), L_EXT * k, H_TAMPA * k, fc="#f9fafc", ec="#111111", lw=1.0, zorder=2))
    ax.plot([p3(L_EXT / 2, H_TOTAL - 2.5)[0], p3(-L_EXT / 2, H_TOTAL - 2.5)[0]],
            [p3(L_EXT / 2, H_TOTAL - 2.5)[1], p3(-L_EXT / 2, H_TOTAL - 2.5)[1]], color="#666666", lw=0.55, zorder=3)
    ax.add_patch(patches.Rectangle(p3(L_TOTAL_ORELHAS / 2, 0.0), 16.0 * k, 7.0 * k, fc="#dfe5ec", ec="#111111", lw=0.9, zorder=2))
    ax.add_patch(patches.Rectangle(p3(-L_EXT / 2, 0.0), 16.0 * k, 7.0 * k, fc="#dfe5ec", ec="#111111", lw=0.9, zorder=2))
    ax.add_patch(patches.Rectangle(p3(11.0, H_TOTAL), 22.0 * k, H_LOGO * k, fc="#2e7d32", ec="#111111", lw=0.7, zorder=3))

    # Janela Conector RETANGULAR DEITADA (27,0 x 13,0 mm em Z = 10,0 a 23,0 mm)
    ax.add_patch(patches.Rectangle(
        p3(ISO_W / 2.0, ISO_Z_BOT), ISO_W * k, ISO_H * k,
        fc="#fff8e1", ec="#b71c1c", lw=1.15, zorder=4
    ))
    ax.plot([vx3, vx3], [vy3_bot - 2.0, vy3_bot + H_TOTAL * k + 4.0], ls="-.", lw=0.45, color="#888888", zorder=5)

    # Cotas Vista Frontal
    cota_h(ax, p3(ISO_W / 2.0, 0)[0], p3(-ISO_W / 2.0, 0)[0],
           p3(0, H_TOTAL)[1], p3(0, H_TOTAL)[1], vy3_bot + H_TOTAL * k + 11.0, "27,0 (26 + 1 folga)", color="#b71c1c")
    cota_h(ax, p3(L_EXT / 2, 0)[0], p3(-L_EXT / 2, 0)[0],
           p3(0, 0)[1], p3(0, 0)[1], vy3_bot - 9.0, "93,0 (Corpo)")
    cota_h(ax, p3(L_TOTAL_ORELHAS / 2, 0)[0], p3(-L_TOTAL_ORELHAS / 2, 0)[0],
           p3(0, 0)[1], p3(0, 0)[1], vy3_bot - 17.5, "125,0 (Larg. Total c/ Orelhas)")

    cota_v(ax, p3(0, ISO_Z_BOT)[1], p3(0, ISO_Z_TOP)[1],
           p3(-L_EXT / 2, ISO_Z_BOT)[0], p3(-L_EXT / 2, ISO_Z_TOP)[0], vx3 + 49.0, "13,0 (12 + 1 folga)", color="#b71c1c", outside_arrows=True)
    cota_v(ax, p3(0, 0)[1], p3(0, H_TOTAL)[1],
           p3(-L_EXT / 2, 0)[0], p3(-L_EXT / 2, H_TOTAL)[0], vx3 + 60.0, "36,0 (Corpo)")
    cota_v(ax, p3(0, 0)[1], p3(0, 7.0)[1],
           p3(L_TOTAL_ORELHAS / 2, 0)[0], p3(L_TOTAL_ORELHAS / 2, 7.0)[0], vx3 - 49.0, "7,0", text_dx=-2.4, outside_arrows=True)
    cota_v(ax, p3(0, 0)[1], p3(0, H_BASE)[1],
           p3(L_EXT / 2, 0)[0], p3(L_EXT / 2, H_BASE)[0], vx3 - 59.0, "20,0 (Base)")

    # ==================== 4. CORTE TRANSVERSAL INTERNO A-A ====================
    vx4, vy4_bot = 326.0, 96.0
    ks = 0.80
    ax.text(vx4, 150.0, "CORTE TRANSVERSAL INTERNO — ESPESSURAS, ENCAIXE E PLACA (ESCALA ~1:1,25)",
            fontsize=7.6, fontweight="bold", ha="center", va="center", color="#111111")

    def p4(y, z):
        return vx4 + y * ks, vy4_bot + z * ks

    base_poly = np.array([
        p4(-46.5, 0), p4(46.5, 0), p4(46.5, 20), p4(43.7, 20), p4(43.7, 21.8), p4(42.7, 21.8), p4(42.7, 20),
        p4(43.5, 20), p4(43.5, 3), p4(-43.5, 3), p4(-43.5, 20), p4(-42.7, 20), p4(-42.7, 21.8), p4(-43.7, 21.8),
        p4(-43.7, 20), p4(-46.5, 20)
    ])
    ax.add_patch(patches.Polygon(base_poly, closed=True, fc="#cfd8dc", ec="#111111", lw=0.95, hatch="////", zorder=2))

    tampa_poly = np.array([
        p4(-46.5, 20), p4(-44.5, 20), p4(-44.5, 22.1), p4(-42.3, 22.1), p4(-42.3, 20), p4(-43.5, 20),
        p4(-43.5, 33), p4(43.5, 33), p4(43.5, 20), p4(42.3, 20), p4(42.3, 22.1), p4(44.5, 22.1), p4(44.5, 20),
        p4(46.5, 20), p4(46.5, 33.5), p4(44.0, 36), p4(-44.0, 36), p4(-46.5, 33.5)
    ])
    ax.add_patch(patches.Polygon(tampa_poly, closed=True, fc="#eceff1", ec="#111111", lw=0.95, hatch="\\\\\\\\", zorder=2))

    for sy in (-SY, SY):
        ax.add_patch(patches.Rectangle(p4(sy - 4.0, 3.0), 8.0 * ks, 6.0 * ks, fc="#b0bec5", ec="#111111", lw=0.8, zorder=3))
    # Placa fenolite 75mm (Y = -37.5..37.5, Z = 9..10.5) + ESP32 (+5mm saliente para -Y = -42.5, centrado em Z = 22.0)
    ax.add_patch(patches.Rectangle(p4(-37.5, 9.0), PLACA_W * ks, 1.5 * ks, fc="#8d6e63", ec="#3e2723", lw=0.8, zorder=4))
    ax.add_patch(patches.Rectangle(p4(-42.5, 17.5), 25.0 * ks, 9.0 * ks, fc="#263238", ec="#000000", lw=0.7, zorder=4))

    callout(ax, p4(-30.0, 22.0), (vx4 - 13.0 * ks, vy4_bot + 18.0 * ks),
            "ESP32 (+5 mm → -Y)\nCentro a 13 mm da placa", ha="left", color="#111111")
    ax.text(vx4 + 14.0 * ks, vy4_bot + 29.2 * ks, "VÃO INTERNO = 30,0 mm",
            fontsize=5.8, fontweight="bold", color="#1b5e20", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.20", fc="#f1f8e9", ec="#a5d6a7", lw=0.6), zorder=5)

    cota_v(ax, p4(0, 3.0)[1], p4(0, 33.0)[1], p4(-43.5, 3)[0], p4(-43.5, 33)[0], vx4 - 47.0, "30,0 (Alt. Int.)", color="#1b5e20")
    cota_v(ax, p4(0, 3.0)[1], p4(0, 9.0)[1], p4(SY, 3)[0], p4(SY, 9)[0], vx4 + 44.0, "6,0", outside_arrows=True)
    cota_h(ax, p4(-43.5, 0)[0], p4(43.5, 0)[0], p4(0, 0)[1], p4(0, 0)[1], vy4_bot - 9.0, "87,0 (Largura Interna)")
    cota_h(ax, p4(-37.5, 0)[0], p4(37.5, 0)[0], p4(0, 9)[1], p4(0, 9)[1], vy4_bot - 17.5, "75,0 (Placa Fenolite)", color="#4e342e")
    callout(ax, p4(45.0, 28.0), (vx4 + 44.0, vy4_bot + 25.0), "Paredes / Fundo / Teto\n3,0 mm (Lip 1,8 mm)", ha="left")

    pdf.savefig(fig)
    plt.close(fig)


def draw_page_2_isometric_and_bom(pdf: PdfPages) -> None:
    """Gera a Folha 2/2 com vistas isométricas, estimativa de filamento e lista de materiais."""
    fig, ax = setup_a3_sheet()
    draw_title_block(ax, "2 / 2", "VISTAS ISOMÉTRICAS, EXPLODIDA, FILAMENTO PLA E LISTA DE MATERIAIS")

    img_configs = [
        ("vista_isometrica_montada.png", "1. VISTA ISOMÉTRICA MONTADA (BASE + TAMPA + LOGO)", 28.0, 152.0, 188.0, 130.0),
        ("vista_isometrica_explodida.png", "2. VISTA ISOMÉTRICA EXPLODIDA (2 PEÇAS INDEPENDENTES)", 220.0, 152.0, 188.0, 130.0),
        ("vista_isometrica_base.png", "3. BASE INFERIOR — STANDOFFS INTERNOS E ORELHAS M4", 28.0, 14.0, 188.0, 132.0),
    ]

    for fname, title, bx, by, bw, bh in img_configs:
        ax.add_patch(patches.Rectangle((bx, by), bw, bh, fc="#ffffff", ec="#999999", lw=0.7, zorder=1))
        ax.add_patch(patches.Rectangle((bx, by + bh - 8.5), bw, 8.5, fc="#eceff1", ec="#999999", lw=0.7, zorder=2))
        ax.text(bx + bw / 2.0, by + bh - 4.25, title, fontsize=7.3, fontweight="bold",
                ha="center", va="center", color="#111111", zorder=3)

        arr = autocrop_png(os.path.join(OUT_DIR, fname), pad=16)
        h_px, w_px = arr.shape[:2]
        max_w_pts = (bw - 10.0) / 25.4 * 72.0
        max_h_pts = (bh - 15.0) / 25.4 * 72.0
        zoom = min(max_w_pts / w_px, max_h_pts / h_px)
        oi = OffsetImage(arr, zoom=zoom)
        ab = AnnotationBbox(oi, (bx + bw / 2.0, by + (bh - 8.5) / 2.0), frameon=False, zorder=2)
        ax.add_artist(ab)

    tx, ty, tw, th = 220.0, 62.0, 188.0, 84.0
    ax.add_patch(patches.Rectangle((tx, ty), tw, th, fc="#ffffff", ec="#111111", lw=0.9, zorder=2))
    ax.add_patch(patches.Rectangle((tx, ty + th - 8.5), tw, 8.5, fc="#1b5e20", ec="#111111", lw=0.9, zorder=3))
    ax.text(tx + tw / 2.0, ty + th - 4.25,
            "ESTIMATIVA DE FILAMENTO (PLA), FATIAMENTO E FIXADORES (BANCADA / EXIBIÇÃO)",
            fontsize=6.9, fontweight="bold", color="white", ha="center", va="center", zorder=4)

    info_text = (
        "VOLUME SÓLIDO CAD EXATO:   Base = 97,51 cm³   |   Tampa = 76,75 cm³   |   Total 100% Sólido = 174,26 cm³\n\n"
        "CONSUMO ESTIMADO EM PLA (ρ = 1,24 g/cm³ — Configuração leve p/ bancada: 2 paredes 0,8 mm, 15% Infill Gyroid):\n"
        "  • Base_Caixa_HIL.stl: ~65 g a 75 g  (imprimir com o fundo plano na mesa — SEM suportes)\n"
        "  • Tampa_Caixa_HIL.stl: ~52 g a 60 g + ~12 g de suporte árvore no teto  →  Total c/ logo embutido: ~130 g a 145 g\n"
        "  • Opção ZERO Suporte: imprimir Tampa_Sem_Logo_Invertida.stl de cabeça para baixo (~52 g) + Logo_IF_Separado.stl (~2 g)\n"
        "    em verde/vermelho e colar com cianoacrilato → Total mínimo: ~120 g a 132 g (~13% de um carretel de 1 kg).\n\n"
        "LISTA DE MATERIAIS E FIXADORES (BOM):\n"
        "  [1] 4× Parafuso M3 × 16 mm (cabeça Allen M3 — fecha a Tampa_Superior nos 4 cantos rebaixados)\n"
        "  [2] 4× Parafuso auto-atarraxante Ø2,9 × 8 mm ou M3 curto (fixa a fenolite 180 × 75 mm nos 4 standoffs de Ø2,6 mm)\n"
        "  [3] 4× Parafuso M4 + porca/arruela (fixa as 4 orelhas externas na bancada / painel de exibição)\n"
        "  [4] Dica de bocal/camada: bico 0,4 mm, altura de camada 0,20 mm, 4 camadas topo/fundo, brim opcional na Base."
    )
    ax.text(tx + 4.5, ty + th - 12.5, info_text, fontsize=6.4, color="#111111",
            ha="left", va="top", linespacing=1.45, zorder=4)

    pdf.savefig(fig)
    plt.close(fig)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with PdfPages(PDF_PATH) as pdf:
        draw_page_1_orthographic(pdf)
        draw_page_2_isometric_and_bom(pdf)

    doc = pymupdf.open(PDF_PATH)
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=180, alpha=False)
        preview_path = os.path.join(OUT_DIR, f"preview_pdf_pag{i}.png")
        pix.save(preview_path)
        print(f"Saved preview: {preview_path} ({pix.width}x{pix.height})")
    doc.close()
    print(f"[SUCESSO] Desenho técnico gerado em: {PDF_PATH} ({os.path.getsize(PDF_PATH)} bytes)")


if __name__ == "__main__":
    main()
