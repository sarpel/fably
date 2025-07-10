#!/bin/bash

# ================================================================================
# Fably Audio Tools - Consolidated Script
# ================================================================================
# This script combines audio generation and Turkish sound creation functionality
# Usage: ./audio-tools.sh [command] [options]
# ================================================================================

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[AUDIO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

header() {
    echo -e "${BLUE}==================== $1 ====================${NC}"
}

# Audio settings
DEST="./fably/sounds"
VOICE="nova"  # OpenAI voice

show_usage() {
    echo "Fably Audio Tools"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  turkish-sounds      Generate Turkish system sounds"
    echo "  regenerate-all      Regenerate all existing sounds"
    echo "  startup-sound       Download and process startup sound"
    echo "  test-audio          Test audio generation functionality"
    echo "  help                Show this help message"
    echo ""
    echo "Options:"
    echo "  --voice VOICE       TTS voice to use (default: nova)"
    echo "  --dest DIR          Destination directory (default: ./fably/sounds)"
    echo ""
    echo "Examples:"
    echo "  $0 turkish-sounds                    # Generate Turkish system sounds"
    echo "  $0 regenerate-all --voice alloy      # Regenerate with different voice"
    echo "  $0 startup-sound                     # Create startup sound"
    echo ""
}

# Function to check if a command is available in PATH
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ================================================================================
# TURKISH SOUND GENERATION (from generate_turkish_sounds.sh)
# ================================================================================

generate_turkish_sounds() {
    header "Generating Turkish System Sounds"
    
    # Ensure the sounds directory exists
    mkdir -p "$DEST"
    
    log "Creating Turkish text files..."
    
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

    cat > "$DEST/instructions_wakeword_text.txt" << 'EOF'
Hey Fably de ve hikaye iste!
EOF

    log "Turkish text files created successfully!"
    
    # Generate audio files using Python TTS service
    log "Generating audio files with TTS service..."
    
    python3 -c "
import asyncio
import os
import sys
from pathlib import Path

# Add fably to Python path
sys.path.insert(0, '.')

try:
    from fably.tts_service import initialize_tts_service, tts_service
except ImportError as e:
    print(f'Error importing TTS service: {e}')
    print('Make sure you are in the Fably root directory and have activated the virtual environment')
    sys.exit(1)

async def generate_sounds():
    # Initialize TTS service
    try:
        initialize_tts_service(openai_key=os.getenv('OPENAI_API_KEY'))
        print('TTS service initialized successfully')
    except Exception as e:
        print(f'Failed to initialize TTS service: {e}')
        return
    
    sounds_dir = Path('$DEST')
    
    texts = {
        'hi': 'Merhaba! Ben Fably! Senin hikaye arkadaşınım!',
        'hi_short': 'Merhaba! Ben Fably!',
        'instructions': 'Düğmeye bas ve bana hangi hikayeyi anlatmamı istediğini söyle.',
        'instructions_wakeword': 'Hey Fably de ve hikaye iste!',
        'what_story': 'Hangi hikayeyi anlatmamı istiyorsun?',
        'sorry': 'Üzgünüm! Anlayamadım. Tekrar dener misin?',
        'bye': 'Görüşürüz! Yakında gel!',
        'wrong': 'Hmm. Bir şeyler ters gitti. Tekrar dener misin?',
        'delete': 'Tüm kaydedilmiş dosyaları siliyorum.',
        'calibrating': 'Mikrofonu ayarlıyorum. Lütfen bir dakika sessiz ol.'
    }
    
    for sound_name, text in texts.items():
        output_file = sounds_dir / f'{sound_name}.wav'
        print(f'Generating {output_file}...')
        try:
            await tts_service.synthesize(
                text=text,
                voice='$VOICE',
                provider='openai',
                output_file=output_file,
                format='wav'
            )
            print(f'✅ Generated {sound_name}.wav')
        except Exception as e:
            print(f'❌ Failed to generate {sound_name}.wav: {e}')
    
    print('Turkish sound generation completed!')

asyncio.run(generate_sounds())
"
}

# ================================================================================
# COMMAND LINE ARGUMENT PARSING AND MAIN DISPATCHER
# ================================================================================

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --voice)
            VOICE="$2"
            shift 2
            ;;
        --dest)
            DEST="$2"
            shift 2
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            COMMAND="$1"
            shift
            ;;
    esac
done

# Main command dispatcher
case "${COMMAND:-help}" in
    "turkish-sounds")
        generate_turkish_sounds
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        error "Unknown command: ${COMMAND:-none}"
        show_usage
        exit 1
        ;;
esac
