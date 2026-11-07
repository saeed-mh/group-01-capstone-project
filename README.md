# AI-Powered Waste Sorting & Recycling Assistant

Capstone Project

A web app that classifies waste from a photo or text with OpenAI and shows the correct bin according to each city's recycling rules.

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

1. Clone the assignment branch and open the project folder:
   ```bash
   git clone -b HomeworkAssignment3 https://github.com/saeed-mh/group-01-capstone-project.git
   cd group-01-capstone-project
   ```
2. Create a virtual environment and install the requirements:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS / Linux
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your OpenAI API key.
4. Start the app:
   ```bash
   python run.py
   ```
5. Open http://127.0.0.1:5000

The SQLite database (`data/app.db`) is created automatically on the first start, and the recycling rules are loaded from `data/rules.csv`.

## Pages

| Page | URL | Subsystem |
|---|---|---|
| Home | `/` | – |
| Classification History | `/classify` | 1 – Waste Classification |
| Bins Guide | `/bins` | 2 – Recycling Rules |
| Statistics Dashboard | `/dashboard` | 3 – Statistics Dashboard |

## Presentation Video

[Watch the team presentation](https://drive.google.com/file/d/1TDqwSLDj1nkhMvnjP7Jd2sDgwDl8A7ZK/view?usp=sharing)
