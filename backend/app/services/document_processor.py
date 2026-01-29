from langchain_community.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_docs(file_text: str):
    """
    Splits text into chunks suitable for embeddings.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = splitter.split_text(file_text)
    docs = [Document(page_content=c) for c in chunks]
    return docs
