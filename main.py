import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router.user_router import user_router
from api.router.conversation_router import conversation_router
from configs import settings
from custom_logger import get_logger

logger = get_logger(__name__)

def create_app(env: str = "dev"):
    app = FastAPI(
        title=f"aline-bot-api-{env}",
        description="aline-bot-api",
        version="0.1.0",
        root_path=f"/api",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app

def add_routes(app: FastAPI):
    app.include_router(user_router)
    app.include_router(conversation_router)
app = create_app(settings.env)
add_routes(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)