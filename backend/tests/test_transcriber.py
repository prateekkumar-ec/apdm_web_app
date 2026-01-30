import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.services.transcriber import transcribe_audio

# 1. Mock the Whisper Response Object
class MockSegment:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text

@patch("app.services.transcriber.openai.audio.transcriptions.create")
@patch("app.services.transcriber.embeddings_model") # Patch the instance directly
def test_transcribe_audio_success(mock_embed_model, mock_whisper):
    # Mock Whisper
    mock_seg = MagicMock(); mock_seg.start=0; mock_seg.end=5; mock_seg.text="Hello"
    mock_transcript = MagicMock(); mock_transcript.text="Hello"; mock_transcript.segments=[mock_seg]
    mock_whisper.return_value = mock_transcript

    # Mock Embeddings - This MUST match what you assert
    fake_vector = [0.1, 0.2, 0.3]
    mock_embed_model.embed_documents.return_value = [fake_vector]

    with patch("builtins.open", mock_open(read_data=b"abc")):
        result = transcribe_audio("fake.mp3")

    # Assert precisely against the fake_vector
    assert result["segments"][0]["embedding"] == fake_vector 

    