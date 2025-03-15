import streamlit as st
from datetime import datetime
from config import Config
from service import InterviewService
from models import InterviewSession

def initialize_session_state():
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "questions_asked" not in st.session_state:
        st.session_state.questions_asked = 0
    if "correct_answers" not in st.session_state:
        st.session_state.correct_answers = 0
    if "improvement_areas" not in st.session_state:
        st.session_state.improvement_areas = []
    if "language" not in st.session_state:
        st.session_state.language = "EN"
    if "answer_submitted" not in st.session_state:
        st.session_state.answer_submitted = False
    if "needs_new_question" not in st.session_state:
        st.session_state.needs_new_question = False
    if "previous_questions" not in st.session_state:
        st.session_state.previous_questions = []
    if "current_answer" not in st.session_state:
        st.session_state.current_answer = ""

def get_next_question():
    st.session_state.needs_new_question = True
    st.session_state.answer_submitted = False
    st.session_state.current_answer = ""  # Clear the answer
    st.rerun()

def main():
    st.title("Data Science Interview Coach 🎓")
    
    # Initialize service and session state
    service = InterviewService()
    initialize_session_state()
    
    # Sidebar for settings
    st.sidebar.header("Interview Settings")
    
    # Language selection
    selected_language = st.sidebar.selectbox(
        "Select Language / Выберите язык",
        list(Config.LANGUAGES.keys()),
        format_func=lambda x: x,
        index=0 if st.session_state.language == "EN" else 1
    )
    st.session_state.language = Config.LANGUAGES[selected_language]
    
    # Topic and difficulty selection
    selected_topic = st.sidebar.selectbox(
        "Select Topic" if st.session_state.language == "EN" else "Выберите тему",
        Config.TOPICS
    )
    difficulty = st.sidebar.selectbox(
        "Select Difficulty" if st.session_state.language == "EN" else "Выберите уровень сложности",
        Config.DIFFICULTY_LEVELS
    )
    
    # Show previous progress if available
    progress = service.get_topic_progress(selected_topic, st.session_state.language)
    if progress:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Your Progress" if st.session_state.language == "EN" else "Ваш прогресс")
        st.sidebar.write(f"{'Current Level' if st.session_state.language == 'EN' else 'Текущий уровень'}: {progress.skill_level}")
        st.sidebar.write(f"{'Confidence Score' if st.session_state.language == 'EN' else 'Оценка уверенности'}: {progress.confidence_score:.2f}")
        st.sidebar.markdown("**" + ("Recommended Focus Areas" if st.session_state.language == "EN" else "Рекомендуемые темы для изучения") + ":**")
        for topic in progress.recommended_topics:
            st.sidebar.markdown(f"- {topic}")
    
    # Display current progress
    if st.session_state.questions_asked > 0:
        st.info(
            f"{'Questions completed' if st.session_state.language == 'EN' else 'Вопросов завершено'}: "
            f"{st.session_state.questions_asked}/{Config.QUESTIONS_PER_SESSION} | "
            f"{'Correct answers' if st.session_state.language == 'EN' else 'Правильных ответов'}: "
            f"{st.session_state.correct_answers}"
        )
    
    # Check if we need to generate a new question
    if st.session_state.needs_new_question:
        # If there's a current question, add it to previous questions
        if st.session_state.current_question:
            st.session_state.previous_questions.append(st.session_state.current_question)
            
        st.session_state.current_question = service.generate_question(
            selected_topic,
            difficulty,
            st.session_state.language,
            st.session_state.previous_questions
        )
        st.session_state.needs_new_question = False
    
    # Main interview interface
    if st.session_state.current_question is None:
        if st.button("Start New Question" if st.session_state.language == "EN" else "Начать новый вопрос"):
            st.session_state.needs_new_question = True
            st.session_state.previous_questions = []  # Reset previous questions for new session
            st.session_state.current_answer = ""  # Clear the answer
            st.rerun()
    
    else:
        # Display current question
        st.markdown("### " + ("Question" if st.session_state.language == "EN" else "Вопрос") + ":")
        st.write(st.session_state.current_question.question_text)
        
        # Get user's answer with a key that changes when question changes
        answer_key = f"answer_{st.session_state.questions_asked}"
        user_answer = st.text_area(
            "Your Answer" if st.session_state.language == "EN" else "Ваш ответ",
            value=st.session_state.current_answer,
            key=answer_key
        )
        # Update the current answer in session state
        st.session_state.current_answer = user_answer
        
        # Create two columns for buttons
        col1, col2 = st.columns(2)
        
        # Submit answer button
        if not st.session_state.answer_submitted:
            if col1.button("Submit Answer" if st.session_state.language == "EN" else "Отправить ответ"):
                evaluation = service.evaluate_answer(
                    st.session_state.current_question,
                    user_answer,
                    st.session_state.language
                )
                
                # Display feedback
                if evaluation["is_correct"]:
                    st.success("Correct! 🎉" if st.session_state.language == "EN" else "Правильно! 🎉")
                    st.session_state.correct_answers += 1
                else:
                    st.error("Not quite right." if st.session_state.language == "EN" else "Не совсем правильно.")
                
                st.markdown("### " + ("Explanation" if st.session_state.language == "EN" else "Объяснение"))
                st.write(evaluation["explanation"])
                
                st.markdown("### " + ("Tips for Improvement" if st.session_state.language == "EN" else "Советы для улучшения"))
                st.write(evaluation["improvement_tips"])
                
                # Update session stats
                st.session_state.questions_asked += 1
                if "improvement_tips" in evaluation:
                    st.session_state.improvement_areas.append(evaluation["improvement_tips"])
                
                st.session_state.answer_submitted = True
                
                # Check if session should end
                if st.session_state.questions_asked >= Config.QUESTIONS_PER_SESSION:
                    # Save session data
                    session = InterviewSession(
                        topic=selected_topic,
                        timestamp=datetime.now(),
                        questions_asked=st.session_state.questions_asked,
                        correct_answers=st.session_state.correct_answers,
                        difficulty_level=difficulty,
                        language=st.session_state.language,
                        areas_for_improvement=st.session_state.improvement_areas
                    )
                    service.save_session(session)
                    
                    # Update progress
                    progress = service.analyze_performance(
                        selected_topic,
                        session,
                        st.session_state.language
                    )
                    service.update_progress(progress)
                    
                    # Reset session state
                    st.session_state.current_question = None
                    st.session_state.questions_asked = 0
                    st.session_state.correct_answers = 0
                    st.session_state.improvement_areas = []
                    st.session_state.answer_submitted = False
                    st.session_state.needs_new_question = False
                    st.session_state.previous_questions = []  # Reset previous questions list
                    st.session_state.current_answer = ""  # Clear the answer
                    
                    st.success(
                        "Session completed! Check your progress in the sidebar." 
                        if st.session_state.language == "EN" 
                        else "Сессия завершена! Проверьте свой прогресс в боковой панели."
                    )
                    st.rerun()
        
        # Next question button
        if st.session_state.answer_submitted and st.session_state.questions_asked < Config.QUESTIONS_PER_SESSION:
            if col2.button("Next Question" if st.session_state.language == "EN" else "Следующий вопрос"):
                get_next_question()

if __name__ == "__main__":
    main() 