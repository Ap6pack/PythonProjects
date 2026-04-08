# Polymarket Copy Bot (Transcript-Based Starter Project)

This project is a reusable starter app:

- picks top active traders (by weekly PnL)
- polls their recent trades
- mirrors buys with fixed USD sizing
- logs all copied actions to JSON
- exposes a local dashboard with start/stop controls and stats

> Important: this ships with a **paper/simulated fallback mode** so it works locally even if Bullpen CLI commands differ or are unavailable.

## Features implemented

- **Top trader discovery**: fetch leaderboard and keep top N active traders.
- **Copy logic**:
  - buy trades are mirrored at fixed `$5` (configurable)
  - sell events are captured and closed in the local ledger
- **Resilient looping**: per-tick and per-trade error handling.
- **Trade ledger**: JSON logs at `data/trades.json`.
- **Dashboard**:
  - Start/Stop bot button
  - Total PnL, Win Rate, Executed, Winners, Losers, Failed, Skipped
  - Auto-refresh every 5 seconds

## Project layout

- `copybot.py` → bot loop, Bullpen CLI wrapper, trade/state persistence
- `dashboard.py` → Flask web app + API endpoints
- `config.example.json` → runtime settings template
- `requirements.txt` → dependencies

## Setup

```bash
cd Trade/polymarket_copybot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.json config.json
```

## Run

```bash
python dashboard.py
```

Open: <http://127.0.0.1:5055>

## Bullpen CLI notes

Before live trading (not required for paper mode), run:

```bash
bullpen polymarket auth
bullpen polymarket approve --yes
bullpen polymarket preflight
```

If your local Bullpen command shapes differ, edit the argument lists in `BullpenClient` inside `copybot.py`.

## Config

`config.json` keys:

- `poll_interval_seconds`
- `trade_amount_usd`
- `top_trader_count`
- `leaderboard_timeframe`
- `min_active_volume`
- `trade_mode`
- `wallet_address`
- `auto_redeem`
- `max_open_trades`
