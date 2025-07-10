import os
import requests
import urllib.parse
import zipfile
from io import BytesIO

# Base directories (move these to the top)
static_dir = "static"
js_dir = os.path.join(static_dir, "js")
css_dir = os.path.join(static_dir, "css")
fonts_dir = os.path.join(static_dir, "fonts")

def file_exists_and_not_empty(file_path):
    """
    Check if a file exists and is not empty.
    Returns True if the file exists and has content, False otherwise.
    """
    if os.path.exists(file_path):
        return os.path.getsize(file_path) > 0
    return False

def check_already_install_dependencies_installed():
    """
    Check if all required dependencies are already installed.
    Returns True if all files exist and are not empty, False otherwise.
    """
    # Define paths to check for critical files
    critical_files = [
        os.path.join(js_dir, "codemirror", "codemirror.min.js"),
        os.path.join(css_dir, "codemirror", "codemirror.min.css"),
        os.path.join(js_dir, "beautify", "beautify.min.js"),
        os.path.join(css_dir, "fontawesome", "all.min.css"),
        os.path.join(fonts_dir, "fontawesome", "fa-solid-900.woff2")
    ]
    
    # Check if all critical files exist and are not empty
    for file_path in critical_files:
        if not file_exists_and_not_empty(file_path):
            print(f"Missing dependency: {file_path}")
            return False
        else:
            print(f"Found dependency: {file_path}")
    
    print("All dependencies are already installed.")
    return True

# Add this code right after creating directories but before starting downloads
if check_already_install_dependencies_installed():
    print("Skipping download process as dependencies are already installed.")
    exit(0)

