
# ==================================================
# IMPORT REQUIRED LIBRARIES
# ==================================================

# Streamlit builds the web interface.
import streamlit as st

# tempfile creates temporary folders for audio processing.
import tempfile

# Path helps us manage file paths.
from pathlib import Path

# hashlib generates fingerprints to detect file changes.
import hashlib

# Import our Deepgram speech-to-text service.
from services.deepgram_service import transcribe_audio

# Import our FFmpeg audio conversion service.
from services.audio_conversion_service import convert_to_wav

# Import our audio validation functions.
from utils.file_handler import (
    validate_audio_file,
    check_audio_integrity
)
# Import our YouTube audio extraction service.
from services.audio_extraction_service import extract_youtube_audio
# Import our YouTube URL validation function.
from utils.url_validator import validate_youtube_url


# Import the multilingual Deepgram function.
from services.deepgram_service import (
    transcribe_audio_with_language
)

# Import our English translation service.
from services.translation_service import (
    translate_to_english
)

import subprocess
import sys
from pathlib import Path

DENO_PATH = Path(__file__).resolve().parent / ".tools" / "deno"

if not DENO_PATH.exists():
    subprocess.run(
        [sys.executable, "install_deno.py"],
        check=True,
        timeout=120,
    )

# ==================================================
# STEP 1: CONFIGURE THE APPLICATION
# ==================================================

# Set the browser tab title and icon.
st.set_page_config(
    page_title="AI Audio Transcriber",
    page_icon="🎙️"
)

# Display the application heading.
st.title("AI Audio Transcriber")

# Display a short description.
st.write("Convert audio into text using Deepgram AI.")


# ==================================================
# STEP 2: CHOOSE AN INPUT METHOD
# ==================================================

# Let the user choose between an audio upload and a URL.
input_method = st.radio(
    "Choose an input method:",
    ["Upload Audio", "YouTube URL"]
)


# ==================================================
# STEP 3: AUDIO UPLOAD WORKFLOW
# ==================================================

# This entire section runs ONLY when Upload Audio is selected.
if input_method == "Upload Audio":

    # Allow the user to upload MP3, WAV, or M4A.
    uploaded_file = st.file_uploader(
        "Upload an audio file",
        type=["mp3", "wav", "m4a"]
    )

    # Check whether a file was uploaded.
    if uploaded_file is not None:

        # Generate a fingerprint using the file's contents.
        file_id = hashlib.sha256(
            uploaded_file.getvalue()
        ).hexdigest()

    else:

        # No file is currently selected.
        file_id = None

    # Check whether the uploaded file has changed.
    if st.session_state.get("last_file_id") != file_id:

        # Clear the previous transcript.
        st.session_state["transcript"] = ""

        # Remember the current file's fingerprint.
        st.session_state["last_file_id"] = file_id

    # Continue only when the user has uploaded a file.
    if uploaded_file is not None:

        # Display an audio player.
        st.audio(uploaded_file)

        # Start processing when the user clicks this button.
        if st.button("Transcribe Audio"):

            # Clear the previous transcript before processing.
            st.session_state["transcript"] = ""

            # Validate the uploaded file's size and extension.
            is_valid, message = validate_audio_file(
                uploaded_file
            )

            # Display an error if validation fails.
            if not is_valid:

                st.error(message)

            else:

                # Show a loading indicator while processing.
                with st.spinner("Processing audio..."):

                    try:

                        # ==================================
                        # STEP 4: CREATE TEMPORARY FILES
                        # ==================================

                        # Create a temporary directory.
                        # It is automatically deleted after use.
                        with tempfile.TemporaryDirectory() as temp_dir:

                            # Get the original file extension.
                            extension = Path(
                                uploaded_file.name
                            ).suffix.lower()

                            # Create a path for the uploaded audio.
                            input_path = (
                                Path(temp_dir) / f"input{extension}"
                            )

                            # Create a path for the converted WAV.
                            output_path = (
                                Path(temp_dir) / "converted.wav"
                            )

                            # Save the uploaded audio to disk.
                            input_path.write_bytes(
                                uploaded_file.getvalue()
                            )

                            # ==================================
                            # STEP 5: VALIDATE AUDIO INTEGRITY
                            # ==================================

                            # Ask FFmpeg to check the audio.
                            is_healthy, integrity_message = (
                                check_audio_integrity(input_path)
                            )

                            # Reject audio that cannot be decoded.
                            if not is_healthy:

                                st.error(integrity_message)

                            else:

                                # ==============================
                                # STEP 6: CONVERT AUDIO TO WAV
                                # ==============================

                                # Convert the audio into
                                # 16 kHz mono PCM WAV format.
                                convert_to_wav(
                                    input_path,
                                    output_path
                                )

                                # ==============================
                                # STEP 7: TRANSCRIBE WITH DEEPGRAM
                                # ==============================

                                # Send the converted WAV to Deepgram.
                                transcript = transcribe_audio(
                                    output_path
                                )

                                # Save the result in session state.
                                st.session_state["transcript"] = (
                                    transcript
                                )

                                # Show feedback based on the result.
                                if transcript.strip():

                                    st.success(
                                        "Transcription completed!"
                                    )

                                else:

                                    st.warning(
                                        "No speech was detected."
                                    )

                        # Temporary audio files are deleted here.

                    # Handle unexpected processing errors.
                    except Exception:

                        # Show a friendly error message.
                        st.error(
                            "Processing failed. Check your "
                            "audio file, connection, and "
                            "Deepgram configuration."
                        )


