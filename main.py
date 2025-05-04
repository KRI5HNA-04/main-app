import os
import pandas as pd
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="SHL Assessment Recommender API", version="1.0")

# Load the SHL Assessment catalog
catalog_df = pd.read_csv("shl_assessment_catalog.csv")

# --- Pydantic Models ---

class RecommendRequest(BaseModel):
    query: str

class Assessment(BaseModel):
    url: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]

class RecommendResponse(BaseModel):
    recommended_assessments: List[Assessment]

# --- Routes ---

@app.get("/")
def read_root():
    return {"message": "🔍 SHL Assessment Recommender API is running!"}

@app.get("/health")
def health_check():
    return {"status": "✅ healthy"}

@app.post("/recommend", response_model=RecommendResponse)
def recommend_assessments(request: RecommendRequest):
    query = request.query.strip().lower()

    # Filter assessments containing the query in their name
    matching = catalog_df[catalog_df["Assessment Name"].str.lower().str.contains(query)]

    if matching.empty:
        return RecommendResponse(recommended_assessments=[])

    assessments = []
    for _, row in matching.iterrows():
        try:
            duration = int(str(row.get("Duration", "0")).split()[0])
        except ValueError:
            duration = 0

        assessments.append(Assessment(
            url=row.get("Assessment URL", ""),
            adaptive_support=row.get("Adaptive/IRT Support", "Unknown"),
            description=row.get("Assessment Name", "No name"),
            duration=duration,
            remote_support=row.get("Remote Testing Support", "Unknown"),
            test_type=[row.get("Test Type", "Unknown")]
        ))

    return RecommendResponse(recommended_assessments=assessments[:10])

# --- Entry Point ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
