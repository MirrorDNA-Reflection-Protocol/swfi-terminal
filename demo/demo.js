// SWFI /demo — client-side behaviour
// Summer launch surface. Queries Gemini 2.5 Pro via /demo/api/ask with the
// curated 500-entity packet inlined server-side. Renders answer + provenance pills.

const form = document.getElementById("ask-form");
const input = document.getElementById("ask-input");
const answer = document.getElementById("ask-answer");
const presetsEl = document.getElementById("ask-presets");
const coverageCount = document.getElementById("coverage-count");
const coverageMeta = document.getElementById("coverage-meta");

async function loadCoverage() {
  try {
    const r = await fetch("/demo/api/coverage");
    if (!r.ok) return;
    const data = await r.json();
    if (coverageCount && typeof data.count === "number") {
      coverageCount.textContent = data.count.toLocaleString();
    }
    if (coverageMeta && data.generated_at) {
      const d = new Date(data.generated_at);
      const formatted = isNaN(d) ? data.generated_at : d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
      let breakdown = "";
      if (data.sources_breakdown && Object.keys(data.sources_breakdown).length) {
        breakdown = " · " + Object.entries(data.sources_breakdown)
          .map(([k, v]) => `${k}: ${v}`)
          .join(" · ");
      }
      coverageMeta.textContent = `Verified ${formatted}${breakdown}`;
    }
  } catch (_) { /* silent until backend wired */ }
}

async function loadPresets() {
  try {
    const r = await fetch("/demo/api/presets");
    if (!r.ok) return;
    const data = await r.json();
    const presets = data.presets || [];
    if (!presetsEl || presets.length === 0) return;
    presetsEl.innerHTML = presets
      .map(p => `<button data-q="${escapeAttr(p.q)}">${escapeHtml(p.label)}</button>`)
      .join("");
  } catch (_) { /* silent */ }
}

function escapeHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeAttr(s) {
  return String(s).replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

async function ask(q) {
  if (!q) return;
  answer.innerHTML = '<div class="answer-stream" id="answer-stream"></div><span class="stream-cursor" aria-hidden="true">▋</span>';
  const streamEl = document.getElementById("answer-stream");

  try {
    const resp = await fetch(`/demo/api/ask/stream?q=${encodeURIComponent(q)}`);
    if (resp.status === 429) {
      answer.textContent = "Rate limit reached. Please wait a moment and try again.";
      return;
    }
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    let fullText = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const lines = buf.split("\n");
      buf = lines.pop(); // hold back incomplete line
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        let evt;
        try { evt = JSON.parse(line.slice(6)); } catch (_) { continue; }
        if (evt.type === "token") {
          fullText += evt.text;
          // Show text as-is during streaming; SOURCES_JSON line stripped on done
          streamEl.textContent = fullText;
        } else if (evt.type === "done") {
          const cleanText = fullText.replace(/\n*SOURCES_JSON:.*$/s, "").trim();
          answer.innerHTML = renderAnswer({ text: cleanText, sources: evt.sources || [], status: "ok" });
        } else if (evt.type === "error") {
          answer.textContent = evt.text || "Something went wrong. Please try again.";
        }
      }
    }
  } catch (_) {
    answer.textContent = "Could not reach the server. Please try again.";
  }
}

function renderAnswer(data) {
  if (!data || !data.text) return "<p>No answer returned.</p>";
  const text = escapeHtml(data.text);
  const sources = (data.sources || []);
  const pills = sources
    .filter(s => s.label || s.url)
    .map((s, i) => {
      const label = escapeHtml(s.label || `Source ${i + 1}`);
      const href = s.url ? escapeAttr(s.url) : "#";
      const field = s.field ? ` title="${escapeAttr(s.field)}"` : "";
      return `<a class="source-pill" href="${href}" target="_blank" rel="noopener"${field}>${label}</a>`;
    })
    .join("");
  return `<div class="answer-text">${text}</div>${pills ? `<div class="source-pills">${pills}</div>` : ""}`;
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  ask(input.value.trim());
});

presetsEl.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-q]");
  if (!btn) return;
  input.value = btn.dataset.q;
  ask(btn.dataset.q);
});

// ── Voice input ──────────────────────────────────────────────────────────────
const micBtn = document.getElementById("mic-btn");

function startVoice() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    if (micBtn) micBtn.title = "Voice input not supported in this browser";
    return;
  }
  const rec = new SR();
  rec.lang = "en-US";
  rec.interimResults = false;
  rec.maxAlternatives = 1;
  if (micBtn) micBtn.classList.add("recording");
  rec.onresult = (e) => {
    const transcript = e.results[0][0].transcript.trim();
    if (transcript) {
      input.value = transcript;
      ask(transcript);
    }
  };
  rec.onerror = () => { if (micBtn) micBtn.classList.remove("recording"); };
  rec.onend   = () => { if (micBtn) micBtn.classList.remove("recording"); };
  rec.start();
}

if (micBtn) {
  micBtn.addEventListener("click", (e) => { e.preventDefault(); startVoice(); });
}

loadCoverage();
loadPresets();
