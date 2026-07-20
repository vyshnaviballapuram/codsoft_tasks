/* ==========================================================
   NEXTSTEP — shared content data
   ========================================================== */

const ACTION_VERBS = {
  Leadership: ["Led", "Directed", "Coordinated", "Mentored", "Delegated", "Championed"],
  Achievement: ["Increased", "Reduced", "Achieved", "Exceeded", "Delivered", "Boosted"],
  Technical: ["Built", "Engineered", "Automated", "Deployed", "Optimized", "Debugged"],
  Communication: ["Presented", "Negotiated", "Authored", "Facilitated", "Persuaded", "Documented"]
};

const RESUME_CHECKLIST = [
  "Quantify achievements with numbers, %, or scale",
  "Start every bullet with a strong action verb",
  "Tailor skills and keywords to the job description",
  "Use reverse-chronological order for experience",
  "Keep formatting and tense consistent throughout",
  "Remove personal pronouns (I, me, my)",
  "Keep to one page for early-career roles",
  "Proofread twice — once forward, once backward",
  "Save as PDF unless the employer requests otherwise"
];

const INTERVIEW_QUESTIONS = {
  Behavioral: [
    { q: "Tell me about a time you faced a conflict with a teammate.", tip: "Use STAR. Focus on how you listened, found common ground, and what the outcome was — not who was 'right'." },
    { q: "Describe a time you failed at something.", tip: "Pick a real, moderate failure. Spend most of the answer on what you learned and changed afterward." },
    { q: "Tell me about a time you went above and beyond.", tip: "Choose an example with a measurable result — time saved, revenue impact, a problem prevented." },
    { q: "Describe a situation where you had to persuade someone.", tip: "Show that you listened to their concerns first, then explain the evidence or reasoning that shifted their view." },
    { q: "Tell me about a time you managed multiple priorities.", tip: "Explain your prioritization method (impact, urgency, dependencies) rather than just listing tasks." }
  ],
  Technical: [
    { q: "Walk me through how you'd approach a problem you've never seen before.", tip: "Narrate your process: clarify requirements, break it down, consider edge cases, then implement and test." },
    { q: "How do you decide between two possible solutions?", tip: "Mention trade-offs explicitly — performance, maintainability, time constraints — rather than picking on instinct alone." },
    { q: "How do you keep your skills up to date?", tip: "Name specific habits: courses, projects, communities, reading source docs — generic answers ('I read blogs') read as weak." },
    { q: "Describe your debugging process.", tip: "Reproduce → isolate → hypothesize → test → fix → verify. Mention a real example if you can." },
    { q: "How do you handle code or work you disagree with?", tip: "Show you raise concerns constructively with reasoning, and can commit once a decision is made." }
  ],
  Situational: [
    { q: "What would you do if you disagreed with your manager's decision?", tip: "Show you'd raise it privately with reasoning, then support the final call professionally." },
    { q: "How would you handle an unclear or shifting deadline?", tip: "Emphasize early communication, clarifying scope, and flagging risk before it becomes a crisis." },
    { q: "What would you do in your first 30 days on this job?", tip: "Structure it: listen and learn, identify quick wins, build relationships, set a longer-term plan." },
    { q: "How would you handle receiving harsh feedback?", tip: "Show you separate the feedback from your ego, ask clarifying questions, and act on it." },
    { q: "What would you do if you noticed a mistake after a project shipped?", tip: "Prioritize transparency: flag it immediately, propose a fix, and note how to prevent recurrence." }
  ]
};

const MOCK_QUESTIONS = Object.entries(INTERVIEW_QUESTIONS).flatMap(([category, list]) =>
  list.map(item => ({ category, ...item }))
);

const STAR_STEPS = [
  { letter: "S", title: "Situation", body: "Set the scene briefly — where, when, what was at stake." },
  { letter: "T", title: "Task", body: "State your specific responsibility or goal in that situation." },
  { letter: "A", title: "Action", body: "Explain exactly what you did — focus on your contribution." },
  { letter: "R", title: "Result", body: "Share the outcome, ideally with a number or measurable impact." }
];
