import os
import uuid
import logging
import tempfile
import threading
import time
import random
import shutil
from audio_processor import AudioProcessor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class YouTubeTranslator:
    """
    Class to handle YouTube video downloading, audio extraction, 
    and translation from English to Brazilian Portuguese.
    """
    
    def __init__(self):
        # Create temporary directory for downloaded and processed files
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'yt_translator')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Dictionary to store job statuses
        self.jobs = {}
        
        # Audio processor for translation
        self.audio_processor = AudioProcessor()
    
    def start_translation_job(self, youtube_url):
        """Start a translation job for the given YouTube URL."""
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        self.jobs[job_id] = {
            'status': 'initializing',
            'progress': 0,
            'youtube_url': youtube_url,
            'message': 'Job created, initializing...'
        }
        
        # Start processing thread
        thread = threading.Thread(target=self._process_job, args=(job_id, youtube_url))
        thread.daemon = True
        thread.start()
        
        return job_id
    
    def get_job_status(self, job_id):
        """Get the status of a translation job."""
        if job_id not in self.jobs:
            return {'status': 'not_found', 'message': 'Job not found'}
        
        return self.jobs[job_id]
    
    def _process_job(self, job_id, youtube_url):
        """Process a translation job in a separate thread."""
        try:
            # Update job status
            self.jobs[job_id]['status'] = 'downloading'
            self.jobs[job_id]['message'] = 'Downloading YouTube video...'
            
            # Download video
            video_info, audio_path = self._download_youtube_audio(youtube_url)
            
            # Update job with video info
            self.jobs[job_id]['video_title'] = video_info['title']
            self.jobs[job_id]['video_author'] = video_info['author']
            self.jobs[job_id]['video_length'] = video_info['length']
            self.jobs[job_id]['progress'] = 20
            
            # Translate audio
            self.jobs[job_id]['status'] = 'translating'
            self.jobs[job_id]['message'] = 'Translating audio from English to Brazilian Portuguese...'
            
            # Start translation process
            translated_audio_path = self._translate_audio(audio_path, job_id)
            
            # Update job with translation results
            self.jobs[job_id]['status'] = 'completed'
            self.jobs[job_id]['message'] = 'Translation completed successfully!'
            self.jobs[job_id]['progress'] = 100
            self.jobs[job_id]['filename'] = os.path.basename(translated_audio_path)
            self.jobs[job_id]['translated_audio_path'] = translated_audio_path
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            self.jobs[job_id]['status'] = 'error'
            self.jobs[job_id]['message'] = f'Error: {str(e)}'
    
    def _download_youtube_audio(self, youtube_url):
        """
        Download audio from a YouTube video.
        
        Returns:
            tuple: (video_info, audio_path)
        """
        try:
            # Create YouTube object
            yt = YouTube(youtube_url)
            
            # Get video info
            video_info = {
                'title': yt.title,
                'author': yt.author,
                'length': yt.length  # Duration in seconds
            }
            
            # Get audio stream
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            # Download audio
            audio_path = audio_stream.download(output_path=self.temp_dir)
            
            # Rename to have .mp3 extension
            base, _ = os.path.splitext(audio_path)
            new_audio_path = f"{base}.mp3"
            os.rename(audio_path, new_audio_path)
            
            return video_info, new_audio_path
            
        except Exception as e:
            logger.error(f"Error downloading YouTube audio: {str(e)}")
            raise Exception(f"Failed to download YouTube audio: {str(e)}")
    
    def _translate_audio(self, audio_path, job_id):
        """
        Translate audio from English to Brazilian Portuguese.
        
        Args:
            audio_path: Path to the audio file
            job_id: Job ID for status updates
            
        Returns:
            str: Path to the translated audio file
        """
        try:
            # Get audio duration
            duration = self.audio_processor.get_audio_duration(audio_path)
            
            # Determine if we need to split the audio
            if duration > 3600:  # If longer than 1 hour
                self.jobs[job_id]['message'] = 'Audio is longer than 1 hour. Splitting into chunks...'
                
                # Split, translate, and join audio
                translated_audio_path = self.audio_processor.process_long_audio(
                    audio_path, 
                    progress_callback=lambda progress, message: self._update_job_progress(job_id, progress, message)
                )
            else:
                # Process audio in one go
                translated_audio_path = self.audio_processor.process_audio(
                    audio_path,
                    progress_callback=lambda progress, message: self._update_job_progress(job_id, progress, message)
                )
            
            return translated_audio_path
            
        except Exception as e:
            logger.error(f"Error translating audio: {str(e)}")
            raise Exception(f"Failed to translate audio: {str(e)}")
    
    def _update_job_progress(self, job_id, progress, message):
        """Update job progress."""
        if job_id in self.jobs:
            # Scale progress from 20-90% (as 0-20% is download, 90-100% is finalization)
            scaled_progress = 20 + (progress * 0.7)
            self.jobs[job_id]['progress'] = min(90, scaled_progress)
            self.jobs[job_id]['message'] = message
