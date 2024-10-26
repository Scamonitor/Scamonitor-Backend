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
        max_speaker_count=2,
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
    current_speaker = 1
    speaker_map = {1: "Person A", 2: "Person B"}

    conversation = []
    current_sentence = []
    for word_info in words_info:
        speaker_tag = word_info.speaker_tag
        word = word_info.word
        speaker_tag = min(speaker_tag, 2)

        # Initialize speaker dialog if not already
        if speaker_tag != current_speaker:
            conversation.append(f"{speaker_map[current_speaker]}: " + " ".join(current_sentence))
            # Reset for the new speaker
            current_sentence = [word]
            current_speaker = speaker_tag
        else:
            # Continue building the sentence for the current speaker
            current_sentence.append(word)

    if current_sentence:
        conversation.append(f"{speaker_map[current_speaker]}: " + " ".join(current_sentence))

    # Join all parts for the final output
    final_output = " ".join(conversation)

    return final_output