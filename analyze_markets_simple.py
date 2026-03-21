#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, timedelta
import math

def run_polymarket_command(cmd):
    """Run polymarket_tools command and return JSON output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd="/home/boldplane/.openclaw/skills/market-scarper"
        )
        if result.returncode != 0:
            print(f"Error running command: {result.stderr}")
            return []
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Exception: {e}")
        return []

def get_all_open_markets():
    """Get all open markets"""
    print("Fetching all open markets...")
    # Get all open markets (no limit)
    markets = run_polymarket_command("python3 -m polymarket_tools get_open_markets")
    return markets

def get_market_trends(market_id):
    """Get historical trends for a market"""
    trends = run_polymarket_command(f"python3 -m polymarket_tools get_market_trends {market_id} --limit 20")
    return trends

def calculate_score(market, trends=None):
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
    
    # Strategy 1: Volume Shock (24-hour volume is >300% of its 7-day moving average)
    # We need historical data for this, will handle with trends if available
    
    # Strategy 2: Breakout (last_traded_price has shifted >10% within last 4 hours)
    # Need historical data
    
    # Strategy 3: Spread Anomaly (spread has suddenly doubled compared to recent average)
    # Need historical data
    
    # Strategy 4: Information Drift (continuous price movement over last 10 trades)
    # Need trade history
    
    # Strategy 5: The Ghost Awakens (Low Liquidity Exception)
    # Market has <$2,000 liquidity AND experiences a single trade that moves price >5% after 48h zero volume
    if liquidity < 2000 and volume > 0:
        # Check if there was a significant price move
        if trends and len(trends) >= 2:
            oldest_price = trends[-1].get('last_trade_price', last_price)
            if oldest_price > 0 and abs(last_price - oldest_price) / oldest_price > 0.05:
                score += 30
                strategies.append("Ghost Awakens")
                reasoning.append(f"Low liquidity (${liquidity:,.2f}) with >5% price move")
    
    # Strategy 6: Risk-Free Arbitrage
    # Yes_Ask + No_Ask < 0.98 (using yes_price and no_price as proxies)
    if yes_price + no_price < 0.98 and liquidity >= 2000:
        score += 40
        strategies.append("Risk-Free Arbitrage")
        reasoning.append(f"Arbitrage opportunity: sum={yes_price + no_price:.3f}")
    
    # Mid-Volume Mandate: Goldilocks Zone
    if 2000 <= liquidity <= 500000:
        score += 10
        if not reasoning:
            reasoning.append(f"Good liquidity: ${liquidity:,.2f}")
    elif liquidity < 2000 and "Ghost Awakens" not in strategies:
        score -= 20  # Penalize low liquidity unless it's a Ghost Awakens
        reasoning.append(f"Low liquidity: ${liquidity:,.2f}")
    
    # Volume-based scoring (proxy for activity)
    if volume > 50000:
        score += 20
        if "Volume Shock" not in strategies:
            strategies.append("High Volume")
            reasoning.append(f"High volume: ${volume:,.2f}")
    elif volume > 10000:
        score += 10
        reasoning.append(f"Moderate volume: ${volume:,.2f}")
    
    # Price extremity (proxy for breakout)
    if last_price <= 0.15 or last_price >= 0.85:
        score += 15
        if "Breakout" not in strategies:
            strategies.append("Extreme Price")
            reasoning.append(f"Extreme price: {last_price:.3f}")
    
    # Spread-based scoring
    if spread < 0.1:  # Tight spread
        score += 10
        if "Spread Anomaly" not in strategies:
            strategies.append("Tight Spread")
            reasoning.append(f"Tight spread: {spread:.3f}")
    
    # Dead Money filter (applied later)
    is_dead_money = last_price >= 0.98 or last_price <= 0.02
    
    return {
        'market_id': market['market_id'],
        'slug': market['slug'],
        'question': market['question'],
        'score': score,
        'strategies': strategies,
        'reasoning': reasoning,
        'liquidity': liquidity,
        'last_price': last_price,
        'volume': volume,
        'spread': spread,
        'yes_price': yes_price,
        'no_price': no_price,
        'is_dead_money': is_dead_money,
        'status': market['status']
    }

def main():
    print("🚀 Starting Polymarket analysis using Alpha Playbook...")
    print("=" * 80)
    
    # Get all open markets
    all_markets = get_all_open_markets()
    print(f"Found {len(all_markets)} open markets")
    
    if len(all_markets) == 0:
        print("No markets found. Exiting.")
        return
    
    # Analyze each market
    analyzed_markets = []
    for i, market in enumerate(all_markets):
        if i % 50 == 0:
            print(f"Analyzing market {i+1}/{len(all_markets)}...")
        
        # Get trends for more sophisticated analysis
        trends = get_market_trends(market['market_id'])
        analyzed = calculate_score(market, trends)
        analyzed_markets.append(analyzed)
    
    # Filter out trash markets
    filtered_markets = []
    for market in analyzed_markets:
        # Trash filter criteria from SOUL.md
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
    
    print(f"\n📊 Analysis Results:")
    print(f"  Total markets analyzed: {len(analyzed_markets)}")
    print(f"  Markets after filtering: {len(filtered_markets)}")
    print(f"  Top markets selected: {len(top_markets)}")
    
    # Prepare output for files
    output_lines = []
    raw_ids = []
    
    for i, market in enumerate(top_markets, 1):
        strategies_str = ", ".join(market['strategies']) if market['strategies'] else "None"
        reasoning_str = "; ".join(market['reasoning']) if market['reasoning'] else "No specific signals"
        
        line = f"{i}. {market['market_id']} | {market['slug']} | Score: {market['score']} | Strategy: {strategies_str} | Reasoning: {reasoning_str} | Liquidity: ${market['liquidity']:,.2f} | Last Price: {market['last_price']:.3f} | Volume: ${market['volume']:,.2f}"
        output_lines.append(line)
        raw_ids.append(market['market_id'])
    
    # Write to files
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = "/home/boldplane/.openclaw/workspace/relevant_markets"
    
    # Ensure directory exists
    import os
    os.makedirs(output_dir, exist_ok=True)
    
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
    
    print(f"\n📁 Files written:")
    print(f"  - {output_dir}/{date_str}.txt")
    print(f"  - {output_dir}/raw_ids.txt")
    
    print(f"\n🏆 Top 5 markets:")
    for i in range(min(5, len(top_markets))):
        market = top_markets[i]
        print(f"  {i+1}. {market['question'][:60]}...")
        print(f"     Score: {market['score']}, Strategies: {', '.join(market['strategies']) if market['strategies'] else 'None'}")
        print(f"     Liquidity: ${market['liquidity']:,.2f}, Price: {market['last_price']:.3f}")
        print()

if __name__ == "__main__":
    main()