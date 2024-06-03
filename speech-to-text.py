import pyaudio
import wave
import openai
from pathlib import Path
from openai import OpenAI

# Initialize OpenAI client
api_key = ""
client = OpenAI(api_key=api_key)

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "audio.wav"  # Change extension to .wav for compatibility

# Record audio from microphone
audio = pyaudio.PyAudio()

print("Recording...")

stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Finished recording.")

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

# Print the transcription
print("Transcription: ", transcription.text)
