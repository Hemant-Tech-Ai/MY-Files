from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import portfolio, projects, skills, resume, chatbot, contact

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(portfolio.router, prefix=f"{settings.API_PREFIX}/portfolio", tags=["Portfolio"])
app.include_router(projects.router, prefix=f"{settings.API_PREFIX}/projects", tags=["Projects"])
app.include_router(skills.router, prefix=f"{settings.API_PREFIX}/skills", tags=["Skills"])
app.include_router(resume.router, prefix=f"{settings.API_PREFIX}/resume", tags=["Resume"])
app.include_router(chatbot.router, prefix=f"{settings.API_PREFIX}/chatbot", tags=["Chatbot"])
app.include_router(contact.router, prefix=f"{settings.API_PREFIX}/contact", tags=["Contact"])

@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    return JSONResponse(
        content={
            "message": "Welcome to the Portfolio API",
            "docs_url": "/docs",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 