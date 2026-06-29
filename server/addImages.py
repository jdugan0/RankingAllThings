import sqlite3, pandas as pd, re

con = sqlite3.connect("data/things.db")
df = pd.read_csv("data/images.csv")

rows = []
for item, img in zip(df["item"], df["img"]):
    m = re.search(r"Q(\d+)", str(item))
    if m and pd.notna(img):
        rows.append((str(img), int(m.group(1))))

cur = con.executemany(
    "UPDATE objects SET img = ? WHERE id = ?", rows
)
con.commit()
print(f"csv rows: {len(df)}, updated: {cur.rowcount}")
con.close()
