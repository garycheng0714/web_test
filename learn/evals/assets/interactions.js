document.querySelectorAll('[data-quiz]').forEach((quiz) => {
  const feedback = quiz.querySelector('.feedback');
  const answer = quiz.dataset.answer;

  quiz.querySelectorAll('input[type="radio"]').forEach((input) => {
    input.addEventListener('change', () => {
      const ok = input.value === answer;
      feedback.hidden = false;
      feedback.className = 'feedback ' + (ok ? 'ok' : 'no');
      feedback.textContent = (ok ? '答對。' : '再看一次上面的定義。') + quiz.dataset.why;
    });
  });
});

document.querySelectorAll('[data-save]').forEach((box) => {
  const key = 'evals:' + box.dataset.save;
  const fields = [...box.querySelectorAll('input, textarea')];

  try {
    const saved = JSON.parse(localStorage.getItem(key) || '[]');
    fields.forEach((field, i) => { if (saved[i]) field.value = saved[i]; });
  } catch {}

  fields.forEach((field) => {
    field.addEventListener('input', () => {
      try { localStorage.setItem(key, JSON.stringify(fields.map((f) => f.value))); } catch {}
    });
  });

  const copy = box.querySelector('[data-copy]');
  if (!copy) return;

  copy.addEventListener('click', async () => {
    const text = fields.map((f) => f.value.trim()).filter(Boolean).join('\n');
    try {
      await navigator.clipboard.writeText(text);
      copy.textContent = '已複製';
    } catch {
      copy.textContent = '複製失敗，請手動選取';
    }
    setTimeout(() => { copy.textContent = '複製 5 行'; }, 1500);
  });
});
