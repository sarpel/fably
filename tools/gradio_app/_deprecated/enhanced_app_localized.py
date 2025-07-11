"""
Enhanced Fably Web Interface with Turkish Localization
Comprehensive Story Management System with Turkish as default language
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import gradio as gr
import openai
import soundfile as sf
import yaml

from fably import fably, utils
from fably_localization import get_text, get_available_languages, DEFAULT_LANGUAGE

# Set Turkish as default language
DEFAULT_LANGUAGE = "tr"


# Default configuration - can be overridden via environment variables
DEFAULT_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
    "elevenlabs_api_key": os.getenv("ELEVENLABS_API_KEY", ""),
    "stt_url": "https://api.openai.com/v1",
    "stt_model": "whisper-1", 
    "llm_url": "https://generativelanguage.googleapis.com/v1beta",
    "llm_model": "gemini-2.5-flash",
    "default_llm_provider": "gemini",
    "tts_url": "https://api.openai.com/v1",
    "tts_model": "tts-1",
    "tts_voice": "xsGHrtxT5AdDzYXTQT0d",
    "tts_provider": "elevenlabs",
    "tts_format": "mp3",
    "elevenlabs_url": "https://api.elevenlabs.io",
    "gemini_url": "https://generativelanguage.googleapis.com/v1beta",
    "language": "tr",  # Turkish as default
    "temperature": 1.2,
    "max_tokens": 4000,
    "stories_path": "./stories",
    "examples_path": "./fably/examples",
    "prompt_file": "./fably/prompt.txt",
    "query_guard": "",  # No query guard - users can speak naturally
    # Audio Quality Settings
    "noise_reduction": False,
    "noise_sensitivity": 2.0,
    "auto_calibrate": False,
    "calibration_duration": 3.0,
    # Wakeword Detection Settings
    "wakeword_engine": None,  # none/ppn/onnx/tflite
    "wakeword_model": "",     # Path to model file
    "wakeword_sensitivity": 0.5,  # 0.0-1.0
    # GPIO Button Settings
    "gpio_button": False,     # Enable GPIO button
    "button_gpio_pin": 17,    # GPIO pin number
    "voice_cycle": False,     # Enable voice cycling
    "hold_time": 3.0          # Long press duration
}

# Available voices from both providers  
OPENAI_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer", "ash", "sage", "coral"]
ELEVENLABS_VOICES = []  # Will be populated dynamically

# TTS Providers (Updated with Gemini support)
TTS_PROVIDERS = ["openai", "elevenlabs", "gemini"]


class EnhancedFablyContext:
    """Enhanced context for the Gradio application with story management capabilities."""
    
    def __init__(self, config: Dict = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        
        # Add all required attributes from CLI context
        self.api_key = self.config["api_key"]
        self.elevenlabs_api_key = self.config.get("elevenlabs_api_key", "")
        self.stt_url = self.config["stt_url"]
        self.stt_model = self.config["stt_model"]
        self.llm_url = self.config["llm_url"]
        self.llm_model = self.config["llm_model"]
        self.temperature = self.config["temperature"]
        self.max_tokens = self.config["max_tokens"]
        self.tts_url = self.config["tts_url"]
        self.tts_model = self.config["tts_model"]
        self.tts_voice = self.config["tts_voice"]
        self.tts_format = self.config["tts_format"]
        self.tts_provider = self.config["tts_provider"]
        self.elevenlabs_url = self.config["elevenlabs_url"]
        self.language = self.config["language"]
        self.sound_driver = "alsa"  # Default sound driver
        
        self._init_clients()
        self._init_paths()
    
    def _init_clients(self):
        """Initialize OpenAI clients and TTS service for different services."""
        self.stt_client = openai.Client(
            base_url=self.config["stt_url"], 
            api_key=self.config["api_key"]
        )
        self.llm_client = openai.AsyncClient(
            base_url=self.config["llm_url"], 
            api_key=self.config["api_key"]
        )
        self.tts_client = openai.AsyncClient(
            base_url=self.config["tts_url"], 
            api_key=self.config["api_key"]
        )
        
        # Initialize enhanced TTS service
        try:
            from fably.tts_service import initialize_tts_service, tts_service
            initialize_tts_service(
                openai_key=self.config["api_key"],
                elevenlabs_key=self.config.get("elevenlabs_api_key"),
                gemini_key=self.config.get("gemini_api_key"),
                openai_url=self.config["tts_url"],
                elevenlabs_url=self.config["elevenlabs_url"],
                gemini_url=self.config.get("gemini_url", "https://generativelanguage.googleapis.com/v1beta")
            )
            self.tts_service = tts_service
            
            # Initialize voice manager
            from fably.voice_manager import voice_manager
            voice_manager.set_voice(
                self.config["tts_voice"], 
                self.config["tts_provider"]
            )
            
        except Exception as e:
            print(f"Warning: Enhanced TTS service not available: {str(e)}")
            self.tts_service = None
    
    def _init_paths(self):
        """Initialize and resolve story paths."""
        self.stories_path = utils.resolve(self.config["stories_path"])
        self.examples_path = utils.resolve(self.config["examples_path"])
        self.prompt_file = utils.resolve(self.config["prompt_file"])
    
    def persist_runtime_params(self, output_file, **kwargs):
        """
        Writes information about the models used to generate the story to a file.
        Compatible with the CLI context's persist_runtime_params method.
        """
        info = {
            "language": self.language,
            "stt_url": self.stt_url,
            "stt_model": self.stt_model,
            "llm_url": self.llm_url,
            "llm_model": self.llm_model,
            "llm_temperature": self.temperature,
            "llm_max_tokens": self.max_tokens,
            "tts_url": self.tts_url,
            "tts_model": self.tts_model,
            "tts_voice": self.tts_voice,
        }
        for key, value in kwargs.items():
            info[key] = value
        utils.write_to_yaml(output_file, info)


# Global context instance
ctx = EnhancedFablyContext()
current_language = "tr"  # Default to Turkish


def set_language(lang):
    """Set the current interface language"""
    global current_language
    current_language = lang
    return lang


def _(key):
    """Shorthand function for getting translated text"""
    return get_text(key, current_language)


def get_story_list() -> List[Tuple[str, str]]:
    """
    Get list of available stories from both stories and examples directories.
    Returns list of (display_name, story_path) tuples.
    """
    stories = []
    
    # Check main stories directory
    if ctx.stories_path.exists():
        for story_dir in ctx.stories_path.iterdir():
            if story_dir.is_dir() and (story_dir / "info.yaml").exists():
                stories.append((f"📖 {story_dir.name}", str(story_dir)))
    
    # Check examples directories  
    if ctx.examples_path.exists():
        for provider_dir in ctx.examples_path.iterdir():
            if provider_dir.is_dir():
                for story_dir in provider_dir.iterdir():
                    if story_dir.is_dir() and (story_dir / "info.yaml").exists():
                        display_name = f"📚 {provider_dir.name}/{story_dir.name}"
                        stories.append((display_name, str(story_dir)))
    
    return sorted(stories)


def load_story_info(story_path: str) -> Tuple[Dict, List[str]]:
    """
    Load story information and paragraph texts.
    Returns (info_dict, paragraph_texts).
    """
    story_dir = Path(story_path)
    
    # Load story metadata
    info_file = story_dir / "info.yaml"
    with open(info_file, "r", encoding="utf-8") as f:
        info = yaml.safe_load(f)
    
    # Load paragraph texts
    paragraphs = []
    paragraph_files = sorted(story_dir.glob("paragraph_*.txt"))
    
    for paragraph_file in paragraph_files:
        text = utils.read_from_file(paragraph_file)
        paragraphs.append(text.strip())
    
    return info, paragraphs


def save_story_paragraph(story_path: str, paragraph_index: int, text: str) -> str:
    """Save updated paragraph text to file."""
    story_dir = Path(story_path)
    paragraph_file = story_dir / f"paragraph_{paragraph_index}.txt"
    
    try:
        utils.write_to_file(paragraph_file, text.strip())
        return f"✅ {_('paragraph_saved')} {paragraph_index}"
    except Exception as e:
        return f"❌ {_('error_saving_paragraph')} {paragraph_index}: {str(e)}"


async def regenerate_paragraph_audio(story_path: str, paragraph_index: int, 
                                   voice: str, text: str) -> str:
    """Regenerate audio for a specific paragraph."""
    story_dir = Path(story_path)
    
    try:
        # Update TTS voice in context
        ctx.config["tts_voice"] = voice
        
        # Generate new audio
        audio_file = await fably.synthesize_audio(
            ctx, story_dir, paragraph_index, text
        )
        
        return f"✅ {_('audio_regenerated')} {paragraph_index} '{voice}'"
    except Exception as e:
        return f"❌ {_('error_regenerating_audio')}: {str(e)}"


def transcribe_audio(audio_file: str) -> str:
    """Transcribe audio file using the configured STT service."""
    if not audio_file:
        return _('no_audio_provided')
    
    try:
        with open(audio_file, "rb") as f:
            response = ctx.stt_client.audio.transcriptions.create(
                model=ctx.config["stt_model"],
                language=ctx.config["language"],
                file=f
            )
        return response.text
    except Exception as e:
        return f"{_('error_transcribing')}: {str(e)}"


async def generate_story_content(query: str, prompt: str, temperature: float, 
                               max_tokens: int) -> str:
    """Generate story content using the configured LLM."""
    # No query guard validation - users can ask for stories naturally
    
    try:
        # Update context parameters
        ctx.config["temperature"] = temperature
        ctx.config["max_tokens"] = max_tokens
        
        # Generate story using Fably's existing function
        story_stream = await fably.generate_story(ctx, query, prompt)
        
        chunks = []
        async for chunk in story_stream:
            fragment = chunk.choices[0].delta.content
            if fragment is None:
                break
            chunks.append(fragment)
        
        return "".join(chunks)
    except Exception as e:
        return f"{_('error_generating_story')}: {str(e)}"


async def get_available_voices() -> List[Tuple[str, str]]:
    """Get all available voices from configured providers."""
    voice_options = []
    
    try:
        if ctx.tts_service:
            all_voices = await ctx.tts_service.get_all_voices()
            
            for provider_name, voices in all_voices.items():
                for voice in voices:
                    voice_label = f"{voice['name']} ({provider_name})"
                    voice_value = f"{provider_name}:{voice['id']}"
                    voice_options.append((voice_label, voice_value))
        else:
            # Fallback to OpenAI voices only
            for voice in OPENAI_VOICES:
                voice_options.append((f"{voice.capitalize()} (OpenAI)", f"openai:{voice}"))
                
    except Exception as e:
        print(f"Error getting voices: {str(e)}")
        # Fallback to OpenAI voices
        for voice in OPENAI_VOICES:
            voice_options.append((f"{voice.capitalize()} (OpenAI)", f"openai:{voice}"))
    
    return voice_options


async def synthesize_with_provider(text: str, voice_spec: str) -> Tuple[int, any]:
    """Synthesize audio using the enhanced TTS service."""
    if not text.strip():
        return None
    
    if not voice_spec:
        voice_spec = f"{ctx.config['tts_provider']}:{ctx.config['tts_voice']}"
    
    try:
        # Parse voice specification (provider:voice_id)
        if ":" in voice_spec:
            provider, voice_id = voice_spec.split(":", 1)
        else:
            # If no provider specified, assume OpenAI
            provider = "openai"
            voice_id = voice_spec
        
        print(f"Debug: Synthesizing with provider='{provider}', voice_id='{voice_id}'")
        
        if ctx.tts_service:
            # Use enhanced TTS service
            audio_data = await ctx.tts_service.synthesize(
                text=text,
                voice=voice_id,
                provider=provider,
                format="wav"
            )
            
            # Write to temporary file and read back for Gradio
            temp_file = "temp_synthesis.wav"
            with open(temp_file, "wb") as f:
                f.write(audio_data)
            
            data, samplerate = sf.read(temp_file)
            
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return samplerate, data
        else:
            # Fallback to OpenAI client
            response = await ctx.tts_client.audio.speech.create(
                input=text,
                model=ctx.config["tts_model"],
                voice=voice_id,
                response_format="wav"
            )
            
            temp_file = "temp_synthesis.wav"
            response.write_to_file(temp_file)
            data, samplerate = sf.read(temp_file)
            
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return samplerate, data
            
    except Exception as e:
        print(f"{_('error_speech_synthesis')}: {str(e)}")
        return None

# Story Library Tab Functions
def on_story_select(selected_story: str) -> Tuple[str, str, List[gr.Textbox]]:
    """Handle story selection and load story details."""
    if not selected_story:
        return _('no_story_selected'), "", []
    
    try:
        # Extract story path from dropdown value
        story_path = selected_story.split(" | ")[1] if " | " in selected_story else ""
        if not story_path:
            return _('invalid_story_selection'), "", []
        
        info, paragraphs = load_story_info(story_path)
        
        # Format story info for display
        info_text = f"""
