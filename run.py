import sys
import subprocess
import webbrowser
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import QProcess, Qt

class FlaskLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flask App Launcher")
        self.setFixedSize(350, 180)
        self.process = None

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Flask server not running.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.start_btn = QPushButton("Start Flask Server")
        self.start_btn.clicked.connect(self.start_flask)
        layout.addWidget(self.start_btn)

        self.open_btn = QPushButton("Open Web Interface")
        self.open_btn.clicked.connect(self.open_browser)
        self.open_btn.setEnabled(False)
        layout.addWidget(self.open_btn)

        self.stop_btn = QPushButton("Stop Flask Server")
        self.stop_btn.clicked.connect(self.stop_flask)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        self.setLayout(layout)

    def start_flask(self):
        if self.process is not None:
            QMessageBox.warning(self, "Warning", "Flask server is already running.")
            return

        self.process = QProcess(self)
        self.process.setProgram(sys.executable)
        self.process.setArguments(["main.py"])
        self.process.setWorkingDirectory(".")
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.started.connect(self.on_started)
        self.process.finished.connect(self.on_finished)
        self.process.start()

        self.status_label.setText("Starting Flask server...")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.open_btn.setEnabled(True)

    def stop_flask(self):
        if self.process is not None:
            self.process.terminate()
            self.process.waitForFinished(3000)
            self.process = None
            self.status_label.setText("Flask server stopped.")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.open_btn.setEnabled(False)

    def open_browser(self):
        webbrowser.open("http://localhost:5000")

    def handle_stdout(self):
        output = self.process.readAllStandardOutput().data().decode()
        if "Running on" in output:
            self.status_label.setText("Flask server is running.")
        # Optionally, print output to a log or console

    def handle_stderr(self):
        error = self.process.readAllStandardError().data().decode()
        # Optionally, print error to a log or console

    def on_started(self):
        self.status_label.setText("Flask server is running.")

    def on_finished(self):
        self.status_label.setText("Flask server stopped.")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.process = None

    def closeEvent(self, event):
        self.stop_flask()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = FlaskLauncher()
    launcher.show()
    sys.exit(app.exec())