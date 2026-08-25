const form = document.getElementById('tammyForm');
const input = document.getElementById('tammyInput');
const title = document.getElementById('judgementTitle');
const body = document.getElementById('judgementBody');
const submitButton = form.querySelector('button[type="submit"]');
const modes = [...document.querySelectorAll('.mode')];
const workItems = [...document.querySelectorAll('.work-item')];
const expand = document.getElementById('expandJudgement');
const insightButtons = [...document.querySelectorAll('.insight')];
const contextTitle = document.querySelector('.context-title');

let activeMode = 'Analyse';
let lastLiveResponse = '';
let lastStructured = null;

const responses = {
  Analyse: { title: 'Ready to analyse.', body: 'Ask Tammy a question. Live reasoning is connected; programme context remains unavailable until bounded Notion retrieval is connected.' },
  Compare: { title: 'Ready to compare.', body: 'Ask Tammy to compare two artefacts, positions or work items. Tammy will separate evidence, inference, contradiction and decisions where the response supports it.' },
  Challenge: { title: 'Ready to challenge.', body: 'Ask Tammy to test assumptions, gaps, risks or contradictions. No programme-state claim will be implied from unavailable context.' },
  Decide: { title: 'Ready to support a decision.', body: 'Ask Tammy for a decision brief. Consequential changes remain proposals until human authority is recorded.' }
};

function setBusy(isBusy) {
  submitButton.disabled = isBusy;
  input.disabled = isBusy;
  submitButton.textContent = isBusy ? '…' : '➤';
}

function cleanJsonFence(text) {
  return text.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '').trim();
}

function parseStructured(text) {
  try {
    const parsed = JSON.parse(cleanJsonFence(text));
    if (!parsed || typeof parsed !== 'object') return null;
    return parsed;
  } catch (_) {
    return null;
  }
}

function list(value) {
  return Array.isArray(value) ? value.filter(Boolean) : [];
}

function renderInsight(button, label, items, emptyText) {
  const strong = button.querySelector('strong');
  const small = button.querySelector('small');
  strong.textContent = label;
  small.textContent = items.length ? `${items.length} item${items.length === 1 ? '' : 's'} identified` : emptyText;
  button.classList.toggle('warn', label.startsWith('Contradictions') && items.length > 0);
}

function renderStructured(data) {
  const judgement = data.judgement || data.summary || data.answer || '';
  title.textContent = data.title || 'Tammy’s judgement';
  body.textContent = judgement || 'Tammy returned a structured response without a judgement.';

  const evidence = list(data.evidence);
  const changes = list(data.changes);
  const contradictions = list(data.contradictions);
  const decisions = list(data.decisions);
  renderInsight(insightButtons[0], 'Evidence · LIVE', evidence, 'No evidence items returned');
  renderInsight(insightButtons[1], 'What changed · LIVE', changes, 'No material change identified');
  renderInsight(insightButtons[2], 'Contradictions · LIVE', contradictions, 'No contradiction identified');
  renderInsight(insightButtons[3], 'Decision needed · LIVE', decisions, 'No human decision identified');

  contextTitle.textContent = 'CONTEXT: RUNTIME RESPONSE · LIVE';
  document.querySelectorAll('.context-card').forEach(card => card.hidden = true);
}

function resetLivePanels() {
  insightButtons.forEach((button, index) => {
    const labels = ['Evidence · WAITING', 'What changed · WAITING', 'Contradictions · WAITING', 'Decision needed · WAITING'];
    button.querySelector('strong').textContent = labels[index];
    button.querySelector('small').textContent = 'Awaiting live response';
  });
  contextTitle.textContent = 'PROGRAMME CONTEXT · NOT CONNECTED';
  document.querySelectorAll('.context-card').forEach(card => card.hidden = false);
}

modes.forEach(button => {
  button.addEventListener('click', () => {
    modes.forEach(m => m.classList.remove('active'));
    button.classList.add('active');
    activeMode = button.dataset.mode;
    lastLiveResponse = '';
    lastStructured = null;
    title.textContent = responses[activeMode].title;
    body.textContent = responses[activeMode].body;
    expand.dataset.expanded = 'false';
    expand.textContent = 'View full judgement ›';
  });
});

workItems.forEach(button => {
  button.addEventListener('click', () => {
    workItems.forEach(item => item.classList.remove('active'));
    button.classList.add('active');
    input.value = `Review ${button.dataset.work}`;
    input.focus();
  });
});

form.addEventListener('submit', async event => {
  event.preventDefault();
  const request = input.value.trim();
  if (!request) return;

  setBusy(true);
  resetLivePanels();
  title.textContent = request;
  body.textContent = `Tammy is ${activeMode.toLowerCase()}ing this against the live runtime…`;
  expand.dataset.expanded = 'false';
  expand.textContent = 'View full judgement ›';

  const contract = `Return ONLY valid JSON with this shape: {"title":"short conclusion","judgement":"clear answer","evidence":["supported evidence only"],"changes":["material changes only"],"contradictions":["unresolved contradictions only"],"decisions":["human decisions required only"],"uncertainty":["important unknowns"],"sources":["sources actually available to you"]}. Never invent programme sources or Notion state. If programme context is unavailable, say so in uncertainty and leave unsupported arrays empty.`;

  try {
    const response = await fetch('/api/tammy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task: `${activeMode}: ${request}\n\n${contract}`, items: [] })
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || data.text || `Tammy API returned ${response.status}`);

    const text = (data.text || '').trim();
    if (!text) throw new Error('Tammy returned no text.');

    lastLiveResponse = text;
    lastStructured = parseStructured(text);
    if (lastStructured) renderStructured(lastStructured);
    else {
      title.textContent = 'Tammy’s judgement';
      body.textContent = text;
      insightButtons.forEach(button => {
        button.querySelector('strong').textContent = button.querySelector('strong').textContent.replace('WAITING', 'UNAVAILABLE');
        button.querySelector('small').textContent = 'Runtime returned unstructured text';
      });
    }
    input.value = '';
  } catch (error) {
    lastLiveResponse = '';
    lastStructured = null;
    title.textContent = 'Live runtime unavailable';
    body.textContent = error.message;
  } finally {
    setBusy(false);
    input.focus();
  }
});

expand.addEventListener('click', () => {
  if (!lastStructured) return;
  const expanded = expand.dataset.expanded === 'true';
  expand.dataset.expanded = String(!expanded);
  expand.textContent = expanded ? 'View full judgement ›' : 'Collapse judgement ↑';
  if (expanded) {
    body.textContent = lastStructured.judgement || lastStructured.summary || '';
    return;
  }
  const uncertainty = list(lastStructured.uncertainty);
  body.textContent = `${lastStructured.judgement || ''}${uncertainty.length ? `\n\nUncertainty: ${uncertainty.join(' · ')}` : ''}`;
});
