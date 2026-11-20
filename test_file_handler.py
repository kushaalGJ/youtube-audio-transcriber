
from io import BytesIO
from utils.file_handler import validate_audio_file

class MockUploadedFile:
    def __init__(self, name, content):
        self.name = name
        self.size = len(content)

tests = [
    MockUploadedFile("lecture.mp3", b"sample"),
    MockUploadedFile("empty.mp3", b""),
    MockUploadedFile("notes.txt", b"sample"),
    MockUploadedFile("large.mp3", b"x" * (10 * 1024 * 1024 + 1))
]

for file in tests:
    valid, message = validate_audio_file(file)
    print(file.name, ":", valid, "-", message)
