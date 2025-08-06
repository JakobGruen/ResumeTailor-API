from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn

from resumetailor.api.application import router as application_router
from resumetailor.api.job_profile import router as job_profile_router
from resumetailor.api.resume import router as resume_router
from resumetailor.api.cover_letter import router as cover_letter_router
from resumetailor.api.data import router as data_router
from resumetailor.core.constants import BASE_DATA_DIR
from resumetailor.services.convert_resume import convert_resume


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Convert YAML resume to JSON
    yaml_file = BASE_DATA_DIR / "full_resume.yaml"
    json_file = BASE_DATA_DIR / "full_resume.json"

    if yaml_file.exists():
        try:
            convert_resume(yaml_file, json_file)
            print(f"✅ Converted {yaml_file} to {json_file} on startup")
        except Exception as e:
            print(f"⚠️ Failed to convert resume on startup: {e}")
    else:
        print(f"⚠️ YAML resume file not found: {yaml_file}")

    yield

    # Shutdown: Add any cleanup logic here if needed
    print("🛑 Application shutting down")


app = FastAPI(lifespan=lifespan)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "resumetailor-api"}


# Allow frontend (localhost:3000) to call the API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(application_router, prefix="")
app.include_router(job_profile_router, prefix="")
app.include_router(resume_router, prefix="")
app.include_router(cover_letter_router, prefix="")
app.include_router(data_router, prefix="")


def main():
    """Main function to start the uvicorn server."""
    uvicorn.run(
        "resumetailor.main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,  # Set to True for development
        log_level="info",
    )


if __name__ == "__main__":
    main()
