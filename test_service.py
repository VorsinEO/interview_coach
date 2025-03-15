import unittest
from datetime import datetime
from pathlib import Path
import json
import os
from service import InterviewService
from models import InterviewSession, UserProgress, Question
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestInterviewService(unittest.TestCase):
    def setUp(self):
        logger.info("Setting up test environment...")
        # Create a temporary history file for testing
        self.test_history_file = "test_history.json"
        Config.HISTORY_FILE = self.test_history_file
        logger.debug(f"Using test history file: {self.test_history_file}")
        logger.debug(f"OpenAI API Key present: {'Yes' if Config.OPENAI_API_KEY else 'No'}")
        self.service = InterviewService()

    def tearDown(self):
        logger.info("Cleaning up test environment...")
        # Clean up the test history file
        if os.path.exists(self.test_history_file):
            os.remove(self.test_history_file)
            logger.debug(f"Removed test history file: {self.test_history_file}")

    def test_save_and_load_session_with_datetime(self):
        logger.info("Testing save and load session with datetime...")
        try:
            # Create a test session
            session = InterviewSession(
                topic="Python",
                timestamp=datetime.now(),
                questions_asked=5,
                correct_answers=3,
                difficulty_level="Intermediate",
                language="EN",
                areas_for_improvement=["List comprehension", "Decorators"]
            )
            logger.debug(f"Created test session: {session}")

            # Save the session
            self.service.save_session(session)
            logger.debug("Session saved successfully")

            # Verify the file exists
            self.assertTrue(os.path.exists(self.test_history_file))
            logger.debug("History file exists")

            # Read the raw JSON to verify datetime serialization
            with open(self.test_history_file, 'r') as f:
                raw_data = json.load(f)
                logger.debug(f"Raw JSON data: {raw_data}")
            
            # Check if the session was saved
            self.assertEqual(len(raw_data["sessions"]), 1)
            saved_session = raw_data["sessions"][0]
            logger.debug(f"Saved session data: {saved_session}")

            # Verify datetime was serialized as string
            self.assertIsInstance(saved_session["timestamp"], str)
            logger.debug(f"Timestamp serialized as: {saved_session['timestamp']}")

            # Load the history again
            new_service = InterviewService()
            loaded_session = new_service.history["sessions"][0]
            logger.debug(f"Loaded session data: {loaded_session}")

            # Verify datetime was deserialized
            self.assertIsInstance(loaded_session["timestamp"], datetime)
            logger.debug("Test completed successfully")
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            raise

    def test_save_and_load_progress(self):
        logger.info("Testing save and load progress...")
        try:
            # Create a test progress
            progress = UserProgress(
                topic="Python",
                skill_level="Intermediate",
                confidence_score=0.75,
                last_session=datetime.now(),
                language="EN",
                recommended_topics=["Generators", "Context Managers"]
            )
            logger.debug(f"Created test progress: {progress}")

            # Save the progress
            self.service.update_progress(progress)
            logger.debug("Progress saved successfully")

            # Verify the file exists
            self.assertTrue(os.path.exists(self.test_history_file))
            logger.debug("History file exists")

            # Read the raw JSON to verify datetime serialization
            with open(self.test_history_file, 'r') as f:
                raw_data = json.load(f)
                logger.debug(f"Raw JSON data: {raw_data}")
            
            # Check if the progress was saved
            key = f"{progress.topic}_{progress.language}"
            self.assertIn(key, raw_data["progress"])
            saved_progress = raw_data["progress"][key]
            logger.debug(f"Saved progress data: {saved_progress}")

            # Verify datetime was serialized as string
            self.assertIsInstance(saved_progress["last_session"], str)
            logger.debug(f"Last session serialized as: {saved_progress['last_session']}")

            # Load the history again
            new_service = InterviewService()
            loaded_progress = new_service.get_topic_progress("Python", "EN")
            logger.debug(f"Loaded progress data: {loaded_progress}")

            # Verify datetime was deserialized
            self.assertIsInstance(loaded_progress.last_session, datetime)
            self.assertEqual(loaded_progress.skill_level, "Intermediate")
            self.assertEqual(loaded_progress.confidence_score, 0.75)
            logger.debug("Test completed successfully")
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            raise

    def test_multiple_sessions_and_progress(self):
        logger.info("Testing multiple sessions and progress...")
        try:
            # Create and save multiple sessions and progress
            for i in range(3):
                session = InterviewSession(
                    topic=f"Topic{i}",
                    timestamp=datetime.now(),
                    questions_asked=5,
                    correct_answers=i+2,
                    difficulty_level="Intermediate",
                    language="EN",
                    areas_for_improvement=[f"Area{i}"]
                )
                self.service.save_session(session)
                logger.debug(f"Saved session {i}: {session}")

                progress = UserProgress(
                    topic=f"Topic{i}",
                    skill_level="Intermediate",
                    confidence_score=0.5 + i*0.1,
                    last_session=datetime.now(),
                    language="EN",
                    recommended_topics=[f"Topic{i}"]
                )
                self.service.update_progress(progress)
                logger.debug(f"Saved progress {i}: {progress}")

            # Read the raw JSON
            with open(self.test_history_file, 'r') as f:
                raw_data = json.load(f)
                logger.debug(f"Raw JSON data: {raw_data}")
            
            # Verify multiple sessions were saved
            self.assertEqual(len(raw_data["sessions"]), 3)
            self.assertEqual(len(raw_data["progress"]), 3)
            logger.debug(f"Verified counts: {len(raw_data['sessions'])} sessions, {len(raw_data['progress'])} progress entries")

            # Load and verify all data
            new_service = InterviewService()
            self.assertEqual(len(new_service.history["sessions"]), 3)
            self.assertEqual(len(new_service.history["progress"]), 3)
            logger.debug("Test completed successfully")
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            raise

    def test_mastered_subtopics(self):
        logger.info("Testing mastered subtopics functionality...")
        try:
            # Create initial progress with some mastered subtopics
            progress = UserProgress(
                topic="Python",
                skill_level="Intermediate",
                confidence_score=0.75,
                last_session=datetime.now(),
                language="EN",
                recommended_topics=["Advanced Topics"],
                mastered_subtopics=["List Comprehension", "Basic Functions"],
                subtopic_scores={
                    "List Comprehension": 0.9,
                    "Basic Functions": 0.95,
                    "Decorators": 0.6
                }
            )
            self.service.update_progress(progress)
            logger.debug(f"Created initial progress: {progress}")

            # Create a question and simulate a correct answer
            question = Question(
                question_text="What are decorators in Python?",
                correct_answer="Decorators are functions that modify other functions",
                explanation="Decorators are a way to modify functions",
                difficulty="Intermediate",
                topic="Python",
                subtopic="Decorators"
            )

            # Simulate multiple good answers to master the subtopic
            for _ in range(3):
                evaluation = self.service.evaluate_answer(
                    question=question,
                    user_answer="Decorators are functions that modify other functions or classes, allowing you to add functionality without changing the original code.",
                    language="EN"
                )
                logger.debug(f"Evaluation result: {evaluation}")

            # Get updated progress
            updated_progress = self.service.get_topic_progress("Python", "EN")
            logger.debug(f"Updated progress: {updated_progress}")

            # Verify that Decorators is now in mastered subtopics
            self.assertIn("Decorators", updated_progress.mastered_subtopics)
            self.assertGreaterEqual(updated_progress.subtopic_scores["Decorators"], 0.85)

            # Verify original mastered subtopics are preserved
            self.assertIn("List Comprehension", updated_progress.mastered_subtopics)
            self.assertIn("Basic Functions", updated_progress.mastered_subtopics)

            logger.debug("Test completed successfully")
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main() 