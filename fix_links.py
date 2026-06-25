import os
import re

MILA_DIR = "/Users/andresjulianherrerasantos/Mila"

# Dictionary of clean URL patterns to replace (without prefix)
URL_MAP = {
    r'href="/area-privata"': 'area-privata.html',
    r'href="/contatti"': 'contatti.html',
    r'href="/chi-siamo"': 'chi-siamo.html',
    r'href="/palazzo-blue-arroyo"': 'palazzo-blue-arroyo.html',
    r'href="/servizi/branding-rebranding"': 'servizi/branding-rebranding.html',
    r'href="/servizi/campagne-marketing"': 'servizi/campagne-marketing.html',
    r'href="/servizi/funnel-di-vendita"': 'servizi/funnel-di-vendita.html',
    r'href="/servizi/seo-posizionamento-organico"': 'servizi/seo-posizionamento-organico.html',
    r'href="/servizi/social-media-management"': 'servizi/social-media-management.html',
    r'href="/servizi"': 'servizi/index.html',
    r'href="/blog/come-costruire-brand-da-zero"': 'blog/come-costruire-brand-da-zero.html',
    r'href="/blog/funnel-di-vendita-guida-completa"': 'blog/funnel-di-vendita-guida-completa.html',
    r'href="/blog/seo-locale-come-posizionarsi-su-google"': 'blog/seo-locale-come-posizionarsi-su-google.html',
    r'href="/blog/social-media-management-pmi"': 'blog/social-media-management-pmi.html',
    r'href="/blog"': 'blog/index.html',
    r'href="/"': 'index.html',
}

def get_depth_prefix(file_path):
    # Compute depth relative to MILA_DIR
    rel_path = os.path.relpath(file_path, MILA_DIR)
    parts = rel_path.split(os.sep)
    depth = len(parts) - 1
    return "../" * depth

def fix_html_file(file_path):
    print(f"Processing: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    prefix = get_depth_prefix(file_path)

    # 1. First, convert all clean absolute links into correct relative paths
    for pattern, replacement in URL_MAP.items():
        # Match href="/something" or href="/something/"
        # Replaces with href="[prefix]something.html"
        pattern_regex = pattern.replace('"', r'"/?') # allow trailing slash
        content = re.sub(pattern_regex, f'href="{prefix}{replacement}"', content)

    # 2. Inject "Mila Voice Brain" navigation link next to "Area Privata" in nav menus
    # Look for the Area Privata link: <a href="[prefix]area-privata.html"
    area_privata_href = f'href="{prefix}area-privata.html"'
    voice_href = f'{prefix}voice.html'
    
    # Check if voice link is already injected in this file
    if f'href="{voice_href}"' not in content:
        # Search for: <a href="[prefix]area-privata.html" style="...">Area Privata</a>
        # Inject voice link right before it
        nav_pattern = r'(<a\s+[^>]*href="' + re.escape(prefix) + r'area-privata\.html"[^>]*>Area Privata<\/a>)'
        voice_link = f'<a href="{voice_href}" style="color:#00e5ff; font-weight:600; text-shadow:0 0 8px rgba(0,229,255,0.4); margin-right:18px;">Mila Voice Brain</a>'
        
        content = re.sub(nav_pattern, f'{voice_link}\\1', content)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    for root, dirs, files in os.walk(MILA_DIR):
        # Exclude directories like node_modules, src-tauri, dist, dist_assets, .git, .vercel
        dirs[:] = [d for d in dirs if d not in ('node_modules', 'src-tauri', 'dist', 'dist_assets', '.git', '.vercel', 'voice_agent_backend')]
        
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                fix_html_file(file_path)

    print("Link fixing complete!")

if __name__ == "__main__":
    main()
