"""
Speech Use Cases.

Operations for speech-to-text and text-to-speech.
All operations use DTOs for input and output.
"""

from src.application.dtos.use_case_dtos import (
    SynthesisOutput,
    SynthesizeInput,
    TranscribeInput,
    TranscriptionOutput,
)
from src.core.ports import SpeechRecognizer, SpeechSynthesizer


class SpeechUseCases:
    """
    Use cases for speech operations.

    Groups related speech operations: transcribe and synthesize.
    """

    def __init__(
        self,
        recognizer: SpeechRecognizer | None = None,
        synthesizer: SpeechSynthesizer | None = None,
    ) -> None:
        """
        Initialize with speech ports.

        Args:
            recognizer: Port for speech-to-text (optional).
            synthesizer: Port for text-to-speech (optional).
        """
        self._recognizer = recognizer
        self._synthesizer = synthesizer

    async def transcribe(self, input_dto: TranscribeInput) -> TranscriptionOutput:
        """
        Transcribe audio to text.

        Args:
            input_dto: Contains audio bytes to transcribe.

        Returns:
            Transcription DTO with text and metadata.

        Raises:
            ValueError: If recognizer not configured.
            PartnerConnectionError: If connection to transcription service fails.
            PartnerResponseError: If transcription service returns an error.
        """
        if self._recognizer is None:
            raise ValueError("Speech recognizer not configured")

        result = await self._recognizer.transcribe(input_dto.audio_bytes)

        return TranscriptionOutput(
            text=result.text,
            confidence=result.confidence,
            duration_seconds=result.duration_seconds,
        )

    async def synthesize(self, input_dto: SynthesizeInput) -> SynthesisOutput:
        """
        Synthesize text to speech audio.

        Args:
            input_dto: Contains text to synthesize.

        Returns:
            Synthesis DTO with audio bytes.

        Raises:
            ValueError: If synthesizer not configured.
            PartnerConnectionError: If connection to synthesis service fails.
            PartnerResponseError: If synthesis service returns an error.
        """
        if self._synthesizer is None:
            raise ValueError("Speech synthesizer not configured")

        audio_bytes = await self._synthesizer.synthesize(input_dto.text)

        return SynthesisOutput(
            audio_bytes=audio_bytes,
            format="mp3",
        )
