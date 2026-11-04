# -*- coding: utf-8 -*-
"""Genera el PDF del informe por actividades a partir del Markdown de la carpeta.

Uso:
    python generar_informe_actividades.py [archivo.md] [salida.pdf]

Sin argumentos toma el primer `Informe_TP*_Actividades.md` de esta carpeta y
escribe el PDF con el mismo nombre. Requiere reportlab.
"""

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, Preformatted, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

RAIZ = Path(__file__).resolve().parent
FUENTES = {
    "Arial": r"C:\Windows\Fonts\arial.ttf",
    "Arial-Bold": r"C:\Windows\Fonts\arialbd.ttf",
    "Arial-Italic": r"C:\Windows\Fonts\ariali.ttf",
    "Consola": r"C:\Windows\Fonts\consola.ttf",
}
for nombre, ruta in FUENTES.items():
    if Path(ruta).exists():
        pdfmetrics.registerFont(TTFont(nombre, ruta))

BASE = "Arial" if "Arial" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
BOLD = "Arial-Bold" if "Arial-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
ITAL = "Arial-Italic" if "Arial-Italic" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Oblique"
MONO = "Consola" if "Consola" in pdfmetrics.getRegisteredFontNames() else "Courier"

AZUL = colors.HexColor("#1F3A5F")
GRIS = colors.HexColor("#5B6770")
GRIS_CLARO = colors.HexColor("#EDF1F5")
BORDE = colors.HexColor("#B8C2CC")

ss = getSampleStyleSheet()
st_h1 = ParagraphStyle("h1", parent=ss["Title"], fontName=BOLD, fontSize=17,
                       leading=21, textColor=AZUL, spaceAfter=4)
st_h2 = ParagraphStyle("h2", parent=ss["Heading1"], fontName=BOLD, fontSize=12,
                       leading=14.5, textColor=AZUL, spaceBefore=10, spaceAfter=4,
                       keepWithNext=1)
st_h3 = ParagraphStyle("h3", parent=ss["Heading2"], fontName=BOLD, fontSize=10,
                       leading=12.5, textColor=AZUL, spaceBefore=7, spaceAfter=3,
                       keepWithNext=1)
st_body = ParagraphStyle("body", parent=ss["Normal"], fontName=BASE, fontSize=9,
                         leading=12, alignment=TA_JUSTIFY, spaceAfter=3)
st_meta = ParagraphStyle("meta", parent=st_body, alignment=TA_CENTER,
                         textColor=GRIS, fontSize=8.4, leading=10.8, spaceAfter=1)
st_li = ParagraphStyle("li", parent=st_body, leftIndent=12, bulletIndent=3,
                       spaceAfter=1.8)
st_quote = ParagraphStyle("quote", parent=st_body, fontName=ITAL, textColor=GRIS,
                          leftIndent=12, spaceAfter=4)
st_code = ParagraphStyle("code", parent=ss["Code"], fontName=MONO, fontSize=6.6,
                         leading=8, textColor=colors.HexColor("#1B1B1B"))
st_cell = ParagraphStyle("cell", parent=ss["Normal"], fontName=BASE, fontSize=7.6,
                         leading=9.4)
st_cell_b = ParagraphStyle("cellb", parent=st_cell, fontName=BOLD,
                           textColor=colors.white)

ANCHO = A4[0] - 3.4 * cm


def inline(texto):
    texto = escape(texto)
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"`(.+?)`", r'<font name="%s" size="7.6">\1</font>' % MONO, texto)
    texto = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", texto)
    return texto


def P(texto, estilo=st_body):
    return Paragraph(inline(texto), estilo)


def fila_tabla(celdas, encabezado=False):
    estilo = st_cell_b if encabezado else st_cell
    return [Paragraph(inline(c.strip()), estilo) for c in celdas]


def anchos_columnas(n):
    if n == 1:
        return [ANCHO]
    if n == 2:
        return [ANCHO * 0.30, ANCHO * 0.70]
    if n == 3:
        return [ANCHO * 0.20, ANCHO * 0.40, ANCHO * 0.40]
    if n == 4:
        return [ANCHO * n_i for n_i in (0.16, 0.28, 0.28, 0.28)]
    base = ANCHO / n
    return [base] * n


def tabla_md(filas):
    datos = []
    for i, fila in enumerate(filas):
        datos.append(fila_tabla(fila, encabezado=(i == 0)))
    n = max(len(f) for f in filas)
    for fila in datos:
        while len(fila) < n:
            fila.append(Paragraph("", st_cell))
    t = Table(datos, colWidths=anchos_columnas(n), repeatRows=1)
    est = [
        ("GRID", (0, 0), (-1, -1), 0.35, BORDE),
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]
    for i in range(1, len(datos)):
        if i % 2 == 0:
            est.append(("BACKGROUND", (0, i), (-1, i), GRIS_CLARO))
    t.setStyle(TableStyle(est))
    return t


