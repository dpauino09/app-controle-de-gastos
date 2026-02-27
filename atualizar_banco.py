import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "gastos.db")

usuario_padrao = input("Digite o nome do usuário padrão para atualizar os registros antigos: ")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(gastos)")
colunas = [coluna[1] for coluna in cursor.fetchall()]

if "usuario" not in colunas:
    print("Adicionando coluna 'usuario' ao banco de dados...")
    cursor.execute("ALTER TABLE gastos ADD COLUMN usuario TEXT")
    conn.commit()
else:
    print("Coluna 'usuario' já existe.")

print(f"Atualizando registros antigos com usuário padrão: {usuario_padrao}")
cursor.execute("UPDATE gastos SET usuario = ? WHERE usuario IS NULL OR usuario = ''", (usuario_padrao,))
conn.commit()
conn.close()
print("✅ Banco de dados atualizado com sucesso.")