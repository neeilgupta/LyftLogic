from fastapi import FastAPI

app = FastAPI(title="GymGPT API")

@app.get("/health")
def health():
    return {"ok": True}
