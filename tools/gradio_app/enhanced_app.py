"""
Enhanced Fably Web Interface - Comprehensive Story Management System

This application provides a full-featured web interface for managing Fably stories,
including browsing existing stories, editing paragraphs, and regenerating audio.
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


# Default configuration - can be overridden via environment variables
DEFAULT_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "elevenlabs_api_key": os.getenv("ELEVENLABS_API_KEY", ""),
    "stt_url": "https://api.openai.com/v1",
    "stt_model": "whisper-1", 
    "llm_url": "https://api.openai.com/v1",
    "llm_model": "gpt-4o",
    "tts_url": "https://api.openai.com/v1",
    "tts_model": "tts-1",
    "tts_voice": "nova",
    "tts_provider": "openai",
    "tts_format": "mp3",
    "elevenlabs_url": "https://api.elevenlabs.io",
    "language": "en",
    "temperature": 1.0,
    "max_tokens": 2000,
    "stories_path": "./stories",
    "examples_path": "./fably/examples",
    "prompt_file": "./fably/prompt.txt",
    "query_guard": ""  # No query guard - users can speak naturally
}

# Available voices from both providers
OPENAI_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
ELEVENLABS_VOICES = []  # Will be populated dynamically

# TTS Providers
TTS_PROVIDERS = ["openai", "elevenlabs"]


class EnhancedFablyContext:
    """Enhanced context for the Gradio application with story management capabilities."""
    
    def __init__(self, config: Dict = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
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
                openai_url=self.config["tts_url"],
                elevenlabs_url=self.config["elevenlabs_url"]
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


# Global context instance
ctx = EnhancedFablyContext()


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
        return f"✅ Saved paragraph {paragraph_index}"
    except Exception as e:
        return f"❌ Error saving paragraph {paragraph_index}: {str(e)}"


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
        
        return f"✅ Regenerated audio for paragraph {paragraph_index} with voice '{voice}'"
    except Exception as e:
        return f"❌ Error regenerating audio: {str(e)}"


def transcribe_audio(audio_file: str) -> str:
    """Transcribe audio file using the configured STT service."""
    if not audio_file:
        return "No audio file provided"
    
    try:
        with open(audio_file, "rb") as f:
            response = ctx.stt_client.audio.transcriptions.create(
                model=ctx.config["stt_model"],
                language=ctx.config["language"],
                file=f
            )
        return response.text
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"


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
        return f"Error generating story: {str(e)}"


async def get_available_voices() -> List[str]:
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
    
    try:
        # Parse voice specification (provider:voice_id)
        if ":" in voice_spec:
            provider, voice_id = voice_spec.split(":", 1)
        else:
            provider = "openai"
            voice_id = voice_spec
        
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
        print(f"Error generating speech: {str(e)}")
        return None
    """Convert text to speech and return audio data."""
    if not text.strip():
        return None
    
    try:
        response = await ctx.tts_client.audio.speech.create(
            input=text,
            model=ctx.config["tts_model"],
            voice=voice,
            response_format="wav",
        )
        
        # Write to temporary file and read back
        temp_file = "temp_story.wav"
        response.write_to_file(temp_file)
        data, samplerate = sf.read(temp_file)
        
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return samplerate, data
    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return None


# Story Library Tab Functions
def on_story_select(selected_story: str) -> Tuple[str, str, List[gr.Textbox]]:
    """Handle story selection and load story details."""
    if not selected_story:
        return "No story selected", "", []
    
    try:
        # Extract story path from dropdown value
        story_path = selected_story.split(" | ")[1] if " | " in selected_story else ""
        if not story_path:
            return "Invalid story selection", "", []
        
        info, paragraphs = load_story_info(story_path)
        
        # Format story info for display
        info_text = f"""
**Query:** {info.get('query', 'N/A')}
**Language:** {info.get('language', 'N/A')}
**LLM Model:** {info.get('llm_model', 'N/A')}
**TTS Voice:** {info.get('tts_voice', 'N/A')}
**Temperature:** {info.get('llm_temperature', 'N/A')}
**Paragraphs:** {len(paragraphs)}
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
        return "Error loading story", f"Error: {str(e)}", []


