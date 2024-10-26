from flask import (
    Blueprint, request, jsonify, g
)
from api.services.db_service import get_db
from api.services.transcript_service import transcribe_audio_with_diarization
from api.services.email_service import send_email
from api.services.file_service import get_unique_filename, upload_file, generate_presigned_url
from .auth import login_required
from openai import OpenAI
from flask import current_app, g


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
        data = request.form
        type = data.get('type')

        if type == "AUDIO":
            try: 
                audio_file = request.files['audio_file']
                asset_filename = get_unique_filename(audio_file.filename)

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
                upload_file(audio_content, 'scamonitor-bucket', asset_filename)
                asset_url = generate_presigned_url('scamonitor-bucket', asset_filename)
                send_email(g.user["name"], asset_url, g.user['contact_email'])
            except Exception as e:
                print(e)
                return jsonify({"error": "Error sending email to contact."}), 500

            try: 
                vote_result = []
                for i in range(9):
                    chat_completion = client.chat.completions.create(
                        model="tgi",
                        messages=[
                            {
                                "role": "user",
                                "content": "You are an assistant specialized in detecting potential scams targeting older adults through phone calls. Given a transcript formatted as 'Person A: [text]' and 'Person B: [text]', your task is to determine whether the call is likely a scam or not. Please respond with a single word: 'scam' if it is a scam, or 'no scam' if it is not. TRANSCRIPT: " + transcript
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
                    vote_result.append(chat_completion.choices[0].message.content == "no scam")
                veredict = "no scam" if vote_result.count(True) > 3 else "scam"
                print("TRANSCRIPT: ", transcript)

            except Exception as e:
                print(e)
                return jsonify({"error": "Error with detection model"}), 500
            
            # Generate suggestions
            client_gpt = OpenAI(api_key=current_app.config["GPT_API_KEY"])
            recommendations_request = client_gpt.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You will receive the transcription of a phone call, along with a flag indicating whether it is a scam or not. If it is a scam, give clues on why it might be a scam. If it is not, then give clues of the transcript that suggest the legitimacy. Give your response in the format of four recommendations tailored to older audiences, contained in a JSON array, separated by commas with no special characters. Just return the JSON array, no more context needed"},
                    {"role": "user", "content": "Transcript: " + transcript + " Veredict: " + veredict},
                ]
            )
            recommendations = recommendations_request.choices[0].message.content
    
        elif type == "IMAGE":
            image_file = request.files['image_file']
            asset_filename = get_unique_filename(image_file.filename)

            try:
                upload_file(image_file, 'scamonitor-bucket', asset_filename)
                asset_url = generate_presigned_url('scamonitor-bucket', asset_filename)
                send_email(g.user["name"], asset_url, g.user['contact_email'])
            except Exception as e:
                print(e)
                return jsonify({"error": "Error sending email to contact."}), 500

            client_gpt = OpenAI(api_key=current_app.config["GPT_API_KEY"])
            response = client_gpt.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": "You will be given an image of an email or a text sms. Please write down the sender, and the message content."},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": asset_url 
                    },
                    },
                ],
                }
            ],
            max_tokens=300,
            )

            message_content = response.choices[0].message.content
            try: 
                client = OpenAI(
                    base_url=current_app.config["IMAGE_MODEL_URL"],
                    api_key="hf_XXXXX"
                )
                vote_result = []
                for i in range(9):
                    chat_completion = client.chat.completions.create(
                        model="tgi",
                        messages=[
                            {
                                "role": "user",
                                "content": "You are given the content of an email or sms message. Please determine if it is likely a scam or not. CONTENT: " + message_content
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
                    vote_result.append(chat_completion.choices[0].message.content == "no scam")
                veredict = "no scam" if vote_result.count(True) > 3 else "scam"

            except Exception as e:
                print(e)
                return jsonify({"error": "Error with detection model"}), 500
            
            # Generate suggestions
            client_gpt = OpenAI(api_key=current_app.config["GPT_API_KEY"])
            recommendations_request = client_gpt.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You will receive the content of an email or message, along with a flag indicating whether it is a scam or not. If it is a scam, give clues on why it might be a scam. If it is not, then give clues of the transcript that suggest the legitimacy. Give four recommendations tailored to older audiences, in the format of a JSON array, separated by commas with no special characters. Just return the array, no more context needed"},
                    {"role": "user", "content": "Content: " + message_content + " Veredict: " + veredict},
                ]
            )
            recommendations = recommendations_request.choices[0].message.content

        # Upload new report to db
        db = get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                'INSERT INTO reports (type, verdict, recommendations, asset_name) VALUES (%s, %s, %s, %s)',
                (type, veredict, recommendations, asset_filename)
            )
            db.commit()

            report_id = cursor.lastrowid

            cursor.execute('SELECT * FROM reports WHERE id = %s', (report_id,))
            new_report = cursor.fetchone()

            return jsonify(new_report), 201
        except Exception as e:
            print(e)  # For debugging purposes
            return jsonify({"error": "An unexpected error occurred."}), 500
