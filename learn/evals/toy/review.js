const state = { traces: [], annotations: {} };
let saveTimer;

const escapeHtml = (s) =>
  s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const hasAnnotation = (a) => Boolean(a && (a.mode || a.note));

async function init() {
  try {
    const [traces, annotations] = await Promise.all([
      fetch('/api/traces').then((r) => r.json()),
      fetch('/api/annotations').then((r) => r.json()),
    ]);
    state.traces = traces;
    state.annotations = annotations || {};
  } catch {
    document.getElementById('status').textContent = '載入失敗：請先跑 python3 learn/evals/toy/review.py';
    return;
  }
  render();
}

function render() {
  const list = document.getElementById('traces');
  const tpl = document.getElementById('trace-template');
  list.innerHTML = '';

  for (const trace of state.traces) {
    const node = tpl.content.cloneNode(true);
    const card = node.querySelector('.trace');
    card.dataset.id = trace.id;

    node.querySelector('.tid').textContent = trace.id;
    node.querySelector('.meta').textContent = [
      trace.meta.intent,
      trace.meta.clarity,
      `${trace.meta.party} 位`,
      trace.meta.day,
      trace.meta.time,
    ]
      .filter(Boolean)
      .join(' · ');

    const [user, assistant] = trace.turns;
    node.querySelector('.user .content').textContent = user.content;
    node.querySelector('.assistant .content').textContent = assistant.content;

    const annotation = state.annotations[trace.id] || {};
    const mode = node.querySelector('.mode');
    const note = node.querySelector('.note');
    const saved = node.querySelector('.saved');
    mode.value = annotation.mode || '';
    note.value = annotation.note || '';

    const update = () => {
      const value = { mode: mode.value.trim(), note: note.value.trim() };
      if (value.mode || value.note) state.annotations[trace.id] = value;
      else delete state.annotations[trace.id];
      saved.textContent = '…';
      clearTimeout(saveTimer);
      saveTimer = setTimeout(() => save(saved), 500);
      updateProgress();
      renderModes();
    };

    mode.addEventListener('input', update);
    note.addEventListener('input', update);
    list.appendChild(node);
  }

  document.getElementById('status').textContent = `${state.traces.length} traces 已載入`;
  updateProgress();
  renderModes();
}

async function save(indicator) {
  try {
    const res = await fetch('/api/annotations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state.annotations),
    });
    indicator.textContent = res.ok ? '已存' : '存檔失敗';
  } catch {
    indicator.textContent = '存檔失敗';
  }
  setTimeout(() => { indicator.textContent = ''; }, 1200);
}

function updateProgress() {
  const done = state.traces.filter((t) => hasAnnotation(state.annotations[t.id])).length;
  const total = state.traces.length;
  document.getElementById('progress-text').textContent = `${done} / ${total}`;
  document.getElementById('progress-bar').style.width = total ? `${(done / total) * 100}%` : '0';
}

function modesOf(annotation) {
  return (annotation?.mode || '')
    .split(/[、,]/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function renderModes() {
  const counts = new Map();
  for (const trace of state.traces) {
    for (const mode of modesOf(state.annotations[trace.id])) {
      counts.set(mode, (counts.get(mode) || 0) + 1);
    }
  }

  const list = document.getElementById('modes');
  list.innerHTML = '';
  for (const [mode, count] of [...counts.entries()].sort((a, b) => b[1] - a[1])) {
    const li = document.createElement('li');
    li.innerHTML = `<span>${escapeHtml(mode)}</span><b>${count}</b>`;
    list.appendChild(li);
  }

  document.getElementById('mode-list').innerHTML = [...counts.keys()]
    .map((mode) => `<option value="${escapeHtml(mode)}">`)
    .join('');
}

document.getElementById('next').addEventListener('click', () => {
  const next = state.traces.find((t) => !hasAnnotation(state.annotations[t.id]));
  if (next) document.querySelector(`[data-id="${next.id}"]`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  else document.getElementById('status').textContent = '全部標完了';
});

init();
