import json
import logging
from typing import Dict, Any, Optional
import tenacity
from google.api_core.exceptions import ResourceExhausted, TooManyRequests

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
# from langchain.output_parsers import PydanticOutputParser # For stricter Pydantic output, if needed later

from app.core.config import settings
from app.api.v1 import schemas # For Pydantic models if using PydanticOutputParser or for reference

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize LLM
if not settings.GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in settings. LLM service will not function.")
    llm = None
else:
    try:
        # Note: The user encountered quota issues with 'gemini-2.0-flash'.
        # This might be a custom or less common model name. Standard models include 'gemini-1.5-flash-latest' or 'gemini-1.0-pro'.
        # For now, keeping the user's specified model. If issues persist beyond rate limits, this could be a point of investigation.
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=settings.GOOGLE_API_KEY,
                                   temperature=0.2, convert_system_message_to_human=True)
        logger.info("Google Generative AI (gemini-2.0-flash) initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Google Generative AI: {e}")
        llm = None

# --- Prompt Templates --- #

EXTRACTION_SYSTEM_MESSAGE = """
You are an expert AI assistant specializing in parsing and extracting structured information from resumes.
Your task is to meticulously analyze the provided resume text and extract key details.
Format your output STRICTLY as a single JSON object. Do not include any explanatory text before or after the JSON.
If a field is not present in the resume, use `null` for optional string/number fields, or an empty list `[]` for list fields.
Ensure all string values are properly escaped within the JSON.

The JSON object should conform to the following structure (use these exact key names):
{{ "name": "Full Name", "email": "email@example.com", "phone": "(555) 123-4567", "linkedin_url": "https://linkedin.com/in/username", "github_url": "https://github.com/username", "portfolio_url": "https://example.com", "address": "City, State, Country", "summary": "A brief professional summary or objective.", "education_history": [ {{ "institution": "University Name", "degree": "Degree Name (e.g., Bachelor of Science)", "field_of_study": "Major/Field of Study", "start_date": "Month YYYY or YYYY", "end_date": "Month YYYY or YYYY or Present", "gpa": 4.0, "details": ["Relevant coursework or honors"] }} ], "work_experience": [ {{ "job_title": "Job Title", "company": "Company Name", "location": "City, State", "start_date": "Month YYYY", "end_date": "Month YYYY or Present", "responsibilities": ["Responsibility 1 using action verbs", "Responsibility 2 with quantified results"], "achievements": ["Key achievement 1", "Key achievement 2"] }} ], "projects": [ {{ "name": "Project Name", "description": "Detailed project description.", "technologies": ["Tech 1", "Tech 2"], "url": "https://project-url.com", "repository_url": "https://github.com/user/project" }} ], "technical_skills": ["Skill 1", "Skill 2", "Programming Language"], "soft_skills": ["Communication", "Teamwork"], "other_skills": ["Specific tool or methodology"], "languages": [ {{ "language": "Language Name", "proficiency": "e.g., Native, Fluent, Proficient" }} ], "certifications": [ {{ "name": "Certification Name", "issuing_organization": "Org Name", "issue_date": "Month YYYY", "expiration_date": "Month YYYY or Does not expire", "credential_id": "ID123", "credential_url": "https://verify-cert.com" }} ], "awards_honors": ["Award 1", "Honor 2"], "publications": ["Publication title and link/details"], "references_available": true }} 

Pay close attention to extracting dates as strings (e.g., "Month YYYY", "YYYY", or "Present"). For GPA, use a float. For responsibilities, achievements, and details within education, provide lists of strings.
For skills, try to categorize them if possible, but a flat list is acceptable for `technical_skills`, `soft_skills`, and `other_skills`.
Extract as much information as accurately as possible based on the schema.
"""

EXTRACTION_HUMAN_MESSAGE_TEMPLATE = "Here is the resume text to parse:\n\n```text\n{resume_text}\n```\n\nPlease extract the information according to the JSON schema provided in the system message."

