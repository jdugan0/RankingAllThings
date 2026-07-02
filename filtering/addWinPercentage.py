import sqlite3, pandas as pd, re

con = sqlite3.connect("data/things.db")

con.execute("ALTER TABLE objects ADD wins INT DEFAULT 0")
con.execute("ALTER TABLE objects ADD total INT DEFAULT 0")

games = con.execute("SELECT winner_id, loser_id FROM votes").fetchall()
for row in games:
    con.execute("UPDATE objects SET total = total + 1 WHERE id = ? OR id = ?", (int(row[0]), int(row[1])))
    con.execute("UPDATE objects SET wins = wins + 1 WHERE id = ?", (int(row[0]),))
con.commit()
con.close()