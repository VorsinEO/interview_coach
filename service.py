from openai import OpenAI
import json
from datetime import datetime
from typing import List, Dict
from config import Config
from models import Question, InterviewSession, UserProgress

class InterviewService:
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY
        )
        self.history = self._load_history()
    
    def _get_language_prompt(self, language: str) -> str:
        return "Answer in Russian language." if language == "RU" else "Answer in English language."
    
    def _serialize_datetime(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')
    
    def _deserialize_datetime(self, data: Dict) -> Dict:
        if "sessions" in data:
            for session in data["sessions"]:
                if "timestamp" in session:
                    session["timestamp"] = datetime.fromisoformat(session["timestamp"])
        if "progress" in data:
            for progress in data["progress"].values():
                if "last_session" in progress and progress["last_session"]:
                    progress["last_session"] = datetime.fromisoformat(progress["last_session"])
        return data
    
    def _load_history(self) -> Dict:
        try:
            with open(Config.HISTORY_FILE, 'r') as f:
                data = json.load(f)
                return self._deserialize_datetime(data)
        except FileNotFoundError:
            return {"sessions": [], "progress": {}}
    
    def _save_history(self):
        with open(Config.HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, default=self._serialize_datetime, indent=2)
    
    def generate_question(self, topic: str, difficulty: str, language: str, previous_questions: List[Question] = None) -> Question:
        lang_prompt = self._get_language_prompt(language)
        
        # Get user progress to check mastered subtopics
        progress = self.get_topic_progress(topic, language)
        mastered_subtopics_text = ""
        if progress and progress.mastered_subtopics:
            mastered_subtopics_text = "\nMastered subtopics (avoid these):\n"
            for subtopic in progress.mastered_subtopics:
                mastered_subtopics_text += f"- {subtopic}\n"
        
        # Create a string of previous questions if they exist
        previous_questions_text = ""
        if previous_questions and len(previous_questions) > 0:
            previous_questions_text = "\nPrevious questions in this session:\n"
            for i, q in enumerate(previous_questions, 1):
                previous_questions_text += f"{i}. Question: {q.question_text}\n   Topic: {q.topic}\n   Subtopic: {q.subtopic}\n"
        
        prompt = f"""{lang_prompt}
        Generate an interview question for a Data Scientist position with the following criteria:
        Topic: {topic}
        Difficulty: {difficulty}
        
        {mastered_subtopics_text}
        {previous_questions_text}
        Important requirements:
        1. The question must be significantly different from any previous questions shown above
        2. If previous questions covered certain subtopics, focus on different subtopics
        3. DO NOT generate questions about mastered subtopics listed above
        4. The question should be unique in both content and the specific skills it tests
        5. Choose a subtopic that the student hasn't mastered yet
        
        Format the response as a JSON with the following fields:
        - question_text
        - correct_answer
        - explanation
        - difficulty
        - topic
        - subtopic"""
        
        response = self.client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        
        question_data = json.loads(response.choices[0].message.content)
        return Question(**question_data)
    
    def evaluate_answer(self, question: Question, user_answer: str, language: str) -> Dict:
        lang_prompt = self._get_language_prompt(language)
        prompt = f"""{lang_prompt}
        Question: {question.question_text}
        Correct Answer: {question.correct_answer}
        User's Answer: {user_answer}
        Subtopic: {question.subtopic}
        
        Evaluate the user's answer and provide:
        1. Whether it's correct (true/false)
        2. A detailed explanation
        3. Additional tips for improvement
        4. Proficiency score for this subtopic (0.0 to 1.0)
        
        Format the response as JSON with fields: is_correct, explanation, improvement_tips, subtopic_score"""
        
        response = self.client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        
        evaluation = json.loads(response.choices[0].message.content)
        
        # Update progress with subtopic score
        progress = self.get_topic_progress(question.topic, language)
        if progress:
            subtopic = question.subtopic
            current_score = progress.subtopic_scores.get(subtopic, 0.0)
            new_score = (current_score + evaluation["subtopic_score"]) / 2
            progress.subtopic_scores[subtopic] = new_score
            
            # If subtopic score is high enough, mark it as mastered
            if new_score >= 0.85:  # 85% proficiency threshold
                if subtopic not in progress.mastered_subtopics:
                    progress.mastered_subtopics.append(subtopic)
            
            self.update_progress(progress)
        
        return evaluation
    
    def analyze_performance(self, topic: str, session_data: InterviewSession, language: str) -> UserProgress:
        lang_prompt = self._get_language_prompt(language)
        
        # Get existing progress to preserve mastered subtopics
        existing_progress = self.get_topic_progress(topic, language)
        mastered_subtopics = []
        subtopic_scores = {}
        
        if existing_progress:
            mastered_subtopics = existing_progress.mastered_subtopics
            subtopic_scores = existing_progress.subtopic_scores
        
        prompt = f"""{lang_prompt}
        Based on the following interview session data:
        Topic: {topic}
        Questions Asked: {session_data.questions_asked}
        Correct Answers: {session_data.correct_answers}
        Difficulty Level: {session_data.difficulty_level}
        
        Provide:
        1. Current skill level (Beginner/Intermediate/Advanced)
        2. Confidence score (0-1)
        3. List of recommended topics for improvement
        
        Format the response as JSON with fields: skill_level, confidence_score, recommended_topics"""
        
        response = self.client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = json.loads(response.choices[0].message.content)
        return UserProgress(
            topic=topic,
            last_session=datetime.now(),
            language=language,
            mastered_subtopics=mastered_subtopics,
            subtopic_scores=subtopic_scores,
            **analysis
        )
    
    def save_session(self, session: InterviewSession):
        session_dict = session.model_dump()
        self.history["sessions"].append(session_dict)
        self._save_history()
    
    def update_progress(self, progress: UserProgress):
        key = f"{progress.topic}_{progress.language}"
        self.history["progress"][key] = progress.model_dump()
        self._save_history()
    
    def get_topic_progress(self, topic: str, language: str) -> UserProgress:
        key = f"{topic}_{language}"
        if key in self.history["progress"]:
            return UserProgress(**self.history["progress"][key])
        return None 