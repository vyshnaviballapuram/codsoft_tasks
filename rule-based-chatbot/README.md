# NextStep — Resume & Interview Prep Hub, Guided by RuleBot

A rule-based chatbot ("build a chatbot that responds to user inputs based on predefined rules, using if-else statements or pattern matching") — wrapped in a full career-prep web application instead of a bare demo.

**RuleBot** answers questions using ordered regex-based intents, no machine learning involved. It appears as a floating widget on every page and as a full chat experience with a live pattern-trace panel.

## Features

- **Resume Toolkit** (`resume.html`)
  - Interactive checklist with a live progress bar
  - Categorized action-verb bank — click any verb to copy it
  - A rule-based bullet-point analyzer that checks your resume bullets for action verbs, quantifiers, passive phrasing, and length
- **Interview Practice** (`interview.html`)
  - STAR method explainer
  - Flip-card question bank across Behavioral / Technical / Situational categories, each with an answer-structuring tip
- **Ask RuleBot** (`chatbot.html`)
  - Full chat page with a grouped intent sidebar, live engine stats, and a "show pattern trace" toggle that reveals exactly which regex/intent produced each reply
- **Floating widget** — RuleBot is reachable from every page via a bottom-right chat bubble, with page-aware quick-reply suggestions
- **About** (`about.html`) — write-up of how the rule engine works, for portfolio/interview talking points

## Tech stack

Plain HTML5, CSS3, and vanilla JavaScript. No frameworks, no build step, no external APIs. The "NLP" is entirely regular-expression pattern matching plus simple entity extraction (e.g. pulling a name out of "my name is Alex").

## Project structure

```
nextstep/
├── index.html            Home
├── resume.html           Checklist, verb bank, bullet analyzer
├── interview.html        STAR method, flip-card question bank
├── chatbot.html          Full RuleBot chat page
├── about.html            Project write-up
├── css/
│   └── styles.css        Shared design system (nav, cards, chat, widget)
├── js/
│   ├── data.js            Content: action verbs, checklist, question bank
│   ├── chatbot-engine.js  Shared rule-based matching engine (RULES, rbMatch)
│   ├── widget.js          Floating chat widget (loaded on every page)
│   ├── chat-page.js       Logic specific to the full chat page
│   └── main.js            Nav highlighting, checklist, analyzer, flip cards
└── README.md
```

## Running it

No build tools needed — it's a static site.

- **Locally:** open `index.html` directly in a browser, or serve the folder with any static server, e.g.:
  ```bash
  npx serve .
  # or
  python3 -m http.server 8000
  ```
- **Deploying:** push the folder to GitHub and enable GitHub Pages (Settings → Pages → Deploy from branch), or drag the folder into Netlify/Vercel.

## How the rule engine works

Every user message is tested, in order, against a list of intents defined in `js/chatbot-engine.js`. Each intent owns one or more regular expressions; the first pattern that matches wins, and its handler produces the reply. Some handlers extract data straight from the sentence — for example, capturing a name from `"my name is Alex"`, or parsing a math expression like `"12 * 4"`. There is no model and no network call involved, so matches typically resolve in well under a millisecond — visible live in the chat page's stats panel.

## Possible extensions

- Persist checklist/chat progress with a backend or `IndexedDB`
- Add more intents (cover letter review, salary calculator by region)
- Swap the rule engine for a hybrid rules + small ML classifier to compare approaches
- Add unit tests for `rbMatch()` against a labeled set of sample messages

## Author's note

Built as a portfolio-ready internship deliverable — the emphasis throughout was on making the rule-based approach *transparent* (via the pattern-trace toggle) rather than hiding it, since demonstrating an understanding of how pattern matching works was the actual point of the assignment.