def create_gradio_interface():
    """Create the main Gradio interface with multiple tabs."""
    
    # Load default prompt
    try:
        default_prompt = utils.read_from_file(ctx.prompt_file)
    except:
        default_prompt = "You are a storyteller who tells imaginative stories to children."
    
    with gr.Blocks(title="Fably - AI Storyteller Management", theme=gr.themes.Soft()) as app:
        
        gr.Markdown("# 📚 Fably - AI Storyteller Management Interface")
        gr.Markdown("*Comprehensive story creation, editing, and audio generation*")
        
        with gr.Tabs():
            
            # Story Library Tab
            with gr.Tab("📖 Story Library"):
                gr.Markdown("### Browse and Edit Existing Stories")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        story_dropdown = gr.Dropdown(
                            choices=[f"{name} | {path}" for name, path in get_story_list()],
                            label="Select Story",
                            interactive=True
                        )
                        refresh_button = gr.Button("🔄 Refresh List")
                        
                        story_info_display = gr.Markdown("*Select a story to view details*")
                    
                    with gr.Column(scale=2):
                        selected_story_path = gr.Textbox(
                            label="Selected Story Path", 
                            visible=False
                        )
                        
                        # Dynamic paragraph editing area
                        paragraph_editor = gr.Column(visible=False)
                        
                        with paragraph_editor:
                            gr.Markdown("### Edit Paragraphs")
                            
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
                                    value=f"{ctx.config['tts_provider']}:{ctx.config['tts_voice']}",
                                    label="TTS Voice",
                                    interactive=True,
                                    allow_custom_value=True
                                )
                                refresh_voices_btn = gr.Button("🔄 Refresh Voices")
                            
                            with gr.Row():
                                save_all_button = gr.Button("💾 Save All Changes", variant="primary")
                                regenerate_all_button = gr.Button("🎵 Regenerate All Audio")
                                continue_story_button = gr.Button("📖 Continue Story", variant="secondary")
                            
                            # Story continuation section
                            with gr.Accordion("Story Continuation", open=False):
                                gr.Markdown("Generate additional paragraphs to continue this story")
                                continuation_prompt = gr.Textbox(
                                    label="Continuation Request",
                                    placeholder="How should the story continue? (e.g., 'What happens when the princess meets the dragon?')",
                                    lines=2
                                )
                                with gr.Row():
                                    continue_paragraphs = gr.Slider(
                                        minimum=1,
                                        maximum=10,
                                        value=3,
                                        step=1,
                                        label="Number of new paragraphs"
                                    )
                                    continuation_voice = gr.Dropdown(
                                        choices=[],  # Will be populated dynamically
                                        value=f"{ctx.config['tts_provider']}:{ctx.config['tts_voice']}",
                                        label="Voice for new paragraphs",
                                        interactive=True,
                                        allow_custom_value=True
                                    )
                                generate_continuation_btn = gr.Button("✨ Generate Continuation", variant="primary")
                            
                            operation_status = gr.Textbox(
                                label="Status",
                                interactive=False,
                                lines=2
                            )
                
                # Event handlers for Story Library
                def refresh_story_list():
                    return gr.Dropdown(
                        choices=[f"{name} | {path}" for name, path in get_story_list()]
                    )
                
                def refresh_voices():
                    """Refresh the voice dropdown options."""
                    import asyncio
                    voice_options = asyncio.run(get_available_voices())
                    return gr.Dropdown(choices=voice_options)
                
                refresh_voices_btn.click(
                    fn=refresh_voices,
                    outputs=[voice_select]
                )
                
                def load_selected_story(selected_story):
                    if not selected_story:
                        return (
                            "",
                            "*Select a story to view details*",
                            gr.Column(visible=False),
                            *[gr.Textbox(visible=False) for _ in range(20)]
                        )
                    
                    try:
                        story_path = selected_story.split(" | ")[1]
                        info, paragraphs = load_story_info(story_path)
                        
                        info_text = f"""
**Query:** {info.get('query', 'N/A')}  
**Language:** {info.get('language', 'N/A')}  
**LLM Model:** {info.get('llm_model', 'N/A')}  
**TTS Voice:** {info.get('tts_voice', 'N/A')}  
**Temperature:** {info.get('llm_temperature', 'N/A')}  
**Paragraphs:** {len(paragraphs)}
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
                            f"**Error loading story:** {str(e)}",
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
            with gr.Tab("✨ Create New Story"):
                gr.Markdown("### Create and Generate New Stories")
                
                with gr.Row():
                    with gr.Column():
                        voice_query = gr.Audio(
                            label="🎤 Voice Query",
                            sources=["microphone"],
                            type="filepath",
                            waveform_options=gr.WaveformOptions(
                                waveform_color="#01C6FF",
                                waveform_progress_color="#0066B4",
                                skip_length=2,
                                show_controls=False,
                            ),
                        )
                        
                        transcribe_button = gr.Button("🔤 Transcribe Voice Query")
                        
                        transcribed_query = gr.Textbox(
                            label="📝 Transcribed Query",
                            placeholder="Or type your story request directly...",
                            lines=2,
                        )
                        
                        with gr.Row():
                            temperature_slider = gr.Slider(
                                0, 2.0, 
                                value=ctx.config["temperature"], 
                                label="🌡️ Creativity (Temperature)"
                            )
                            max_tokens_slider = gr.Slider(
                                100, 4000, 
                                value=ctx.config["max_tokens"], 
                                label="📏 Max Length (Tokens)"
                            )
                    
                    with gr.Column():
                        prompt_input = gr.Textbox(
                            lines=6,
                            label="📋 Story Generation Prompt",
                            value=default_prompt,
                        )
                        
                        new_story_voice = gr.Dropdown(
                            choices=[],  # Will be populated dynamically
                            value=f"{ctx.config['tts_provider']}:{ctx.config['tts_voice']}",
                            label="🎵 TTS Voice",
                            interactive=True,
                            allow_custom_value=True
                        )
                        
                        refresh_new_story_voices_btn = gr.Button("🔄 Refresh Voices", size="sm")
                
                generate_story_button = gr.Button("✨ Generate Story", variant="primary")
                
                story_output = gr.Textbox(
                    lines=20,
                    label="📖 Generated Story",
                    placeholder="Your generated story will appear here..."
                )
                
                with gr.Row():
                    read_story_button = gr.Button("🎵 Convert to Audio")
                    save_story_button = gr.Button("💾 Save Story")
                
                story_audio = gr.Audio(
                    label="🔊 Story Audio",
                    interactive=False,
                )
                
                new_story_status = gr.Textbox(
                    label="Status",
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
                    return asyncio.run(generate_story_content(query, prompt, temperature, max_tokens))
                
                generate_story_button.click(
                    fn=generate_story_sync,
                    inputs=[transcribed_query, prompt_input, temperature_slider, max_tokens_slider],
                    outputs=[story_output],
                )
                
                # Async wrapper for TTS
                def read_story_sync(text, voice_spec):
                    return asyncio.run(synthesize_with_provider(text, voice_spec))
                
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
            
            # Settings Tab
            with gr.Tab("⚙️ Settings"):
                gr.Markdown("### Configuration Settings")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### API Configuration")
                        
                        api_key_input = gr.Textbox(
                            label="OpenAI API Key",
                            value=ctx.config["api_key"],
                            type="password",
                            placeholder="sk-..."
                        )
                        
                        elevenlabs_key_input = gr.Textbox(
                            label="ElevenLabs API Key",
                            value=ctx.config.get("elevenlabs_api_key", ""),
                            type="password",
                            placeholder="your-elevenlabs-api-key"
                        )
                        
                        tts_provider_select = gr.Dropdown(
                            choices=TTS_PROVIDERS,
                            value=ctx.config["tts_provider"],
                            label="Default TTS Provider"
                        )
                        
                        stt_url_input = gr.Textbox(
                            label="STT Service URL",
                            value=ctx.config["stt_url"]
                        )
                        
                        llm_url_input = gr.Textbox(
                            label="LLM Service URL", 
                            value=ctx.config["llm_url"]
                        )
                        
                        tts_url_input = gr.Textbox(
                            label="TTS Service URL",
                            value=ctx.config["tts_url"] 
                        )
                        
                        elevenlabs_url_input = gr.Textbox(
                            label="ElevenLabs Service URL",
                            value=ctx.config["elevenlabs_url"]
                        )
                    
                    with gr.Column():
                        gr.Markdown("#### Model Configuration")
                        
                        stt_model_input = gr.Textbox(
                            label="STT Model",
                            value=ctx.config["stt_model"]
                        )
                        
                        llm_model_input = gr.Textbox(
                            label="LLM Model",
                            value=ctx.config["llm_model"]
                        )
                        
                        tts_model_input = gr.Textbox(
                            label="TTS Model",
                            value=ctx.config["tts_model"]
                        )
                        
                        default_voice_input = gr.Dropdown(
                            choices=[],  # Will be populated dynamically
                            value=f"{ctx.config['tts_provider']}:{ctx.config['tts_voice']}",
                            label="Default TTS Voice",
                            allow_custom_value=True
                        )
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Story Configuration")
                        
                        stories_path_input = gr.Textbox(
                            label="Stories Directory",
                            value=ctx.config["stories_path"]
                        )
                        
                        query_guard_input = gr.Textbox(
                            label="Query Guard Phrase (Legacy)",
                            value=ctx.config["query_guard"],
                            info="Optional prefix for stories (leave empty for natural language)"
                        )
                        
                        language_input = gr.Textbox(
                            label="Language",
                            value=ctx.config["language"]
                        )
                    
                    with gr.Column():
                        gr.Markdown("#### Generation Defaults")
                        
                        default_temperature = gr.Slider(
                            0, 2.0,
                            value=ctx.config["temperature"],
                            label="Default Temperature"
                        )
                        
                        default_max_tokens = gr.Slider(
                            100, 4000,
                            value=ctx.config["max_tokens"],
                            label="Default Max Tokens"
                        )
                
                # Audio Quality & Noise Reduction Settings
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Audio Quality Settings")
                        
                        noise_reduction_enabled = gr.Checkbox(
                            label="Enable Noise Reduction",
                            value=ctx.config.get("noise_reduction", False),
                            info="Filter background noise during voice recording"
                        )
                        
                        noise_sensitivity = gr.Slider(
                            0.1, 10.0,
                            value=ctx.config.get("noise_sensitivity", 2.0),
                            step=0.1,
                            label="Noise Sensitivity",
                            info="Higher values are more sensitive to quiet sounds"
                        )
                    
                    with gr.Column():
                        gr.Markdown("#### Audio Calibration")
                        
                        auto_calibrate = gr.Checkbox(
                            label="Auto-Calibrate Noise Floor",
                            value=ctx.config.get("auto_calibrate", False),
                            info="Automatically measure ambient noise on startup"
                        )
                        
                        calibration_duration = gr.Slider(
                            1.0, 10.0,
                            value=ctx.config.get("calibration_duration", 3.0),
                            step=0.5,
                            label="Calibration Duration (seconds)",
                            info="How long to measure ambient noise"
                        )
                
                save_settings_button = gr.Button("💾 Save Settings", variant="primary")
                settings_status = gr.Textbox(
                    label="Settings Status",
                    interactive=False
                )
                
                def save_settings(*args):
                    """Save updated settings to context."""
                    try:
                        # Update context configuration
                        config_keys = [
                            "api_key", "elevenlabs_api_key", "tts_provider", 
                            "stt_url", "llm_url", "tts_url", "elevenlabs_url",
                            "stt_model", "llm_model", "tts_model", "tts_voice",
                            "stories_path", "query_guard", "language",
                            "temperature", "max_tokens",
                            "noise_reduction", "noise_sensitivity", "auto_calibrate", "calibration_duration"
                        ]
                        
                        for i, key in enumerate(config_keys):
                            if i < len(args):
                                ctx.config[key] = args[i]
                        
                        # Reinitialize clients with new settings
                        ctx._init_clients()
                        ctx._init_paths()
                        
                        return "✅ Settings saved successfully!"
                    
                    except Exception as e:
                        return f"❌ Error saving settings: {str(e)}"
                
                save_settings_button.click(
                    fn=save_settings,
                    inputs=[
                        api_key_input, elevenlabs_key_input, tts_provider_select,
                        stt_url_input, llm_url_input, tts_url_input, elevenlabs_url_input,
                        stt_model_input, llm_model_input, tts_model_input, default_voice_input,
                        stories_path_input, query_guard_input, language_input,
                        default_temperature, default_max_tokens,
                        noise_reduction_enabled, noise_sensitivity, auto_calibrate, calibration_duration
                    ],
                    outputs=[settings_status]
                )
            
            # Story Collections Tab - Advanced Story Management
            with gr.Tab("📚 Collections"):
                gr.Markdown("### Advanced Story Management & Organization")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### Quick Stats")
                        stats_display = gr.HTML("")
                        refresh_stats_btn = gr.Button("🔄 Refresh Stats")
                        
                        gr.Markdown("#### Filters & Search")
                        search_query = gr.Textbox(
                            label="Search Stories",
                            placeholder="Search by title, content, or topic..."
                        )
                        
                        category_filter = gr.Dropdown(
                            choices=["All", "Favorites", "Recent", "Long Stories", "Short Stories"],
                            value="All",
                            label="Category Filter"
                        )
                        
                        voice_filter = gr.Dropdown(
                            choices=["All Voices"] + OPENAI_VOICES,
                            value="All Voices", 
                            label="Voice Filter"
                        )
                        
                        apply_filters_btn = gr.Button("🔍 Apply Filters")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("#### Story Collection")
                        story_collection = gr.HTML("")
                        
                        with gr.Row():
                            favorite_btn = gr.Button("⭐ Add to Favorites")
                            export_btn = gr.Button("📤 Export Selected")
                            delete_btn = gr.Button("🗑️ Delete Selected", variant="stop")
                        
                        selected_stories = gr.JSON(value=[], visible=False)
                        collection_status = gr.Textbox(
                            label="Status",
                            interactive=False
                        )
                
                # Collection event handlers
                def refresh_stats():
                    """Generate story collection statistics."""
                    return get_story_statistics()
                
                def apply_story_filters(search, category, voice):
                    """Apply filters and search to story collection."""
                    return filter_story_collection(search, category, voice)
                
                refresh_stats_btn.click(
                    fn=refresh_stats,
                    outputs=[stats_display]
                )
                
                apply_filters_btn.click(
                    fn=apply_story_filters,
                    inputs=[search_query, category_filter, voice_filter],
                    outputs=[story_collection]
                )
            
            # About Tab
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
                ### 📚 Fably - AI Storyteller Management Interface
                
                **Enhanced Web Interface for Fably Story Management**
                
                This comprehensive interface allows you to:
                
                #### 📖 Story Library
                - Browse existing stories from your stories directory and examples
                - View story metadata (query, model used, voice, etc.)
                - Edit individual paragraphs with live preview
                - Regenerate audio for specific paragraphs with different voices
                
                #### ✨ Create New Story
                - Record voice queries or type text requests
                - Configure generation parameters (temperature, max tokens)
                - Generate stories using various LLM models
                - Convert stories to audio with selectable voices
                - Save stories in the standard Fably format
                
                #### ⚙️ Settings
                - Configure API endpoints (OpenAI, local servers)
                - Set default models and voices
                - Manage story directories and safety settings
                
                ---
                
                **Fably Project Features:**
                - 🎯 **Child-Safe**: Built-in query guards and content filtering
                - 🚀 **Low Latency**: Streaming generation for quick response
                - 🏠 **Self-Hostable**: Support for local AI models via Ollama
                - 🔧 **Modular**: Configurable STT, LLM, and TTS services
                - 📱 **Hardware Ready**: Optimized for Raspberry Pi deployment
                
                **System Requirements:**
                - Python 3.8+
                - OpenAI API key (or local AI server setup)
                - Microphone and speakers for voice interaction
                
                For more information, visit the [Fably GitHub repository](https://github.com/stefanom/fably).
                """)
        
        # Initialize voice dropdowns on startup
        def initialize_voice_dropdowns():
            import asyncio
            voice_options = asyncio.run(get_available_voices())
            return voice_options
        
        # Set initial voice options
        app.load(
            fn=lambda: (
                initialize_voice_dropdowns(),  # voice_select
                initialize_voice_dropdowns(),  # new_story_voice  
                initialize_voice_dropdowns()   # default_voice_input
            ),
            outputs=[voice_select, new_story_voice, default_voice_input]
        )
        
        return app


