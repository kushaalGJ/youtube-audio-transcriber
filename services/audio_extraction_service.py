
# ==================================================
# YOUTUBE AUDIO EXTRACTION SERVICE
# ==================================================

from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def extract_youtube_audio(video_url, output_dir):
    """
    Download audio from a YouTube video when permitted.

    Parameters:
        video_url: Validated YouTube video URL.
        output_dir: Temporary directory for downloaded audio.

    Returns:
        Path: Location of the downloaded audio file.

    Raises:
        RuntimeError: If YouTube extraction fails.
        FileNotFoundError: If no audio file was produced.
    """

    # Convert the directory to a Path object.
    output_dir = Path(output_dir)

    # Create the directory if necessary.
    output_dir.mkdir(parents=True, exist_ok=True)

    # Remove leftover files from earlier downloads
    # that use our predictable filename.
    for old_file in output_dir.glob("youtube_audio.*"):
        if old_file.is_file():
            old_file.unlink()

    # Configure yt-dlp.
    options = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "youtube_audio.%(ext)s"),
        "noplaylist": True,
        "writesubtitles": False,
        "writeautomaticsub": False,
        "quiet": False,
        "no_warnings": False,
        "verbose": True,
        "ignoreerrors": False,
        "retries": 2,
        "fragment_retries": 2,
        "socket_timeout": 20,
    }

    try:
        # Create the downloader.
        with YoutubeDL(options) as ydl:

            # Download audio from the requested video.
            ydl.download([video_url])

    except DownloadError as error:
        # Handle failures reported by yt-dlp.
        raise RuntimeError(
            "Unable to download audio from YouTube. "
            "The video may be unavailable, restricted, "
            "or YouTube may be rejecting requests from "
            "this hosting environment. "
            "Please try uploading an audio file instead."
        ) from error

    # Locate the downloaded audio.
    downloaded_files = [
        file
        for file in output_dir.glob("youtube_audio.*")
        if file.is_file()
        and not file.name.endswith(".part")
    ]

    # Verify that a file was downloaded.
    if not downloaded_files:
        raise FileNotFoundError(
            "YouTube extraction completed without an audio file."
        )

    return downloaded_files[0]
