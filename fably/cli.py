"""
Fably's Command line interface.
"""

import logging
import os
import platform
import sys

import click

from dotenv import load_dotenv

from fably import fably
from fably import utils
from fably import leds
from fably.tts_service import initialize_tts_service, tts_service
from fably.voice_manager import voice_manager

from fably.cli_utils import pass_context

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
DEEPSEEK_URL = "https://api.deepseek.com/v1"
OLLAMA_URL = "http://127.0.0.1:11434/v1"
ELEVENLABS_URL = "https://api.elevenlabs.io"

PROMPT_FILE = "./fably/prompt.txt"
QUERIES_PATH = "./queries"
STORIES_PATH = "./stories"
MODELS_PATH = "./models"
SOUND_MODEL = "vosk-model-small-tr-0.3"  # Türkçe model (güncellenmiş)
SAMPLE_RATE = 24000
LLM_URL = GEMINI_URL
LLM_MODEL = "o4-mini"
# LLM_MODEL = "gpt-3.5-turbo"
TEMPERATURE = 1.0
MAX_TOKENS = 2000
TTS_URL = GEMINI_URL
TTS_MODEL = "tts-1"
TTS_VOICE = "nova"
TTS_FORMAT = "mp3"
LANGUAGE = "tr"  # Sadece Türkçe
BUTTON_GPIO_PIN = 17
HOLD_TIME = 3
SOUND_DRIVER = "alsa"
QUERY_GUARD = ""  # No more rigid query requirements - users can speak freely
CONTINUATION_PATTERNS = [
    "hikayeye devam et", 
    "daha anlat", 
    "sonra ne oldu", 
    "devam et", 
    "hikayeyi surdur", 
    "ne olacak simdi"
]

# Audio Quality / Noise Reduction Defaults
NOISE_REDUCTION_ENABLED = False
NOISE_SENSITIVITY = 2.0
CALIBRATION_DURATION = 3.0
AUTO_CALIBRATE = False

# STARTING_COLORS = [0xff0000, 0x00ff00, 0x0000ff]
STARTING_COLORS = [0xFF0000, 0xFF0000, 0xFF0000]

# Load environment variables from .env file, if available
load_dotenv()


