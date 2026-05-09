"""
Harmon Ung
4/4/2026
Movie Library Manager app
using json for storing data, trying to create a website application
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import movie_library as lib


DATA_FILE = "movies.json"

app = Flask(__name__)

@app.route("/")
def index():
    status_filter = request.args.get("status", "all")
    query = request.args.get("q", "").strip()
    sort = request.args.get("sort", "added")
 
    if query:
        movies = lib.search(query)
    elif status_filter != "all":
        movies = lib.filter_by_status(status_filter)
    else:
        movies = lib.load_library()
 
    if sort == "title":
        movies.sort(key=lambda m: m["title"].lower())
    elif sort == "rating":
        movies.sort(key=lambda m: m["rating"] or 0, reverse=True)
    elif sort == "year":
        movies.sort(key=lambda m: m["year"], reverse=True)
    else:
        movies.sort(key=lambda m: m["id"], reverse=True)
 
    summary = lib.stats()
    return render_template(
        "index.html",
        movies=movies,
        summary=summary,
        status_filter=status_filter,
        query=query,
        sort=sort,
    )
 
 
@app.route("/add", methods=["POST"])
def add():
    rating = request.form.get("rating")
    movie = lib.new_movie(
        title=request.form["title"],
        year=int(request.form["year"]),
        genre=request.form["genre"],
        rating=int(rating) if rating else None,
        status=request.form.get("status", "unwatched"),
    )
    lib.add_movie(movie)
    return redirect(url_for("index"))
 
 
@app.route("/edit/<int:movie_id>", methods=["POST"])
def edit(movie_id):
    rating = request.form.get("rating")
    lib.update_movie(movie_id, {
        "title": request.form["title"],
        "year": int(request.form["year"]),
        "genre": request.form["genre"],
        "rating": int(rating) if rating else None,
        "status": request.form.get("status", "unwatched"),
    })
    return redirect(url_for("index"))
 
 
@app.route("/delete/<int:movie_id>", methods=["POST"])
def delete(movie_id):
    lib.delete_movie(movie_id)
    return redirect(url_for("index"))
 
 
@app.route("/toggle/<int:movie_id>", methods=["POST"])
def toggle(movie_id):
    movies = lib.load_library()
    movie = next((m for m in movies if m["id"] == movie_id), None)
    if movie:
        new_status = "unwatched" if movie["status"] == "watched" else "watched"
        lib.update_movie(movie_id, {"status": new_status})
    return redirect(request.referrer or url_for("index"))
 
 
if __name__ == "__main__":
    app.run(debug=True)