import sys
import threading
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Offline Compiler App")
        self.setGeometry(100, 100, 800, 600)

        self.browser = QWebEngineView()
        # Delay setting URL until server is confirmed running or use a placeholder
        # self.browser.setUrl(QUrl("http://localhost:5000"))

        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.flask_server_process = None
        self.start_flask_server()

        # Attempt to load URL after a short delay to allow server to start
        # A more robust solution would involve checking server readiness
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.browser.setUrl(QUrl("http://localhost:5000")))


    def start_flask_server(self):
        # Start the Flask server as a subprocess in a new thread
        def run_server():
            # Environment for subprocess
            env = {**subprocess.os.environ, "FLASK_APP": "main.py"}

            # Command to run Flask server
            # Ensure python executable and flask module are correctly referenced
            # For Windows, explicitly use python.exe if sys.executable points to a wrapper
            python_executable = sys.executable
            if "pythonw.exe" in python_executable: # common on windows for GUI apps
                python_executable = python_executable.replace("pythonw.exe", "python.exe")

            command = [python_executable, "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

            try:
                self.flask_server_process = subprocess.Popen(command, env=env)
                self.flask_server_process.wait()
            except Exception as e:
                print(f"Failed to start Flask server: {e}")


        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True  # Daemonize thread to exit with main app
        self.server_thread.start()

    def closeEvent(self, event):
        # Terminate the Flask server when the main window is closed
        print("Closing application...")
        if self.flask_server_process and self.flask_server_process.poll() is None:
            print("Terminating Flask server...")
            self.flask_server_process.terminate()
            try:
                self.flask_server_process.wait(timeout=5) # Wait for process to terminate
                print("Flask server terminated.")
            except subprocess.TimeoutExpired:
                print("Flask server did not terminate in time, killing...")
                self.flask_server_process.kill() # Force kill if terminate fails
                self.flask_server_process.wait()
                print("Flask server killed.")

        # Ensure the server thread is joined
        if hasattr(self, 'server_thread') and self.server_thread.is_alive():
            print("Joining server thread...")
            self.server_thread.join(timeout=5) # Add timeout to prevent hanging
            if self.server_thread.is_alive():
                print("Server thread did not join in time.")
            else:
                print("Server thread joined.")

        event.accept()

def main():
    # Ensure QtWebEngine is initialized
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
