#!/usr/bin/env python3

# --- Import necessary libraries ---
import asyncio
import os
import sys
import yaml
import gradio as gr
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from gradio.themes import Soft
import requests

# Add the parent directory to the system path to allow for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# --- Main Context Class ---
class FablyWebContext:
    """
    Manages the application's configuration and current state, like language.
    """
    def __init__(self):
        # Load default configuration on initialization
        self.config = self.load_default_config()
        self.current_language = "tr"  # Default language

    def load_default_config(self) -> Dict[str, Any]:
        """
        Loads default settings from environment variables or sets fallback values.
        """
        return {
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "openai_url": "https://api.openai.com/v1",
            "llm_model": "gpt-4o-mini",
            "tts_provider": "openai",
            "tts_voice": "nova",
            "elevenlabs_api_key": os.getenv("ELEVENLABS_API_KEY", ""),
            "elevenlabs_url": "https://api.elevenlabs.io/v1",
            "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
            "gemini_url": "https://generativelanguage.googleapis.com/v1beta",
            "llm_temperature": 0.9,
            "max_tokens": 2000,
            "noise_reduction": True,
            "noise_sensitivity": 2.0,
        }

    def update_language(self, language_code: str):
        """
        Updates the current language of the application.
        """
        self.current_language = language_code


# Create a global context object for the application
ctx = FablyWebContext()


# --- Helper Functions ---
def ensure_stories_directory():
    """
    Ensures that the directory for storing stories exists.
    """
    stories_dir = Path("./fably/stories")
    stories_dir.mkdir(parents=True, exist_ok=True)
    return stories_dir

def get_text(key: str, lang: Optional[str] = None) -> str:
    """
    Retrieves UI text from a dictionary based on the current language.
    """
    if lang is None:
        lang = ctx.current_language

    translations = {
        "tr": {
            "language_changed": "Dil değiştirildi",
            "story_library": "Hikaye Kütüphanesi",
            "create_story": "Yeni Hikaye Oluştur",
            "settings": "Ayarlar",
            "about": "Hakkında"
        },
        "en": {
            "language_changed": "Language changed",
            "story_library": "Story Library",
            "create_story": "Create New Story",
            "settings": "Settings",
            "about": "About"
        }
    }
    return translations.get(lang, {}).get(key, key)


def get_story_list() -> List[Tuple[str, str]]:
    """
    Scans the stories directory and returns a list of available stories.
    """
    stories_dir = ensure_stories_directory()
    story_list = []
    try:
        for story_path in stories_dir.iterdir():
            if story_path.is_dir() and (story_path / 'info.yaml').exists():
                try:
                    with open(story_path / 'info.yaml', 'r', encoding='utf-8') as f:
                        info = yaml.safe_load(f)
                    display_name = info.get('query', story_path.name)[:50]
                    if len(info.get('query', '')) > 50:
                        display_name += "..."
                    story_list.append((display_name, str(story_path)))
                except Exception:
                    continue  # Skip corrupted stories
    except Exception:
        pass  # Handle case where directory cannot be read
    return sorted(story_list)


def load_story_info(story_path: str) -> Tuple[Dict, List[str]]:
    """
    Loads story metadata and paragraph texts from a given story path.
    """
    story_dir = Path(story_path)
    with open(story_dir / 'info.yaml', 'r', encoding='utf-8') as f:
        info = yaml.safe_load(f)

    paragraphs = []
    for i in range(info.get('paragraphs', 20)):
        paragraph_file = story_dir / f'paragraph_{i}.txt'
        if paragraph_file.exists():
            with open(paragraph_file, 'r', encoding='utf-8') as f:
                paragraphs.append(f.read().strip())
        else:
            break
    return info, paragraphs


async def get_available_voices() -> List[Tuple[str, str]]:
    """
    Gets a list of available TTS voices from different providers.
    """
    voices = []
    openai_voices = ["nova", "alloy", "echo", "fable", "onyx", "shimmer"]
    for voice in openai_voices:
        voices.append((f"OpenAI: {voice.title()}", f"openai:{voice}"))

    if ctx.config.get("elevenlabs_api_key"):
        elevenlabs_voices = ["rachel", "adam", "arnold", "josh", "sam"]
        for voice in elevenlabs_voices:
            voices.append((f"ElevenLabs: {voice.title()}", f"elevenlabs:{voice}"))
    return voices


