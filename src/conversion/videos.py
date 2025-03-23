import subprocess
import os
import tempfile
from openai import OpenAI

def transcribe_video(video_path, api_key=None):
    """
    Extract audio from a video file and transcribe it in one step using ffmpeg.
    
    Args:
        video_path (str): Path to the video file
        api_key (str, optional): OpenAI API key. If None, will use OPENAI_API_KEY environment variable
        
    Returns:
        str: The transcribed text
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key if api_key else os.getenv('OPENAI_API_KEY'))
    
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
        
        return transcript.text
    
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        raise
    
    finally:
        # Clean up the temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    # Example usage
    video_path = 'docs/video.mp4'
    transcript = transcribe_video(video_path)
    print("\nTranscription:")
    print(transcript)