import pandas as pd
from wordfreq import zipf_frequency
data = pd.read_csv("data/auto_kept.csv")

def findFreq(row):
    return zipf_frequency(row["itemLabel"], "en")

data["zipf"] = data.apply(findFreq, axis=1)

data.sort_values(by="zipf").to_csv("data/zipf_sorted.csv", index=False)