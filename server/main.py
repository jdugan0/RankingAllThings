from fastapi import FastAPI, HTTPException
import sqlite3
import math
import random
import uuid
import os
import base64
import hashlib

import threading
vote_lock = threading.Lock()

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("THINGS_DB", os.path.join(HERE, "..", "data", "things.db"))

def hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)  
    digest = hasher.digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8')[:12]

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

@app.get("/num_votes")
def num_votes():
    con = db()
    num = con.execute("SELECT COUNT(*) AS total_rows FROM votes").fetchone()
    return num["total_rows"]

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

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

def _serve_html(filename):
    with open(os.path.join(HERE, filename), "r", encoding="utf-8") as f:
        html = f.read()
    for asset in ("style.css", "script.js", "leaderboard.js"):
        html = html.replace(f'"{asset}"', f'"{asset}?v={hash(asset)}"')
    return HTMLResponse(html)

@app.get("/")
def index():
    return _serve_html("index.html")

@app.get("/leaderboard")
def leaderboard():
    return _serve_html("leaderboard.html")

app.mount("/", StaticFiles(directory=HERE, html=True), name="static")