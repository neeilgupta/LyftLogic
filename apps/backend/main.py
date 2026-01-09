from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.plans import router as plans_router
from dotenv import load_dotenv
from services.db import init_db


init_db()
load_dotenv()

app = FastAPI()

# ✅ CORS (THIS FIXES THE UI ERROR)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# health
@app.get("/health")
def health():
    return {"status": "ok"}

# routers
from routes.plans import router as plans_router
app.include_router(plans_router)
