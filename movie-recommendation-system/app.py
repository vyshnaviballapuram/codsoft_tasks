"""
app.py
------
Flask web server for the CineMatch-style movie recommender.

Routes:
  GET  /                -> renders the search UI
  GET  /api/titles       -> list of all movie titles (for autocomplete)
  GET  /api/recommend?title=<name>&n=<count> -> JSON recommendations
"""

from flask import Flask, jsonify, render_template, request

from recommender import MovieRecommender

app = Flask(__name__)
recommender = MovieRecommender()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/titles")
def api_titles():
    return jsonify(recommender.titles())


@app.route("/api/recommend")
def api_recommend():
    title = request.args.get("title", "").strip()
    n = request.args.get("n", default=5, type=int)

    if not title:
        return jsonify({"error": "Please provide a 'title' query parameter."}), 400

    result = recommender.recommend(title, n=n)
    if result is None:
        return jsonify({"error": f"No movie found matching '{title}'."}), 404

    return jsonify(result)


if __name__ == "__main__":
    # host=0.0.0.0 so it also runs correctly inside containers / HF Spaces
    import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)), debug=False)
