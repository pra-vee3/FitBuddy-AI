# FitBuddy-AI

FitBuddy-AI is an AI-powered fitness planning web application built with FastAPI, SQLite, and Google Gemini.

## Features

- User fitness profile creation
- AI-generated 7-day workout plans
- Nutrition tips
- User feedback-based workout plan updates
- User data storage using SQLite
- Admin page to view all users
- Admin user deletion
- REST API endpoints
- Swagger API documentation
- Demo mode for testing without an API key

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Google Gemini API
- Jinja2
- HTML
- CSS
- Pydantic
- Uvicorn

## Project Structure

```text
FitBuddy-AI/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── ai.py
│   └── routes.py
│
├── templates/
│   ├── admin.html
│   ├── index.html
│   └── workout.html
│
├── static/
│   └── styles.css
│
├── tests/
│   ├── __init__.py
│   └── test_app.py
│
├── docs/
│   └── SETUP.md
│
├── .vscode/
│   └── settings.json
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md