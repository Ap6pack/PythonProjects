"use strict";

// GeoAsk frontend: chat -> POST /ask -> render the answer layer + transparency
// trace. State is a list of result layers the user can toggle; each /ask call is
// independent (the backend is stateless per request), which is enough for the
// MVP's "ask, refine, ask again" loop.

const PORTLAND = [-122.68, 45.52];
const PALETTE = ["#2f6fed", "#e8590c", "#2f9e44", "#9c36b5", "#e03131", "#0c8599"];

// The map library loads from a CDN; if that's blocked (offline/restricted
// network) the app still works — it shows each answer's explanation and
// transparency trace, just without the map canvas.
const MAP_OK = typeof maplibregl !== "undefined";

let map = null;
let mapReady = false;
const pending = [];

if (MAP_OK) {
  map = new maplibregl.Map({
    container: "map",
    style: "https://demotiles.maplibre.org/style.json",
    center: PORTLAND,
    zoom: 8.5,
  });
  map.addControl(new maplibregl.NavigationControl(), "top-right");
  map.on("load", () => {
    mapReady = true;
    pending.forEach((fn) => fn());
    pending.length = 0;
  });
} else {
  const el = document.getElementById("map");
  el.innerHTML =
    '<div style="display:flex;height:100%;align-items:center;justify-content:center;' +
    'color:var(--muted);padding:24px;text-align:center">' +
    "Map library unavailable on this network — answers and the transparency trace " +
    "still work; layers are listed on the left.</div>";
}

function whenReady(fn) {
  if (!MAP_OK) return;
  if (mapReady) fn();
  else pending.push(fn);
}

const state = { layers: [], seq: 0 };

const els = {
  messages: document.getElementById("messages"),
  form: document.getElementById("ask-form"),
  question: document.getElementById("question"),
  askButton: document.getElementById("ask-button"),
  chips: document.getElementById("chips"),
  layersPanel: document.getElementById("layers-panel"),
  layers: document.getElementById("layers"),
};

// The one MVP question, phrased several ways — all resolve to the same sample
// access-gap result via /ask/demo, demonstrating phrasing robustness offline.
const SAMPLES = [
  "Neighbourhoods >10 min from a pharmacy with above-average seniors",
  "Where are the pharmacy deserts?",
  "Which older communities can't easily reach a pharmacy?",
];

// --- messaging --------------------------------------------------------------

const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function addMessage(text, kind, swatch) {
  const div = document.createElement("div");
  div.className = `msg ${kind}`;
  if (swatch) {
    const dot = document.createElement("span");
    dot.className = "swatch";
    dot.style.background = swatch;
    dot.setAttribute("aria-hidden", "true");
    div.appendChild(dot);
  }
  div.appendChild(document.createTextNode(text));
  els.messages.appendChild(div);
  els.messages.scrollTop = els.messages.scrollHeight;
  return div;
}

function addThinking() {
  const div = addMessage("Working", "assistant");
  div.classList.add("thinking");
  div.setAttribute("role", "status");
  return div;
}

// --- transparency trace -----------------------------------------------------

function describeStep(step) {
  const a = step.args || {};
  const n = step.result && step.result.feature_count;
  if (step.is_error) return `${step.tool}: ${step.result.error}`;
  switch (step.tool) {
    case "load_pois": return `Loaded ${n} “${a.category}” location(s)`;
    case "load_tracts": return `Loaded ${n} census tracts`;
    case "isochrone": return `Built ${a.minutes}-min ${a.mode || "drive"}-time areas`;
    case "buffer": return `Buffered by ${a.distance_m} m`;
    case "spatial_join":
      return a.keep === "non_matching"
        ? `Selected features outside every area (the access gap): ${n}`
        : `Selected features that ${a.predicate || "intersect"}: ${n}`;
    case "filter_by_attribute": return `Kept where ${a.attribute} ${a.op} ${a.value}: ${n}`;
    case "demographic_overlay": return `Overlaid ${a.value_field} onto the areas`;
    case "nearest": return `Measured distance to the nearest destination`;
    case "finish": return `Final answer ready`;
    default: return step.tool;
  }
}

function addSummary(container, geojson) {
  const feats = geojson.features || [];
  let pop = 0, hasPop = false;
  feats.forEach((f) => {
    const p = f.properties && f.properties.population;
    if (typeof p === "number") { pop += p; hasPop = true; }
  });
  const div = document.createElement("div");
  div.className = "summary";
  const n = feats.length;
  div.innerHTML = `<strong>${n}</strong> neighbourhood${n === 1 ? "" : "s"} in the access gap`
    + (hasPop ? ` · <strong>~${pop.toLocaleString()}</strong> residents` : "");
  container.appendChild(div);
}

