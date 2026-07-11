import os, requests, argparse, sys
H = {"Authorization": f"Bearer {os.environ['ADMIN_KEY']}"}
BASE = "https://justindugan.com/rank"
id = int(sys.argv[1])
payload = {'id': id}
requests.post(BASE + "/admin_remove", json=payload)