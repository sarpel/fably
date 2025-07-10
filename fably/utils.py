"""
Shared utility functions.
Cross-platform compatibility for Windows development and Linux deployment.
"""

import os
import re
import logging
import json
import time
import colorsys
import zipfile
import queue
import sys

from pathlib import Path, PurePosixPath

import yaml
import numpy as np
import requests
import sounddevice as sd
import soundfile as sf

from vosk import Model, KaldiRecognizer

# Cross-platform path handling
from .cross_platform import normalize_path, ensure_directory, get_fably_paths, get_platform_info


MAX_FILE_LENGTH = 255
SOUNDS_PATH = "sounds"
QUERY_SAMPLE_RATE = 16000


def rotate_rgb_color(rgb_value, step_size=1):
    """
    Rotate an RGB color by a given step size (in degrees).

    The function takes an RGB value as input (in the format 0xRRGGBB), and
    returns a new RGB value that is a rotation of the original color by the
    given step size.

    The step size is expected to be given in degrees. The function will
    convert the step size to radians and then use it to rotate the color in
    the HSV color space. The resulting RGB color is then converted back to
    the RGB color space.
    """

    # Convert RGB value to normalized RGB components (0.0 to 1.0)
    r = ((rgb_value >> 16) & 0xFF) / 255.0
    g = ((rgb_value >> 8) & 0xFF) / 255.0
    b = (rgb_value & 0xFF) / 255.0

    # Convert RGB to HSV (Hue, Saturation, Value)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Rotate the hue component
    h = (h + (step_size / 360.0)) % 1.0  # Increment hue by step_size (in degrees)

    # Convert HSV back to RGB
    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)

    # Convert RGB components (0.0 to 1.0) back to integer RGB value
    new_rgb_value = int(r_new * 255) << 16 | int(g_new * 255) << 8 | int(b_new * 255)

    return new_rgb_value


def resolve(path):
    """
    Resolve a path to an absolute path, creating any necessary parent
    directories. Cross-platform compatible (Windows dev -> Linux deploy).

    If the given path is already absolute, it is returned as is. If it is
    relative, it is resolved relative to the directory of the current file.

    If the resolved path points to a directory, it is created if it does not
    exist.
    """
    # Use cross-platform path normalization
    normalized_path = normalize_path(path)
    
    if normalized_path.is_absolute():
        absolute_path = normalized_path
    else:
        # Resolve relative path relative to the directory of the current file
        current_file_path = Path(__file__).resolve().parent
        absolute_path = current_file_path / normalized_path
    
    # Ensure directory exists using cross-platform function
    return ensure_directory(absolute_path.parent) / absolute_path.name if absolute_path.suffix else ensure_directory(absolute_path)


def get_speech_recognizer(models_path, model_name):
    """
    Return a speech recognizer instance using the given model.

    The model is downloaded if not already available.
    Includes fallback support for Turkish models.
    """
    model_dir = Path(models_path) / Path(model_name)

    if not model_dir.exists():
        # Try to download the specified model
        success = download_vosk_model(models_path, model_name)
        
        if not success and model_name.startswith("vosk-model-small-tr"):
            # Fallback for Turkish models
            logging.warning(f"Turkish model {model_name} not found, trying fallback versions...")
            fallback_models = [
                "vosk-model-small-tr-0.3",
                "vosk-model-small-tr-0.22", 
                "vosk-model-small-tr-0.21"
            ]
            
            for fallback_model in fallback_models:
                if fallback_model != model_name:
                    logging.info(f"Trying fallback Turkish model: {fallback_model}")
                    success = download_vosk_model(models_path, fallback_model)
                    if success:
                        model_name = fallback_model
                        model_dir = Path(models_path) / Path(model_name)
                        break
            
            if not success:
                raise RuntimeError(f"Failed to download any Turkish Vosk model. Please check your internet connection or manually download from https://alphacephei.com/vosk/models/")
        elif not success:
            raise RuntimeError(f"Failed to download Vosk model {model_name}. Please check your internet connection.")

    model = Model(str(model_dir))
    return KaldiRecognizer(
        model, QUERY_SAMPLE_RATE
    )  # The sample rate is fixed in the model