@click.command()
@click.argument("query", required=False, default=None, nargs=1)
@click.option(
    "--prompt-file",
    default=PROMPT_FILE,
    help=f'The file to use as the prompt when generating stories. Defaults to "%s".' % PROMPT_FILE,
)
@click.option(
    "--sample-rate",
    default=SAMPLE_RATE,
    help=f"The sample rate to use when generating stories. Defaults to %s." % SAMPLE_RATE,
)
@click.option(
    "--queries-path",
    default=QUERIES_PATH,
    help=f'The directory to store the recorded voice queries in. Defaults to "%s".' % QUERIES_PATH,
)
@click.option(
    "--stories-path",
    default=STORIES_PATH,
    help=f'The directory to store the generated stories in. Defaults to "%s".' % STORIES_PATH,
)
@click.option(
    "--models-path",
    default=MODELS_PATH,
    help=f'The directory to store the downloaded models running locally. Defaults to "%s".' % MODELS_PATH,
)
@click.option(
    "--sound-model",
    default=SOUND_MODEL,
    help=f'The model to use to discriminate speech in voice queries. Defaults to "%s".' % SOUND_MODEL,
)
@click.option(
    "--llm-url",
    default=LLM_URL,
    help=f'The URL of the cloud endpoint for the LLM model. Defaults to "%s".' % LLM_URL,
)
@click.option(
    "--llm-model",
    default=LLM_MODEL,
    help=f'The LLM model to use when generating stories. Defaults to "%s".' % LLM_MODEL,
)
@click.option(
    "--llm-provider",
    type=click.Choice(["gemini", "deepseek", "ollama"], case_sensitive=False),
    default="gemini",
    help='The LLM provider to use. Defaults to "gemini".',
)
@click.option(
    "--gemini-api-key",
    help="Google Gemini API key. Can also be set via GEMINI_API_KEY environment variable.",
)
@click.option(
    "--deepseek-api-key", 
    help="Deepseek API key. Can also be set via DEEPSEEK_API_KEY environment variable.",
)
@click.option(
    "--google-cloud-api-key",
    help="Google Cloud API key. Can also be set via GOOGLE_CLOUD_API_KEY environment variable.",
)
@click.option(
    "--google-project-id",
    help="Google Cloud project ID. Can also be set via GOOGLE_PROJECT_ID environment variable.",
)
@click.option(
    "--local-whisper-model",
    type=click.Choice(["tiny", "base", "small", "medium", "large"], case_sensitive=False),
    default="tiny",
    help="Local Whisper model size. Defaults to 'tiny'.",
)
@click.option(
    "--temperature",
    type=float,
    default=TEMPERATURE,
    help="The temperature to use when generating stories. Defaults to %s." % TEMPERATURE,
)
@click.option(
    "--max-tokens",
    type=int,
    default=MAX_TOKENS,
    help="The maximum number of tokens to use when generating stories. Defaults to %s." % MAX_TOKENS,
)
@click.option(
    "--tts-url",
    default=LLM_URL,
    help=f'The URL of the cloud endpoint for the TTS model. Defaults to "%s".' % TTS_URL,
)
@click.option(
    "--tts-model",
    default=TTS_MODEL,
    help=f'The TTS model to use when generating stories. Defaults to "%s".' % TTS_MODEL,
)
@click.option(
    "--tts-voice",
    default=TTS_VOICE,
    help=f'The TTS voice to use when generating stories. Defaults to "%s".' % TTS_VOICE,
)
@click.option(
    "--tts-format",
    default=TTS_FORMAT,
    help=f'The TTS format to use when generating stories. Defaults to "%s".' % TTS_FORMAT,
)
@click.option(
    "--tts-provider",
    type=click.Choice(["elevenlabs"], case_sensitive=False),
    default="elevenlabs",
    help=f'The TTS provider to use. Defaults to "elevenlabs".',
)
@click.option(
    "--elevenlabs-url",
    default=ELEVENLABS_URL,
    help=f'The URL of the ElevenLabs API endpoint. Defaults to "%s".' % ELEVENLABS_URL,
)
@click.option(
    "--list-voices",
    is_flag=True,
    default=False,
    help="List all available voices from configured providers and exit.",
)
@click.option(
    "--voice-cycle",
    is_flag=True,
    default=False,
    help="Enable voice cycling with hardware button (double-tap to cycle).",
)
@click.option(
    "--voice-preview",
    help="Generate a preview audio sample for the specified voice and exit.",
)
@click.option(
    "--query-guard",
    default=QUERY_GUARD,
    help=f'Optional text prefix for queries (legacy feature). Defaults to "%s" (empty = natural language).' % QUERY_GUARD,
)
@click.option(
    "--continuation-patterns",
    default=",".join(CONTINUATION_PATTERNS),
    help=f'Comma-separated list of patterns that indicate story continuation requests. Defaults to "%s".' % ",".join(CONTINUATION_PATTERNS),
)
@click.option(
    "--story-request",
    help="Request a specific story topic or theme (e.g., 'space adventure', 'princess and dragon').",
)
@click.option(
    "--gpio-button",
    is_flag=True,
    default=False,
    help="Enable GPIO button as alternative to wakeword (acts like voice activation).",
)
@click.option(
    "--wakeword-engine",
    type=click.Choice(["ppn", "onnx", "tflite"], case_sensitive=False),
    default=None,
    help="Wakeword engine to use (ppn=Picovoice recommended for Pi Zero 2W).",
)
@click.option(
    "--wakeword-model",
    help="Path to wakeword model file (.ppn, .onnx, or .tflite).",
)
@click.option(
    "--wakeword-sensitivity",
    type=float,
    default=0.5,
    help="Wakeword detection sensitivity (0.0-1.0). Higher = more sensitive.",
)
@click.option(
    "--continue-story",
    help="Continue a specific story by providing its directory name or topic keywords.",
)
@click.option("--debug", is_flag=True, default=False, help="Enables debug logging.")
@click.option(
    "--noise-reduction",
    is_flag=True,
    default=NOISE_REDUCTION_ENABLED,
    help="Enable noise reduction and audio filtering to reduce false triggers from ambient sounds.",
)
@click.option(
    "--noise-sensitivity",
    type=float,
    default=NOISE_SENSITIVITY,
    help=f"Noise gate sensitivity multiplier. Higher values are more sensitive to quiet sounds. Defaults to %s." % NOISE_SENSITIVITY,
)
@click.option(
    "--calibration-duration",
    type=float,
    default=CALIBRATION_DURATION,
    help=f"Duration in seconds to record ambient noise for calibration. Defaults to %s." % CALIBRATION_DURATION,
)
@click.option(
    "--auto-calibrate",
    is_flag=True,
    default=AUTO_CALIBRATE,
    help="Automatically calibrate noise floor on startup when using noise reduction.",
)
@click.option(
    "--ignore_cache",
    is_flag=True,
    default=False,
    help="Ignores the cache and always generates a new story.",
)
@click.option(
    "--sound-driver",
    type=click.Choice(["alsa", "sounddevice"], case_sensitive=False),
    default=SOUND_DRIVER,
    help="Which driver to use to emit sound.",
)
@click.option(
    "--trim-first-frame",
    is_flag=True,
    default=False,
    help="Trim the first frame of recorded audio data. Useful if the mic has a click or hiss at the beginning of each recording.",
)
@click.option(
    "--button-gpio-pin",
    type=int,
    default=BUTTON_GPIO_PIN,
    help=f"The GPIO pin to use for the button. Defaults to %s." % BUTTON_GPIO_PIN,
)
@click.option(
    "--hold-time",
    type=float,
    default=HOLD_TIME,
    help="The time to hold the button to erase all recorded sounds. Defaults to %s seconds." % HOLD_TIME,
)
@click.option("--loop", is_flag=True, default=False, help="Enables loop operation.")
@click.option("--web-app", is_flag=True, default=False, help="Launch the professional web interface for story management.")
@pass_context
def cli(
    ctx,
    query,
    prompt_file,
    sample_rate,
    queries_path,
    stories_path,
    models_path,
    sound_model,
    llm_url,
    llm_model,
    llm_provider,
    gemini_api_key,
    deepseek_api_key,
    google_cloud_api_key,
    google_project_id,
    local_whisper_model,
    temperature,
    max_tokens,
    tts_url,
    tts_model,
    tts_voice,
    tts_format,
    tts_provider,
    elevenlabs_url,
    list_voices,
    voice_cycle,
    voice_preview,
    query_guard,
    continuation_patterns,
    story_request,
    gpio_button,
    wakeword_engine,
    wakeword_model,
    wakeword_sensitivity,
    continue_story,
    debug,
    ignore_cache,
    sound_driver,
    trim_first_frame,
    noise_reduction,
    noise_sensitivity,
    calibration_duration,
    auto_calibrate,
    button_gpio_pin,
    hold_time,
    loop,
    web_app,
):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    ctx.sound_model = sound_model
    ctx.llm_url = llm_url
    ctx.llm_model = llm_model
    ctx.llm_provider = llm_provider
    ctx.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
    ctx.deepseek_api_key = deepseek_api_key or os.getenv("DEEPSEEK_API_KEY")
    ctx.google_cloud_api_key = google_cloud_api_key or os.getenv("GOOGLE_CLOUD_API_KEY")
    ctx.google_project_id = google_project_id or os.getenv("GOOGLE_PROJECT_ID")
    ctx.local_whisper_model = local_whisper_model
    ctx.tts_url = tts_url
    ctx.tts_model = tts_model
    ctx.temperature = temperature
    ctx.sample_rate = sample_rate
    ctx.max_tokens = max_tokens
    ctx.tts_voice = tts_voice
    ctx.tts_format = tts_format
    ctx.tts_provider = tts_provider
    ctx.elevenlabs_url = elevenlabs_url
    ctx.voice_cycle = voice_cycle
    ctx.language = LANGUAGE  # Sabit Türkçe
    ctx.query_guard = query_guard
    ctx.continuation_patterns = continuation_patterns.split(",") if continuation_patterns else CONTINUATION_PATTERNS
    ctx.story_request = story_request
    ctx.gpio_button = gpio_button
    ctx.wakeword_engine = wakeword_engine
    ctx.wakeword_model = wakeword_model
    ctx.wakeword_sensitivity = wakeword_sensitivity
    ctx.continue_story = continue_story
    ctx.ignore_cache = ignore_cache
    ctx.debug = debug
    ctx.loop = loop
    ctx.web_app = web_app
    ctx.sound_driver = sound_driver
    ctx.trim_first_frame = trim_first_frame
    ctx.noise_reduction = noise_reduction
    ctx.noise_sensitivity = noise_sensitivity
    ctx.calibration_duration = calibration_duration
    ctx.auto_calibrate = auto_calibrate
    ctx.button_gpio_pin = button_gpio_pin
    ctx.hold_time = hold_time

    ctx.prompt_file = utils.resolve(prompt_file)
    ctx.queries_path = utils.resolve(queries_path)
    ctx.stories_path = utils.resolve(stories_path)
    ctx.models_path = utils.resolve(models_path)

    ctx.leds = leds.LEDs(STARTING_COLORS)

    ctx.running = True
    ctx.talking = False

    # Initialize TTS service with available providers
    try:
        # Prepare arguments for initialize_tts_service, only pass if not None
        tts_args = {}
        if ctx.elevenlabs_url:
            tts_args['elevenlabs_url'] = ctx.elevenlabs_url
        if ctx.gemini_api_key:
            tts_args['gemini_key'] = ctx.gemini_api_key
        tts_args['gemini_url'] = GEMINI_URL
        initialize_tts_service(**tts_args)
        
        # Set the TTS service in context
        ctx.tts_service = tts_service
        
        # Set default provider if not specified or invalid
        available_providers = tts_service.get_available_providers()
        if ctx.tts_provider not in available_providers:
            if available_providers:
                ctx.tts_provider = available_providers[0]
                logging.info(f"TTS provider '{tts_provider}' not available, using {ctx.tts_provider}")
            else:
                logging.warning("No TTS providers available")
        
        # Set current voice in voice manager
        voice_manager.set_voice(ctx.tts_voice, ctx.tts_provider)
        
    except Exception as e:
        logging.warning(f"Failed to initialize enhanced TTS service: {str(e)}")
        ctx.tts_service = None
    
    # Handle special commands
    if list_voices:
        import asyncio
        asyncio.run(handle_list_voices())
        return
    
    if voice_preview:
        import asyncio
        asyncio.run(handle_voice_preview(voice_preview, ctx.tts_provider))
        return
    
    if web_app:
        import subprocess
        import sys
        
        # Use the new professional web interface
        web_interface_path = os.path.join(os.path.dirname(__file__), "..", "web_interface", "launch.py")
        
        if os.path.exists(web_interface_path):
            subprocess.run([sys.executable, web_interface_path])
        else:
            # Fallback to old enhanced app if exists
            enhanced_app_path = os.path.join(os.path.dirname(__file__), "..", "tools", "gradio_app", "enhanced_app.py")
            basic_app_path = os.path.join(os.path.dirname(__file__), "..", "tools", "gradio_app", "app.py")
            
            if os.path.exists(enhanced_app_path):
                subprocess.run([sys.executable, enhanced_app_path])
            elif os.path.exists(basic_app_path):
                subprocess.run([sys.executable, basic_app_path])
            else:
                print("Web arayuzu bulunamadi. Lutfen web_interface/ dizinini kontrol edin.")
        return

    # Alsa is only supported on Linux.
    if ctx.sound_driver == "alsa" and platform.system() != "Linux":
        ctx.sound_driver = "sounddevice"

    try:
        fably.main(ctx, query)
    finally:
        ctx.leds.stop()


