import subprocess
import os
import tempfile
from openai import OpenAI
from src.utils import chunking
from langchain_core.documents import Document

def transcribe_video(video_path, metadata):
    """
    Extract audio from a video file and transcribe it.
    
    Args:
        video_path (str): Path to the video file.
        metadata (dict): Metadata for the file.
        
    Returns:
        list: List with a single document containing the transcript.
    """
    print(f"Transcribing video: {video_path}")
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Create a temporary file for the audio
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
    
    try:
        # Extract audio from video using ffmpeg directly
        print(f"Extracting audio from {video_path}...")
        subprocess.run([
            'ffmpeg', 
            '-i', video_path,
            '-q:a', '0',
            '-map', 'a',
            temp_audio_path,
            '-y',  # Overwrite output file if it exists
            '-loglevel', 'error'  # Reduce output verbosity
        ], check=True)
        
        # Transcribe the audio
        print("Transcribing audio...")
        with open(temp_audio_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Create a Document object similar to what we'd get from a PDF
        doc = Document(
            page_content=transcript.text,
            metadata=metadata
        )
        
        # Apply chunking to the transcript
        metadata.update({'content_type': 'transcript'})
        chunks = chunking([doc], metadata)
        print(f"Created {len(chunks)} chunks from video transcript")
        
        return chunks
    
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        return []
    
    finally:
        # Clean up the temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)