from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from services.db import init_db

load_dotenv()
init_db()

app = FastAPI()

# CORS
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
from routes.nutrition import router as nutrition_router
from routes.auth import router as auth_router
from routes.logs import router as logs_router

app.include_router(plans_router)
app.include_router(nutrition_router)
app.include_router(auth_router)
app.include_router(logs_router, prefix="/logs")
