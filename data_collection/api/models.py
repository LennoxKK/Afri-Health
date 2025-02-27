from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()

class Category(models.Model):
    """Represents a category such as Malaria, Cholera, or Heat Stress."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Added created_at field

    def __str__(self):
        return str(self.name)


class Question(models.Model):
    """Represents a question linked to a category."""
    category = models.ForeignKey(Category, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  # Added created_at field

    def __str__(self):
        return str(self.text)


class Option(models.Model):
    """Represents an option for a question."""
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  # Added created_at field

    def __str__(self):
        return str(self.text)


class Response(models.Model):
    """Represents a user's response to a question."""
    user = models.ForeignKey(User, related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', related_name='responses', on_delete=models.CASCADE)
    selected_option = models.ForeignKey('Option', related_name='responses', on_delete=models.CASCADE)
    location = models.CharField(max_length=255, null=True, blank=True)  # New field for place name
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.question} - {self.selected_option} - {self.location}"

