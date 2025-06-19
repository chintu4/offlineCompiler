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

1. Run the Flask application:
   ```
   python main.py
   ```
2. Open your web browser and navigate to: `http://localhost:5000`
3. Select the programming language you want to use
4. Enter your code in the editor or select one of the provided examples
5. Add compiler options if needed
6. Provide input for your program if required
7. Click "Compile & Run" to execute the code
8. View the output or any errors in the output panel

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

## Offline Mode

This application is designed to work completely offline. All libraries and resources are served locally from the `static` directory. The dependencies are downloaded once using the `download_dependencies.py` script.

If you need to update the dependencies or install them again, simply run:
```
python download_dependencies.py
```
