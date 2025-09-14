from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Book, UserBookInteraction, Review
from .serializers import (
    BookSerializer,
    BookDetailSerializer,
    UserBookInteractionSerializer,
    ReviewSerializer,
)
from .services import (
    search_google_books,
    normalize_google_book,
    get_or_create_book_details,
    generate_and_cache_ai_summary,
    get_genre_top_books,
    get_recent_books,
    get_bestsellers
)
from .permissions import IsOwnerOrReadOnly


# -------------------------------
# Book Search
# -------------------------------
class BookSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.GET.get("q", "")
        if not query:
            return Response({"error": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        data = search_google_books(query)
        if not data or "items" not in data:
            return Response({"books": []})

        books = [normalize_google_book(item) for item in data.get("items", [])]
        return Response({"books": books})


# -------------------------------
# Book Details
# -------------------------------
class BookDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, google_id):
        book = get_or_create_book_details(google_id)
        if not book:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookDetailSerializer(book)
        return Response(serializer.data)


# -------------------------------
# AI Summary
# -------------------------------
class BookSummaryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, book_id):
        summary = generate_and_cache_ai_summary(book_id)
        return Response({"summary": summary})


# -------------------------------
# Home / Genre Top / Recent / Bestseller Books
# -------------------------------
class HomeBooksView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "carousel": get_genre_top_books(limit=10),
            "recent": get_recent_books(limit=10),
            "bestsellers": get_bestsellers(limit=10)
        })


# -------------------------------
# UserBookInteraction
# -------------------------------
class UserBookInteractionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UserBookInteractionSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        book_id = request.data.get("book_id")
        if not book_id:
            return Response({"error": "book_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            interaction = UserBookInteraction.objects.get(user=request.user, book_id=book_id)
        except UserBookInteraction.DoesNotExist:
            return Response({"error": "Interaction not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserBookInteractionSerializer(
            interaction, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# Reviews
# -------------------------------
class ReviewListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, book_id):
        serializer = ReviewSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user, book_id=book_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, review_id):
        return get_object_or_404(Review, id=review_id)

    def put(self, request, review_id):
        review = self.get_object(review_id)
        self.check_object_permissions(request, review)
        serializer = ReviewSerializer(review, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, review_id):
        review = self.get_object(review_id)
        self.check_object_permissions(request, review)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------------
# User Library & Favorites
# -------------------------------
class UserLibraryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        interactions = UserBookInteraction.objects.filter(user=request.user)
        data = []
        for interaction in interactions:
            book = interaction.book
            data.append({
                "id": book.id,
                "google_id": book.google_id,
                "title": book.title,
                "authors": book.authors,
                "published_date": book.published_date,
                "thumbnail_url": book.thumbnail_url,
                "short_description": book.short_description,
                "status": interaction.status,
                "is_favorite": interaction.is_favorite,
            })
        return Response({"library": data})


class UserFavoritesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        favorites = UserBookInteraction.objects.filter(user=request.user, is_favorite=True)
        data = []
        for interaction in favorites:
            book = interaction.book
            data.append({
                "id": book.id,
                "google_id": book.google_id,
                "title": book.title,
                "authors": book.authors,
                "published_date": book.published_date,
                "thumbnail_url": book.thumbnail_url,
                "short_description": book.short_description,
                "status": interaction.status,
                "is_favorite": interaction.is_favorite,
            })
        return Response({"favorites": data})
