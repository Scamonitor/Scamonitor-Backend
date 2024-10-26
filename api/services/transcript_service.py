import io
from google.cloud import speech

def transcribe_audio_with_diarization(audio_path):
    client = speech.SpeechClient()

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
