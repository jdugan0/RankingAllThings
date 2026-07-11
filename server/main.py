from fastapi import FastAPI, HTTPException
import sqlite3
import math
import random
import os
import base64
import hashlib,hmac
import time
from pydantic import BaseModel

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("THINGS_DB", os.path.join(HERE, "..", "data", "things.db"))

LOCAL = os.environ.get("LOCAL") == "1"

import requests

from fastapi import Request

def db():
    con = sqlite3.connect(DB_PATH, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=5000")
    return con


def client_ip(request: Request) -> str:
    cf = request.headers.get("cf-connecting-ip")
    if cf:
        return cf.strip()
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

TS_SECRET = (b"1x0000000000000000000000000000000AA" if LOCAL
             else os.environ["SECRET_KEY_TURNSTILE"].encode())
def validate_turnstile(token, remoteip=None):
    url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

    data = {
        'secret': TS_SECRET,
        'response': token
    }

    if remoteip:
        data['remoteip'] = remoteip

    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Turnstile validation error: {e}")
        return {'success': False, 'error-codes': ['internal-error']}

def hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)  
    digest = hasher.digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8')[:12]
SECRET = (os.environ.get("SECRET_KEY", "dev-local-secret") if LOCAL
          else os.environ["SECRET_KEY"]).encode()
