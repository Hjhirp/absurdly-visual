from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from .config import settings
from .websocket import register_socket_events
from .api import routes
from .routes import feed

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Allow all origins for now
    logger=True,
    engineio_logger=True
)

# Register socket events
register_socket_events(sio)

# Create FastAPI app
app = FastAPI(
    title="Absurdly Visual API",
    description="Backend API for Multimodal Cards Against Humanity",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API routes
app.include_router(routes.router)
app.include_router(feed.router)

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(
    sio,
    other_asgi_app=app,
    socketio_path='/socket.io'
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Absurdly Visual API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:socket_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
