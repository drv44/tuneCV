from sqlalchemy.orm import Session
from typing import List, Optional, Type
from pydantic import HttpUrl

from app.db import models # Corrected: Direct import of models module
from app.api.v1 import schemas # Corrected: Direct import of schemas module

# Helper to convert Pydantic schema to dictionary, excluding unset values for updates
def schema_to_dict(schema_instance):
    return schema_instance.model_dump(exclude_unset=True)

def create_resume_entry(db: Session, file_name: str, raw_text: Optional[str] = None) -> models.Resume:
    """
    Creates an initial resume entry with file name and optional raw text.
    """
    db_resume = models.Resume(file_name=file_name, raw_text=raw_text)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def get_resume_by_id(db: Session, resume_id: int) -> Optional[models.Resume]:
    """
    Retrieves a single resume by its ID.
    """
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()

def get_all_resumes(db: Session, skip: int = 0, limit: int = 100) -> List[Type[models.Resume]]:
    """
    Retrieves a list of resumes, with pagination.
    """
    return db.query(models.Resume).offset(skip).limit(limit).all()

def update_resume_with_extracted_data(db: Session, resume_id: int, update_data: schemas.ResumeUpdate) -> Optional[models.Resume]:
    """
    Updates a resume entry with extracted data and LLM analysis.
    The update_data should be a Pydantic schema (ResumeUpdate).
    """
    db_resume = get_resume_by_id(db, resume_id)
    if db_resume:
        update_data_dict = schema_to_dict(update_data)
        
        for key, value in update_data_dict.items():
            if hasattr(db_resume, key):
                if isinstance(value, HttpUrl):
                    setattr(db_resume, key, str(value))
                else:
                    setattr(db_resume, key, value)
            # else: # Optional: handle cases where key in update_data is not in model
                # print(f"Warning: Key {key} not found in Resume model.")

        # Special handling for llm_analysis if it's a Pydantic model itself
        if update_data.llm_analysis is not None:
            # Assuming llm_analysis in the model is JSONB and can store the dict directly
            db_resume.llm_analysis = schema_to_dict(update_data.llm_analysis)
        
        # Similarly for other complex JSONB fields if they are passed as Pydantic models
        # For example, if education_history in update_data is a list of EducationBase Pydantic models:
        if update_data.education_history:
            db_resume.education_history = [schema_to_dict(edu) for edu in update_data.education_history]
        if update_data.work_experience:
            db_resume.work_experience = [schema_to_dict(work) for work in update_data.work_experience]
        if update_data.projects:
            db_resume.projects = [schema_to_dict(proj) for proj in update_data.projects]
        if update_data.languages:
            db_resume.languages = [schema_to_dict(lang) for lang in update_data.languages]
        if update_data.certifications:
            db_resume.certifications = [schema_to_dict(cert) for cert in update_data.certifications]

        db.commit()
        db.refresh(db_resume)
    return db_resume

def delete_resume(db: Session, resume_id: int) -> Optional[models.Resume]:
    """
    Deletes a resume entry by its ID.
    """
    db_resume = get_resume_by_id(db, resume_id)
    if db_resume:
        db.delete(db_resume)
        db.commit()
    return db_resume # Returns the deleted object (now detached from session) or None 