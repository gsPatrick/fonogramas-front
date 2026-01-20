"""Script para atualizar user_id dos fonogramas"""
import sqlite3

conn = sqlite3.connect('instance/fonogramas.db')
c = conn.cursor()

# Atualizar fonogramas sem user_id
c.execute('UPDATE fonogramas SET user_id = 2 WHERE user_id IS NULL')
print(f'Atualizados: {c.rowcount}')

conn.commit()

# Verificar total
c.execute('SELECT COUNT(*) FROM fonogramas WHERE user_id = 2')
print(f'Total fonogramas com user_id=2: {c.fetchone()[0]}')

conn.close()
print('Concluido!')
