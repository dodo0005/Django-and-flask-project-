from flask import Blueprint

stories_bp = Blueprint('stories', __name__, url_prefix='/stories')

@stories_bp.route('', methods=['GET'])
def list_stories():
    return {"message": "List stories endpoint"}
