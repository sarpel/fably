"""
Cross-platform path utilities for Fably
Handles Windows/Linux path differences and ensures compatibility
"""

import os
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
import logging


def get_platform_info():
    """Platform bilgilerini al"""
    return {
        "system": sys.platform,
        "os_name": os.name,
        "is_windows": sys.platform.startswith('win'),
        "is_linux": sys.platform.startswith('linux'),
        "is_raspberry_pi": is_raspberry_pi(),
        "path_separator": os.sep,
        "line_separator": os.linesep
    }


def is_raspberry_pi():
    """Raspberry Pi tespiti"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
    except (FileNotFoundError, PermissionError):
        return False


def normalize_path(path_str):
    """
    Path'i cross-platform uyumlu hale getir
    Windows'ta yazılıp Linux'ta çalışacak şekilde normalize et
    """
    if not path_str:
        return Path()
    
    # String path'i Path objesine çevir
    path = Path(path_str)
    
    # Platform spesifik düzeltmeler
    if sys.platform.startswith('win'):
        # Windows'ta forward slash'leri backslash'e çevir
        return path.resolve()
    else:
        # Linux'ta backslash'leri forward slash'e çevir
        if '\\' in str(path):
            # Windows path formatını Linux formatına çevir
            parts = str(path).replace('\\', '/').split('/')
            # Drive letter'ı kaldır (C: gibi)
            if len(parts) > 0 and ':' in parts[0]:
                parts = parts[1:]
            return Path('/'.join(parts))
        return path.resolve()


def ensure_directory(path):
    """Dizinin var olduğundan emin ol"""
    normalized_path = normalize_path(path)
    normalized_path.mkdir(parents=True, exist_ok=True)
    return normalized_path


def safe_file_path(base_path, filename):
    """Güvenli dosya path'i oluştur"""
    base = normalize_path(base_path)
    # Filename'deki tehlikeli karakterleri temizle
    safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
    return base / safe_filename


def get_fably_paths():
    """Fably için standart path'leri al"""
    # Script'in bulunduğu dizini bul
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller bundle
        base_dir = Path(sys._MEIPASS)
    else:
        # Normal Python execution
        base_dir = Path(__file__).parent.parent
    
    paths = {
        'base': normalize_path(base_dir),
        'fably': normalize_path(base_dir / 'fably'),
        'stories': normalize_path(base_dir / 'stories'),
        'queries': normalize_path(base_dir / 'queries'), 
        'models': normalize_path(base_dir / 'models'),
        'sounds': normalize_path(base_dir / 'fably' / 'sounds'),
        'examples': normalize_path(base_dir / 'fably' / 'examples'),
        'tools': normalize_path(base_dir / 'tools'),
        'docs': normalize_path(base_dir / 'docs'),
        'install': normalize_path(base_dir / 'install'),
        'tests': normalize_path(base_dir / 'tests')
    }
    
    # Gerekli dizinleri oluştur
    for path_name, path in paths.items():
        if path_name in ['stories', 'queries', 'models']:
            ensure_directory(path)
    
    return paths


def convert_line_endings(file_path, target_ending='lf'):
    """
    Dosya satır sonlarını dönüştür
    target_ending: 'lf' (Linux), 'crlf' (Windows), 'cr' (Mac classic)
    """
    file_path = normalize_path(file_path)
    
    if not file_path.exists():
        return False
    
    try:
        # Dosyayı oku
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Satır sonlarını normalize et
        content = content.replace(b'\r\n', b'\n')  # CRLF -> LF
        content = content.replace(b'\r', b'\n')    # CR -> LF
        
        # Hedef format
        if target_ending.lower() == 'crlf':
            content = content.replace(b'\n', b'\r\n')
        elif target_ending.lower() == 'cr':
            content = content.replace(b'\n', b'\r')
        # 'lf' için değişiklik gerekmiyor
        
        # Geri yaz
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        logging.error(f"Line ending conversion failed for {file_path}: {e}")
        return False


def fix_python_files_for_linux():
    """
    Python dosyalarını Linux uyumluluğu için düzelt
    Windows'ta geliştirilen kodların Linux'ta çalışması için
    """
    paths = get_fably_paths()
    
    # Python dosyalarını bul ve düzelt
    python_files = []
    for directory in [paths['fably'], paths['tools'], paths['tests']]:
        if directory.exists():
            python_files.extend(directory.glob('**/*.py'))
    
    fixed_count = 0
    for py_file in python_files:
        if convert_line_endings(py_file, 'lf'):
            fixed_count += 1
    
    # Shell script'leri düzelt
    script_files = list(paths['base'].glob('*.sh'))
    for script_file in script_files:
        if convert_line_endings(script_file, 'lf'):
            fixed_count += 1
            # Executable permission ver (sadece Linux'ta)
            if not sys.platform.startswith('win'):
                os.chmod(script_file, 0o755)
    
    logging.info(f"Fixed line endings for {fixed_count} files")
    return fixed_count


def get_audio_device_path():
    """Platform'a göre ses cihazı path'ini al"""
    platform_info = get_platform_info()
    
    if platform_info['is_raspberry_pi']:
        # Raspberry Pi'da USB audio adapter
        return '/dev/snd/'
    elif platform_info['is_linux']:
        # Genel Linux
        return '/dev/snd/'
    else:
        # Windows
        return None  # Windows'ta driver otomatik tespit eder


def get_default_configs():
    """Platform'a göre varsayılan konfigürasyon"""
    platform_info = get_platform_info()
    
    config = {
        'sample_rate': 24000,
        'channels': 1,  # Mono
        'bit_depth': 16,
        'buffer_size': 4096
    }
    
    if platform_info['is_raspberry_pi']:
        # Raspberry Pi optimize ayarları
        config.update({
            'sample_rate': 16000,  # Daha düşük CPU kullanımı
            'buffer_size': 2048,   # Daha küçük buffer
            'audio_driver': 'alsa'
        })
    elif platform_info['is_linux']:
        config['audio_driver'] = 'alsa'
    else:
        config['audio_driver'] = 'sounddevice'
    
    return config


if __name__ == "__main__":
    # Test ve düzeltme scripti
    print("🔧 Fably Cross-Platform Compatibility Check")
    print("=" * 50)
    
    # Platform bilgileri
    platform_info = get_platform_info()
    print(f"Platform: {platform_info['system']}")
    print(f"OS: {platform_info['os_name']}")
    print(f"Windows: {platform_info['is_windows']}")
    print(f"Linux: {platform_info['is_linux']}")
    print(f"Raspberry Pi: {platform_info['is_raspberry_pi']}")
    print(f"Path Separator: '{platform_info['path_separator']}'")
    print(f"Line Separator: {repr(platform_info['line_separator'])}")
    print()
    
    # Path bilgileri
    paths = get_fably_paths()
    print("📁 Fably Paths:")
    for name, path in paths.items():
        exists = "✅" if path.exists() else "❌"
        print(f"  {name}: {exists} {path}")
    print()
    
    # Python dosyalarını düzelt
    print("🔧 Fixing Python files for Linux compatibility...")
    fixed_count = fix_python_files_for_linux()
    print(f"✅ Fixed {fixed_count} files")
    print()
    
    # Ses cihazı bilgileri
    audio_path = get_audio_device_path()
    if audio_path:
        print(f"🔊 Audio Device Path: {audio_path}")
    
    # Varsayılan config
    config = get_default_configs()
    print("⚙️ Default Audio Config:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Cross-platform compatibility check completed!")
