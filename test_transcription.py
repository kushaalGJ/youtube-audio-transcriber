
# Import our translation function.
from services.translation_service import translate_to_english

# Sample Hindi text.
hindi_text = "नमस्ते, आप कैसे हैं?"

# Send the Hindi text to the translation service.
english_text = translate_to_english(
    text=hindi_text,
    source_language="hi"
)

# Display the original and translated text.
print("Original text:", hindi_text)
print("English translation:", english_text)
