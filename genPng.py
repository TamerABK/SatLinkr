from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask import request, send_file
import time
import os


def genPng():
 

    data = request.get_json()
    map_html = data['html']
    width = data['width']
    height = data['height']

    # Wrap in full HTML if it's just inner content
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><style>html, body {{ margin: 0; padding: 0; overflow: hidden;}}</style></head>
    <body>
    <div id="map">{map_html}</div>
    </body>
    </html>
    """

    # Save temporary HTML file
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
    options.add_argument(f"--window-size={height}x{width}")
    driver = webdriver.Chrome(options=options)

    driver.get("file://" + html_path)
    time.sleep(5)  # Let it render
    png_path = os.path.join(os.getcwd(),'tmp', 'mp.png')
    driver.save_screenshot(png_path)
    driver.quit()

    # Send the file and clean up
    return send_file(png_path, mimetype='image/png')