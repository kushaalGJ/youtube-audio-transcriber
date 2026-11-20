
# Import the URL validation function.
from utils.url_validator import validate_youtube_url


# Create different test URLs.
test_urls = [
    # Standard YouTube URL.
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",

    # Shortened YouTube URL.
    "https://youtu.be/dQw4w9WgXcQ",

    # YouTube Shorts URL.
    "https://www.youtube.com/shorts/dQw4w9WgXcQ",

    # Invalid website.
    "https://example.com/watch?v=dQw4w9WgXcQ",

    # Invalid video ID.
    "https://www.youtube.com/watch?v=123",

    # Empty input.
    ""
]


# Test each URL.
for url in test_urls:

    # Call the validator.
    is_valid, result = validate_youtube_url(url)

    # Print the result.
    print("URL:", url)
    print("Valid:", is_valid)
    print("Result:", result)
    print("-------------------------")