# ==================================================
# STEP 8: YOUTUBE URL WORKFLOW
# ==================================================

# This section runs ONLY when YouTube URL is selected.

# ==================================================
# YOUTUBE TRANSCRIPTION WORKFLOW
# ==================================================

elif input_method == "YouTube URL":

    # Let the user enter a YouTube video URL.
    youtube_url = st.text_input(
        "Enter YouTube video URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )

    # Confirm that the user has permission to
    # download and process this video's audio.
    has_permission = st.checkbox(
        "I have permission to download and "
        "process this video's audio."
    )

    # Begin when the user clicks the button.
    if st.button("Transcribe YouTube Video"):

        # Clear the previous YouTube transcript.
        st.session_state["youtube_transcript"] = ""
        st.session_state["english_transcript"] = ""
        st.session_state["detected_language"] = None
        st.session_state["translation_language"] = None
        st.session_state.pop("youtube_language_choice", None)

        # Validate the URL before using it.
        is_valid, result = validate_youtube_url(
            youtube_url
        )

        if not is_valid:

            # Show the validation error.
            st.error(result)

        elif not has_permission:

            # Do not proceed without authorization.
            st.error(
                "Please confirm that you have "
                "permission to process this video."
            )

        else:

            # Construct a canonical URL from the
            # validated video ID.
            video_id = result

            safe_url = (
                f"https://www.youtube.com/watch?v={video_id}"
            )

            # Show a loading message.
            with st.spinner(
                "Downloading and transcribing audio..."
            ):

                try:

                    # Create a temporary directory.
                    # Downloaded and converted files will
                    # be deleted automatically afterward.
                    with tempfile.TemporaryDirectory() as temp_dir:

                        # STEP 1: Download permitted audio.
                        audio_path = extract_youtube_audio(
                            safe_url,
                            temp_dir
                        )

                        # STEP 2: Check audio integrity.
                        is_healthy, message = (
                            check_audio_integrity(audio_path)
                        )

                        if not is_healthy:

                            st.error(message)

                        else:

                            # STEP 3: Create a WAV output path.
                            wav_path = (
                                Path(temp_dir) / "converted.wav"
                            )

                            # STEP 4: Convert audio using FFmpeg.
                            convert_to_wav(
                                audio_path,
                                wav_path
                            )

                            # STEP 5: Transcribe audio and obtain language metadata.
                            transcript, detected_language = (
                                transcribe_audio_with_language(wav_path)
                            )

                            # STEP 6: Save the original transcript and language.
                            st.session_state["youtube_transcript"] = transcript
                            st.session_state["detected_language"] = detected_language

                            # Clear translations from previous videos.
                            st.session_state["english_transcript"] = ""
                            st.session_state["translation_language"] = None

                            # STEP 7: Display the result.
                            if transcript.strip():
                                st.success("YouTube transcription completed!")
                                if detected_language:
                                    st.info(f"Detected language: {detected_language}")
                                else:
                                    st.info("Select the spoken language below to translate.")
                            else:
                                st.warning("No speech was detected.")

                # Handle unavailable or inaccessible media.
                except Exception:

                    st.error(
                        "Unable to process this video. "
                        "Check that downloading is permitted, "
                        "the video is accessible, and "
                        "your Deepgram configuration works."
                    )

    # Display the original YouTube transcript after processing.
    if st.session_state.get("youtube_transcript"):
        st.subheader("Original YouTube Transcript")
        st.text_area(
            "Recognized speech",
            value=st.session_state["youtube_transcript"],
            height=250,
            key="youtube_original_display"
        )
        st.download_button(
            "Download Original Transcript",
            data=st.session_state["youtube_transcript"],
            file_name="youtube_original_transcript.txt",
            mime="text/plain"
        )

        # MyMemory needs one source-language code per translation request.
        # The user can correct the detected language if necessary.
        language_options = {
            "Choose language": "",
            "English": "en",
            "Hindi": "hi",
            "Kannada": "kn",
            "Telugu": "te",
            "Tamil": "ta",
            "Malayalam": "ml",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
        }

        detected_language = st.session_state.get("detected_language")
        detected_name = next(
            (name for name, code in language_options.items()
             if code and code == detected_language),
            "Choose language"
        )

        # Only set the initial value once; keep user corrections on reruns.
        if "youtube_language_choice" not in st.session_state:
            st.session_state["youtube_language_choice"] = detected_name

        selected_name = st.selectbox(
            "Language spoken in this video",
            options=list(language_options.keys()),
            key="youtube_language_choice"
        )
        selected_code = language_options[selected_name]

        # A previously translated result is invalid if the user changes language.
        if st.session_state.get("translation_language") != selected_code:
            st.session_state["english_transcript"] = ""

        if st.button("Translate to English"):
            if not selected_code:
                st.warning("Please choose the spoken language first.")
            else:
                with st.spinner("Translating into English..."):
                    try:
                        english_text = translate_to_english(
                            st.session_state["youtube_transcript"],
                            selected_code
                        )
                        st.session_state["english_transcript"] = english_text
                        st.session_state["translation_language"] = selected_code
                        st.success("English translation completed!")
                    except Exception as error:
                        st.error(f"Translation failed: {error}")

        # Show translation only when it matches the selected language.
        if (st.session_state.get("english_transcript")
                and st.session_state.get("translation_language") == selected_code):
            st.subheader("English Translation")
            st.text_area(
                "Translated transcript",
                value=st.session_state["english_transcript"],
                height=250,
                key="youtube_english_display"
            )
            st.download_button(
                "Download English Transcript",
                data=st.session_state["english_transcript"],
                file_name="youtube_english_transcript.txt",
                mime="text/plain"
            )


# ==================================================
# STEP 9: DISPLAY THE TRANSCRIPT
# ==================================================

# Only display a transcript in Upload Audio mode.
# This avoids showing an old upload transcript
# while the user is validating a YouTube URL.
if (
    input_method == "Upload Audio"
    and st.session_state.get("transcript")
):

    # Display the transcript section heading.
    st.subheader("Generated Transcript")

    # Display the recognized speech.
    st.text_area(
        "Transcript",
        value=st.session_state["transcript"],
        height=250
    )

    # Allow the user to download the transcript.
    st.download_button(
        label="Download Transcript",
        data=st.session_state["transcript"],
        file_name="transcript.txt",
        mime="text/plain"
    )
