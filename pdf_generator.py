from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from database import BASE_DIR, listar_gastos_por_mes

def gerar_pdf(mes, usuario):
    gastos = listar_gastos_por_mes(mes, usuario)
    dados = [(g[1], g[2]) for g in gastos]


    os.makedirs(os.path.join(BASE_DIR, "pdfs"), exist_ok=True)
    nome_arquivo = f"relatorio_{usuario}_{mes}.pdf".replace(" ", "_")
    filename = os.path.join(BASE_DIR, "pdfs", nome_arquivo)
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