ANALYSIS_SYSTEM_MESSAGE = """
You are an expert AI career coach and resume analyst.
Your task is to provide a comprehensive analysis of the given resume data and offer constructive feedback and suggestions.
Format your output STRICTLY as a single JSON object. Do not include any explanatory text before or after the JSON.

The JSON output should have the following structure (use these exact key names):
{{ "resume_rating": {{ "overall_score": 8.5, "comments": "Overall score out of 10 (e.g., 8.5). Brief comment on the score." }}, "strength_areas": ["Well-quantified achievements in X role", "Strong alignment of skills with Y industry"], "improvement_areas": {{ "content_suggestions": ["Elaborate on project Z impact", "Add a dedicated skills section if not prominent"], "formatting_style_suggestions": ["Consider using a more modern template", "Ensure consistent date formatting"], "missing_information_suggestions": ["Include a LinkedIn profile URL if available", "Consider adding a portfolio link for creative roles"] }}, "action_verb_check": {{ "current_usage_rating": "Good", "suggestions": ["Replace 'Responsible for' with stronger verbs like 'Managed', 'Led', 'Developed' in specific sections"] }}, "quantification_check": {{ "current_usage_rating": "Needs Improvement", "suggestions": ["Quantify achievements where possible (e.g., 'Increased sales by X%' instead of just 'Increased sales') for roles A and B"] }}, "upskill_suggestions": [ {{ "skill_name": "Advanced Python for Data Analysis", "reasoning": "Based on your current data science experience, this will open up opportunities in advanced machine learning roles.", "suggested_resources": ["Coursera - Applied Data Science with Python Specialization", "Book: Python for Data Analysis by Wes McKinney"], "relevance_to_career_goals": "High (assuming career goal is Senior Data Scientist)" }}, {{ "skill_name": "Cloud Certification (e.g., AWS Certified Solutions Architect - Associate)", "reasoning": "Cloud skills are highly in demand for most tech roles, including software engineering and data science.", "suggested_resources": ["AWS Training and Certification official site", "A Cloud Guru courses"], "relevance_to_career_goals": "Medium to High (depending on specific target roles)" }} ], "career_path_alignment": {{ "current_alignment_assessment": "Moderately Aligned", "potential_paths": ["Data Scientist", "Machine Learning Engineer", "Data Analyst"], "suggestions_for_strengthening_alignment": ["Tailor your summary to explicitly state your career target (e.g., Data Scientist).", "Highlight projects and experiences that directly relate to your desired career path."] }} }}

Be specific, constructive, and actionable in your feedback. For upskilling, suggest relevant skills, why they are important for the candidate's potential profile, and if possible, general types of resources (e.g., specific online courses, books, platforms).
"""

ANALYSIS_HUMAN_MESSAGE_TEMPLATE = "Please analyze the following resume information:\n\nExtracted Data:\n```json\n{extracted_data_json}\n```\n\n{raw_text_section}Provide your analysis and suggestions based on the JSON schema in the system message."

# Output Parsers
string_output_parser = StrOutputParser()

# Helper function to parse LLM JSON output
def parse_llm_json_output(llm_output: str, context: str) -> Dict[str, Any]:
    try:
        # The LLM might sometimes include markdown ```json ... ``` around the JSON
        if llm_output.strip().startswith("```json"):
            llm_output = llm_output.strip()[7:-3].strip()
        elif llm_output.strip().startswith("```"):
             llm_output = llm_output.strip()[3:-3].strip()

        parsed_json = json.loads(llm_output)
        return parsed_json
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON output from LLM for {context}. Error: {e}. Output: {llm_output}")
        # Fallback or error reporting
        return {"error": "Failed to parse LLM output", "details": str(e), "raw_output": llm_output}
    except Exception as e:
        logger.error(f"An unexpected error occurred during JSON parsing for {context}. Error: {e}. Output: {llm_output}")
        return {"error": "Unexpected error parsing LLM output", "details": str(e), "raw_output": llm_output}

def _invoke_llm_chain_with_retry(chain: Any, params: Dict[str, Any], operation_name: str) -> str:
    """Helper function to invoke LLM chain with retry logic."""
    retry_decorator = tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=60), # Exponential backoff, min 4s, max 60s
        stop=tenacity.stop_after_attempt(5), # Stop after 5 attempts
        retry=(
            tenacity.retry_if_exception_type(ResourceExhausted) | # Retry on Google's ResourceExhausted (429)
            tenacity.retry_if_exception_type(TooManyRequests) | # General 429
            tenacity.retry_if_exception_type(Exception) # Fallback for other transient errors, can be narrowed
        ),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING), # Log retries
        reraise=True # Reraise the last exception if all retries fail
    )
    return retry_decorator(chain.invoke)(params)

