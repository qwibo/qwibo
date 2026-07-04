const labels = {
  asr: { pct: "pct-asr", fill: "fill-asr", hint: "hint-asr" },
  qwen: { pct: "pct-qwen", fill: "fill-qwen", hint: "hint-qwen" },
};

function setProgress(id, pct, mb, hint) {
  const L = labels[id];
  if (!L) return;
  document.getElementById(L.pct).textContent = `${pct}%` + (mb ? ` · ${mb} MB` : "");
  document.getElementById(L.fill).style.width = `${Math.min(100, pct)}%`;
  if (hint) document.getElementById(L.hint).textContent = hint;
}

function setSkip(id, reason) {
  const L = labels[id];
  if (!L) return;
  document.getElementById(L.pct).textContent = "Non necessario";
  document.getElementById(L.fill).style.width = "100%";
  document.getElementById(L.fill).style.background = "#475569";
  document.getElementById(L.hint).innerHTML = `<span class="skip">${reason}</span>`;
}

function showError(msg) {
  const el = document.getElementById("err");
  el.style.display = "block";
  el.textContent = msg;
  document.getElementById("spin").style.display = "none";
}

function showDone() {
  document.getElementById("panel-active").style.display = "none";
  document.getElementById("panel-done").style.display = "block";
}

if (window.setupApi) {
  window.setupApi.onProgress((data) => {
    if (data.event === "phase") {
      setProgress(data.id, 0, 0, data.label);
    } else if (data.event === "progress") {
      setProgress(data.id, data.pct, data.mb, "");
    } else if (data.event === "skip") {
      setSkip(data.id, data.reason);
    } else if (data.event === "done") {
      setProgress(data.id, 100, null, "Completato");
    } else if (data.event === "complete") {
      showDone();
    } else if (data.event === "error") {
      showError(data.message);
    }
  });
}
