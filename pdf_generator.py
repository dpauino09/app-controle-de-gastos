from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import sqlite3
import matplotlib.pyplot as plt

def gerar_pdf(mes, usuario):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome, valor FROM gastos WHERE mes = ? AND usuario = ?", (mes, usuario))
    dados = cursor.fetchall()
    conn.close()

    filename = f"relatorio_{usuario}_{mes}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica", 14)
    c.drawString(50, 800, f"Relatório de Gastos - {mes} ({usuario})")
    y = 760
    total = 0

    for nome, valor in dados:
        c.drawString(50, y, f"{nome}: R$ {valor:.2f}")
        y -= 20
        total += valor

    c.drawString(50, y - 20, f"Total: R$ {total:.2f}")
    c.save()
    return filename