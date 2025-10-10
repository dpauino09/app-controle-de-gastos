import sqlite3

# Conecta ao banco de dados existente
conn = sqlite3.connect("gastos.db")
cursor = conn.cursor()

# Verifica se a coluna 'usuario' já existe
cursor.execute("PRAGMA table_info(gastos)")
colunas = [coluna[1] for coluna in cursor.fetchall()]

# Adiciona a coluna 'usuario' se ela não existir
if "usuario" not in colunas:
    print("Adicionando coluna 'usuario' ao banco de dados...")
    cursor.execute("ALTER TABLE gastos ADD COLUMN usuario TEXT")
    conn.commit()
else:
    print("Coluna 'usuario' já existe.")

# Atualiza os registros antigos com um nome de usuário padrão
usuario_padrao = "Daniel"
print(f"Atualizando registros antigos com usuário padrão: {usuario_padrao}")
cursor.execute("UPDATE gastos SET usuario = ? WHERE usuario IS NULL OR usuario = ''", (usuario_padrao,))
conn.commit()

# Finaliza
conn.close()
print("✅ Banco de dados atualizado com sucesso.")