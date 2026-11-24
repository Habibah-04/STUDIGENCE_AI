# STUDIGENCE AI — Robo-powered MCA learning studio

**Python 3.10+ · Streamlit · SQLite · Optional OpenAI-compatible AI · Robo Tutor**

STUDIGENCE AI is an MCA major-project prototype that combines academic learning, practice, personal learning analytics, career preparation and productivity in one application. This upgraded edition adds a premium charcoal-and-gold visual system, a custom Robo Tutor mascot, a quick-action learning cockpit, and the distinctive **Teach-back Loop**: learners explain a concept in their own words and receive supportive, structured feedback. It contains 15 learning modules plus account/settings.

## The 15 modules

| # | Module | What it does |
|---:|---|---|
| 1 | Dashboard | Personal activity summary, upcoming tasks, quiz trend and next actions |
| 2 | AI Study Tutor + Teach-back Loop | Level-aware lessons, analogies, worked examples, code walkthroughs, and qualitative feedback on a learner's own explanation |
| 3 | PDF Lab | Extracts selectable PDF text, saves documents, generates summaries and practice questions |
| 4 | Exam & Quiz Center | Topic quizzes, scoring, explanations, attempt history and automatic mistake logging |
| 5 | Study Planner | Add tasks, set deadlines, priorities and track completion |
| 6 | Learning DNA | Topic-level performance analysis based on actual quiz attempts |
| 7 | Mistake DNA | Review incorrect answers and recurring weak topics; add topics to revision |
| 8 | Memory & Revision | Persistent spaced-repetition queue with recall-quality feedback |
| 9 | Career Intelligence | Role-specific learning roadmaps and portfolio/interview suggestions |
| 10 | Resume Studio | Save resume sections, preview and export a text resume, request AI feedback |
| 11 | Skill Gap Analyzer | Self-assessed skill levels, target levels, gap chart and improvement plan |
| 12 | YouTube Learning Finder | Builds focused YouTube searches by topic, level, language and content type |
| 13 | Notes & Assignment Studio | Save tagged study notes and generate assignment structures |
| 14 | Focus Room | Record completed focus blocks and track total focus time |
| 15 | Analytics & Reports | Performance and task charts; export activity as JSON |

Settings are provided separately for profile updates and deployment configuration.

## Creative Studio additions

The Creative Studio adds five practical creation workflows:
- Convert multiple JPG/PNG/WEBP/BMP images into a multi-page PDF.
- Generate a topic diagram using AI-generated structured nodes and arrows; download PNG and editable Mermaid source.
- Generate a formatted study PDF from a text prompt.
- Generate a PowerPoint deck from a prompt (4–15 slides).
- Upload a notes image and ask a vision-capable model to explain it simply, shorten it for revision, or do both.

Image-note understanding requires a vision-capable model and an API key. Image-to-PDF works locally without AI. Prompt-based PDF/PPT and AI diagrams require the configured AI API. Generated academic content and diagrams must be checked for correctness.

## What makes this version distinctive

- **Robo Tutor:** friendly mascot and guided tutor experience in the same gold/charcoal palette.
- **Teach-back Loop:** learn a topic, explain it yourself, and receive feedback on correct ideas, gaps, and a follow-up question.
- **Learning cockpit:** quick actions, activity metrics, pending tasks, and quiz trend in one place.
- **15 connected modules:** persistent accounts, study activity, revision queue, notes, and progress records using SQLite.
- **Offline-first core:** accounts, quizzes, planning, notes, revision, and tracking work without an AI key; AI generation uses an optional compatible API.

## Technology stack

- Python 3.10+ (Python 3.11 recommended)
- Streamlit interface
- SQLite persistence
- PBKDF2-HMAC-SHA256 password hashing
- pandas for analysis and reporting
- PyMuPDF for PDF text extraction
- OpenAI Python SDK for optional text and image understanding
- Pillow for image conversion
- ReportLab for PDF generation
- python-pptx for PowerPoint generation
- Matplotlib for downloadable diagrams

## Run on Windows

1. Extract the ZIP and open PowerShell in the `STUDIGENCE_AI` folder.
2. Create a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.

3. Install dependencies and launch:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`) and create an account.

## Optional AI configuration

The application works without an API key; AI-dependent actions then return a guided fallback response. To enable generated explanations, summaries, roadmaps and feedback, copy `.env.example` to `.env` and add a key from your chosen compatible provider:

```dotenv
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

Never commit `.env` or publish API keys. API calls may incur charges. You can alternatively add the same values in Streamlit Community Cloud **App settings → Secrets** using TOML syntax:

```toml
OPENAI_API_KEY = "your_api_key"
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_BASE_URL = "https://api.openai.com/v1"
```

## Push to GitHub

Create an empty GitHub repository, then run these commands from this folder:

```powershell
git init
git add .
git commit -m "Build STUDIGENCE AI 15-module platform"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/STUDIGENCE-AI.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. `.gitignore` excludes virtual environments, local databases, `.env` and Streamlit secrets.

## Deploy on Streamlit Community Cloud

1. Push the project to GitHub.
2. Sign in at https://share.streamlit.io/.
3. Select **Create app**, choose the repository and `main` branch.
4. Set the main file path to `app.py` and Python to 3.11 if the option is available.
5. Add optional AI credentials under **Advanced settings → Secrets**.
6. Deploy and test account creation, login, quiz submission, task saving and note saving.

**Persistence warning:** SQLite is suitable for a local demonstration and a single-instance prototype. Files on Streamlit Community Cloud may not be durable across restarts/redeployments. For a real multi-user deployment, migrate user data to managed PostgreSQL and documents to private object storage. Do not store sensitive student records in a public repository.

## Important implementation boundaries

This is a feature-rich academic prototype, not a production-certified adaptive learning system. Learning DNA uses recorded quiz performance; Skill Gap Analyzer uses self-assessment; neither is a validated psychometric or placement predictor. PDF Lab extracts selectable text and does not include OCR for scanned PDFs. YouTube Finder opens search results rather than verifying or ranking individual videos. Focus Room records a session when the learner marks it complete; it does not run a background timer. AI output can be incorrect and should be checked against course material. Live job scraping, institution integrations, proctored exams, trained ML prediction, and production-grade vector RAG are not claimed as implemented.

## Project structure

```text
STUDIGENCE_AI/
├── app.py
├── src/
│   ├── db.py
│   ├── ai.py
│   ├── advanced.py
│   ├── pages.py
│   ├── content.py
│   └── ui.py
├── tests/
├── data/
├── assets/
├── .streamlit/
├── requirements.txt
└── README.md
```


## Updated visual experience

The current build uses the warm black, amber and gold visual theme, a split sign-in card with the animated graduation mascot, dashboard module tiles, and top-right profile controls. Navigation is on the dashboard; there is no separate sidebar.

For API setup, copy `.env.example` to `.env` and add your own OpenAI API key locally. Never include `.env` in a ZIP, Git repository, screenshots, or messages.
