from fastapi import FastAPI, UploadFile, File, HTTPException

from pydantic import BaseModel
from dotenv import load_dotenv
import os
from image_processor import ImageProcessor
from translator import TranslationService
import tempfile
from pathlib import Path
load_dotenv()

app = FastAPI()

MAX_BYTES = 10 * 1024 * 1024  # 10MB
CHUNK_SIZE = 1024 * 1024      # 1MB
ALLOWED_CT = {"image/jpeg", "image/png", "image/webp"}

TMP_DIR = Path("/tmp/myapp_uploads")
TMP_DIR.mkdir(parents=True, exist_ok=True)

 

@app.post("/v1/extract-items")
async def add(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CT:
        raise HTTPException(415, "Unsupported content type")

    suffix = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }[file.content_type]

    tmp_path = None

    try:
        # Create temp file
        fd, name = tempfile.mkstemp(dir=str(TMP_DIR), suffix=suffix)
        os.close(fd)
        tmp_path = name

        # Read file (limit size)
        data = await file.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise HTTPException(413, "File too large")

        # Write to disk (sync is fine here)
        with open(tmp_path, "wb") as f:
            f.write(data)

        # --- Your existing logic ---
        image_processor = ImageProcessor()
        translator = TranslationService()

        text = image_processor.extract_text_from_image(tmp_path)
        extracted_items = image_processor.extract_items_from_text(text)
        extracted_items = translator.translate_items(extracted_items)

        return {"ok": True, "items": extracted_items}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)    

@app.get("/config-example")
def config_example():
    # Example: read from .env
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API_KEY is missing in .env")
    return {"api_key_loaded": True}


