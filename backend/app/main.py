from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import upload, statistics, analysis, chat, clustering
from app.api import regression
import os

# Create FastAPI app
app = FastAPI(
    title="Data Analysis API",
    description="Advanced data analysis platform with LLM integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API routers
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(statistics.router, prefix="/api/v1", tags=["Statistics"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(regression.router, prefix="/api/v1", tags=["Regression"])
app.include_router(clustering.router, prefix="/api/v1", tags=["Clustering"])

@app.get("/")
async def root():
    return {"message": "Data Analysis API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is operational"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
