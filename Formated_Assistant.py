import os
import openai
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
from pathlib import Path
import subprocess
import pyaudio
import wave

"""
This program demonstrates how to use the OpenAI API to create an assistant, upload files to a vector store,
and have a conversation with the assistant using voice input and audio output.
"""

# Set the API key
api_key = ""
client = OpenAI(api_key=api_key)

# Create the assistant or check if one already exists
assistant_id = 'asst_fNFnL4zAeTqijcmsxPZXfiFe'

def check_assistant_exists(assistant_id):
    """
    Checks if an assistant with the given ID exists.

    Args:
        assistant_id (str): The ID of the assistant to check.

    Returns:
        bool: True if the assistant exists, False otherwise.
    """
    try:
        response = client.beta.assistants.retrieve(assistant_id)
        return True if response else False
    except Exception as e:
        print(f"An error occurred while checking the assistant: {e}", file=sys.stderr)
        return False

if not check_assistant_exists(assistant_id):
    # Assistant creation logic - Ensure values are from config or inputs
    assistant = client.beta.assistants.create(
        name=os.getenv("ASSISTANT_NAME", "Default Assistant Name"),
        instructions=os.getenv("ASSISTANT_INSTRUCTIONS", "Default Instructions"),
        tools=[{"type": "code_interpreter"}],
        model="gpt-4"
    )
    assistant_id = assistant["id"]

# Create a thread
thread = client.beta.threads.create()

# Create a vector store called "Financial Statements"
vector_store = client.beta.vector_stores.create(name="BankData")

# Ready the files for upload to OpenAI
file_paths = ["BankData.txt", "Guide_Bank_Data.txt"]

# Open the files in binary mode
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

# Print the status and the file counts of the batch
print(file_batch.status)
print(file_batch.file_counts)

# Update the assistant to use the files now
assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# Let's create a chat thread to talk with the assistant

# Upload the user provided file to OpenAI
def record_and_transcribe_audio():
    """
    Records audio from the microphone, saves it to a file, and transcribes it using the OpenAI Whisper API.

    Returns:
        str: The transcribed text from the audio recording.
    """
    # Audio recording parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 10
    WAVE_OUTPUT_FILENAME = "audio.wav"

    # Record audio from microphone
    audio = pyaudio.PyAudio()

    print("Listening...")

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Done.")

    # Stop recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio as a file
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    # Perform speech-to-text transcription
    with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    return transcription.text

# Record and transcribe audio
user_message = record_and_transcribe_audio()

# Upload the user provided file to OpenAI
message_file = client.files.create(
    file=open("BankData.txt", "rb"), purpose="assistants"
)

# Create a thread and attach the file to the message
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": user_message,
            # Attach the new file to the message.
            "attachments": [
                {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
            ],
        }
    ]
)

class EventHandler(AssistantEventHandler):
    """
    An event handler for the OpenAI assistant that prints the assistant's responses and citations.
    """

    @override
    def on_text_created(self, text) -> None:
        """
        Handles the event when the assistant creates text.

        Args:
            text (str): The text created by the assistant.
        """
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        """
        Handles the event when the assistant calls a tool.

        Args:
            tool_call (ToolCall): The tool call made by the assistant.
        """
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        """
        Handles the event when the assistant finishes processing a message.

        Args:
            message (Message): The message processed by the assistant.
        """
        # Print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        script_path = Path(__file__).parent / "tex-to-speech.py"
        response_text = message_content.value
        subprocess.run(["python", str(script_path), response_text])

# Then, we use the stream SDK helper
# with the EventHandler class to create the Run
# and stream the response.
with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Sir.",
    event_handler=EventHandler(),
) as stream:
    stream.until_done()