async def handle_list_voices():
    """Handle the --list-voices command."""
    print("\n🎵 Available TTS Voices:\n")
    
    try:
        all_voices = await tts_service.get_all_voices()
        
        for provider_name, voices in all_voices.items():
            print(f"📢 {provider_name.upper()} Provider:")
            
            if not voices:
                print("  No voices available")
                continue
            
            for voice in voices:
                name = voice.get("name", voice["id"])
                description = voice.get("description", "")
                gender = voice.get("gender", "")
                
                # Format voice info
                info_parts = []
                if gender:
                    info_parts.append(f"Gender: {gender}")
                if description:
                    info_parts.append(f"Description: {description}")
                
                info_str = f" ({', '.join(info_parts)})" if info_parts else ""
                print(f"  • {voice['id']}: {name}{info_str}")
            
            print()
        
        # Show current voice setting
        current_voice, current_provider = voice_manager.get_current_voice()
        print(f"🎯 Current Voice: {current_voice} ({current_provider})")
        
    except Exception as e:
        print(f"❌ Error listing voices: {str(e)}")


async def handle_voice_preview(voice_id: str, provider: str = "elevenlabs"):
    """Handle the --voice-preview command."""
    print(f"\n🎧 Generating voice preview for: {voice_id}")
    
    try:
        preview_file = await voice_manager.preview_voice(voice_id, provider)
        print(f"✅ Preview generated: {preview_file}")
        print("🔊 Playing preview...")
        
        # Play the preview
        utils.play_audio_file(preview_file, "sounddevice")
        
    except Exception as e:
        print(f"❌ Error generating voice preview: {str(e)}")


