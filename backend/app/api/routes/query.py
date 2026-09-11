import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.query import QueryRequest, QueryResponse
from app.services import generation, retrieval

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "vector_store_ready": retrieval.is_ready()}


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        retrieved = retrieval.retrieve(request.question)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    answer = generation.generate_answer(request.question, retrieved)

    sources = []
    for r in retrieved:
        s = "Page " + str(r["page_number"])
        if s not in sources:
            sources.append(s)

    return QueryResponse(answer=answer, sources=sources)


@router.post("/query-image", response_model=QueryResponse)
async def query_with_image(question: str = Form(...), image: UploadFile = File(...)):
    try:
        retrieved = retrieval.retrieve(question)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(image.filename).suffix) as tmp:
        shutil.copyfileobj(image.file, tmp)
        tmp_path = tmp.name

    try:
        detected = generation.detect_components(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    answer = generation.generate_answer(question, retrieved, detected_components=detected)

    sources = []
    for r in retrieved:
        s = "Page " + str(r["page_number"])
        if s not in sources:
            sources.append(s)

    return QueryResponse(answer=answer, sources=sources, detected_components=detected)