#!/bin/bash

# Turkish Sound Generation Script for Fably
# This script generates Turkish audio files for all system sounds

DEST="./fably/sounds"
VOICE="nova"  # OpenAI voice

# Ensure the sounds directory exists
mkdir -p "$DEST"

echo "Generating Turkish sound files for Fably..."

# Create Turkish text files first
cat > "$DEST/hi_text.txt" << 'EOF'
Merhaba! Ben Fably! Senin hikaye arkadaşınım!
EOF

cat > "$DEST/hi_short_text.txt" << 'EOF'
Merhaba! Ben Fably!
EOF

cat > "$DEST/instructions_text.txt" << 'EOF'
Düğmeye bas ve bana hangi hikayeyi anlatmamı istediğini söyle.
EOF

cat > "$DEST/what_story_text.txt" << 'EOF'
Hangi hikayeyi anlatmamı istiyorsun?
EOF

cat > "$DEST/sorry_text.txt" << 'EOF'
Üzgünüm! Anlayamadım. Tekrar dener misin?
EOF

cat > "$DEST/bye_text.txt" << 'EOF'
Görüşürüz! Yakında gel!
EOF

cat > "$DEST/wrong_text.txt" << 'EOF'
Hmm. Bir şeyler ters gitti. Tekrar dener misin?
EOF

cat > "$DEST/delete_text.txt" << 'EOF'
Tüm kaydedilmiş dosyaları siliyorum.
EOF

cat > "$DEST/calibrating_text.txt" << 'EOF'
Mikrofonu ayarlıyorum. Lütfen bir dakika sessiz ol.
EOF

echo "Turkish text files created successfully!"
echo ""
echo "To generate audio files, run:"
echo "python tools/tts.py --voice nova --text-file fably/sounds/hi_text.txt fably/sounds/hi.wav"
echo "python tools/tts.py --voice nova --text-file fably/sounds/hi_short_text.txt fably/sounds/hi_short.wav"
echo "python tools/tts.py --voice nova --text-file fably/sounds/instructions_text.txt fably/sounds/instructions.wav"
echo "python tools/tts.py --voice nova --text-file fably/sounds/what_story_text.txt fably/sounds/what_story.wav"
echo "python tools/tts.py --voice nova --text-file fably/sounds/sorry_text.txt fably/sounds/sorry.wav"
echo "python tools/tts.py --voice nova --text-file fably/sounds/bye_text.txt fably/sounds/bye.wav"
echo "python tools/tts.py --voice nova --text-file fably/sounds/wrong_text.txt fably/sounds/wrong.wav"
echo "python tools/tts.py --voice nova --text-file fably/sounds/delete_text.txt fably/sounds/delete.wav"
echo ""
echo "Or use the simpler command:"
echo 'python -c "
import asyncio
from fably.tts_service import initialize_tts_service, tts_service
import os
from pathlib import Path

async def generate_sounds():
    # Initialize TTS service
    initialize_tts_service(openai_key=os.getenv(\"OPENAI_API_KEY\"))
    
    sounds_dir = Path(\"fably/sounds\")
    
    texts = {
        \"hi\": \"Merhaba! Ben Fably! Senin hikaye arkadaşınım!\",
        \"hi_short\": \"Merhaba! Ben Fably!\",
        \"instructions\": \"Düğmeye bas ve bana hangi hikayeyi anlatmamı istediğini söyle.\",
        \"what_story\": \"Hangi hikayeyi anlatmamı istiyorsun?\",
        \"sorry\": \"Üzgünüm! Anlayamadım. Tekrar dener misin?\",
        \"bye\": \"Görüşürüz! Yakında gel!\",
        \"wrong\": \"Hmm. Bir şeyler ters gitti. Tekrar dener misin?\",
        \"delete\": \"Tüm kaydedilmiş dosyaları siliyorum.\"
    }
    
    for sound_name, text in texts.items():
        output_file = sounds_dir / f\"{sound_name}.wav\"
        print(f\"Generating {output_file}...\")
        await tts_service.synthesize(
            text=text,
            voice=\"nova\",
            provider=\"openai\",
            output_file=output_file,
            format=\"wav\"
        )
    
    print(\"All Turkish sound files generated!\")

asyncio.run(generate_sounds())
"'
