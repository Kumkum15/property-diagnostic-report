# AI Property Diagnostic Report Generator

This project is an AI-powered system that automatically generates structured property inspection diagnostic reports from uploaded inspection PDFs.

The system uses Retrieval-Augmented Generation (RAG) to extract relevant inspection data from documents and generate professional reports with embedded inspection images.

## Features
- Upload **text-based inspection PDFs**
- Upload **image-based inspection PDFs**
- Extract **text and inspection images**
- Store inspection data in **Qdrant vector database**
- Retrieve relevant inspection observations using **semantic search**
- Generate structured **Diagnostic Reports using OpenAI GPT**
- Automatically embed **inspection images within report sections**

## Tech Stack
- FastAPI
- JavaScript (Frontend)
- OpenAI GPT
- LangChain
- Qdrant Vector Database
- Python

## Workflow
1. Upload inspection PDFs
2. Extract text and images
3. Store embeddings in vector database
4. Retrieve relevant inspection context
5. Generate AI-powered diagnostic report
