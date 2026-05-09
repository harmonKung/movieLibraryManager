"""
Movie Library Manager
Lightweight movie tracking system using JSON for persistent storage.
"""

import json
import os
from datetime import datetime
from typing import Optional


DATA_FILE = "movies.json"


# schema

def new_movie(
    title: str,
    year: int,
    genre: str,
    rating: Optional[int] = None,
    status: str = "unwatched",
) -> dict:
    """Return a new movie record conforming to the library schema."""
    if rating is not None and not (1 <= rating <= 5):
        raise ValueError("Rating must be between 1 and 5.")
    if status not in ("watched", "unwatched", "wishlist"):
        raise ValueError("Status must be 'watched', 'unwatched', or 'wishlist'.")
    return {
        "id": None,                     
        "title": title.strip(),
        "year": year,
        "genre": genre.strip(),
        "rating": rating,
        "status": status,
        "added_at": datetime.now().isoformat(timespec="seconds"),
    }


# json

def load_library(path: str = DATA_FILE) -> list[dict]:
    """Read and return all movies from the JSON file."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("movies", [])


def save_library(movies: list[dict], path: str = DATA_FILE) -> None:
    """Persist the full movie list to the JSON file."""
    payload = {
        "schema_version": 1,
        "last_updated": datetime.now().isoformat(timespec="seconds"),
        "movies": movies,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def _next_id(movies: list[dict]) -> int:
    return max((m["id"] for m in movies if m["id"]), default=0) + 1


# add update delete

def add_movie(movie: dict, path: str = DATA_FILE) -> dict:
    """Add a new movie and return it with its assigned id."""
    movies = load_library(path)
    movie["id"] = _next_id(movies)
    movies.append(movie)
    save_library(movies, path)
    return movie


def update_movie(movie_id: int, updates: dict, path: str = DATA_FILE) -> dict:
    """Update fields on an existing movie by id."""
    movies = load_library(path)
    for m in movies:
        if m["id"] == movie_id:
            for key, value in updates.items():
                if key not in ("id", "added_at"):  
                    m[key] = value
            save_library(movies, path)
            return m
    raise KeyError(f"No movie with id {movie_id}.")


def delete_movie(movie_id: int, path: str = DATA_FILE) -> None:
    """Remove a movie from the library by id."""
    movies = load_library(path)
    filtered = [m for m in movies if m["id"] != movie_id]
    if len(filtered) == len(movies):
        raise KeyError(f"No movie with id {movie_id}.")
    save_library(filtered, path)


# Query

def search(query: str, path: str = DATA_FILE) -> list[dict]:
    """Return movies whose title or genre contains the query string (case-insensitive)."""
    q = query.lower()
    return [
        m for m in load_library(path)
        if q in m["title"].lower() or q in m["genre"].lower()
    ]


def filter_by_status(status: str, path: str = DATA_FILE) -> list[dict]:
    """Return all movies matching the given watch status."""
    return [m for m in load_library(path) if m["status"] == status]


def stats(path: str = DATA_FILE) -> dict:
    """Return summary statistics for the library."""
    movies = load_library(path)
    rated = [m for m in movies if m["rating"]]
    return {
        "total": len(movies),
        "watched": sum(1 for m in movies if m["status"] == "watched"),
        "unwatched": sum(1 for m in movies if m["status"] == "unwatched"),
        "wishlist": sum(1 for m in movies if m["status"] == "wishlist"),
        "avg_rating": round(sum(m["rating"] for m in rated) / len(rated), 2) if rated else None,
    }


# demo

if __name__ == "__main__":
    # Seed some movies
    for entry in [
        new_movie("Interstellar", 2014, "Sci-fi", rating=5, status="watched"),
        new_movie("Parasite", 2019, "Thriller", rating=5, status="watched"),
        new_movie("Poor Things", 2023, "Fantasy", status="unwatched"),
        new_movie("Dune: Part Two", 2024, "Sci-fi", rating=4, status="watched"),
        new_movie("The Zone of Interest", 2023, "Drama", status="wishlist"),
    ]:
        add_movie(entry)

    # Update a rating
    update_movie(3, {"rating": 4, "status": "watched"})

    # Print stats
    print("── Library stats ──────────────────────")
    for k, v in stats().items():
        print(f"  {k:<12} {v}")

    # Search
    print("\n── Sci-fi movies ──────────────────────")
    for m in search("sci-fi"):
        stars = "★" * (m["rating"] or 0)
        print(f"  [{m['id']}] {m['title']} ({m['year']})  {stars or '—'}")

    # Show raw JSON
    print("\n── Raw JSON (first record) ────────────")
    print(json.dumps(load_library()[0], indent=2))