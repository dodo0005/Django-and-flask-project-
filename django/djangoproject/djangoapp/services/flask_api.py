import os
import requests
from django.conf import settings

BASE_URL = settings.FLASK_API_BASE_URL
API_KEY = os.environ.get("FLASK_API_KEY", "Stories")


def get_headers():
    """Return headers with API key for write operations"""
    return {"X-API-KEY": API_KEY}


# READ OPERATIONS (no API key needed)


def get_published_stories():
    """GET /stories?status=published"""
    response = requests.get(f"{BASE_URL}/stories?status=published")
    response.raise_for_status()
    return response.json()


def get_all_stories():
    """GET /stories"""
    response = requests.get(f"{BASE_URL}/stories")
    response.raise_for_status()
    return response.json()


def get_stories_by_author(author_id):
    """GET /stories?author_id=<id>"""
    response = requests.get(f"{BASE_URL}/stories", params={"author_id": author_id})
    response.raise_for_status()
    return response.json()


def get_story(story_id):
    """GET /stories/<id>"""
    response = requests.get(f"{BASE_URL}/stories/{story_id}")
    response.raise_for_status()
    return response.json()


def get_story_pages(story_id):
    """GET /stories/<id>/pages — all pages with choices"""
    response = requests.get(f"{BASE_URL}/stories/{story_id}/pages")
    response.raise_for_status()
    return response.json()


def get_start_page(story_id):
    """GET /stories/<id>/start"""
    response = requests.get(f"{BASE_URL}/stories/{story_id}/start")
    response.raise_for_status()
    return response.json()


def get_page(page_id):
    """GET /pages/<id>"""
    response = requests.get(f"{BASE_URL}/pages/{page_id}")
    response.raise_for_status()
    return response.json()


# WRITE OPERATIONS (require API key)


def create_story(title, description, status="draft", author_id=None):
    """POST /stories"""
    data = {
        "title": title,
        "description": description,
        "status": status,
        "author_id": author_id,
    }
    response = requests.post(f"{BASE_URL}/stories", json=data, headers=get_headers())
    response.raise_for_status()
    return response.json()


def update_story(
    story_id,
    title=None,
    description=None,
    status=None,
    start_page_id=None,
    requesting_author_id=None,
):
    """PUT /stories/<id>"""
    data = {}
    if title:
        data["title"] = title
    if description:
        data["description"] = description
    if status:
        data["status"] = status
    if start_page_id:
        data["start_page_id"] = start_page_id
    if requesting_author_id is not None:
        data["requesting_author_id"] = requesting_author_id

    response = requests.put(
        f"{BASE_URL}/stories/{story_id}", json=data, headers=get_headers()
    )
    response.raise_for_status()
    return response.json()


def delete_story(story_id, requesting_author_id=None):
    """DELETE /stories/<id>"""
    data = {}
    if requesting_author_id is not None:
        data["requesting_author_id"] = requesting_author_id
    response = requests.delete(
        f"{BASE_URL}/stories/{story_id}", json=data or None, headers=get_headers()
    )
    response.raise_for_status()
    return response.json()


def create_page(
    story_id, text, is_ending=False, ending_label=None, is_start_page=False
):
    """POST /stories/<id>/pages"""
    data = {
        "text": text,
        "is_ending": is_ending,
        "ending_label": ending_label,
        "is_start_page": is_start_page,
    }
    response = requests.post(
        f"{BASE_URL}/stories/{story_id}/pages", json=data, headers=get_headers()
    )
    response.raise_for_status()
    return response.json()


def update_page(page_id, text=None, is_ending=None, ending_label=None):
    """PUT /pages/<id>"""
    data = {}
    if text is not None:
        data["text"] = text
    if is_ending is not None:
        data["is_ending"] = is_ending
    if ending_label is not None:
        data["ending_label"] = ending_label

    response = requests.put(
        f"{BASE_URL}/pages/{page_id}", json=data, headers=get_headers()
    )
    response.raise_for_status()
    return response.json()


def delete_page(page_id):
    """DELETE /pages/<id>"""
    response = requests.delete(f"{BASE_URL}/pages/{page_id}", headers=get_headers())
    response.raise_for_status()
    return response.json()


def create_choice(page_id, text, next_page_id):
    """POST /pages/<id>/choices"""
    data = {
        "text": text,
        "next_page_id": next_page_id,
    }
    response = requests.post(
        f"{BASE_URL}/pages/{page_id}/choices", json=data, headers=get_headers()
    )
    response.raise_for_status()
    return response.json()


def update_choice(page_id, choice_id, text=None, next_page_id=None):
    """PUT /pages/<page_id>/choices/<choice_id>"""
    data = {}
    if text is not None:
        data["text"] = text
    if next_page_id is not None:
        data["next_page_id"] = next_page_id

    response = requests.put(
        f"{BASE_URL}/pages/{page_id}/choices/{choice_id}",
        json=data,
        headers=get_headers(),
    )
    response.raise_for_status()
    return response.json()


def delete_choice(page_id, choice_id):
    """DELETE /pages/<page_id>/choices/<choice_id>"""
    response = requests.delete(
        f"{BASE_URL}/pages/{page_id}/choices/{choice_id}", headers=get_headers()
    )
    response.raise_for_status()
    return response.json()
