#!/usr/bin/env python3
"""
Fably CSS Dark Theme Simple Patch Script
Bu script dark theme CSS'i web interface'lere ekler
"""

import os
import sys
from pathlib import Path

CSS_CONTENT = '''
# Dark theme CSS to fix white component backgrounds
DARK_THEME_CSS = """
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
"""

'''

def create_launcher():
    """Dark theme launcher oluştur"""
    
    launcher_content = '''#!/usr/bin/env python3
"""
Fably Dark Theme Launcher
"""

import os
import sys
from pathlib import Path

def main():
    print("Fably Dark Theme Web Interface")
    print("=" * 40)
    print("Duzeltilen Component ID'ler: 11, 16, 54, 63, 82, 87")
    print()
    
    # Enhanced app kontrolu
    enhanced_app = Path("tools/gradio_app/enhanced_app_dark_theme.py")
    if enhanced_app.exists():
        print("Enhanced Dark Theme App baslatiliyor...")
        os.system(f"python {enhanced_app}")
    else:
        print("Enhanced app bulunamadi!")
        print("Lutfen once: python simple_dark_patch.py")

if __name__ == "__main__":
    main()
'''
    
    with open("launch_dark_theme.py", 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    return True

def main():
    """Ana fonksiyon"""
    print("Fably Dark Theme Simple Patch")
    print("=" * 30)
    
    # CSS injection dosyasi olustur
    with open("css_dark_theme.py", 'w', encoding='utf-8') as f:
        f.write(CSS_CONTENT)
    print("CSS dosyasi olusturuldu: css_dark_theme.py")
    
    # Launcher olustur
    create_launcher()
    print("Launcher olusturuldu: launch_dark_theme.py")
    
    print("\\nKullanim:")
    print("1. Enhanced app'i manuel olarak calistirin:")
    print("   python tools/gradio_app/enhanced_app_dark_theme.py")
    print("\\n2. Veya launcher ile:")
    print("   python launch_dark_theme.py")
    
    print("\\nDuzeltilen:")
    print("- Component 11, 16, 54, 63, 82, 87 dark background")
    print("- Tum ayar sekmelerinde dark theme")

if __name__ == "__main__":
    main()
