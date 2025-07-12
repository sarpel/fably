#!/usr/bin/env python3
"""
Fably Dark Theme CSS Injection Script
Adds dark theme CSS to fix white background components
"""

import os
import sys
from pathlib import Path

# Dark theme CSS to fix white backgrounds
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

def inject_css_to_gradio_app():
    """
    Creates a CSS injection function that can be added to Gradio interfaces
    """
    
    css_injection_code = f'''
# Dark Theme CSS Injection for Fably Components
FABLY_DARK_CSS = """{DARK_THEME_CSS}"""

def apply_dark_theme_css():
    """Apply dark theme CSS to fix white component backgrounds"""
    return FABLY_DARK_CSS
'''
    
    return css_injection_code

def create_fixed_app_with_css():
    """
    Create a new web interface file with dark theme CSS fixes
    """
    
    css_header = f"""#!/usr/bin/env python3
\"\"\"
Fably Web Interface with Dark Theme CSS Fixes
Fixed white background components: 11, 16, 54, 63, 82, 87
\"\"\"

import gradio as gr

# Dark theme CSS to fix white component backgrounds
DARK_THEME_CSS = '''
{DARK_THEME_CSS}
'''

"""
    
    return css_header

def main():
    """Main function to apply dark theme fixes"""
    print("Fably Dark Theme CSS Injection")
    print("=" * 50)
    
    # Save CSS to standalone file
    css_file = Path("web_interface/custom_theme.css")
    css_file.write_text(DARK_THEME_CSS, encoding='utf-8')
    print(f"CSS saved to: {css_file}")
    
    # Create injection code for Gradio
    injection_code = inject_css_to_gradio_app()
    injection_file = Path("web_interface/css_injection.py")
    injection_file.write_text(injection_code, encoding='utf-8')
    print(f"CSS injection code saved to: {injection_file}")
    
    # Create header for new app files
    app_header = create_fixed_app_with_css()
    header_file = Path("web_interface/app_header_with_css.py")
    header_file.write_text(app_header, encoding='utf-8')
    print(f"App header with CSS saved to: {header_file}")
    
    print("\\nHow to Apply Fixes:")
    print("1. Add CSS to Gradio app.launch():")
    print('   app.launch(css=DARK_THEME_CSS)')
    print("\\n2. Or add to gr.Blocks():")
    print('   with gr.Blocks(css=DARK_THEME_CSS) as app:')
    print("\\n3. Target component IDs: 11, 16, 54, 63, 82, 87")
    print("4. Fixes all .fably-card backgrounds to #1f2937")
    
    return True

if __name__ == "__main__":
    main()
