from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.utils.helpers import load_json_data, get_data_file_path, filter_items, sort_items

router = APIRouter()

@router.get("/")
async def get_projects(
    technologies: Optional[List[str]] = Query(None),
    featured: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query("desc")
):
    """
    Get a list of projects with optional filtering and sorting.
    
    Args:
        technologies: Filter projects by technologies used
        featured: Filter projects by featured status
        sort_by: Field to sort by (e.g., "date")
        sort_order: Sort order ("asc" or "desc")
    """
    # Load projects data
    projects_data = load_json_data(get_data_file_path("projects.json"))
    projects = projects_data.get("projects", [])
    
    # Apply filters
    filters = {}
    if featured is not None:
        filters["featured"] = featured
    
    filtered_projects = filter_items(projects, filters)
    
    # Filter by technologies (special case since it's a list)
    if technologies:
        filtered_projects = [
            project for project in filtered_projects
            if any(tech in project.get("technologies", []) for tech in technologies)
        ]
    
    # Apply sorting
    sorted_projects = sort_items(filtered_projects, sort_by, sort_order)
    
    return JSONResponse(content=sorted_projects)

@router.get("/{project_id}")
async def get_project(project_id: str):
    """
    Get detailed information about a specific project.
    
    Args:
        project_id: ID of the project to retrieve
    """
    # Load projects data
    projects_data = load_json_data(get_data_file_path("projects.json"))
    projects = projects_data.get("projects", [])
    
    # Find the project with the given ID
    project = next((p for p in projects if p.get("id") == project_id), None)
    
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    
    return JSONResponse(content=project) 