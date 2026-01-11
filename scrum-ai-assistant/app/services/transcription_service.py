"""
Transcription service interface and stub implementation.
In production, this would integrate with real transcription services like OpenAI Whisper or AWS Transcribe.
"""
from abc import ABC, abstractmethod

from app.core.logging import get_logger

logger = get_logger(__name__)


class TranscriptionService(ABC):
    """Abstract base class for transcription services."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        pass


class MockTranscriptionService(TranscriptionService):
    """Mock transcription service for demo purposes."""

    def transcribe(self, audio_path: str) -> str:
        """
        Mock transcription - returns a demo transcript.
        In production, integrate with OpenAI Whisper, AWS Transcribe, Google Speech-to-Text, etc.
        """
        logger.info(f"Mock transcribing audio file: {audio_path}")
        
        # Demo transcript
        demo_transcript = """
        Good morning everyone. Let's start our standup.
        
        First, let's talk about OB-123. We finished the login feature integration.
        
        Sarah, what did you work on yesterday? I implemented the user dashboard component. 
        Today I'll continue with the profile settings page.
        
        John, your turn? I was blocked because the API endpoint wasn't ready. 
        Can someone check on that?
        
        I'll assign John to OB-124 to track this. Decision: We'll use React Query for data fetching.
        
        One blocker: The database migration is still pending. We need to schedule maintenance window.
        
        Action item: Tom needs to complete the payment gateway integration by Friday.
        Tom, can you confirm? Yes, I'll have it done.
        
        Great. Let's wrap up. See you tomorrow.
        """
        
        logger.info("Mock transcription completed")
        return demo_transcript
