from rest_framework import serializers
from .models import Book, UserBookInteraction, Review


# -----------------------------------
# Book Serializers
# -----------------------------------

class BookSerializer(serializers.Serializer):
    """
    Serializer for normalized external API books (Google Books, NYT).
    This matches the unified schema returned by services.py.
    """
    google_id = serializers.CharField(allow_null=True, required=False)
    title = serializers.CharField()
    authors = serializers.ListField(child=serializers.CharField(), default=[])
    published_date = serializers.CharField(allow_null=True, required=False)
    categories = serializers.ListField(child=serializers.CharField(), default=[])
    thumbnail = serializers.URLField(allow_null=True, required=False)
    description = serializers.CharField(allow_null=True, required=False)
    average_rating = serializers.FloatField(allow_null=True, required=False)

    amazon_url = serializers.URLField(allow_null=True, required=False)
    rank = serializers.IntegerField(allow_null=True, required=False)


class BookDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed book info from our local DB model.
    """
    class Meta:
        model = Book
        fields = [
            "google_id",
            "title",
            "authors",
            "published_date",
            "thumbnail_url",
            "short_description",
        ]


# -----------------------------------
# Summary Serializer
# -----------------------------------

class SummarySerializer(serializers.Serializer):
    """
    Serializer for AI-generated summaries.
    """
    summary = serializers.CharField()


# -----------------------------------
# User Interactions
# -----------------------------------

class UserBookInteractionSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserBookInteraction model.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserBookInteraction
        fields = ["user", "book", "status", "is_favorite"]


# -----------------------------------
# Reviews
# -----------------------------------

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for reviews with username display.
    """
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "book", "user", "username", "rating", "comment", "created_at"]
        read_only_fields = ["user", "book"]
