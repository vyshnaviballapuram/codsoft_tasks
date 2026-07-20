/* ==========================================================
   RULEBOT WIDGET — floating assistant, included on every page
   ========================================================== */

(function(){
  const page = document.body.getAttribute('data-page') || 'default';

  const CHIP_SETS = {
    resume:   ["resume tips", "action verbs", "ats tips"],
    interview:["interview tips", "star method", "mock question"],
    default:  ["what can you do?", "resume tips", "interview tips"]
  };
  const chips = CHIP_SETS[page] || CHIP_SETS.default;

  // ---- inject markup ----
  const btn = document.createElement('button');
  btn.id = 'rb-widget-btn';
  btn.innerHTML = '💬 Ask RuleBot';
  document.body.appendChild(btn);

  const panel = document.createElement('div');
  panel.id = 'rb-widget-panel';
  panel.className = 'chat-wrap';
  panel.innerHTML = `
    <div class="chat-head">
      <div class="avatar">🤖</div>
      <div class="info">
        <b>RuleBot</b>
        <span><span class="status-dot"></span>pattern matching active</span>
      </div>
      <button class="close-btn" aria-label="Close chat">✕</button>
    </div>
    <div class="messages" id="rb-w-messages"></div>
    <div class="chips" id="rb-w-chips"></div>
    <div class="input-row">
      <input id="rb-w-input" type="text" placeholder="Ask about resumes, interviews…" autocomplete="off" />
      <button class="send-btn" id="rb-w-send">Send</button>
    </div>
  `;
  document.body.appendChild(panel);

  const messagesEl = panel.querySelector('#rb-w-messages');
  const inputEl = panel.querySelector('#rb-w-input');
  const sendBtn = panel.querySelector('#rb-w-send');
  const chipsEl = panel.querySelector('#rb-w-chips');
  const closeBtn = panel.querySelector('.close-btn');

  function addMsg(sender, text){
    const wrap = document.createElement('div');
    wrap.className = `msg ${sender}`;
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    wrap.appendChild(bubble);
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }
  function showTyping(){
    const t = document.createElement('div');
    t.className = 'typing';
    t.id = 'rb-w-typing';
    t.innerHTML = '<span></span><span></span><span></span>';
    messagesEl.appendChild(t);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }
  function hideTyping(){
    const t = document.getElementById('rb-w-typing');
    if(t) t.remove();
  }
  function send(text){
    const value = (text || inputEl.value).trim();
    if(!value) return;
    addMsg('user', value);
    inputEl.value = '';
    showTyping();
    const result = rbMatch(value);
    const delay = 320 + Math.random() * 280;
    setTimeout(() => { hideTyping(); addMsg('bot', result.response); }, delay);
  }

  sendBtn.addEventListener('click', () => send());
  inputEl.addEventListener('keydown', (e) => { if(e.key === 'Enter') send(); });
  closeBtn.addEventListener('click', () => panel.classList.remove('open'));
  btn.addEventListener('click', () => {
    panel.classList.toggle('open');
    if(panel.classList.contains('open')) inputEl.focus();
  });

  chipsEl.innerHTML = chips.map(c => `<div class="chip">${c}</div>`).join('');
  chipsEl.querySelectorAll('.chip').forEach((chip, i) => {
    chip.addEventListener('click', () => send(chips[i]));
  });

  addMsg('bot', "Hi! I'm RuleBot. Ask me about resumes, interviews, or tap a suggestion below.");
})();
