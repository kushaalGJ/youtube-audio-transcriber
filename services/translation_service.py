
# Import requests for HTTP API communication.
import requests

# Import time to add a short delay between requests.
import time

# MyMemory translation endpoint.
TRANSLATION_URL = (
    "https://api.mymemory.translated.net/get"
)

# Keep chunks below the API's 500-byte limit.
MAX_CHUNK_BYTES = 450


def split_text_into_chunks(text):
    """
    Split text into chunks of at most 450 UTF-8 bytes.

    UTF-8 bytes matter because characters in
    Hindi, Kannada, Tamil, etc. may occupy
    more than one byte.
    """

    # Store the resulting chunks here.
    chunks = []

    # Start with an empty chunk.
    current_chunk = ""

    # Process the text character by character.
    for character in text:

        # Try adding the next character.
        candidate = current_chunk + character

        # Check the byte length, not character count.
        if len(candidate.encode("utf-8")) <= MAX_CHUNK_BYTES:

            # The candidate still fits.
            current_chunk = candidate

        else:

            # Save the completed chunk.
            if current_chunk:
                chunks.append(current_chunk)

            # Start a new chunk.
            current_chunk = character

    # Save the final chunk.
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def translate_to_english(text, source_language):
    """
    Translate a transcript into English using MyMemory.

    Long transcripts are divided into smaller requests.
    """

    # Return immediately if the transcript is empty.
    if not text or not text.strip():
        return ""

    # No translation is required for English text.
    if source_language == "en":
        return text

    # A language code is required by MyMemory.
    if not source_language:
        raise ValueError(
            "Source language is required for translation."
        )

    # Split the transcript into API-safe chunks.
    chunks = split_text_into_chunks(text)

    # Store translated chunks in this list.
    translated_chunks = []

    # Translate each chunk individually.
    for chunk in chunks:

        # Prepare the API request parameters.
        params = {
            "q": chunk,
            "langpair": f"{source_language}|en"
        }

        # Send the chunk to MyMemory.
        response = requests.get(
            TRANSLATION_URL,
            params=params,
            timeout=30
        )

        # Check for HTTP errors.
        response.raise_for_status()

        # Parse the JSON response.
        result = response.json()

        # Check whether the API accepted the request.
        if result.get("responseStatus") != 200:
            raise RuntimeError(
                result.get(
                    "responseDetails",
                    "Translation failed."
                )
            )

        # Extract the translated text.
        translated_text = result["responseData"][
            "translatedText"
        ]

        # Save the translated chunk.
        translated_chunks.append(translated_text)

        # Briefly space out API requests.
        time.sleep(0.2)

    # Combine all translated chunks into one string.
    return "".join(translated_chunks)