def download_vosk_model(models_path, model_name):
    """
    Download a Vosk model from the official repository.
    
    Args:
        models_path: Path to store models
        model_name: Name of the model to download
        
    Returns:
        bool: True if download succeeded, False otherwise
    """
    model_dir = Path(models_path) / Path(model_name)
    zip_path = model_dir.with_suffix(".zip")
    model_url = f"https://alphacephei.com/vosk/models/{model_name}.zip"

    try:
        logging.info(f"Downloading {model_name} from {model_url}...")

        # Download the model with timeout and proper error handling
        with requests.get(model_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            
            # Create directory if it doesn't exist
            zip_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Unzip the model
        logging.info(f"Unzipping {model_name}...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(model_dir.parent)

        # Remove the zip file after extraction
        if zip_path.exists():
            zip_path.unlink()
            
        logging.info(f"Model {model_name} downloaded and unpacked successfully in {model_dir}")
        return True
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error downloading {model_name}: {e}")
        return False
    except zipfile.BadZipFile as e:
        logging.error(f"Invalid zip file for {model_name}: {e}")
        if zip_path.exists():
            zip_path.unlink()
        return False
    except Exception as e:
        logging.error(f"Unexpected error downloading {model_name}: {e}")
        if zip_path.exists():
            zip_path.unlink()
        return False


def write_audio_data_to_file(audio_data, audio_file, sample_rate):
    """Write audio data to a file with the given sample rate."""
    sf.write(audio_file, audio_data, sample_rate)


def play_sound(sound, audio_driver="alsa", fallback_silent=False):
    """
    Play a sound file with the given name.
    
    Args:
        sound: Name of the sound file (without .wav extension)
        audio_driver: Audio driver to use ("alsa" or "sounddevice")
        fallback_silent: If True, fail silently when sound file not found
    """
    sound_file = Path(__file__).resolve().parent / SOUNDS_PATH / f"{sound}.wav"
    if not sound_file.exists():
        if fallback_silent:
            logging.debug(f"Sound {sound} not found at {sound_file}, skipping...")
            return
        else:
            raise ValueError(f"Sound {sound} not found in path {sound_file}.")
    play_audio_file(sound_file, audio_driver)


def play_audio_file(audio_file, audio_driver="alsa"):
    """
    Play the given audio file using the configured sound driver.
    """
    logging.debug("Playing audio from %s with %s", audio_file, audio_driver)
    if audio_driver == "sounddevice":
        audio_data, sampling_frequency = sf.read(audio_file)
        sd.play(audio_data, sampling_frequency)
        sd.wait()
    elif audio_driver == "alsa":
        if audio_file.suffix == ".mp3":
            os.system(f"mpg123 {audio_file}")
        else:
            os.system(f"aplay {audio_file}")
    else:
        raise ValueError(f"Unsupported audio driver: {audio_driver}")
    logging.debug("Done playing %s with %s", audio_file, audio_driver)


def query_to_filename(query, prefix):
    """
    Convert a query from a voice assistant into a file name that can be used to save the story.

    This function removes the query guard part and removes any illegal characters from the file name.
    """
    # Remove the query guard part since it doesn't add any information
    query = query.lower().replace(prefix, "", 1).strip()

    # Remove the period at the end if it exists
    if query.endswith("."):
        query = query[:-1]

    # Replace illegal file name characters with underscores and truncate
    return re.sub(r'[\\/*?:"<>| ]', "_", query)[:MAX_FILE_LENGTH]


def write_to_file(path, text):
    """
    Write the given text to a file at the given path.
    """
    with open(path, "w", encoding="utf8") as f:
        f.write(text)


def read_from_file(path):
    """
    Read the contents of a file at the given path and return the text.
    """
    return Path(path).read_text(encoding="utf8")


def write_to_yaml(path, data):
    """
    Write data to a YAML file at the given path.
    """
    with open(path, "w", encoding="utf-8") as file:
        yaml.dump(data, file, default_flow_style=False)


def read_from_yaml(path):
    """
    Read data from a YAML file at the given path.
    """
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def record_until_silence(
    recognizer, trim_first_frame=False, sample_rate=QUERY_SAMPLE_RATE
):
    """
    Records audio until silence is detected.
    This uses a tiny speech recognizer (vosk) to detect silence.

    Returns an nparray of int16 samples.

    NOTE: There are probably less overkill ways to do this but this works well enough for now.
    """
    query = []
    recorded_frames = []
    recognition_queue = queue.Queue()

    def callback(indata, frames, _time, _status):
        """This function is called for each audio block from the microphone"""
        logging.debug("Recorded audio frame with %i samples", frames)
        recognition_queue.put(bytes(indata))
        recorded_frames.append(bytes(indata))

    with sd.RawInputStream(
        samplerate=sample_rate,
        blocksize=sample_rate // 4,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        logging.debug("Recording voice query...")

        while True:
            data = recognition_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if result["text"]:
                    query.append(result["text"])
                    break

        final_result = json.loads(recognizer.FinalResult())
        query.append(final_result["text"])

    npframes = [np.frombuffer(frame, dtype=np.int16) for frame in recorded_frames]

    if trim_first_frame:
        npframes = npframes.pop(0)

    return np.concatenate(npframes, axis=0), sample_rate, " ".join(query)


def transcribe(
    stt_client,
    audio_data,
    stt_model="whisper-1",
    language="en",
    sample_rate=QUERY_SAMPLE_RATE,
    audio_path=None,
):
    """
    Transcribes the given audio data using the OpenAI API.
    """

    file_name = time.strftime("%d_%m_%Y-%H_%M_%S") + ".wav"

    if not audio_path:
        audio_file = Path(file_name)
    else:
        audio_path = audio_path if isinstance(audio_path, Path) else Path(audio_path)
        if audio_path.is_dir():
            audio_file = audio_path / file_name
        else:
            audio_file = audio_path
    write_audio_data_to_file(audio_data, audio_file, sample_rate)

    logging.debug("Sending voice query for transcription...")

    with open(audio_file, "rb") as query:
        response = stt_client.audio.transcriptions.create(
            model=stt_model, language=language, file=query
        )

    return response.text, audio_file


def find_story_for_continuation(stories_path, query, continuation_patterns=None):
    """
    Find the appropriate story to continue based on a continuation query.
    
    Args:
        stories_path: Path to the stories directory
        query: The user's continuation query
        continuation_patterns: List of continuation patterns to recognize
        
    Returns:
        Path: Path to the story directory to continue, or None if not found
    """
    if not is_continuation_query(query, continuation_patterns):
        return None
    
    # Try to extract a specific topic from the query
    topic = extract_topic_from_query(query)
    
    if topic:
        # Look for stories matching the topic
        matching_stories = find_stories_by_topic(stories_path, topic, max_results=1)
        if matching_stories:
            logging.info(f"Found story to continue based on topic '{topic}': {matching_stories[0].name}")
            return matching_stories[0]
    
    # Fallback to most recent story
    recent_story = get_most_recent_story(stories_path)
    if recent_story:
        logging.info(f"Using most recent story for continuation: {recent_story.name}")
        return recent_story
    
    logging.warning("No existing stories found for continuation")
    return None


# Story Continuation Utilities


def is_continuation_query(query, continuation_patterns=None):
    """
    Check if a query is asking for story continuation.
    
    Args:
        query: The user's voice query
        continuation_patterns: List of patterns that indicate continuation requests
        
    Returns:
        bool: True if this is a continuation query
    """
    if not continuation_patterns:
        continuation_patterns = [
            "continue the story",
            "tell me more",
            "what happens next", 
            "continue",
            "keep going",
            "more story"
        ]
    
    query_lower = query.lower().strip()
    
    for pattern in continuation_patterns:
        if pattern.lower() in query_lower:
            return True
    
    return False


def extract_topic_from_query(query):
    """
    Extract topic keywords from a continuation query.
    
    Args:
        query: The user's continuation query
        
    Returns:
        str: Extracted topic or None if no specific topic found
    """
    query_lower = query.lower().strip()
    
    # Patterns to extract topics from continuation queries
    patterns = [
        r"continue the story about (.+)",
        r"tell me more about (.+)",
        r"what happens next (?:in|with|to) (.+)",
        r"continue (.+)",
        r"more about (.+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            topic = match.group(1).strip()
            # Clean up common endings
            topic = re.sub(r"\s+(story|tale)$", "", topic)
            return topic
    
    return None


def find_stories_by_topic(stories_path, topic, max_results=5):
    """
    Find existing stories that match a given topic.
    
    Args:
        stories_path: Path to the stories directory
        topic: Topic keywords to search for
        max_results: Maximum number of results to return
        
    Returns:
        List[Path]: List of story directory paths, sorted by relevance
    """
    if not topic:
        return []
    
    stories_path = Path(stories_path)
    if not stories_path.exists():
        return []
    
    topic_words = set(topic.lower().split())
    matching_stories = []
    
    for story_dir in stories_path.iterdir():
        if not story_dir.is_dir():
            continue
        
        # Check directory name for topic matches
        dir_name = story_dir.name.lower()
        dir_words = set(re.findall(r'\w+', dir_name))
        
        # Calculate relevance score based on word overlap
        common_words = topic_words.intersection(dir_words)
        if common_words:
            relevance_score = len(common_words) / len(topic_words)
            matching_stories.append((story_dir, relevance_score))
    
    # Sort by relevance score (descending) and return paths
    matching_stories.sort(key=lambda x: x[1], reverse=True)
    return [story[0] for story in matching_stories[:max_results]]


def get_most_recent_story(stories_path):
    """
    Get the most recently modified story directory.
    
    Args:
        stories_path: Path to the stories directory
        
    Returns:
        Path: Path to the most recent story directory, or None if no stories found
    """
    stories_path = Path(stories_path)
    if not stories_path.exists():
        return None
    
    story_dirs = [d for d in stories_path.iterdir() if d.is_dir()]
    if not story_dirs:
        return None
    
    # Sort by modification time (most recent first)
    story_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return story_dirs[0]


def get_next_paragraph_index(story_path):
    """
    Get the next paragraph index for a story continuation.
    
    Args:
        story_path: Path to the story directory
        
    Returns:
        int: Next paragraph index to use
    """
    story_path = Path(story_path)
    if not story_path.exists():
        return 0
    
    # Find all existing paragraph files
    paragraph_files = list(story_path.glob("paragraph_*.txt"))
    if not paragraph_files:
        return 0
    
    # Extract indices and find the maximum
    indices = []
    for file in paragraph_files:
        match = re.search(r'paragraph_(\d+)\.txt', file.name)
        if match:
            indices.append(int(match.group(1)))
    
    return max(indices) + 1 if indices else 0


def extract_story_context(story_path, max_paragraphs=None):
    """
    Extract the context from an existing story for continuation.
    
    Args:
        story_path: Path to the story directory
        max_paragraphs: Maximum number of paragraphs to include (None for all)
        
    Returns:
        dict: Story context with 'original_query', 'paragraphs', and 'paragraph_count'
    """
    story_path = Path(story_path)
    context = {
        'original_query': None,
        'paragraphs': [],
        'paragraph_count': 0
    }
    
    if not story_path.exists():
        return context
    
    # Read original query from info.yaml
    info_file = story_path / "info.yaml"
    if info_file.exists():
        try:
            info_data = read_from_yaml(info_file)
            context['original_query'] = info_data.get('query', 'Unknown')
        except Exception as e:
            logging.warning(f"Failed to read story info from {info_file}: {e}")
    
    # Read all paragraph files
    paragraph_files = list(story_path.glob("paragraph_*.txt"))
    paragraph_files.sort(key=lambda x: int(re.search(r'paragraph_(\d+)', x.name).group(1)))
    
    # Limit paragraphs if specified
    if max_paragraphs:
        paragraph_files = paragraph_files[:max_paragraphs]
    
    for file in paragraph_files:
        try:
            content = read_from_file(file)
            context['paragraphs'].append(content.strip())
        except Exception as e:
            logging.warning(f"Failed to read paragraph from {file}: {e}")
    
    context['paragraph_count'] = len(context['paragraphs'])
    return context


# Audio Quality and Noise Reduction Utilities


def calculate_rms_energy(audio_data):
    """
    Calculate the Root Mean Square (RMS) energy of audio data.
    
    Args:
        audio_data: numpy array of audio samples
        
    Returns:
        float: RMS energy value
    """
    return np.sqrt(np.mean(np.square(audio_data)))


def calibrate_noise_floor(sample_rate=QUERY_SAMPLE_RATE, duration=3.0, percentile=95):
    """
    Calibrate the ambient noise floor by recording silence for a short period.
    
    Args:
        sample_rate: Audio sample rate
        duration: Duration in seconds to record for calibration
        percentile: Percentile of energy values to use as noise floor
        
    Returns:
        float: Calibrated noise floor energy level
    """
    logging.info(f"Calibrating noise floor for {duration} seconds...")
    
    energy_samples = []
    
    def calibration_callback(indata, frames, time, status):
        """Callback to collect energy samples during calibration."""
        if status:
            logging.warning(f"Audio input status: {status}")
        
        audio_chunk = indata[:, 0] if indata.shape[1] > 0 else indata.flatten()
        energy = calculate_rms_energy(audio_chunk)
        energy_samples.append(energy)
    
    try:
        with sd.InputStream(
            samplerate=sample_rate,
            blocksize=sample_rate // 4,
            dtype="int16",
            channels=1,
            callback=calibration_callback,
        ):
            # Record for the specified duration
            sd.sleep(int(duration * 1000))
        
        if energy_samples:
            noise_floor = np.percentile(energy_samples, percentile)
            logging.info(f"Noise floor calibrated: {noise_floor:.6f} (from {len(energy_samples)} samples)")
            return noise_floor
        else:
            logging.warning("No energy samples collected during calibration")
            return 0.01  # Default fallback value
            
    except Exception as e:
        logging.error(f"Noise floor calibration failed: {e}")
        return 0.01  # Default fallback value


def apply_noise_gate(audio_data, noise_floor, sensitivity=2.0):
    """
    Apply a noise gate to audio data based on energy threshold.
    
    Args:
        audio_data: numpy array of audio samples
        noise_floor: Calibrated noise floor energy level
        sensitivity: Multiplier for noise threshold (higher = more sensitive)
        
    Returns:
        numpy array: Filtered audio data (silent if below threshold)
    """
    energy = calculate_rms_energy(audio_data)
    threshold = noise_floor * sensitivity
    
    # If energy is below threshold, return silence
    if energy < threshold:
        return np.zeros_like(audio_data)
    
    return audio_data


def preprocess_audio(audio_data, noise_floor=None, sensitivity=2.0, apply_filtering=True):
    """
    Apply audio preprocessing including noise reduction and quality enhancements.
    
    Args:
        audio_data: numpy array of audio samples
        noise_floor: Calibrated noise floor (None to skip noise gate)
        sensitivity: Noise gate sensitivity
        apply_filtering: Whether to apply noise filtering
        
    Returns:
        numpy array: Processed audio data
    """
    if not apply_filtering or noise_floor is None:
        return audio_data
    
    # Apply noise gate
    filtered_audio = apply_noise_gate(audio_data, noise_floor, sensitivity)
    
    # Additional preprocessing could be added here:
    # - High-pass filter to remove low-frequency noise
    # - Dynamic range compression
    # - Spectral subtraction for advanced noise reduction
    
    return filtered_audio


def record_until_silence_with_noise_reduction(
    recognizer, 
    trim_first_frame=False, 
    sample_rate=QUERY_SAMPLE_RATE,
    noise_floor=None,
    noise_sensitivity=2.0,
    enable_noise_reduction=True
):
    """
    Enhanced version of record_until_silence with noise reduction capabilities.
    
    Args:
        recognizer: Vosk speech recognizer
        trim_first_frame: Whether to trim the first audio frame
        sample_rate: Audio sample rate
        noise_floor: Calibrated noise floor energy level
        noise_sensitivity: Noise gate sensitivity multiplier
        enable_noise_reduction: Whether to apply noise reduction
        
    Returns:
        tuple: (audio_data, sample_rate, transcribed_text)
    """
    query = []
    recorded_frames = []
    recognition_queue = queue.Queue()
    
    def callback(indata, frames, _time, _status):
        """Enhanced callback with noise reduction"""
        audio_chunk = indata[:, 0] if indata.shape[1] > 0 else indata.flatten()
        
        # Apply noise reduction preprocessing
        if enable_noise_reduction and noise_floor is not None:
            processed_chunk = preprocess_audio(
                audio_chunk, 
                noise_floor, 
                noise_sensitivity, 
                apply_filtering=True
            )
        else:
            processed_chunk = audio_chunk
        
        # Only process non-silent chunks
        if enable_noise_reduction and noise_floor is not None:
            chunk_energy = calculate_rms_energy(processed_chunk)
            if chunk_energy < noise_floor * noise_sensitivity:
                # Skip processing silent chunks but still record original
                recorded_frames.append(bytes(indata))
                return
        
        logging.debug("Recorded audio frame with %i samples", frames)
        recognition_queue.put(bytes(processed_chunk))
        recorded_frames.append(bytes(indata))  # Store original unprocessed audio

    with sd.RawInputStream(
        samplerate=sample_rate,
        blocksize=sample_rate // 4,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        logging.debug("Recording voice query with noise reduction...")

        while True:
            data = recognition_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if result["text"]:
                    query.append(result["text"])
                    break

        final_result = json.loads(recognizer.FinalResult())
        query.append(final_result["text"])

    npframes = [np.frombuffer(frame, dtype=np.int16) for frame in recorded_frames]

    if trim_first_frame and npframes:
        npframes.pop(0)

    audio_data = np.concatenate(npframes, axis=0) if npframes else np.array([])
    return audio_data, sample_rate, " ".join(query)
