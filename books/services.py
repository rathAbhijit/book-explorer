import requests
from django.conf import settings
from django.core.cache import cache
from .models import Book
import openai

# -------------------------------
# External API helpers
# -------------------------------

def search_google_books(query, max_results=20):
    """Query the Google Books API with a search term."""
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": max_results,
        "key": getattr(settings, "GOOGLE_BOOKS_API_KEY", None),
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code != 200:
        return None
    return response.json()


def get_google_book_details(google_id):
    """Get details for a specific book by Google ID."""
    url = f"https://www.googleapis.com/books/v1/volumes/{google_id}"
    params = {"key": getattr(settings, "GOOGLE_BOOKS_API_KEY", None)}
    response = requests.get(url, params=params, timeout=10)
    if response.status_code != 200:
        return None
    return response.json()


def get_nyt_bestsellers(list_name="hardcover-fiction", limit=10):
    """Get NYT bestseller list."""
    url = f"https://api.nytimes.com/svc/books/v3/lists/current/{list_name}.json"
    params = {"api-key": getattr(settings, "NYT_BOOKS_API_KEY", None)}
    response = requests.get(url, params=params, timeout=10)
    if response.status_code != 200:
        return []
    data = response.json()
    return data.get("results", {}).get("books", [])[:limit]


# -------------------------------
# Normalizers (Google + NYT)
# -------------------------------

def normalize_google_book(item):
    """Normalize Google Books API item into unified schema."""
    volume = item.get("volumeInfo", {})
    return {
        "google_id": item.get("id"),
        "title": volume.get("title", "Unknown Title"),
        "authors": volume.get("authors", []),
        "published_date": volume.get("publishedDate"),
        "categories": volume.get("categories", []),
        "thumbnail": (volume.get("imageLinks", {}) or {}).get("thumbnail"),
        "description": volume.get("description"),
        "average_rating": volume.get("averageRating"),
        "amazon_url": None,
        "rank": None,
    }


def normalize_nyt_book(item):
    """Normalize NYT bestseller book into unified schema."""
    return {
        "google_id": None,
        "title": item.get("title"),
        "authors": [item.get("author")] if item.get("author") else [],
        "published_date": None,
        "categories": [item.get("list_name")] if item.get("list_name") else [],
        "thumbnail": item.get("book_image"),
        "description": item.get("description"),
        "average_rating": None,
        "amazon_url": item.get("amazon_product_url"),
        "rank": item.get("rank"),
    }


# -------------------------------
# DB caching / get_or_create
# -------------------------------

def get_or_create_book_details(google_id):
    """Check DB for book; fetch from Google if missing."""
    try:
        return Book.objects.get(google_id=google_id)
    except Book.DoesNotExist:
        data = get_google_book_details(google_id)
        if not data or "volumeInfo" not in data:
            return None
        volume = data.get("volumeInfo", {})
        book = Book.objects.create(
            google_id=data.get("id"),
            title=volume.get("title", "Unknown Title"),
            authors=volume.get("authors", []),
            published_date=volume.get("publishedDate"),
            categories=volume.get("categories", []),
            thumbnail=volume.get("imageLinks", {}).get("thumbnail"),
            description=volume.get("description", ""),
            average_rating=volume.get("averageRating")
        )
        return book


# -------------------------------
# High-level business logic
# -------------------------------

def get_genre_top_books(limit=10):
    """Get top book from each genre (Google Books)."""
    genres = [
        "Fiction", "Science", "History", "Biography", "Fantasy",
        "Romance", "Mystery", "Self-Help", "Technology", "Philosophy",
    ]
    books = []
    for genre in genres[:limit]:
        data = search_google_books(genre, max_results=1)
        if data and "items" in data:
            books.append(normalize_google_book(data["items"][0]))
    return books


def get_recent_books(limit=10):
    """Get recently published books (Google Books)."""
    data = search_google_books("subject:fiction", max_results=limit)
    if not data:
        return []
    return [normalize_google_book(item) for item in data.get("items", [])]


def get_bestsellers(limit=10):
    """Get bestseller books (NYT)."""
    books = get_nyt_bestsellers(limit=limit)
    return [normalize_nyt_book(item) for item in books]


# -------------------------------
# AI Summary (OpenAI / caching)
# -------------------------------

def generate_and_cache_ai_summary(book_id):
    """Generate spoiler-free AI summary and cache it."""
    cache_key = f"book_summary_{book_id}"
    summary = cache.get(cache_key)
    if summary:
        return summary

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return "Summary not available."

    prompt = (
        f"Write a spoiler-free, concise summary for the book titled '{book.title}' "
        f"by {', '.join(book.authors or ['Unknown Author'])}."
    )

    openai.api_key = getattr(settings, "OPENAI_API_KEY", None)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        summary = response.choices[0].message.content.strip()
    except Exception:
        summary = "Summary not available due to API error."

    cache.set(cache_key, summary, 60 * 60 * 24)  # 24 hours cache
    return summary
