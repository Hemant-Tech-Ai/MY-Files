from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.utils.helpers import load_json_data, get_data_file_path

router = APIRouter()

@router.get("/")
async def get_skills(
    category: Optional[str] = Query(None),
    min_proficiency: Optional[int] = Query(None)
):
    """
    Get a list of skills, optionally filtered by category and minimum proficiency.
    
    Args:
        category: Filter skills by category
        min_proficiency: Filter skills by minimum proficiency level
    """
    # Load skills data
    skills_data = load_json_data(get_data_file_path("skills.json"))
    skills = skills_data.get("skills", [])
    
    # Apply filters
    if category:
        skills = [skill for skill in skills if skill.get("category") == category]
    
    if min_proficiency is not None:
        skills = [skill for skill in skills if skill.get("proficiency", 0) >= min_proficiency]
    
    # Group skills by category
    grouped_skills = {}
    for skill in skills:
        category = skill.get("category")
        if category not in grouped_skills:
            grouped_skills[category] = []
        grouped_skills[category].append(skill)
    
    return JSONResponse(content=grouped_skills)

@router.get("/top")
async def get_top_skills(limit: Optional[int] = Query(5)):
    """
    Get the top skills based on proficiency.
    
    Args:
        limit: Number of top skills to return
    """
    # Load skills data
    skills_data = load_json_data(get_data_file_path("skills.json"))
    skills = skills_data.get("skills", [])
    
    # Sort skills by proficiency (descending) and take the top N
    top_skills = sorted(skills, key=lambda x: x.get("proficiency", 0), reverse=True)[:limit]
    
    return JSONResponse(content=top_skills) 