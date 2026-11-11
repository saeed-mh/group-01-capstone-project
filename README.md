# AI-Powered Waste Sorting & Recycling Assistant

Capstone Project

A web app that classifies waste from a photo or text with AI (Google Gemini) and shows the correct bin according to each city's recycling rules. A sustainability coach answers recycling questions using only the rules of the selected city.

## Team

| Member | Matr. No. | Subsystem | Pages |
|---|---|---|---|
| Md Sad Abdullah Sami | 7225989 | Waste Classification | `classify.html` |
| Saeed Mohammadi Gahrooei | 7224510 | Recycling Rules & Sustainability Coach | `bins.html`, `coach.html`, `admin.html` |
| Amin Elkasaby | 7224933 | Statistics Dashboard | `dashboard.html` |

## Homework Assignment 2: Stream Processing Framework
<img alt="stream_framework_uml" src="docs/stream_framework_uml.png" />

## System Design

### Subsystem 1: Waste Classification
<img width="2518" height="1454" alt="subsystem1_classification" src="docs/classification_uml.png" />

### Subsystem 2: Recycling Rules & Sustainability Coach
<img width="2610" height="1190" alt="subsystem2_rules_coach" src="https://github.com/user-attachments/assets/0df89cd5-967f-4927-ad37-d50e89047f5b" />

### Subsystem 3: Statistics Dashboard
<img width="2160" height="930" alt="subsystem3_statistics" src="docs/statistics_uml.png" />

## How to run

1. Clone the project and open the folder:
   ```bash
   git clone -b final-capstone-project https://github.com/saeed-mh/group-01-capstone-project.git
   cd group-01-capstone-project
   ```
2. Create a virtual environment and install the requirements:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS / Linux
   python -m pip install -r requirements.txt
   ```
3. Create your `.env` file from the example (see [Configuration](#configuration)):
   ```bash
   copy .env.example .env       # Windows
   cp .env.example .env         # macOS / Linux
   ```
4. Start the app:
   ```bash
   python run.py
   ```
5. Open http://127.0.0.1:5000

The SQLite database (`data/app.db`) is created automatically on the first start, and the recycling rules are loaded from `data/rules.csv`.

## Configuration

All settings are in the `.env` file. It is ignored by Git, so your API key and password are never uploaded.

| Setting | Meaning |
|---|---|
| `OPENAI_API_KEY` | Your Google Gemini API key (free at https://aistudio.google.com → "Get API key") |
| `OPENAI_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai/` (Gemini's OpenAI-compatible endpoint) |
| `OPENAI_MODEL` | `gemini-3.5-flash-lite` |
| `ADMIN_PASSWORD` | Password for the Admin page. Change `change-me` to your own password. |
| `DATABASE_PATH` | Where the SQLite database is stored (default `data/app.db`) |

Without an API key, the app still runs in **demo mode**: the coach and the classification return fixed demo answers.

## Tests

```bash
python -m pytest
```

The tests use a temporary database and fake AI clients, so they never call the real AI and do not need an API key. To run only one subsystem's tests:

```bash
python -m pytest tests/test_rules_coach.py -v
```

## Pages

| Page | URL | Subsystem |
|---|---|---|
| Home | `/` | – |
| Waste Classification | `/classify` | 1 – Waste Classification |
| Bins Guide (with item search) | `/bins` | 2 – Recycling Rules |
| Sustainability Coach (with tip of the day) | `/coach` | 2 – Sustainability Coach |
| Admin (add, edit and delete rules, password-protected) | `/admin` | 2 – Recycling Rules |
| Statistics Dashboard | `/dashboard` | 3 – Statistics Dashboard |

## Presentation Video

[Watch the team presentation](https://drive.google.com/file/d/1dMtmLWlaKOn-08XC9T-9Ur56MzPHkIFH/view?usp=sharing)
