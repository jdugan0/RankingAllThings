import pandas as pd
import random
data = pd.read_csv("../datakept.csv")

i1 = random.randint(0, len(data.index) - 1)
i2 = random.randint(0, len(data.index) - 1)

row1 = data.iloc[i1]
row2 = data.iloc[i2]

print(f"\n{row1["itemLabel"]} | {row1["itemDesc"]}\n{row2["itemLabel"]} | {row2["itemDesc"]}\n")