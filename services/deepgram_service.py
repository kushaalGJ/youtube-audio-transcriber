
# ==================================================
# DEEPGRAM SPEECH-TO-TEXT SERVICE
# ==================================================

# Import os to access environment variables.
import os

# Import requests to send HTTP requests to Deepgram.
import requests

# Import dotenv to load our API key from .env.
from dotenv import load_dotenv


# Load environment variables from the .env file.
load_dotenv()

import streamlit as st

def get_deepgram_api_key():
    # Use the environment variable for local development.
    api_key = get_deepgram_api_key()

    if api_key:
        return api_key

    # Use Streamlit secrets when deployed.
    return st.secrets.get("DEEPGRAM_API_KEY")


def transcribe_audio_with_language(file_path):
    """
    Convert speech into text using Deepgram Nova-3.

    Also return the detected language when available.

    Returns:
        transcript: The recognized speech.
        language: Detected language code or None.
    """

    # STEP 1: Read the Deepgram API key.
    api_key = os.getenv("DEEPGRAM_API_KEY")

    # Check whether the API key exists.
    if not api_key:
        raise ValueError("Deepgram API key is missing.")

    # STEP 2: Define the Deepgram API endpoint.
    url = "https://api.deepgram.com/v1/listen"

    # STEP 3: Configure request headers.
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/wav"
    }

    # STEP 4: Configure multilingual transcription.
    params = {
        "model": "nova-3",

        # Enable multilingual speech recognition.
        "language": "multi",

        # Improve punctuation and formatting.
        "smart_format": "true"
    }

    # STEP 5: Open the WAV audio file.
    with open(file_path, "rb") as audio_file:

        # Send the audio to Deepgram.
        response = requests.post(
            url,
            headers=headers,
            params=params,
            data=audio_file,
            timeout=180
        )

    # STEP 6: Check for API errors.
    response.raise_for_status()

    # STEP 7: Parse the JSON response.
    result = response.json()

    # Extract the first audio channel.
    channel = result["results"]["channels"][0]

    # Extract the transcript.
    transcript = channel["alternatives"][0].get(
        "transcript", ""
    )

    # STEP 8: Read language detection metadata.
    language = channel.get("detected_language")

    # Some responses contain multiple languages.
    detected_languages = channel.get(
        "detected_languages", []
    )

    # Use the first reported language if needed.
    if not language and detected_languages:
        language = detected_languages[0]

    # STEP 9: Return both transcript and language.
    return transcript, language


def transcribe_audio(file_path):
    """
    Maintain compatibility with our existing
    audio-upload transcription workflow.

    This function returns only the transcript.
    """

    # Call our multilingual transcription function.
    transcript, language = (
        transcribe_audio_with_language(file_path)
    )

    # Return only the text.
    return transcript
