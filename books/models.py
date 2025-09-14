from django.conf import settings
from django.db import models

class Book(models.Model):
    google_id = models.CharField(max_length=100, unique=True, primary_key=True)
    title = models.CharField(max_length=255)
    authors = models.JSONField(default=list) 
    published_date = models.CharField(max_length=20, null=True, blank=True)
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True)
    full_description = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True) # For the AI summary on page load
    ai_summary = models.TextField(null=True, blank=True) # For the on-demand AI summary

    def __str__(self):
        return self.title


class UserBookInteraction(models.Model):
    class Status(models.TextChoices):
        WANT_TO_READ = 'WTR', 'Want to Read'
        READING = 'RDG', 'Reading'
        READ = 'RD', 'Read'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='interactions')
    status = models.CharField(
        max_length=3, 
        choices=Status.choices, 
        null=True, 
        blank=True
    )
    is_favorite = models.BooleanField(default=False)
    
    class Meta:
        # Ensures a user can only have one interaction entry per book
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField() # e.g., 1 to 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensures a user can only write one review per book
        unique_together = ('user', 'book')

    def __str__(self):
        return f'Review for {self.book.title} by {self.user.username}'