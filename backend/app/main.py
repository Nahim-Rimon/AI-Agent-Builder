from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import init_db
from .auth import router as auth_router
from .agents import router as agents_router
from .chat import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)
    
print("===================================================")
print("Frontend is running on ====> http://0.0.0.0:3000")
print("Backend is running  on ====> http://0.0.0.0:8000")
print("===================================================")

app = FastAPI(title="AI Agent Builder", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(agents_router, prefix="/agents")
app.include_router(chat_router, prefix="/chat")
