import sys
from pathlib import Path
from openai import OpenAI

api_key = "sk-proj-S3SHhak5QUB1HEI8mbAsT3BlbkFJzqgnHptaPgYqLtLMNstd"
client = OpenAI(api_key=api_key)

if len(sys.argv) < 2:
    print("Please provide the input text as a command-line argument.")
    sys.exit(1)

input_text = sys.argv[1]

speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=input_text
)

response.stream_to_file(speech_file_path)