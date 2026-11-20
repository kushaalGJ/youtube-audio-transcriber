
# Import the translation function.
from services.translation_service import (
    translate_to_english
)


# Sample Hindi sentence.
hindi_text = "नमस्ते, आप कैसे हैं?"

# Translate Hindi into English.
english_text = translate_to_english(
    hindi_text,
    source_language="hi"
)

# Display the results.
print("Original:", hindi_text)
print("English:", english_text)