// Plain-language list of the neighbourhoods, so a non-technical user gets the
// answer in words without having to read the map.
function addReadout(container, geojson) {
  const feats = (geojson.features || []).filter((f) => f.properties && f.properties.tract);
  if (!feats.length) return;
  const parts = feats.slice(0, 8).map((f) => {
    const p = f.properties;
    const s = typeof p.pct_senior === "number" ? ` (${Math.round(p.pct_senior)}% seniors)` : "";
    return p.tract + s;
  });
  const more = feats.length > 8 ? `, and ${feats.length - 8} more` : "";
  const div = document.createElement("div");
  div.className = "readout";
  div.textContent = "Neighbourhoods: " + parts.join(", ") + more + ".";
  container.appendChild(div);
}

// A clarifying question's options, as clickable buttons. Picking one continues
// the conversation instead of leaving the user stuck.
function addClarifyOptions(container, options, resolveEndpoint) {
  const row = document.createElement("div");
  row.className = "options";
  options.forEach((opt) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.textContent = opt;
    b.addEventListener("click", () => {
      addMessage(opt, "user");
      // In the offline demo, any choice resolves to the sample map; against the
      // live backend, the choice refines the original question.
      if (resolveEndpoint.includes("/demo")) submitQuestion(opt, "/ask/demo");
      else submitQuestion(`${lastQuestion} — ${opt}`, "/ask");
    });
    row.appendChild(b);
  });
  container.appendChild(row);
}

function addHint(container, text) {
  const div = document.createElement("div");
  div.className = "hint";
  div.textContent = text;
  container.appendChild(div);
}

// Per-query LLM cost, so the operator can see what each question costs (the
// plan flags cost as a risk to track). Hidden for the scripted demo (0 tokens).
function addUsage(container, usage) {
  if (!usage) return;
  const tokens = (usage.input_tokens || 0) + (usage.output_tokens || 0);
  if (tokens <= 0) return;
  const cost = usage.est_cost_usd || 0;
  const div = document.createElement("div");
  div.className = "usage";
  div.textContent = `${tokens.toLocaleString()} tokens · ~$${cost < 0.01 ? cost.toFixed(4) : cost.toFixed(2)}`;
  container.appendChild(div);
}

// Quick refinements of the current answer — the "now only show ones with >20%
// seniors" loop from the plan, one tap.
function addRefine(container, endpoint) {
  const isDemo = endpoint.includes("/demo");
  const refinements = isDemo
    ? [["Only ≥20% seniors", "/ask/demo?variant=refine", null]]
    : [
        ["Only the ones with >20% seniors", "/ask", "but only where seniors are more than 20% of the population"],
        ["Widen to a 15-minute drive", "/ask", "but use a 15-minute drive time"],
      ];
  const wrap = document.createElement("div");
  wrap.className = "refine";
  const label = document.createElement("span");
  label.className = "refine-label";
  label.textContent = "Refine:";
  wrap.appendChild(label);
  const row = document.createElement("div");
  row.className = "options";
  refinements.forEach(([text, ep, phrase]) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.textContent = text;
    b.addEventListener("click", () => {
      addMessage(text, "user");
      submitQuestion(phrase ? `${lastQuestion} — ${phrase}` : text, ep);
    });
    row.appendChild(b);
  });
  wrap.appendChild(row);
  container.appendChild(wrap);
}

function addTrace(container, trace) {
  const det = document.createElement("details");
  det.className = "trace";
  det.open = true;
  const sum = document.createElement("summary");
  sum.textContent = "What the engine did";
  det.appendChild(sum);
  const ol = document.createElement("ol");
  trace.forEach((step) => {
    const li = document.createElement("li");
    if (step.is_error) li.className = "err";
    li.textContent = describeStep(step);
    ol.appendChild(li);
  });
  det.appendChild(ol);
  container.appendChild(det);
}

// --- map layers -------------------------------------------------------------

function bboxOf(geojson) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  const walk = (c) => {
    if (typeof c[0] === "number") {
      minX = Math.min(minX, c[0]); maxX = Math.max(maxX, c[0]);
      minY = Math.min(minY, c[1]); maxY = Math.max(maxY, c[1]);
    } else c.forEach(walk);
  };
  (geojson.features || []).forEach((f) => f.geometry && walk(f.geometry.coordinates));
  return minX === Infinity ? null : [[minX, minY], [maxX, maxY]];
}

function addResultLayer(geojson, name, color) {
  const id = `res_${state.seq++}`;
  const sub = [`${id}_fill`, `${id}_line`, `${id}_pt`];
  whenReady(() => {
    map.addSource(id, { type: "geojson", data: geojson });
    map.addLayer({ id: sub[0], type: "fill", source: id,
      filter: ["==", ["geometry-type"], "Polygon"],
      paint: { "fill-color": color, "fill-opacity": 0.28 } });
    map.addLayer({ id: sub[1], type: "line", source: id,
      filter: ["==", ["geometry-type"], "Polygon"],
      paint: { "line-color": color, "line-width": 2 } });
    map.addLayer({ id: sub[2], type: "circle", source: id,
      filter: ["==", ["geometry-type"], "Point"],
      paint: { "circle-color": color, "circle-radius": 6, "circle-stroke-color": "#fff", "circle-stroke-width": 1.5 } });
    const bb = bboxOf(geojson);
    if (bb) map.fitBounds(bb, { padding: 60, maxZoom: 12, duration: REDUCED_MOTION ? 0 : 600 });
  });
  const layer = { id, name, color, sub, visible: true };
  state.layers.push(layer);
  renderLayerList();
  return layer;
}

