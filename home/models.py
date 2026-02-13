from django.db import models


class ContactSubmission(models.Model):
    """Stores contact form submissions from the Contact Us page."""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'} ({self.created_at:%Y-%m-%d})"
