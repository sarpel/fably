# Project: Fably - AI Storyteller

## General Instructions:

* When generating new Python code, please follow the existing coding style as defined in the `.pylintrc` file.
* Ensure all new functions and classes have comprehensive docstrings that explain their purpose, arguments, and return values.
* All code should be compatible with **Python 3.8+** and optimized for deployment on hardware like the **Raspberry Pi**.
* The project uses `asyncio` for concurrent operations, especially for handling I/O with API calls and hardware. New code should follow this pattern where appropriate.

## Coding Style:

* Use **4 spaces** for indentation.
* Follow **snake\_case** for function, method, and variable names (e.g., `generate_story`, `story_path`).
* Use **PascalCase** for class names (e.g., `EnhancedFablyContext`, `VoiceManager`).
* Private class members should be prefixed with an underscore (`_`) (e.g., `_load_config`).
* Constants should be in **UPPER\_CASE** (e.g., `MAX_TOKENS`, `DEFAULT_CONFIG`).

## Specific Component: `fably/tts_service.py`

* This file provides a unified interface for multiple Text-to-Speech (TTS) providers like OpenAI and ElevenLabs.
* When adding a new TTS provider, create a new class that inherits from the `TTSProvider` abstract base class.
* The new provider class must implement the `synthesize` and `get_available_voices` methods.
* Ensure the new provider is registered in the `initialize_tts_service` function to make it available to the application.

## Regarding Dependencies:

* Avoid introducing new external dependencies unless absolutely necessary. The current dependencies are listed in `setup.py`.
* If a new dependency is required, please state the reason and explain how it should be added to the `setup.py` file.