CREATE TABLE objects (
    id INT PRIMARY KEY,
    label TEXT,
    descr TEXT,
    rating REAL DEFAULT 1500,
    rd REAL DEFAULT 350,
    img TEXT
);

CREATE TABLE votes (
  winner_id TEXT,
  loser_id  TEXT,
  ts        TEXT DEFAULT CURRENT_TIMESTAMP
);