def sign(msg: str) -> str:
    return hmac.new(SECRET, msg.encode(), hashlib.sha256).hexdigest()

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
def _init_rate_limits():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS rate_limits (
        ip TEXT NOT NULL,
        bucket TEXT NOT NULL,
        window_start INTEGER NOT NULL,
        count INTEGER NOT NULL,
        PRIMARY KEY (ip, bucket)
    )""")
    con.close()
_init_rate_limits()

def _init_sfw():
    con = db()
    cols = {r["name"] for r in con.execute("PRAGMA table_info(objects)")}
    if "sfw" not in cols:
        con.execute("ALTER TABLE objects ADD COLUMN sfw INT DEFAULT 1")
    con.close()
    
_init_sfw()

WINDOW = 60

def check_rate(ip: str, bucket: str, limit: int):
    now = int(time.time())
    con = db()
    try:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute(
            "SELECT window_start, count FROM rate_limits WHERE ip=? AND bucket=?",
            (ip, bucket)).fetchone()
        if row is None or row["window_start"] + WINDOW <= now:
            con.execute(
                "INSERT INTO rate_limits (ip, bucket, window_start, count) VALUES (?,?,?,1) "
                "ON CONFLICT(ip,bucket) DO UPDATE SET window_start=excluded.window_start, count=1",
                (ip, bucket, now))
            allowed, retry = True, 0
        elif row["count"] >= limit:
            allowed, retry = False, row["window_start"] + WINDOW - now
        else:
            con.execute("UPDATE rate_limits SET count = count + 1 WHERE ip=? AND bucket=?",
                        (ip, bucket))
            allowed, retry = True, 0
        if random.random() < 0.01:
            con.execute("DELETE FROM rate_limits WHERE window_start + ? < ?", (WINDOW, now))
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()
    return allowed, retry

from fastapi import Depends

def rate_limit(bucket: str, limit: int):
    def dep(request: Request):
        allowed, retry = check_rate(client_ip(request), bucket, limit)
        if not allowed:
            raise HTTPException(429, headers={"Retry-After": str(max(1, retry))})
    return dep

def glicko_update(old_rating, old_RD, op_rating, op_RD, s):
    q = math.log(10) / 400
    def g(RD):
        return 1 / (math.sqrt(1 + (3 * q * q * RD * RD) / (math.pi * math.pi)))
    E = 1 / (1 + 10**(-g(op_RD) * (old_rating - op_rating)/400))
    dsq = 1 / (q * q * g(op_RD)**2 * E * (1 - E))
    r_new = old_rating + q/(1/old_RD**2 + 1 / dsq )*g(op_RD) * (s - E)
    rd_new = math.sqrt(1 / (1 / old_RD**2 +  1/dsq))
    return (r_new, rd_new)


class Pair(BaseModel):
    sfw : int
@app.post("/pair", dependencies=[Depends(rate_limit("pair", 60))])
def pair(x : Pair):
    con = db()
    row1 = con.execute(
    "SELECT id, label, descr, rd, rating, img, sfw FROM objects WHERE (sfw=? OR sfw=1) ORDER BY RANDOM() LIMIT 1", 
    (x.sfw,)
    ).fetchone()
    sigma = 40
    t = random.gauss(row1["rating"], max(0, sigma - row1["rd"] / 3))
    row2 = con.execute(
        "SELECT id, label, descr, img FROM objects WHERE id != ? AND (sfw=? OR sfw=1) ORDER BY abs(rating - ?), RANDOM() LIMIT 1",
        (row1["id"], x.sfw, t)
    ).fetchone()
    payload = f"{row1['id']},{row2['id']}-{int(time.time())}"
    token = f"{payload}.{sign(payload)}"
    con.close()
    return {'pair': [dict(r) for r in [row1, row2]], 'token' : token}

@app.get("/leaderboard_rank")
def leaderboard_rank():
    con = db()
    rows = con.execute("SELECT label, descr, rating, wins, total, img, sfw FROM objects ORDER BY rating DESC").fetchall()
    con.close()
    return [dict(r) for r in rows]

@app.get("/num_votes")
def num_votes():
    con = db()
    num = con.execute("SELECT COUNT(*) AS total_rows FROM votes").fetchone()
    con.close()
    return num["total_rows"]
    

class Vote(BaseModel):
    winner_id: int
    loser_id: int
    token: str
    turnstile: str
    
TIME = 10 * 60
@app.post("/vote", dependencies=[Depends(rate_limit("vote", 30))])
def vote(v : Vote):
    con = db()
    try:
        con.execute("BEGIN IMMEDIATE")
        token = v.token.split(".")
        turnstile = v.turnstile.rsplit('.')
        if (not hmac.compare_digest(sign(turnstile[0]), turnstile[1])):
            raise HTTPException(403)
        if (int(turnstile[0]) + TIME <= int(time.time())):
            raise HTTPException(403)
        sgn = sign(token[0])
        if (not hmac.compare_digest(sgn, token[1])):
            raise HTTPException(400)
        ts = token[0].split("-")
        if (int(ts[1]) + 120 <= int(time.time())):
            raise HTTPException(400)
        pair = ts[0].split(",")
        if not ((int(pair[0]) == v.winner_id and int(pair[1]) == v.loser_id) 
                or (int(pair[1]) == v.winner_id and int(pair[0]) == v.loser_id)):
            raise HTTPException(400)
        winner = con.execute("SELECT rating, rd FROM objects WHERE id=?", (v.winner_id,)).fetchone()
        loser = con.execute("SELECT rating, rd FROM objects WHERE id=?", (v.loser_id,)).fetchone()
        winner_new = glicko_update(winner["rating"], winner["rd"], loser["rating"], loser["rd"], 1)
        loser_new = glicko_update(loser["rating"], loser["rd"], winner["rating"], winner["rd"], 0)
        con.execute("UPDATE objects SET rating=?, rd=? WHERE id=?", (winner_new[0], winner_new[1], v.winner_id))
        con.execute("UPDATE objects SET rating=?, rd=? WHERE id=?", (loser_new[0], loser_new[1], v.loser_id))
        con.execute("UPDATE objects SET wins = wins + 1, total = total + 1 WHERE id=?", (v.winner_id,))
        con.execute("UPDATE objects SET total = total + 1 WHERE id=?", (v.loser_id,))
        con.execute("INSERT INTO votes (winner_id, loser_id) VALUES (?, ?)", (v.winner_id, v.loser_id))
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()
    return  {'status': 'ok'}


class TS_Token(BaseModel):
    turnstile: str

@app.post("/validate", dependencies=[Depends(rate_limit("validate", 10))])
def validate(token : TS_Token, request: Request):
    ts = token.turnstile
    v = validate_turnstile(ts, remoteip=client_ip(request))
    if (v["success"]):
        tok = f'{int(time.time())}'
        return {'token': f'{tok}.{sign(tok)}'}
    else:
        return {'token': None}
    
@app.post("/validate_timed_token")
def validate_timed_token(token : TS_Token):
    turnstile = token.turnstile.rsplit('.')
    print(turnstile)
    if (not hmac.compare_digest(sign(turnstile[0]), turnstile[1])):
        raise HTTPException(403)
    if (int(turnstile[0]) + TIME <= int(time.time())):
        raise HTTPException(403)
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
def leaderboard_rank():
    return _serve_html("leaderboard.html")

ADMIN_KEY = os.environ.get("ADMIN_KEY", "dev-local-admin") if LOCAL else os.environ["ADMIN_KEY"]

def require_admin(request: Request):
    key = (request.headers.get("authorization") or "").removeprefix("Bearer ")
    if not hmac.compare_digest(key, ADMIN_KEY):
        raise HTTPException(401)
    
    
class Object_SFW(BaseModel):
    id: int
    sfw : int
class Object(BaseModel):
    id: int
class Label(BaseModel):
    label : str
@app.post("/admin_setsfw", dependencies=[Depends(require_admin), Depends(rate_limit("admin", 20))])
def admin_setsfw(x : Object_SFW):
    con = db()
    con.execute("UPDATE objects SET SFW = ? WHERE id = ?", (x.sfw, x.id))
    con.commit()
    con.close()
@app.post("/admin_remove", dependencies=[Depends(require_admin), Depends(rate_limit("admin", 20))])
def admin_remove(x : Object):
    con = db()
    con.execute("DELETE FROM objects WHERE id = ?", (x.id,))
    con.commit()
    con.close()
    return {'message': 'removed'}
@app.post("/admin_getid", dependencies=[Depends(require_admin), Depends(rate_limit("admin", 20))])
def admin_getid(x : Label):
    con=db()
    id = con.execute("SELECT id FROM objects WHERE label=?", (x.label,))
    con.close()
    return {'id': id}

app.mount("/", StaticFiles(directory=HERE, html=True), name="static")