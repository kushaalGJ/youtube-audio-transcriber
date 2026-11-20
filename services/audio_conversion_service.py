
# subprocess allows Python to execute FFmpeg.
import subprocess

# Path helps us work with file paths.
from pathlib import Path


def convert_to_wav(input_path, output_path):
    """
    Convert an audio file into 16 kHz mono PCM WAV.

    Parameters:
        input_path: Location of the original audio file.
        output_path: Location for the converted WAV file.
    """

    # Build the FFmpeg command as a list.
    command = [
        "ffmpeg",

        # Do not ask questions in the terminal.
        "-nostdin",

        # Overwrite the output file if it exists.
        "-y",

        # Only display FFmpeg error messages.
        "-v", "error",

        # Path of the original audio file.
        "-i", str(input_path),

        # Select the first audio stream.
        "-map", "0:a:0",

        # Disable video output.
        "-vn",

        # Use 16-bit PCM encoding.
        "-c:a", "pcm_s16le",

        # Set sample rate to 16,000 Hz.
        "-ar", "16000",

        # Convert audio to one channel (mono).
        "-ac", "1",

        # Save the converted audio.
        str(output_path)
    ]

    try:
        # Run FFmpeg and wait for it to finish.
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=120
        )

    except subprocess.TimeoutExpired:
        # Handle files taking too long to convert.
        raise ValueError("Audio conversion timed out.")

    except subprocess.CalledProcessError:
        # Handle invalid or unsupported audio.
        raise ValueError(
            "Audio could not be decoded or converted."
        )

    except FileNotFoundError:
        # Handle missing FFmpeg installation.
        raise RuntimeError(
            "FFmpeg is not installed or not in PATH."
        )

    # Verify that FFmpeg created the output file.
    output = Path(output_path)

    if not output.exists() or output.stat().st_size == 0:
        raise ValueError("Converted audio is empty.")

    # Return the converted file's location.
    return str(output)
