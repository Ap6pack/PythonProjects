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
  demoButton: document.getElementById("demo-button"),
  layersPanel: document.getElementById("layers-panel"),
  layers: document.getElementById("layers"),
};

// --- messaging --------------------------------------------------------------

function addMessage(text, kind, swatch) {
  const div = document.createElement("div");
  div.className = `msg ${kind}`;
  if (swatch) {
    const dot = document.createElement("span");
    dot.className = "swatch";
    dot.style.background = swatch;
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
    if (bb) map.fitBounds(bb, { padding: 60, maxZoom: 12, duration: 600 });
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
    cb.addEventListener("change", () => {
      layer.visible = cb.checked;
      const v = cb.checked ? "visible" : "none";
      whenReady(() => layer.sub.forEach((s) => map.getLayer(s) && map.setLayoutProperty(s, "visibility", v)));
    });
    const sw = document.createElement("span");
    sw.className = "swatch";
    sw.style.background = layer.color;
    const label = document.createElement("span");
    label.textContent = layer.name;
    li.append(cb, sw, label);
    els.layers.appendChild(li);
  });
}

// --- request flow -----------------------------------------------------------

async function submitQuestion(question, endpoint) {
  els.askButton.disabled = true;
  els.demoButton.disabled = true;
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
      addMessage(
        resp.status === 503
          ? `Not configured: ${detail.detail || "backend unavailable"}. Try the sample question below.`
          : `Request failed (${resp.status}).`,
        "error"
      );
      return;
    }

    const data = await resp.json();
    const color = PALETTE[state.layers.length % PALETTE.length];
    const hasMap = data.geojson && (data.geojson.features || []).length > 0;

    const msg = addMessage(data.explanation || "(no explanation)", "assistant", hasMap ? color : null);
    if (data.trace && data.trace.length) addTrace(msg, data.trace);

    if (hasMap) {
      const count = data.geojson.features.length;
      addResultLayer(data.geojson, `${trimName(question)} (${count})`, color);
    } else if (data.finished === false) {
      // model answered in prose without producing a map — already shown.
    }
  } catch (err) {
    thinking.remove();
    addMessage(`Network error: ${err.message}`, "error");
  } finally {
    els.askButton.disabled = false;
    els.demoButton.disabled = false;
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

const SAMPLE_Q = "Neighbourhoods >10 min from a pharmacy with above-average seniors";
els.demoButton.addEventListener("click", () => {
  addMessage(SAMPLE_Q, "user");
  submitQuestion(SAMPLE_Q, "/ask/demo");
});
