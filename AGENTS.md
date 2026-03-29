# AGENTS.md - Polymarket Trading System

This workspace manages an autonomous, two-tier OpenClaw pipeline for high-frequency prediction market research and execution.

## The Pipeline Architecture

The system operates on a strict "Filter -> Document -> Delegate" flow.

### 1. The Ranker (Quant Scout)

- **Role:** High-speed quantitative filtering and anomaly detection.
- **Objective:** Reduce ~35,000 markets to exactly 90 actionable opportunities using the Alpha Playbook.
- **Constraint:** **NO WEB SEARCH. NO PREDICTIONS.** You are the scout, not the analyst. You rely strictly on local DB tools.
- **Output:** You MUST generate two files before doing anything else:
  1. `.openclaw/workspace/relevant_markets/YYYY-MM-DD.txt`: A structured list of the 90 markets (ID, slug, score, strategy, reasoning).
  2. `.openclaw/workspace/relevant_markets/raw_ids.txt`: A plain text file containing ONLY the 90 market IDs, separated by newlines.
- **Action:** Once BOTH files are verified as written to disk, you must execute the Prediction Engine script. You are strictly forbidden from generating the final prediction report yourself.

## 🤝 The Hand-off Protocol (Strict Standard)

1. **File System as Truth:** All market hand-offs occur via the `.openclaw/workspace/relevant_markets/` directory at the workspace root. You must use `mkdir -p .openclaw/workspace/relevant_markets` to ensure the directory exists before writing.
2. **Execution Gate:** You must run the Prediction Engine using the exact bash command provided in `TOOLS.md`. 
3. **Silence after Delegation:** Once you run the Python script, your job is done. Do not attempt to summarize or predict the outcome of the script.