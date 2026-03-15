from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os

from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

load_dotenv()

app = FastAPI()
app.mount("/extracted_images", StaticFiles(directory="extracted_images"), name="images")
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploaded_pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve extracted images
app.mount("/extracted_images", StaticFiles(directory="extracted_images"), name="images")

client = OpenAI()

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="pdf_vectors",
    embedding=embedding_model
)


# ---------- UPLOAD TEXT PDF ----------

@app.post("/upload_text_pdf")
async def upload_text_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Text PDF uploaded", "file": file.filename}


# ---------- UPLOAD IMAGE PDF ----------

@app.post("/upload_image_pdf")
async def upload_image_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Image PDF uploaded", "file": file.filename}


# ---------- GENERATE REPORT ----------

@app.get("/generate_report")
def generate_report():

    query = "Generate a detailed diagnostic report for the property inspection."

    search_results = vector_db.similarity_search(
        query=query,
        k=5
    )

    context = "\n\n".join(
        doc.page_content for doc in search_results
    )

    # -------- Image Section --------
    image_section = ""

    images_folder = "extracted_images"

    if os.path.exists(images_folder):

        for img in os.listdir(images_folder)[:3]:

            image_section += f"<br><img src='/extracted_images/{img}' width='500'><br>"

    # -------- SYSTEM PROMPT (UNCHANGED) --------

    SYSTEM_PROMPT = f"""
You are an AI system generating a Detailed Diagnostic Report (DDR) for a property inspection.

Return the response ONLY as clean HTML so it renders properly in the frontend.

Rules:
- Do not invent facts
- If information is missing say "Not Available"
- Use simple professional language
- Structure the report using HTML headings, paragraphs and bullet points

Structure the report EXACTLY like this:

<h1>Diagnostic Report</h1>

<h2>Property Details</h2>
<p>
Property: Flat No. 8/63, Yamuna CHS, Hari Om Nagar, Mulund<br>
Prepared by: UrbanRoof Private Limited<br>
Website: www.urbanroof.in
</p>

<h2>1. Introduction</h2>
<p>Explain the purpose of the inspection.</p>

<h2>2. General Information</h2>
<ul>
<li>Client Details</li>
<li>Site Description</li>
</ul>

<h2>3. Key Findings</h2>

<h3>Leakage and Water Ingress</h3>
<p>Explain moisture related observations.</p>

<h3>Bathroom Balcony and Terrace</h3>
<ul>
<li>Seepage observations</li>
<li>Cracks or waterproofing issues</li>
<li>Areas in good condition</li>
</ul>

<h3>External Walls and Structural Members</h3>
<ul>
<li>Damp patches</li>
<li>Efflorescence</li>
<li>Paint blistering</li>
<li>Surface cracks</li>
</ul>

<h2>4. Severity Assessment</h2>
<p>Explain seriousness of issues.</p>

<h2>5. Recommended Actions</h2>
<ul>
<li>Structural engineer inspection</li>
<li>Waterproofing improvements</li>
<li>Further environmental checks</li>
</ul>

<h2>6. Inspection Images</h2>
<p>Relevant inspection images should appear below:</p>

<h2>7. Limitations</h2>
<ul>
<li>Visual inspection only</li>
<li>Hidden defects not assessed</li>
<li>Environmental hazards not tested</li>
</ul>

<h2>Summary</h2>
<p>Provide a concise conclusion.</p>

Inspection Context:
{context}


IMAGE RULES (VERY IMPORTANT):

Inspection images are provided below as HTML <img> tags.

You MUST place these images inside the most relevant section of the report.

Examples:
- Leakage images → under "Leakage and Water Ingress"
- Bathroom or balcony images → under "Bathroom Balcony and Terrace"
- Wall crack images → under "External Walls and Structural Members"

Do NOT place all images together at the end.

Each image must appear immediately after the observation it supports.

Use this format:

<p>Observation text explaining the issue.</p>
<img src="IMAGE_URL" width="500">

{image_section}
"""

    chat_completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )

    report = chat_completion.choices[0].message.content
    report = f"""
<style>
h1, h2, h3 {{
color: black;
margin-bottom: 5px;
margin-top: 10px;
}}

p {{
margin-top: 2px;
margin-bottom: 6px;
}}

ul {{
margin-top: 2px;
}}
</style>

{report}
"""

    return {"report": report}