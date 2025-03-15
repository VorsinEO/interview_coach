from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InterviewSession(BaseModel):
    topic: str
    timestamp: datetime
    questions_asked: int
    correct_answers: int
    difficulty_level: str
    language: str
    areas_for_improvement: List[str]
    mastered_subtopics: List[str] = []  # Track mastered subtopics in each session
    
class UserProgress(BaseModel):
    topic: str
    skill_level: str
    confidence_score: float
    last_session: Optional[datetime]
    language: str
    recommended_topics: List[str]
    mastered_subtopics: List[str] = []  # Track overall mastered subtopics
    subtopic_scores: dict[str, float] = {}  # Track proficiency scores for each subtopic
    
class Question(BaseModel):
    question_text: str
    correct_answer: str
    explanation: str
    difficulty: str
    topic: str
    subtopic: str 