"""The study website: the findings pages (web/, data in web/data/study.json) and the live model.

    GET  /api/health    liveness check (used by the deploy smoke test)
    GET  /api/model     model card: questions, accuracy from cross-validation, labels
    POST /api/predict   answers -> a score per model, with what moved it
    /                   the site (web/): a static page with hash routing; charts read data/study.json

Answers are scored in memory and never stored or logged.
"""
import mimetypes
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .scoring import Models

# ES modules need a JavaScript MIME type; some hosts' registries map .js to text/plain
mimetypes.add_type('text/javascript', '.js')
WEB_DIR = Path(__file__).resolve().parent.parent / 'web'
MODELS = Models()

app = FastAPI(title='Is Generative AI Displacing Arabic? Study site and model', docs_url='/api/docs',
              openapi_url='/api/openapi.json', redoc_url=None)


class Answers(BaseModel):
    Age: int
    Education: int
    Field: int
    Eng_Prof: int
    Events: list[int] = Field(default_factory=list)
    AI_Start: int
    AI_Freq: int
    AI_TaskShare: int
    AI_Breadth: list[int] = Field(default_factory=list)
    AI_Lang: int
    AI_Content: int
    AI_ContentLang: int


@app.get('/api/health')
def health():
    return {'status': 'ok', 'models': len(MODELS.spec['models'])}


@app.get('/api/model')
def model_card():
    return MODELS.card()


@app.post('/api/predict')
def predict(answers: Answers):
    a = answers.model_dump()
    errors = MODELS.validate(a)
    if errors:
        raise HTTPException(status_code=422, detail=errors)
    return MODELS.predict(a)


app.mount('/', StaticFiles(directory=WEB_DIR, html=True), name='web')
