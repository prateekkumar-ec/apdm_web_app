from langchain_community.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def create_docs(extracted_content):
    docs = []

    # PDF CASE (plain text)
    if isinstance(extracted_content, str):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_text(extracted_content)
        docs = [Document(page_content=c) for c in chunks]
        return docs

    # AUDIO / VIDEO CASE
    # extracted_content = list of segments
    if isinstance(extracted_content, list):
        # We group segments to provide context, but store
        # individual segments for precise timestamp matching later.
        window_size = 10  # Number of segments per document
        step_size = 5  # Overlap (moves forward by 5 segments)

        for i in range(0, len(extracted_content), step_size):
            window = extracted_content[i : i + window_size]
            if not window:
                break

            # Combine text for the LLM to read
            combined_text = " ".join([seg["text"].strip() for seg in window])

            docs.append(
                Document(
                    page_content=combined_text,
                    metadata={
                        "start": window[0]["start"],
                        "end": window[-1]["end"],
                        # We store the granular segments inside metadata
                        "original_segments": window,
                    },
                )
            )

            # Stop if we've reached the end of the content
            if i + window_size >= len(extracted_content):
                break

        return docs

    raise ValueError("Unsupported extracted content format")
