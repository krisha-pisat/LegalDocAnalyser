from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.api.general_search import get_search_results
import uvicorn

app = FastAPI()

# ✅ Add this CORS middleware block exactly as shown:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods like POST, OPTIONS, etc.
    allow_headers=["*"],
)

class Query(BaseModel):
    summary: str

@app.post("/search")
def search(query: Query):
    results = get_search_results(query.summary)
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)