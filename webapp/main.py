from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from image_processor import ImageProcessor
from translator import TranslationService
load_dotenv()

app = FastAPI(
    title="My Project API",
    version="0.1.0",
    description="API to call project functions",
)

class AddRequest(BaseModel):
    pictureAddress: str
    

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/add")
def add(req: AddRequest):
    image_processor = ImageProcessor()
    translator = TranslationService()
    text = image_processor.extract_text_from_image(req.pictureAddress)        
    # Extract items and prices
    extracted_items = image_processor.extract_items_from_text(text)
    extracted_items =translator.translate_items(extracted_items)
            
            # Update display
    # update_items_display()
    
    return {"result": extracted_items}

@app.get("/config-example")
def config_example():
    # Example: read from .env
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API_KEY is missing in .env")
    return {"api_key_loaded": True}


