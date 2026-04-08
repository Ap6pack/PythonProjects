+from __future__ import annotations
+
+from flask import Flask, jsonify, render_template_string
+
+from copybot import CopyBot
+
+HTML = """
+<!doctype html>
+<html>
+<head>
+  <meta charset="utf-8" />
+  <title>Polymarket Copy Bot</title>
+  <style>
+    body { font-family: Arial, sans-serif; margin: 24px; background: #0b1020; color: #e4e8f3; }
+    .grid { display: grid; grid-template-columns: repeat(4, minmax(130px, 1fr)); gap: 12px; }
+    .card { background: #151d36; border-radius: 10px; padding: 12px; }
+    button { padding: 10px 16px; border-radius: 8px; border: none; cursor: pointer; }
+    .ok { background: #1f9d55; color: white; }
+    .warn { background: #d64545; color: white; }
+    table { width: 100%; border-collapse: collapse; margin-top: 12px; }
+    th, td { text-align: left; border-bottom: 1px solid #2a355d; padding: 8px; font-size: 13px; }
+  </style>
+</head>
+<body>
+  <h1>Polymarket Copy Bot Dashboard</h1>
+  <p>Status: <strong id="status">stopped</strong></p>
+  <button class="ok" onclick="startBot()">Start Live</button>
+  <button class="warn" onclick="stopBot()">Stop</button>
+
+  <h2>Stats</h2>
+  <div class="grid">
+    <div class="card">PnL: <span id="pnl">0</span></div>
+    <div class="card">Win rate: <span id="winRate">0</span>%</div>
+    <div class="card">Executed: <span id="executed">0</span></div>
+    <div class="card">Winners: <span id="winners">0</span></div>
+    <div class="card">Losers: <span id="losers">0</span></div>
+    <div class="card">Failed: <span id="failed">0</span></div>
+    <div class="card">Skipped: <span id="skipped">0</span></div>
+  </div>
+
+  <h2>Trade Log</h2>
+  <table>
+    <thead><tr><th>Time</th><th>Trader</th><th>Market</th><th>Outcome</th><th>Action</th><th>Amount</th><th>Status</th><th>PnL</th></tr></thead>
+    <tbody id="trades"></tbody>
+  </table>
+
+<script>
+async function loadStats() {
+  const r = await fetch('/api/stats');
+  const data = await r.json();
+  document.getElementById('status').innerText = data.running ? 'running' : 'stopped';
+  document.getElementById('pnl').innerText = data.total_pnl_usd;
+  document.getElementById('winRate').innerText = data.win_rate;
+  document.getElementById('executed').innerText = data.trades_executed;
+  document.getElementById('winners').innerText = data.winners;
+  document.getElementById('losers').innerText = data.losers;
+  document.getElementById('failed').innerText = data.failed;
+  document.getElementById('skipped').innerText = data.skipped;
+
+  const rows = data.recent_trades.map(t => `
+    <tr>
+      <td>${t.timestamp}</td>
+      <td>${t.source_trader}</td>
+      <td>${t.market_slug}</td>
+      <td>${t.outcome}</td>
+      <td>${t.action}</td>
+      <td>${t.copied_amount_usd}</td>
+      <td>${t.status}</td>
+      <td>${t.pnl_usd}</td>
+    </tr>
+  `).join('');
+  document.getElementById('trades').innerHTML = rows;
+}
+
+async function startBot() {
+  await fetch('/api/start', { method: 'POST' });
+  await loadStats();
+}
+
+async function stopBot() {
+  await fetch('/api/stop', { method: 'POST' });
+  await loadStats();
+}
+
+setInterval(loadStats, 5000);
+loadStats();
+</script>
+</body>
+</html>
+"""
+
+
+def create_app() -> Flask:
+    bot = CopyBot()
+    app = Flask(__name__)
+
+    @app.get("/")
+    def home() -> str:
+        return render_template_string(HTML)
+
+    @app.get("/api/stats")
+    def stats():
+        return jsonify(bot.stats())
+
+    @app.post("/api/start")
+    def start():
+        started = bot.start()
+        return jsonify({"started": started, "running": True})
+
+    @app.post("/api/stop")
+    def stop():
+        stopped = bot.stop()
+        return jsonify({"stopped": stopped, "running": False})
+
+    return app
+
+
+if __name__ == "__main__":
+    create_app().run(host="127.0.0.1", port=5055, debug=False)
