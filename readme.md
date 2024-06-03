# OpenAI Assistant

This Python script demonstrates how to use the OpenAI API to create an AI assistant capable of understanding voice commands, searching through files, and providing spoken responses. The assistant can be customized with a name, instructions, and a list of available tools.

## Features

- Create a new assistant or retrieve an existing one using the OpenAI API.
- Upload files to a vector store and associate them with the assistant for file search capabilities.
- Record and transcribe audio input using PyAudio and the OpenAI Whisper API.
- Create a conversation thread with the assistant, attaching relevant files for context.
- Stream the assistant's responses and handle events such as text creation, tool calls, and message completion.
- Convert the assistant's text responses to speech using text-to-speech functionality.

## Requirements

- Python 3.6 or later
- OpenAI Python library (`openai`)
- PyAudio library (`pyaudio`)
- wave library (part of the Python standard library)

## Installation

1. Clone the repository:


## Usage

1. Set up your OpenAI API key in the `api_key` variable in the `Assistant.py` file.
2. Customize the assistant's name, instructions, and tools as needed.
3. Provide the necessary files (e.g., `BankData.txt`, `Guide_Bank_Data.txt`) in the same directory as the `Assistant.py` script.
4. Run the script:

5. The assistant will start listening for voice input. Speak your query or command, and the assistant will provide a spoken response based on the available information and instructions.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have any improvements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [OpenAI](https://openai.com/) for their powerful language models and APIs.
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) for audio recording functionality.
- [wave](https://docs.python.org/3/library/wave.html) for handling audio file operations.
