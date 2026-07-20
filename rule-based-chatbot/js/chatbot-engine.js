/* ==========================================================
   RULEBOT ENGINE — pure pattern matching, no ML
   Ordered intents, each backed by one or more regex patterns.
   The first confident match produces a reply.
   ========================================================== */

const RB = { userName: null, turns: 0 };

function rbPick(arr){ return arr[Math.floor(Math.random() * arr.length)]; }

function rbMathOp(text){
  const cleaned = text
    .replace(/\bplus\b/gi, '+')
    .replace(/\bminus\b/gi, '-')
    .replace(/\b(times|multiplied by|x)\b/gi, '*')
    .replace(/\bdivided by\b/gi, '/');
  const match = cleaned.match(/(-?\d+(\.\d+)?)\s*([+\-*/])\s*(-?\d+(\.\d+)?)/);
  if(!match) return null;
  const a = parseFloat(match[1]);
  const op = match[3];
  const b = parseFloat(match[4]);
  let result;
  switch(op){
    case '+': result = a + b; break;
    case '-': result = a - b; break;
    case '*': result = a * b; break;
    case '/': result = b === 0 ? null : a / b; break;
  }
  return result === null ? 'undefined (division by zero)' : Math.round(result * 10000) / 10000;
}

const RULES = [
  // ---------------- General / small talk ----------------
  { group:'General', intent:'greeting', patterns:[/\b(hi|hello|hey|hola|yo|sup|howdy)\b/i, /\bgood (morning|afternoon|evening)\b/i],
    handle:() => rbPick(["Hey there! Looking for resume help, interview practice, or just chatting?","Hello! Ask me about resumes, interviews, or tap a suggestion below.","Hi! What can I help you prep for today?"]) },
  { group:'General', intent:'farewell', patterns:[/\b(bye|goodbye|see ya|see you|farewell|catch you later)\b/i],
    handle:() => rbPick(["Good luck out there!","See you later — good luck with the prep.","Bye for now!"]) },
  { group:'General', intent:'thanks', patterns:[/\b(thanks|thank you|thx|appreciate it|cheers)\b/i],
    handle:() => rbPick(["You're welcome!","Anytime — good luck!","Happy to help."]) },
  { group:'General', intent:'set_name', patterns:[/\b(?:my name is|call me|i'?m called)\s+([a-zA-Z]{2,20})/i],
    handle:(m) => { RB.userName = m[1][0].toUpperCase() + m[1].slice(1).toLowerCase(); return `Nice to meet you, ${RB.userName}! I'll remember that for this session.`; } },
  { group:'General', intent:'get_name', patterns:[/\bwhat(?:'s| is) my name\b/i],
    handle:() => RB.userName ? `You told me your name is ${RB.userName}.` : "You haven't told me your name yet — try \"my name is ...\"." },
  { group:'General', intent:'bot_identity', patterns:[/\bwho are you\b/i, /\bwhat are you\b/i, /\byour name\b/i],
    handle:() => "I'm RuleBot — NextStep's rule-based prep guide. No machine learning, just pattern matching against your message." },
  { group:'General', intent:'capabilities', patterns:[/\b(help|what can you do|your (features|capabilities)|commands)\b/i],
    handle:() => "I can help with resume tips, action verbs, ATS advice, interview tips, the STAR method, and mock interview questions. I also do small talk, time/date, jokes, and quick math. Try the chips below." },
  { group:'General', intent:'how_are_you', patterns:[/\bhow are you\b/i, /\bhow('?s| is) it going\b/i, /\bwhat'?s up\b/i],
    handle:() => rbPick(["Running smoothly, thanks! How's your prep going?","All rules firing correctly! How are you feeling about your search?"]) },
  { group:'General', intent:'mood_negative', patterns:[/\bi(?:'?m| am) (sad|tired|upset|stressed|anxious|nervous|not (?:ok|okay|good|great))\b/i],
    handle:() => "That's understandable — job searching is genuinely stressful. Take it one step at a time; even 10 minutes of prep counts. Want a quick, low-pressure interview question to warm up with?" },
  { group:'General', intent:'mood_positive', patterns:[/\bi(?:'?m| am) (good|great|fine|happy|excellent|okay|ok|ready|confident)\b/i],
    handle:() => rbPick(["Love that energy — let's put it to use.","Great! Want to jump into a mock question or a resume check?"]) },
  { group:'General', intent:'compliment', patterns:[/\byou(?:'?re| are) (great|awesome|smart|cool|amazing|helpful)\b/i],
    handle:() => "Thank you! That's kind of you to say." },
  { group:'General', intent:'insult', patterns:[/\b(stupid|dumb|useless|idiot)\b/i],
    handle:() => "I'm simple by design — just pattern matching — but I'll keep trying to be useful." },
  { group:'General', intent:'time', patterns:[/\b(what(?:'s| is) the time|current time|what time is it)\b/i],
    handle:() => `It's currently ${new Date().toLocaleTimeString()} on your device.` },
  { group:'General', intent:'date', patterns:[/\b(what(?:'s| is) the date|today'?s date|what day is it)\b/i],
    handle:() => `Today is ${new Date().toDateString()}.` },
  { group:'General', intent:'joke', patterns:[/\b(joke|make me laugh|say something funny)\b/i],
    handle:() => rbPick(["Why do programmers prefer dark mode? Because light attracts bugs.","I told the interviewer I was 'detail-oriented' — then misspelled it on my resume.","Why did the developer go broke? They used up all their cache."]) },
  { group:'General', intent:'math', patterns:[/-?\d+(\.\d+)?\s*(\+|\-|\*|\/|plus|minus|times|multiplied by|divided by|x)\s*-?\d+(\.\d+)?/i],
    handle:(m, raw) => { const r = rbMathOp(raw); return r !== null ? `That equals ${r}.` : "Try a format like \"12 * 4\" or \"9 divided by 3\"."; } },
  { group:'General', intent:'weather', patterns:[/\bweather\b/i],
    handle:() => "No live weather feed here — I'm pattern-matching only. But I'm glad to help with prep instead!" },

  // ---------------- Resume ----------------
  { group:'Resume', intent:'resume_tips', patterns:[/\b(resume tips|resume advice|improve my resume|resume help)\b/i],
    handle:() => "Three quick wins: (1) quantify results with numbers, (2) open bullets with strong action verbs, (3) mirror keywords from the job post. Full checklist and tools → the Resume page." },
  { group:'Resume', intent:'action_verbs', patterns:[/\baction verbs?\b/i],
    handle:() => "Strong picks: Led, Launched, Reduced, Streamlined, Negotiated, Automated. Browse the full categorized bank on the Resume page — click any verb to copy it." },
  { group:'Resume', intent:'ats', patterns:[/\b(ats|applicant tracking system)\b/i],
    handle:() => "For ATS: use standard section headings, avoid tables/text boxes/images for key info, match keywords from the job description, and submit as a PDF unless told otherwise." },
  { group:'Resume', intent:'cover_letter', patterns:[/\bcover letter\b/i],
    handle:() => "Keep it to 3 short paragraphs: a specific hook on why this role, evidence you're a fit (1-2 concrete examples), and a confident close. Avoid repeating your resume verbatim." },

  // ---------------- Interview ----------------
  { group:'Interview', intent:'interview_tips', patterns:[/\b(interview tips|interview advice|interview help)\b/i],
    handle:() => "Research the company, prepare 2-3 STAR stories you can adapt, have questions ready to ask them, and do a tech/audio check early if it's remote. Practice out loud, not just in your head." },
  { group:'Interview', intent:'star_method', patterns:[/\bstar method\b/i],
    handle:() => "STAR = Situation, Task, Action, Result. Set the scene briefly, state your specific responsibility, explain what you did, then share the measurable outcome. See the full breakdown on the Interview page." },
  { group:'Interview', intent:'tell_me_about_yourself', patterns:[/\btell me about yourself\b/i],
    handle:() => "Structure it present → past → future: what you do now, the relevant experience that got you here, and why this role is the logical next step. Aim for 60-90 seconds." },
  { group:'Interview', intent:'weakness_q', patterns:[/\b(greatest weakness|my weakness(es)?)\b/i],
    handle:() => "Pick a real but non-critical weakness, then show the concrete steps you're taking to improve it. Avoid disguised strengths like \"I work too hard.\"" },
  { group:'Interview', intent:'strength_q', patterns:[/\b(greatest strength|my strength(s)?)\b/i],
    handle:() => "Choose a strength that's actually relevant to the role, and back it with one specific example or result — don't just state the trait." },
  { group:'Interview', intent:'salary_negotiation', patterns:[/\bsalary|negotiat/i],
    handle:() => "Research the market range first. If possible, let them name a number first. Negotiate the whole package — base, bonus, equity, PTO — not just salary." },
  { group:'Interview', intent:'thank_you_note', patterns:[/\bthank you (email|note|letter)\b/i],
    handle:() => "Send it within 24 hours. Keep it short, personalize one detail from the conversation, and briefly reaffirm your interest in the role." },
  { group:'Interview', intent:'mock_question', patterns:[/\b(mock question|practice question|give me a( interview)? question|ask me a( interview)? question)\b/i],
    handle:() => { const item = rbPick(MOCK_QUESTIONS); return `[${item.category}] ${item.q}\n\nTip: ${item.tip}`; } },
];

const FALLBACKS = [
  "I didn't catch a pattern I recognize. Try rephrasing, or tap a suggestion below.",
  "That's outside my rule set. Try asking about resumes, interviews, or type \"help\".",
  "I'm not sure how to match that yet. The suggestion chips are a good starting point.",
];

function rbMatch(raw){
  RB.turns++;
  for(const rule of RULES){
    for(const pattern of rule.patterns){
      const m = raw.match(pattern);
      if(m){
        return { intent: rule.intent, group: rule.group, patternSource: pattern.toString(), response: rule.handle(m, raw) };
      }
    }
  }
  return { intent: 'fallback', group:'General', patternSource: '(no pattern matched)', response: rbPick(FALLBACKS) };
}
