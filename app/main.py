import uvicorn
from fastapi import FastAPI
from app.api.endpoints import router
from app.core.config import settings

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        'app.main:app',
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )