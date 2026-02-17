# DocuMind - AI Document Assistant

**Chat with your documents using Retrieval-Augmented Generation (RAG)**

[Try Live Demo on Hugging Face](https://huggingface.co/spaces/Basilarafeh/documind) • Accuracy: 73.3% • Avg Response Time: 3.9s

DocuMind Interface
<img width="1919" height="911" alt="image" src="https://github.com/user-attachments/assets/7a1fddcd-d0ae-4fca-bac5-9e956c9abf5d" />




---

## What is DocuMind?

DocuMind is an intelligent document assistant that lets you upload PDFs, text files, or markdown documents and ask questions about them in natural language. The system uses Retrieval-Augmented Generation (RAG) to find relevant information in your documents and generate accurate answers with source citations.

**Key highlights:**
- Achieves 73% accuracy on technical benchmarks
- Provides source citations for every answer
- Responds in under 4 seconds on average
- 100% accuracy on medium-complexity questions

---

## Why I Built This

Manual document search is time-consuming and inefficient. Existing AI solutions often hallucinate facts or lack transparency about their sources. DocuMind solves both problems by:

1. Only answering from your uploaded documents (no external data)
2. Citing the exact chunks used to generate each answer
3. Providing fast, semantic search across large documents

---

## Features

### Document Processing
- Upload PDF, TXT, and Markdown files up to 25MB
- Drag-and-drop interface with multi-document support
- Automatic text extraction and chunking
- Real-time metadata tracking (file size, chunks, upload time)

### Intelligent Q&A
- RAG pipeline with semantic search using vector embeddings
- Chunk-level source citations for transparency
- Conversational chat interface with history
- Suggested questions after document upload
- Average 3.9 second response time

### User Experience
- Clean, modern dark-themed interface
- Copy answers to clipboard
- Document management (view, remove documents)
- Real-time processing indicators
- Privacy-focused: answers only from your documents

---

## Performance & Evaluation

Tested on 15 technical questions across 2 transformer architecture documents:
- **73.3% overall accuracy** (11/15 correct) with **3.9s average response time**
- **100% accuracy on medium-complexity queries** (6/6) - the most common real-world use case
- Struggles with exact factual recall (author names, formulas) and comparative analysis
- Full results: Run `tests/evaluation.py` or see `evaluation/evaluation_results.json`

---

## How It Works

1. **Upload**: You upload a document (PDF, TXT, or MD)
2. **Parse & Chunk**: The system extracts text and splits it into overlapping chunks
3. **Embed**: Each chunk is converted to a vector embedding using OpenAI
4. **Store**: Embeddings are stored in ChromaDB vector database
5. **Query**: When you ask a question, it's embedded and matched against stored chunks
6. **Retrieve**: Top relevant chunks are retrieved based on semantic similarity
7. **Generate**: GPT-4 generates an answer using only the retrieved context
8. **Cite**: The system returns the answer with source chunk references

---

## Tech Stack

**Backend:**
- FastAPI for REST API
- Python 3.10+

**AI/ML:**
- OpenAI GPT-4 for answer generation
- OpenAI text-embedding-ada-002 for embeddings
- ChromaDB for vector storage and semantic search

**Frontend:**
- Vanilla JavaScript
- HTML/CSS (custom dark theme)

**Deployment:**
- Docker & Docker Compose
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
