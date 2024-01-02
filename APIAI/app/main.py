import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.keyword_explorer import ModelKeywordsExplorer


class InputBase(BaseModel):
    text: str

class OutputBase(BaseModel):
    keywords: list

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
model_path = 'minhtu0408/BERT-keyword-extractor'
ke = ModelKeywordsExplorer(model_path)
@app.get("/")
def read_root():
    return {"Hello": "World"}
@app.post("/kw", response_model=OutputBase)
def keywords_extraction(request: InputBase):
    text = request.text
    if not text:
        raise HTTPException(status_code=400, detail="Text parameter is required")

    keywords = ke.model_generate(text)
    return {"keywords": keywords}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5050, log_level=logging.INFO)
