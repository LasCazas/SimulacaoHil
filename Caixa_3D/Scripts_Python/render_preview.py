import os
import cadquery as cq
import pymupdf


def svg_to_png(svg_path: str, png_path: str, scale: float = 1.5) -> None:
    """Rasteriza um SVG gerado pelo CadQuery para PNG via PyMuPDF."""
    doc = pymupdf.open(svg_path)
    page = doc[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
    pix.save(png_path)
    doc.close()


def render_views() -> None:
    caixa_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proj_dir_files = os.path.join(caixa_dir, "Arquivos_Projeto")
    out_dir = os.path.join(caixa_dir, "Imagens_e_PDF")
    os.makedirs(out_dir, exist_ok=True)

    conjunto = cq.importers.importStep(os.path.join(proj_dir_files, "Conjunto_Caixa_HIL_Montada.step"))
    explodida = cq.importers.importStep(os.path.join(proj_dir_files, "Conjunto_Caixa_HIL_Vista_Explodida.step"))
    base = cq.importers.importStep(os.path.join(proj_dir_files, "Base_Caixa_HIL.step"))

    # Direção (-X, -Y, +Z) olhando da frente-direita-cima para ver conector ISO frontal,
    # janela ESP32 na lateral DIREITA (-Y) e logo no topo (+Z).
    cam_front_right_top = (-1.2, -1.0, 0.85)

    views = [
        (conjunto, "vista_isometrica_montada", cam_front_right_top, (20, 20, 20)),
        (explodida, "vista_isometrica_explodida", cam_front_right_top, (20, 20, 20)),
        (base, "vista_isometrica_base", (-1.1, -1.0, 1.3), (0, 80, 160)),
    ]

    for shape, name, proj_dir, stroke_rgb in views:
        svg_path = os.path.join(out_dir, f"{name}.svg")
        png_path = os.path.join(out_dir, f"{name}.png")
        cq.exporters.export(
            shape,
            svg_path,
            opt={
                "projectionDir": proj_dir,
                "showHidden": False,
                "width": 1000,
                "height": 700,
                "strokeWidth": 0.9,
                "strokeColor": stroke_rgb,
                "hiddenColor": (180, 180, 180),
                "showAxes": False,
            },
        )
        svg_to_png(svg_path, png_path)
        print(f"Rendered {png_path}")


if __name__ == "__main__":
    render_views()
