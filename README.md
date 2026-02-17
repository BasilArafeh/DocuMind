# DocuMind - AI Document Assistant

**Chat with your documents using Retrieval-Augmented Generation (RAG)**

[Try Live Demo on Hugging Face](https://huggingface.co/spaces/Basilarafeh/documind) • Accuracy: 73.3% • Avg Response Time: 3.9s

![DocuMind Interface](<img width="1919" height="902" alt="image" src="https://github.com/user-attachments/assets/3f6a070c-b22e-42ea-9850-a7926198ae13" />
<img width="1919" height="902" alt="image" src="https://github.com/user-attachments/assets/3f6a070c-b22e-42ea-9850-a7926198ae13" />
)

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

I tested DocuMind on 15 questions about transformer architecture using 2 technical documents:

**Overall Results:**
- Correct answers: 11/15 (73.3%)
- Average response time: 3.93 seconds
- Median response time: 4.11 seconds

**Breakdown by difficulty:**
- Easy questions: 75% (3/4 correct)
- Medium questions: 100% (6/6 correct)
- Hard questions: 40% (2/5 correct)

**What works well:**
- Explaining technical concepts from context
- Medium-complexity queries (most common real-world use case)
- Consistent sub-4-second response times
- Source attribution for answer verification

**Current limitations:**
- Struggles with exact factual details (author names, specific formulas)
- Difficulty with comparative analysis requiring synthesis across chunks
- Complex multi-step reasoning questions need improvement

The full evaluation can be reproduced using `tests/evaluation.py`.

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

