import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HDDS Clinical Intelligence API")

# Enable CORS so the React frontend can fetch data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON = os.path.join(PROJECT_ROOT, "outputs", "ai_medical_insights.json")

@app.get("/")
def read_root():
    return {"message": "HDDS Clinical Intelligence API is running."}

@app.get("/api/insights")
def get_insights():
    if not os.path.exists(OUTPUT_JSON):
        raise HTTPException(status_code=404, detail="Insights JSON not found. Please run the prototype runner first.")
    
    try:
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
