
# ==================================================
# YOUTUBE AUDIO EXTRACTION SERVICE
# ==================================================

from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def extract_youtube_audio(video_url, output_dir):
    """
    Download audio from a permitted YouTube video.

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

    # Remove leftover files from previous downloads.
    for old_file in output_dir.glob("youtube_audio.*"):
        if old_file.is_file():
            old_file.unlink()

    # Configure yt-dlp.
    options = {

        # Prefer the best available audio stream.
        "format": "bestaudio/best",

        # Save audio with a predictable filename.
        "outtmpl": str(
            output_dir / "youtube_audio.%(ext)s"
        ),

        # Download only one video.
        "noplaylist": True,

        # Disable subtitle downloads.
        "writesubtitles": False,
        "writeautomaticsub": False,

        # Enable detailed logs while debugging.
        "quiet": False,
        "no_warnings": False,
        "verbose": True,

        # Stop if extraction fails.
        "ignoreerrors": False,

        # Retry temporary download failures.
        "retries": 2,
        "fragment_retries": 2,

        # Avoid indefinitely waiting for a response.
        "socket_timeout": 20,

        # Enable Node.js for YouTube JavaScript processing.
        # Requires a supported Node.js installation
        # on the deployment server.
        "js_runtimes": {
        "deno": {
            "path": str(
                Path(__file__).resolve().parents[1]
                / ".tools"
                / "deno"
            )
        }
    },
    }

    try:
        # Initialize yt-dlp.
        with YoutubeDL(options) as ydl:

            # Download the selected audio stream.
            ydl.download([video_url])

    except DownloadError as error:
        # Preserve the underlying exception for debugging.
        raise RuntimeError(
            "Unable to download audio from YouTube. "
            "The video may be restricted, unavailable, "
            "or YouTube may be rejecting requests "
            "from this hosting environment."
        ) from error

    # Find the downloaded audio file.
    downloaded_files = [
        file
        for file in output_dir.glob("youtube_audio.*")
        if file.is_file()
        and not file.name.endswith(".part")
    ]

    # Ensure a file was actually downloaded.
    if not downloaded_files:
        raise FileNotFoundError(
            "YouTube extraction completed "
            "without producing an audio file."
        )

    # Return the downloaded audio file path.
    return downloaded_files[0]
