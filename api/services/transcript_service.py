import io
from google.cloud import speech
from flask import current_app

def transcribe_audio_with_diarization(audio_content):
    client = speech.SpeechClient.from_service_account_info({
            "type": "service_account",
            "project_id": "scamonitor",
            "private_key": current_app.config["GCP_PRIVATE_KEY"],
            "client_email": current_app.config["GCP_CLIENT_EMAIL"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    })

    # Configure audio and diarization settings
    audio = speech.RecognitionAudio(content=audio_content)
    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=10,
    )
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="en-US",
        diarization_config=diarization_config,
    )

    # Perform speech-to-text request
    response = client.recognize(config=config, audio=audio)
    # Process and print the results

    result = response.results[-1]

    words_info = result.alternatives[0].words

    # Building the dialog format
    speaker_dialog = {}
    current_speaker = None
    for word_info in words_info:
        speaker_tag = word_info.speaker_tag
        word = word_info.word

        # Initialize speaker dialog if not already
        if speaker_tag != current_speaker:
            current_speaker = speaker_tag
            speaker_name = "Person A" if speaker_tag == 1 else "Person B"
            if speaker_name not in speaker_dialog:
                speaker_dialog[speaker_name] = ""
            speaker_dialog[speaker_name] += f"{speaker_name}: {word}"
        else:
            speaker_dialog[speaker_name] += f" {word}"

    # Join all parts for the final output
    final_output = " ".join(speaker_dialog.values())

    return final_output