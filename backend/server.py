"""HTTP API exposing the SML lexer to the local React application."""

from dataclasses import asdict

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from .lexer import tokenize


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: str = Field(max_length=1_000_000)
    keep_comments: bool = Field(default=False, alias="keepComments")


app = FastAPI(title="SML Lexical Analyzer API", version="1.0.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/tokenize")
def analyze(request: AnalyzeRequest) -> dict[str, list[dict]]:
    analyzed = tokenize(request.source, keep_comments=request.keep_comments)
    return {
        "tokens": [asdict(token) for token in analyzed if token.type != "ERROR"],
        "errors": [asdict(token) for token in analyzed if token.type == "ERROR"],
    }