def save_story_to_disk(query: str, story_text: str, voice: str) -> str:
    """Save a new story to disk in Fably format."""
    try:
        # Create story directory
        story_name = utils.query_to_filename(query, ctx.config["query_guard"])
        story_dir = ctx.stories_path / story_name
        story_dir.mkdir(parents=True, exist_ok=True)
        
        # Save story metadata
        info = {
            "query": query,
            "language": ctx.config["language"],
            "stt_model": ctx.config["stt_model"],
            "llm_model": ctx.config["llm_model"],
            "llm_temperature": ctx.config["temperature"],
            "llm_max_tokens": ctx.config["max_tokens"],
            "tts_model": ctx.config["tts_model"],
            "tts_voice": voice,
        }
        utils.write_to_yaml(story_dir / "info.yaml", info)
        
        # Split story into paragraphs and save
        paragraphs = [p.strip() for p in story_text.split('\n\n') if p.strip()]
        for i, paragraph in enumerate(paragraphs):
            utils.write_to_file(story_dir / f"paragraph_{i}.txt", paragraph)
        
        return f"✅ Story saved to {story_dir} ({len(paragraphs)} paragraphs)"
    
    except Exception as e:
        return f"❌ Error saving story: {str(e)}"


def batch_save_paragraphs(story_path: str, paragraph_texts: List[str]) -> str:
    """Save all paragraph changes at once."""
    if not story_path:
        return "❌ No story selected"
    
    try:
        story_dir = Path(story_path)
        saved_count = 0
        
        for i, text in enumerate(paragraph_texts):
            if text and text.strip():  # Only save non-empty paragraphs
                paragraph_file = story_dir / f"paragraph_{i}.txt"
                utils.write_to_file(paragraph_file, text.strip())
                saved_count += 1
        
        return f"✅ Saved {saved_count} paragraphs successfully"
    
    except Exception as e:
        return f"❌ Error saving paragraphs: {str(e)}"


