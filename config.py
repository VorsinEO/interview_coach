from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPEN_AI_API_KEY')
    OPENAI_MODEL = os.getenv('OPEN_AI_MODEL', 'gpt-3.5-turbo')  # Default model if not specified
    
    LANGUAGES = {
        "English": "EN",
        "Russian": "RU"
    }
    
    TOPICS = [
        "Python",
        "SQL",
        "Machine Learning and Deep Learning",
        "Statistics"
    ]
    
    DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced"]
    
    # Number of questions per session
    QUESTIONS_PER_SESSION = 5
    
    # History file path - store in user's home directory
    HISTORY_FILE = str(Path.cwd() / "interview_history.json") 