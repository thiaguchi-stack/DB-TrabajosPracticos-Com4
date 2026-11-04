# -*- coding: utf-8 -*-
"""Genera TP1_Diagrama_ER.pdf: diagrama Crow's Foot del esquema Food Store.

Uso: python generar_diagrama_er.py
Requiere reportlab.
"""

import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "TP1_Diagrama_ER.pdf"

FUENTES = {
    "Arial": r"C:\Windows\Fonts\arial.ttf",
    "Arial-Bold": r"C:\Windows\Fonts\arialbd.ttf",
}
for nombre, ruta in FUENTES.items():
    if Path(ruta).exists():
        pdfmetrics.registerFont(TTFont(nombre, ruta))
BASE = "Arial" if "Arial" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
BOLD = "Arial-Bold" if "Arial-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"

AZUL = colors.HexColor("#1F3A5F")
AZUL_CLARO = colors.HexColor("#E8EEF6")
GRIS = colors.HexColor("#5B6770")
BORDE = colors.HexColor("#8FA0B3")
VERDE = colors.HexColor("#1E6B45")
ROJO = colors.HexColor("#9B2C2C")

PAGE_W, PAGE_H = landscape(A4)

ENTIDADES = {
    "categoria": {
        "x": 40, "y": 365, "w": 160,
        "campos": [
            ("id", "bigint", "PK"),
            ("nombre", "varchar", "UK"),
            ("activo", "boolean", ""),
            ("created_at", "timestamptz", ""),
        ],
    },
    "producto": {
        "x": 240, "y": 340, "w": 175,
        "campos": [
            ("id", "bigint", "PK"),
            ("categoria_id", "bigint", "FK"),
            ("nombre", "varchar", ""),
            ("descripcion", "text", ""),
            ("precio", "numeric", ""),
            ("stock", "integer", ""),
            ("activo", "boolean", ""),
            ("created_at", "timestamptz", ""),
        ],
    },
    "cliente": {
        "x": 650, "y": 350, "w": 160,
        "campos": [
            ("id", "bigint", "PK"),
            ("nombre", "varchar", ""),
            ("apellido", "varchar", ""),
            ("email", "varchar", "UK"),
            ("telefono", "varchar", ""),
            ("activo", "boolean", ""),
            ("created_at", "timestamptz", ""),
        ],
    },
    "pedido": {
        "x": 650, "y": 180, "w": 160,
        "campos": [
            ("id", "bigint", "PK"),
            ("cliente_id", "bigint", "FK"),
            ("fecha", "timestamptz", ""),
            ("forma_pago", "enum", ""),
            ("created_at", "timestamptz", ""),
        ],
    },
    "linea_pedido": {
        "x": 410, "y": 170, "w": 190,
        "campos": [
            ("pedido_id", "bigint", "PK/FK"),
            ("producto_id", "bigint", "PK/FK"),
            ("cantidad", "integer", ""),
            ("precio_unitario", "numeric", ""),
        ],
    },
}


def altura(entidad):
    return 20 + len(entidad["campos"]) * 13 + 4


