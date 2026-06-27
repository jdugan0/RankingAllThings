import pandas as pd
raw = pd.read_csv("../dataraw.csv")
auto_removed = []
auto_kept = []
for index, row in raw.iterrows():
    if ("moon of" in str(row["itemDesc"])):
        auto_removed.append(row)
    else:
        auto_kept.append(row)

pd.DataFrame(auto_kept).to_csv("../dataauto_kept.csv", index=False)
pd.DataFrame(auto_removed).to_csv("../dataauto_removed.csv", index=False)