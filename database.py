import sqlite3

def init_db():
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            valor REAL,
            mes TEXT,
            usuario TEXT
        )
    """)
    conn.commit()
    conn.close()

def adicionar_gasto(nome, valor, mes, usuario):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gastos (nome, valor, mes, usuario) VALUES (?, ?, ?, ?)", (nome, valor, mes, usuario))
    conn.commit()
    conn.close()

def listar_gastos_por_usuario(usuario):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, valor, mes FROM gastos WHERE usuario = ?", (usuario,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def listar_gastos_por_mes(mes, usuario):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, valor, mes FROM gastos WHERE mes = ? AND usuario = ?", (mes, usuario))
    dados = cursor.fetchall()
    conn.close()
    return dados

def calcular_total_geral(usuario):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM gastos WHERE usuario = ?", (usuario,))
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total

def excluir_gasto(id):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gastos WHERE id = ?", (id,))
    conn.commit()
    conn.close()