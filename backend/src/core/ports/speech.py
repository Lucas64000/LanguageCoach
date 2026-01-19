"""
SpeechRecognizer port for speech-to-text transcription.

Port defines the contract for generating responses.
Core layer must have ZERO external imports.
"""

from typing import Protocol

from src.core.value_objects import TranscriptionResult


class SpeechRecognizer(Protocol):
    """
    Port for speech recognition services.

    Implementations convert audio bytes to text transcription.
    """

    async def transcribe(self, audio: bytes) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio: Raw audio bytes.

        Returns:
            TranscriptionResult with text, confidence, and duration.
        """
        ...


class SpeechSynthesizer(Protocol):
    """
    Port for text-to-speech synthesis services.

    Implementations convert text to audio bytes.
    """

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio.

        Args:
            text: Text to convert to speech.

        Returns:
            Audio bytes in MP3 format.
        """
        ...
