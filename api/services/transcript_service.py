import io
from google.cloud import speech

def transcribe_audio_with_diarization(audio_path):
    client = speech.SpeechClient.from_service_account_info({
            "type": "service_account",
            "project_id": "scamonitor",
            "private_key_id": "e278120a1f1370a2be2154dca2e7241efe137855",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCf6f9DyuqKKdvW\n5AvaCC7nDNkMVxD3zxgHfyPizJ1L2U2v1/wWNdGoJnMJDzWyUx5EyXNnWrX+6olP\nlLRMcvbX5sQ9LrDOLc//zG2dEsfAQ77sdzY4NKFmVs/ZG3cvw4MF5UkqwfEqnRvT\nk7a6I5nCNWU/xCGRN6vwr8ApeQJJKqycFxX4xwpfJPmxk/pqpzyr7otECoksxGL8\n8azeMUUnehBLwKzLp8Uwg7zhygwsKuE+Pz4iGgOOSxqGcypGFHwtQRgWGoNat7sZ\nUczMAh4cLGkC+kNj6ueEfpe95wgF/lRhr2qkPvKVSsOSYTQaLAJNnIP9yYXJ/UCu\nLm2tcoVLAgMBAAECggEAMNmWdOsjwpkO4xI+3JfrXAF8vFxMfqbwvDmGiN3gny7+\noFzmURKXvTohof7XdGYXtQOlEUmQlxKmZ30RptjntwRzpg0BTbqI86dLRNRb2MvZ\nIvs3wOuy8kRKshPF0P10pPRp6XndZhsgSP2ysCH38m/FQjlz15yeFaRam1Cv9hFr\ni2WK0s+cdM63TxLUsTm1PzbIPfepk9O0IzQeKU9xJRelRu2LhUeC8212bcZX9/Ns\nuzZQnEpXor1Xvafkb/qHSuNouKNmFtlZZJWN7rVzvO2wkfs1FcXShJZKjt2vDsxq\njxy/pIAS40LVpDBbrDmRDYWc40fMfnsP/3wX/U/L4QKBgQDO57/XbgBc/a3mtuJI\nCa26+6+vjCUdRwPFEpqZxt97XY9nhbPZb8sv+X5NapuoRjU9YL8f/RLJJpt1LSt6\nmisqtfg3omjDY5osQoDYFJLM8d1MhhYqoPA+GaRnAiGDqKWr+EUMIdk0Aq+gb0gM\n9VfgY2Itmi2RYOg7BRl5zZeP1QKBgQDF29BWHgCjZr55+F11JyVPPnBgl+3rAkbv\nJ1uBz2I6DbrbH1HlewYPx/jHJPmiKxHDY+6M5lVIQKWj4NREhC6VRW5ftazA6IuT\neA0GDXmeKj1X7VGrZJKE3cX/XCvXX4BU/njcN58XEZYqDf/WA6sYQmzxqmPzGkR0\n4Gx5nFdwnwKBgQDFkd5KZCvMoCASksf4aeWPCw5z3qsCDfG3mVAvTwvPzUNGYxGd\nq3amVOMaIZaJVKE5/swCS7JIiakgdwVxiQ13N1PSLC9FhDKP2OEXdG3JbZsXm2JH\nSm6dnfaytgIyqjOoxuWH9Dpnw7jYxepTFWPYTI5PZU3l6FdZJEFzYbI8EQKBgQCm\nbjM97TjOOgOpJ2C9xfLdSIFQzxujHiQ60RlpBN/0Q05VOXAzHxvHNIewRArz/VSQ\nzcOAo9NC1pY+VkVXaPSiPWgNfA1Xq4SUxFv4JmeRwqgdCRQ0noGc38vH9GkwXjXd\nyLwzSVo6FmIA+AumoylNW7q2QYSXnhXNVmYImZj3swKBgQDMBtRwzyShJCO3gYip\n9QB0RyOfyh1afoD2zVYp0FsabpzXi0go3y09U40J6OZDu0CdPUadJWIofNE69NUv\naCj8T7Wul9t2hgfKVld5LvXZAb3mUA75KfDll4SoEgtzwxPODoii37Ck/NB0hHFB\nGfaALql2o14U7bJryQt0bfUNAw==\n-----END PRIVATE KEY-----\n",
            "client_email": "scamonitor-admin@scamonitor.iam.gserviceaccount.com",
            "client_id": "115979597841147812420",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/scamonitor-admin%40scamonitor.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
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
