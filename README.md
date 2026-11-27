# STUDIGENCE AI – AI-Powered Intelligent Study Assistant

<p align="center">
  <b>An All-in-One AI-Powered Learning, Academic Productivity and Career Development Platform</b>
</p>

<p align="center">
  Python 3.10+ | Streamlit | SQLite | Google Gemini API
</p>

<p align="center">
  <a href="https://studigence-ai.streamlit.app/">Live Demo</a> •
  <a href="https://github.com/Habibah-04/STUDIGENCE_AI">GitHub Repository</a>
</p>

---

## About the Project

**STUDIGENCE AI** is an AI-powered intelligent study assistant developed as an MCA mini project. It provides an integrated platform for academic learning, examination preparation, study planning, performance monitoring, career development and educational content creation.

Students often depend on multiple applications for accessing study resources, preparing notes, practising questions, organizing assignments and developing professional skills.

STUDIGENCE AI addresses this problem by bringing these activities together in one web-based application.

The system is developed using Python and Streamlit, with SQLite for persistent local data storage and Google's Gemini API for AI-assisted functionalities.

It includes **15 major learning and productivity modules**, along with an additional Creative Studio.

## Key Features

### 15 Core Modules

| No. | Module | Description |
|---|---|---|
| 1 | Dashboard | Displays learning activity, upcoming tasks, quiz trends and progress. |
| 2 | AI Study Tutor | Provides level-based explanations, examples, analogies and code walkthroughs. |
| 3 | Teach-back Loop | Allows students to explain concepts in their own words and receive structured feedback. |
| 4 | PDF Lab | Extracts selectable PDF text and supports summaries and practice-question generation. |
| 5 | Exam & Quiz Center | Provides topic-based quizzes, automatic scoring, explanations and attempt history. |
| 6 | Study Planner | Manages study tasks, priorities, deadlines and completion status. |
| 7 | Learning DNA | Analyses topic-wise performance using recorded quiz attempts. |
| 8 | Mistake DNA | Records incorrect answers and helps identify topics requiring revision. |
| 9 | Memory & Revision | Maintains a spaced-repetition-based revision queue. |
| 10 | Career Intelligence | Provides career roadmaps, skill suggestions and interview preparation guidance. |
| 11 | Resume Studio | Supports resume creation, preview, export and AI-assisted feedback. |
| 12 | Skill Gap Analyzer | Compares self-assessed current and target skill levels. |
| 13 | YouTube Learning Finder | Generates focused educational video searches. |
| 14 | Notes & Assignment Studio | Supports study-note management and assignment structure generation. |
| 15 | Focus Room & Analytics | Records focus sessions and provides learning and productivity reports. |

### Creative Studio

The additional Creative Studio provides educational content creation facilities:

- **Image-to-PDF Converter:** Converts multiple supported images into a single PDF.
- **AI Topic Diagram Generator:** Generates topic diagrams with downloadable PNG and editable Mermaid source.
- **Study PDF Generator:** Creates formatted educational PDFs from text prompts.
- **PowerPoint Generator:** Generates presentations containing approximately 4–15 slides.
- **Image Notes Assistant:** Uses a vision-capable Gemini model to explain or simplify uploaded study-note images.

## What Makes STUDIGENCE AI Different?

### 1. Teach-back Loop

Students do not simply read AI-generated explanations. They explain a topic in their own words and receive feedback covering:

- Correct concepts.
- Missing or unclear information.
- Suggested corrections.
- Follow-up questions.

### 2. Learning DNA and Mistake DNA

The system uses recorded quiz attempts and incorrect answers to help learners identify topics requiring additional practice.

### 3. Integrated Academic and Career Support

The platform combines learning assistance, revision, academic productivity, resume creation and career preparation.

### 4. Offline-First Core Functionality

Account management, study planning, notes, quiz records, revision and activity tracking use local application functionality and SQLite.

AI-generated content requires a valid Gemini API configuration.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Main programming language |
| Streamlit | Web application framework |
| SQLite | Relational database |
| Google Gemini API | AI-powered learning and content generation |
| google-genai | Official Gemini Python SDK |
| pandas | Data processing and analysis |
| PyMuPDF | PDF text extraction |
| python-dotenv | Environment configuration |
| Plotly | Interactive visualizations |
| Matplotlib | Diagram generation |
| Pillow | Image processing |
| ReportLab | PDF generation |
| python-pptx | PowerPoint generation |
| pytest | Testing |

## System Architecture

The application follows a modular architecture:

1. **Presentation Layer:** Streamlit-based user interface.
2. **Application Logic Layer:** Handles learning modules and user operations.
3. **Database Layer:** SQLite stores user accounts and learning activities.
4. **AI Integration Layer:** Google Gemini API handles AI-dependent operations.
5. **Supporting Utilities:** Python libraries support document processing, visualization and content generation.

