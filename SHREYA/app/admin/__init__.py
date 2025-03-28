from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

# Don't import routes here to avoid circular imports 