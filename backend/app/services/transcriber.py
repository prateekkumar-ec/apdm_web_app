import openai
from app.core.config import OPENAI_API_KEY
from langchain_openai import OpenAIEmbeddings

openai.api_key = OPENAI_API_KEY
# This model converts text into semantic vectors
embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)


def transcribe_audio(file_path: str):
    with open(file_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="verbose_json"
        )

    # 1. Get just the text from each segment
    segment_texts = [seg.text for seg in transcript.segments]

    # 2. Convert text into real embeddings (Semantic Vectors)
    # This sends a batch request to OpenAI's text-embedding-3-small
    vectors = embeddings_model.embed_documents(segment_texts)

    segments = []
    for i, seg in enumerate(transcript.segments):
        segments.append(
            {
                "start": float(seg.start),
                "end": float(seg.end),
                "text": seg.text,
                "embedding": vectors[i],  # This is a list of ~1536 floats
            }
        )

    return {"text": transcript.text, "segments": segments}