# --- Core Logic Functions ---
def transcribe_audio(audio_file) -> str:
    """
    (Placeholder) Transcribes audio input to text.
    """
    if not audio_file:
        return "❌ Ses dosyası bulunamadı"
    try:
        # This is a placeholder; actual transcription logic would go here.
        return f"🎤 Ses dosyası işlendi: {Path(audio_file).name}"
    except Exception as e:
        return f"❌ Ses işleme hatası: {str(e)}"


async def generate_story_content(
    query: str, prompt: str = "", temperature: float = 0.9, max_tokens: int = 2000
) -> str:
    """
    (Placeholder) Generates story content using an LLM.
    """
    if not query.strip():
        return "❌ Lütfen bir hikaye konusu girin"
    try:
        # This is a placeholder; actual LLM call would go here.
        return f"""🎭 **Hikaye Oluşturuldu**

**Konu:** {query}

**Paragraf 1:**
Bir zamanlar, {query} ile ilgili harika bir macera yaşanmış...

**Paragraf 2:**
Kahramanımız yolculuğuna devam ederken...

**Paragraf 3:**
Ve nihayet, mutlu sona ulaştılar...

*Bu örnek bir hikayedir. Gerçek kullanımda LLM servisi çağrılacak.*"""
    except Exception as e:
        return f"❌ Hikaye oluşturma hatası: {str(e)}"


async def synthesize_with_provider(text: str, voice_spec: str) -> Optional[str]:
    """
    (Placeholder) Synthesizes text to speech using a specified provider.
    """
    if not text.strip():
        return None
    try:
        provider, voice = voice_spec.split(":", 1)
        # This is a placeholder; actual TTS call would go here.
        return f"🔊 Ses dosyası oluşturuldu: {provider}:{voice}"
    except Exception as e:
        print(f"TTS Hatası: {str(e)}")
        return None


