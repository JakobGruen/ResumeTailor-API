from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
import json
from shutil import rmtree

from resumetailor.core.constants import BASE_DATA_DIR

router = APIRouter()


@router.get("/data/full_resume.json")
def get_full_resume():
    file_path = BASE_DATA_DIR / "full_resume.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    with open(file_path) as f:
        return json.load(f)


@router.get("/data/history")
def get_history():
    history = []
    for app_dir in BASE_DATA_DIR.iterdir():
        if app_dir.is_dir():
            info_json = app_dir / "info.json"
            if info_json.exists() and info_json.stat().st_size > 0:
                with open(info_json) as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = None
                history.append({"id": app_dir.name, "data": data})
            else:
                history.append({"id": app_dir.name, "data": None})
    return history


@router.get("/data/{id}/job_description.txt")
def get_job_description_txt(id: str):
    file_path = BASE_DATA_DIR / id / "job_description.txt"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Job description not found.")
    return FileResponse(
        path=file_path, filename="job_description.txt", media_type="text/plain"
    )


@router.get("/data/{id}/job_profile.json")
def get_profile_json(id: str):
    file_path = BASE_DATA_DIR / id / "job_profile.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Job Profile JSON not found.")
    with open(file_path) as f:
        return json.load(f)


@router.get("/data/{id}/resume.html")
def get_resume_html(id: str):
    file_path = BASE_DATA_DIR / id / "resume.html"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume HTML not found.")
    return HTMLResponse(content=file_path.read_text(), status_code=200)


@router.get("/data/{id}/cover_letter.html")
def get_cover_letter_html(id: str):
    file_path = BASE_DATA_DIR / id / "cover_letter.html"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Cover letter HTML not found.")
    return HTMLResponse(content=file_path.read_text(), status_code=200)


@router.get("/data/{id}/resume.pdf")
def download_resume_pdf(id: str):
    file_path = BASE_DATA_DIR / id / "resume.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume PDF not found.")
    return FileResponse(
        path=file_path, filename="resume.pdf", media_type="application/pdf"
    )


@router.get("/data/{id}/cover_letter.pdf")
def download_cover_letter_pdf(id: str):
    file_path = BASE_DATA_DIR / id / "cover_letter.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Cover letter PDF not found.")
    return FileResponse(
        path=file_path, filename="cover_letter.pdf", media_type="application/pdf"
    )


@router.delete("/data/{id}")
def delete_data_id(id: str):
    dir_path = BASE_DATA_DIR / id
    if not dir_path.exists() or not dir_path.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found.")
    try:
        rmtree(dir_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete: {e}")
    return {"detail": f"Deleted {id} successfully."}
