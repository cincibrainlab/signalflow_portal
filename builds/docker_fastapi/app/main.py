from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from app.models import AnalysisInput
from app.analysis import run_analysis, run_bandpower

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/analyze")
async def analyze_file(input_data: AnalysisInput):
    result = run_analysis(input_data.filename, input_data.metadata)
    return result

@app.post("/power_bandpower")
async def analysis_bandpower(input_data: AnalysisInput):
    result = run_bandpower(input_data.filename, input_data.metadata)
    return result