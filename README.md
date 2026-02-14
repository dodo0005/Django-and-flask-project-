# NAHB – Not Another Hero's Book

**NAHB** is a “Choose Your Own Adventure” web application split across **Django** and **Flask**.  
The Flask API manages story content, while the Django web app handles gameplay, user accounts, and front-end rendering.

---

## Architecture

The application consists of two separate servers:

- **Flask REST API (port 5000)**  
  Stores and serves all story content: stories, pages, choices.  
  Exposes a JSON API with **no HTML**.

- **Django Web App (port 8000)**  
  Game engine, HTML templates, user authentication, and gameplay tracking.  
  Calls the Flask API to display stories.

**Key Rule:**  
- Story content (`Story`, `Page`, `Choice`) lives only in **Flask**.  
- Gameplay data (`Play`, `Rating`, `Report`) and users live only in **Django**.

---

## Setup & Run

### Prerequisites
- Python 3.10+
- pip or pipenv

### 1. Start the Flask API
```bash
cd flask/flaskapi
pip install -r requirements.txt
flask db upgrade
python app.py   # → http://127.0.0.1:5000

### 2. Start the Django App
cd django/djangoproject
pip install django requests
python manage.py migrate
python manage.py runserver   # → http://127.0.0.1:8000

Test Accounts

Superuser: username: user | password: user

You can also create accounts via /register/ or Django admin panel:

python manage.py createsuperuser
Role	How to set
Reader	Default on registration
Admin/Staff	Set is_staff = True in admin panel


Flask API Endpoints

Base URL: http://127.0.0.1:5000
Authentication: Write endpoints require HTTP header X-API-KEY: Stories

Stories
Method	Endpoint	Auth	Description
GET	/stories	—	List all stories (filter: ?status=published)
GET	/stories/<id>	—	Get a single story
GET	/stories/<id>/start	—	Get the start page ID
POST	/stories	✅	Create a story
PUT	/stories/<id>	✅	Update a story
DELETE	/stories/<id>	✅	Delete a story
POST	/stories/<id>/pages	✅	Add a page to a story
Pages
Method	Endpoint	Auth	Description
GET	/pages/<id>	—	Get page text + all choices
PUT	/pages/<id>	✅	Update a page
DELETE	/pages/<id>	✅	Delete a page
POST	/pages/<id>/choices	✅	Add a choice to a page
PUT	/pages/<pid>/choices/<cid>	✅	Update a choice
DELETE	/pages/<pid>/choices/<cid>	✅	Delete a choice


Data Models
Flask — Story Content

Story: id, title, description, status (draft/published/suspended), start_page_id

Page: id, story_id, text, is_ending (bool), ending_label

Choice: id, page_id, text, next_page_id

Django — Gameplay & Users

Play: user (nullable), story_id, ending_page_id, created_at

Rating: user, story_id, rating (1–5), comment, created_at

Unique: (user, story_id)

Report: user, story_id, reason, description, created_at, resolved


Test Accounts

Superuser: username: user | password: user

You can also create accounts via /register/ or Django admin panel:

python manage.py createsuperuser
Role	How to set
Reader	Default on registration
Admin/Staff	Set is_staff = True in admin panel
Flask API Endpoints

Base URL: http://127.0.0.1:5000
Authentication: Write endpoints require HTTP header X-API-KEY: Stories

Stories
Method	Endpoint	Auth	Description
GET	/stories	—	List all stories (filter: ?status=published)
GET	/stories/<id>	—	Get a single story
GET	/stories/<id>/start	—	Get the start page ID
POST	/stories	✅	Create a story
PUT	/stories/<id>	✅	Update a story
DELETE	/stories/<id>	✅	Delete a story
POST	/stories/<id>/pages	✅	Add a page to a story
Pages
Method	Endpoint	Auth	Description
GET	/pages/<id>	—	Get page text + all choices
PUT	/pages/<id>	✅	Update a page
DELETE	/pages/<id>	✅	Delete a page
POST	/pages/<id>/choices	✅	Add a choice to a page
PUT	/pages/<pid>/choices/<cid>	✅	Update a choice
DELETE	/pages/<pid>/choices/<cid>	✅	Delete a choice
Data Models
Flask — Story Content

Story: id, title, description, status (draft/published/suspended), start_page_id

Page: id, story_id, text, is_ending (bool), ending_label

Choice: id, page_id, text, next_page_id

Django — Gameplay & Users

Play: user (nullable), story_id, ending_page_id, created_at

Rating: user, story_id, rating (1–5), comment, created_at

Unique: (user, story_id)

Report: user, story_id, reason, description, created_at, resolved



django project/
├── flask/
│   └── flaskapi/
│       ├── app.py           # Flask application factory
│       ├── models.py        # Story, Page, Choice
│       ├── routes/
│       │   ├── stories.py   # Story endpoints + page creation
│       │   ├── pages.py     # Page + choice CRUD
│       │   └── choices.py   # (empty blueprint placeholder)
│       └── migrations/
│
└── django/
    └── djangoproject/
        ├── manage.py
        └── djangoapp/
            ├── models.py        # Play, Rating, Report
            ├── views.py         # All Django views
            ├── urls.py          # URL routing
            ├── forms.py         # StoryForm, RatingForm, etc.
            ├── services/
            │   └── flask_api.py # HTTP client for Flask API
            └── templates/djangoapp/