async def batch_regenerate_audio(story_path: str, voice: str, 
                               paragraph_texts: List[str]) -> str:
    """Regenerate audio for all paragraphs with the selected voice."""
    if not story_path:
        return "❌ No story selected"
    
    try:
        story_dir = Path(story_path)
        regenerated_count = 0
        
        # Update context voice
        ctx.config["tts_voice"] = voice
        
        for i, text in enumerate(paragraph_texts):
            if text and text.strip():
                await fably.synthesize_audio(ctx, story_dir, i, text.strip())
                regenerated_count += 1
        
        return f"✅ Regenerated audio for {regenerated_count} paragraphs with voice '{voice}'"
    
    except Exception as e:
        return f"❌ Error regenerating audio: {str(e)}"


# Advanced Story Management Functions

def get_story_statistics() -> str:
    """Generate HTML statistics for story collection."""
    try:
        stories_list = get_story_list()
        total_stories = len(stories_list)
        
        # Count paragraphs and estimate total content
        total_paragraphs = 0
        voice_counts = {}
        recent_stories = []
        
        for name, path in stories_list:
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
        
        # Generate HTML stats
        stats_html = f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4>📊 Story Collection Statistics</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px;">
                <div><strong>Total Stories:</strong> {total_stories}</div>
                <div><strong>Total Paragraphs:</strong> {total_paragraphs}</div>
                <div><strong>Recent Stories:</strong> {len(recent_stories)}</div>
                <div><strong>Avg Paragraphs:</strong> {total_paragraphs // total_stories if total_stories > 0 else 0}</div>
            </div>
            
            <h5 style="margin-top: 15px;">🎵 Voice Usage</h5>
            <div style="font-size: 0.9em;">
        """
        
        for voice, count in sorted(voice_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_stories * 100) if total_stories > 0 else 0
            stats_html += f"<div>{voice}: {count} stories ({percentage:.1f}%)</div>"
        
        stats_html += """
            </div>
        </div>
        """
        
        return stats_html
    
    except Exception as e:
        return f"<div>Error generating statistics: {str(e)}</div>"


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
            if include_story and category != "All":
                if category == "Recent":
                    import time
                    if story_path.stat().st_mtime <= time.time() - (7 * 24 * 3600):
                        include_story = False
                elif category == "Long Stories":
                    paragraph_count = len(list(story_path.glob("paragraph_*.txt")))
                    if paragraph_count < 7:
                        include_story = False
                elif category == "Short Stories":
                    paragraph_count = len(list(story_path.glob("paragraph_*.txt")))
                    if paragraph_count >= 7:
                        include_story = False
            
            # Apply voice filter
            if include_story and voice_filter != "All Voices":
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
            return "<div>No stories match the current filters.</div>"
        
        html_content = f"""
        <div style="max-height: 400px; overflow-y: auto;">
            <h5>📖 Found {len(filtered_stories)} stories</h5>
        """
        
        for name, path in filtered_stories[:20]:  # Limit to 20 for performance
            story_path = Path(path)
            paragraph_count = len(list(story_path.glob("paragraph_*.txt")))
            
            # Get story info
            info_file = story_path / "info.yaml"
            voice_info = "Unknown"
            query_info = "Unknown"
            if info_file.exists():
                try:
                    with open(info_file, 'r') as f:
                        info = yaml.safe_load(f)
                    voice_info = info.get('tts_voice', 'Unknown')
                    query_info = info.get('query', 'Unknown')[:100] + "..." if len(info.get('query', '')) > 100 else info.get('query', 'Unknown')
                except:
                    pass
            
            html_content += f"""
            <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 5px; background: white;">
                <div style="font-weight: bold; color: #333;">{name}</div>
                <div style="font-size: 0.9em; color: #666; margin: 5px 0;">
                    Query: {query_info}
                </div>
                <div style="font-size: 0.8em; color: #888;">
                    {paragraph_count} paragraphs • Voice: {voice_info}
                </div>
            </div>
            """
        
        if len(filtered_stories) > 20:
            html_content += f"<div style='text-align: center; padding: 10px; color: #666;'>... and {len(filtered_stories) - 20} more stories</div>"
        
        html_content += "</div>"
        return html_content
    
    except Exception as e:
        return f"<div>Error filtering stories: {str(e)}</div>"


# Export/Import and Backup Functions

def export_story_collection(selected_stories: list) -> str:
    """Export selected stories to a backup format."""
    try:
        import json
        import zipfile
        from datetime import datetime
        
        if not selected_stories:
            return "❌ No stories selected for export"
        
        # Create export directory
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = export_dir / f"fably_stories_{timestamp}.zip"
        
        with zipfile.ZipFile(export_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for story_name in selected_stories:
                # Find story path
                stories_list = get_story_list()
                story_path = None
                for name, path in stories_list:
                    if name == story_name:
                        story_path = Path(path)
                        break
                
                if story_path and story_path.exists():
                    # Add all files from story directory
                    for file_path in story_path.rglob("*"):
                        if file_path.is_file():
                            arc_name = f"{story_name}/{file_path.relative_to(story_path)}"
                            zipf.write(file_path, arc_name)
        
        return f"✅ Exported {len(selected_stories)} stories to {export_file}"
    
    except Exception as e:
        return f"❌ Error exporting stories: {str(e)}"


def create_story_backup() -> str:
    """Create a complete backup of all stories and settings."""
    try:
        import json
        import zipfile
        from datetime import datetime
        
        # Create backup directory
        backup_dir = Path("backups") 
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"fably_complete_backup_{timestamp}.zip"
        
        stories_path = Path(ctx.stories_path)
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup all stories
            if stories_path.exists():
                for file_path in stories_path.rglob("*"):
                    if file_path.is_file():
                        arc_name = f"stories/{file_path.relative_to(stories_path)}"
                        zipf.write(file_path, arc_name)
            
            # Backup configuration
            config_data = {
                "version": "1.0",
                "export_timestamp": timestamp,
                "config": {k: v for k, v in ctx.config.items() if k != "api_key"}  # Exclude sensitive data
            }
            
            zipf.writestr("config.json", json.dumps(config_data, indent=2))
        
        return f"✅ Complete backup created: {backup_file}"
    
    except Exception as e:
        return f"❌ Error creating backup: {str(e)}"


async def generate_story_continuation(story_path: str, 
                                    continuation_request: str,
                                    num_paragraphs: int,
                                    voice: str) -> str:
    """Generate continuation for an existing story."""
    if not story_path:
        return "❌ No story selected"
    
    if not continuation_request or not continuation_request.strip():
        return "❌ Please provide a continuation request"
    
    try:
        story_dir = Path(story_path)
        
        # Extract story context using our new utility functions
        story_context = utils.extract_story_context(story_dir, max_paragraphs=10)
        if not story_context['paragraphs']:
            return "❌ No existing story content found"
        
        # Get the next paragraph index
        starting_index = utils.get_next_paragraph_index(story_dir)
        
        # Create continuation prompt
        base_prompt = utils.read_from_file(ctx.config["prompt_file"])
        continuation_context = "\n\n".join(story_context['paragraphs'])
        
        full_prompt = f"""{base_prompt}

You are continuing an existing story. Here is what has happened so far:

Original request: {story_context['original_query']}

Story so far:
{continuation_context}

Now continue this story based on the user's request: {continuation_request}

Generate exactly {num_paragraphs} new paragraphs that continue the story naturally."""

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
        
        return f"✅ Generated {generated_count} new paragraphs continuing the story!"
    
    except Exception as e:
        return f"❌ Error generating story continuation: {str(e)}"


if __name__ == "__main__":
    # Launch the enhanced Gradio interface
    app = create_gradio_interface()
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