**Query:** {info.get('query', 'N/A')}
**{_('language')}:** {info.get('language', 'N/A')}
**LLM Model:** {info.get('llm_model', 'N/A')}
**TTS Voice:** {info.get('tts_voice', 'N/A')}
**Temperature:** {info.get('llm_temperature', 'N/A')}
**{_('paragraphs')}:** {len(paragraphs)}
        """.strip()
        
        # Create paragraph textboxes
        paragraph_boxes = []
        for i, paragraph in enumerate(paragraphs):
            paragraph_boxes.append(
                gr.Textbox(
                    value=paragraph,
                    label=f"Paragraph {i}",
                    lines=3,
                    interactive=True
                )
            )
        
        return story_path, info_text, paragraph_boxes
    
    except Exception as e:
        return _('error_loading_story'), f"Error: {str(e)}", []


# Global Functions (needed by multiple tabs)

def refresh_voices():
    """Refresh the voice dropdown options."""
    import asyncio
    voice_options = asyncio.run(get_available_voices())
    return gr.Dropdown(choices=voice_options)


def initialize_voice_dropdowns():
    """Initialize voice dropdowns with available voices."""
    import asyncio
    voice_options = asyncio.run(get_available_voices())
    return voice_options


def create_gradio_interface():
    """Create the main Gradio interface with multiple tabs and Turkish localization."""
    
    # Load default prompt
    try:
        default_prompt = utils.read_from_file(ctx.prompt_file)
    except:
        default_prompt = "You are a storyteller who tells imaginative stories to children."
    
    with gr.Blocks(title=_('title'), theme=gr.themes.Soft()) as app:
        
        # Language selector at the top
        with gr.Row():
            with gr.Column(scale=5):
                gr.Markdown(f"# {_('title')}")
                gr.Markdown(f"*{_('subtitle')}*")
            with gr.Column(scale=2):
                language_selector = gr.Dropdown(
                    choices=get_available_languages(),
                    value=current_language,
                    label=_('language_selector') if current_language in get_available_languages() else "🌍 Dil Seçimi",
                    interactive=True
                )
        
        with gr.Tabs():
            
            # Story Library Tab
            with gr.Tab(_('tab_story_library')):
                gr.Markdown(f"### {_('library_header')}")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        story_dropdown = gr.Dropdown(
                            choices=[f"{name} | {path}" for name, path in get_story_list()],
                            label=_('select_story'),
                            interactive=True
                        )
                        refresh_button = gr.Button(_('refresh_list'))
                        
                        story_info_display = gr.Markdown(_('story_details'))
                    
                    with gr.Column(scale=2):
                        selected_story_path = gr.Textbox(
                            label="Selected Story Path", 
                            visible=False
                        )
                        
                        # Dynamic paragraph editing area
                        paragraph_editor = gr.Column(visible=False)
                        
                        with paragraph_editor:
                            gr.Markdown(f"### {_('edit_paragraphs')}")
                            
                            # These will be populated dynamically
                            paragraph_textboxes = []
                            for i in range(20):  # Support up to 20 paragraphs
                                textbox = gr.Textbox(
                                    label=f"Paragraph {i}",
                                    lines=3,
                                    visible=False,
                                    interactive=True
                                )
                                paragraph_textboxes.append(textbox)
                            
                            with gr.Row():
                                voice_select = gr.Dropdown(
                                    choices=[],  # Will be populated dynamically
                                    value=None,  # Will be set during initialization  
                                    label=_('tts_voice'),
                                    interactive=True,
                                    allow_custom_value=True
                                )
                                refresh_voices_btn = gr.Button(_('refresh_voices'))
                            
                            with gr.Row():
                                save_all_button = gr.Button(_('save_all_changes'), variant="primary")
                                regenerate_all_button = gr.Button(_('regenerate_all_audio'))
                                continue_story_button = gr.Button(_('continue_story'), variant="secondary")
                            
                            # Story continuation section
                            with gr.Accordion(_('story_continuation'), open=False):
                                gr.Markdown(_('continuation_desc'))
                                continuation_prompt = gr.Textbox(
                                    label=_('continuation_request'),
                                    placeholder=_('continuation_placeholder'),
                                    lines=2
                                )
                                with gr.Row():
                                    continue_paragraphs = gr.Slider(
                                        minimum=1,
                                        maximum=10,
                                        value=3,
                                        step=1,
                                        label=_('new_paragraphs')
                                    )
                                    continuation_voice = gr.Dropdown(
                                        choices=[],  # Will be populated dynamically
                                        value=None,  # Will be set during initialization
                                        label=_('voice_for_new'),
                                        interactive=True,
                                        allow_custom_value=True
                                    )
                                generate_continuation_btn = gr.Button(_('generate_continuation'), variant="primary")
                            
                            operation_status = gr.Textbox(
                                label=_('status'),
                                interactive=False,
                                lines=2
                            )
                
                # Event handlers for Story Library
                def refresh_story_list():
                    return gr.Dropdown(
                        choices=[f"{name} | {path}" for name, path in get_story_list()]
                    )
                
                refresh_voices_btn.click(
                    fn=refresh_voices,
                    outputs=[voice_select]
                )
                
                refresh_button.click(
                    fn=refresh_story_list,
                    outputs=[story_dropdown]
                )
                
                def load_selected_story(selected_story):
                    if not selected_story:
                        return (
                            "",
                            _('story_details'),
                            gr.Column(visible=False),
                            *[gr.Textbox(visible=False) for _ in range(20)]
                        )
                    
                    try:
                        story_path = selected_story.split(" | ")[1]
                        info, paragraphs = load_story_info(story_path)
                        
                        info_text = f"""
