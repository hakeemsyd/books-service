"""Books categorization service - FastAPI application."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.routes import router
from .clients.db_client import get_pool

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("books-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()  # warm the connection pool on startup
    yield
    pool = await get_pool()
    await pool.close()


app = FastAPI(title="Books Categorization Service", lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)
