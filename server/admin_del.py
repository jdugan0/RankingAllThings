import os, requests, argparse, sys
H = {"Authorization": f"Bearer {os.environ['ADMIN_KEY']}"}
BASE = "https://justindugan.com/rank"
# id = int(sys.argv[1])

#2192288, 5873, 8124, 58, 8401, 8401, 178066, 185529, 131295, 127683, 8396, 234213, 170538, 5873, 14076, 5887, 181784, 8398, 154136
# 751722, 2122, 608, 290, 228036, 1212935, 172563, 497

remove =[
    ]
for x in remove:
    payload = {'id': x, 'sfw': 0}
    r = requests.post(BASE + "/admin_setsfw", json=payload, headers=H)
    print(r)