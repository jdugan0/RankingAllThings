import sqlite3
import os
HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("THINGS_DB", os.path.join(HERE, "..", "data", "things.db"))

con = sqlite3.connect(DB_PATH)

con.execute("DELETE FROM objects WHERE id=")
con.commit()
con.close()