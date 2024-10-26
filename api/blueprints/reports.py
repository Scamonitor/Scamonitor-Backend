from flask import (
    Blueprint, request, jsonify, g
)
from api.services.db_service import get_db
from .auth import login_required

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'GET':
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Fetch all reports
        cursor.execute('SELECT * FROM reports')
        reports = cursor.fetchall()

        return jsonify({"reports": reports}), 200

    elif request.method == 'POST':
        # Get form data
        data = request.form
        type = data.get('type')
        verdict = data.get('verdict')
        recommendations = data.get('recommendations')
        link = data.get('link')

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            # Insert the new report into the database
            cursor.execute(
                'INSERT INTO reports (type, verdict, recommendations, link) VALUES (%s, %s, %s, %s)',
                (type, verdict, recommendations, link)
            )
            db.commit()
            
            return jsonify({"message": "Report created."}), 201
        except Exception as e:
            print(e)  # For debugging purposes
            return jsonify({"error": "An unexpected error occurred."}), 400
