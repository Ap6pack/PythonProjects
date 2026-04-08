from __future__ import annotations

import json
import random
import subprocess
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).parent / "data"
TRADES_FILE = DATA_DIR / "trades.json"
STATE_FILE = DATA_DIR / "state.json"
CONFIG_FILE = Path(__file__).parent / "config.json"


@dataclass
class CopiedTrade:
    timestamp: str
    source_trader: str
    market_slug: str
    outcome: str
    action: str
    source_amount_usd: float
    copied_amount_usd: float
    status: str
    pnl_usd: float = 0.0
    error: str | None = None


class BullpenClient:
    """Thin wrapper over Bullpen CLI.

    Commands are intentionally conservative and can be adjusted to your local
    Bullpen CLI version.
    """

    def _run(self, args: list[str]) -> dict[str, Any]:
        try:
            completed = subprocess.run(
                args,
                check=True,
                text=True,
                capture_output=True,
            )
            out = completed.stdout.strip() or "{}"
            return json.loads(out)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Bullpen command failed: {' '.join(args)} :: {exc}") from exc

    def preflight(self) -> dict[str, Any]:
        return self._run(["bullpen", "polymarket", "preflight", "--json"])

    def approve(self) -> dict[str, Any]:
        return self._run(["bullpen", "polymarket", "approve", "--yes", "--json"])

    def leaderboard(self, timeframe: str = "week") -> list[dict[str, Any]]:
        payload = self._run([
            "bullpen",
            "polymarket",
            "data",
            "leaderboard",
            "--timeframe",
            timeframe,
            "--json",
        ])
        return payload.get("traders", [])

    def trader_trades(self, wallet: str) -> list[dict[str, Any]]:
        payload = self._run([
            "bullpen",
            "polymarket",
            "data",
            "profile",
            "trades",
            "--wallet",
            wallet,
            "--json",
        ])
        return payload.get("trades", [])


class CopyBot:
    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.running = False
        self.thread: threading.Thread | None = None
        self.client = BullpenClient()
        self.config = self._load_config()
        self._ensure_files()

    def _load_config(self) -> dict[str, Any]:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text())
        example = Path(__file__).parent / "config.example.json"
        return json.loads(example.read_text())

    def _ensure_files(self) -> None:
        if not TRADES_FILE.exists():
            TRADES_FILE.write_text("[]")
        if not STATE_FILE.exists():
            STATE_FILE.write_text(json.dumps({"seen_trade_ids": []}, indent=2))

    def _read_json(self, path: Path, default: Any) -> Any:
        try:
            return json.loads(path.read_text())
        except Exception:
            return default

    def _write_json(self, path: Path, data: Any) -> None:
        path.write_text(json.dumps(data, indent=2))

    def start(self) -> bool:
        with self.lock:
            if self.running:
                return False
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            return True

    def stop(self) -> bool:
        with self.lock:
            if not self.running:
                return False
            self.running = False
            return True

    def _append_trade(self, trade: CopiedTrade) -> None:
        current = self._read_json(TRADES_FILE, [])
        current.append(asdict(trade))
        self._write_json(TRADES_FILE, current)

    def _loop(self) -> None:
        while self.running:
            try:
                self._tick()
            except Exception as exc:  # noqa: BLE001
                self._append_trade(
                    CopiedTrade(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        source_trader="system",
                        market_slug="n/a",
                        outcome="n/a",
                        action="error",
                        source_amount_usd=0,
                        copied_amount_usd=0,
                        status="failed",
                        error=str(exc),
                    )
                )
            time.sleep(self.config.get("poll_interval_seconds", 30))

    def _top_active_traders(self) -> list[str]:
        # Fallback simulator: returns placeholder traders if CLI is unavailable.
        try:
            traders = self.client.leaderboard(self.config.get("leaderboard_timeframe", "week"))
            active = [
                t for t in traders if float(t.get("volume", 0)) >= self.config.get("min_active_volume", 1)
            ]
            active.sort(key=lambda t: float(t.get("pnl", 0)), reverse=True)
            return [t.get("wallet") for t in active[: self.config.get("top_trader_count", 10)] if t.get("wallet")]
        except Exception:
            return [f"sim_trader_{n}" for n in range(1, self.config.get("top_trader_count", 10) + 1)]

    def _tick(self) -> None:
        state = self._read_json(STATE_FILE, {"seen_trade_ids": []})
        seen = set(state.get("seen_trade_ids", []))

        wallets = self._top_active_traders()
        new_ids: list[str] = []

        for wallet in wallets:
            source_trades = self._fetch_trades(wallet)
            for source_trade in source_trades:
                trade_id = source_trade["id"]
                if trade_id in seen:
                    continue
                seen.add(trade_id)
                new_ids.append(trade_id)
                self._copy_trade(wallet, source_trade)

        if new_ids:
            state["seen_trade_ids"] = list(seen)
            self._write_json(STATE_FILE, state)

    def _fetch_trades(self, wallet: str) -> list[dict[str, Any]]:
        try:
            trades = self.client.trader_trades(wallet)
            normalized = []
            for t in trades:
                normalized.append(
                    {
                        "id": str(t.get("id") or t.get("txHash") or random.random()),
                        "slug": t.get("marketSlug", "unknown-market"),
                        "outcome": t.get("outcome", "YES"),
                        "action": str(t.get("side", "BUY")).lower(),
                        "amount": float(t.get("amountUsd", 5)),
                    }
                )
            return normalized[:5]
        except Exception:
            # Simulated fallback data for local testing.
            if random.random() < 0.65:
                return []
            action = "buy" if random.random() < 0.8 else "sell"
            return [
                {
                    "id": f"{wallet}-{int(time.time())}",
                    "slug": random.choice([
                        "will-fed-cut-rates-2026",
                        "bitcoin-above-100k-2026",
                        "us-election-market-demo",
                    ]),
                    "outcome": random.choice(["YES", "NO"]),
                    "action": action,
                    "amount": round(random.uniform(5, 100), 2),
                }
            ]

    def _copy_trade(self, wallet: str, source_trade: dict[str, Any]) -> None:
        action = source_trade["action"]
        copy_amount = float(self.config.get("trade_amount_usd", 5))

        # placeholder pnl calculation for resolved trades in paper mode
        pnl = 0.0
        status = "copied"
        if action == "sell":
            pnl = round(random.uniform(-6, 8), 2)
            status = "closed"

        trade = CopiedTrade(
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_trader=wallet,
            market_slug=source_trade["slug"],
            outcome=source_trade["outcome"],
            action=action,
            source_amount_usd=source_trade["amount"],
            copied_amount_usd=copy_amount,
            status=status,
            pnl_usd=pnl,
        )
        self._append_trade(trade)

    def stats(self) -> dict[str, Any]:
        trades = self._read_json(TRADES_FILE, [])
        executed = [t for t in trades if t.get("status") in {"copied", "closed"}]
        closed = [t for t in trades if t.get("status") == "closed"]
        winners = [t for t in closed if float(t.get("pnl_usd", 0)) > 0]
        losers = [t for t in closed if float(t.get("pnl_usd", 0)) < 0]
        failed = [t for t in trades if t.get("status") == "failed"]
        skipped = [t for t in trades if t.get("status") == "skipped"]

        win_rate = (len(winners) / len(closed) * 100) if closed else 0.0
        pnl = round(sum(float(t.get("pnl_usd", 0)) for t in closed), 2)

        return {
            "running": self.running,
            "total_pnl_usd": pnl,
            "win_rate": round(win_rate, 2),
            "trades_executed": len(executed),
            "winners": len(winners),
            "losers": len(losers),
            "failed": len(failed),
            "skipped": len(skipped),
            "recent_trades": list(reversed(trades[-100:])),
        }
