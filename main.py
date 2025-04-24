import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.current import router as currentRouter
from app.routes.status import router as statusRouter
from app.routes.upload import router as uploadRouter
from app.routes.debugImage import router as debugImageRouter

ROUTERS = (
    currentRouter, 
    statusRouter, 
    uploadRouter, 
    debugImageRouter
)

app = FastAPI(
    title="Finger Detection Server",
    description="A FastAPI server for detecting fingers in images from ESP32-CAM",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
for r in ROUTERS:
    app.include_router(r)

@app.get("/")
async def root():
    return "Alive and Well"

if __name__ == "__main__":
    print("Starting Finger Detection Server...")
    print("API will be available at http://0.0.0.0:8000")
    print("API documentation available at http://0.0.0.0:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)