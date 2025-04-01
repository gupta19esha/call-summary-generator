from django.conf import settings
import google.generativeai as genai
import os

class SummarizationService:
    """Service for summarizing transcriptions using Google's Gemini API"""
    
    def __init__(self):
        # Try getting from settings first
        self.api_key = settings.GEMINI_API_KEY
        
        # If not available, try getting directly from environment
        if not self.api_key:
            self.api_key = os.environ.get('GEMINI_API_KEY')
        
        # If still not available, use hardcoded key temporarily for testing
        if not self.api_key:
            # Fallback to hardcoded key - ONLY FOR TEMPORARY TESTING
            self.api_key = "AIzaSyDa6uDmBSTPuEkcz3lUEWv4P7KoW7A-T9k"
            print("WARNING: Using hardcoded API key for Gemini - this should be removed in production")
        
        print(f"Configuring Gemini with API key: {self.api_key[:5]}...")
        genai.configure(api_key=self.api_key)
        
        # Configure the model
        generation_config = {
            "temperature": 0.4,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        try:
            # Try the primary model name format
            self.model = genai.GenerativeModel('gemini-1.5-pro', generation_config=generation_config)
        except Exception as e:
            print(f"Error with primary model name, trying fallback: {str(e)}")
            try:
                # Try fallback model
                self.model = genai.GenerativeModel('gemini-pro-vision', generation_config=generation_config)
            except Exception as e2:
                print(f"Error with fallback model: {str(e2)}")
                # Final fallback to whatever models are available
                available_models = genai.list_models()
                for model in available_models:
                    if 'gemini' in model.name.lower() and model.supported_generation_methods:
                        if 'generateContent' in model.supported_generation_methods:
                            print(f"Using available model: {model.name}")
                            self.model = genai.GenerativeModel(model.name, generation_config=generation_config)
                            break
    
    def summarize_transcription(self, transcription):
        """
        Generate a concise summary from a transcription.
        
        Args:
            transcription: The full transcription text with speaker information
            
        Returns:
            A concise summary of the key discussion points
        """
        try:
            # Define prompt for summarization
            prompt = f"""
            You are an AI that creates concise, structured summaries of meetings and conversations.
            Extract the key points and important information from the transcription provided.
            Organize the summary into clear sections with bullet points for easy readability.
            Focus on action items, decisions made, and important discussions.
            Do not include unnecessary details or pleasantries.
            
            Here is the meeting transcript to summarize:
            
            {transcription}
            """
            
            # Generate the summary using Gemini
            response = self.model.generate_content(prompt)
            
            # Extract and return the summary
            summary = response.text.strip()
            return summary
            
        except Exception as e:
            print(f"Error in summarize_transcription: {str(e)}")
            # Return a default summary in case of error
            return f"Error generating summary: {str(e)}"
    
    def generate_title_suggestions(self, transcription, summary):
        """
        Generate title suggestions for the meeting summary.
        
        Args:
            transcription: The full transcription text
            summary: The generated summary
            
        Returns:
            A list of 3 suggested titles
        """
        try:
            # Define prompt for title generation
            prompt = f"""
            You are an AI that creates concise, descriptive titles for meeting summaries.
            Each title should be short (under 8 words) but descriptive enough to distinguish this meeting
            from others. Focus on the main topic or decision from the meeting.
            
            Generate exactly 3 different title suggestions for this meeting. The titles should be
            descriptive and specific to the content discussed.
            
            Summary of the meeting:
            {summary}
            
            Full transcript (beginning):
            {transcription[:1000]}...
            
            Return just the 3 titles, numbered 1, 2, and 3, with no additional explanation.
            """
            
            # Generate the titles using Gemini
            response = self.model.generate_content(prompt)
            
            # Extract and process the titles
            titles_text = response.text.strip()
            
            # Parse the titles - assuming they're numbered
            titles = []
            for line in titles_text.split('\n'):
                # Remove leading numbers, dashes, etc.
                cleaned_line = line.strip()
                if cleaned_line:
                    # Remove numbered list markers (1., 2., etc.) or bullet points
                    if cleaned_line[0].isdigit() and cleaned_line[1:].startswith('. '):
                        cleaned_line = cleaned_line[3:].strip()
                    elif cleaned_line.startswith('- '):
                        cleaned_line = cleaned_line[2:].strip()
                    # Remove quotation marks if present
                    cleaned_line = cleaned_line.strip('"\'')
                    if cleaned_line:
                        titles.append(cleaned_line)
            
            # Take the first 3 titles (or fewer if less than 3 were generated)
            return titles[:3]
            
        except Exception as e:
            print(f"Error in generate_title_suggestions: {str(e)}")
            # Return default titles in case of error
            return ["Meeting Summary", "Discussion Overview", "Conversation Recap"]