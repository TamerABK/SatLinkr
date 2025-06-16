from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import request, send_file
from PIL import Image
import time
import os
import re

def extract_map_js_from_html(html):
    # Cherche le srcdoc de l'iframe
    m = re.search(r'iframe[^>]+srcdoc="([^"]+)"', html)
    if not m:
        raise ValueError("Pas de srcdoc trouvé dans l'iframe")
    srcdoc = m.group(1)
    # Décodage des entités HTML
    from html import unescape
    srcdoc = unescape(srcdoc)
    # Extrait le JS d'initialisation (entre <script> et </script>)
    js_match = re.search(r'<script>(.*?)</script>\s*</html>', srcdoc, re.DOTALL)
    if not js_match:
        raise ValueError("Pas de script d'initialisation trouvé")
    map_js = js_match.group(1)
    return map_js

def genPng():
 

    data = request.get_json()
    map_html = data['html']
    width = data['width']
    height = data['height']

    # Wrap in full HTML if it's just inner content
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
    <style>
    
    * {{
        margin: 0;
        padding: 0;
        padding: 0;
        box-sizing: border-box;
    }}
     html, body, #map {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100vh;
        overflow: hidden;
    }}
    #map{{
        height: 99vh;
    }}
    </style></head>
    <body>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <div id="map" >
    <script>
        {extract_map_js_from_html(map_html)}
    </script>
    </div>
    </body>
    </html>
    """

    # Save temporary HTML file
    os.makedirs(os.path.join(os.getcwd(),'tmp'), exist_ok=True)
    html_path = os.path.join(os.getcwd(),'tmp', 'mp.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    # Configure headless browser
    options = Options()
    options.headless = True
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")  # already added
    options.add_argument("--disable-setuid-sandbox")  # especially for Windows
    options.add_argument("--disable-features=NetworkService")  # network crash workaround
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(width, height)
    driver.get("file://" + html_path)
    time.sleep(3)

    png_path = os.path.join(os.getcwd(),'tmp', 'mp.png')

    with open("tmp/debug_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.get_screenshot_as_file(png_path)
    driver.quit()

    img = Image.open(png_path)

    # Convert to RGB and get pixel data
    img_rgb = img.convert("RGB")
    pixels = img_rgb.load()

    # Get image size
    width, height = img.size

    # Find bottom-most non-white row
    def is_row_white(y):
        for x in range(width):
            if pixels[x, y] != (255, 255, 255):
                return False
        return True

    # Find where the map ends
    cutoff = height
    for y in reversed(range(height)):
        if not is_row_white(y):
            cutoff = y + 1
            break

    # Crop the image
    if cutoff < height:
        img_cropped = img.crop((0, 0, width, cutoff))
        img_cropped.save(png_path)
    # Send the file and clean up
    return send_file(png_path, mimetype='image/png')