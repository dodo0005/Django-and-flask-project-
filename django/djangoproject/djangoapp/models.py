from django.db import models
from django.contrib.auth.models import User

# Django only stores GAMEPLAY tracking and USER data
# Story content (Story, Page, Choice) is stored ONLY in Flask API


class Play(models.Model):
    """
    Records each time a user completes a story (reaches an ending).
    This is gameplay tracking data, not story content.
    """

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    story_id = models.IntegerField()  # References Flask Story.id
    ending_page_id = models.IntegerField()  # References Flask Page.id
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username}: Story {self.story_id} → Ending {self.ending_page_id}"
        return f"Anonymous: Story {self.story_id} → Ending {self.ending_page_id}"

    class Meta:
        verbose_name_plural = "Plays"


# Level 18: Community features


class Rating(models.Model):
    """User ratings for stories"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story_id = models.IntegerField()  # References Flask Story.id
    rating = models.IntegerField()  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "story_id"]  # One rating per user per story

    def __str__(self):
        return f"{self.user.username} rated Story {self.story_id}: {self.rating}/5"


class Report(models.Model):
    """User reports for inappropriate stories"""

    REASON_CHOICES = [
        ("spam", "Spam"),
        ("offensive", "Offensive Content"),
        ("inappropriate", "Inappropriate"),
        ("copyright", "Copyright Violation"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story_id = models.IntegerField()  # References Flask Story.id
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.user.username} on Story {self.story_id}"
