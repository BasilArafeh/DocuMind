# DocuMind - AI Document Assistant

**Chat with your documents using Retrieval-Augmented Generation (RAG)**

[Try Live Demo on Hugging Face](https://huggingface.co/spaces/Basilarafeh/documind) • Accuracy: 73.3% • Avg response time: 3.9s

![DocuMind Interface](https://github.com/user-attachments/assets/9fb70688-aae9-4fa1-b9a7-df740e67ae3e)

---

## What is DocuMind?

DocuMind is an intelligent document assistant that lets you upload PDFs, text files, or Markdown documents and ask questions about them in natural language. The system uses Retrieval-Augmented Generation (RAG) to find relevant information in your documents and generate accurate answers with source citations.

**Key highlights:**
- 73.3% accuracy on a technical benchmark (15 questions over 2 transformer papers)
- Source citations for every answer
- Under 4 seconds average response time
- 100% accuracy on medium‑complexity questions

---

## Why I Built This

Manual document search is time‑consuming and error‑prone. Many AI tools hallucinate or do not show where answers come from. DocuMind focuses on:

1. Answering only from your uploaded documents (no external web data)
2. Citing the exact chunks used to generate each answer
3. Providing fast, semantic search across long technical documents

---

## Features

### Document Processing
- Upload PDF, TXT, and Markdown files up to 25 MB
- Drag‑and‑drop interface with multi‑document support
- Automatic text extraction and chunking
- Real‑time metadata (file size, chunk count, upload time)

### Intelligent Q&A
- RAG pipeline with semantic search using vector embeddings
- Chunk‑level source citations for transparency
- Conversational chat interface with history
- Suggested questions after document upload
- Average 3.9‑second response time on benchmark tests

### User Experience
- Clean, dark‑themed interface
- Copy answers to clipboard
- Document management (view and remove documents)
- Loading and processing indicators
- Privacy‑focused: answers only from your documents

---

## Performance & Evaluation

On a benchmark of 15 questions about transformer architecture across 2 technical documents, DocuMind achieved **73.3% accuracy (11/15)** with an average response time of **3.9 seconds**. It reached **100% accuracy on medium‑complexity questions**, but still struggles with exact factual recall (author names, specific formulas) and some comparative questions. You can reproduce the evaluation with `tests/evaluation.py`.

---

## How It Works

1. **Upload** – You upload a document (PDF, TXT, or MD).
2. **Parse & Chunk** – The system extracts text and splits it into overlapping chunks.
3. **Embed** – Each chunk is converted to a vector embedding using OpenAI.
4. **Store** – Embeddings are stored in a ChromaDB vector database.
5. **Query** – Your question is embedded and matched against stored chunks.
6. **Retrieve** – The most relevant chunks are selected using semantic similarity.
7. **Generate** – GPT‑4 generates an answer using only the retrieved context.
8. **Cite** – The answer is returned with references to the source chunks.

---

## Tech Stack

**Backend**
- FastAPI (Python 3.10+)

**AI / ML**
- OpenAI GPT‑4o-mini for answer generation
- OpenAI `text-embedding-3-small` for embeddings
- ChromaDB for vector storage and semantic search

**Frontend**
- Vanilla JavaScript
- HTML + CSS (custom dark theme)

**Deployment**
- Docker and Docker Compose
- Hugging Face Spaces

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/BasilArafeh/DocuMind.git
cd DocuMind
2.
Install dependencies:
bash
pip install -r backend/requirements.txt
Configure your OpenAI API key:
3.
bash
# in backend/.env
OPENAI_API_KEY=your_api_key_here
Run the backend:
4.
bash
cd backend
uvicorn main:app --reload
Open the frontend:
5.
Open frontend/index.html in your browser (or serve it with any simple HTTP server)

## Project Structure

```text
documind/
├── backend/                     # FastAPI backend and RAG logic
│   ├── config.py                # Settings and environment configuration
│   ├── ingestion.py             # Document parsing, cleaning, and chunking
│   ├── llm_client.py            # Wrapper around OpenAI APIs (LLM + embeddings)
│   ├── main.py                  # FastAPI app, routes, and dependency wiring
│   ├── prompts.py               # Prompt templates for answer generation
│   ├── schemas.py               # Pydantic models for requests/responses
│   ├── vector_store.py          # ChromaDB integration and retrieval helpers
│   └── requirements.txt         # Python dependencies for the backend
├── evaluation/                  # Offline evaluation scripts and results
│   ├── evaluation.py            # Runs benchmark over documents and questions
│   ├── evaluation_results.json  
│   └── test_questions.json      # Benchmark questions used for testing
├── frontend/                    # Web UI (vanilla JS)
│   ├── app.js                   # Frontend logic and API calls
│   ├── index.html               
│   └── styles.css               
├── tests/                       
│   ├── evaluation.py            
│   └── test_questions.json     
├── Dockerfile                   # Container image definition
├── docker-compose.yml           # Local/production service orchestration
└── README.md                    # Project documentation

