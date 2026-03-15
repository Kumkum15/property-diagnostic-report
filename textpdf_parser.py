import fitz
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from pathlib import Path

def index_text_pdf(pdf_path):

    docs = []

    pdf = fitz.open(pdf_path)

    for page in pdf:

        text = page.get_text()

        if text.strip():   # avoid empty pages
            docs.append(
            Document(
                page_content=text,
                metadata={"type": "text"}
            )
        )

    vector_db = QdrantVectorStore.from_documents(
        documents=docs,
        url="http://localhost:6333",
        collection_name="pdf_vectors",
        embedding=OpenAIEmbeddings(model="text-embedding-3-large")
    )

    print("Text PDF indexed successfully")

if __name__ == "__main__":

    pdf_path = Path(__file__).parent / "Main DDR.pdf"

    index_text_pdf(pdf_path)