function renderLayerList() {
  els.layersPanel.hidden = state.layers.length === 0;
  els.layers.innerHTML = "";
  state.layers.forEach((layer) => {
    const li = document.createElement("li");
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = layer.visible;
    cb.setAttribute("aria-label", `Show layer: ${layer.name}`);
    cb.addEventListener("change", () => {
      layer.visible = cb.checked;
      const v = cb.checked ? "visible" : "none";
      whenReady(() => layer.sub.forEach((s) => map.getLayer(s) && map.setLayoutProperty(s, "visibility", v)));
    });
    const sw = document.createElement("span");
    sw.className = "swatch";
    sw.style.background = layer.color;
    sw.setAttribute("aria-hidden", "true");
    const label = document.createElement("span");
    label.textContent = layer.name;
    li.append(cb, sw, label);
    els.layers.appendChild(li);
  });
}

// --- request flow -----------------------------------------------------------

function setBusy(busy) {
  els.askButton.disabled = busy;
  els.chips.querySelectorAll("button").forEach((b) => (b.disabled = busy));
}

let lastQuestion = "";

async function submitQuestion(question, endpoint) {
  lastQuestion = question;
  setBusy(true);
  const thinking = addThinking();
  try {
    const resp = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    thinking.remove();

    if (!resp.ok) {
      const detail = await resp.json().catch(() => ({}));
      const msg = addMessage(
        resp.status === 503
          ? "This deployment isn't connected to live data yet."
          : `Something went wrong (${resp.status}).`,
        "error"
      );
      addHint(msg, "You can still try the sample questions below — they run with no setup.");
      return;
    }

    const data = await resp.json();

    // 1) The engine needs a clarification — ask, with clickable options.
    if (data.clarification) {
      const msg = addMessage(data.clarification.question, "assistant");
      addClarifyOptions(msg, data.clarification.options || [], endpoint);
      return;
    }

    const color = PALETTE[state.layers.length % PALETTE.length];
    const hasMap = data.geojson && (data.geojson.features || []).length > 0;
    const msg = addMessage(data.explanation || "(no explanation)", "assistant", hasMap ? color : null);

    if (hasMap) {
      // 2) A real answer — summary, plain-language readout, trace, map layer,
      //    cost, and one-tap refinements.
      addSummary(msg, data.geojson);
      addReadout(msg, data.geojson);
      if (data.trace && data.trace.length) addTrace(msg, data.trace);
      addUsage(msg, data.usage);
      addRefine(msg, endpoint);
      const count = data.geojson.features.length;
      addResultLayer(data.geojson, `${trimName(question)} (${count})`, color);
    } else if (data.finished) {
      // 3) Finished but nothing matched.
      addHint(msg, "No neighbourhoods matched. Try widening it — a longer travel time, or dropping the demographic filter.");
      if (data.trace && data.trace.length) addTrace(msg, data.trace);
    } else {
      // 4) Out of scope — the model answered in prose. Nudge toward what works.
      addHint(msg, "Right now I map access-gap questions — which neighbourhoods are poorly served by a facility. Try a sample below.");
    }
  } catch (err) {
    thinking.remove();
    addMessage(`Network error: ${err.message}`, "error");
  } finally {
    setBusy(false);
  }
}

function trimName(q) {
  return q.length > 28 ? q.slice(0, 27) + "…" : q;
}

els.form.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = els.question.value.trim();
  if (!q) return;
  addMessage(q, "user");
  els.question.value = "";
  submitQuestion(q, "/ask");
});

// Render the sample-question chips. Most hit /ask/demo (same sample result),
// showing the one MVP question type is robust to phrasing; one is deliberately
// vague to show the engine asking a clarifying question.
function addChip(text, onClick) {
  const chip = document.createElement("button");
  chip.type = "button";
  chip.className = "chip";
  chip.textContent = text;
  chip.addEventListener("click", onClick);
  els.chips.appendChild(chip);
}

SAMPLES.forEach((text) =>
  addChip(text, () => {
    addMessage(text, "user");
    submitQuestion(text, "/ask/demo");
  })
);
addChip("Which areas are underserved?  (vague — see it ask)", () => {
  addMessage("Which areas are underserved?", "user");
  submitQuestion("Which areas are underserved?", "/ask/demo?variant=clarify");
});

// Welcome / empty state so a first-time, non-technical user knows what to do.
addMessage(
  "Hi! Ask which neighbourhoods are poorly served by a facility — for example, "
    + "“where are the pharmacy deserts?” I’ll build the map and show my "
    + "work. Not sure where to start? Tap a sample below.",
  "assistant"
);
