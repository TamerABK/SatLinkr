from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask import request, send_file
from PIL import Image
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
    <head><meta charset="utf-8"><style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
     html, body, #map {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100vh;
        overflow: hidden;
    }}</style></head>
    <body>
    <div id="map" >{map_html}</div>
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
    time.sleep(5)  # Let it render

    png_path = os.path.join(os.getcwd(),'tmp', 'mp.png')
    print("Saving page source for debug...")
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