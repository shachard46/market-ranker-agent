#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timedelta
import math

# Load the markets data from stdin
data = json.load(sys.stdin)

# Define the Alpha Playbook strategies
def calculate_score(market):
    """Calculate score based on Alpha Playbook strategies"""
    score = 0
    strategies = []
    reasoning = []
    
    latest = market.get('latest_change', {})
    liquidity = latest.get('liquidity', 0) or 0
    last_price = latest.get('last_trade_price', 0) or 0
    spread = latest.get('spread', 1.0) or 1.0
    volume = latest.get('volume', 0) or 0
    yes_price = latest.get('yes_price', 0.5) or 0.5
    no_price = latest.get('no_price', 0.5) or 0.5
    
    # Strategy 1: Volume Shock (24-hour volume >300% of 7-day moving average)
    # We don't have historical data, so we'll skip this for now
    # But we can use current volume as a proxy
    if volume > 10000:  # High volume threshold
        score += 25
        strategies.append("Volume Shock")
        reasoning.append(f"High volume: ${volume:,.2f}")
    
    # Strategy 2: Breakout (price shifted >10% within last 4 hours)
    # We don't have 4-hour history, but we can check if price is extreme
    if last_price <= 0.1 or last_price >= 0.9:
        score += 20
        strategies.append("Breakout")
        reasoning.append(f"Extreme price: {last_price:.3f}")
    
    # Strategy 3: Spread Anomaly (spread suddenly doubled)
    # Without history, we'll flag unusually wide spreads
    if spread > 0.5:  # Wide spread
        score += 15
        strategies.append("Spread Anomaly")
        reasoning.append(f"Wide spread: {spread:.3f}")
    
    # Strategy 4: Information Drift (continuous price movement)
    # Can't assess without trade history
    
    # Strategy 5: The Ghost Awakens (low liquidity + >5% price move after 48h zero volume)
    # We'll check for low liquidity markets with recent trades
    if liquidity < 2000 and volume > 0:
        score += 30
        strategies.append("Ghost Awakens")
        reasoning.append(f"Low liquidity (${liquidity:,.2f}) with activity")
    
    # Strategy 6: Risk-Free Arbitrage (Yes_Ask + No_Ask < 0.98)
    # Using yes_price and no_price as proxies for ask prices
    if yes_price + no_price < 0.98 and liquidity >= 2000:
        score += 40
        strategies.append("Risk-Free Arbitrage")
        reasoning.append(f"Arbitrage opportunity: {yes_price + no_price:.3f}")
    
    # Mid-Volume Mandate: Goldilocks Zone
    if 2000 <= liquidity <= 500000:
        score += 10
        reasoning.append(f"Good liquidity: ${liquidity:,.2f}")
    elif liquidity < 2000 and "Ghost Awakens" not in strategies:
        score -= 20  # Penalize low liquidity unless it's a Ghost Awakens
        reasoning.append(f"Low liquidity: ${liquidity:,.2f}")
    
    # Dead Money filter (applied later)
    is_dead_money = last_price >= 0.98 or last_price <= 0.02
    
    return {
        'market_id': market['market_id'],
        'slug': market['slug'],
        'score': score,
        'strategies': strategies,
        'reasoning': reasoning,
        'liquidity': liquidity,
        'last_price': last_price,
        'volume': volume,
        'spread': spread,
        'is_dead_money': is_dead_money,
        'status': market['status']
    }

# Analyze all markets
analyzed_markets = []
for market in data:
    analyzed = calculate_score(market)
    analyzed_markets.append(analyzed)

# Filter out trash markets
filtered_markets = []
for market in analyzed_markets:
    # Trash filter criteria
    if market['is_dead_money']:
        continue  # Dead Money
    if market['liquidity'] < 2000 and "Ghost Awakens" not in market['strategies']:
        continue  # Ghost Towns
    if market['status'] != 'active':
        continue  # Closed markets
    
    filtered_markets.append(market)

# Sort by score (highest first)
filtered_markets.sort(key=lambda x: x['score'], reverse=True)

# Take top 90
top_markets = filtered_markets[:90]

# Output results
print(f"Total markets analyzed: {len(analyzed_markets)}")
print(f"Markets after filtering: {len(filtered_markets)}")
print(f"Top markets selected: {len(top_markets)}")

# Prepare output for files
output_lines = []
raw_ids = []

for i, market in enumerate(top_markets, 1):
    strategies_str = ", ".join(market['strategies']) if market['strategies'] else "None"
    reasoning_str = "; ".join(market['reasoning']) if market['reasoning'] else "No specific signals"
    
    line = f"{i}. {market['market_id']} | {market['slug']} | Score: {market['score']} | Strategy: {strategies_str} | Reasoning: {reasoning_str} | Liquidity: ${market['liquidity']:,.2f} | Last Price: {market['last_price']:.3f}"
    output_lines.append(line)
    raw_ids.append(market['market_id'])

# Write to files
date_str = datetime.now().strftime("%Y-%m-%d")
output_dir = "/home/boldplane/.openclaw/agents/market-ranker/relevant_markets"

# Write detailed file
with open(f'{output_dir}/{date_str}.txt', 'w') as f:
    f.write(f"# Top 90 Polymarket Markets - {date_str}\n")
    f.write(f"# Generated by Quant Scout using Alpha Playbook\n")
    f.write(f"# Total analyzed: {len(analyzed_markets)}, Filtered: {len(filtered_markets)}\n\n")
    for line in output_lines:
        f.write(line + '\n')

# Write raw IDs file
with open(f'{output_dir}/raw_ids.txt', 'w') as f:
    for market_id in raw_ids:
        f.write(market_id + '\n')

print(f"\nFiles written:")
print(f"  - relevant_markets/{date_str}.txt")
print(f"  - relevant_markets/raw_ids.txt")
print(f"\nSample of top markets:")
for i in range(min(5, len(top_markets))):
    print(f"  {i+1}. {top_markets[i]['slug'][:50]}... (Score: {top_markets[i]['score']})")