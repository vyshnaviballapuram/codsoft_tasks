const titleInput = document.getElementById("titleInput");
const searchBtn = document.getElementById("searchBtn");
const statusArea = document.getElementById("statusArea");
const resultsGrid = document.getElementById("results");
const trending = document.getElementById("trending");
const titleList = document.getElementById("titleList");
const marquee = document.querySelector("header.marquee");

const TRENDING_PICKS = ["Inception", "The Dark Knight", "Parasite", "Coco", "The Godfather"];

/* ---------- Signature touches: film grain + cursor spotlight ---------- */
function injectAtmosphere() {
  const grain = document.createElement("div");
  grain.className = "grain-overlay";
  document.body.appendChild(grain);

  if (marquee) {
    const spotlight = document.createElement("div");
    spotlight.className = "spotlight";
    marquee.prepend(spotlight);

    marquee.addEventListener("mousemove", (e) => {
      const rect = marquee.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      spotlight.style.setProperty("--spot-x", `${x}%`);
      spotlight.style.setProperty("--spot-y", `${y}%`);
    });
  }
}

async function loadTitles() {
  try {
    const res = await fetch("/api/titles");
    const titles = await res.json();
    titleList.innerHTML = titles.map((t) => `<option value="${t}"></option>`).join("");
  } catch (err) {
    console.error("Could not load title list", err);
  }
}

function renderTrending() {
  const label = document.createElement("span");
  label.className = "label";
  label.textContent = "Trending:";
  trending.appendChild(label);

  TRENDING_PICKS.forEach((title) => {
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.type = "button";
    chip.textContent = title;
    chip.addEventListener("click", () => {
      titleInput.value = title;
      runSearch();
    });
    trending.appendChild(chip);
  });
}

function setStatus(message, isError = false) {
  statusArea.textContent = message;
  statusArea.classList.toggle("error", isError);
}

function renderEmptyState() {
  resultsGrid.innerHTML = `
    <div class="empty-state" style="grid-column: 1 / -1;">
      <div class="icon">🎞️</div>
      <p>Your recommendations will appear here.</p>
    </div>
  `;
}

function renderSkeletons(count = 5) {
  resultsGrid.innerHTML = Array.from({ length: count })
    .map(
      () => `
      <div class="skeleton-card">
        <div class="skeleton-line w-40"></div>
        <div class="skeleton-line w-70"></div>
        <div class="skeleton-line w-100"></div>
        <div class="skeleton-line w-90"></div>
      </div>
    `
    )
    .join("");
}

/* Builds a small circular progress ring (SVG) showing the match percentage */
function scoreRingMarkup(percent) {
  const radius = 17;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - percent / 100);
  return `
    <div class="score-ring">
      <svg width="42" height="42" viewBox="0 0 42 42">
        <circle class="track" cx="21" cy="21" r="${radius}"></circle>
        <circle
          class="fill"
          cx="21" cy="21" r="${radius}"
          stroke-dasharray="${circumference}"
          stroke-dashoffset="${circumference}"
          data-offset="${offset}"
        ></circle>
      </svg>
      <div class="value">${percent}%</div>
    </div>
  `;
}

function renderResults(data) {
  resultsGrid.innerHTML = "";
  data.results.forEach((movie, i) => {
    const percent = Math.round(movie.score * 100);
    const card = document.createElement("div");
    card.className = "card";
    card.style.setProperty("--i", i);
    card.innerHTML = `
      <div class="card-top">
        <div class="card-meta">${movie.genres || "Unclassified"}</div>
        ${scoreRingMarkup(percent)}
      </div>
      <div class="card-title">${movie.title}</div>
      <div class="card-overview">${movie.overview || "No synopsis available."}</div>
      <div class="card-footer">
        <span class="director">Dir. ${movie.director || "Unknown"}</span>
      </div>
    `;
    resultsGrid.appendChild(card);
  });

  // Animate the score rings in after the cards mount, so the sweep is visible.
  requestAnimationFrame(() => {
    resultsGrid.querySelectorAll(".score-ring .fill").forEach((circle) => {
      const offset = circle.getAttribute("data-offset");
      setTimeout(() => {
        circle.style.strokeDashoffset = offset;
      }, 200);
    });
  });
}

async function runSearch() {
  const title = titleInput.value.trim();
  if (!title) {
    setStatus("Type a movie title to get started.", true);
    return;
  }

  setStatus("Finding matches...");
  renderSkeletons();

  try {
    const res = await fetch(`/api/recommend?title=${encodeURIComponent(title)}&n=5`);
    const data = await res.json();

    if (!res.ok) {
      setStatus(data.error || "Something went wrong.", true);
      renderEmptyState();
      return;
    }

    setStatus(`Because you liked "${data.query}" —`);
    renderResults(data);
  } catch (err) {
    setStatus("Could not reach the server. Is the Flask app running?", true);
    renderEmptyState();
  }
}

searchBtn.addEventListener("click", runSearch);
titleInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") runSearch();
});

injectAtmosphere();
loadTitles();
renderTrending();
renderEmptyState();