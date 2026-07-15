from scipy.stats import norm
import math,ast

importData = input("Import your order\n")
order = ast.literal_eval(importData)
worst5 = input("What is the WORST movie you'd give 5 stars?\n")
mean  = int(input("What do you think the average star rating of the movies you've seen is?\n"))


i = order.index(worst5)
p_i = (i + 0.5) / len(order)
sigma = (5 - mean) / norm.ppf(p_i)
for x in range(len(order)):
    rate = mean + sigma * norm.ppf((x + 0.5) / len(order))
    rate = max(rate, 0.5)
    rate = min(rate, 5)
    rate = round(rate * 2) / 2
    print(f"{order[x]}: {rate}")