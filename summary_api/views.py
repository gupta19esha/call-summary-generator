from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
import os
from django.conf import settings

from .models import AudioSummary
from .serializers import AudioSummaryInputSerializer, AudioSummaryOutputSerializer
from .services.transcription_service import TranscriptionService
from .services.summarization_service import SummarizationService

class GenerateSummaryView(APIView):
    """API view for generating summaries from audio files"""
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests to process audio files and generate summaries"""
        try:
            # Check if audio file is in the request
            if 'audio_file' not in request.FILES:
                return Response(
                    {'error': 'No audio file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate input data
            serializer = AudioSummaryInputSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid input', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create a new audio summary record
            audio_summary = serializer.save()
            
            # Create a more accessible directory for Windows
            upload_dir = os.path.join(os.path.dirname(settings.BASE_DIR), 'uploaded_files')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the file to our accessible directory
            audio_file = request.FILES['audio_file']
            file_path = os.path.join(upload_dir, f"{audio_summary.id}_{audio_file.name}")
            with open(file_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            
            # 1. Transcribe the audio file using the file path, not the file object
            transcription_service = TranscriptionService()
            transcription_result = transcription_service.transcribe_audio(file_path)
            
            # Get the full transcription text
            transcription_text = transcription_result['full_transcription']
            
            # Check if transcription was successful
            if not transcription_text.strip():
                return Response(
                    {'error': 'Transcription failed. The audio might be unclear or in an unsupported format.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 2. Summarize the transcription
            summarization_service = SummarizationService()
            summary = summarization_service.summarize_transcription(transcription_text)
            
            # 3. Generate title suggestions
            titles = summarization_service.generate_title_suggestions(transcription_text, summary)
            
            # Update the audio summary record with results
            audio_summary.transcription = transcription_text
            audio_summary.summary = summary
            audio_summary.title_suggestions = titles
            audio_summary.save()
            
            # Return the processed data
            output_serializer = AudioSummaryOutputSerializer(audio_summary)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Log the error
            import traceback
            print(f"Error in GenerateSummaryView: {str(e)}")
            print(traceback.format_exc())
            
            # Return error response
            return Response(
                {'error': 'An error occurred while processing the audio file', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SimpleUploadTestView(APIView):
    """Simple test view for file uploads"""
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests to test file uploads"""
        if 'audio_file' not in request.FILES:
            return JsonResponse({'error': 'No audio_file in request'}, status=400)
            
        audio_file = request.FILES['audio_file']
        
        # Create a more accessible directory for Windows
        upload_dir = os.path.join(os.path.dirname(settings.BASE_DIR), 'uploaded_files')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_dir, audio_file.name)
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            
            return JsonResponse({
                'success': True,
                'file_name': audio_file.name,
                'file_size': audio_file.size,
                'saved_to': file_path
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)