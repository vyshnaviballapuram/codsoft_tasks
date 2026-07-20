/* ==========================================================
   NEXTSTEP — shared page interactions
   ========================================================== */

// ---- Nav: active link + mobile toggle ----
document.addEventListener('DOMContentLoaded', () => {
  const path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a[data-page]').forEach(a => {
    if(a.getAttribute('data-page') === path) a.classList.add('active');
  });
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if(toggle && links){
    toggle.addEventListener('click', () => links.classList.toggle('open'));
  }

  initChecklist();
  initVerbBank();
  initAnalyzer();
  initFlipCards();
  initStar();
});

// ---- Resume checklist ----
function initChecklist(){
  const list = document.getElementById('resumeChecklist');
  if(!list) return;
  list.innerHTML = RESUME_CHECKLIST.map((item, i) =>
    `<li data-i="${i}"><span class="check-box">✓</span><span class="label">${item}</span></li>`
  ).join('');

  const fill = document.getElementById('progressFill');
  const label = document.getElementById('progressLabel');

  function updateProgress(){
    const total = list.children.length;
    const done = list.querySelectorAll('li.done').length;
    fill.style.width = `${(done/total)*100}%`;
    label.textContent = `${done} / ${total} complete`;
  }

  list.querySelectorAll('li').forEach(li => {
    li.addEventListener('click', () => { li.classList.toggle('done'); updateProgress(); });
  });
  updateProgress();
}

// ---- Action verb bank (click to copy) ----
function initVerbBank(){
  const container = document.getElementById('verbBank');
  if(!container) return;
  container.innerHTML = Object.entries(ACTION_VERBS).map(([cat, verbs]) => `
    <div class="verb-cat">
      <h4>${cat}</h4>
      <div class="chip-grid">
        ${verbs.map(v => `<div class="chip" data-verb="${v}">${v}</div>`).join('')}
      </div>
    </div>
  `).join('');

  container.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', async () => {
      const verb = chip.getAttribute('data-verb');
      try {
        await navigator.clipboard.writeText(verb);
        const original = chip.textContent;
        chip.textContent = 'Copied!';
        chip.classList.add('copied');
        setTimeout(() => { chip.textContent = original; chip.classList.remove('copied'); }, 1000);
      } catch(e){ /* clipboard unavailable — silently ignore */ }
    });
  });
}

// ---- Resume bullet analyzer (rule-based text check) ----
function analyzeBullet(text){
  const trimmed = text.trim();
  const allVerbs = Object.values(ACTION_VERBS).flat().map(v => v.toLowerCase());
  const firstWord = trimmed.split(/\s+/)[0]?.toLowerCase().replace(/[^a-z]/g, '') || '';

  const checks = [
    { label: 'Starts with a strong action verb', pass: allVerbs.includes(firstWord) },
    { label: 'Contains a number, %, or metric', pass: /\d/.test(trimmed) },
    { label: 'Avoids personal pronouns (I, me, my)', pass: !/\b(i|me|my)\b/i.test(trimmed) },
    { label: 'Avoids passive phrasing ("responsible for")', pass: !/responsible for|duties included|worked on/i.test(trimmed) },
    { label: 'Reasonable length (under ~220 characters)', pass: trimmed.length > 0 && trimmed.length <= 220 },
  ];
  return checks;
}

function initAnalyzer(){
  const textarea = document.getElementById('bulletInput');
  const btn = document.getElementById('analyzeBtn');
  const results = document.getElementById('analyzerResults');
  if(!textarea || !btn) return;

  btn.addEventListener('click', () => {
    const text = textarea.value.trim();
    if(!text){ results.classList.remove('show'); return; }
    const checks = analyzeBullet(text);
    results.innerHTML = checks.map(c =>
      `<div class="result-row ${c.pass ? 'pass' : 'fail'}"><span class="mark">${c.pass ? '✓' : '✕'}</span><span>${c.label}</span></div>`
    ).join('');
    results.classList.add('show');
  });
}

// ---- Interview flip cards ----
function initFlipCards(){
  const grid = document.getElementById('flipGrid');
  const tabs = document.getElementById('flipTabs');
  if(!grid || !tabs) return;

  const categories = Object.keys(INTERVIEW_QUESTIONS);
  tabs.innerHTML = categories.map((c, i) => `<div class="flip-tab ${i===0?'active':''}" data-cat="${c}">${c}</div>`).join('');

  function renderCategory(cat){
    grid.innerHTML = INTERVIEW_QUESTIONS[cat].map((item, i) => `
      <div class="flip-card" data-idx="${i}">
        <div class="flip-inner">
          <div class="flip-face flip-front">
            <span class="cat-tag">${cat}</span>
            <p>${item.q}</p>
          </div>
          <div class="flip-face flip-back">
            <span class="tip-label">How to approach it</span>
            <p>${item.tip}</p>
          </div>
        </div>
      </div>
    `).join('');
    grid.querySelectorAll('.flip-card').forEach(card => {
      card.addEventListener('click', () => card.classList.toggle('flipped'));
    });
  }

  tabs.querySelectorAll('.flip-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.querySelectorAll('.flip-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      renderCategory(tab.getAttribute('data-cat'));
    });
  });

  renderCategory(categories[0]);
}

// ---- STAR method cards ----
function initStar(){
  const grid = document.getElementById('starGrid');
  if(!grid) return;
  grid.innerHTML = STAR_STEPS.map(s => `
    <div class="star-item">
      <div class="letter">${s.letter}</div>
      <h4>${s.title}</h4>
      <p>${s.body}</p>
    </div>
  `).join('');
}
