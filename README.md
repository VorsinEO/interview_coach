# Data Science Interview Coach 🎓

An intelligent interview preparation system for data science and machine learning topics, powered by OpenAI's language models. The application provides an interactive environment for practicing interview questions, receiving instant feedback, and tracking your progress.

## Features

- 🌍 Bilingual Support: English and Russian
- 📚 Multiple Topics:
  - Python Programming
  - SQL
  - Machine Learning and Deep Learning
  - Statistics
- 🎯 Adaptive Learning:
  - Tracks mastered subtopics
  - Avoids repetitive questions
  - Focuses on areas needing improvement
- 📊 Progress Tracking:
  - Session history
  - Performance analytics
  - Skill level assessment
  - Confidence scoring
- 🔄 Interactive Sessions:
  - Real-time feedback
  - Detailed explanations
  - Improvement tips
  - Customizable difficulty levels

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/interview_coach.git
cd interview_coach
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your OpenAI API key:
```env
OPEN_AI_API_KEY='your-api-key-here'
OPEN_AI_MODEL='gpt-3.5-turbo'  # or your preferred model
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided URL (typically http://localhost:8501)

3. In the sidebar:
   - Select your preferred language
   - Choose a topic
   - Set the difficulty level

4. Click "Start New Question" to begin your interview session

5. For each question:
   - Type your answer in the text area
   - Click "Submit Answer" to receive feedback
   - Review the explanation and improvement tips
   - Click "Next Question" to continue

6. After completing a session:
   - Review your progress in the sidebar
   - Check recommended focus areas
   - Start a new session if desired

## Features in Detail

### Adaptive Learning System
- Tracks your performance in specific subtopics
- Marks topics as mastered when achieving 85% proficiency
- Generates new questions focusing on non-mastered areas
- Maintains progress across sessions

### Progress Tracking
- Stores session history in JSON format
- Tracks correct answers and areas for improvement
- Calculates confidence scores per topic
- Provides personalized learning recommendations

### Bilingual Support
- Full support for English and Russian
- Language-specific feedback and explanations
- Maintains separate progress tracking per language

## Project Structure

```
interview_coach/
├── app.py              # Main Streamlit application
├── config.py           # Configuration settings
├── models.py           # Data models
├── service.py          # Business logic and OpenAI integration
├── requirements.txt    # Project dependencies
├── .env               # Environment variables (not in repo)
└── interview_history.json  # User progress (not in repo)
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT API
- Streamlit for the web application framework
- All contributors and users of the application 