# Modified download function that checks if file exists before downloading
# Modified download function that checks if file exists before downloading
def download_file(url, save_path):
    if file_exists_and_not_empty(save_path):
        print(f"File already exists: {save_path}")
        return True
    
    print(f"Downloading {url} to {save_path}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Successfully downloaded {url}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

# Create directories
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Base directories
static_dir = "static"
js_dir = os.path.join(static_dir, "js")
css_dir = os.path.join(static_dir, "css")
fonts_dir = os.path.join(static_dir, "fonts")

# Ensure directories exist before checking for dependencies
for directory in [static_dir, js_dir, css_dir, fonts_dir]:
    ensure_dir(directory)

# Now check if dependencies are already installed
if check_already_install_dependencies_installed():
    print("Skipping download process as dependencies are already installed.")
    exit(0)
# Create subdirectories for libraries
codemirror_js_dir = os.path.join(js_dir, "codemirror")
codemirror_css_dir = os.path.join(css_dir, "codemirror")
fontawesome_css_dir = os.path.join(css_dir, "fontawesome")
fontawesome_webfonts_dir = os.path.join(fonts_dir, "fontawesome")
beautify_dir = os.path.join(js_dir, "beautify")

# Ensure subdirectories exist
for directory in [codemirror_js_dir, codemirror_css_dir, fontawesome_css_dir, 
                  fontawesome_webfonts_dir, beautify_dir]:
    ensure_dir(directory)

# Create mode and addon directories for CodeMirror
codemirror_mode_dir = os.path.join(codemirror_js_dir, "mode")
codemirror_addon_dir = os.path.join(codemirror_js_dir, "addon")
codemirror_keymap_dir = os.path.join(codemirror_js_dir, "keymap")
codemirror_theme_dir = os.path.join(codemirror_css_dir, "theme")
codemirror_css_addon_dir = os.path.join(codemirror_css_dir, "addon")

# Ensure CodeMirror subdirectories exist
for directory in [codemirror_mode_dir, codemirror_addon_dir, codemirror_keymap_dir, 
                  codemirror_theme_dir, codemirror_css_addon_dir]:
    ensure_dir(directory)

# Further subdirectories for CodeMirror addons
addon_subdirs = ["edit", "hint", "search", "dialog", "fold", "comment", "selection", "display"]
for subdir in addon_subdirs:
    ensure_dir(os.path.join(codemirror_addon_dir, subdir))
    ensure_dir(os.path.join(codemirror_css_addon_dir, subdir))

# Create mode subdirectories
mode_subdirs = ["rust", "python", "clike"]
for subdir in mode_subdirs:
    ensure_dir(os.path.join(codemirror_mode_dir, subdir))

# Function to download a file
def download_file(url, save_path):
    print(f"Downloading {url} to {save_path}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Successfully downloaded {url}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

# Download CodeMirror main files
codemirror_version = "5.65.2"
codemirror_base_url = f"https://cdnjs.cloudflare.com/ajax/libs/codemirror/{codemirror_version}"

# Main CodeMirror JS and CSS
download_file(f"{codemirror_base_url}/codemirror.min.js", os.path.join(codemirror_js_dir, "codemirror.min.js"))
download_file(f"{codemirror_base_url}/codemirror.min.css", os.path.join(codemirror_css_dir, "codemirror.min.css"))

# CodeMirror Themes
themes = ["dracula", "monokai", "material", "nord", "solarized"]
for theme in themes:
    download_file(f"{codemirror_base_url}/theme/{theme}.min.css", 
                 os.path.join(codemirror_theme_dir, f"{theme}.min.css"))

# CodeMirror Modes
modes = [
    {"name": "rust", "path": "rust/rust.min.js"},
    {"name": "python", "path": "python/python.min.js"},
    {"name": "clike", "path": "clike/clike.min.js"}
]

for mode in modes:
    download_file(f"{codemirror_base_url}/mode/{mode['path']}", 
                 os.path.join(codemirror_mode_dir, mode['path']))

# CodeMirror Addons (JS)
addons_js = [
    {"category": "edit", "name": "closebrackets"},
    {"category": "edit", "name": "matchbrackets"},
    {"category": "edit", "name": "closetag"},
    {"category": "edit", "name": "trailingspace"},
    {"category": "fold", "name": "foldcode"},
    {"category": "fold", "name": "foldgutter"},
    {"category": "fold", "name": "brace-fold"},
    {"category": "fold", "name": "comment-fold"},
    {"category": "hint", "name": "show-hint"},
    {"category": "hint", "name": "anyword-hint"},
    {"category": "search", "name": "search"},
    {"category": "search", "name": "searchcursor"},
    {"category": "search", "name": "jump-to-line"},
    {"category": "search", "name": "match-highlighter"},
    {"category": "dialog", "name": "dialog"},
    {"category": "selection", "name": "active-line"},
    {"category": "comment", "name": "comment"},
    {"category": "display", "name": "placeholder"}
]

for addon in addons_js:
    addon_path = os.path.join(codemirror_addon_dir, addon["category"])
    ensure_dir(addon_path)
    download_file(f"{codemirror_base_url}/addon/{addon['category']}/{addon['name']}.min.js", 
                 os.path.join(addon_path, f"{addon['name']}.min.js"))

# CodeMirror Addons (CSS)
addons_css = [
    {"category": "hint", "name": "show-hint"},
    {"category": "fold", "name": "foldgutter"},
    {"category": "dialog", "name": "dialog"},
    {"category": "search", "name": "matchesonscrollbar"}
]

for addon in addons_css:
    addon_path = os.path.join(codemirror_css_addon_dir, addon["category"])
    ensure_dir(addon_path)
    download_file(f"{codemirror_base_url}/addon/{addon['category']}/{addon['name']}.min.css", 
                 os.path.join(addon_path, f"{addon['name']}.min.css"))

# CodeMirror Keymaps
download_file(f"{codemirror_base_url}/keymap/sublime.min.js", 
             os.path.join(codemirror_keymap_dir, "sublime.min.js"))

# JS-Beautify
beautify_version = "1.14.7"
beautify_base_url = f"https://cdnjs.cloudflare.com/ajax/libs/js-beautify/{beautify_version}"

download_file(f"{beautify_base_url}/beautify.min.js", 
             os.path.join(beautify_dir, "beautify.min.js"))
download_file(f"{beautify_base_url}/beautify-css.min.js", 
             os.path.join(beautify_dir, "beautify-css.min.js"))
download_file(f"{beautify_base_url}/beautify-html.min.js", 
             os.path.join(beautify_dir, "beautify-html.min.js"))

# Font Awesome (download zip and extract)
fontawesome_version = "5.15.4"
fontawesome_url = f"https://use.fontawesome.com/releases/v{fontawesome_version}/fontawesome-free-{fontawesome_version}-web.zip"

print(f"Downloading Font Awesome {fontawesome_version}...")
try:
    response = requests.get(fontawesome_url)
    response.raise_for_status()
    
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        # Extract CSS files
        css_files = [f for f in z.namelist() if f.startswith(f"fontawesome-free-{fontawesome_version}-web/css/") and f.endswith(".min.css")]
        for css_file in css_files:
            filename = os.path.basename(css_file)
            with open(os.path.join(fontawesome_css_dir, filename), 'wb') as f:
                f.write(z.read(css_file))
                print(f"Extracted {filename}")
        
        # Extract webfonts
        webfont_files = [f for f in z.namelist() if f.startswith(f"fontawesome-free-{fontawesome_version}-web/webfonts/")]
        for webfont_file in webfont_files:
            filename = os.path.basename(webfont_file)
            if filename:  # Skip directory entries
                with open(os.path.join(fontawesome_webfonts_dir, filename), 'wb') as f:
                    f.write(z.read(webfont_file))
                    print(f"Extracted {filename}")
    
    print("Font Awesome extraction complete")
except Exception as e:
    print(f"Error downloading or extracting Font Awesome: {e}")

print("All dependencies downloaded successfully!")

