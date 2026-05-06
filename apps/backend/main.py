import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from services.db import init_db, _conn

load_dotenv()
init_db()

app = FastAPI()

# CORS
_DEV_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]
ALLOWED_ORIGINS = (
    _DEV_ORIGINS
    if os.getenv("ENV") != "production"
    else [os.getenv("FRONTEND_URL", "")]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Something went wrong"})


# health
@app.get("/health")
def health():
    try:
        with _conn() as conn:
            conn.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "version": os.getenv("APP_VERSION", "dev"),
    }

# routers
from routes.plans import router as plans_router
from routes.nutrition import router as nutrition_router
from routes.auth import router as auth_router
from routes.logs import router as logs_router

app.include_router(plans_router)
app.include_router(nutrition_router)
app.include_router(auth_router)
app.include_router(logs_router, prefix="/logs")
