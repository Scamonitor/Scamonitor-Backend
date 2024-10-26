from flask import (
    Blueprint, request, jsonify, g
)
from api.services.db_service import get_db
from api.services.transcript_service import transcribe_audio_with_diarization
from api.services.email_service import send_email
from .auth import login_required
from openai import OpenAI
from flask import current_app


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
        data = request.form
        type = data.get('type')

        send_email()
        
        if type == "AUDIO":
            try: 
                audio_file = request.files['audio_file']
                audio_content = audio_file.read()
                transcript = transcribe_audio_with_diarization(audio_content)
                client = OpenAI(
                    base_url=current_app.config["AUDIO_MODEL_URL"],
                    api_key="hf_XXXXX"
                )
            except Exception as e:
                print(e)
                return jsonify({"error": "Error transcribing audio."}), 500

            try: 
                chat_completion = client.chat.completions.create(
                    model="tgi",
                    messages=[
                        {
                            "role": "assistant",
                            "content": "You are an assistant that aids in scam detection in phone call transcripts. You will only answer binary: 'scam' if it is likely a scam, or 'no scam' otherwise",
                        },
                        {
                            "role": "user",
                            "content": "Identify if this is a scam conversation: " + transcript
                        }
                    ],
                    top_p=None,
                    temperature=None,
                    max_tokens=150,
                    stream=False,
                    seed=None,
                    frequency_penalty=None,
                    presence_penalty=None
                )   

                print("TRANSCRIPTION", transcript)
                print("RESULT", chat_completion.choices[0].message.content)
            except Exception as e:
                print(e)
                return jsonify({"error": "Error with predictive model"}), 500

        db = get_db()
        cursor = db.cursor(dictionary=True)

        veredict="SPAM"
        recommendations="Block the number"
        link="https://www.google.com"
        try:
            # Insert the new report into the database
            cursor.execute(
                'INSERT INTO reports (type, verdict, recommendations, link) VALUES (%s, %s, %s, %s)',
                (type, veredict, recommendations, link)
            )
            db.commit()
            
            return jsonify({"message": "Report created."}), 201
        except Exception as e:
            print(e)  # For debugging purposes
            return jsonify({"error": "An unexpected error occurred."}), 500
