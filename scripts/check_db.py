"""Verifica o banco de dados"""
import sqlite3

conn = sqlite3.connect('instance/fonogramas.db')
c = conn.cursor()

print("=== Fonogramas por user_id ===")
c.execute('SELECT user_id, COUNT(*) FROM fonogramas GROUP BY user_id')
for r in c.fetchall():
    print(f"user_id={r[0]}: {r[1]} fonogramas")

print("\n=== Usuários ===")
c.execute('SELECT id, email FROM users')
for r in c.fetchall():
    print(f"id={r[0]}: {r[1]}")

print("\n=== Primeiros 3 ISRCs ===")
c.execute('SELECT isrc, titulo FROM fonogramas LIMIT 3')
for r in c.fetchall():
    print(f"ISRC: {r[0]}, Titulo: {r[1]}")

conn.close()