## Project Structure

```text
STUDIGENCE_AI/
│
├── app.py
│
├── src/
│   ├── db.py
│   ├── ai.py
│   ├── advanced.py
│   ├── pages.py
│   ├── content.py
│   └── ui.py
│
├── pages/
├── assets/
├── data/
├── tests/
├── .streamlit/
│
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
├── run_windows.bat
├── run_mac_linux.sh
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.10 or later.
- Recommended Python version: 3.11.
- Git.
- A modern web browser.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Habibah-04/STUDIGENCE_AI.git
```

### Step 2: Navigate to the Project Directory

```bash
cd STUDIGENCE_AI
```

### Step 3: Create a Virtual Environment

```bash
py -3.11 -m venv .venv
```

### Step 4: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

For Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

For Linux/macOS:

```bash
source .venv/bin/activate
```

### Step 5: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal:

```text
http://localhost:8501
```

## Google Gemini API Configuration

STUDIGENCE AI uses Google's Gemini API through the `google-genai` Python SDK.

AI-dependent features require a valid Gemini API key.

### Step 1: Generate an API Key

Visit Google AI Studio:

https://aistudio.google.com/apikey

Create an API key for your application.

### Step 2: Configure Environment Variables

Create a `.env` file in the project root directory.

Add:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Replace the placeholder with your actual API key.

The model name should be kept consistent with the model configured in your application.

### Step 3: Restart the Application

```bash
streamlit run app.py
```

**Security Notice:**

- Never upload your `.env` file to GitHub.
- Never expose your Gemini API key in screenshots or source code.
- Use Streamlit Secrets when deploying online.
- API usage may be subject to Google's quota and billing policies.

## Deploy on Streamlit Community Cloud

1. Push the project to your GitHub repository.
2. Visit https://share.streamlit.io/
3. Sign in using GitHub.
4. Select **Create App**.
5. Choose the repository `Habibah-04/STUDIGENCE_AI`.
6. Select the `main` branch.
7. Set the main file path to `app.py`.
8. Select Python 3.11 if available.
9. Open Advanced Settings and configure the required secrets.
10. Deploy the application.

### Streamlit Secrets Configuration

Add the following in the application's Secrets section:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

After deployment, test account creation, login, quizzes, study tasks, notes and AI-dependent features.

**Deployment:** https://studigence-ai.streamlit.app/

### Important Database Consideration

The current application uses SQLite, which is suitable for local development and prototype demonstrations.

Files stored on Streamlit Community Cloud may not be durable across restarts or redeployments. For production use with multiple users, a managed database such as PostgreSQL and private document storage are recommended.

## Important Implementation Boundaries

STUDIGENCE AI is an academic software prototype, not a production-certified adaptive learning system.

- Learning DNA uses recorded quiz performance; it does not use a separately trained predictive ML model.
- Skill Gap Analyzer is based on user-provided self-assessment.
- PDF Lab extracts selectable text and does not include OCR for scanned PDFs.
- YouTube Learning Finder generates search links; it does not independently verify or rank videos.
- Focus Room records completed focus sessions; it does not perform background website monitoring.
- AI-generated responses may contain inaccurate information and should be verified against academic resources.
- AI-dependent features require a valid Gemini API key and internet connectivity.
- Production-grade vector-based RAG, live job scraping, institutional integrations and proctored examinations are not included in the current implementation.

## Testing

The project includes a testing directory and uses pytest for automated testing.

To execute the available test suite:

```bash
pytest -v
```

Only tests that have actually been executed should be reported as passed.

## Future Scope

Potential enhancements include:

- Advanced document-based RAG.
- OCR support for scanned documents.
- Mobile application development.
- Cloud database migration.
- Multilingual AI tutoring.
- Enhanced personalized learning analytics.
- Institutional LMS integration.
- Collaborative study groups.
- Improved account and session security.

## Project Information

| Field | Details |
|---|---|
| Project Name | STUDIGENCE AI |
| Project Type | MCA Mini Project |
| Student | Habibah Qamar |
| Course | Master of Computer Applications |
| Institute | KIPM – College of Management, GIDA, Gorakhpur |
| University | Dr. A.P.J. Abdul Kalam Technical University, Lucknow |
| Academic Session | 2026–2027 |
| Project Guide | Mr. Hrishikesh Tripathi |

## Author

**Habibah Qamar**

GitHub: https://github.com/Habibah-04

Portfolio: https://myportfolio-auif.onrender.com

---

## Acknowledgement

This project uses Python, Streamlit, SQLite, Google Gemini API and several open-source Python libraries.

Special thanks to the developers and communities behind these technologies for providing documentation and resources that supported the development of STUDIGENCE AI.

---

<p align="center">
  <b>STUDIGENCE AI – Learn Smarter. Prepare Better. Grow Further.</b>
</p>