def add_voice_cycling_to_button_handler(ctx):
    """Add voice cycling functionality to button handler."""
    if not ctx.voice_cycle:
        return
    
    # Store original button handlers
    original_pressed = getattr(ctx.button, 'when_pressed', None)
    original_released = getattr(ctx.button, 'when_released', None)
    
    # Track button press timing for double-tap detection
    ctx.last_press_time = 0
    ctx.press_count = 0
    
    def enhanced_pressed():
        import time
        current_time = time.time()
        
        # Check for double-tap (within 0.5 seconds)
        if current_time - ctx.last_press_time < 0.5:
            ctx.press_count += 1
        else:
            ctx.press_count = 1
        
        ctx.last_press_time = current_time
        
        # Call original handler
        if original_pressed:
            original_pressed()
    
    def enhanced_released():
        import time
        import asyncio
        
        # Check if this is a double-tap after a short delay
        def check_double_tap():
            time.sleep(0.6)  # Wait for potential second tap
            
            if ctx.press_count >= 2:
                # Double tap detected - cycle voice
                logging.info("Double-tap detected - cycling voice")
                
                try:
                    # Run voice cycling in new event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    new_voice, new_provider = loop.run_until_complete(
                        voice_manager.cycle_voice(1)
                    )
                    
                    # Update context
                    ctx.tts_voice = new_voice
                    ctx.tts_provider = new_provider
                    
                    # Announce new voice
                    announcement_text = f"Voice changed to {new_voice}"
                    
                    # Generate and play announcement
                    announcement_file = utils.resolve("temp_voice_announcement.mp3")
                    loop.run_until_complete(
                        tts_service.synthesize(
                            text=announcement_text,
                            voice=new_voice,
                            provider=new_provider,
                            output_file=announcement_file
                        )
                    )
                    
                    utils.play_audio_file(announcement_file, ctx.sound_driver)
                    
                    # Clean up
                    if announcement_file.exists():
                        announcement_file.unlink()
                    
                    loop.close()
                    
                except Exception as e:
                    logging.error(f"Voice cycling failed: {str(e)}")
                
                ctx.press_count = 0
        
        # Start double-tap check in background thread
        import threading
        threading.Thread(target=check_double_tap, daemon=True).start()
        
        # Call original handler
        if original_released:
            original_released()
    
    # Set enhanced handlers
    ctx.button.when_pressed = enhanced_pressed
    ctx.button.when_released = enhanced_released


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit("\nInterrupted by user")
