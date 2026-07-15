import pandas as pd
import ast
import random
import numpy as np
names = pd.read_csv("watched.csv", usecols=["Name"])["Name"].tolist()
random.shuffle(names)
order = []
movRange = dict()

def comp(a, b):
    try:
        best = int(input(f"Which is better?\n1: {a}\n2: {b}\n")) - 1
        return best
    except ValueError:
        return 10
    


importData = input("Would you like to import an order?\n")
if (importData != ""):
    order = ast.literal_eval(importData)
    for x in order:
        names.remove(x)
else:
    order.append(names.pop())

importMov = input("Would you like to import movie ranges?\n")
if (importMov != ""):
    movRange = ast.literal_eval(importMov)

topN = int(input(f"How many movies would you like to confirm rankings of? (i.e top 10, top 20)."
                 f"\nYou've seen {len(order) + len(names)} total movies.\nTop: "))

def monte_carlo(sims = 1000):
    runs = []
    for i in range(0,sims):
        namesCpy = names.copy()
        orderCpy = order.copy()
        movRangeCpy = movRange.copy()
        c_total = 0
        while (len(namesCpy) > 0):
            next = namesCpy.pop()
            start = 0
            end = len(orderCpy)
            if (next in movRangeCpy):
                lo, hi = movRangeCpy[next]
                start = orderCpy.index(lo) + 1 if lo is not None else 0
                end = orderCpy.index(hi) if hi is not None else len(orderCpy)
            while (start < end):
                if end <= len(orderCpy) - topN:
                    movRangeCpy[next] = (orderCpy[start - 1] if start > 0 else None,
                                         orderCpy[end] if end < len(orderCpy) else None)
                    break
                mid = int((end + start) / 2)
                c = random.choice([0,1])
                c_total += 1
                if (c == 0):
                    start = mid + 1
                elif c==1:
                    end = mid
            orderCpy.insert(start, next)
        runs.append(c_total)
    return runs

monte_runs = monte_carlo()
print(f"It will take ~{round(np.average(monte_runs))} comparisons to find the top {topN}")
        

while (len(names) > 0):
    next = names.pop()
    start = 0
    end = len(order)
    if (next in movRange):
        lo, hi = movRange[next]
        start = order.index(lo) + 1 if lo is not None else 0
        end = order.index(hi) if hi is not None else len(order)
    skip = False
    while (start < end):
        if end <= len(order) - topN:
            skip = True
            movRange[next] = (order[start - 1] if start > 0 else None,
                              order[end] if end < len(order) else None)
            break
        mid = int((end + start) / 2)
        # print(start, mid, end)
        c = comp(next, order[mid])
        if (c == 0):
            start = mid + 1
        elif c==1:
            end = mid
        else:
            skip = True
            break
    if not skip:
        order.insert(start, next)
        print(order)
        print(movRange)