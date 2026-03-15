import fitz
import os
import base64
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from openai import OpenAI
from pathlib import Path

load_dotenv()

client = OpenAI()

IMAGE_FOLDER = "extracted_images"

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)


def extract_images(pdf_path):

    os.makedirs(IMAGE_FOLDER, exist_ok=True)

    doc = fitz.open(pdf_path)

    image_paths = []
    seen_xrefs = set()

    for page_index in range(len(doc)):

        page = doc[page_index]
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):

            xref = img[0]

            if xref in seen_xrefs:
                continue

            seen_xrefs.add(xref)

            base_image = doc.extract_image(xref)

            # skip tiny images
            if base_image["width"] < 300 or base_image["height"] < 300:
                continue

            image_bytes = base_image["image"]
            ext = base_image["ext"]

            image_name = f"page{page_index+1}_{img_index}.{ext}"
            image_path = os.path.join(IMAGE_FOLDER, image_name)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_paths.append(image_path)

    return image_paths


def encode_image(image_path):

    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def describe_image(image_path):

    base64_img = encode_image(image_path)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe this thermal inspection image"},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_img}"
                }
            ]
        }]
    )

    return response.output_text


def index_images(pdf_path):

    image_paths = extract_images(pdf_path)

    docs = []

    for img in image_paths:

        print("Processing image:", img)

        description = describe_image(img)

        docs.append(
            Document(
                page_content=description,
                metadata={
                    "type": "image",
                    "image_path": img
                }
            )
        )

    vector_store = QdrantVectorStore.from_documents(
        documents=docs,
        url="http://localhost:6333",
        collection_name="pdf_vectors",
        embedding=embedding_model
    )

    print("Image indexing completed")

if __name__ == "__main__":

    pdf_path = Path(__file__).parent / "Thermal Images.pdf"

    index_images(pdf_path)