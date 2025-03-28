from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class Skill(BaseModel):
    """Skill schema."""
    id: str
    name: str
    category: str
    proficiency: int
    icon: Optional[str] = None
    description: Optional[str] = None

class Education(BaseModel):
    """Education schema."""
    institution: str
    degree: str
    field: str
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

class Experience(BaseModel):
    """Work experience schema."""
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None
    description: List[str]
    location: Optional[str] = None
    technologies: Optional[List[str]] = None

class Certification(BaseModel):
    """Certification schema."""
    name: str
    issuer: str
    date: str
    url: Optional[HttpUrl] = None
    description: Optional[str] = None

class Resume(BaseModel):
    """Resume schema."""
    education: List[Education]
    experience: List[Experience]
    certifications: Optional[List[Certification]] = None

class ProjectImage(BaseModel):
    """Project image schema."""
    url: str
    alt: str
    is_primary: bool = False

class Project(BaseModel):
    """Project schema."""
    id: str
    title: str
    description: str
    long_description: Optional[str] = None
    technologies: List[str]
    github_url: Optional[HttpUrl] = None
    live_url: Optional[HttpUrl] = None
    images: Optional[List[ProjectImage]] = None
    featured: bool = False
    date: str

class ChatbotQuery(BaseModel):
    """Chatbot query schema."""
    message: str

class ChatbotResponse(BaseModel):
    """Chatbot response schema."""
    response: str
    context: Optional[dict] = None 