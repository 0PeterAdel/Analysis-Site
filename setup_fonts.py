#!/usr/bin/env python3
"""
Script to download and setup Arabic fonts for the application
"""

import os
import requests
from pathlib import Path
import shutil

FONTS_URLS = {
    'NotoSansArabic-Regular.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Regular.ttf',
    'NotoSansArabic-Bold.ttf': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Bold.ttf'
}

def download_fonts():
    """Download required fonts for Arabic support"""
    fonts_dir = Path(__file__).parent / 'src' / 'assets' / 'fonts'
    fonts_dir.mkdir(parents=True, exist_ok=True)
    
    for font_name, url in FONTS_URLS.items():
        font_path = fonts_dir / font_name
        if not font_path.exists():
            print(f"Downloading {font_name}...")
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                print(f"Successfully downloaded {font_name}")
            except Exception as e:
                print(f"Error downloading {font_name}: {str(e)}")
        else:
            print(f"{font_name} already exists")

if __name__ == "__main__":
    download_fonts()
    print("Font setup completed")
