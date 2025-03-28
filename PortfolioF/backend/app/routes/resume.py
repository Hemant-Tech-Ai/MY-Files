from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.utils.helpers import load_json_data, get_data_file_path

router = APIRouter()

@router.get("/")
async def get_resume():
    """
    Get the complete resume data including education, experience, and certifications.
    """
    # Load resume data
    resume_data = load_json_data(get_data_file_path("resume.json"))
    
    return JSONResponse(content=resume_data)

@router.get("/experience")
async def get_experience():
    """
    Get only the work experience section of the resume.
    """
    # Load resume data
    resume_data = load_json_data(get_data_file_path("resume.json"))
    experience = resume_data.get("experience", [])
    
    return JSONResponse(content=experience)

@router.get("/education")
async def get_education():
    """
    Get only the education section of the resume.
    """
    # Load resume data
    resume_data = load_json_data(get_data_file_path("resume.json"))
    education = resume_data.get("education", [])
    
    return JSONResponse(content=education)

@router.get("/certifications")
async def get_certifications():
    """
    Get only the certifications section of the resume.
    """
    # Load resume data
    resume_data = load_json_data(get_data_file_path("resume.json"))
    certifications = resume_data.get("certifications", [])
    
    return JSONResponse(content=certifications) 