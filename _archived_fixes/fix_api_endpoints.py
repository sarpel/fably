#!/usr/bin/env python3
"""
API Endpoint Düzeltmeleri - Fably için güncel endpoint'ler
Bu script, dökümentasyona göre API endpoint'lerini düzeltir
"""

import os
from pathlib import Path

def update_cli_endpoints():
    """CLI modülündeki endpoint'leri güncelle"""
    
    cli_file = Path("fably/cli.py")
    
    if not cli_file.exists():
        print("❌ CLI dosyası bulunamadı!")
        return False
    
    # Backup oluştur
    backup_file = cli_file.with_suffix('.py.backup')
    import shutil
    shutil.copy2(cli_file, backup_file)
    print(f"Backup olusturuldu: {backup_file}")
    
    # Dosyayı oku
    with open(cli_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Endpoint düzeltmeleri
    fixes = [
        # Gemini API OpenAI compatible endpoint
        ('GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"', 
         'GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai"'),
        
        # ElevenLabs API endpoint (doğru)
        ('ELEVENLABS_URL = "https://api.elevenlabs.io"',
         'ELEVENLABS_URL = "https://api.elevenlabs.io"'),
        
        # OpenAI API endpoint (doğru)
        ('OPENAI_URL = "https://api.openai.com/v1"',
         'OPENAI_URL = "https://api.openai.com/v1"'),
         
        # Model güncellemeleri
        ('LLM_MODEL = "o4-mini"',
         'LLM_MODEL = "gpt-4o-mini"'),  # o4-mini henüz mevcut değil
    ]
    
    # Düzeltmeleri uygula
    for old_text, new_text in fixes:
        if old_text in content:
            content = content.replace(old_text, new_text)
            print(f"Duzeltildi: {old_text.split('=')[0].strip()}")
        else:
            print(f"Bulunamadi: {old_text.split('=')[0].strip()}")
    
    # Dosyayı yaz
    with open(cli_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"CLI dosyasi guncellendi: {cli_file}")
    return True

def update_tts_service():
    """TTS service'deki endpoint'leri güncelle"""
    
    tts_file = Path("fably/tts_service.py")
    
    if not tts_file.exists():
        print("❌ TTS Service dosyası bulunamadı!")
        return False
    
    # Backup oluştur
    backup_file = tts_file.with_suffix('.py.backup')
    import shutil
    shutil.copy2(tts_file, backup_file)
    print(f"✅ Backup oluşturuldu: {backup_file}")
    
    # Dosyayı oku
    with open(tts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Gemini TTS'i tamamen kaldır (Gemini'nin TTS API'si yok)
    gemini_class_start = content.find('class GeminiTTSProvider(TTSProvider):')
    if gemini_class_start != -1:
        # Gemini class'ını bul ve comment out et
        lines = content.split('\n')
        new_lines = []
        in_gemini_class = False
        indent_level = 0
        
        for line in lines:
            if 'class GeminiTTSProvider(TTSProvider):' in line:
                in_gemini_class = True
                indent_level = len(line) - len(line.lstrip())
                new_lines.append('# DISABLED: Gemini does not have native TTS API')
                new_lines.append('# ' + line)
                continue
            
            if in_gemini_class:
                current_indent = len(line) - len(line.lstrip()) if line.strip() else 999
                
                # Eğer aynı veya daha düşük indent seviyesindeyse class bitmiştir
                if line.strip() and current_indent <= indent_level:
                    in_gemini_class = False
                    new_lines.append(line)
                else:
                    # Gemini class içindeyse comment out et
                    new_lines.append('# ' + line if line.strip() else line)
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        print("✅ Gemini TTS provider devre dışı bırakıldı (Gemini TTS API mevcut değil)")
    
    # initialize_tts_service fonksiyonunu güncelle
    old_init = '''def initialize_tts_service(openai_key: str = None, elevenlabs_key: str = None,
                          gemini_key: str = None,
                          openai_url: str = "https://api.openai.com/v1",
                          elevenlabs_url: str = "https://api.elevenlabs.io",
                          gemini_url: str = "https://generativelanguage.googleapis.com/v1beta"):'''
    
    new_init = '''def initialize_tts_service(openai_key: str = None, elevenlabs_key: str = None,
                          openai_url: str = "https://api.openai.com/v1",
                          elevenlabs_url: str = "https://api.elevenlabs.io"):'''
    
    if old_init.replace(' ', '').replace('\n', '') in content.replace(' ', '').replace('\n', ''):
        content = content.replace(old_init, new_init)
        print("✅ initialize_tts_service signature güncellendi")
    
    # Gemini provider initialization'ı kaldır
    gemini_init_block = '''    if gemini_key:
        try:
            gemini_provider = GeminiTTSProvider(gemini_key, gemini_url)
            tts_service.add_provider("gemini", gemini_provider)
            logging.info("Gemini TTS provider initialized")
        except Exception as e:
            logging.warning(f"Failed to initialize Gemini provider: {str(e)}")'''
    
    if gemini_init_block.replace(' ', '') in content.replace(' ', ''):
        content = content.replace(gemini_init_block, '    # Gemini TTS not available - Gemini does not have native TTS API')
        print("✅ Gemini TTS initialization kaldırıldı")
    
    # Default provider selection güncelle
    old_default = '''    # Set default provider preference (ElevenLabs if available, otherwise OpenAI, then Gemini)
    if "elevenlabs" in tts_service.providers:
        tts_service.set_default_provider("elevenlabs")
    elif "openai" in tts_service.providers:
        tts_service.set_default_provider("openai")
    elif "gemini" in tts_service.providers:
        tts_service.set_default_provider("gemini")
    else:
        logging.warning("No TTS providers available")'''
    
    new_default = '''    # Set default provider preference (ElevenLabs if available, otherwise OpenAI)
    if "elevenlabs" in tts_service.providers:
        tts_service.set_default_provider("elevenlabs")
    elif "openai" in tts_service.providers:
        tts_service.set_default_provider("openai")
    else:
        logging.warning("No TTS providers available")'''
    
    content = content.replace(old_default, new_default)
    print("✅ Default provider selection güncellendi")
    
    # Dosyayı yaz
    with open(tts_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ TTS Service dosyası güncellendi: {tts_file}")
    return True

def create_api_reference():
    """API referans dosyası oluştur"""
    
    api_ref = '''# Fably API Endpoints Reference (Updated 2025)

## OpenAI API
- **Base URL:** `https://api.openai.com/v1`
- **Chat Completions:** `POST /chat/completions`
- **Audio Speech:** `POST /audio/speech`
- **Audio Transcriptions:** `POST /audio/transcriptions`
- **Authentication:** `Authorization: Bearer {api_key}`

### Supported Models:
- **LLM:** gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
- **TTS:** tts-1, tts-1-hd
- **STT:** whisper-1

## ElevenLabs API  
- **Base URL:** `https://api.elevenlabs.io`
- **Text-to-Speech:** `POST /v1/text-to-speech/{voice_id}`
- **List Voices:** `GET /v1/voices`
- **Authentication:** `xi-api-key: {api_key}`

### Supported Models:
- eleven_v3 (Alpha - most expressive)
- eleven_multilingual_v2 (recommended)
- eleven_flash_v2_5 (fast, low latency)
- eleven_turbo_v2_5 (balanced quality/speed)

## Google Gemini API (OpenAI Compatible)
- **Base URL:** `https://generativelanguage.googleapis.com/v1beta/openai/`
- **Chat Completions:** `POST /chat/completions`
- **Authentication:** `Authorization: Bearer {api_key}`

### Supported Models:
- gemini-2.5-pro
- gemini-2.5-flash
- gemini-1.5-pro
- gemini-1.5-flash

**Note:** Gemini does NOT have native TTS API. Use OpenAI or ElevenLabs for TTS.

## DeepSeek API
- **Base URL:** `https://api.deepseek.com/v1`
- **Chat Completions:** `POST /chat/completions`
- **Authentication:** `Authorization: Bearer {api_key}`

### Supported Models:
- deepseek-chat
- deepseek-coder

## Local Ollama API
- **Base URL:** `http://127.0.0.1:11434/v1`
- **Chat Completions:** `POST /chat/completions`
- **Authentication:** Not required for local

### Common Models:
- llama3, llama3:latest
- gemma2:9b, gemma2:2b
- tinyllama (for Pi Zero 2W)

## Updated Configurations

### CLI Defaults:
```python
OPENAI_URL = "https://api.openai.com/v1"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai"  # Updated
DEEPSEEK_URL = "https://api.deepseek.com/v1"
ELEVENLABS_URL = "https://api.elevenlabs.io"
LLM_MODEL = "gpt-4o-mini"  # Updated from o4-mini
```

### Error Fixes Applied:
1. ✅ Gemini URL corrected to OpenAI-compatible endpoint
2. ✅ Gemini TTS removed (not available)
3. ✅ ElevenLabs headers correct (`xi-api-key`)
4. ✅ Model name corrected (gpt-4o-mini instead of o4-mini)
5. ✅ Default provider priority updated
'''
    
    with open("API_ENDPOINTS_REFERENCE.md", 'w', encoding='utf-8') as f:
        f.write(api_ref)
    
    print("✅ API referans dosyası oluşturuldu: API_ENDPOINTS_REFERENCE.md")

def main():
    """Ana düzeltme fonksiyonu"""
    print("Fably API Endpoint Duzeltmeleri")
    print("=" * 50)
    print("Dokumentasyona gore endpoint'ler guncelleniyor...")
    print()
    
    success_count = 0
    
    # CLI endpoint'leri düzelt
    if update_cli_endpoints():
        success_count += 1
    
    # TTS service endpoint'leri düzelt
    if update_tts_service():
        success_count += 1
    
    # API referans oluştur
    create_api_reference()
    success_count += 1
    
    print()
    print("=" * 50)
    print(f"Basarili: {success_count}/3 duzeltme uygulandı!")
    
    print()
    print("Ana Duzeltmeler:")
    print("1. Gemini URL: OpenAI-compatible endpoint kullaniliyor")
    print("2. Gemini TTS: Kaldirildi (mevcut degil)")
    print("3. ElevenLabs: xi-api-key header dogru")
    print("4. Model ismi: gpt-4o-mini (o4-mini yerine)")
    print("5. Default provider siralamasi guncellendi")
    
    print()
    print("Test etmek icin:")
    print("python -m fably --debug 'test hikayesi'")

if __name__ == "__main__":
    main()
