import io
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

from app.services.profiling import profile_dataset
from app.ai.intent_parser import parse_query
from app.analysis.analysis_executor import execute_analysis
from app.analysis.explanation import generate_explanation

# Load environment variables from a local .env file if present
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory storage for latest dataset schema
_current_schema = None
_current_dataframe = None


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
async def health_check():
    return {"status": "Backend running"}


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and analyze a CSV file.
    Returns filename, row count, column count, schema analysis, and first 5 rows preview.
    """
    global _current_schema, _current_dataframe
    
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    
    try:
        # Read the uploaded file
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Profile the dataset
        schema = profile_dataset(df)
        _current_schema = schema
        _current_dataframe = df
        
        # Generate preview (first 5 rows)
        preview_rows = df.head(5).to_dict(orient="records")
        
        return {
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "schema": schema,
            "preview": preview_rows
        }
    
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/query")
async def query_intent(request: QueryRequest):
    """
    Parse natural language query using Groq API.
    Uses the schema from the last uploaded dataset.
    """
    if _current_schema is None or _current_dataframe is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded yet. Please upload a CSV first.")
    
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    # Parse the query using the latest schema context, then execute deterministic analysis.
    intent = parse_query(question, _current_schema)
    if "error" in intent:
        return intent

    try:
        result = execute_analysis(intent, _current_dataframe)
    except ValueError as e:
        return {"error": str(e)}
    explanation = generate_explanation(intent["operation"], result)

    return {
        "intent": intent,
        "result": result,
        "explanation": explanation,
    }

