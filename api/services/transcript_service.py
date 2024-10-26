import io
from google.cloud import speech
from flask import current_app

def transcribe_audio_with_diarization(audio_path):
    client = speech.SpeechClient.from_service_account_info({
            "type": "service_account",
            "project_id": "scamonitor",
            "private_key": current_app.config["GCP_PRIVATE_KEY"],
            "client_email": current_app.config["GCP_CLIENT_EMAIL"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    })

    # Load audio file
    with io.open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    # Configure audio and diarization settings
    audio = speech.RecognitionAudio(content=content)
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

    # Printing out the output:
    for word_info in words_info:
        print(f"word: '{word_info.word}', speaker_tag: {word_info.speaker_tag}")
