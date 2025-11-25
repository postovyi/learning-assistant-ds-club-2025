import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, materials

app = FastAPI(title="Learning Assistant API", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(materials.router, prefix="/api", tags=["materials"])

@app.get("/")
async def root():
    return {"message": "Learning Assistant API"}

if __name__ == "__main__":
    uvicorn.run(
        'app.main:app',
        host="0.0.0.0",
        port=8000,
        reload=True
    )