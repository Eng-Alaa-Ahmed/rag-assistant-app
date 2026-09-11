import logging

import ollama

from app.core.config import settings

logger = logging.getLogger(__name__)

_yolo_model = None


def load_yolo_model():
    global _yolo_model
    try:
        from ultralytics import YOLO
        _yolo_model = YOLO(settings.yolo_model_path)
        logger.info("YOLO model loaded from %s", settings.yolo_model_path)
    except Exception as e:
        logger.warning("YOLO model not loaded (%s). Image detection will be skipped.", e)
        _yolo_model = None


def detect_components(image_path: str):
    if _yolo_model is None:
        return []
    results = _yolo_model.predict(source=image_path, conf=settings.yolo_confidence, verbose=False)
    detected = set()
    for r in results:
        for box in r.boxes:
            detected.add(_yolo_model.names[int(box.cls[0])])
    return list(detected)


def build_prompt(question, retrieved_chunks, detected_components=None):
    context_blocks = []
    for i, chunk in enumerate(retrieved_chunks, start=1):
        context_blocks.append("[Source " + str(i) + " - Page " + str(chunk["page_number"]) + "]\n" + chunk["text"])
    context = "\n\n".join(context_blocks)

    image_note = ""
    if detected_components:
        image_note = "The uploaded image shows the following component(s): " + ", ".join(detected_components) + ".\n\n"

    prompt = "You are a helpful assistant answering questions about basic electronics, using ONLY the context provided below. If the answer is not in the context, say so clearly instead of guessing.\n\n"
    prompt += image_note + "Context:\n" + context + "\n\n"
    prompt += "Question: " + question + "\n\n"
    prompt += "Answer the question using only the context above. After your answer, cite which source(s) (e.g. Source 1, Page X) you used.\n\nAnswer:"
    return prompt


def generate_answer(question, retrieved_chunks, detected_components=None):
    prompt = build_prompt(question, retrieved_chunks, detected_components)
    response = ollama.generate(model=settings.ollama_model, prompt=prompt)
    return response["response"]