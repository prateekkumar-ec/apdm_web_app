from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.mongo import files_collection
from app.db.vector_store import embeddings, save_vectorstore, load_vectorstore
from app.services.document_processor import create_docs
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
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
    # Check if file is processed
    file_doc = files_collection.find_one({"file_id": req.file_id})
    if not file_doc or "extracted_text" not in file_doc:
        raise HTTPException(status_code=404, detail="File not processed")

    # Load or create vectorstore
    vectorstore = load_vectorstore(file_id=req.file_id)
    if not vectorstore:
        docs = create_docs(file_doc["extracted_text"])
        vectorstore = FAISS.from_documents(docs, embeddings)
        save_vectorstore(vectorstore, file_id=req.file_id)
    memory = get_memory_for_file(req.file_id)

    # LLM QA
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=OpenAI(openai_api_key=OPENAI_API_KEY),
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory
    )
    answer = qa_chain.run(req.question)

    return {"answer": answer}

def get_memory_for_file(file_id: str):
    global current_file_id, current_memory

    if current_file_id != file_id:
        current_file_id = file_id
        current_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    return current_memory
