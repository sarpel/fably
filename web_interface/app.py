#!/usr/bin/env python3

# --- Import necessary libraries ---
import asyncio
import os
import sys
import yaml
import gradio as gr
from pathlib import Path
import json
from typing import List, Tuple, Optional, Dict, Any
from gradio.themes import Soft
import requests

# Add the parent directory to the system path to allow for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

CONFIG_FILE = "config.yaml"

class FablyWebContext:
    """
    Manages the application's configuration and current state, like language.
    """
    def __init__(self):
        self.config = self.load_config()
        self.current_language = "tr"  # Default language

    def load_config(self) -> Dict[str, Any]:
        """
        Loads configuration from config.yaml or sets fallback values.
        """
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or self.load_default_config()
            except Exception:
                return self.load_default_config()
        else:
            return self.load_default_config()

    def save_config(self):
        """
        Saves the current configuration to config.yaml.
        """
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.config, f)
        except Exception as e:
            print(f"Config kaydedilemedi: {e}")

    def load_default_config(self) -> Dict[str, Any]:
        """
        Loads default settings from environment variables or sets fallback values.
        """
        return {
            "llm_model": "gemini-2.5-flash-lite",
            "tts_provider": "elevenlabs",
            "tts_voice": "rachel",
            "elevenlabs_api_key": os.getenv("ELEVENLABS_API_KEY", ""),
            "elevenlabs_url": "https://api.elevenlabs.io/v1",
            "elevenlabs_model": "eleven_multilingual_v2",
            "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
            "gemini_url": "https://generativelanguage.googleapis.com/v1beta",
            "llm_temperature": 1.0,
            "max_tokens": 4000,
            "gpio_button": True,
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
    if ctx.config.get("elevenlabs_api_key"):
        elevenlabs_voices = ["rachel", "adam", "arnold", "josh", "sam"]
        for voice in elevenlabs_voices:
            voices.append((f"ElevenLabs: {voice.title()}", f"elevenlabs:{voice}"))
    return voices


# --- Core Logic Functions ---
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


# --- Add value-based story metadata and listening history ---
STORY_VALUES = [
    "Dürüstlük", "Yardımlaşma", "Sabır", "Cesaret", "Nezaket", "Paylaşmak", "Sorumluluk", "Empati", "Adalet", "Özgüven",
    "Çalışkanlık", "Saygı", "Hoşgörü", "Merhamet", "Azim", "Dostluk", "Vefa", "Cömertlik", "Alçakgönüllülük", "Sevgi"
]

# Simulated story metadata (in real use, load from info.yaml or DB)
DEFAULT_STORIES = [
    {
        "title": f"{value} Hikayesi",
        "filename": f"story_{i+1}.mp3",
        "value": value,
        "summary": f"Bu hikaye çocuklara {value.lower()} değerini öğretir.",
        "paragraphs": 5
    }
    for i, value in enumerate(STORY_VALUES)
]

# Session-based listening history
LISTENED_STORIES = set()

# --- Add replay and audio format settings ---
REPLAY_ALLOWED = True  # Default: allow replay (can be toggled in UI)
AUDIO_FORMAT = "wav"   # Default: WAV for RPi Zero 2W compatibility

# In the UI, add:
# - Checkbox: "Hikayeler tekrar dinlenebilsin" (REPLAY_ALLOWED)
# - Dropdown: "Ses formatı" (AUDIO_FORMAT, options: wav, mp3, ogg)

# Update get_value_filtered_stories to use REPLAY_ALLOWED
def get_value_filtered_stories(selected_value=None, only_unheard=True):
    filtered = [s for s in DEFAULT_STORIES if (not selected_value or s["value"] == selected_value)]
    if only_unheard and not REPLAY_ALLOWED:
        filtered = [s for s in filtered if s["filename"] not in LISTENED_STORIES]
    return filtered


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
        title="🎭 Sarpy - AI Hikaye Yönetim Sistemi",
        theme=Soft(),
        css=custom_css
    ) as app:
        # --- Header and Language Selector ---
        with gr.Row():
            gr.HTML("""
            <div class="fably-header">
                <h1>🎭 Sarpy - Profesyonel AI Hikaye Sistemi</h1>
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
                    # Remove the microphone/audio input column and button
                    # with gr.Column(elem_classes="fably-card"):
                    #     gr.Markdown("#### 🎤 Sesli Sorgu")
                    #     voice_query = gr.Audio(
                    #         label="Hikaye İsteğinizi Kaydedin",
                    #         sources=["microphone"],
                    #         type="filepath"
                    #     )
                    #     transcribe_btn = gr.Button("📝 Sesi Metne Çevir")
                    with gr.Column(elem_classes="fably-card"):
                        gr.Markdown("#### ✍️ Masal İsteği")
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
                            value="Sarpy İçin Sistem Prompt'u\nSen, 5 yaşındaki çocuklar için harika masallar anlatan sihirli bir masalcı olan Sarpy'sin. Senin görevin, çocukları hayal gücüyle mutlu etmek.\n\nMASAL OLUŞTURMA KURALLARI:\n\nDil ve Üslup:\n\nMasallarını her zaman 5 yaşındaki bir çocuğun anlayabileceği basit, akıcı ve net bir Türkçe ile anlat.\n\nDilin sıcak, arkadaş canlısı ve ilgi çekici olsun.\n\nYapı ve İçerik:\n\nKullanıcı senden ne tür bir masal isterse istesin, 5-6 paragraftan oluşan, sürükleyici bir masal oluştur.\n\nMasalların her zaman yaşa uygun, hayal gücü geniş ve pozitif mesajlar içermelidir.\n\nHikayelerin net bir başlangıcı, gelişmesi ve sonu olmalıdır.\n\nİçerisinde sevimli karakterler ve basit maceralar barındırsın.\n\nKonu İşleme:\n\nHayvanlar, uzay, prensesler, robotlar veya günlük maceralar gibi her türlü masal talebini kabul et.\n\nEğer istek belirsiz ise, sihirli ve eğlenceli bir masal yarat.\n\nMASAL DEVAM ETTİRME:\n\nEğer mevcut bir masalı devam ettiriyorsan, şu kurallara uymalısın:\n\nÖnceki bölümdeki karakterlere, mekana ve atmosfere sadık kal.\n\nHikayenin kaldığı yerden doğal bir şekilde devam et.\n\nAnlatım tarzını ve sesini koru.\n\nÖnceki olayların üzerine inşa ederek hikayeyi ilgi çekici bir şekilde ilerlet.\n\nMASAL DIŞI TALEPLER:\n\nEğer kullanıcı masal dışında bir soru sorarsa (\"Nasılsın?\", \"Hava nasıl?\" gibi), onu nazikçe masal istemeye yönlendir.\n\nÖrnek: \"Ben hep hikaye anlatmaya hazırım! Hangi konuda hikaye istersin?\"\n\nÖrnek: \"Hava hikayeleri çok güzel! Bulutlar, yağmur ya da güneş hakkında hikaye istersen anlatabilirim!\"\n\nUnutma, senin varoluş amacın masallar anlatmak ve çocukları mutlu etmek!",
                            lines=2,
                            interactive=True
                        )
                        with gr.Row():
                            temperature_slider = gr.Slider(minimum=0.1, maximum=2.0, value=ctx.config.get("llm_temperature", 1.0), step=0.1, label="🌡️ Yaratıcılık Seviyesi")
                            max_tokens_slider = gr.Slider(minimum=500, maximum=4000, value=ctx.config.get("max_tokens", 4000), step=100, label="📏 Maksimum Uzunluk")
                    with gr.Column(elem_classes="fably-card"):
                        gr.Markdown("#### 🎵 Ses Ayarları")
                        new_story_voice = gr.Dropdown(choices=[], label="TTS Sesi", interactive=True, value=ctx.config.get("tts_voice", "rachel"), allow_custom_value=True)

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
                                default_llm_provider = gr.Dropdown(choices=["gemini"], value="gemini", label="Varsayılan LLM Sağlayıcısı", interactive=True)
                                default_tts_provider = gr.Dropdown(choices=["elevenlabs"], value="elevenlabs", label="Varsayılan TTS Sağlayıcısı", interactive=True)
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### 📊 Varsayılan Parametreler")
                                default_temperature = gr.Slider(minimum=0.1, maximum=2.0, value=ctx.config.get("llm_temperature", 1.0), step=0.1, label="Varsayılan Sıcaklık", interactive=True)
                                default_max_tokens = gr.Slider(minimum=500, maximum=4000, value=ctx.config.get("max_tokens", 4000), step=100, label="Varsayılan Token Limiti", interactive=True)
                        with gr.Row():
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### 🎙️ Ses Kalitesi Ayarları")
                                noise_reduction_enabled = gr.Checkbox(label="Gürültü Azaltma", value=ctx.config.get("noise_reduction", True), interactive=True)
                                noise_sensitivity = gr.Slider(minimum=0.1, maximum=10.0, value=ctx.config.get("noise_sensitivity", 2.0), step=0.1, label="Gürültü Hassasiyeti", interactive=True)
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### 🎛️ Donanım Kontrolleri")
                                gpio_button_enabled = gr.Checkbox(label="GPIO Düğmesi Aktif", value=ctx.config.get("gpio_button", True), interactive=True)

                    with gr.Tab("ElevenLabs"):
                        with gr.Row():
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### ElevenLabs API Yapilandirmasi")
                                elevenlabs_api_key = gr.Textbox(label="ElevenLabs API Anahtari", value=ctx.config.get("elevenlabs_api_key", ""), type="password", interactive=True)
                                elevenlabs_base_url = gr.Textbox(label="ElevenLabs Temel URL", value=ctx.config["elevenlabs_url"], interactive=True)
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### ElevenLabs Ayarlari")
                                elevenlabs_voice_select = gr.Dropdown(choices=[], label="Varsayilan ElevenLabs Sesi", interactive=True)
                                elevenlabs_voice_status = gr.Textbox(label="Ses Yükleme Durumu", interactive=False)
                                load_elevenlabs_voices_btn = gr.Button("ElevenLabs Seslerimi Yukle")
                    
                    with gr.Tab("Google Gemini"):
                        with gr.Row():
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### Google Gemini Yapilandirmasi")
                                gemini_api_key = gr.Textbox(label="Gemini API Anahtari", value=ctx.config.get("gemini_api_key", ""), type="password", interactive=True)
                                gemini_base_url = gr.Textbox(label="Gemini Temel URL", value=ctx.config["gemini_url"], interactive=True)
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### Gemini Modelleri")
                                gemini_model_val = ctx.config["llm_model"] if "gemini" in ctx.config["llm_model"] else "gemini-2.5-flash-lite"
                                gemini_model = gr.Dropdown(
                                    choices=[
                                        "gemini-2.5-flash-lite",
                                        "gemini-2.5-flash",
                                        "gemini-2.5-pro"
                                    ],
                                    value=gemini_model_val,
                                    label="Gemini LLM Modeli (Stable)",
                                    interactive=True
                                )

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

            # --- Story Management Tab ---
            with gr.Tab("🛠️ Masal Yönetimi"):
                with gr.Row():
                    with gr.Column(scale=2, elem_classes="fably-card"):
                        gr.Markdown("#### Masal Listesi ve Yönetimi")
                        story_table = gr.Dataframe(headers=["Başlık", "Okundu", "Sıra", "Etiketler", "Yaş Grubu", "Klasör"], datatype=["str", "bool", "number", "str", "str", "str"], interactive=True)
                        filter_text = gr.Textbox(label="Başlık/Etiket Ara", placeholder="Ara...", interactive=True)
                        filter_read = gr.Checkbox(label="Sadece Okunmamışları Göster", value=False)
                        refresh_mgmt_btn = gr.Button("🔄 Listeyi Yenile")
                    with gr.Column(scale=1, elem_classes="fably-card"):
                        gr.Markdown("#### Masal Ekle/Düzenle")
                        story_title = gr.Textbox(label="Başlık", interactive=True)
                        story_desc = gr.Textbox(label="Açıklama", interactive=True)
                        story_age = gr.Textbox(label="Yaş Grubu", interactive=True)
                        story_tags = gr.Textbox(label="Etiketler (virgülle)", interactive=True)
                        story_order = gr.Number(label="Sıra", interactive=True)
                        story_read = gr.Checkbox(label="Okundu", value=False)
                        story_folder = gr.Textbox(label="Klasör Adı", interactive=True)
                        add_btn = gr.Button("➕ Ekle")
                        edit_btn = gr.Button("✏️ Güncelle")
                        delete_btn = gr.Button("🗑️ Sil")
                        reset_read_btn = gr.Button("🔄 Okundu Flagini Sıfırla")
                        archive_btn = gr.Button("📦 Arşivle/Geri Al")
                        import_btn = gr.Button("⬆️ İçe Aktar")
                        export_btn = gr.Button("⬇️ Dışa Aktar")
                        mgmt_status = gr.Textbox(label="Durum", interactive=False, lines=2)
                        import_json = gr.Textbox(label="İçe Aktarılacak JSON", lines=4, interactive=True)
                        export_json = gr.Textbox(label="Dışa Aktarılan JSON", lines=4, interactive=False)

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

        # Remove transcribe_btn click handler and handle_transcription references
        # transcribe_btn.click(
        #     fn=handle_transcription,
        #     inputs=[voice_query],
        #     outputs=[transcribed_query]
        # )

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
            try:
                path = save_story_to_disk(query, story, voice)
                return f"✅ Hikaye kaydedildi: {path}"
            except Exception as e:
                return f"❌ Hikaye kaydedilemedi: {str(e)}"

        def handle_paragraph_save(story_path, *paragraph_texts):
            try:
                count = batch_save_paragraphs(story_path, list(paragraph_texts))
                return f"✅ {count} paragraf kaydedildi."
            except Exception as e:
                return f"❌ Paragraflar kaydedilemedi: {str(e)}"

        def handle_audio_regeneration(story_path, voice, *paragraph_texts):
            try:
                result = asyncio.run(batch_regenerate_audio(story_path, voice, list(paragraph_texts)))
                return f"✅ Sesler yeniden oluşturuldu: {result}"
            except Exception as e:
                return f"❌ Sesler oluşturulamadı: {str(e)}"

        def handle_settings_save(*args):
            try:
                # args sırası settings_inputs ile aynı olmalı
                keys = [
                    "llm_model", "tts_model",
                    "elevenlabs_api_key", "elevenlabs_url", "elevenlabs_model",
                    "gemini_api_key", "gemini_url", "gemini_model",
                    "llm_provider", "tts_provider",
                    "llm_temperature", "max_tokens",
                    "noise_reduction", "noise_sensitivity",
                    "gpio_button"
                ]
                for k, v in zip(keys, args):
                    ctx.config[k] = v
                ctx.save_config()
                return "✅ Ayarlar başarıyla kaydedildi ve config.yaml dosyasına yazıldı!"
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
                return gr.update(choices=[], value=None, label="Varsayılan ElevenLabs Sesi", visible=True), "❌ API anahtarı veya URL eksik."
            voices = fetch_elevenlabs_voices(api_key, base_url)
            valid_voices = [(name, vid) for name, vid in voices if vid]
            if not valid_voices:
                return gr.update(choices=[], value=None, visible=True), "❌ Ses bulunamadı."
            return gr.update(choices=valid_voices, value=valid_voices[0][1], visible=True), f"✅ {len(valid_voices)} ElevenLabs sesi yüklendi."

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

        def list_stories_for_mgmt(filter_text=None, only_unread=False):
            stories_dir = ensure_stories_directory()
            rows = []
            for story_dir in sorted(stories_dir.iterdir()):
                if story_dir.is_dir():
                    info_path = story_dir / "story_info.json"
                    info = {}
                    if info_path.exists():
                        try:
                            with open(info_path, "r", encoding="utf-8") as f:
                                info = json.load(f)
                        except Exception:
                            info = {}
                    title = info.get("title") or info.get("query") or story_dir.name
                    desc = info.get("desc", "")
                    age = info.get("age", "")
                    tags = ", ".join(info.get("tags", [])) if isinstance(info.get("tags"), list) else info.get("tags", "")
                    order = info.get("order", 0)
                    read = info.get("read", False)
                    archived = info.get("archived", False)
                    if only_unread and read:
                        continue
                    if filter_text and filter_text.lower() not in title.lower() and filter_text.lower() not in tags.lower():
                        continue
                    rows.append([title, read, order, tags, age, story_dir.name])
            return sorted(rows, key=lambda x: x[2])

        def add_story(title, desc, age, tags, order, folder):
            stories_dir = ensure_stories_directory()
            story_dir = stories_dir / folder
            if story_dir.exists():
                return False, "Bu klasör zaten var."
            story_dir.mkdir()
            info = {"title": title, "desc": desc, "age": age, "tags": [t.strip() for t in tags.split(",") if t.strip()], "order": order, "read": False, "archived": False}
            with open(story_dir / "story_info.json", "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            return True, "Masal eklendi."

        def edit_story(folder, title, desc, age, tags, order, read):
            stories_dir = ensure_stories_directory()
            story_dir = stories_dir / folder
            info_path = story_dir / "story_info.json"
            if not story_dir.exists() or not info_path.exists():
                return False, "Masal bulunamadı."
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            info.update({"title": title, "desc": desc, "age": age, "tags": [t.strip() for t in tags.split(",") if t.strip()], "order": order, "read": read})
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            return True, "Masal güncellendi."

        def delete_story(folder):
            stories_dir = ensure_stories_directory()
            story_dir = stories_dir / folder
            if not story_dir.exists():
                return False, "Masal bulunamadı."
            for item in story_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    import shutil
                    shutil.rmtree(item)
            story_dir.rmdir()
            return True, "Masal silindi."

        def set_story_read_flag(folder, read):
            stories_dir = ensure_stories_directory()
            story_dir = stories_dir / folder
            info_path = story_dir / "story_info.json"
            if not info_path.exists():
                return False, "Masal bulunamadı."
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            info["read"] = read
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            return True, "Okundu flag'i güncellendi."

        def archive_story(folder, archive=True):
            stories_dir = ensure_stories_directory()
            story_dir = stories_dir / folder
            info_path = story_dir / "story_info.json"
            if not info_path.exists():
                return False, "Masal bulunamadı."
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            info["archived"] = archive
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            return True, "Arşiv durumu güncellendi."

        def import_story(json_str):
            try:
                data = json.loads(json_str)
                folder = data.get("folder") or data.get("title")
                return add_story(data.get("title"), data.get("desc", ""), data.get("age", ""), ",".join(data.get("tags", [])), data.get("order", 0), folder)
            except Exception as e:
                return False, f"İçe aktarma hatası: {str(e)}"

        def export_story(folder):
            stories_dir = ensure_stories_directory()
            story_dir = stories_dir / folder
            info_path = story_dir / "story_info.json"
            if not info_path.exists():
                return False, "Masal bulunamadı."
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            info["folder"] = folder
            return True, json.dumps(info, ensure_ascii=False, indent=2)

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

        # Settings Tab
        settings_inputs = [
            gemini_model,
            elevenlabs_api_key, elevenlabs_base_url,
            gemini_api_key, gemini_base_url, gemini_model,
            default_llm_provider, default_tts_provider,
            default_temperature, default_max_tokens,
            noise_reduction_enabled, noise_sensitivity,
            gpio_button_enabled
        ]
        save_settings_btn.click(
            fn=handle_settings_save,
            inputs=settings_inputs,
            outputs=[settings_status]
        )
        # After saving settings, also update the new_story_voice dropdown to reflect the new default TTS model/voice
        save_settings_btn.click(
            fn=initialize_voice_dropdowns,
            outputs=[new_story_voice]
        )

        # ElevenLabs voices button handler
        load_elevenlabs_voices_btn.click(
            fn=handle_load_elevenlabs_voices,
            inputs=[elevenlabs_api_key, elevenlabs_base_url],
            outputs=[elevenlabs_voice_select, elevenlabs_voice_status]
        )
        # Also update new_story_voice dropdown when voices are loaded
        load_elevenlabs_voices_btn.click(
            fn=initialize_voice_dropdowns,
            outputs=[new_story_voice]
        )

        # Story Management Tab
        refresh_mgmt_btn.click(fn=list_stories_for_mgmt, outputs=[story_table])
        filter_text.change(fn=list_stories_for_mgmt, inputs=[filter_text, filter_read], outputs=[story_table])
        filter_read.change(fn=list_stories_for_mgmt, inputs=[filter_text, filter_read], outputs=[story_table])
        add_btn.click(fn=add_story, inputs=[story_title, story_desc, story_age, story_tags, story_order, story_folder], outputs=[mgmt_status])
        edit_btn.click(fn=edit_story, inputs=[story_folder, story_title, story_desc, story_age, story_tags, story_order, story_read], outputs=[mgmt_status])
        delete_btn.click(fn=delete_story, inputs=[story_folder], outputs=[mgmt_status])
        reset_read_btn.click(lambda folder: set_story_read_flag(folder, False), inputs=[story_folder], outputs=[mgmt_status])
        archive_btn.click(fn=archive_story, inputs=[story_folder], outputs=[mgmt_status])
        import_btn.click(fn=import_story, inputs=[import_json], outputs=[mgmt_status])
        export_btn.click(lambda folder: export_story(folder)[1] if export_story(folder)[0] else export_story(folder)[1], inputs=[story_folder], outputs=[export_json])

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