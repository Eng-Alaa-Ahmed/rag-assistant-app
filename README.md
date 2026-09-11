# Electronics RAG Assistant

A RAG-powered assistant that answers questions about basic electronics, grounded in a
textbook corpus, with an Extended Track computer-vision component that identifies
electronic components (resistor, capacitor, transistor, IC, etc.) from an uploaded photo.

## Overview

- **Domain:** Basic Electronics (components: resistors, capacitors, transistors, diodes, ICs, logic gates, flip-flops, etc.)
- **Text source:** "Basic Electronics" textbook (180 pages, single PDF)
- **Vision component (Extended Track):** YOLOv8n fine-tuned on the ElectroCom61 dataset (2121 images, 61 component classes)
- **Track:** Extended

## Architecture

User asks a question (with optional photo) in the Streamlit Frontend, which calls the
FastAPI Backend. The backend retrieves relevant chunks from the Chroma Vector Store,
optionally runs the fine-tuned YOLOv8 model on an uploaded image, and sends the combined
context to the Ollama LLM (llama3.1) to generate a grounded, cited answer.

## Tech Stack

- **Notebook / data pipeline:** Python, PyMuPDF, sentence-transformers (all-MiniLM-L6-v2), ChromaDB, Ultralytics YOLOv8
- **Backend:** FastAPI, Pydantic, Ollama (local LLM), ChromaDB
- **Frontend:** Streamlit
- **LLM:** Ollama running llama3.1 locally

## Project Structure

- notebooks/rag_pipeline.ipynb
- backend/app/ (main.py, api/routes/query.py, core/config.py, schemas/, services/)
- backend/data/ (vector_store/, yolo_model/)
- backend/requirements.txt, backend/.env.example
- frontend/app.py, frontend/api_client.py, frontend/requirements.txt
- data/ (raw/, images/ - not committed, see below)

## Domain & Data

- **Text corpus:** "Basic Electronics" textbook by V. Ramani Kumar & P. Meena Priya Dharshini (180 pages).
- **Image dataset:** [ElectroCom61](https://data.mendeley.com/datasets/6scy6h8sjz/2) (2121 images, 61 electronic component classes, CC BY license).

## Backend Setup

1. cd backend
2. python -m venv .venv
3. .venv\Scripts\activate
4. pip install -r requirements.txt
5. copy .env.example .env
6. uvicorn app.main:app --reload

Open http://localhost:8000/docs to test /query from the Swagger UI.

## Frontend Setup

1. cd frontend
2. pip install -r requirements.txt
3. streamlit run app.py

## Environment Variables

| Variable | Where | Description |
|---|---|---|
| VECTOR_STORE_PATH | backend | Path to the persisted Chroma store |
| COLLECTION_NAME | backend | Chroma collection name |
| EMBEDDING_MODEL_NAME | backend | sentence-transformers model |
| OLLAMA_MODEL | backend | Local Ollama model (llama3.1) |
| YOLO_MODEL_PATH | backend | Path to fine-tuned YOLO weights |
| CORS_ORIGINS | backend | Allowed frontend origins |
| API_BASE_URL | frontend | URL of the FastAPI backend |

## API Reference

### GET /health
Returns status ok and vector_store_ready true.

### POST /query
Send a JSON body with a "question" field to http://localhost:8000/query, receive an
answer with cited sources.

### POST /query-image (Extended Track)
Send a multipart form with "question" and "image" fields to
http://localhost:8000/query-image.

## Evaluation Results

## 2.6 Evaluation

| # | Question | Retrieved Source(s) | Grounded/Correct? | Notes |
|---|----------|---------------------|--------------------|----|
| 1 | What is a transistor? | Page 54, 57 | ✅ Correct | Matches textbook definition (3-layer device, NPN/PNP) exactly |
| 2 | What is a resistor and how is it measured? | Page 174, 171, 175 | ✅ Correct | Formula R = ρl/a matches source; model correctly excluded an irrelevant chunk |
| 3 | Difference between NPN and PNP transistors | Page 57, 8, 54 | ✅ Correct | Correctly explains p-type/n-type sandwich arrangement |
| 4 | What is a capacitor used for? | Page 40, 174, 172 | ⚠️ Partially correct | Answer only mentions filtering/voltage regulation; retrieved chunks did not surface capacitor's core role (energy storage), so the answer is grounded but incomplete |
| 5 | What is a diode? | Page 18, 19 | ✅ Correct | Correct p-n junction and forward-bias definition |
| 6 | Explain Boolean algebra briefly | Page 113, 107, 114 | ✅ Correct | Correct and concise |
| 7 | What is a logic gate? | Page 107, 126 | ✅ Correct | Correct general definition |
| 8 | What is a flip-flop? | Page 126, 131 | ✅ Correct | Detailed and accurate (Q/Q̄ states, toggle behavior) |
| 9 | What is binary coded decimal? | Page 96, 106 | ✅ Correct | Correct, concise |
| 10 | What is a half adder? | Page 125, 123, 124 | ✅ Correct | Correct (sum + carry outputs) |

**Result: 9/10 fully correct and grounded, 1/10 partially correct (grounded but incomplete).**

**Main failure pattern observed:** The only weak case (Q4, capacitor) was not hallucination — the model didn't invent facts — but a **retrieval gap**: the top-3 chunks retrieved for "capacitor" leaned toward filtering/voltage-regulation content and did not surface the more fundamental "energy storage" definition that likely exists elsewhere in the textbook. This suggests the embedding model matched surface-level keyword overlap ("capacitor", "voltage") over conceptual completeness. 

**Mitigation:** Increasing `top_k` from 3 to 5 for broader coverage was tested informally and is a reasonable general fix, though it was not re-run systematically for this report to preserve the original evaluation set. No hallucination (answers not grounded in retrieved context) was observed in any of the 10 test questions, which confirms the RAG pipeline is retrieving and citing correctly rather than falling back on the LLM's own parametric knowledge.

## Screenshots:

<img width="780" height="808" alt="screenshot_text_query" src="https://github.com/user-attachments/assets/88326d9d-e6f9-437e-b232-36eac4f6606e" />

<img width="875" height="896" alt="Screenshot_img_query" src="https://github.com/user-attachments/assets/13851606-8c13-42d6-9c7c-b73a4dcf715f" />



## Video walkthrough:
(https://drive.google.com/file/d/1WfN5j2daVLs4ErHOSNhtPvClCuZcPOd8/view?usp=sharing)

## Tests
   
   ![pytest results]<img width="1533" height="417" alt="screenshot_pytest" src="https://github.com/user-attachments/assets/9bc75e4f-511c-4abd-99d8-8914d56ceba2" />



