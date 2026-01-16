"""
Tests for SpeechUseCases.

Covers transcription and synthesis operations.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.dtos.use_case_dtos import (
    SynthesisOutput,
    SynthesizeInput,
    TranscribeInput,
    TranscriptionOutput,
)
from src.application.use_cases.speech import SpeechUseCases
from src.core.exceptions import PartnerConnectionError, PartnerResponseError
from src.core.value_objects import TranscriptionResult


class TestSpeechUseCases:
    """Tests for SpeechUseCases."""

    @pytest.fixture
    def mock_recognizer(self) -> MagicMock:
        """Create mock SpeechRecognizer."""
        mock = MagicMock()
        mock.transcribe = AsyncMock()
        return mock

    @pytest.fixture
    def mock_synthesizer(self) -> MagicMock:
        """Create mock SpeechSynthesizer."""
        mock = MagicMock()
        mock.synthesize = AsyncMock()
        return mock

    @pytest.fixture
    def use_case(
        self, mock_recognizer: MagicMock, mock_synthesizer: MagicMock
    ) -> SpeechUseCases:
        """Create use case with mock ports."""
        return SpeechUseCases(recognizer=mock_recognizer, synthesizer=mock_synthesizer)

    # Transcription Tests

    async def test_transcribe_returns_output(
        self, use_case: SpeechUseCases, mock_recognizer: MagicMock
    ) -> None:
        """Verify transcribe returns correct output DTO."""
        expected_result = TranscriptionResult(
            text="Hello world",
            confidence=0.95,
            duration_seconds=2.5,
        )
        mock_recognizer.transcribe.return_value = expected_result
        input_dto = TranscribeInput(audio_bytes=b"fake audio")

        result = await use_case.transcribe(input_dto)

        assert isinstance(result, TranscriptionOutput)
        assert result.text == "Hello world"
        assert result.confidence == 0.95
        assert result.duration_seconds == 2.5
        mock_recognizer.transcribe.assert_called_once_with(b"fake audio")

    async def test_transcribe_propagates_errors(
        self, use_case: SpeechUseCases, mock_recognizer: MagicMock
    ) -> None:
        """Verify errors from recognizer are propagated."""
        mock_recognizer.transcribe.side_effect = PartnerConnectionError("Failed")

        with pytest.raises(PartnerConnectionError):
            await use_case.transcribe(TranscribeInput(audio_bytes=b"audio"))

    async def test_transcribe_raises_if_not_configured(self) -> None:
        """Verify raises ValueError if recognizer is missing."""
        use_case = SpeechUseCases(recognizer=None)
        with pytest.raises(ValueError, match="recognizer"):
            await use_case.transcribe(TranscribeInput(audio_bytes=b"audio"))

    # Synthesis Tests

    async def test_synthesize_returns_output(
        self, use_case: SpeechUseCases, mock_synthesizer: MagicMock
    ) -> None:
        """Verify synthesize returns correct output DTO."""
        mock_synthesizer.synthesize.return_value = b"audio_data"
        input_dto = SynthesizeInput(text="Hello")

        result = await use_case.synthesize(input_dto)

        assert isinstance(result, SynthesisOutput)
        assert result.audio_bytes == b"audio_data"
        assert result.format == "mp3"
        mock_synthesizer.synthesize.assert_called_once_with("Hello")

    async def test_synthesize_propagates_errors(
        self, use_case: SpeechUseCases, mock_synthesizer: MagicMock
    ) -> None:
        """Verify errors from synthesizer are propagated."""
        mock_synthesizer.synthesize.side_effect = PartnerResponseError("Failed")

        with pytest.raises(PartnerResponseError):
            await use_case.synthesize(SynthesizeInput(text="Hello"))

    async def test_synthesize_raises_if_not_configured(self) -> None:
        """Verify raises ValueError if synthesizer is missing."""
        use_case = SpeechUseCases(synthesizer=None)
        with pytest.raises(ValueError, match="synthesizer"):
            await use_case.synthesize(SynthesizeInput(text="Hello"))
