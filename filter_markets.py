#!/usr/bin/env python3
import json
import subprocess
import sys
import os
from datetime import datetime, timezone

def run_poly_scan(args):
    """Run poly-scan command and return parsed JSON output."""
    # Use absolute path to poly-scan
    poly_path = '/home/boldplane/.openclaw/skills/market-scraper/.venv/bin/poly-scan'
    cmd = [poly_path] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running poly-scan {args}: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from poly-scan {args}: {e}", file=sys.stderr)
        return None

def filter_market(market_id, market_data):
    """Apply trash filter and return True if market should be kept."""
    # Get detailed market info
    details = run_poly_scan(['get_market', market_id])
    if not details:
        print(f"  Could not fetch details for {market_id}, skipping", file=sys.stderr)
        return False
    
    status = details.get('status')
    if status not in ('active', 'open'):
        # closed, resolved, etc.
        print(f"  {market_id}: status {status} -> reject")
        return False
    
    latest = details.get('latest_change')
    if not latest:
        print(f"  {market_id}: missing latest_change -> reject")
        return False
    
    liquidity = latest.get('liquidity', 0)
    last_trade_price = latest.get('last_trade_price')
    
    # Dead Money filter
    if last_trade_price is not None:
        if last_trade_price >= 0.98 or last_trade_price <= 0.02:
            print(f"  {market_id}: dead money price {last_trade_price} -> reject")
            return False
    
    # Ghost Towns filter
    if liquidity < 2000:
        # Check if Ghost Awakens criteria met via ranker's triggered_attributes
        triggered = market_data.get('triggered_attributes', [])
        if 'Ghost Awakens' in triggered:
            print(f"  {market_id}: liquidity {liquidity} < 2000 but Ghost Awakens triggered -> keep")
            # Still need to ensure liquidity > 0? keep
        else:
            print(f"  {market_id}: liquidity {liquidity} < 2000, no Ghost Awakens -> reject")
            return False
    
    # Liquidity ceiling (optional) <= 500,000
    if liquidity > 500000:
        print(f"  {market_id}: liquidity {liquidity} > 500k -> reject (institutional saturation)")
        return False
    
    # All checks passed
    print(f"  {market_id}: keep")
    return True

def main():
    ranker_file = '/home/boldplane/.openclaw/workspace/relevant_markets/ranker_output.json'
    with open(ranker_file, 'r') as f:
        markets = json.load(f)
    
    print(f"Loaded {len(markets)} markets from ranker output")
    kept = []
    for i, m in enumerate(markets):
        market_id = m['market_id']
        print(f"[{i+1}/{len(markets)}] Processing {market_id}")
        if filter_market(market_id, m):
            kept.append(m)
    
    print(f"\nKept {len(kept)} markets after filtering.")
    
    # Write detailed list
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    detailed_path = f'/home/boldplane/.openclaw/workspace/relevant_markets/{date_str}.txt'
    with open(detailed_path, 'w') as f:
        for m in kept:
            # Format: ID, slug, score, strategy, reasoning
            # strategy is triggered_attributes joined with '+'
            strategies = '+'.join(m.get('triggered_attributes', []))
            reasoning = f"Triggered: {strategies}"
            line = f"{m['market_id']} | {m['slug']} | {m['interest_score']} | {strategies} | {reasoning}\n"
            f.write(line)
    
    # Write raw IDs
    raw_ids_path = '/home/boldplane/.openclaw/workspace/relevant_markets/raw_ids.txt'
    with open(raw_ids_path, 'w') as f:
        for m in kept:
            f.write(m['market_id'] + '\n')
    
    print(f"Wrote detailed list to {detailed_path}")
    print(f"Wrote raw IDs to {raw_ids_path}")
    
    # If we have less than 90 markets, we need to search for more (Cold Start)
    # For now just exit with error code
    if len(kept) < 90:
        print(f"WARNING: Only {len(kept)} markets passed filter, need 90. Initiating Cold Start.")
        sys.exit(1)
    else:
        print("Successfully filtered to 90 markets.")

if __name__ == '__main__':
    main()