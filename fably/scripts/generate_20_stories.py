import os
import yaml
import requests
from pathlib import Path
from dotenv import load_dotenv

STORY_VALUES = [
    "Dürüstlük", "Yardımlaşma", "Sabır", "Cesaret", "Nezaket", "Paylaşmak", "Sorumluluk", "Empati", "Adalet", "Özgüven",
    "Çalışkanlık", "Saygı", "Hoşgörü", "Merhamet", "Azim", "Dostluk", "Vefa", "Cömertlik", "Alçakgönüllülük", "Sevgi"
]

STORIES_DIR = Path("fably/stories")
STORIES_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(dotenv_path=Path(".env"))
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_VOICE_ID = "xsGHrtxT5AdDzYXTQT0d"  # Gönül Filiz
ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{}"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={}"

WAV_SAMPLE_RATE = 16000
WAV_FORMAT = "wav"

# Helper: Generate story text with Gemini
def generate_story_text(value):
    prompt = f"Çocuklara {value.lower()} değerini öğreten, 5-7 yaşa uygun, 5 paragraflık kısa bir hikaye yaz. Her paragrafı ayrı başlıkla belirt."
    if GEMINI_API_KEY:
        try:
            response = requests.post(
                GEMINI_URL.format(GEMINI_API_KEY),
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text
        except Exception as e:
            print(f"Gemini API error: {e}")
    # Fallback
    return f"Bir zamanlar {value.lower()} değerini öğrenen bir çocuk vardı... (örnek hikaye)"

# Helper: Synthesize story to WAV with ElevenLabs
def synthesize_to_wav(text, out_path):
    url = ELEVENLABS_URL.format(ELEVENLABS_VOICE_ID)
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Accept": "audio/wav",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(r.content)
        return True
    else:
        print(f"TTS error: {r.status_code} {r.text}")
        return False

for i, value in enumerate(STORY_VALUES):
    story_dir = STORIES_DIR / f"story_{i+1}"
    story_dir.mkdir(exist_ok=True)
    print(f"[{i+1}/20] {value} hikayesi üretiliyor...")
    story_text = generate_story_text(value)
    wav_path = story_dir / "story.wav"
    ok = synthesize_to_wav(story_text, wav_path)
    info = {
        "title": f"{value} Hikayesi",
        "value": value,
        "summary": f"Bu hikaye çocuklara {value.lower()} değerini öğretir.",
        "paragraphs": 5
    }
    with open(story_dir / "info.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(info, f, allow_unicode=True)
    if ok:
        print(f"  ✔ {wav_path} kaydedildi.")
    else:
        print(f"  ✖ {wav_path} üretilemedi!") 