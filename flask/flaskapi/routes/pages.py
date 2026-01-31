from flask import Blueprint

pages_bp = Blueprint('pages', __name__, url_prefix='/pages')

@pages_bp.route('/<int:id>', methods=['GET'])
def get_page(id):
    return {"message": f"Get page {id}"}
