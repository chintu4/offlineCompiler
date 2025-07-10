# Local Code Compiler Web Interface

A web-based interface for compiling and running code in multiple languages locally, similar to online compiler services.

## Supported Languages

- Rust
- Python
- C
- C++

## Requirements

- Python 3.6 or higher
- Flask
- Rust compiler (rustc) installed and available in the system PATH
- GCC (for C compilation) installed and available in the system PATH
- G++ (for C++ compilation) installed and available in the system PATH
- Python interpreter (for Python code execution)

## Installation

1. Make sure you have the required compilers/interpreters installed:
   - Rust: [https://www.rust-lang.org/tools/install](https://www.rust-lang.org/tools/install)
   - GCC/G++: [https://gcc.gnu.org/install/](https://gcc.gnu.org/install/) (or use MinGW on Windows)
   - Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Download the dependencies for offline use:
   ```
   python download_dependencies.py
   ```
   This will download all JavaScript and CSS libraries to the static folder.

## Usage

There are two ways to run this application:

**1. As a Desktop Application (Recommended for Offline Use):**

   This method uses a PySide6 GUI to wrap the web interface, providing a standalone desktop experience.

   1. Ensure all dependencies, including PySide6, are installed:
      ```bash
      pip install -r requirements.txt
      ```
   2. Run the PySide6 application:
      ```bash
      python app.py
      ```
   This will open a window containing the compiler interface. The Flask server will be started and managed automatically in the background.

**2. As a Web Application (Traditional Flask method):**

   If you prefer to run it as a standard web application accessible via a browser:

   1. Ensure Flask is installed (it's included in `requirements.txt`):
      ```bash
      pip install -r requirements.txt
      ```
   2. Run the Flask application directly (ensure `main.py` is configured to run, or use `flask run`):
      ```bash
      flask run --host=0.0.0.0 --port=5000
      ```
      (You might need to set `FLASK_APP=main.py` as an environment variable if not running `python main.py` directly after uncommenting its `if __name__ == '__main__':` block)
   3. Open your web browser and navigate to: `http://localhost:5000`

**Using the Interface (Applies to Both Methods):**

1. Once the application is running (either as a desktop app or in your browser), select the programming language you want to use.
2. Enter your code in the editor or select one of the provided examples.
3. Add compiler options if needed.
4. Provide input for your program if required.
5. Click "Compile & Run" to execute the code.
6. View the output or any errors in the output panel.

## Features

- Web-based code editor with syntax highlighting
- Support for multiple programming languages (Rust, Python, C, C++)
- Compile and run code locally
- Provide input to your programs
- Add compiler options
- View compilation errors and program output
- Example code snippets for each language
- Clean, responsive UI
- Completely offline - no internet connection required
- **Code History:** Automatically saves your code snippets to a local SQLite database. You can view, load, and delete saved code via the history panel in the desktop application or through dedicated API endpoints if using the web version directly.

### Code History Details

- **Saving Code:** Code can be saved using the "Save" icon in the editor toolbar (Ctrl+S). A title is automatically generated from the first line of code, or you can be prompted for one (feature may vary by interface).
- **Viewing History:**
    - **Desktop App:** A "Code History" panel is available as a dockable widget. It lists saved snippets with language, title, and timestamp. You can refresh this list, load code by double-clicking or using a context menu, and delete entries.
    - **Web Interface (Direct):** History is accessible via API endpoints (`/api/history`). The HTML interface includes a basic (initially hidden) panel that can be populated via JavaScript if you are running the Flask app directly and not through the PySide6 wrapper.
- **Database Location:** The SQLite database file (`code_history.sqlite3`) is stored in a platform-specific user data directory:
    - **Windows:** `%APPDATA%\OfflineCompiler\` (e.g., `C:\Users\<YourUser>\AppData\Roaming\OfflineCompiler\`)
    - **Linux:** `$XDG_DATA_HOME/OfflineCompiler/` (typically `~/.local/share/OfflineCompiler/`)
    - **macOS:** `~/Library/Application Support/OfflineCompiler/` (Note: `database.py` currently uses the Linux XDG path for macOS; this might be refined).
- **Deleting History:** Individual entries can be deleted from the history panel in the desktop app or via the API.

## Offline Mode

This application is designed to work completely offline. All libraries and resources are served locally from the `static` directory. The dependencies are downloaded once using the `download_dependencies.py` script.

If you need to update the dependencies or install them again, simply run:
```
python download_dependencies.py
```
