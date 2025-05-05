import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from configs import settings
from schedule_service.service import scheduler, job_runner
from database.db import create_db_and_tables
from custom_logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # start up contexts
    scheduler.add_job(job_runner, "interval", seconds=25)
    scheduler.start()
    logger.info("Scheduler started")
    
    await create_db_and_tables()
    logger.info("Database tables created")
    yield
    # Clean up contexts
    scheduler.shutdown()
    logger.info("Scheduler shutdown")
    
def create_app(env: str = "dev", lifespan: asynccontextmanager = None):
    app = FastAPI(
        title=f"aline-bot-api-{env}",
        description="aline-bot-api",
        version="0.1.0",
        lifespan=lifespan,
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
    from api.router.user_router import user_router
    from api.router.conversation_router import conversation_router
    from api.router.chat_router import chat_router    
    app.include_router(user_router)
    app.include_router(conversation_router)
    app.include_router(chat_router)



app = create_app(settings.env, lifespan=lifespan)
add_routes(app)

@app.get("/health-check")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