**Query:** {info.get('query', 'N/A')}  
**{_('language')}:** {info.get('language', 'N/A')}  
**LLM Model:** {info.get('llm_model', 'N/A')}  
**TTS Voice:** {info.get('tts_voice', 'N/A')}  
**Temperature:** {info.get('llm_temperature', 'N/A')}  
**{_('paragraphs')}:** {len(paragraphs)}
                        """
                        
                        # Prepare paragraph textbox updates
                        textbox_updates = []
                        for i in range(20):
                            if i < len(paragraphs):
                                textbox_updates.append(
                                    gr.Textbox(
                                        value=paragraphs[i], 
                                        visible=True,
                                        label=f"Paragraph {i}"
                                    )
                                )
                            else:
                                textbox_updates.append(gr.Textbox(visible=False))
                        
                        return (
                            story_path,
                            info_text,
                            gr.Column(visible=True),
                            *textbox_updates
                        )
                    
                    except Exception as e:
                        return (
                            "",
                            f"**{_('error_loading_story')}:** {str(e)}",
                            gr.Column(visible=False),
                            *[gr.Textbox(visible=False) for _ in range(20)]
                        )
                
                story_dropdown.change(
                    fn=load_selected_story,
                    inputs=[story_dropdown],
                    outputs=[
                        selected_story_path,
                        story_info_display, 
                        paragraph_editor,
                        *paragraph_textboxes
                    ]
                )
                
                # Save all paragraphs handler
                def save_all_paragraphs(story_path, *paragraph_texts):
                    return batch_save_paragraphs(story_path, list(paragraph_texts))
                
                save_all_button.click(
                    fn=save_all_paragraphs,
                    inputs=[selected_story_path, *paragraph_textboxes],
                    outputs=[operation_status]
                )
                
                # Regenerate all audio handler
                def regenerate_all_audio_sync(story_path, voice, *paragraph_texts):
                    return asyncio.run(batch_regenerate_audio(story_path, voice, list(paragraph_texts)))
                
                # Story continuation handler
                def continue_story_sync(story_path, continuation_request, num_paragraphs, voice):
                    """Continue an existing story with new paragraphs."""
                    return asyncio.run(generate_story_continuation(
                        story_path, continuation_request, num_paragraphs, voice
                    ))
                
                regenerate_all_button.click(
                    fn=regenerate_all_audio_sync,
                    inputs=[selected_story_path, voice_select, *paragraph_textboxes],
                    outputs=[operation_status]
                )
                
                generate_continuation_btn.click(
                    fn=continue_story_sync,
                    inputs=[selected_story_path, continuation_prompt, continue_paragraphs, continuation_voice],
                    outputs=[operation_status]
                )
            
            # New Story Tab (Enhanced version of original functionality)
            with gr.Tab(_('tab_create_story')):
                gr.Markdown(f"### {_('create_header')}")
                
                with gr.Row():
                    with gr.Column():
                        voice_query = gr.Audio(
                            label=_('voice_query'),
                            sources=["microphone"],
                            type="filepath",
                            waveform_options=gr.WaveformOptions(
                                waveform_color="#01C6FF",
                                waveform_progress_color="#0066B4",
                                skip_length=2,
                                show_controls=False,
                            ),
                        )
                        
                        transcribe_button = gr.Button(_('transcribe_voice'))
                        
                        transcribed_query = gr.Textbox(
                            label=_('transcribed_query'),
                            placeholder=_('query_placeholder'),
                            lines=2,
                        )
                        
                        with gr.Row():
                            temperature_slider = gr.Slider(
                                0, 2.0, 
                                value=ctx.config["temperature"], 
                                label=_('creativity_temp')
                            )
                            max_tokens_slider = gr.Slider(
                                100, 4000, 
                                value=ctx.config["max_tokens"], 
                                label=_('max_length')
                            )
                    
                    with gr.Column():
                        prompt_input = gr.Textbox(
                            lines=6,
                            label=_('story_prompt'),
                            value=default_prompt,
                        )
                        
                        new_story_voice = gr.Dropdown(
                            choices=[],  # Will be populated dynamically
                            value=None,  # Will be set during initialization
                            label=_('tts_voice'),
                            interactive=True,
                            allow_custom_value=True
                        )
                        
                        refresh_new_story_voices_btn = gr.Button(_('refresh_voices'), size="sm")
                
                generate_story_button = gr.Button(_('generate_story'), variant="primary")
                
                story_output = gr.Textbox(
                    lines=20,
                    label=_('generated_story'),
                    placeholder=_('story_placeholder')
                )
                
                with gr.Row():
                    read_story_button = gr.Button(_('convert_to_audio'))
                    save_story_button = gr.Button(_('save_story'))
                
                story_audio = gr.Audio(
                    label=_('story_audio'),
                    interactive=False,
                )
                
                new_story_status = gr.Textbox(
                    label=_('status'),
                    interactive=False,
                    lines=2
                )
                
                # Event handlers for New Story tab
                transcribe_button.click(
                    fn=transcribe_audio,
                    inputs=[voice_query],
                    outputs=[transcribed_query],
                )
                
                # Async wrapper for story generation
                def generate_story_sync(query, prompt, temperature, max_tokens):
                    """Wrapper for async story generation with error handling."""
                    if not query or not query.strip():
                        return _('please_provide_request')
                    try:
                        return asyncio.run(generate_story_content(query, prompt, temperature, max_tokens))
                    except Exception as e:
                        return f"❌ {_('error_generating_story')}: {str(e)}"
                
                generate_story_button.click(
                    fn=generate_story_sync,
                    inputs=[transcribed_query, prompt_input, temperature_slider, max_tokens_slider],
                    outputs=[story_output],
                )
                
                # Async wrapper for TTS
                def read_story_sync(text, voice_spec):
                    """Wrapper for async TTS with error handling."""
                    if not text or not text.strip():
                        return None
                    if not voice_spec:
                        voice_spec = f"{ctx.config['tts_provider']}:{ctx.config['tts_voice']}"
                    try:
                        return asyncio.run(synthesize_with_provider(text, voice_spec))
                    except Exception as e:
                        print(f"Error in TTS: {str(e)}")
                        return None
                
                read_story_button.click(
                    fn=read_story_sync,
                    inputs=[story_output, new_story_voice],
                    outputs=[story_audio],
                )
                
                save_story_button.click(
                    fn=lambda query, story, voice: save_story_to_disk(query, story, voice),
                    inputs=[transcribed_query, story_output, new_story_voice],
                    outputs=[new_story_status]
                )
                
                refresh_new_story_voices_btn.click(
                    fn=refresh_voices,
                    outputs=[new_story_voice]
                )
            
            # Settings Tab with Turkish localization
            with gr.Tab(_('tab_settings')):
                gr.Markdown(f"### {_('settings_header')}")
                gr.Markdown(f"*{_('settings_desc')}*")
                
                with gr.Tabs():
                    
                    # OpenAI Provider Tab
                    with gr.Tab("🤖 OpenAI"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown(f"#### {_('openai_config')}")
                                
                                openai_api_key = gr.Textbox(
                                    label=_('openai_api_key'),
                                    value=ctx.config["api_key"],
                                    type="password",
                                    placeholder="sk-proj-...",
                                    info=_('api_key_required'),
                                    interactive=True
                                )
                                
                                openai_base_url = gr.Textbox(
                                    label=_('openai_base_url'),
                                    value=ctx.config["llm_url"],
                                    placeholder="https://api.openai.com/v1",
                                    info=_('custom_endpoint_info'),
                                    interactive=True
                                )
                            
                            with gr.Column():
                                gr.Markdown(f"#### {_('openai_models')}")
                                
                                openai_llm_model = gr.Dropdown(
                                    choices=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                                    value=ctx.config["llm_model"],
                                    label=_('language_model'),
                                    allow_custom_value=True,
                                    info=_('story_generation_model'),
                                    interactive=True
                                )
                                
                                openai_stt_model = gr.Dropdown(
                                    choices=["whisper-1"],
                                    value=ctx.config["stt_model"],
                                    label=_('stt_model'),
                                    allow_custom_value=True,
                                    interactive=True
                                )
                                
                                openai_tts_model = gr.Dropdown(
                                    choices=["tts-1", "tts-1-hd"],
                                    value=ctx.config["tts_model"],
                                    label=_('tts_model'),
                                    allow_custom_value=True,
                                    info=_('higher_quality_tts'),
                                    interactive=True
                                )
                                
                                openai_voice_select = gr.Dropdown(
                                    choices=[(voice.capitalize(), voice) for voice in OPENAI_VOICES],
                                    value=ctx.config["tts_voice"] if ctx.config["tts_provider"] == "openai" else "nova",
                                    label=_('default_voice'),
                                    info=_('voice_for_tts'),
                                    interactive=True
                                )
                    
                    # ElevenLabs Provider Tab
                    with gr.Tab("🎵 ElevenLabs"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown(f"#### {_('elevenlabs_config')}")
                                
                                elevenlabs_api_key = gr.Textbox(
                                    label=_('elevenlabs_api_key'),
                                    value=ctx.config.get("elevenlabs_api_key", ""),
                                    type="password",
                                    placeholder="your-elevenlabs-api-key",
                                    info=_('elevenlabs_required'),
                                    interactive=True
                                )
                                
                                elevenlabs_base_url = gr.Textbox(
                                    label=_('elevenlabs_base_url'),
                                    value=ctx.config["elevenlabs_url"],
                                    placeholder="https://api.elevenlabs.io",
                                    interactive=True
                                )
                            
                            with gr.Column():
                                gr.Markdown(f"#### {_('elevenlabs_settings')}")
                                
                                elevenlabs_model = gr.Dropdown(
                                    choices=[
                                        "eleven_v3",
                                        "eleven_multilingual_v2", 
                                        "eleven_flash_v2_5",
                                        "eleven_turbo_v2_5",
                                        "eleven_multilingual_v1",
                                        "eleven_monolingual_v1"
                                    ],
                                    value="eleven_multilingual_v2",
                                    label=_('elevenlabs_model'),
                                    allow_custom_value=True,
                                    info=_('v2_recommended'),
                                    interactive=True
                                )
                                
                                elevenlabs_voice_select = gr.Dropdown(
                                    choices=[],  # Will be populated dynamically
                                    label=_('default_elevenlabs_voice'),
                                    info=_('account_voices'),
                                    allow_custom_value=True,
                                    interactive=True
                                )
                                
                                load_elevenlabs_voices_btn = gr.Button(_('load_voices'))
                                
                                with gr.Accordion(_('voice_quality_settings'), open=False):
                                    stability_slider = gr.Slider(
                                        minimum=0.0, maximum=1.0, value=0.5, step=0.1,
                                        label=_('stability'), info=_('stability_info')
                                    )
                                    similarity_slider = gr.Slider(
                                        minimum=0.0, maximum=1.0, value=0.75, step=0.05,
                                        label=_('similarity_boost'), info=_('similarity_info')
                                    )
                    
                    # Gemini Provider Tab
                    with gr.Tab("💎 Google Gemini"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown(f"#### {_('gemini_config')}")
                                
                                gemini_api_key = gr.Textbox(
                                    label=_('gemini_api_key'),
                                    value=ctx.config.get("gemini_api_key", ""),
                                    type="password",
                                    placeholder="AIza...",
                                    info=_('get_from_studio'),
                                    interactive=True
                                )
                                
                                gemini_base_url = gr.Textbox(
                                    label=_('gemini_base_url'),
                                    value="https://generativelanguage.googleapis.com/v1beta",
                                    placeholder="https://generativelanguage.googleapis.com/v1beta",
                                    interactive=True
                                )
                            
                            with gr.Column():
                                gr.Markdown(f"#### {_('gemini_models')}")
                                
                                gemini_model = gr.Dropdown(
                                    choices=["gemini-2.5-pro", "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
                                    value="gemini-2.5-flash",
                                    label=_('gemini_llm_model'),
                                    allow_custom_value=True,
                                    info=_('llm_for_stories'),
                                    interactive=True
                                )
                                
                                gemini_tts_model = gr.Dropdown(
                                    choices=["gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"],
                                    value="gemini-2.5-flash-preview-tts",
                                    label=_('gemini_tts_model'),
                                    allow_custom_value=True,
                                    info=_('tts_model_info'),
                                    interactive=True
                                )
                                
                                gemini_voice_select = gr.Dropdown(
                                    choices=[
                                        (_('voice_default'), "default"),
                                        (_('voice_natural'), "natural"), 
                                        (_('voice_professional'), "professional"),
                                        (_('voice_expressive'), "expressive")
                                    ],
                                    value="default",
                                    label=_('default_gemini_voice'),
                                    info=_('voice_style_info'),
                                    interactive=True
                                )
                    
                    # Custom Provider Tab
                    with gr.Tab("🔧 " + _('custom_provider')):
                        gr.Markdown(f"#### {_('custom_provider')}")
                        gr.Markdown(f"*{_('custom_desc')}*")
                        
                        with gr.Row():
                            with gr.Column():
                                custom_provider_name = gr.Textbox(
                                    label=_('provider_name'),
                                    placeholder=_('provider_name_placeholder'),
                                    info=_('provider_friendly_name'),
                                    interactive=True
                                )
                                
                                custom_api_key = gr.Textbox(
                                    label=_('api_key'),
                                    type="password",
                                    placeholder=_('custom_api_key_placeholder'),
                                    interactive=True
                                )
                                
                                custom_base_url = gr.Textbox(
                                    label=_('base_url'),
                                    placeholder=_('base_url_placeholder'),
                                    info=_('full_endpoint_url'),
                                    interactive=True
                                )
                            
                            with gr.Column():
                                custom_llm_model = gr.Textbox(
                                    label=_('llm_model_id'),
                                    placeholder=_('llm_model_placeholder'),
                                    info=_('model_identifier'),
                                    interactive=True
                                )
                                
                                custom_stt_model = gr.Textbox(
                                    label=_('stt_model_optional'),
                                    placeholder="whisper-1",
                                    interactive=True
                                )
                                
                                custom_tts_model = gr.Textbox(
                                    label=_('tts_model_optional'),
                                    placeholder="tts-1",
                                    interactive=True
                                )
                                
                                test_custom_connection_btn = gr.Button(_('test_connection'))
                    
                    # Global Settings Tab
                    with gr.Tab(_('global_settings')):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown(f"#### {_('default_provider_selection')}")
                                
                                default_llm_provider = gr.Dropdown(
                                    choices=["openai", "gemini", "custom"],
                                    value="openai",
                                    label=_('default_llm_provider'),
                                    info=_('llm_provider_info'),
                                    interactive=True
                                )
                                
                                default_tts_provider = gr.Dropdown(
                                    choices=["openai", "elevenlabs", "gemini"],
                                    value=ctx.config["tts_provider"],
                                    label=_('default_tts_provider'),
                                    info=_('tts_provider_info'),
                                    interactive=True
                                )
                                
                                default_stt_provider = gr.Dropdown(
                                    choices=["openai", "custom"],
                                    value="openai",
                                    label=_('default_stt_provider'),
                                    info=_('stt_provider_info'),
                                    interactive=True
                                )
                            
                            with gr.Column():
                                gr.Markdown(f"#### {_('story_generation_defaults')}")
                                
                                default_temperature = gr.Slider(
                                    0, 2.0,
                                    value=1.2,
                                    label=_('default_temperature'),
                                    info=_('temperature_info'),
                                    interactive=True
                                )
                                
                                default_max_tokens = gr.Slider(
                                    100, 4000,
                                    value=4000,
                                    label=_('default_max_tokens'),
                                    info=_('max_tokens_info'),
                                    interactive=True
                                )
                                
                                language_input = gr.Textbox(
                                    label=_('language'),
                                    value="tr",
                                    placeholder=_('language_placeholder'),
                                    info=_('language_info'),
                                    interactive=True
                                )
                                
                                # Interface Language Selector in Global Settings
                                interface_language_selector = gr.Dropdown(
                                    choices=get_available_languages(),
                                    value=current_language,
                                    label=_('language_selector'),
                                    info="Arayüz dilini değiştir / Change interface language",
                                    interactive=True
                                )
                                
                                stories_path_input = gr.Textbox(
                                    label=_('stories_directory'),
                                    value=ctx.config["stories_path"],
                                    placeholder=_('stories_dir_placeholder'),
                                    info=_('stories_dir_info'),
                                    interactive=True
                                )
                
                # Audio Quality & Noise Reduction Settings
                with gr.Row():
                    with gr.Column():
                        gr.Markdown(f"#### {_('audio_quality_settings')}")
                        
                        noise_reduction_enabled = gr.Checkbox(
                            label=_('enable_noise_reduction'),
                            value=ctx.config.get("noise_reduction", False),
                            info=_('noise_reduction_info')
                        )
                        
                        noise_sensitivity = gr.Slider(
                            0.1, 10.0,
                            value=ctx.config.get("noise_sensitivity", 2.0),
                            step=0.1,
                            label=_('noise_sensitivity'),
                            info=_('noise_sensitivity_info')
                        )
                    
                    with gr.Column():
                        gr.Markdown(f"#### {_('audio_calibration')}")
                        
                        auto_calibrate = gr.Checkbox(
                            label=_('auto_calibrate'),
                            value=ctx.config.get("auto_calibrate", False),
                            info=_('auto_calibrate_info')
                        )
                        
                        calibration_duration = gr.Slider(
                            1.0, 10.0,
                            value=ctx.config.get("calibration_duration", 3.0),
                            step=0.5,
                            label=_('calibration_duration'),
                            info=_('calibration_duration_info')
                        )
                
                # Complete Settings Section with Save functionality
                with gr.Row():
                    save_settings_button = gr.Button(_('save_all_settings'), variant="primary", size="lg")
                    
                with gr.Row():    
                    settings_status = gr.Textbox(
                        label=_('settings_status'),
                        interactive=False,
                        lines=3
                    )
                
                # Settings event handlers
                def load_elevenlabs_voices(api_key):
                    """Load voices from ElevenLabs account."""
                    try:
                        if not api_key.strip():
                            return gr.Dropdown(choices=[]), f"❌ {_('api_key_missing')}"
                        
                        # Create temporary ElevenLabs provider to get voices
                        import asyncio
                        from fably.tts_service import ElevenLabsTTSProvider
                        
                        async def get_voices():
                            provider = ElevenLabsTTSProvider(api_key)
                            voices = await provider.get_available_voices()
                            return [(voice['name'], voice['id']) for voice in voices]
                        
                        voice_choices = asyncio.run(get_voices())
                        return gr.Dropdown(choices=voice_choices), f"✅ {len(voice_choices)} {_('voices_loaded')}"
                    except Exception as e:
                        return gr.Dropdown(choices=[]), f"❌ {_('error_loading_voices')}: {str(e)}"
                
                load_elevenlabs_voices_btn.click(
                    fn=load_elevenlabs_voices,
                    inputs=[elevenlabs_api_key],
                    outputs=[elevenlabs_voice_select, settings_status]
                )
                
                # Master save settings function
                def save_all_settings_master(
                    # OpenAI settings
                    openai_key, openai_url, openai_llm, openai_stt, openai_tts, openai_voice,
                    # ElevenLabs settings  
                    elevenlabs_key, elevenlabs_url, elevenlabs_model,
                    # Gemini settings
                    gemini_key, gemini_url, gemini_llm, gemini_tts, gemini_voice,
                    # Global settings
                    default_llm_prov, default_tts_prov, default_stt_prov,
                    default_temp, default_tokens, lang, interface_lang, stories_path,
                    # Audio settings
                    noise_reduction, noise_sens, auto_cal, cal_duration
                ):
                    """Save all settings across all provider tabs."""
                    try:
                        # Update context configuration
                        ctx.config.update({
                            # OpenAI
                            "api_key": openai_key,
                            "llm_url": openai_url,
                            "stt_url": openai_url,
                            "tts_url": openai_url,
                            "llm_model": openai_llm,
                            "stt_model": openai_stt,
                            "tts_model": openai_tts,
                            # ElevenLabs
                            "elevenlabs_api_key": elevenlabs_key,
                            "elevenlabs_url": elevenlabs_url,
                            "elevenlabs_model": elevenlabs_model,
                            # Gemini
                            "gemini_api_key": gemini_key,
                            "gemini_url": gemini_url,
                            "gemini_model": gemini_llm,
                            "gemini_tts_model": gemini_tts,
                            # Global settings
                            "default_llm_provider": default_llm_prov,
                            "tts_provider": default_tts_prov,
                            "default_stt_provider": default_stt_prov,
                            "temperature": default_temp,
                            "max_tokens": default_tokens,
                            "language": lang,
                            "stories_path": stories_path,
                            # Audio settings
                            "noise_reduction": noise_reduction,
                            "noise_sensitivity": noise_sens,
                            "auto_calibrate": auto_cal,
                            "calibration_duration": cal_duration
                        })
                        
                        # Set the appropriate voice based on provider
                        if default_tts_prov == "openai":
                            ctx.config["tts_voice"] = openai_voice
                        elif default_tts_prov == "gemini":
                            ctx.config["tts_voice"] = gemini_voice
                        
                        # Reinitialize services with new settings
                        ctx._init_clients()
                        ctx._init_paths()
                        
                        # Update TTS service with new keys
                        try:
                            from fably.tts_service import initialize_tts_service
                            initialize_tts_service(
                                openai_key=openai_key if openai_key else None,
                                elevenlabs_key=elevenlabs_key if elevenlabs_key else None,
                                gemini_key=gemini_key if gemini_key else None,
                                openai_url=openai_url,
                                elevenlabs_url=elevenlabs_url,
                                gemini_url=gemini_url
                            )
                        except Exception as e:
                            return f"⚠️  {_('all_settings_saved')} {_('error_saving_settings')}: {str(e)}"
                        
                        # Update interface language
                        global current_language
                        current_language = interface_lang
                        
                        return _('all_settings_saved')
                        
                    except Exception as e:
                        return f"❌ {_('error_saving_settings')}: {str(e)}"
                
                # Language change handler for Global Settings selector
                def change_interface_language(new_lang):
                    """Change the interface language from Global Settings"""
                    global current_language
                    current_language = new_lang
                    # Return a status message in the new language
                    if new_lang == 'tr':
                        return "✅ Arayüz dili Türkçe olarak değiştirildi. Sayfayı yeniden yükleyin."
                    else:
                        return "✅ Interface language changed to English. Please reload the page."
                
                # Connect interface language selector to change handler
                interface_language_selector.change(
                    fn=change_interface_language,
                    inputs=[interface_language_selector],
                    outputs=[settings_status]
                )
                
                # Language change handler for top selector (existing functionality)
                def change_top_language(new_lang):
                    """Change the interface language from top selector"""
                    global current_language
                    current_language = new_lang
                    return new_lang
                
                # Connect top language selector
                language_selector.change(
                    fn=change_top_language,
                    inputs=[language_selector],
                    outputs=[]
                )
                
                # Connect the save button to the master save function
                save_settings_button.click(
                    fn=save_all_settings_master,
                    inputs=[
                        # OpenAI settings
                        openai_api_key, openai_base_url, openai_llm_model, 
                        openai_stt_model, openai_tts_model, openai_voice_select,
                        # ElevenLabs settings
                        elevenlabs_api_key, elevenlabs_base_url, elevenlabs_model,
                        # Gemini settings
                        gemini_api_key, gemini_base_url, gemini_model,
                        gemini_tts_model, gemini_voice_select,
                        # Global settings
                        default_llm_provider, default_tts_provider, default_stt_provider,
                        default_temperature, default_max_tokens, language_input, interface_language_selector, stories_path_input,
                        # Audio settings
                        noise_reduction_enabled, noise_sensitivity, auto_calibrate, calibration_duration
                    ],
                    outputs=[settings_status]
                )
, path in stories_list:
            story_path = Path(path)
            
            # Count paragraphs
            paragraphs = list(story_path.glob("paragraph_*.txt"))
            total_paragraphs += len(paragraphs)
            
            # Get voice info
            info_file = story_path / "info.yaml"
            if info_file.exists():
                try:
                    with open(info_file, 'r') as f:
                        info = yaml.safe_load(f)
                    voice = info.get('tts_voice', 'unknown')
                    voice_counts[voice] = voice_counts.get(voice, 0) + 1
                    
                    # Check if recent (last 7 days)
                    import time
                    if story_path.stat().st_mtime > time.time() - (7 * 24 * 3600):
                        recent_stories.append(name)
                except:
                    pass
        
        # Generate HTML stats with Turkish text
        stats_html = f"""
        <div style="background: #2c3e50; padding: 15px; border-radius: 8px; margin: 10px 0; color: #ffffff;">
            <h4 style="color: #ffffff;">📊 Hikaye Koleksiyonu İstatistikleri</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; color: #ecf0f1;">
                <div><strong>Toplam Hikayeler:</strong> {total_stories}</div>
                <div><strong>Toplam Paragraflar:</strong> {total_paragraphs}</div>
                <div><strong>Son Hikayeler:</strong> {len(recent_stories)}</div>
                <div><strong>Ortalama Paragraf:</strong> {total_paragraphs // total_stories if total_stories > 0 else 0}</div>
            </div>
            
            <h5 style="margin-top: 15px; color: #ffffff;">🎵 Ses Kullanımı</h5>
            <div style="font-size: 0.9em; color: #ecf0f1;">
        """
        
        for voice, count in sorted(voice_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_stories * 100) if total_stories > 0 else 0
            stats_html += f"<div style='color: #ecf0f1;'>{voice}: {count} hikaye ({percentage:.1f}%)</div>"
        
        stats_html += """
            </div>
        </div>
        """
        
        return stats_html
    
    except Exception as e:
        return f"<div style='color: #ffffff; padding: 10px; background: #e74c3c; border-radius: 5px;'>İstatistik oluşturulurken hata: {str(e)}</div>"


def filter_story_collection(search_query: str, category: str, voice_filter: str) -> str:
    """Filter and display story collection based on criteria."""
    try:
        stories_list = get_story_list()
        filtered_stories = []
        
        for name, path in stories_list:
            story_path = Path(path)
            include_story = True
            
            # Apply search filter
            if search_query and search_query.strip():
                query_lower = search_query.lower().strip()
                if query_lower not in name.lower():
                    # Check story content
                    found_in_content = False
                    for para_file in story_path.glob("paragraph_*.txt"):
                        try:
                            content = para_file.read_text().lower()
                            if query_lower in content:
                                found_in_content = True
                                break
                        except:
                            pass
                    if not found_in_content:
                        include_story = False
            
            # Apply category filter
            if include_story and category != _('all_categories'):
                if category == _('recent'):
                    import time
                    if story_path.stat().st_mtime <= time.time() - (7 * 24 * 3600):
                        include_story = False
                elif category == _('long_stories'):
                    paragraph_count = len(list(story_path.glob("paragraph_*.txt")))
                    if paragraph_count < 7:
                        include_story = False
                elif category == _('short_stories'):
                    paragraph_count = len(list(story_path.glob("paragraph_*.txt")))
                    if paragraph_count >= 7:
                        include_story = False
            
            # Apply voice filter
            if include_story and voice_filter != _('all_voices'):
                info_file = story_path / "info.yaml"
                if info_file.exists():
                    try:
                        with open(info_file, 'r') as f:
                            info = yaml.safe_load(f)
                        story_voice = info.get('tts_voice', '')
                        if story_voice != voice_filter:
                            include_story = False
                    except:
                        include_story = False
                else:
                    include_story = False
            
            if include_story:
                filtered_stories.append((name, path))
        
        # Generate HTML for filtered stories
        if not filtered_stories:
            return "<div style='color: #495057; padding: 10px;'>Mevcut filtrelere uyan hikaye yok.</div>"
        
        html_content = f"""
        <div style="max-height: 400px; overflow-y: auto; color: #333;">
            <h5 style="color: #2c3e50;">📖 {len(filtered_stories)} hikaye bulundu</h5>
        """
        
        for name, path in filtered_stories[:20]:  # Limit to 20 for performance
            story_path = Path(path)
            paragraph_count = len(list(story_path.glob("paragraph_*.txt")))
            
            # Get story info
            info_file = story_path / "info.yaml"
            voice_info = "Bilinmeyen"
            query_info = "Bilinmeyen"
            if info_file.exists():
                try:
                    with open(info_file, 'r') as f:
                        info = yaml.safe_load(f)
                    voice_info = info.get('tts_voice', 'Bilinmeyen')
                    query_info = info.get('query', 'Bilinmeyen')[:100] + "..." if len(info.get('query', '')) > 100 else info.get('query', 'Bilinmeyen')
                except:
                    pass
            
            html_content += f"""
            <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 5px; background: #ffffff; color: #333;">
                <div style="font-weight: bold; color: #2c3e50;">{name}</div>
                <div style="font-size: 0.9em; color: #666; margin: 5px 0;">
                    Sorgu: {query_info}
                </div>
                <div style="font-size: 0.8em; color: #888;">
                    {paragraph_count} paragraf • Ses: {voice_info}
                </div>
            </div>
            """
        
        if len(filtered_stories) > 20:
            html_content += f"<div style='text-align: center; padding: 10px; color: #666;'>... ve {len(filtered_stories) - 20} hikaye daha</div>"
        
        html_content += "</div>"
        return html_content
    
    except Exception as e:
        return f"<div style='color: #e74c3c; padding: 10px; background: #f8f9fa; border-radius: 5px;'>Hikayeler filtrelenirken hata: {str(e)}</div>"


async def generate_story_continuation(story_path: str, 
                                    continuation_request: str,
                                    num_paragraphs: int,
                                    voice: str) -> str:
    """Generate continuation for an existing story."""
    if not story_path:
        return f"❌ {_('no_story_selected')}"
    
    if not continuation_request or not continuation_request.strip():
        return f"❌ {_('please_provide_request')}"
    
    try:
        story_dir = Path(story_path)
        
        # Extract story context using our new utility functions
        story_context = utils.extract_story_context(story_dir, max_paragraphs=10)
        if not story_context['paragraphs']:
            return "❌ Mevcut hikaye içeriği bulunamadı"
        
        # Get the next paragraph index
        starting_index = utils.get_next_paragraph_index(story_dir)
        
        # Create continuation prompt
        base_prompt = utils.read_from_file(ctx.config["prompt_file"])
        continuation_context = "\n\n".join(story_context['paragraphs'])
        
        full_prompt = f"""{base_prompt}

Var olan bir hikayeye devam ediyorsun. Şimdiye kadar olan:

Orijinal istek: {story_context['original_query']}

Şimdiye kadarki hikaye:
{continuation_context}

Şimdi kullanıcının isteğine göre bu hikayeye devam et: {continuation_request}

Hikayeyi doğal şekilde devam ettiren tam olarak {num_paragraphs} yeni paragraf oluştur."""

        # Generate the continuation using the LLM
        response = await ctx.llm_client.chat.completions.create(
            model=ctx.config["llm_model"],
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": continuation_request}
            ],
            temperature=ctx.config["temperature"],
            max_tokens=ctx.config["max_tokens"],
            stream=True
        )
        
        # Process the streaming response
        current_paragraph = []
        paragraph_index = starting_index
        generated_count = 0
        
        async for chunk in response:
            fragment = chunk.choices[0].delta.content
            if fragment is None:
                break
            
            current_paragraph.append(fragment)
            
            # Check for paragraph breaks
            if fragment.endswith("\n\n"):
                paragraph_text = "".join(current_paragraph).strip()
                if paragraph_text:
                    # Save paragraph text
                    paragraph_file = story_dir / f"paragraph_{paragraph_index}.txt"
                    utils.write_to_file(paragraph_file, paragraph_text)
                    
                    # Generate audio for the paragraph
                    await fably.synthesize_audio(ctx, story_dir, paragraph_index, paragraph_text)
                    
                    generated_count += 1
                    paragraph_index += 1
                    current_paragraph = []
                    
                    if generated_count >= num_paragraphs:
                        break
        
        # Handle any remaining content
        if current_paragraph and generated_count < num_paragraphs:
            paragraph_text = "".join(current_paragraph).strip()
            if paragraph_text:
                paragraph_file = story_dir / f"paragraph_{paragraph_index}.txt"
                utils.write_to_file(paragraph_file, paragraph_text)
                await fably.synthesize_audio(ctx, story_dir, paragraph_index, paragraph_text)
                generated_count += 1
        
        return f"✅ {generated_count} {_('continuation_generated')}"
    
    except Exception as e:
        return f"❌ {_('error_generating_continuation')}: {str(e)}"


if __name__ == "__main__":
    # Launch the enhanced Gradio interface with Turkish as default
    app = create_gradio_interface()
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
