from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

# Base Schemas
class EducationBase(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None # Could be date or str like "YYYY" or "Month YYYY"
    end_date: Optional[str] = None # Could be date or str like "YYYY" or "Month YYYY" or "Present"
    gpa: Optional[float] = None
    details: Optional[List[str]] = []

class WorkExperienceBase(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None # Or "Present"
    responsibilities: Optional[List[str]] = []
    achievements: Optional[List[str]] = []

class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = []
    url: Optional[HttpUrl] = None
    repository_url: Optional[HttpUrl] = None

class LanguageBase(BaseModel):
    language: str
    proficiency: Optional[str] = None # e.g., Native, Fluent, Proficient, Conversational

class CertificationBase(BaseModel):
    name: str
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None # Or "Does not expire"
    credential_id: Optional[str] = None
    credential_url: Optional[HttpUrl] = None

# LLM Analysis Schema Details
class ResumeRatingDetails(BaseModel):
    overall_score: Optional[float] = None
    comments: Optional[str] = None

class ImprovementAreasDetails(BaseModel):
    content_suggestions: Optional[List[str]] = []
    formatting_style_suggestions: Optional[List[str]] = []
    missing_information_suggestions: Optional[List[str]] = []

class ActionVerbCheck(BaseModel):
    current_usage_rating: Optional[str] = None # e.g., Good, Needs Improvement
    suggestions: Optional[List[str]] = []

class QuantificationCheck(BaseModel):
    current_usage_rating: Optional[str] = None # e.g., Good, Needs Improvement
    suggestions: Optional[List[str]] = []

class UpskillSuggestion(BaseModel):
    skill_name: Optional[str] = None
    reasoning: Optional[str] = None
    suggested_resources: Optional[List[str]] = [] # List of strings as per prompt example (not dicts)
    relevance_to_career_goals: Optional[str] = None

class CareerPathAlignment(BaseModel):
    current_alignment_assessment: Optional[str] = None
    potential_paths: Optional[List[str]] = []
    suggestions_for_strengthening_alignment: Optional[List[str]] = []

# LLM Analysis Schema
class LLMAnalysis(BaseModel):
    resume_rating: Optional[ResumeRatingDetails] = None # MODIFIED
    # clarity_conciseness_rating: Optional[float] = None # REMOVED - Not in the latest prompt structure
    # impact_quantification_rating: Optional[float] = None # REMOVED - Not in the latest prompt structure
    # skill_relevance_rating: Optional[float] = None # REMOVED - Not in the latest prompt structure
    # overall_presentation_rating: Optional[float] = None # REMOVED - Not in the latest prompt structure
    # positive_feedback: Optional[str] = None # REMOVED - Not explicitly in the new detailed prompt structure under this name

    strength_areas: Optional[List[str]] = [] # As per prompt
    improvement_areas: Optional[ImprovementAreasDetails] = None # MODIFIED
    
    action_verb_check: Optional[ActionVerbCheck] = None # ADDED - As per prompt
    quantification_check: Optional[QuantificationCheck] = None # ADDED - As per prompt
    
    upskill_suggestions: Optional[List[UpskillSuggestion]] = [] # MODIFIED to use new sub-model
    
    career_path_alignment: Optional[CareerPathAlignment] = None # ADDED - As per prompt

    # Fields to remove that are not in the ANALYSIS_SYSTEM_MESSAGE prompt structure
    # missing_sections_suggestions: Optional[List[str]] = [] # Covered by improvement_areas.missing_information_suggestions
    # action_verb_suggestions: Optional[List[str]] = [] # Covered by action_verb_check.suggestions
    # quantification_suggestions: Optional[List[str]] = [] # Covered by quantification_check.suggestions
    # formatting_suggestions: Optional[List[str]] = [] # Covered by improvement_areas.formatting_style_suggestions
    # career_path_suggestions: Optional[List[str]] = [] # Covered by career_path_alignment.potential_paths or suggestions

# Resume Schemas
class ResumeBase(BaseModel):
    file_name: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None
    address: Optional[str] = None
    summary: Optional[str] = None # Or "Objective"
    
    education_history: Optional[List[EducationBase]] = []
    work_experience: Optional[List[WorkExperienceBase]] = []
    projects: Optional[List[ProjectBase]] = []
    
    technical_skills: Optional[List[str]] = [] # Could be categorized Dict[str, List[str]] e.g. {"Programming Languages": ["Python"], "Databases": ["PostgreSQL"]}
    soft_skills: Optional[List[str]] = []
    other_skills: Optional[List[str]] = []

    languages: Optional[List[LanguageBase]] = []
    certifications: Optional[List[CertificationBase]] = []
    awards_honors: Optional[List[str]] = []
    publications: Optional[List[str]] = []
    references_available: Optional[bool] = None # e.g. "References available upon request"

class ResumeCreate(BaseModel): # Used for initial file upload, before LLM processing
    file_name: str
    # No other fields, as they will be extracted by LLM

class ResumeUpdate(ResumeBase): # All fields are optional for update after LLM processing
    raw_text: Optional[str] = None
    llm_analysis: Optional[LLMAnalysis] = None
    pass

class ResumeInDBBase(ResumeBase):
    id: int
    uploaded_at: datetime
    raw_text: Optional[str] = None
    llm_analysis: Optional[LLMAnalysis] = None

    class Config:
        from_attributes = True # Pydantic V2, replaces orm_mode

# Schema for returning a single resume (full detail)
class ResumeDetail(ResumeInDBBase):
    pass

# Schema for listing resumes (summary view)
class ResumeListInfo(BaseModel):
    id: int
    file_name: str
    uploaded_at: datetime
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True

class ResumeUploadResponse(BaseModel):
    message: str
    resume_id: int
    data: ResumeDetail 