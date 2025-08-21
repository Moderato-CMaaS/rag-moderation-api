
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .api import api_router
from .core.config import DOT_NET_API_KEY


app = FastAPI(
    title="Content Moderation API",
    description="An API for moderating text using custom rules.",
    version="1.0.0",
)

# Add CORS middleware - THIS MUST BE BEFORE OTHER MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Key Security Middleware ---

@app.middleware("http")
async def check_api_key(request: Request, call_next):
    # Allow unauthenticated access to root and documentation endpoints
    open_paths = {"/", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}
    
    # Allow all OPTIONS requests for CORS preflight
    if request.method == "OPTIONS":
        return await call_next(request)
    
    if request.url.path in open_paths:
        return await call_next(request)
    if request.headers.get("X-API-Key") != DOT_NET_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid or missing API key.")
    return await call_next(request)


app.include_router(api_router)


@app.get("/")
def read_root():
    return {"status": "API is running"}

# To run: uvicorn app.main:app --reload