def save_story_to_disk(query: str, story: str, voice: str) -> str:
    """
    Saves the generated story and its metadata to the disk.
    """
    if not query.strip() or not story.strip():
        return "❌ Hikaye ve sorgu gereklidir"
    try:
        stories_dir = ensure_stories_directory()
        story_name = query.strip()[:50].replace(" ", "_").replace("/", "_")
        story_dir = stories_dir / story_name
        story_dir.mkdir(exist_ok=True)

        info = {
            "query": query,
            "language": "tr",
            "llm_model": ctx.config["llm_model"],
            "tts_voice": voice,
            "paragraphs": len(story.split("\n\n"))
        }

        with open(story_dir / 'info.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(info, f, allow_unicode=True)
        return f"✅ Hikaye kaydedildi: {story_dir}"
    except Exception as e:
        return f"❌ Kaydetme hatası: {str(e)}"


def batch_save_paragraphs(story_path: str, paragraph_texts: List[str]) -> str:
    """
    Saves all edited paragraphs to their respective text files.
    """
    if not story_path:
        return "❌ Hikaye seçilmedi"
    try:
        story_dir = Path(story_path)
        saved_count = 0
        for i, text in enumerate(paragraph_texts):
            if text and text.strip():
                with open(story_dir / f'paragraph_{i}.txt', 'w', encoding='utf-8') as f:
                    f.write(text.strip())
                saved_count += 1
        return f"✅ {saved_count} paragraf kaydedildi"
    except Exception as e:
        return f"❌ Kaydetme hatası: {str(e)}"


async def batch_regenerate_audio(story_path: str, voice: str, paragraph_texts: List[str]) -> str:
    """
    Regenerates audio for all paragraphs using the selected voice.
    """
    if not story_path or not voice:
        return "❌ Hikaye ve ses seçilmeli"
    try:
        regenerated_count = 0
        for i, text in enumerate(paragraph_texts):
            if text and text.strip():
                audio_result = await synthesize_with_provider(text, voice)
                if audio_result:
                    regenerated_count += 1
        return f"✅ {regenerated_count} paragraf sesi yeniden oluşturuldu"
    except Exception as e:
        return f"❌ Ses oluşturma hatası: {str(e)}"


def refresh_voices() -> gr.Dropdown:
    """
    Refreshes the voice selection dropdown with currently available voices.
    """
    voice_options = asyncio.run(get_available_voices())
    current_voice = f"{ctx.config['tts_provider']}:{ctx.config['tts_voice']}"
    is_current_voice_available = any(v[1] == current_voice for v in voice_options)
    
    return gr.Dropdown(
        choices=voice_options,
        value=current_voice if is_current_voice_available else (voice_options[0][1] if voice_options else None)
    )


# --- Gradio UI Definition ---
def create_fably_interface():
    """
    Builds the entire Gradio web interface for the application.
    """
    custom_css = """
    .fably-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin: 1rem 0;
    }
    .fably-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    .gradio-container {
        background: linear-gradient(135deg, #2a2e6e 0%, #4b206b 100%);
        min-height: 100vh;
    }
    """
    with gr.Blocks(
        title="🎭 Fably - AI Hikaye Yönetim Sistemi",
        theme=Soft(),
        css=custom_css
    ) as app:
        # --- Header and Language Selector ---
        with gr.Row():
            gr.HTML("""
            <div class="fably-header">
                <h1>🎭 Fably - Profesyonel AI Hikaye Sistemi</h1>
                <p>Yapay zeka destekli hikaye oluşturma ve yönetim platformu</p>
            </div>
            """)
        with gr.Row():
            language_selector = gr.Dropdown(
                choices=[("🇹🇷 Türkçe", "tr"), ("🇺🇸 English", "en")],
                value="tr",
                label="🌍 Dil / Language",
                scale=1
            )

        # --- Main Tabs ---
        with gr.Tabs() as main_tabs:
            
            # --- Story Library Tab ---
            with gr.Tab("📚 Hikaye Kütüphanesi"):
                with gr.Row():
                    with gr.Column(scale=1, elem_classes="fably-card"):
                        gr.Markdown("#### 📖 Mevcut Hikayeler")
                        story_dropdown = gr.Dropdown(
                            choices=[f"{name} | {path}" for name, path in get_story_list()],
                            label="Hikaye Seç",
                            interactive=True
                        )
                        refresh_list_btn = gr.Button("🔄 Listeyi Yenile")
                        selected_story_path = gr.Textbox(
                            label="Seçilen Hikaye Yolu",
                            interactive=False,
                            visible=False
                        )
                    with gr.Column(scale=2, elem_classes="fably-card"):
                        gr.Markdown("#### ℹ️ Hikaye Bilgileri")
                        story_info_display = gr.Markdown("Detayları görmek için bir hikaye seçin")
                
                with gr.Column(visible=False, elem_classes="fably-card") as paragraph_editor:
                    gr.Markdown("#### ✏️ Paragraf Düzenleyici")
                    with gr.Row():
                        voice_select = gr.Dropdown(choices=[], label="🎵 Ses Seçin", interactive=True)
                        refresh_voices_btn = gr.Button("🔄 Sesleri Yenile")
                    
                    paragraph_textboxes = []
                    for i in range(20):
                        textbox = gr.Textbox(
                            label=f"Paragraf {i}",
                            lines=3,
                            interactive=True,
                            visible=False
                        )
                        paragraph_textboxes.append(textbox)
                    
                    with gr.Row():
                        save_all_btn = gr.Button("💾 Tüm Paragrafları Kaydet", variant="primary")
                        regenerate_all_btn = gr.Button("🎵 Tüm Sesleri Yeniden Oluştur", variant="secondary")
                    
                    operation_status = gr.Textbox(label="İşlem Durumu", interactive=False, lines=2)

            # --- Create New Story Tab ---
            with gr.Tab("✨ Yeni Hikaye Oluştur"):
                with gr.Row():
                    with gr.Column(elem_classes="fably-card"):
                        gr.Markdown("#### 🎤 Sesli Sorgu")
                        voice_query = gr.Audio(
                            label="Hikaye İsteğinizi Kaydedin",
                            sources=["microphone"],
                            type="filepath"
                        )
                        transcribe_btn = gr.Button("📝 Sesi Metne Çevir")
                    with gr.Column(elem_classes="fably-card"):
                        gr.Markdown("#### ✍️ Metin Girişi")
                        transcribed_query = gr.Textbox(
                            label="Hikaye İsteği",
                            placeholder="Örnek: Uzayda yaşayan kediler hakkında bir hikaye anlat",
                            lines=3,
                            interactive=True
                        )
                with gr.Row():
                    with gr.Column(elem_classes="fably-card"):
                        gr.Markdown("#### ⚙️ Hikaye Ayarları")
                        prompt_input = gr.Textbox(
                            label="Özel Prompt (İsteğe Bağlı)",
                            placeholder="Hikayeleri daha yaratıcı yap...",
                            lines=2,
                            interactive=True
                        )
                        with gr.Row():
                            temperature_slider = gr.Slider(minimum=0.1, maximum=2.0, value=0.9, step=0.1, label="🌡️ Yaratıcılık Seviyesi")
                            max_tokens_slider = gr.Slider(minimum=500, maximum=4000, value=2000, step=100, label="📏 Maksimum Uzunluk")
                    with gr.Column(elem_classes="fably-card"):
                        gr.Markdown("#### 🎵 Ses Ayarları")
                        new_story_voice = gr.Dropdown(choices=[], label="TTS Sesi", interactive=True)
                        refresh_new_voices_btn = gr.Button("🔄 Sesleri Yenile")

                with gr.Row():
                    generate_story_btn = gr.Button("🎭 Hikaye Oluştur", variant="primary", size="lg")

                with gr.Row():
                    with gr.Column():
                        story_output = gr.Textbox(label="📚 Oluşturulan Hikaye", lines=10, interactive=False)
                    with gr.Column():
                        story_audio = gr.Audio(label="🎵 Hikaye Sesi", interactive=False)
                        convert_audio_btn = gr.Button("🎵 Sese Dönüştür")

                with gr.Row():
                    save_story_btn = gr.Button("💾 Hikayeyi Kaydet", variant="secondary")
                    new_story_status = gr.Textbox(label="Durum", interactive=False, lines=2)

            # --- Settings Tab ---
            with gr.Tab("⚙️ Ayarlar"):
                with gr.Tabs():
                    with gr.Tab("🌍 Genel Ayarlar"):
                        with gr.Row():
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### 🤖 Varsayılan AI Sağlayıcıları")
                                default_llm_provider = gr.Dropdown(choices=["openai", "gemini"], value="openai", label="Varsayılan LLM Sağlayıcısı", interactive=True)
                                default_tts_provider = gr.Dropdown(choices=["openai", "elevenlabs"], value="openai", label="Varsayılan TTS Sağlayıcısı", interactive=True)
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### 📊 Varsayılan Parametreler")
                                default_temperature = gr.Slider(minimum=0.1, maximum=2.0, value=0.9, step=0.1, label="Varsayılan Sıcaklık", interactive=True)
                                default_max_tokens = gr.Slider(minimum=500, maximum=4000, value=2000, step=100, label="Varsayılan Token Limiti", interactive=True)
                        with gr.Row():
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### 🎙️ Ses Kalitesi Ayarları")
                                noise_reduction_enabled = gr.Checkbox(label="Gürültü Azaltma", value=True, interactive=True)
                                noise_sensitivity = gr.Slider(minimum=0.1, maximum=10.0, value=2.0, step=0.1, label="Gürültü Hassasiyeti", interactive=True)
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### 🎛️ Donanım Kontrolleri")
                                wakeword_engine = gr.Dropdown(choices=["disabled", "ppn", "onnx", "tflite"], value="disabled", label="Uyandırma Kelimesi Motoru", interactive=True)
                                gpio_button_enabled = gr.Checkbox(label="GPIO Düğmesi Aktif", value=False, interactive=True)

                    with gr.Tab("🤖 OpenAI"):
                        with gr.Row():
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### OpenAI API Yapılandırması")
                                openai_api_key = gr.Textbox(label="OpenAI API Anahtarı", value=ctx.config.get("openai_api_key", ""), type="password", interactive=True)
                                openai_base_url = gr.Textbox(label="OpenAI Temel URL", value=ctx.config["openai_url"], interactive=True)
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### OpenAI Modelleri")
                                openai_llm_model_val = ctx.config["llm_model"] if "gpt" in ctx.config["llm_model"] else "gpt-4o-mini"
                                openai_llm_model = gr.Dropdown(choices=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo-preview", "gpt-3.5-turbo"], value=openai_llm_model_val, label="OpenAI LLM Modeli", interactive=True)
                                openai_tts_model = gr.Dropdown(choices=["tts-1", "tts-1-hd"], value="tts-1", label="OpenAI TTS Modeli", interactive=True)

                    with gr.Tab("ElevenLabs"):
                        with gr.Row():
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### ElevenLabs API Yapilandirmasi")
                                elevenlabs_api_key = gr.Textbox(label="ElevenLabs API Anahtari", value=ctx.config.get("elevenlabs_api_key", ""), type="password", interactive=True)
                                elevenlabs_base_url = gr.Textbox(label="ElevenLabs Temel URL", value=ctx.config["elevenlabs_url"], interactive=True)
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### ElevenLabs Ayarlari")
                                elevenlabs_model = gr.Dropdown(choices=["eleven_v3", "eleven_multilingual_v2", "eleven_flash_v2_5"], value="eleven_multilingual_v2", label="ElevenLabs Modeli", interactive=True)
                                elevenlabs_voice_select = gr.Dropdown(choices=[], label="Varsayilan ElevenLabs Sesi", interactive=True)
                                load_elevenlabs_voices_btn = gr.Button("ElevenLabs Seslerimi Yukle")
                    
                    with gr.Tab("Google Gemini"):
                        with gr.Row():
                             with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### Google Gemini Yapilandirmasi")
                                gemini_api_key = gr.Textbox(label="Gemini API Anahtari", value=ctx.config.get("gemini_api_key", ""), type="password", interactive=True)
                                gemini_base_url = gr.Textbox(label="Gemini Temel URL", value=ctx.config["gemini_url"], interactive=True)
                             with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### Gemini Modelleri")
                                gemini_model_val = ctx.config["llm_model"] if "gemini" in ctx.config["llm_model"] else "gemini-1.5-flash"
                                gemini_model = gr.Dropdown(choices=["gemini-1.5-pro", "gemini-1.5-flash"], value=gemini_model_val, label="Gemini LLM Modeli", interactive=True)

                with gr.Row():
                    save_settings_btn = gr.Button("Tum Ayarlari Kaydet", variant="primary", size="lg")
                with gr.Row():
                    settings_status = gr.Textbox(label="Ayarlar Durumu", interactive=False, lines=3)

            # --- About Tab ---
            with gr.Tab("Hakkinda"):
                gr.Markdown(
                    """
                    ### Fably - AI Hikaye Yonetim Sistemi
                    **Profesyonel AI destekli hikaye olusturma ve yonetim platformu**
                    
                    Bu kapsamli arayuz sunlari yapmaniza olanak tanir:
                    
                    #### Hikaye Kutuphanesi
                    - Mevcut hikayeleri goruntuleyin ve duzenleyin
                    - Paragraflari gercek zamanli onizleme ile duzenleyin
                    - Farkli seslerle ses dosyalarini yeniden olusturun
                    
                    #### Yeni Hikaye Olustur
                    - Sesli sorgular kaydedin veya metin girisi yapin
                    - Cesitli AI modelleri kullanarak hikayeler olusturun
                    - Hikayeleri farkli seslerle sese donusturun
                    
                    #### Ayarlar
                    - Coklu AI saglayici destegi (OpenAI, Gemini, ElevenLabs)
                    - Ses kalitesi ve donanim kontrolleri
                    - Kisisellestirilebilir varsayilanlar
                    
                    ---
                    
                    **Teknik Ozellikler:**
                    - Cocuk Guvenli: Uygun icerik filtreleri
                    - Dusuk Gecikme: Gercek zamanli hikaye uretimi
                    - Yerel Dagitim: Raspberry Pi destegi
                    - Moduler Mimari: Esnek yapilandirma
                    - Cok Dilli: Turkce ve Ingilizce destegi
                    
                    **Sistem Gereksinimleri:**
                    - Python 3.8+
                    - OpenAI/Gemini API anahtari
                    - Mikrofon ve hoparlor (ses etkilesimi icin)
                    
                    Daha fazla bilgi icin Fably GitHub deposunu ziyaret edin.
                    """,
                    visible=True
                )

        # --- Event Handlers ---
        def handle_language_change(new_language):
            ctx.update_language(new_language)
            return f"Dil degistirildi: {get_text('language_changed', new_language)}"

        def handle_story_selection(selected_story):
            if not selected_story:
                return (
                    "", 
                    "Detayları görmek için bir hikaye seçin", 
                    gr.Column(visible=False), 
                    *[gr.Textbox(visible=False) for _ in range(20)]
                )
            try:
                story_path = selected_story.split(" | ")[1]
                info, paragraphs = load_story_info(story_path)
                info_text = (
                    f"**Sorgu:** {info.get('query', 'N/A')}  \n"
                    f"**Dil:** {info.get('language', 'N/A')}  \n"
                    f"**LLM Model:** {info.get('llm_model', 'N/A')}  \n"
                    f"**TTS Sesi:** {info.get('tts_voice', 'N/A')}  \n"
                    f"**Sıcaklık:** {info.get('llm_temperature', 'N/A')}  \n"
                    f"**Paragraf Sayısı:** {len(paragraphs)}"
                )
                
                textbox_updates = []
                for i in range(20):
                    if i < len(paragraphs):
                        textbox_updates.append(gr.Textbox(value=paragraphs[i], visible=True, label=f"Paragraf {i}"))
                    else:
                        textbox_updates.append(gr.Textbox(visible=False))
                
                return story_path, info_text, gr.Column(visible=True), *textbox_updates
            except Exception as e:
                return "", f"**Hata:** {str(e)}", gr.Column(visible=False), *[gr.Textbox(visible=False) for _ in range(20)]

        def handle_transcription(audio_file):
            return transcribe_audio(audio_file)

        def handle_story_generation(query, prompt, temperature, max_tokens):
            if not query or not query.strip():
                return "❌ Lütfen bir hikaye isteği sağlayın"
            try:
                # Running async function in a sync context
                return asyncio.run(generate_story_content(query, prompt, temperature, max_tokens))
            except Exception as e:
                return f"❌ Hikaye oluşturulurken hata: {str(e)}"

        def handle_audio_synthesis(text, voice_spec):
            if not text or not text.strip():
                return None
            try:
                return asyncio.run(synthesize_with_provider(text, voice_spec))
            except Exception as e:
                print(f"TTS Hatası: {str(e)}")
                return None

        def handle_story_save(query, story, voice):
            return save_story_to_disk(query, story, voice)

        def handle_paragraph_save(story_path, *paragraph_texts):
            return batch_save_paragraphs(story_path, list(paragraph_texts))

        def handle_audio_regeneration(story_path, voice, *paragraph_texts):
            return asyncio.run(batch_regenerate_audio(story_path, voice, list(paragraph_texts)))

        def handle_settings_save(*args):
            # Placeholder for saving settings logic
            try:
                # In a real app, you would update ctx.config and save to a file
                return "✅ Ayarlar başarıyla kaydedildi!"
            except Exception as e:
                return f"❌ Ayarlar kaydedilirken hata: {str(e)}"

        def refresh_story_list():
            return gr.Dropdown(choices=[f"{name} | {path}" for name, path in get_story_list()])

        def fetch_elevenlabs_voices(api_key, base_url):
            url = f"{base_url.rstrip('/')}/voices"
            headers = {"xi-api-key": api_key}
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                voices = data.get("voices", [])
                return [(v.get("name", v.get("voice_id", "Unknown")), v.get("voice_id", "")) for v in voices]
            except Exception as e:
                return [(f"API Hatası: {str(e)}", "")]

        def handle_load_elevenlabs_voices(api_key, base_url):
            if not api_key or not base_url:
                return gr.update(choices=[], value=None, label="Varsayılan ElevenLabs Sesi", visible=True)
            voices = fetch_elevenlabs_voices(api_key, base_url)
            valid_voices = [(name, vid) for name, vid in voices if vid]
            if not valid_voices:
                return gr.update(choices=[], value=None, visible=True)
            # Doğru format: [(label, value), ...]
            return gr.update(choices=valid_voices, value=valid_voices[0][1], visible=True)

        def initialize_voice_dropdowns():
            voice_options = asyncio.run(get_available_voices())
            current_voice_spec = f"{ctx.config['tts_provider']}:{ctx.config['tts_voice']}"
            default_value = None
            for _, value in voice_options:
                if value == current_voice_spec:
                    default_value = value
                    break
            if not default_value and voice_options:
                default_value = voice_options[0][1]
            return gr.Dropdown(choices=voice_options, value=default_value)

        # --- Connect Components to Functions ---
        
        # General
        language_selector.change(
            fn=handle_language_change,
            inputs=[language_selector],
            outputs=[settings_status]
        )

        # Story Library Tab
        story_dropdown.change(
            fn=handle_story_selection,
            inputs=[story_dropdown],
            outputs=[selected_story_path, story_info_display, paragraph_editor, *paragraph_textboxes]
        )
        refresh_list_btn.click(fn=refresh_story_list, outputs=[story_dropdown])
        save_all_btn.click(
            fn=handle_paragraph_save,
            inputs=[selected_story_path, *paragraph_textboxes],
            outputs=[operation_status]
        )
        regenerate_all_btn.click(
            fn=handle_audio_regeneration,
            inputs=[selected_story_path, voice_select, *paragraph_textboxes],
            outputs=[operation_status]
        )
        refresh_voices_btn.click(fn=refresh_voices, outputs=[voice_select])

        # Create New Story Tab
        transcribe_btn.click(
            fn=handle_transcription,
            inputs=[voice_query],
            outputs=[transcribed_query]
        )
        generate_story_btn.click(
            fn=handle_story_generation,
            inputs=[transcribed_query, prompt_input, temperature_slider, max_tokens_slider],
            outputs=[story_output]
        )
        convert_audio_btn.click(
            fn=handle_audio_synthesis,
            inputs=[story_output, new_story_voice],
            outputs=[story_audio]
        )
        save_story_btn.click(
            fn=handle_story_save,
            inputs=[transcribed_query, story_output, new_story_voice],
            outputs=[new_story_status]
        )
        refresh_new_voices_btn.click(fn=refresh_voices, outputs=[new_story_voice])

        # Settings Tab
        settings_inputs = [
            openai_api_key, openai_base_url, openai_llm_model, openai_tts_model,
            elevenlabs_api_key, elevenlabs_base_url, elevenlabs_model,
            gemini_api_key, gemini_base_url, gemini_model,
            default_llm_provider, default_tts_provider,
            default_temperature, default_max_tokens,
            noise_reduction_enabled, noise_sensitivity,
            wakeword_engine, gpio_button_enabled
        ]
        save_settings_btn.click(
            fn=handle_settings_save,
            inputs=settings_inputs,
            outputs=[settings_status]
        )

        # ElevenLabs voices button handler
        load_elevenlabs_voices_btn.click(
            fn=handle_load_elevenlabs_voices,
            inputs=[elevenlabs_api_key, elevenlabs_base_url],
            outputs=[elevenlabs_voice_select]
        )

        # Initial loading actions
        app.load(
            fn=lambda: (initialize_voice_dropdowns(), initialize_voice_dropdowns()),
            outputs=[voice_select, new_story_voice]
        )

        return app


def main():
    """Entry point for launching the Fably web interface from other modules."""
    fably_app = create_fably_interface()
    fably_app.launch(server_name="0.0.0.0", server_port=7860)


# --- Main execution block ---
if __name__ == "__main__":
    # Create the Gradio interface
    fably_app = create_fably_interface()
    
    # Launch the web server
    fably_app.launch(server_name="0.0.0.0", server_port=7860)