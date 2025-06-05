from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.base_class import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Extracted Personal Information
    name = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    address = Column(String, nullable=True)
    summary = Column(Text, nullable=True) # Or "Objective"

    # Structured Data Fields (using JSONB for flexibility)
    # These correspond to Pydantic models like EducationBase, WorkExperienceBase etc.
    education_history = Column(JSONB, nullable=True)  # List of education objects
    work_experience = Column(JSONB, nullable=True)    # List of work experience objects
    projects = Column(JSONB, nullable=True)           # List of project objects
    
    technical_skills = Column(JSONB, nullable=True)   # List of strings or dict
    soft_skills = Column(JSONB, nullable=True)        # List of strings
    other_skills = Column(JSONB, nullable=True)       # List of strings

    languages = Column(JSONB, nullable=True)          # List of language objects
    certifications = Column(JSONB, nullable=True)     # List of certification objects
    awards_honors = Column(JSONB, nullable=True)      # List of strings
    publications = Column(JSONB, nullable=True)       # List of strings
    references_available = Column(Boolean, nullable=True)

    # Raw text from resume
    raw_text = Column(Text, nullable=True)

    # LLM Analysis and Suggestions
    # This corresponds to the LLMAnalysis Pydantic model
    llm_analysis = Column(JSONB, nullable=True)
    # Example sub-fields that might be directly in llm_analysis JSON:
    # resume_rating = Column(Float, nullable=True) 
    # improvement_areas = Column(Text, nullable=True)
    # upskill_suggestions = Column(Text, nullable=True) # Or JSONB if more structured

    def __repr__(self):
        return f"<Resume(id={self.id}, file_name='{self.file_name}', name='{self.name}')>" 