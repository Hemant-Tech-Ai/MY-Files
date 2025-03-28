from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.utils.helpers import load_json_data, get_data_file_path

router = APIRouter()

@router.get("/overview")
async def get_portfolio_overview():
    """
    Get an overview of the portfolio including basic information.
    """
    return JSONResponse(
        content={
            "name": "John Doe",
            "title": "Senior Software Engineer",
            "summary": "Experienced software engineer with expertise in full-stack development, cloud architecture, and machine learning.",
            "location": "San Francisco, CA",
            "email": "john.doe@example.com",
            "github": "https://github.com/johndoe",
            "linkedin": "https://linkedin.com/in/johndoe"
        }
    )

@router.get("/stats")
async def get_portfolio_stats():
    """
    Get aggregated statistics about skills and projects.
    """
    # Load skills data
    skills_data = load_json_data(get_data_file_path("skills.json"))
    skills = skills_data.get("skills", [])
    
    # Load projects data
    projects_data = load_json_data(get_data_file_path("projects.json"))
    projects = projects_data.get("projects", [])
    
    # Calculate statistics
    skill_categories = {}
    for skill in skills:
        category = skill.get("category")
        if category in skill_categories:
            skill_categories[category] += 1
        else:
            skill_categories[category] = 1
    
    top_skills = sorted(skills, key=lambda x: x.get("proficiency", 0), reverse=True)[:5]
    
    project_technologies = {}
    for project in projects:
        for tech in project.get("technologies", []):
            if tech in project_technologies:
                project_technologies[tech] += 1
            else:
                project_technologies[tech] = 1
    
    return JSONResponse(
        content={
            "total_skills": len(skills),
            "total_projects": len(projects),
            "skill_categories": skill_categories,
            "top_skills": [{"name": skill.get("name"), "proficiency": skill.get("proficiency")} for skill in top_skills],
            "project_technologies": project_technologies,
            "featured_projects": len([p for p in projects if p.get("featured", False)])
        }
    ) 