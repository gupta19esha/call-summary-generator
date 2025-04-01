from django.db import models
import uuid
import os

def audio_file_path(instance, filename):
    """Generate file path for new audio file"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/audio/', filename)

class AudioSummary(models.Model):
    """Model for storing audio summaries"""
    audio_file = models.FileField(upload_to=audio_file_path)
    transcription = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    title_suggestions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Audio Summary {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"