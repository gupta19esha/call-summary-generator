from rest_framework import serializers
from .models import AudioSummary

class AudioSummaryInputSerializer(serializers.ModelSerializer):
    """Serializer for audio file input"""
    class Meta:
        model = AudioSummary
        fields = ('audio_file',)

class AudioSummaryOutputSerializer(serializers.ModelSerializer):
    """Serializer for audio summary output"""
    class Meta:
        model = AudioSummary
        fields = ('id', 'summary', 'title_suggestions', 'transcription', 'created_at')
        read_only_fields = ('id', 'summary', 'title_suggestions', 'transcription', 'created_at')