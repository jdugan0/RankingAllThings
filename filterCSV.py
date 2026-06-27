import pandas as pd, os

data = pd.read_csv("data/zipf_sorted.csv")
done = set()
for f in ("data/kept.csv", "removed.csv"):
    if os.path.exists(f):
        done |= set(pd.read_csv(f)["itemLabel"])
count = 0   
for _, row in data.iterrows():
    if row["sitelinks"] < 90 and row["zipf"] < 3.5:
        count += 1
print(count)

for _, row in data.iterrows():
    if row["itemLabel"] in done:
        continue
    if row["sitelinks"] >= 90 or row["zipf"] >= 3.5:
        out = "data/kept.csv"
        pd.DataFrame([row]).to_csv(out, mode="a", header=not os.path.exists(out), index=False)
        continue
    keep = input(f'\n{row.itemLabel}  |  {row.itemDesc}  |  {row.sitelinks}\n')
    if keep not in ("1", "2"):
        break
    out = "data/kept.csv" if keep == "1" else "data/removed.csv"
    pd.DataFrame([row]).to_csv(out, mode="a", header=not os.path.exists(out), index=False)