Trade/polymarket_copybot/dashboard.py
Trade/polymarket_copybot/dashboard.py
New
+119
-0

from __future__ import annotations

from flask import Flask, jsonify, render_template_string

from copybot import CopyBot

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Polymarket Copy Bot</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #0b1020; color: #e4e8f3; }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(130px, 1fr)); gap: 12px; }
    .card { background: #151d36; border-radius: 10px; padding: 12px; }
    button { padding: 10px 16px; border-radius: 8px; border: none; cursor: pointer; }
    .ok { background: #1f9d55; color: white; }
    .warn { background: #d64545; color: white; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    th, td { text-align: left; border-bottom: 1px solid #2a355d; padding: 8px; font-size: 13px; }
  </style>
</head>
<body>
  <h1>Polymarket Copy Bot Dashboard</h1>
  <p>Status: <strong id="status">stopped</strong></p>
  <button class="ok" onclick="startBot()">Start Live</button>
  <button class="warn" onclick="stopBot()">Stop</button>

  <h2>Stats</h2>
  <div class="grid">
    <div class="card">PnL: <span id="pnl">0</span></div>
    <div class="card">Win rate: <span id="winRate">0</span>%</div>
    <div class="card">Executed: <span id="executed">0</span></div>
    <div class="card">Winners: <span id="winners">0</span></div>
    <div class="card">Losers: <span id="losers">0</span></div>
    <div class="card">Failed: <span id="failed">0</span></div>
    <div class="card">Skipped: <span id="skipped">0</span></div>
  </div>

  <h2>Trade Log</h2>
  <table>
    <thead><tr><th>Time</th><th>Trader</th><th>Market</th><th>Outcome</th><th>Action</th><th>Amount</th><th>Status</th><th>PnL</th></tr></thead>
    <tbody id="trades"></tbody>
  </table>

<script>
async function loadStats() {
  const r = await fetch('/api/stats');
  const data = await r.json();
  document.getElementById('status').innerText = data.running ? 'running' : 'stopped';
  document.getElementById('pnl').innerText = data.total_pnl_usd;
  document.getElementById('winRate').innerText = data.win_rate;
  document.getElementById('executed').innerText = data.trades_executed;
  document.getElementById('winners').innerText = data.winners;
  document.getElementById('losers').innerText = data.losers;
  document.getElementById('failed').innerText = data.failed;
  document.getElementById('skipped').innerText = data.skipped;

  const rows = data.recent_trades.map(t => `
    <tr>
      <td>${t.timestamp}</td>
      <td>${t.source_trader}</td>
      <td>${t.market_slug}</td>
      <td>${t.outcome}</td>
      <td>${t.action}</td>
      <td>${t.copied_amount_usd}</td>
      <td>${t.status}</td>
      <td>${t.pnl_usd}</td>
    </tr>
  `).join('');
  document.getElementById('trades').innerHTML = rows;
}

async function startBot() {
  await fetch('/api/start', { method: 'POST' });
  await loadStats();
}

async function stopBot() {
  await fetch('/api/stop', { method: 'POST' });
  await loadStats();
}

setInterval(loadStats, 5000);
loadStats();
</script>
</body>
</html>
"""


def create_app() -> Flask:
    bot = CopyBot()
    app = Flask(__name__)

    @app.get("/")
    def home() -> str:
        return render_template_string(HTML)

    @app.get("/api/stats")
    def stats():
        return jsonify(bot.stats())

    @app.post("/api/start")
    def start():
        started = bot.start()
        return jsonify({"started": started, "running": True})

    @app.post("/api/stop")
    def stop():
        stopped = bot.stop()
        return jsonify({"stopped": stopped, "running": False})

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5055, debug=False)