def caja_codigo(lineas):
    texto = "\n".join(lineas).rstrip("\n")
    caja = Table([[Preformatted(texto, st_code)]], colWidths=[ANCHO])
    caja.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6F8FA")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D2DB")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return caja


def es_especial(linea):
    s = linea.strip()
    return (
        not s
        or s.startswith("#")
        or s.startswith("```")
        or s.startswith("|")
        or s.startswith("> ")
        or s.startswith("- ")
        or s.startswith("* ")
        or re.match(r"^\d+\.\s", s)
        or s in ("---", "***", "___")
    )


def convertir(md):
    lineas = md.splitlines()
    story = []
    titulo = "Informe de actividades"
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        s = linea.strip()

        if not s:
            i += 1
            continue

        if s.startswith("```"):
            i += 1
            bloque = []
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                bloque.append(lineas[i])
                i += 1
            i += 1
            story.append(caja_codigo(bloque))
            story.append(Spacer(1, 4))
            continue

        if s.startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                crudo = lineas[i].strip().strip("|")
                celdas = [c.strip() for c in crudo.split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in celdas):
                    filas.append(celdas)
                i += 1
            if filas:
                story.append(tabla_md(filas))
                story.append(Spacer(1, 5))
            continue

        if s.startswith("# "):
            titulo = s[2:].strip()
            story.append(Paragraph(inline(titulo), st_h1))
            i += 1
            continue

        if s.startswith("## "):
            story.append(Paragraph(inline(s[3:].strip()), st_h2))
            i += 1
            continue

        if s.startswith("### "):
            story.append(Paragraph(inline(s[4:].strip()), st_h3))
            i += 1
            continue

        if s in ("---", "***", "___"):
            story.append(HRFlowable(width="100%", thickness=0.6, color=BORDE,
                                    spaceBefore=4, spaceAfter=5))
            i += 1
            continue

        if s.startswith("> "):
            bloque = []
            while i < len(lineas) and lineas[i].strip().startswith("> "):
                bloque.append(lineas[i].strip()[2:].strip())
                i += 1
            story.append(P(" ".join(bloque), st_quote))
            continue

        if s.startswith("- ") or s.startswith("* "):
            while i < len(lineas) and (
                lineas[i].strip().startswith("- ") or lineas[i].strip().startswith("* ")
            ):
                texto = lineas[i].strip()[2:].strip()
                story.append(Paragraph(inline(texto), st_li, bulletText="•"))
                i += 1
            story.append(Spacer(1, 2))
            continue

        if re.match(r"^\d+\.\s", s):
            while i < len(lineas):
                m = re.match(r"^(\d+)\.\s+(.*)$", lineas[i].strip())
                if not m:
                    break
                story.append(Paragraph(inline(m.group(2)), st_li,
                                       bulletText=m.group(1) + "."))
                i += 1
            story.append(Spacer(1, 2))
            continue

        bloque = []
        while i < len(lineas) and not es_especial(lineas[i]):
            bloque.append(lineas[i].strip())
            i += 1
        if bloque:
            story.append(P(" ".join(bloque)))

    return titulo, story


def encabezado_pie(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(AZUL)
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, A4[1] - 1.35 * cm,
                A4[0] - doc.rightMargin, A4[1] - 1.35 * cm)
    canvas.setFont(BASE, 7.2)
    canvas.setFillColor(GRIS)
    canvas.drawString(doc.leftMargin, A4[1] - 1.05 * cm, doc.titulo_doc)
    canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 1.05 * cm,
                           "Food Store · Base de Datos II")
    canvas.drawCentredString(A4[0] / 2, 1.0 * cm, "Página %d" % doc.page)
    canvas.restoreState()


def main():
    if len(sys.argv) > 1:
        md_path = Path(sys.argv[1]).resolve()
    else:
        candidatos = sorted(RAIZ.glob("Informe_TP*_Actividades.md"))
        if not candidatos:
            raise SystemExit("No se encontró un archivo Informe_TP*_Actividades.md")
        md_path = candidatos[0]

    pdf_path = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else md_path.with_suffix(".pdf")
    titulo, story = convertir(md_path.read_text(encoding="utf-8"))

    doc = SimpleDocTemplate(
        str(pdf_path), pagesize=A4,
        leftMargin=1.7 * cm, rightMargin=1.7 * cm,
        topMargin=1.8 * cm, bottomMargin=1.6 * cm,
        title=titulo, author="Food Store - Base de Datos II",
    )
    doc.titulo_doc = titulo
    doc.build(story, onFirstPage=encabezado_pie, onLaterPages=encabezado_pie)
    print("PDF generado:", pdf_path)


if __name__ == "__main__":
    main()
