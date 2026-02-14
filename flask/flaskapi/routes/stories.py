from flask import Blueprint, request, jsonify
from models import Story
from extensions import db

stories_bp = Blueprint("stories", __name__, url_prefix="/stories")

import os

API_KEY = os.environ.get("FLASK_API_KEY", "Stories")


def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-KEY")
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def story_to_dict(story):
    return {
        "id": story.id,
        "title": story.title,
        "description": story.description,
        "status": story.status,
        "start_page_id": story.start_page_id,
        "author_id": story.author_id,
    }


# ── READ ENDPOINTS (public) ─────────────────────────────────────────────────


@stories_bp.route("", methods=["GET"])
def list_stories():
    """GET /stories?status=published&author_id=<id>"""
    status = request.args.get("status")
    author_id = request.args.get("author_id", type=int)

    query = Story.query
    if status:
        query = query.filter_by(status=status)
    if author_id is not None:
        query = query.filter_by(author_id=author_id)

    return jsonify([story_to_dict(s) for s in query.all()])


@stories_bp.route("/<int:id>", methods=["GET"])
def get_story(id):
    """GET /stories/<id>"""
    story = Story.query.get_or_404(id)
    return jsonify(story_to_dict(story))


@stories_bp.route("/<int:id>/start", methods=["GET"])
def start_story(id):
    """GET /stories/<id>/start"""
    story = Story.query.get_or_404(id)
    return jsonify({"start_page_id": story.start_page_id})


@stories_bp.route("/<int:id>/pages", methods=["GET", "POST"])
def story_pages(id):
    from models import Page, Choice

    story = Story.query.get_or_404(id)

    if request.method == "GET":
        """GET /stories/<id>/pages — returns all pages with their choices"""
        pages = Page.query.filter_by(story_id=story.id).all()
        result = []
        for page in pages:
            choices = Choice.query.filter_by(page_id=page.id).all()
            result.append(
                {
                    "id": page.id,
                    "text": page.text,
                    "is_ending": page.is_ending,
                    "ending_label": page.ending_label,
                    "is_start": page.id == story.start_page_id,
                    "choices": [
                        {"id": c.id, "text": c.text, "next_page_id": c.next_page_id}
                        for c in choices
                    ],
                }
            )
        return jsonify(result)

    else:  # POST
        """POST /stories/<id>/pages"""
        key = request.headers.get("X-API-KEY")
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        page = Page(
            story_id=story.id,
            text=data.get("text", ""),
            is_ending=data.get("is_ending", False),
            ending_label=data.get("ending_label"),
        )
        db.session.add(page)
        db.session.commit()

        if data.get("is_start_page"):
            story.start_page_id = page.id
            db.session.commit()

        return jsonify({"message": "Page created successfully", "id": page.id}), 201


# ── WRITE ENDPOINTS (require API key) ───────────────────────────────────────


@stories_bp.route("", methods=["POST"])
@require_api_key
def create_story():
    """POST /stories  — expects author_id in payload"""
    data = request.get_json()

    story = Story(
        title=data.get("title"),
        description=data.get("description"),
        status=data.get("status", "draft"),
        start_page_id=data.get("start_page_id"),
        author_id=data.get("author_id"),  # set by Django on creation
    )

    db.session.add(story)
    db.session.commit()

    return jsonify({"message": "Story created successfully", "id": story.id}), 201


@stories_bp.route("/<int:id>", methods=["PUT"])
@require_api_key
def update_story(id):
    """PUT /stories/<id>"""
    story = Story.query.get_or_404(id)
    data = request.get_json()

    # Ownership check: only enforce if both sides are set
    # (stories created before author_id was added will have author_id=None — allow edit)
    requesting_author = data.get("requesting_author_id")
    if requesting_author is not None and story.author_id is not None:
        if int(requesting_author) != int(story.author_id):
            return jsonify({"error": "Forbidden: you do not own this story"}), 403

    story.title = data.get("title", story.title)
    story.description = data.get("description", story.description)
    story.status = data.get("status", story.status)
    story.start_page_id = data.get("start_page_id", story.start_page_id)

    db.session.commit()
    return jsonify({"message": "Story updated successfully"})


@stories_bp.route("/<int:id>", methods=["DELETE"])
@require_api_key
def delete_story(id):
    """DELETE /stories/<id>"""
    story = Story.query.get_or_404(id)
    data = request.get_json(silent=True) or {}

    # Ownership check
    requesting_author = data.get("requesting_author_id")
    if requesting_author is not None and story.author_id is not None:
        if int(requesting_author) != story.author_id:
            return jsonify({"error": "Forbidden: you do not own this story"}), 403

    db.session.delete(story)
    db.session.commit()
    return jsonify({"message": "Story deleted successfully"})
