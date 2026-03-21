import json
import subprocess

def run_poly_scan(args):
    poly_path = '/home/boldplane/.openclaw/skills/market-scraper/.venv/bin/poly-scan'
    cmd = [poly_path] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except:
        return None

with open('/home/boldplane/.openclaw/workspace/relevant_markets/ranker_output.json') as f:
    markets = json.load(f)

count_total = len(markets)
count_geq_2k = 0
count_lt_2k = 0
for i, m in enumerate(markets[:10]):  # first 10 only for speed
    details = run_poly_scan(['get_market', m['market_id']])
    if details and 'latest_change' in details:
        liq = details['latest_change'].get('liquidity', 0)
        if liq >= 2000:
            count_geq_2k += 1
        else:
            count_lt_2k += 1
    else:
        print(f"Failed to fetch {m['market_id']}")

print(f"Total: {count_total}")
print(f"Liquidity >=2k: {count_geq_2k}")
print(f"Liquidity <2k: {count_lt_2k}")