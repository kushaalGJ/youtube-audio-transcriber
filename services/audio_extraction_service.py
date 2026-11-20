
# ==================================================
# YOUTUBE AUDIO EXTRACTION SERVICE
# ==================================================

# Path helps us manage downloaded files.
from pathlib import Path

# YoutubeDL provides yt-dlp's Python interface.
from yt_dlp import YoutubeDL


def extract_youtube_audio(video_url, output_dir):
    """
    Download audio from a permitted YouTube video.

    Parameters:
        video_url: Valid YouTube video URL.
        output_dir: Temporary directory for downloaded audio.

    Returns:
        Path to the downloaded audio file.
    """

    # Convert the output directory to a Path object.
    output_dir = Path(output_dir)

    # Create the directory if it doesn't exist.
    output_dir.mkdir(parents=True, exist_ok=True)

    # Configure yt-dlp.
    options = {

        # Prefer an audio-only stream.
        "format": "bestaudio/best",

        # Save the file using a predictable filename.
        "outtmpl": str(output_dir / "youtube_audio.%(ext)s"),

        # Process only one video, not a playlist.
        "noplaylist": True,

        # Disable subtitle downloads.
        "writesubtitles": False,
        "writeautomaticsub": False,

        # Reduce unnecessary console output.
        "quiet": True,
        "no_warnings": True,

        # Stop if the video is unavailable.
        "ignoreerrors": False,
    }

    # Create a yt-dlp instance.
    with YoutubeDL(options) as ydl:

        # Download the selected audio stream.
        # Only call this for content you're authorized
        # to download and process.
        ydl.download([video_url])

    # Find the downloaded audio file.
    downloaded_files = [
        file
        for file in output_dir.glob("youtube_audio.*")
        if file.is_file()
    ]

    # Check whether the download produced a file.
    if not downloaded_files:
        raise FileNotFoundError(
            "No audio file was downloaded."
        )

    # Return the downloaded audio file's path.
    return downloaded_files[0]
