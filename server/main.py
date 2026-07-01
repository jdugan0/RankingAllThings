from fastapi import FastAPI, HTTPException
import sqlite3
import math
import random
import uuid
import os

import threading
vote_lock = threading.Lock()

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("THINGS_DB", os.path.join(HERE, "..", "data", "things.db"))

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

tokens = dict()

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
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

@app.get("/pair")
def pair():
    con = db()
    token = uuid.uuid4()
    row1 = con.execute(
        "SELECT id, label, descr, rd, rating, img FROM objects ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    sigma = 40
    t = random.gauss(row1["rating"], max(0, sigma - row1["rd"] / 3))
    row2 = con.execute(
        "SELECT id, label, descr, img FROM objects WHERE id != ? ORDER BY abs(rating - ?), RANDOM() LIMIT 1",
        (row1["id"], t)
    ).fetchone()
    tokens[token] = {row1["id"], row2["id"]}
    con.close()
    return {'pair': [dict(r) for r in [row1, row2]], 'token' : token}

@app.get("/leaderboard_rank")
def leaderboard():
    con = db()
    rows = con.execute("SELECT label, descr, rating FROM objects ORDER BY rating DESC").fetchall()
    con.close()
    return [dict(r) for r in rows]

from pydantic import BaseModel

class Vote(BaseModel):
    winner_id: int
    loser_id: int
    token: uuid.UUID
    
    
@app.post("/vote")
def vote(v : Vote):
    con = db()
    try:
        with vote_lock:
            valid = tokens.pop(v.token, None)        # consume on read
            if valid is None or v.winner_id not in valid or v.loser_id not in valid:
                raise HTTPException(400)
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
    return  {'status': 'ok'}

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

@app.get("/leaderboard")
def leaderboard():
    return FileResponse(os.path.join(HERE, "leaderboard.html"))

app.mount("/", StaticFiles(directory=HERE, html=True), name="static")