def dibujar_entidad(c, nombre, e):
    x, y, w = e["x"], e["y"], e["w"]
    h = altura(e)
    c.setFillColor(colors.white)
    c.setStrokeColor(BORDE)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)

    c.setFillColor(AZUL)
    c.roundRect(x, y + h - 20, w, 20, 4, fill=1, stroke=0)
    c.rect(x, y + h - 20, w, 8, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(BOLD, 9.2)
    c.drawString(x + 7, y + h - 14, nombre)

    c.setFont(BASE, 6.9)
    for i, (campo, tipo, clave) in enumerate(e["campos"]):
        fila_y = y + h - 33 - i * 13
        if clave:
            c.setFillColor(VERDE if "PK" in clave else ROJO)
            c.setFont(BOLD, 6.6)
            c.drawString(x + 6, fila_y, clave)
        c.setFillColor(colors.black)
        c.setFont(BOLD if "PK" in clave else BASE, 7.0)
        c.drawString(x + 36, fila_y, campo)
        c.setFillColor(GRIS)
        c.setFont(BASE, 6.4)
        c.drawRightString(x + w - 6, fila_y, tipo)

def centro_borde(e, lado):
    x, y, w = e["x"], e["y"], e["w"]
    h = altura(e)
    if lado == "izq":
        return x, y + h / 2
    if lado == "der":
        return x + w, y + h / 2
    if lado == "arr":
        return x + w / 2, y + h
    return x + w / 2, y


def pata_gallo(c, px, py, hacia, escala=5):
    """Dibuja la pata de gallo en el extremo hijo."""
    if hacia in ("izq", "der"):
        signo = -1 if hacia == "izq" else 1
        c.line(px, py, px + signo * escala, py + escala)
        c.line(px, py, px + signo * escala, py)
        c.line(px, py, px + signo * escala, py - escala)
    else:
        signo = -1 if hacia == "arr" else 1
        c.line(px, py, px + escala, py + signo * escala)
        c.line(px, py, px, py + signo * escala)
        c.line(px, py, px - escala, py + signo * escala)


def etiqueta(c, x, y, texto, color=AZUL):
    c.setFillColor(color)
    c.setFont(BOLD, 7.2)
    c.drawCentredString(x, y, texto)


def conectar(c, padre, lado_padre, hijo, lado_hijo, uno, n):
    (x1, y1) = centro_borde(ENTIDADES[padre], lado_padre)
    (x2, y2) = centro_borde(ENTIDADES[hijo], lado_hijo)
    c.setStrokeColor(AZUL)
    c.setLineWidth(1.0)
    c.line(x1, y1, x2, y2)
    pata_gallo(c, x2, y2, lado_hijo)
    dx, dy = x2 - x1, y2 - y1
    largo = math.hypot(dx, dy) or 1
    ox, oy = -dy / largo * 7, dx / largo * 7
    etiqueta(c, x1 + dx * 0.15 + ox, y1 + dy * 0.15 + oy, uno)
    etiqueta(c, x1 + dx * 0.85 + ox, y1 + dy * 0.85 + oy, n)


def main():
    c = canvas.Canvas(str(SALIDA), pagesize=landscape(A4))
    c.setTitle("Food Store - Diagrama Entidad-Relacion (Crow's Foot)")
    c.setAuthor("Food Store - Base de Datos II")

    c.setFillColor(AZUL)
    c.setFont(BOLD, 15)
    c.drawString(1.4 * cm, PAGE_H - 1.4 * cm,
                 "Food Store — Diagrama Entidad-Relación")
    c.setFillColor(GRIS)
    c.setFont(BASE, 8.4)
    c.drawString(1.4 * cm, PAGE_H - 1.9 * cm,
                 "Notación: Pata de Gallo (Crow's Foot) · TP N.º 1 · Base de Datos I")
    c.setStrokeColor(AZUL)
    c.setLineWidth(0.6)
    c.line(1.4 * cm, PAGE_H - 2.2 * cm, PAGE_W - 1.4 * cm, PAGE_H - 2.2 * cm)

    for nombre, e in ENTIDADES.items():
        dibujar_entidad(c, nombre, e)

    conectar(c, "categoria", "der", "producto", "izq", "1", "N")
    conectar(c, "producto", "aba", "linea_pedido", "arr", "1", "N")
    conectar(c, "pedido", "izq", "linea_pedido", "der", "1", "N")
    conectar(c, "cliente", "aba", "pedido", "arr", "1", "N")

    # Leyenda
    lx, ly = 1.4 * cm, 2.9 * cm
    c.setFillColor(AZUL_CLARO)
    c.setStrokeColor(BORDE)
    c.roundRect(lx, ly, 320, 42, 3, fill=1, stroke=1)
    c.setFillColor(AZUL)
    c.setFont(BOLD, 7.8)
    c.drawString(lx + 8, ly + 31, "Leyenda")
    c.setFont(BASE, 7.0)
    c.setFillColor(VERDE)
    c.drawString(lx + 8, ly + 20, "PK")
    c.setFillColor(colors.black)
    c.drawString(lx + 30, ly + 20, "clave primaria")
    c.setFillColor(ROJO)
    c.drawString(lx + 105, ly + 20, "FK")
    c.setFillColor(colors.black)
    c.drawString(lx + 127, ly + 20, "clave foránea")
    c.setFillColor(VERDE)
    c.drawString(lx + 205, ly + 20, "UK")
    c.setFillColor(colors.black)
    c.drawString(lx + 227, ly + 20, "clave candidata única")
    c.drawString(lx + 8, ly + 8, "1 / N: cardinalidad; la pata de gallo marca el lado muchos.")

    c.setFillColor(GRIS)
    c.setFont(BASE, 6.6)
    c.drawRightString(PAGE_W - 1.4 * cm, 1.1 * cm,
                      "Fuente: diagrama_er.dbml · generado con generar_diagrama_er.py")

    c.showPage()
    c.save()
    print("PDF generado:", SALIDA)


if __name__ == "__main__":
    main()
