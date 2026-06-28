from fastapi import FastAPI
import sqlite3
import math
app = FastAPI()

def glicko_update(old_rating, old_RD, op_rating, op_RD, s):
    q = math.log(10) / 400
    def g(RD):
        return 1 / (math.sqrt(1 + (3 * q * q * RD * RD) / (math.pi * math.pi)))
    E = 1 / (1 + 10**(-g(op_RD) * (old_rating - op_rating)/400))
    dsq = 1 / (q * q * g(op_RD)**2 * E * (1 - E))
    r_new = old_rating + q/(1/old_RD**2 + 1 / dsq )*g(op_RD) * (s - E)
    rd_new = math.sqrt(1 / (1 / old_RD**2 +  1/dsq))
    return (r_new, rd_new)

def db():
    con = sqlite3.connect("../data/things.db")
    con.row_factory = sqlite3.Row
    return con

@app.get("/pair")
def pair():
    rows = db().execute(
        "SELECT id, label, descr FROM objects ORDER BY RANDOM() LIMIT 2"
    ).fetchall()
    return [dict(r) for r in rows]

from pydantic import BaseModel

class Vote(BaseModel):
    winner_id: int
    loser_id: int
    
    
@app.post("/vote")
def vote(v : Vote):
    con = db()
    try:
        winner = con.execute("SELECT rating, rd FROM objects WHERE id=?", (v.winner_id,)).fetchone()
        loser = con.execute("SELECT rating, rd FROM objects WHERE id=?", (v.loser_id,)).fetchone()
        winner_new = glicko_update(winner["rating"], winner["rd"], loser["rating"], loser["rd"], 1)
        loser_new = glicko_update(loser["rating"], loser["rd"], winner["rating"], winner["rd"], 0)
        con.execute("UPDATE objects SET rating=?, rd=? WHERE id=?", (winner_new[0], winner_new[1], v.winner_id))
        con.execute("UPDATE objects SET rating=?, rd=? WHERE id=?", (loser_new[0], loser_new[1], v.loser_id))
        con.execute("INSERT INTO votes (winner_id, loser_id) VALUES (?, ?)", (v.winner_id, v.loser_id))
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()