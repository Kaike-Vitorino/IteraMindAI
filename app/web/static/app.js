"use strict";

const $ = (id) => document.getElementById(id);
const els = {
  form: $("run-form"),
  task: $("task"),
  provider: $("provider"),
  model: $("model"),
  apiKey: $("api-key"),
  keyField: $("key-field"),
  iterations: $("iterations"),
  iterVal: $("iter-val"),
  temperature: $("temperature"),
  tempVal: $("temp-val"),
  runBtn: $("run-btn"),
  spinner: document.querySelector(".spinner"),
  hint: $("hint"),
  status: $("status"),
  timeline: $("timeline"),
  final: $("final"),
  finalBody: $("final-body"),
};

let providers = [];

// ---- Provider metadata ----------------------------------------------------
async function loadProviders() {
  try {
    const res = await fetch("/api/providers");
    providers = await res.json();
  } catch {
    providers = [{ name: "mock", label: "Mock (offline demo)", default_model: "mock-1", requires_key: false, key_configured: false }];
  }
  els.provider.innerHTML = "";
  for (const p of providers) {
    const opt = document.createElement("option");
    opt.value = p.name;
    const mark = p.requires_key ? (p.key_configured ? " ✓" : " ·key") : " ✓";
    opt.textContent = p.label + mark;
    els.provider.appendChild(opt);
  }
  syncProvider();
}

function currentProvider() {
  return providers.find((p) => p.name === els.provider.value);
}

function syncProvider() {
  const p = currentProvider();
  if (!p) return;
  els.model.placeholder = p.default_model || "default";
  const needsKey = p.requires_key && !p.key_configured;
  els.keyField.style.opacity = p.requires_key ? "1" : "0.5";
  els.hint.textContent = needsKey
    ? `${p.label} needs an API key — paste one above or it will fail.`
    : "";
  els.hint.style.color = needsKey ? "var(--critic)" : "var(--danger)";
}

// ---- Minimal safe markdown (escape first, then code blocks) ---------------
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function renderContent(text) {
  const parts = text.split(/```/);
  let html = "";
  for (let i = 0; i < parts.length; i++) {
    if (i % 2 === 1) {
      const body = parts[i].replace(/^[a-zA-Z0-9]*\n/, "");
      html += `<pre><code>${escapeHtml(body.trim())}</code></pre>`;
    } else {
      const inline = escapeHtml(parts[i]).replace(/`([^`]+)`/g, "<code>$1</code>");
      html += inline
        .split(/\n{2,}/)
        .filter((b) => b.trim())
        .map((b) => `<p>${b.replace(/\n/g, "<br>")}</p>`)
        .join("");
    }
  }
  return html;
}

// ---- Rendering ------------------------------------------------------------
function clearTimeline() {
  els.timeline.innerHTML = "";
  els.final.hidden = true;
  els.finalBody.innerHTML = "";
}
function addCard(step) {
  const card = document.createElement("div");
  card.className = `card ${step.role}`;
  card.innerHTML = `
    <div class="card-head">
      <span class="badge ${step.role}">${step.role}</span>
      <span>Iteration ${step.iteration}</span>
      <span class="meta">${step.provider} · ${step.model}</span>
    </div>
    <div class="content">${renderContent(step.content)}</div>`;
  els.timeline.appendChild(card);
  card.scrollIntoView({ behavior: "smooth", block: "nearest" });
}
function setStatus(kind, text) {
  els.status.className = `status ${kind}`;
  els.status.textContent = text;
}
function setBusy(busy) {
  els.runBtn.disabled = busy;
  els.spinner.hidden = !busy;
  els.runBtn.querySelector(".btn-label").textContent = busy ? "Running…" : "Run iterations";
}

// ---- Run (SSE over fetch stream) ------------------------------------------
async function run(payload) {
  clearTimeline();
  setBusy(true);
  setStatus("running", "running");
  els.hint.textContent = "";

  try {
    const res = await fetch("/api/iterate/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let idx;
      while ((idx = buffer.indexOf("\n\n")) !== -1) {
        const chunk = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);
        const line = chunk.split("\n").find((l) => l.startsWith("data:"));
        if (line) handleEvent(JSON.parse(line.slice(5).trim()));
      }
    }
  } catch (err) {
    setStatus("error", "error");
    els.hint.style.color = "var(--danger)";
    els.hint.textContent = err.message || String(err);
  } finally {
    setBusy(false);
  }
}

function handleEvent(event) {
  if (event.type === "step") {
    addCard(event.step);
  } else if (event.type === "done") {
    setStatus("done", event.result.stopped_early ? "approved early" : "done");
    els.final.hidden = false;
    els.finalBody.innerHTML = renderContent(event.result.final_solution);
  } else if (event.type === "error") {
    setStatus("error", "error");
    els.hint.style.color = "var(--danger)";
    els.hint.textContent = event.message;
  }
}

// ---- Wiring ---------------------------------------------------------------
els.iterations.addEventListener("input", () => (els.iterVal.textContent = els.iterations.value));
els.temperature.addEventListener("input", () => (els.tempVal.textContent = els.temperature.value));
els.provider.addEventListener("change", syncProvider);

els.form.addEventListener("submit", (e) => {
  e.preventDefault();
  const task = els.task.value.trim();
  if (!task) {
    els.hint.style.color = "var(--danger)";
    els.hint.textContent = "Please enter a task.";
    return;
  }
  run({
    task,
    provider: els.provider.value,
    model: els.model.value.trim() || null,
    api_key: els.apiKey.value.trim() || null,
    max_iterations: Number(els.iterations.value),
    temperature: Number(els.temperature.value),
  });
});

loadProviders();
