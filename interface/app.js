const form = document.getElementById('tammyForm');
const input = document.getElementById('tammyInput');
const title = document.getElementById('judgementTitle');
const body = document.getElementById('judgementBody');
const modes = [...document.querySelectorAll('.mode')];
const workItems = [...document.querySelectorAll('.work-item')];
const expand = document.getElementById('expandJudgement');

let activeMode = 'Analyse';

const responses = {
  Analyse: {
    title: 'The issue isn’t the two documents. It’s the gateway and the reasoning sequence between them.',
    body: 'CARE captures the live contact and immediate reasoning well. The Secondary Clinical Assessment adds useful depth when change or uncertainty remains after initial engagement. The current gateway is present but could be more explicit and consistent.'
  },
  Compare: {
    title: 'CARE and Secondary Assessment are doing different jobs, but the boundary between those jobs is still too porous.',
    body: 'The strongest design is not to make the documents mirror each other. CARE should establish the live picture and whether unresolved change, uncertainty or foreseeable deterioration warrants deeper assessment; Secondary should then add formulation depth rather than repeat the first contact.'
  },
  Challenge: {
    title: 'The weak point is the assumption that staff will infer the gateway consistently from two otherwise coherent documents.',
    body: 'If the threshold is only implicit, two counsellors can hear the same presentation and make different decisions about whether CARE is sufficient. The challenge is therefore calibration of judgement, not adding another checklist.'
  },
  Decide: {
    title: 'The decision is whether the gateway becomes an explicit clinical rule or remains a matter of professional judgement supported by examples.',
    body: 'A useful decision would preserve professional judgement while making the minimum trigger set visible: material change, unresolved uncertainty, complexity, foreseeable deterioration, or a need for a more developed formulation than CARE can reasonably hold.'
  }
};

modes.forEach(button => {
  button.addEventListener('click', () => {
    modes.forEach(m => m.classList.remove('active'));
    button.classList.add('active');
    activeMode = button.dataset.mode;
    title.textContent = responses[activeMode].title;
    body.textContent = responses[activeMode].body;
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

form.addEventListener('submit', event => {
  event.preventDefault();
  const request = input.value.trim();
  if (!request) return;

  const base = responses[activeMode];
  title.textContent = `${activeMode}: ${request}`;
  body.textContent = `${base.body} This interface prototype is not yet connected to the live Tammy intelligence runtime, so no programme state has been read or changed.`;
  input.value = '';
});

expand.addEventListener('click', () => {
  const expanded = expand.dataset.expanded === 'true';
  expand.dataset.expanded = String(!expanded);
  expand.textContent = expanded ? 'View full judgement ›' : 'Collapse judgement ↑';
  body.textContent = expanded
    ? responses[activeMode].body
    : `${responses[activeMode].body} Evidence should remain visible as evidence, inference as inference, and consequential changes should remain proposals until a human decision is recorded.`;
});
