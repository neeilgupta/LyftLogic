from fastapi import FastAPI
from routes import plans  # <-- THIS is the missing import

app = FastAPI(title="GymGPT API")
source .venv/bin/activate

# mount the /plans endpoints
app.include_router(plans.router, prefix="/plans", tags=["plans"])

@app.get("/health")
def health():
    return {"ok": True}