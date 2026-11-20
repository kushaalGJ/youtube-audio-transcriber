
# ==================================================
# DEEPGRAM SPEECH-TO-TEXT SERVICE
# ==================================================

# Import os to access environment variables.
import os

# Import requests to communicate with the Deepgram API.
import requests

# Import dotenv to load local environment variables.
from dotenv import load_dotenv

# Import Streamlit to access deployment secrets.
import streamlit as st


# ==================================================
# STEP 1: LOAD ENVIRONMENT VARIABLES
# ==================================================

# Load variables from the local .env file.
# On Render, variables are configured in the dashboard.
load_dotenv()


# ==================================================
# STEP 2: RETRIEVE DEEPGRAM API KEY
# ==================================================

def get_deepgram_api_key():
    """
    Retrieve the Deepgram API key securely.

    Supported environments:
    1. Local development using .env
    2. Render using environment variables
    3. Streamlit Cloud using Streamlit secrets
    """

    # First, check the operating system's environment.
    api_key = os.getenv("DEEPGRAM_API_KEY")

    # Return the key if it exists.
    if api_key:
        return api_key

    # Otherwise, try Streamlit secrets.
    # Handle cases where no secrets file is configured.
    try:
        api_key = st.secrets.get("DEEPGRAM_API_KEY")

        if api_key:
            return api_key

    except (FileNotFoundError, KeyError):
        pass

    # Return None if no key is configured.
    return None


# ==================================================
# STEP 3: TRANSCRIBE AUDIO AND DETECT LANGUAGE
# ==================================================

def transcribe_audio_with_language(file_path):
    """
    Transcribe audio using Deepgram Nova-3.

    Supports multilingual speech recognition.

    Args:
        file_path: Path to the WAV audio file.

    Returns:
        tuple:
            transcript: Recognized speech as text.
            language: Detected language code or None.
    """

    # Retrieve the API key from the environment.
    api_key = get_deepgram_api_key()

    # Stop if the API key is missing.
    if not api_key:
        raise ValueError(
            "Deepgram API key is missing. "
            "Configure DEEPGRAM_API_KEY in your environment."
        )

    # Define the Deepgram speech-to-text endpoint.
    url = "https://api.deepgram.com/v1/listen"

    # Configure authentication and audio format.
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/wav"
    }

    # Configure Deepgram Nova-3.
    params = {
        # Use Deepgram's Nova-3 transcription model.
        "model": "nova-3",

        # Enable multilingual speech recognition.
        "language": "multi",

        # Improve punctuation and formatting.
        "smart_format": "true"
    }

    # ==================================================
    # STEP 4: SEND AUDIO TO DEEPGRAM
    # ==================================================

    # Open the WAV file in binary mode.
    with open(file_path, "rb") as audio_file:

        # Send audio to Deepgram for transcription.
        response = requests.post(
            url,
            headers=headers,
            params=params,
            data=audio_file,
            timeout=180
        )

    # Raise an exception for HTTP errors.
    # Examples: 401 Unauthorized, 429 Too Many Requests.
    response.raise_for_status()

    # ==================================================
    # STEP 5: PROCESS THE API RESPONSE
    # ==================================================

    # Convert the JSON response into a Python dictionary.
    result = response.json()

    # Retrieve the first audio channel.
    channels = result.get("results", {}).get("channels", [])

    # Return an empty result if no channels exist.
    if not channels:
        return "", None

    # Read the first available channel.
    channel = channels[0]

    # Retrieve transcription alternatives.
    alternatives = channel.get("alternatives", [])

    # Extract the recognized text safely.
    transcript = (
        alternatives[0].get("transcript", "")
        if alternatives
        else ""
    )

    # ==================================================
    # STEP 6: DETECT THE SPOKEN LANGUAGE
    # ==================================================

    # Try the primary detected language field.
    language = channel.get("detected_language")

    # Some responses include multiple detected languages.
    detected_languages = channel.get(
        "detected_languages", []
    )

    # Use the first detected language if necessary.
    if not language and detected_languages:
        language = detected_languages[0]

    # Return both the transcript and language code.
    return transcript, language


# ==================================================
# STEP 7: AUDIO UPLOAD COMPATIBILITY
# ==================================================

def transcribe_audio(file_path):
    """
    Transcribe audio and return only the text.

    This function maintains compatibility with
    the existing Streamlit audio-upload workflow.
    """

    # Call the multilingual transcription function.
    transcript, language = (
        transcribe_audio_with_language(file_path)
    )

    # Return only the recognized text.
    return transcript
