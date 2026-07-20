/* ==========================================================
   RULEBOT — full chat page logic
   ========================================================== */

const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const chipsEl = document.getElementById('chips');
const traceToggle = document.getElementById('traceToggle');
const statTurns = document.getElementById('statTurns');

let traceOn = false;

function renderIntentList(){
  const list = document.getElementById('intentList');
  const groups = {};
  RULES.forEach(r => { (groups[r.group] = groups[r.group] || new Set()).add(r.intent); });
  let html = '';
  Object.keys(groups).forEach(group => {
    html += `<div class="intent-group-label">${group}</div>`;
    html += [...groups[group]].map(name =>
      `<li><span class="dot"></span>${name.replace(/_/g,' ')}</li>`
    ).join('');
  });
  list.innerHTML = html;

  const uniqueIntents = new Set(RULES.map(r => r.intent));
  document.getElementById('statIntents').textContent = uniqueIntents.size;
  const totalPatterns = RULES.reduce((sum, r) => sum + r.patterns.length, 0);
  document.getElementById('statPatterns').textContent = totalPatterns;
}

function addMessage(sender, text, meta){
  const wrap = document.createElement('div');
  wrap.className = `msg ${sender}`;
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  wrap.appendChild(bubble);

  if(sender === 'bot' && meta){
    const trace = document.createElement('div');
    trace.className = 'trace' + (traceOn ? ' show' : '');
    trace.textContent = `intent: ${meta.intent}  →  pattern: ${meta.patternSource}`;
    wrap.appendChild(trace);
  }
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showTyping(){
  const t = document.createElement('div');
  t.className = 'typing';
  t.id = 'typingIndicator';
  t.innerHTML = '<span></span><span></span><span></span>';
  messagesEl.appendChild(t);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}
function hideTyping(){
  const t = document.getElementById('typingIndicator');
  if(t) t.remove();
}

function handleSend(text){
  const value = (text !== undefined ? text : inputEl.value).trim();
  if(!value) return;
  addMessage('user', value);
  inputEl.value = '';
  showTyping();

  const start = performance.now();
  const result = rbMatch(value);
  const elapsed = (performance.now() - start).toFixed(2);
  document.getElementById('statSpeed').textContent = `${elapsed}ms`;
  statTurns.textContent = RB.turns;

  const delay = 320 + Math.random() * 280;
  setTimeout(() => {
    hideTyping();
    addMessage('bot', result.response, result);
  }, delay);
}

sendBtn.addEventListener('click', () => handleSend());
inputEl.addEventListener('keydown', (e) => { if(e.key === 'Enter') handleSend(); });

traceToggle.addEventListener('click', () => {
  traceOn = !traceOn;
  traceToggle.classList.toggle('on', traceOn);
  traceToggle.setAttribute('aria-checked', traceOn);
  document.querySelectorAll('.trace').forEach(el => el.classList.toggle('show', traceOn));
});
traceToggle.addEventListener('keydown', (e) => { if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); traceToggle.click(); } });

const SUGGESTIONS = ["What can you do?", "Resume tips", "Interview tips", "STAR method", "Give me a mock question", "My name is Alex"];
chipsEl.innerHTML = SUGGESTIONS.map(s => `<div class="chip">${s}</div>`).join('');
chipsEl.querySelectorAll('.chip').forEach((chip, i) => {
  chip.addEventListener('click', () => handleSend(SUGGESTIONS[i]));
});

renderIntentList();
addMessage('bot', "Hi! I'm RuleBot — a rule-based guide for resume and interview prep. Ask me something, or tap a suggestion below.", { intent: 'greeting', patternSource: '(session start)' });
inputEl.focus();
