"""Shrink the local DB to a handful of random objects for testing.

Destructive: keeps KEEP random objects and clears votes + rate_limits.
The real DB is backed up. Targets the same DB file as main.py (THINGS_DB
env var, else ../data/things.db).
"""
import os, sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("THINGS_DB", os.path.join(HERE, "..", "data", "things.db"))

KEEP = 5

con = sqlite3.connect(DB_PATH)
before = con.execute("SELECT COUNT(*) FROM objects").fetchone()[0]

con.execute(
    "DELETE FROM objects WHERE id NOT IN "
    "(SELECT id FROM objects ORDER BY RANDOM() LIMIT ?)",
    (KEEP,),
)
con.execute("DELETE FROM votes")
con.execute("DELETE FROM rate_limits")
con.commit()

kept = con.execute("SELECT id, label, rating, sfw FROM objects").fetchall()
con.close()

print(f"objects: {before} -> {len(kept)} (votes and rate_limits cleared)")
for row in kept:
    print(" ", row)