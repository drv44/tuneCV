from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict

from app.db.database import get_db
from app.api.v1 import schemas
from app.crud import crud_resume
from app.utils import file_helpers
from app.services import llm_service
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=schemas.ResumeUploadResponse)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a resume file, extracts its content, performs LLM analysis,
    and stores the information in the database.
    """
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="LLM service not configured: GOOGLE_API_KEY missing.")
    if not llm_service.llm: # Check if LLM was initialized successfully
        raise HTTPException(status_code=500, detail="LLM client could not be initialized. Check API key and service status.")

    logger.info(f"Starting resume upload process for file: {file.filename}")

    # 1. Save uploaded file and extract text
    try:
        saved_file_path = file_helpers.save_upload_file(file)
        logger.info(f"File saved to: {saved_file_path}")
        raw_text = file_helpers.get_text_from_file(saved_file_path)
        if not raw_text:
            logger.warning(f"Could not extract text from file: {file.filename}")
            raise HTTPException(status_code=400, detail=f"Could not extract text from file: {file.filename}. Ensure it's a supported format (PDF, DOCX, TXT) and not empty/corrupted.")
        logger.info(f"Text extracted successfully from {file.filename} (length: {len(raw_text)} chars)")
    except Exception as e:
        logger.error(f"Error during file processing for {file.filename}: {e}", exc_info=True)
        # Attempt to clean up saved file if it exists
        if 'saved_file_path' in locals() and os.path.exists(saved_file_path):
            try:
                os.remove(saved_file_path)
                logger.info(f"Cleaned up saved file: {saved_file_path}")
            except Exception as cleanup_e:
                logger.error(f"Error cleaning up file {saved_file_path}: {cleanup_e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    # 2. Create initial resume entry in DB
    try:
        db_resume_entry = crud_resume.create_resume_entry(db, file_name=file.filename, raw_text=raw_text)
        logger.info(f"Initial resume entry created with ID: {db_resume_entry.id}")
    except Exception as e:
        logger.error(f"Error creating initial DB entry for {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: Could not create initial resume entry.")

    # 3. LLM Extraction
    extracted_data_dict: Dict[str, Any] = {}
    try:
        logger.info(f"Sending text to LLM for extraction (resume ID: {db_resume_entry.id})")
        extracted_data_dict = llm_service.extract_resume_data_from_text(raw_text)
        if "error" in extracted_data_dict:
            logger.error(f"LLM extraction failed for resume ID {db_resume_entry.id}: {extracted_data_dict.get('details', extracted_data_dict['error'])}")
            # Update DB entry with error? Or just fail request? For now, fail.
            # Potentially, we could save the raw text and mark it for later processing.
            raise HTTPException(status_code=500, detail=f"LLM data extraction failed: {extracted_data_dict.get('details', extracted_data_dict['error'])}")
        logger.info(f"LLM extraction successful for resume ID: {db_resume_entry.id}")
    except Exception as e:
        logger.error(f"Exception during LLM extraction for resume ID {db_resume_entry.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM data extraction process encountered an error: {str(e)}")

    # 4. LLM Analysis
    llm_analysis_dict: Dict[str, Any] = {}
    try:
        logger.info(f"Sending extracted data to LLM for analysis (resume ID: {db_resume_entry.id})")
        llm_analysis_dict = llm_service.analyze_resume_content(extracted_data_dict, raw_resume_text=raw_text)
        if "error" in llm_analysis_dict:
            logger.error(f"LLM analysis failed for resume ID {db_resume_entry.id}: {llm_analysis_dict.get('details', llm_analysis_dict['error'])}")
            # As above, consider how to handle. For now, fail.
            raise HTTPException(status_code=500, detail=f"LLM analysis failed: {llm_analysis_dict.get('details', llm_analysis_dict['error'])}")
        logger.info(f"LLM analysis successful for resume ID: {db_resume_entry.id}")
    except Exception as e:
        logger.error(f"Exception during LLM analysis for resume ID {db_resume_entry.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM analysis process encountered an error: {str(e)}")

    # 5. Prepare data for DB update (using Pydantic models for validation and structure)
    try:
        # Create LLMAnalysis Pydantic model from dictionary
        # Assuming llm_analysis_dict matches the structure of schemas.LLMAnalysis
        llm_analysis_pydantic = schemas.LLMAnalysis(**llm_analysis_dict)
        
        # Create ResumeUpdate Pydantic model
        valid_resume_fields = schemas.ResumeUpdate.model_fields.keys()
        filtered_extracted_data = {k: v for k, v in extracted_data_dict.items() if k in valid_resume_fields}

        resume_update_data = schemas.ResumeUpdate(
            file_name=file.filename,
            raw_text=raw_text,
            llm_analysis=llm_analysis_pydantic,
            **filtered_extracted_data
        )
        logger.info(f"Prepared data for DB update (resume ID: {db_resume_entry.id})")
    except Exception as e: # Catch Pydantic validation errors or other issues
        logger.error(f"Error preparing data for DB update (resume ID: {db_resume_entry.id}): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error preparing data for database update: {str(e)}")

    # 6. Update resume entry in DB with extracted data and analysis
    try:
        updated_resume = crud_resume.update_resume_with_extracted_data(
            db, resume_id=db_resume_entry.id, update_data=resume_update_data
        )
        if not updated_resume:
            logger.error(f"Failed to update resume in DB (ID: {db_resume_entry.id})")
            raise HTTPException(status_code=404, detail="Resume not found after update attempt.")
        logger.info(f"Resume entry updated successfully in DB (ID: {updated_resume.id})")
    except Exception as e:
        logger.error(f"Error updating DB with extracted data for resume ID {db_resume_entry.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: Could not update resume with extracted data.")

    # Clean up the saved file after processing
    try:
        os.remove(saved_file_path)
        logger.info(f"Successfully cleaned up uploaded file: {saved_file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up uploaded file {saved_file_path}: {e}")
        # Non-critical, so don't raise HTTP Exception, just log

    return schemas.ResumeUploadResponse(
        message="Resume uploaded and processed successfully!", 
        resume_id=updated_resume.id, 
        data=schemas.ResumeDetail.model_validate(updated_resume) # Use model_validate for Pydantic v2
    )

@router.get("/", response_model=List[schemas.ResumeListInfo])
def read_resumes(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of resumes with basic information.
    """
    logger.info(f"Fetching resumes with skip={skip}, limit={limit}")
    resumes = crud_resume.get_all_resumes(db, skip=skip, limit=limit)
    logger.info(f"Retrieved {len(resumes)} resumes from DB.")
    return [schemas.ResumeListInfo.model_validate(resume) for resume in resumes]

@router.get("/{resume_id}", response_model=schemas.ResumeDetail)
def read_resume_details(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves detailed information for a specific resume by its ID.
    """
    logger.info(f"Fetching details for resume ID: {resume_id}")
    db_resume = crud_resume.get_resume_by_id(db, resume_id=resume_id)
    if db_resume is None:
        logger.warning(f"Resume with ID {resume_id} not found.")
        raise HTTPException(status_code=404, detail="Resume not found")
    logger.info(f"Successfully retrieved details for resume ID: {resume_id}")
    return schemas.ResumeDetail.model_validate(db_resume)

@router.delete("/{resume_id}", response_model=schemas.ResumeDetail) # Or a simple message
def delete_resume_entry(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Deletes a resume entry from the database.
    """
    logger.info(f"Attempting to delete resume ID: {resume_id}")
    deleted_resume = crud_resume.delete_resume(db, resume_id=resume_id)
    if deleted_resume is None:
        logger.warning(f"Resume with ID {resume_id} not found for deletion.")
        raise HTTPException(status_code=404, detail="Resume not found for deletion")
    logger.info(f"Successfully deleted resume ID: {resume_id}")
    # The object is detached but contains the data before deletion.
    return schemas.ResumeDetail.model_validate(deleted_resume) 