def extract_resume_data_from_text(resume_text: str) -> Dict[str, Any]:
    if not llm:
        return {"error": "LLM not initialized"}

    extraction_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(EXTRACTION_SYSTEM_MESSAGE),
        HumanMessagePromptTemplate.from_template(EXTRACTION_HUMAN_MESSAGE_TEMPLATE)
    ])
    
    chain = extraction_prompt | llm | string_output_parser
    
    logger.info("Sending resume text to LLM for data extraction...")
    try:
        response_content = _invoke_llm_chain_with_retry(chain, {"resume_text": resume_text}, "data extraction")
        logger.info("Received extraction response from LLM.")
        # Basic check if response seems like JSON before parsing fully
        if not response_content.strip().startswith("{"):
             logger.warning(f"LLM extraction output does not look like JSON: {response_content[:200]}...") # Log first 200 chars
             # Potentially add specific error key or attempt to find JSON within the string if robustly needed

        extracted_data = parse_llm_json_output(response_content, "resume data extraction")
        return extracted_data
    except ResourceExhausted as e: # Specifically catch ResourceExhausted if it's reraised
        logger.error(f"Rate limit exceeded during LLM data extraction chain after retries: {e}")
        return {"error": "LLM rate limit exceeded", "details": str(e)}
    except Exception as e:
        logger.error(f"Error during LLM data extraction chain: {e}")
        return {"error": "LLM chain invocation failed for extraction", "details": str(e)}

def analyze_resume_content(extracted_data_dict: Dict[str, Any], raw_resume_text: Optional[str] = None) -> Dict[str, Any]:
    if not llm:
        return {"error": "LLM not initialized"}

    analysis_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(ANALYSIS_SYSTEM_MESSAGE),
        HumanMessagePromptTemplate.from_template(ANALYSIS_HUMAN_MESSAGE_TEMPLATE)
    ])

    chain = analysis_prompt | llm | string_output_parser

    raw_text_section_content = ""
    if raw_resume_text:
        raw_text_section_content = f"Full Resume Text (for context):\n```text\n{raw_resume_text}\n```"

    # Convert extracted_data_dict to JSON string for the prompt
    extracted_data_json_str = json.dumps(extracted_data_dict, indent=2)

    logger.info("Sending extracted data (and optionally raw text) to LLM for analysis...")
    try:
        response_content = _invoke_llm_chain_with_retry(
            chain,
            {
                "extracted_data_json": extracted_data_json_str,
                "raw_text_section": raw_text_section_content
            },
            "resume analysis"
        )
        logger.info("Received analysis response from LLM.")
        if not response_content.strip().startswith("{"):
             logger.warning(f"LLM analysis output does not look like JSON: {response_content[:200]}...")

        analysis_result = parse_llm_json_output(response_content, "resume analysis")
        return analysis_result
    except ResourceExhausted as e: # Specifically catch ResourceExhausted if it's reraised
        logger.error(f"Rate limit exceeded during LLM analysis chain after retries: {e}")
        return {"error": "LLM rate limit exceeded for analysis", "details": str(e)}
    except Exception as e:
        logger.error(f"Error during LLM analysis chain: {e}")
        return {"error": "LLM chain invocation failed for analysis", "details": str(e)}

# Example Usage (for testing purposes, can be removed or placed in a test file)
# if __name__ == "__main__":
#     if not settings.GOOGLE_API_KEY:
#         print("Please set your GOOGLE_API_KEY in a .env file (see .env.example)")
#     else:
#         sample_resume_text = """
#         John Doe
#         john.doe@email.com | (123) 456-7890 | linkedin.com/in/johndoe

#         Summary
#         Experienced software engineer with a passion for developing innovative solutions.

#         Experience
#         Software Engineer, Tech Solutions Inc. (Jan 2020 - Present)
#         - Developed and maintained web applications using Python and React.
#         - Led a team of 3 junior developers.
        
#         Education
#         M.S. in Computer Science, State University (2018-2020)
#         B.S. in Software Engineering, Tech Institute (2014-2018)
#         GPA: 3.8

#         Skills
#         Python, Java, JavaScript, React, Node.js, SQL, Docker, AWS
#         """
        
#         print("--- Testing Resume Data Extraction ---")
#         extracted_info = extract_resume_data_from_text(sample_resume_text)
#         print(json.dumps(extracted_info, indent=2))

#         if extracted_info and "error" not in extracted_info:
#             print("\n--- Testing Resume Analysis ---")
#             analysis = analyze_resume_content(extracted_info, raw_resume_text=sample_resume_text)
#             print(json.dumps(analysis, indent=2))
#         else:
#             print("\nSkipping analysis due to extraction error or no data.") 