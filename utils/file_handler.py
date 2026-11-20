

# Maximum allowed upload size: 10 MiB.
MAX_FILE_SIZE = 10 * 1024 * 1024

# File extensions our application supports.
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a"}


def validate_audio_file(uploaded_file):
    # Check whether the user selected a file.
    if uploaded_file is None:
        return False, "Please upload an audio file."

    # Reject files containing no data.
    if uploaded_file.size == 0:
        return False, "The uploaded file is empty."

    # Reject files exceeding our upload limit.
    if uploaded_file.size > MAX_FILE_SIZE:
        return False, "File must be 10 MiB or smaller."

    # Extract the extension from the filename.
    from pathlib import Path
    extension = Path(uploaded_file.name).suffix.lower()

    # Check whether the extension is supported.
    if extension not in ALLOWED_EXTENSIONS:
        return False, "Only MP3, WAV, and M4A are supported."

    # Basic checks passed.
    # Actual audio decoding is checked separately.
    return True, "Basic validation passed."


import subprocess

def check_audio_integrity(file_path):
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-v", "error",
                "-xerror",
                "-i", str(file_path),
                "-map", "0:a:0",
                "-f", "null",
                "-"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return True, "Audio decoded successfully."

        return False, "The audio file is invalid or corrupted."

    except subprocess.TimeoutExpired:
        return False, "Audio validation took too long."

    except FileNotFoundError:
        return False, "FFmpeg is not installed or not in PATH."
