import os
import base64
import json
import re
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Finance Document Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in .env file")

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3-flash-preview"

ANALYSIS_PROMPT = """
You are an experienced financial attorney and analyst. You have been provided with a financial document (loan, mortgage, insurance policy, credit agreement, or similar).

Analyze the document and return your response STRICTLY as JSON (no markdown, no text before or after the JSON):

{
  "document_type": "Type of document (loan / mortgage / insurance / credit / other)",
  "document_summary": "Short 2-3 sentence summary of the document in plain language",
  "risk_level": "low | medium | high | critical",
  "risk_explanation": "1-2 sentence explanation of the risk level in plain language",
  "hidden_fees": [
    {
      "title": "Name of the fee or charge",
      "description": "Plain-language explanation — what it is, when it is charged",
      "amount": "Amount or percentage if stated in the document, otherwise null",
      "severity": "low | medium | high"
    }
  ],
  "penalties": [
    {
      "title": "Name of the penalty or fine",
      "description": "When and why it applies — plain-language explanation",
      "amount": "Size of the penalty if stated, otherwise null",
      "severity": "low | medium | high"
    }
  ],
  "dangerous_clauses": [
    {
      "title": "Name of the dangerous clause",
      "description": "What this clause means and why it is risky for the client",
      "recommendation": "What to do or what to watch out for",
      "severity": "low | medium | high | critical"
    }
  ],
  "key_conditions": [
    {
      "label": "Condition name",
      "value": "Condition value"
    }
  ],
  "red_flags": [
    "Specific warning 1 — in plain language",
    "Specific warning 2"
  ],
  "recommendations": [
    "Specific recommendation 1 — what to do before signing",
    "Specific recommendation 2"
  ],
  "overall_verdict": "Overall conclusion: should you sign this document and why — plain language, 3-5 sentences"
}

Important:
- Write ONLY in English
- Explain everything in plain language, avoid legal jargon
- If the document is not financial, state that in document_type and explain in document_summary
- Be specific: quote real amounts and percentages from the document
- Return ONLY valid JSON with no extra characters
"""


def extract_json_from_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise ValueError("Could not extract valid JSON from response")


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf"]:
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 20MB")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        pdf_base64 = base64.b64encode(content).decode("utf-8")

        model = genai.GenerativeModel(MODEL_NAME)

        response = model.generate_content([
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "application/pdf",
                            "data": pdf_base64
                        }
                    },
                    {
                        "text": ANALYSIS_PROMPT
                    }
                ]
            }
        ])

        raw_text = response.text
        result = extract_json_from_response(raw_text)

        return JSONResponse(content={"success": True, "data": result, "filename": file.filename})

    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "authentication" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Invalid Gemini API key")
        if "quota" in error_msg.lower() or "rate" in error_msg.lower():
            raise HTTPException(status_code=429, detail="API rate limit exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {error_msg}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
