# Reel Match — Content-Based Movie Recommender

A Flask + scikit-learn movie recommendation system, built in the same spirit as
: type a movie
you like, get 5 similar ones back, ranked by content similarity.

This is a good portfolio piece for an AI/ML internship because it touches the
full stack in miniature: feature engineering, vectorization, a similarity
metric, a REST API, and a UI — while staying small enough to explain in an
interview in two minutes.

## How it works

1. **Feature soup** — for every movie, `recommender.py` concatenates its
   genres, keywords, top-billed cast, director, and plot overview into one
   "tags" string. Genres and director are repeated to weight them more
   heavily than the free-text overview.
2. **Vectorization** — `TfidfVectorizer` turns each movie's tag string into a
   sparse numeric vector. TF-IDF (rather than plain word counts) matters here:
   it automatically downweights words that appear in *lots* of movies (like
   "action") and upweights words that are rare and distinguishing (like a
   specific director's name).
3. **Similarity** — `cosine_similarity` computes how close every pair of
   movie vectors is. Cosine similarity is standard for this because it
   measures the angle between vectors, not their magnitude — so it isn't
   biased by longer or shorter overviews.
4. **Recommend** — given a title, look up its row, sort every other movie by
   similarity score, return the top N.

This is the same "content-based filtering" pattern used by CineMatch and most
TMDB-5000 tutorials, just re-implemented from scratch with a bit of extra
feature weighting.

## Project structure

```
movie-recommender/
├── app.py                  # Flask routes + API
├── recommender.py          # Feature engineering + similarity engine
├── requirements.txt
├── data/
│   └── movies_sample.csv   # 50-movie demo dataset (swap for TMDB 5000, see below)
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Run it locally

```bash
cd movie-recommender
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:7860**.

## API

- `GET /api/titles` — all movie titles, used for the search box's autocomplete.
- `GET /api/recommend?title=Inception&n=5` — returns the top-N similar movies
  as JSON: `{"query": "...", "results": [{"title", "genres", "director",
  "overview", "score"}, ...]}`.

## Upgrading to the full TMDB 5000 dataset

The demo ships with 50 hand-picked movies so it runs instantly with no
external downloads. To use the same ~5,000-movie dataset as the original
CineMatch:

1. Download `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` from Kaggle
   (search "TMDB 5000 Movie Dataset").
2. Merge them on `id`/`movie_id`, and build a CSV with these columns:
   `movie_id, title, genres, keywords, cast, director, overview`.
   The raw TMDB files store `genres`, `keywords`, and `cast` as
   JSON-list-of-dicts strings (e.g. `[{"id":28,"name":"Action"}, ...]`) —
   `recommender.py` already detects and parses that format automatically via
   `_split_multi()`, so you don't need to reformat those columns by hand.
   For `director`, pull the `crew` entry where `job == "Director"`.
3. Save the merged file as `data/movies_full.csv` and set
   `DATA_PATH = "data/movies_full.csv"` at the top of `recommender.py`.

No other code changes are needed — the pipeline is dataset-size agnostic.

## Deploying (e.g. to Hugging Face Spaces, like the original)

1. Create a new Space, SDK = **Docker** (or **Gradio/Static** won't fit a
   Flask app — Docker is simplest).
2. Add a minimal `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   EXPOSE 7860
   CMD ["python", "app.py"]
   ```
3. Push this project to the Space's git repo. HF Spaces expects the app to
   listen on port 7860, which `app.py` already does.

## Ideas to extend (good talking points for interviews)

- **Posters & real images** — call the TMDB API (`/movie/{id}`) with your own
  API key to pull poster URLs and show real artwork in the cards.
- **Hybrid filtering** — blend this content-based score with a
  collaborative-filtering signal (e.g. matrix factorization on user ratings)
  once you have interaction data.
- **Better embeddings** — swap TF-IDF + cosine similarity for sentence
  embeddings (e.g. `sentence-transformers`) on the overview text for
  semantic (not just keyword) matching.
- **Evaluation** — hold out some (user, liked-movie) pairs and measure
  precision@5 / recall@5 to quantify recommendation quality, not just
  eyeball it.
- **Caching** — precompute and persist the similarity matrix (`joblib.dump`)
  instead of rebuilding it on every server start, which matters once the
  dataset is 5,000 rows instead of 50.
