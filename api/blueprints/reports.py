from flask import (
    Blueprint, request, jsonify, g
)
from api.services.db_service import get_db
from api.services.transcript_service import transcribe_audio_with_diarization
from .auth import login_required

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/', methods=('GET', 'POST'))
# @login_required
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
        data = request.get_json()
        type = data.get('type')
        verdict = data.get('verdict')
        recommendations = data.get('recommendations')
        link = data.get('link')
        print(type)

        if type == "AUDIO":
            audio_path = "api/services/test_audio.wav"  # Change this to the path of the uploaded audio file
            transcribe_audio_with_diarization(audio_path)

        return jsonify({"message": "Report created."}), 201
        # db = get_db()
        # cursor = db.cursor(dictionary=True)

        # try:
        #     # Insert the new report into the database
        #     cursor.execute(
        #         'INSERT INTO reports (type, verdict, recommendations, link) VALUES (%s, %s, %s, %s)',
        #         (type, verdict, recommendations, link)
        #     )
        #     db.commit()
            
        #     return jsonify({"message": "Report created."}), 201
        # except Exception as e:
        #     print(e)  # For debugging purposes
        #     return jsonify({"error": "An unexpected error occurred."}), 400
