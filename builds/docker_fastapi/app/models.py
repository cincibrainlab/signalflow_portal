from pydantic import BaseModel

class AnalysisInput(BaseModel):
    filename: str
    metadata: dict