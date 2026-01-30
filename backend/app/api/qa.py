import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.mongo import files_collection
from app.db.vector_store import embeddings, save_vectorstore, load_vectorstore
from app.services.document_processor import create_docs
from langchain_community.llms import OpenAI
from langchain_community.vectorstores import FAISS
from app.core.config import OPENAI_API_KEY
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

router = APIRouter(prefix="/qa", tags=["Q&A"])
current_file_id = None
current_memory = None


class QuestionRequest(BaseModel):
    file_id: str
    question: str


@router.post("")
def answer_question(req: QuestionRequest):
    # Validation & Setup
    file_doc = files_collection.find_one({"file_id": req.file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found!")

    # Vectorstore & Memory Management
    vectorstore = load_vectorstore(file_id=req.file_id)
    if not vectorstore:
        if "segments" in file_doc and file_doc["segments"]:
            docs = create_docs(file_doc["segments"])  # Audio/Video with metadata
        else:
            docs = create_docs(file_doc.get("extracted_text", ""))  # PDF
        vectorstore = FAISS.from_documents(docs, embeddings)
        save_vectorstore(vectorstore, file_id=req.file_id)

    memory = get_memory_for_file(req.file_id)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # LLM QA Chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=OpenAI(openai_api_key=OPENAI_API_KEY),
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        output_key="answer",  # Crucial for memory with multiple outputs
    )

    result = qa_chain.invoke({"question": req.question})
    answer_text = result["answer"].lower()

    # Embed the answer once to compare with segments
    answer_embedding = embeddings.embed_query(answer_text)

    raw_precise_segments = []
    SIMILARITY_THRESHOLD = 0.75

    # We look inside the 'original_segments' list we stored in each Doc's metadata
    for doc in result.get("source_documents", []):
        segments = doc.metadata.get("original_segments", [])
        for seg in segments:
            seg_embedding = seg.get("embedding")
            if seg_embedding:
                score = get_cosine_similarity(answer_embedding, seg_embedding)

                # If semantically similar, this is the part of the video to play
                if score >= SIMILARITY_THRESHOLD:
                    raw_precise_segments.append(
                        {
                            "text": seg["text"],
                            "start": seg["start"],
                            "end": seg["end"],
                            "score": score,
                        }
                    )

    # We merge the tiny 5-sec snippets into continuous playable video clips
    final_timestamps = merge_timestamps(raw_precise_segments)

    return {
        "answer": result["answer"],
        "timestamps": final_timestamps,
    }


def get_memory_for_file(file_id: str):
    global current_file_id, current_memory

    if current_file_id != file_id:
        current_file_id = file_id
        current_memory = ConversationBufferMemory(
            memory_key="chat_history",  # Essential for ConversationalRetrievalChain
            input_key="question",  # Matches your chain's input_key
            output_key="answer",  # Matches your chain's output_key
            return_messages=True,
        )
    return current_memory


def merge_timestamps(timestamps):
    if not timestamps:
        return []

    # 1. Deduplicate by start time (in case same segment appears in multiple docs)
    unique_segments = {ts["start"]: ts for ts in timestamps}.values()
    
    # 2. Sort by start time
    sorted_ts = sorted(unique_segments, key=lambda x: x["start"])
    merged = []

    curr = sorted_ts[0].copy() # Copy to avoid mutating original data

    for next_ts in sorted_ts[1:]:
        # 3. If segments overlap or touch (within 1.5s gap is safer for speech)
        if next_ts["start"] <= curr["end"] + 1.5:
            # Update end time only if the next segment actually ends later
            curr["end"] = max(curr["end"], next_ts["end"])
            
            # Avoid repeating exact same text if segments overlap
            if next_ts["text"].strip() not in curr["text"]:
                curr["text"] += " " + next_ts["text"].strip()
        else:
            merged.append(curr)
            curr = next_ts.copy()

    merged.append(curr)
    return merged


def get_cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
