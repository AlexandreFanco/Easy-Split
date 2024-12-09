import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Criar a tabela de usuários
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()
print("Banco de dados inicializado.")
