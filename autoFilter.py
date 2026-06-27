import pandas as pd
raw = pd.read_csv("data/raw.csv")
auto_removed = []
auto_kept = []
for index, row in raw.iterrows():
    if ("moon of" in str(row["itemDesc"])):
        auto_removed.append(row)
    else:
        auto_kept.append(row)

pd.DataFrame(auto_kept).to_csv("data/auto_kept.csv", index=False)
pd.DataFrame(auto_removed).to_csv("data/auto_removed.csv", index=False)