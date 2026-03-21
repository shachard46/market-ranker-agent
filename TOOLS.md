# Tooling and Standard Operating Procedure

## Available Tools

### 1. `market-ranker`

- **Description:** Local Python script (`/home/.openclaw/skills/market-ranker/rank_markets.py`) returning top markets mathematically scored for actionable trading opportunities.
- **Usage:** Run to fetch the initial data set of anomalies, and use the .venv in `/home/.openclaw/skills/market-ranker` to run the script with the correct dependencies.

### 2. `polymarket_tools` (market-scraper)

- **Description:** CLI application to query the Polymarket database.
- **Available Commands:**
  - `search_markets`: Search by keywords.
  - `get_category_markets`: Filter by categories (e.g., Politics, Crypto).
  - `get_open_markets`: Return a list of all currently active markets.
  - `get_market_trends`: Retrieve historical price/volume data.
  - `get_market`: Retrieve full enriched details for a specific market ID.

### 3. File System Tools

- **Description:** Standard bash commands.
- **Usage:** Create directories (`mkdir -p`) and use standard echo/cat/tee commands to write your formatted lists to the required `.txt` files.

### 4. The Prediction Engine

- **Description:** A Python script that ingests `raw_ids.txt`, utilizes web search, and performs fundamental analysis to generate the final prediction report.
- **Usage:** Execute this exact command to launch the script in a detached tmux session called "prediction-engine" (DO NOT alter the path or command):
  ```bash
  tmux new-session -d -s prediction-engine 'cd /home/boldplane/.openclaw/workspace/prediction_engine && python3 batch_runner.py'
  ```

---

## Standard Operating Procedure (SOP)

1. **Execute:** Run `market-ranker` to generate the baseline anomaly list.
2. **Evaluate:** If `market-ranker` fails to return exactly 90 markets, initiate the "Cold Start" fallback using `get_category_markets` and `get_market_trends` until you reach exactly 90.
3. **Document (File 1):** Write the detailed list (market_id, slug, interest_score, strategy, reasoning) to `.openclaw/workspace/relevant_markets/YYYY-MM-DD.txt`.
4. **Document (File 2):** Write ONLY the extracted market IDs, one per line, to `.openclaw/workspace/relevant_markets/raw_ids.txt`.
5. **Delegate:** Execute the Prediction Engine tool via bash using the exact command provided above. **DO NOT generate the final prediction report yourself.** The Python script handles all predictions.
