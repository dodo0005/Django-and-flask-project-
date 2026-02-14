from flask import Blueprint, jsonify, request
from models import Page, Choice
from extensions import db

pages_bp = Blueprint("pages", __name__, url_prefix="/pages")

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


@pages_bp.route("/<int:id>", methods=["GET"])
def get_page(id):
    """GET /pages/<id> - Returns page text + choices"""
    page = Page.query.get_or_404(id)

    choices = Choice.query.filter_by(page_id=page.id).all()

    return jsonify(
        {
            "id": page.id,
            "story_id": page.story_id,
            "text": page.text,
            "is_ending": page.is_ending,
            "ending_label": page.ending_label,
            "choices": [
                {
                    "id": choice.id,
                    "text": choice.text,
                    "next_page_id": choice.next_page_id,
                }
                for choice in choices
            ],
        }
    )


@pages_bp.route("/<int:id>", methods=["PUT"])
@require_api_key
def update_page(id):
    """PUT /pages/<id> - Update page text/ending status"""
    page = Page.query.get_or_404(id)
    data = request.get_json()

    page.text = data.get("text", page.text)
    page.is_ending = data.get("is_ending", page.is_ending)
    page.ending_label = data.get("ending_label", page.ending_label)

    db.session.commit()

    return jsonify({"message": "Page updated successfully"})


@pages_bp.route("/<int:id>", methods=["DELETE"])
@require_api_key
def delete_page(id):
    """DELETE /pages/<id>"""
    page = Page.query.get_or_404(id)

    db.session.delete(page)
    db.session.commit()

    return jsonify({"message": "Page deleted successfully"})


# NEW: Create choices for a page
@pages_bp.route("/<int:id>/choices", methods=["POST"])
@require_api_key
def create_choice_for_page(id):
    """POST /pages/<id>/choices"""
    page = Page.query.get_or_404(id)
    data = request.get_json()

    choice = Choice(
        page_id=page.id,
        text=data.get("text", ""),
        next_page_id=data.get("next_page_id"),
    )

    db.session.add(choice)
    db.session.commit()

    return jsonify({"message": "Choice created successfully", "id": choice.id}), 201


@pages_bp.route("/<int:page_id>/choices/<int:choice_id>", methods=["PUT"])
@require_api_key
def update_choice(page_id, choice_id):
    """PUT /pages/<page_id>/choices/<choice_id>"""
    choice = Choice.query.filter_by(id=choice_id, page_id=page_id).first_or_404()
    data = request.get_json()

    choice.text = data.get("text", choice.text)
    choice.next_page_id = data.get("next_page_id", choice.next_page_id)

    db.session.commit()

    return jsonify({"message": "Choice updated successfully"})


@pages_bp.route("/<int:page_id>/choices/<int:choice_id>", methods=["DELETE"])
@require_api_key
def delete_choice(page_id, choice_id):
    """DELETE /pages/<page_id>/choices/<choice_id>"""
    choice = Choice.query.filter_by(id=choice_id, page_id=page_id).first_or_404()

    db.session.delete(choice)
    db.session.commit()

    return jsonify({"message": "Choice deleted successfully"})
