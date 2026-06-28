import sqlite3, pandas as pd, re
con = sqlite3.connect("data/things.db")
con.executescript(open("server/schema.sql").read())

df = pd.read_csv("data/kept.csv")
#item,itemLabel,itemDesc,sitelinks
df["item"] = df["item"].apply(lambda x: int(re.search(r"\d+", x).group()))
df = df.rename(columns={"item" : "id", "itemLabel" : "label", "itemDesc" : "descr"})
df = df.drop(columns=['sitelinks', 'zipf'])
df.to_sql("objects", con, if_exists="append", index=False)
con.commit()

print(con.execute("SELECT label, rating, rd FROM objects LIMIT 5").fetchall())