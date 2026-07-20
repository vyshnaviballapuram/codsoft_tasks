"""
recommender.py
--------------
Content-based movie recommendation engine.

How it works (classic "CineMatch"-style approach):
1. Load a movie dataset with title, genres, keywords, cast, director, overview.
2. Build a single "tags" string per movie by combining all of those fields.
3. Vectorize the tags with CountVectorizer (bag-of-words).
4. Compute cosine similarity between every pair of movies.
5. To recommend, find the movie's row, sort other movies by similarity score,
   and return the top N.

This mirrors the standard TMDB-5000-based recommender pattern. Swap in the
full TMDB 5000 dataset (see README) by pointing DATA_PATH at your merged
movies+credits CSV with the same column names.
"""

import ast
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = "data/movies_sample.csv"


def _clean(text: str) -> str:
    """Lowercase and strip non-alphanumeric characters for consistent tokens."""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _split_multi(value: str) -> str:
    """
    Handles two possible source formats:
    - simple ';' or ' ' separated strings (our sample CSV), e.g. "Action Crime"
    - JSON-list-of-dicts strings, as found in the raw TMDB 5000 CSV files,
      e.g. "[{'id': 28, 'name': 'Action'}, ...]"
    Returns a plain space-joined string either way.
    """
    if isinstance(value, str) and value.strip().startswith("["):
        try:
            items = ast.literal_eval(value)
            return " ".join(d.get("name", "") for d in items if isinstance(d, dict))
        except (ValueError, SyntaxError):
            return value
    return str(value).replace(";", " ")


class MovieRecommender:
    def __init__(self, data_path: str = DATA_PATH, top_cast: int = 3):
        self.data_path = data_path
        self.top_cast = top_cast
        self.df = None
        self.similarity = None
        self._build()

    def _build(self):
        df = pd.read_csv(self.data_path)

        # Normalize expected columns; missing ones become empty strings.
        for col in ["genres", "keywords", "cast", "director", "overview"]:
            if col not in df.columns:
                df[col] = ""
            df[col] = df[col].fillna("")

        df["genres_clean"] = df["genres"].apply(_split_multi)
        df["keywords_clean"] = df["keywords"].apply(_split_multi)

        def top_n_cast(value):
            # cast is ';'-separated names (may contain spaces), handle directly
            if isinstance(value, str) and value.strip().startswith("["):
                try:
                    items = ast.literal_eval(value)
                    people = [d.get("name", "") for d in items if isinstance(d, dict)]
                except (ValueError, SyntaxError):
                    people = []
            else:
                people = [p.strip() for p in str(value).split(";") if p.strip()]
            people = people[: self.top_cast]
            return " ".join(p.replace(" ", "") for p in people)

        df["cast_clean"] = df["cast"].apply(top_n_cast)
        df["director_clean"] = df["director"].apply(
            lambda v: str(v).replace(" ", "").replace(";", " ")
        )

        # Overview gets light weight (natural language), everything else
        # gets repeated once — this is the standard "soup" approach.
        df["tags"] = (
            df["overview"].apply(_clean)
            + " "
            + df["genres_clean"].apply(_clean)
            + " "
            + df["genres_clean"].apply(_clean)  # weight genres higher
            + " "
            + df["keywords_clean"].apply(_clean)
            + " "
            + df["cast_clean"].apply(_clean)
            + " "
            + df["director_clean"].apply(_clean)
            + " "
            + df["director_clean"].apply(_clean)  # weight director higher
            + " "
            + df["director_clean"].apply(_clean)
        )

        vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        vectors = vectorizer.fit_transform(df["tags"]).toarray()
        self.similarity = cosine_similarity(vectors)
        self.df = df.reset_index(drop=True)

    def titles(self):
        return sorted(self.df["title"].tolist())

    def recommend(self, title: str, n: int = 5):
        matches = self.df[self.df["title"].str.lower() == title.strip().lower()]
        if matches.empty:
            # fall back to a loose contains-match
            matches = self.df[
                self.df["title"].str.lower().str.contains(title.strip().lower(), na=False)
            ]
        if matches.empty:
            return None

        idx = matches.index[0]
        scores = list(enumerate(self.similarity[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        scores = [s for s in scores if s[0] != idx][:n]

        results = []
        for i, score in scores:
            row = self.df.iloc[i]
            results.append(
                {
                    "title": row["title"],
                    "genres": row["genres_clean"],
                    "director": row["director"],
                    "overview": row["overview"],
                    "score": round(float(score), 3),
                }
            )
        return {"query": self.df.iloc[idx]["title"], "results": results}


if __name__ == "__main__":
    rec = MovieRecommender()
    print(rec.recommend("Inception"))
