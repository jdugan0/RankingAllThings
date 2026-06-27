import pandas as pd
auto_removed = []
auto_kept = []
keywords = ["ethnic", "language", "Islamic", "Islam", "Japanese", "Hindi", "Hindustani"]
data = pd.read_csv("data/zipf_sorted.csv")
for index, row in data.iterrows():
    desc = str(row["itemDesc"])
    if (any(word in desc for word in keywords) and row["zipf"] < 3) or "ethnic" in desc:
        auto_removed.append(row)
    else:
        auto_kept.append(row)
    
pd.DataFrame(auto_kept).to_csv("data/auto_kept_zipf.csv", index=False)
pd.DataFrame(auto_removed).to_csv("data/auto_removed_zipf.csv", index=False)