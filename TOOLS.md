# Tooling and Standard Operating Procedure

## Available Tools

### 1. `market-ranker` (CLI)

- **Description:** Installed CLI tool that ranks Polymarket markets by quantitative scoring (Volume Shock, Breakout, Spread Anomaly, Information Drift, Ghost Awakens) against the local SQLite DB.
- **Usage:**
  ```bash
  market-ranker [--limit N] [--db-path PATH] [--output json|table]
  ```
  - `--limit N`: Number of top markets to return (default: 90)
  - `--db-path PATH`: Override database path (default: `POLYMARKET_DB_PATH` env var, then `../market-scarper/polymarket.db`)
  - `--output json|table`: Output format (default: `json`)
- **Output:** JSON array — each object contains: `market_id`, `slug`, `question`, `interest_score`, `triggered_attributes`
- **Example:**
  ```bash
  market-ranker --limit 90
  ```

---

### 2. `poly-scan` (market-scraper CLI)

- **Description:** CLI application to query the Polymarket SQLite database. All query commands print JSON to stdout.
- **Available Commands:**

| Command | Full Usage | Description |
|---------|-----------|-------------|
| `get_open_markets` | `poly-scan get_open_markets [--limit N]` | List open/active markets |
| `get_all_markets` | `poly-scan get_all_markets [--limit N]` | List all markets (any status) |
| `get_closed_markets` | `poly-scan get_closed_markets [--limit N]` | List closed/resolved markets |
| `get_market` | `poly-scan get_market <market_id>` | Full enriched details for one market |
| `get_market_trends` | `poly-scan get_market_trends <market_id> [--limit N]` | Price/volume history for a market |
| `get_category_markets` | `poly-scan get_category_markets <cat> [cat ...] [--limit N]` | Markets by category (supports multiple) |
| `search_markets` | `poly-scan search_markets <kw> [kw ...] [--limit N] [--all] [--and]` | Full-text search on question/description |
| `query_market_field` | `poly-scan query_market_field <market_id> <field_name>` | Get a single field value for a market |

- **Examples:**
  ```bash
  poly-scan get_open_markets --limit 100
  poly-scan get_category_markets Politics Crypto --limit 50
  poly-scan search_markets oil price --limit 30
  poly-scan search_markets bitcoin --and --limit 20
  poly-scan get_market_trends 0xabc123... --limit 100
  poly-scan get_market 0xabc123...
  poly-scan query_market_field 0xabc123... spread
  ```

---

### 3. File System Tools

- **Description:** Standard bash commands.
- **Usage:** Create directories (`mkdir -p`) and use echo/cat/tee to write formatted lists to the required `.txt` files.

---

### 4. The Prediction Engine

- **Description:** A Python script that ingests `raw_ids.txt`, performs web search and fundamental analysis, and generates the final prediction report.
- **Usage:** Execute this exact command to launch in a detached tmux session (DO NOT alter the path or command):
  ```bash
  tmux new-session -d -s prediction-engine 'cd /home/boldplane/.openclaw/workspace/prediction_engine && python3 batch_runner.py'
  ```

---

## Standard Operating Procedure (SOP)

1. **Execute:** Run `market-ranker --limit 90` to generate the baseline anomaly list.
2. **Evaluate:** If `market-ranker` fails or returns fewer than 90 markets, initiate the "Cold Start" fallback — use `poly-scan get_open_markets`, `poly-scan get_category_markets`, and `poly-scan get_market_trends` to manually apply the Alpha Playbook until you reach exactly 90.
3. **Document (File 1):** Write the detailed list (market_id, slug, interest_score, strategy, reasoning) to `relevant_markets/YYYY-MM-DD.txt`.
4. **Document (File 2):** Write ONLY the extracted market IDs, one per line, to `relevant_markets/raw_ids.txt`.
5. **Delegate:** Execute the Prediction Engine via bash using the exact command above. **DO NOT generate the final prediction report yourself.** The Python script handles all predictions.
