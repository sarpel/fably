#!/usr/bin/env python3
"""
Fably CSS Dark Theme Patch Script
Bu script mevcut web interface dosyalarına dark theme CSS'i ekler
"""

import os
import sys
from pathlib import Path

def patch_gradio_app_with_css():
    """Mevcut Gradio app dosyalarına CSS ekleme"""
    
    # CSS content to inject
    css_content = """
# Dark theme CSS to fix white component backgrounds
DARK_THEME_CSS = '''
/* Fably Dark Theme CSS Fixes - Component Background Colors */

/* Target specific component IDs with white backgrounds */
#component-11,
#component-16, 
#component-54,
#component-63,
#component-82,
#component-87 {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
}

/* Fix all fably-card elements with white backgrounds */
.fably-card {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    padding: 16px !important;
}

/* Fix card-like containers in all tabs */
.block.svelte-1svsvh2,
.form.svelte-633qhp,
.column.fably-card {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
}

/* Fix dropdown and input containers */
.wrap.svelte-1hfxrpf,
.secondary-wrap.svelte-1hfxrpf {
    background-color: #1f2937 !important;
}

/* Fix white backgrounds in settings tabs */
.gradio-tabitem {
    background-color: #111827 !important;
}

/* Fix input fields and dropdowns */
input[class*="svelte"],
select[class*="svelte"],
textarea[class*="svelte"] {
    background-color: #374151 !important;
    border: 1px solid #4b5563 !important;
    color: #f9fafb !important;
}

/* Fix button backgrounds */
button[class*="svelte"].secondary {
    background-color: #374151 !important;
    border: 1px solid #4b5563 !important;
    color: #f9fafb !important;
}

/* Fix markdown containers */
.prose.svelte-lag733 {
    background-color: #1f2937 !important;
    color: #f9fafb !important;
}

/* Fix any remaining white backgrounds in containers */
[style*="background: #ffffff"],
[style*="background: white"],
[style*="background-color: #ffffff"],
[style*="background-color: white"] {
    background-color: #1f2937 !important;
}

/* Fix content containers */
.svelte-vuh1yp,
.container.svelte-g2oxp3 {
    background-color: #1f2937 !important;
}

/* Ensure text is readable on dark backgrounds */
.fably-card *,
#component-11 *,
#component-16 *,
#component-54 *,
#component-63 *,
#component-82 *,
#component-87 * {
    color: #f9fafb !important;
}

/* Fix any stats or info cards */
div[style*="background: #f8f9fa"] {
    background: #1f2937 !important;
    border: 1px solid #374151 !important;
}
'''

"""
    
    return css_content

def apply_css_to_existing_files():
    """Mevcut web interface dosyalarına CSS'i uygula"""
    
    files_to_patch = [
        "web_interface/app.py",
        "tools/gradio_app/enhanced_app_unified.py"
    ]
    
    css_injection = patch_gradio_app_with_css()
    
    for file_path in files_to_patch:
        if os.path.exists(file_path):
            print(f"Patching {file_path}...")
            
            # Read existing file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Create backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)
            print(f"  Backup created: {backup_path}")
            
            # Add CSS injection at the beginning
            new_content = css_injection + "\n\n" + content
            
            # Modify gr.Blocks or app.launch calls to include CSS
            if "gr.Blocks(" in content:
                new_content = new_content.replace(
                    "gr.Blocks(",
                    "gr.Blocks(css=DARK_THEME_CSS, "
                )
                print(f"  Modified gr.Blocks() call to include CSS")
            
            if "app.launch(" in content:
                new_content = new_content.replace(
                    "app.launch(",
                    "app.launch(css=DARK_THEME_CSS, "
                )
                print(f"  Modified app.launch() call to include CSS")
            
            # Write patched file
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(new_content)
            
            print(f"  Successfully patched {file_path}")
        else:
            print(f"  File not found: {file_path}")

def create_launch_script():
    """Dark theme ile web interface başlatma scripti oluştur"""
    
    launch_script = '''#!/usr/bin/env python3
"""
Fably Dark Theme Web Interface Launcher
Düzeltilmiş component'ler: 11, 16, 54, 63, 82, 87
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Dark theme web interface'i başlat"""
    
    print("🎨 Fably Dark Theme Web Interface")
    print("=" * 50)
    print("Düzeltilen Component ID'ler: 11, 16, 54, 63, 82, 87")
    print("Tüm ayar sekmelerinde dark background aktif")
    print()
    
    # Check for enhanced app first
    enhanced_app = Path("tools/gradio_app/enhanced_app_dark_theme.py")
    if enhanced_app.exists():
        print("🚀 Enhanced Dark Theme App başlatılıyor...")
        os.system(f"python {enhanced_app}")
    else:
        # Try regular web interface
        web_app = Path("web_interface/app.py")
        if web_app.exists():
            print("🚀 Standard Web Interface başlatılıyor...")
            os.system(f"python {web_app}")
        else:
            print("❌ Web interface dosyası bulunamadı!")
            print("Lütfen şu dosyalardan birinin mevcut olduğundan emin olun:")
            print("- tools/gradio_app/enhanced_app_dark_theme.py")
            print("- web_interface/app.py")

if __name__ == "__main__":
    main()
'''
    
    with open("launch_dark_theme.py", 'w', encoding='utf-8') as f:
        f.write(launch_script)
    
    print("✅ Dark theme launcher created: launch_dark_theme.py")

def main():
    """Ana fonksiyon"""
    print("Fably Dark Theme CSS Patch")
    print("=" * 40)
    
    print("\n1. CSS injection dosyaları oluşturuluyor...")
    css_content = patch_gradio_app_with_css()
    
    print("\n2. Mevcut web interface dosyaları patch'leniyor...")
    apply_css_to_existing_files()
    
    print("\n3. Dark theme launcher oluşturuluyor...")
    create_launch_script()
    
    print("\n✅ Dark Theme Patch Tamamlandı!")
    print("\n🔧 Kullanım:")
    print("1. Dark theme web interface: python launch_dark_theme.py")
    print("2. Veya doğrudan: python tools/gradio_app/enhanced_app_dark_theme.py")
    print("\n🎯 Düzeltilen özellikler:")
    print("- Component ID'leri 11, 16, 54, 63, 82, 87 dark background (#1f2937)")
    print("- Tüm .fably-card elementleri dark theme")
    print("- Ayar sekmelerinde tutarlı dark background")
    print("- Input ve button'lar için uygun renk paleti")

if __name__ == "__main__":
    main()
