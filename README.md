# AI-Powered Call Summary Generator

A Django-based application that automatically generates concise, structured summaries from audio recordings of conversations or meetings. The application uses AI transcription with basic speaker identification to identify speakers, summarize key discussion points, and suggest potential report titles.

## Features

- **Audio-to-Summary Conversion**: Accepts audio recordings, transcribes them with speaker identification, and summarizes key points.
- **Title Suggestions**: Generates 3 AI-powered summary titles that encapsulate the essence of the meeting.
- **File Upload Testing**: Simple endpoint to verify file uploads are working correctly.

## Technology Stack

- **Backend**: Django with Django REST Framework
- **Transcription**: SpeechRecognition library with Google's free speech recognition API
- **Audio Processing**: pydub for audio segmentation and speaker identification
- **AI Summarization**: Google's Gemini AI API for summarization and title generation

## Prerequisites

- Python 3.8 or higher
- Django 4.2 or higher
- API key for Google's Gemini AI (for summarization and title generation)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/call-summary-generator.git
   cd call-summary-generator
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env.local` file in the project root directory with the following content:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   GEMINI_API_KEY=your-gemini-api-key
   ```
   Note: You can obtain a free Gemini API key from https://makersuite.google.com/

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Usage

> **>>> IMPORTANT: For best results, use WAV format audio files!** 
> The application works most reliably with WAV files. If you have MP3 or other formats, 
> please convert them to WAV before uploading for the most accurate transcription.

### 1. Test File Upload Endpoint

This is a simple endpoint to test that file uploads are working correctly.

**Endpoint:** `POST /api/test-upload/`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `audio_file`: The audio file to upload (WAV format recommended)

**Response:**
```json
{
  "success": true,
  "file_name": "recording.wav",
  "file_size": 200448,
  "saved_to": "C:\\Users\\Username\\uploaded_files\\recording.wav"
}
```

### 2. Generate Summary Endpoint

This is the main endpoint for generating summaries from audio files.

**Endpoint:** `POST /api/generate-summary/`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `audio_file`: The audio file to process (WAV format recommended)

**Response:**
```json
{
  "id": 1,
  "summary": "## Meeting Overview\n- Discussion about Q2 marketing strategy\n- Budget allocation for new product launch\n- Team responsibilities and deadlines\n\n## Key Decisions\n- Increase social media budget by 20%\n- Launch new product on July 15th\n- Sarah to lead the marketing campaign\n\n## Action Items\n- John: Finalize budget by Friday\n- Sarah: Prepare campaign outline by Monday\n- Team: Review marketing materials by Wednesday",
  "title_suggestions": [
    "Q2 Marketing Strategy and Product Launch",
    "July Product Launch Planning Meeting",
    "Marketing Budget and Campaign Assignment"
  ],
  "transcription": "Speaker 1: Good morning everyone. Let's get started with our marketing meeting.\n\nSpeaker 2: I've prepared the Q2 strategy document as we discussed last time.\n\nSpeaker 1: Great, let's go through the budget allocation first...",
  "created_at": "2025-04-01T12:34:56.789Z"
}
```

## Testing the API (Recommended Method)

The most reliable way to test this API is using the HTML form below, which has been thoroughly tested and confirmed to work with this application:

1. Create a file named `test.html` with the following content:
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Audio Upload Test</title>
       <style>
           body {
               font-family: Arial, sans-serif;
               max-width: 800px;
               margin: 0 auto;
               padding: 20px;
           }
           .container {
               display: flex;
               flex-direction: column;
               gap: 20px;
           }
           .test-form {
               border: 1px solid #ccc;
               padding: 20px;
               border-radius: 5px;
           }
           h2 {
               margin-top: 0;
           }
           button {
               padding: 10px 15px;
               background-color: #4CAF50;
               color: white;
               border: none;
               border-radius: 4px;
               cursor: pointer;
           }
           button:hover {
               background-color: #45a049;
           }
           .important-note {
               background-color: #ffe0e0;
               border-left: 4px solid #ff5252;
               padding: 10px 15px;
               margin-bottom: 20px;
           }
       </style>
   </head>
   <body>
       <div class="container">
           <h1>Audio Upload Testing</h1>
           
           <div class="important-note">
               <strong>Important:</strong> For best results, please use WAV format audio files. Other formats may cause processing errors.
           </div>
           
           <div class="test-form">
               <h2>Test Simple Upload</h2>
               <p>This tests just the file upload functionality without any processing.</p>
               <form action="http://127.0.0.1:8000/api/test-upload/" method="post" enctype="multipart/form-data">
                   <div>
                       <input type="file" name="audio_file" accept="audio/wav" required>
                   </div>
                   <br>
                   <button type="submit">Upload File</button>
               </form>
           </div>
           
           <div class="test-form">
               <h2>Test Full Audio Summary Generation</h2>
               <p>This tests the complete API with transcription, summarization, and title generation.</p>
               <form action="http://127.0.0.1:8000/api/generate-summary/" method="post" enctype="multipart/form-data">
                   <div>
                       <input type="file" name="audio_file" accept="audio/wav" required>
                   </div>
                   <br>
                   <button type="submit">Process Audio</button>
               </form>
           </div>
       </div>
   </body>
   </html>
   ```

2. Save this file to your computer and open it in any web browser
3. **For quickest verification**:
   - Start with the "Test Simple Upload" form to confirm basic file handling works
   - Once that succeeds, use the "Test Full Audio Summary Generation" form for the complete experience
4. The response will be displayed directly in your browser, showing the results in a formatted JSON view

## Troubleshooting

### Common Issues

1. **File Upload Errors**
   - Check that your file is in a supported format (WAV recommended)
   - Ensure the file is not corrupted or too large

2. **API Key Issues**
   - Verify that your Gemini API key is correctly set in the .env.local file
   - Check that you have sufficient credits/quota on your API account

3. **Transcription Quality Issues**
   - Consider using higher quality audio recordings
   - Make sure your audio is clear and has minimal background noise

4. **Windows Permission Issues**
   - The application uses a directory named 'uploaded_files' in the parent directory of your project to store files temporarily
   - Ensure this directory is writable by the user running the Django application
