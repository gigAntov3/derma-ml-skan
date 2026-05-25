import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from api import api_router

from config import settings
from utils.database.engine import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan контекст для управления ресурсами"""

    await create_tables()
    
    yield

    # await db_manager.close()


app = FastAPI(
    title=settings.app.title,
    description=settings.app.description,
    version=settings.app.version,
    lifespan=lifespan,
    docs_url=settings.app.docs_url,
    redoc_url=settings.app.redoc_url,
    root_path=settings.app.root_path
    # openapi_url=settings.app.openapi_url,
    # openapi_prefix="/api",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
    expose_headers=settings.cors.expose_headers,
    max_age=settings.cors.max_age
)

# if os.path.exists("uploads"):
#     app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.include_router(router=api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
    )