"""Books categorization service - FastAPI application."""
import logging

from fastapi import FastAPI

from .api.routes import router

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("books-service")

app = FastAPI(title="Books Categorization Service")
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)
