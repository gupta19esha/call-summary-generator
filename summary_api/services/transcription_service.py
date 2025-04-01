import os
import uuid
import tempfile
from django.conf import settings
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptionService:
    """Service for transcribing audio files with basic speaker segmentation"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Check for required dependencies
        try:
            # Verify ffmpeg is available for pydub
            AudioSegment.ffmpeg.get_ffmpeg_version()
            logger.info("ffmpeg detected successfully")
        except Exception as e:
            logger.error(f"ffmpeg not properly configured: {str(e)}")
            logger.warning("Audio conversion may fail without proper ffmpeg installation")
    
    def _convert_to_wav(self, audio_path, output_path):
        """Convert audio file to WAV format if needed"""
        try:
            logger.info(f"Converting audio: {audio_path} to {output_path}")
            
            # Verify the file exists and is accessible
            if not os.path.exists(audio_path):
                logger.error(f"Audio file does not exist: {audio_path}")
                return False
                
            # Check file permissions
            if not os.access(audio_path, os.R_OK):
                logger.error(f"Cannot read audio file (permission denied): {audio_path}")
                return False
                
            # Get file format from extension
            file_ext = os.path.splitext(audio_path)[1].lower()
            logger.info(f"Detected file extension: {file_ext}")
            
            # Handle different audio formats
            try:
                # Try with format inference first
                audio = AudioSegment.from_file(audio_path)
                logger.info("Successfully loaded audio with format inference")
            except Exception as format_error:
                logger.warning(f"Format inference failed: {str(format_error)}")
                
                # Try with explicit format based on extension
                try:
                    if file_ext == '.mp3':
                        audio = AudioSegment.from_mp3(audio_path)
                    elif file_ext == '.wav':
                        audio = AudioSegment.from_wav(audio_path)
                    elif file_ext == '.ogg':
                        audio = AudioSegment.from_ogg(audio_path)
                    elif file_ext == '.flac':
                        audio = AudioSegment.from_file(audio_path, "flac")
                    elif file_ext in ['.m4a', '.aac']:
                        audio = AudioSegment.from_file(audio_path, "aac")
                    else:
                        # Last resort - try raw format with default parameters
                        audio = AudioSegment.from_file(audio_path, format="raw", 
                                                      frame_rate=44100, channels=2, sample_width=2)
                    logger.info(f"Successfully loaded audio with explicit format: {file_ext}")
                except Exception as explicit_error:
                    logger.error(f"Explicit format loading failed: {str(explicit_error)}")
                    return False
            
            # Process the audio
            audio = audio.set_channels(1)  # Convert to mono
            audio = audio.set_frame_rate(16000)  # Set frame rate to 16kHz
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Export to WAV
            audio.export(output_path, format="wav")
            
            # Verify the output file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Successfully converted audio to: {output_path}")
                return True
            else:
                logger.error(f"Conversion failed - output file empty or missing: {output_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error converting audio: {str(e)}", exc_info=True)
            return False
    
    def _segment_audio(self, audio_path):
        """Split audio on silence to create rough speaker segments"""
        try:
            logger.info(f"Segmenting audio: {audio_path}")
            audio = AudioSegment.from_file(audio_path)
            
            # Split audio where silence is 700ms or more and get chunks
            chunks = split_on_silence(
                audio, 
                min_silence_len=700,
                silence_thresh=audio.dBFS-16,
                keep_silence=500
            )
            
            logger.info(f"Successfully segmented audio into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error segmenting audio: {str(e)}", exc_info=True)
            return []
    
    def transcribe_audio(self, audio_path):
        """
        Transcribe audio file with basic speaker segmentation.
        
        audio_path: Path to the audio file (string)
        """
        try:
            logger.info(f"Starting transcription for: {audio_path}")
            
            # Create a more accessible directory for temporary files
            temp_dir = os.path.join(os.path.dirname(os.path.dirname(audio_path)), 'temp_audio')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Convert to WAV if needed
            wav_filename = f"{uuid.uuid4()}.wav"
            wav_path = os.path.join(temp_dir, wav_filename)
            
            logger.info(f"Converting audio from {audio_path} to {wav_path}")
            conversion_success = self._convert_to_wav(audio_path, wav_path)
            
            if not conversion_success:
                logger.error("Audio conversion failed")
                return {
                    'full_transcription': "Failed to convert audio to a processable format.",
                    'segments': []
                }
            
            # Get audio segments
            logger.info(f"Segmenting audio from {wav_path}")
            audio_chunks = self._segment_audio(wav_path)
            
            if not audio_chunks:
                logger.error("Audio segmentation failed or no segments detected")
                return {
                    'full_transcription': "Failed to segment audio or no audio chunks detected.",
                    'segments': []
                }
            
            transcript_with_speakers = []
            current_speaker = 1
            chunk_files = []
            
            # Process each audio chunk
            for i, chunk in enumerate(audio_chunks):
                # Export the audio chunk to a file
                chunk_filename = f"{uuid.uuid4()}_chunk_{i}.wav"
                chunk_path = os.path.join(temp_dir, chunk_filename)
                chunk.export(chunk_path, format="wav")
                chunk_files.append(chunk_path)
                
                # Use SpeechRecognition to transcribe the chunk
                with sr.AudioFile(chunk_path) as source:
                    audio_data = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio_data)
                        if text.strip():  # If transcription is not empty
                            # Alternate speakers for simplified diarization
                            if i > 0 and len(transcript_with_speakers) > 0:
                                # Check if this segment is likely from a different speaker
                                # by checking if there was a significant pause
                                if len(audio_chunks) > 1:  # Only if we have multiple chunks
                                    prev_end = audio_chunks[i-1].duration_seconds
                                    current_start = sum(c.duration_seconds for c in audio_chunks[:i])
                                    if current_start - prev_end > 2:  # If more than 2 seconds silence
                                        current_speaker = 2 if current_speaker == 1 else 1
                            
                            transcript_with_speakers.append({
                                'speaker': f"Speaker {current_speaker}",
                                'text': text
                            })
                            logger.info(f"Transcribed chunk {i}: Speaker {current_speaker}, text length: {len(text)}")
                    except sr.UnknownValueError:
                        # Speech was unintelligible
                        logger.warning(f"Chunk {i}: Speech was unintelligible")
                    except Exception as e:
                        logger.error(f"Error recognizing chunk {i}: {str(e)}")
            
            # Clean up temporary files
            try:
                # Remove WAV file
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
                
                # Remove chunk files
                for chunk_path in chunk_files:
                    if os.path.exists(chunk_path):
                        os.unlink(chunk_path)
                
                logger.info("Temporary files cleaned up successfully")
            except Exception as e:
                logger.warning(f"Warning: Failed to delete some temporary files: {e}")
            
            # Format the full transcription as a string
            formatted_transcription = '\n\n'.join(
                [f"{item['speaker']}: {item['text']}" for item in transcript_with_speakers]
            )
            
            # If no transcription was generated, provide a fallback
            if not formatted_transcription.strip():
                logger.warning("No clear transcription generated")
                formatted_transcription = "No clear speech detected in the audio file."
            else:
                logger.info(f"Successfully transcribed audio, total segments: {len(transcript_with_speakers)}")
            
            return {
                'full_transcription': formatted_transcription,
                'segments': transcript_with_speakers
            }
            
        except Exception as e:
            logger.error(f"Error in transcribe_audio: {str(e)}", exc_info=True)
            # Return a default response in case of error
            return {
                'full_transcription': f"Error processing audio: {str(e)}",
                'segments': []
            }