from django.urls import path
from .views import (
    BookSearchView,
    BookDetailView,
    BookSummaryView,
    HomeBooksView,
    UserBookInteractionView,
    UserLibraryView,
    ReviewListCreateView,
    ReviewDetailView,
    UserFavoritesView,
)

urlpatterns = [
    # Public book endpoints
    path("search/", BookSearchView.as_view(), name="book-search"),
    path("details/<str:google_id>/", BookDetailView.as_view(), name="book-detail"),
    path("summary/<int:book_id>/", BookSummaryView.as_view(), name="book-summary"),
    path("home/", HomeBooksView.as_view(), name="home-books"),

    # User interactions (JWT protected)
    path("interactions/", UserBookInteractionView.as_view(), name="user-interaction"),
    path("interactions/my-library/", UserLibraryView.as_view(), name="user-library"),
    path("interactions/favorites/", UserFavoritesView.as_view(), name="user-favorites"),

    # Reviews
    path("books/<int:book_id>/reviews/", ReviewListCreateView.as_view(), name="book-reviews"),
    path("reviews/<int:review_id>/", ReviewDetailView.as_view(), name="review-detail"),
]
