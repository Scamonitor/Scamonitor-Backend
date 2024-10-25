from flask import (
    Blueprint, request, jsonify, g
)
from api.services.db_service import get_db
from api.services.file_service import upload_file, get_unique_filename
from .auth import login_required

bp = Blueprint('news', __name__, url_prefix='/news')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'GET':
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            'SELECT * FROM news_article'
        )
        news = cursor.fetchall()

        return jsonify({"news": news}), 200

    elif request.method == 'POST':
        data = request.form
        author_id = g.user['id']
        title = data.get('title')
        content = data.get('content')
        banner_image = request.files.get('banner_image')
        unique_banner_filename = get_unique_filename(banner_image.filename)

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                'INSERT INTO news_article (author_id, title, content, banner_filename) VALUES (%s, %s, %s, %s)',
                (author_id, title, content, unique_banner_filename)
            )
            db.commit()

            upload_file(banner_image, 'skiliket', unique_banner_filename)
            return jsonify({"message": "News article created."}), 201
        except Exception:
            return jsonify({"error": "An unexpected error occurred."}), 400

