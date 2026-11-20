
# ==================================================
# YOUTUBE URL VALIDATION SERVICE
# ==================================================

# urlparse separates a URL into its components.
from urllib.parse import urlparse, parse_qs

# Regular expressions help us check video IDs.
import re


def validate_youtube_url(url):
    """
    Validate a YouTube URL and extract its video ID.

    Returns:
        (True, video_id) for a valid URL.
        (False, error_message) for an invalid URL.
    """

    # STEP 1: Reject empty input.
    if not url or not url.strip():
        return False, "Please enter a YouTube URL."

    # STEP 2: Remove spaces around the URL.
    url = url.strip()

    # STEP 3: Parse the URL into components.
    parsed_url = urlparse(url)

    # STEP 4: Only accept HTTPS URLs.
    if parsed_url.scheme != "https":
        return False, "Please use an HTTPS YouTube URL."

    # STEP 5: Get the website hostname.
    hostname = (parsed_url.hostname or "").lower()

    # STEP 6: Extract the video ID based on URL type.
    if hostname in ("youtube.com", "www.youtube.com"):

        # Example:
        # https://www.youtube.com/watch?v=VIDEO_ID
        if parsed_url.path == "/watch":

            # Extract the v parameter from the URL.
            parameters = parse_qs(parsed_url.query)

            video_id = parameters.get("v", [""])[0]

        # Example:
        # https://www.youtube.com/shorts/VIDEO_ID
        elif parsed_url.path.startswith("/shorts/"):

            video_id = parsed_url.path.split("/")[2]

        else:
            return False, "Unsupported YouTube URL format."

    elif hostname == "youtu.be":

        # Example:
        # https://youtu.be/VIDEO_ID
        video_id = parsed_url.path.strip("/")

    else:

        # Reject unrelated websites.
        return False, "Please enter a valid YouTube URL."

    # STEP 7: Validate the video ID format.
    # YouTube video IDs normally contain 11 characters.
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        return False, "Invalid YouTube video ID."

    # STEP 8: Return the extracted video ID.
    return True, video_id
