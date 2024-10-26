from flask import (
    Blueprint, request, jsonify, g
)
from api.services.db_service import get_db
from api.services.transcript_service import transcribe_audio_with_diarization
from api.services.email_service import send_email
from api.services.file_service import get_unique_filename, upload_file, generate_presigned_url
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
        data = request.form
        type = data.get('type')

        if type == "AUDIO":
            try: 
                audio_file = request.files['audio_file']
                unique_audio_filename = get_unique_filename(audio_file.filename)

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
                upload_file(audio_content, 'scamonitor-bucket', unique_audio_filename)
                asset_url = generate_presigned_url('scamonitor-bucket', unique_audio_filename)
                send_email(asset_url)
            except Exception as e:
                print(e)
                return jsonify({"error": "Error sending email to contact."}), 500

            try: 
                print("TRANSCRIPT", transcript)
                chat_completion_1 = client.chat.completions.create(
                    model="tgi",
                    messages=[
                        {
                            "role": "user",
                            "content": "You are an assistant that helps in scam detection of phone call transcripts. You will be given a transcript in the format Person A and Person B. I need you to identify if the transcript likely corresponds to a scam or not. ONLY ANSWER BINARY, 'scam' or 'no scam'. TRANSCRIPT: " + transcript
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
                chat_completion_2 = client.chat.completions.create(
                    model="tgi",
                    messages=[
                        {
                            "role": "user",
                            "content": "You are an assistant that helps in scam detection of phone call transcripts. You will be given a transcript in the format Person A and Person B. I need you to identify if the transcript likely corresponds to a scam or not. ONLY ANSWER BINARY, 'scam' or 'no scam'. TRANSCRIPT: " + transcript
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
                chat_completion_3 = client.chat.completions.create(
                    model="tgi",
                    messages=[
                        {
                            "role": "user",
                            "content": "You are an assistant that helps in scam detection of phone call transcripts. You will be given a transcript in the format Person A and Person B. I need you to identify if the transcript likely corresponds to a scam or not. ONLY ANSWER BINARY, 'scam' or 'no scam'. TRANSCRIPT: " + transcript
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

                print("A", chat_completion_1.choices[0].message.content)
                print("B", chat_completion_2.choices[0].message.content)
                print("C", chat_completion_3.choices[0].message.content)

                vote_1 = chat_completion_1.choices[0].message.content.lower() == "no scam"
                vote_2 = chat_completion_2.choices[0].message.content.lower() == "no scam"
                vote_3 = chat_completion_3.choices[0].message.content.lower() == "no scam"

                vote_result = [vote_1, vote_2, vote_3]
                veredict = "no scam" if vote_result.count(True) > 1 else "scam"

            except Exception as e:
                print(e)
                return jsonify({"error": "Error with detection model"}), 500
            
            # Generate suggestions
            client_gpt = OpenAI(api_key="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")
            recommendations_request = client_gpt.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "you will receive a transcription of a phone call, and you will also get true if it is a scam, or false otherwise. If it is a scam, give clues on why it might be a scam. If it is not, then give clues of the transcript that suggest the legitimacy. Give four recommendations, in the format of a JSON array, separated by commas with no special characters. Just return the array, no more context needed"},
                    {"role": "user", "content": "Transcript: " + transcript + " Veredict: " + veredict},
                ]
            )
            recommendations = recommendations_request.choices[0].message.content
    
        # Upload new report to db
        db = get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                'INSERT INTO reports (type, verdict, recommendations, asset_name) VALUES (%s, %s, %s, %s)',
                (type, veredict, recommendations, unique_audio_filename)
            )
            db.commit()

            report_id = cursor.lastrowid

            cursor.execute('SELECT * FROM reports WHERE id = %s', (report_id,))
            new_report = cursor.fetchone()

            return jsonify(new_report), 201
        except Exception as e:
            print(e)  # For debugging purposes
            return jsonify({"error": "An unexpected error occurred."}), 500
