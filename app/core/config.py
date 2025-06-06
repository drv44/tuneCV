import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file at the earliest opportunity
# This will ensure that environment variables are available when settings are loaded
# Construct the path to the .env file relative to this config.py file
# Assuming .env is in the tuneCV/ directory, and config.py is in tuneCV/app/core/

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "TuneCV"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    # DATABASE_URL: str | None = DATABASE_URL
    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")

    # Optional: Add more settings as needed, e.g., for LLM model name
    # GEMINI_MODEL_NAME: str = "gemini-pro" 

    class Config:
        case_sensitive = True
        # If you are not using a .env file for some deployments,
        # Pydantic can still try to load from environment variables directly.
        # env_file = ".env" # Pydantic-settings uses find_dotenv by default if env_file is not specified.
        # extra = "ignore" # To ignore extra fields from .env that are not in the model

settings = Settings()

if settings.DATABASE_URL is None:
    print("Warning: DATABASE_URL is not set. Please check your .env file or environment variables.")
if settings.GOOGLE_API_KEY is None:
    print("Warning: GOOGLE_API_KEY is not set. Please check your .env file or environment variables.") 