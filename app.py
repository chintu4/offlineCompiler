import sys
import threading
import subprocess
import os # For path operations
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QDockWidget, QListWidget, QListWidgetItem, QPushButton,
                             QHBoxLayout, QMessageBox, QMenu)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt, QTimer, QSize # Added QSize
from PySide6.QtGui import QAction # Added QAction for context menu

# Assuming database.py is in the same directory
import database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Offline Compiler App with History")
        self.setGeometry(100, 100, 1000, 700) # Increased default size for history panel

        # Initialize database
        self.db_session = next(database.get_db())
        database.create_db_tables() # Ensure tables are created

        self.setup_ui()

        self.flask_server_process = None
        self.start_flask_server()

        QTimer.singleShot(2000, lambda: self.browser.setUrl(QUrl("http://localhost:5000")))

    def setup_ui(self):
        # Central Web View
        self.browser = QWebEngineView()

        # History Dock Widget
        self.history_dock = QDockWidget("Code History", self)
        self.history_list_widget = QListWidget()
        self.history_list_widget.itemDoubleClicked.connect(self.load_history_item)

        # Context menu for history items
        self.history_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list_widget.customContextMenuRequested.connect(self.show_history_context_menu)

        # Buttons for history management
        self.refresh_history_button = QPushButton("Refresh History")
        self.refresh_history_button.clicked.connect(self.populate_history_list)

        # Layout for history dock content
        history_layout = QVBoxLayout()
        history_layout.addWidget(self.refresh_history_button)
        history_layout.addWidget(self.history_list_widget)

        history_container = QWidget()
        history_container.setLayout(history_layout)
        self.history_dock.setWidget(history_container)
        self.addDockWidget(Qt.RightDockWidgetArea, self.history_dock)

        # Main layout
        main_container = QWidget() # Central widget needs a container
        main_layout = QHBoxLayout(main_container) # Use QHBoxLayout if browser is meant to be beside dock
        main_layout.addWidget(self.browser)
        # If dock is overlay or separate, browser can be set directly or in a QVBoxLayout
        self.setCentralWidget(main_container) # Set the container as central widget

        self.populate_history_list()


    def show_history_context_menu(self, position):
        item = self.history_list_widget.itemAt(position)
        if not item:
            return

        context_menu = QMenu(self)
        load_action = QAction("Load Code", self)
        load_action.triggered.connect(lambda: self.load_history_item(item))
        context_menu.addAction(load_action)

        delete_action = QAction("Delete Entry", self)
        delete_action.triggered.connect(lambda: self.delete_history_item_from_context_menu(item))
        context_menu.addAction(delete_action)

        context_menu.exec(self.history_list_widget.mapToGlobal(position))

    def delete_history_item_from_context_menu(self, item):
        entry_id = item.data(Qt.UserRole) # Retrieve stored ID
        if entry_id is None:
            QMessageBox.warning(self, "Error", "Could not find ID for this history item.")
            return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to delete '{item.text()}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if database.delete_code_history_by_id(self.db_session, entry_id):
                self.populate_history_list() # Refresh list
                QMessageBox.information(self, "Success", "History entry deleted.")
                # Optionally, notify the webview to clear if this code was loaded
                # self.browser.page().runJavaScript("clearEditorIfMatchesHistoryId(...);")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete history entry from database.")


    def populate_history_list(self):
        self.history_list_widget.clear()
        try:
            history_entries = database.get_all_code_history(self.db_session)
            if not history_entries:
                self.history_list_widget.addItem(QListWidgetItem("No history found."))
                return

            for entry in history_entries:
                # Display title, language, and a bit of the timestamp
                display_text = f"{entry.title} ({entry.language}) - {entry.timestamp.strftime('%Y-%m-%d %H:%M')}"
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.UserRole, entry.id)  # Store ID for later use
                self.history_list_widget.addItem(list_item)
        except Exception as e:
            print(f"Error populating history list: {e}")
            self.history_list_widget.addItem(QListWidgetItem("Error loading history."))


    def load_history_item(self, item):
        entry_id = item.data(Qt.UserRole)
        if entry_id is None: return # Should not happen if populated correctly

        entry = database.get_code_history_by_id(self.db_session, entry_id)
        if entry:
            # Use JavaScript to set code in CodeMirror editor in the web view
            # This requires corresponding JavaScript functions in your web page
            js_code = f"""
            if (window.setCodeFromHost) {{
                window.setCodeFromHost('{entry.language}', `{entry.code.replace('`', '\\`')}`);
            }} else {{
                console.warn('setCodeFromHost function not found in webview.');
                alert('Could not load code into editor: Communication function missing.');
            }}
            """
            self.browser.page().runJavaScript(js_code)
        else:
            QMessageBox.warning(self, "Error", "Could not retrieve history item from database.")


    def start_flask_server(self):
        def run_server():
            env = {**os.environ, "FLASK_APP": "main.py", "FLASK_ENV": "development"} # FLASK_ENV for debug if needed
            python_executable = sys.executable
            if "pythonw.exe" in python_executable:
                python_executable = python_executable.replace("pythonw.exe", "python.exe")

            # Ensure Flask uses the same Python interpreter if venvs are tricky
            command = [python_executable, "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

            try:
                # For PyInstaller/frozen apps, main.py might not be directly accessible
                # in the same way. Consider adjusting CWD or path if running frozen.
                self.flask_server_process = subprocess.Popen(command, env=env)
                self.flask_server_process.wait()
            except Exception as e:
                print(f"Failed to start Flask server: {e}")
                # Show a message box to the user
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Server Error", f"Failed to start backend server: {e}"))


        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def closeEvent(self, event):
        print("Closing application...")
        if self.flask_server_process and self.flask_server_process.poll() is None:
            print("Terminating Flask server...")
            self.flask_server_process.terminate()
            try:
                self.flask_server_process.wait(timeout=5)
                print("Flask server terminated.")
            except subprocess.TimeoutExpired:
                print("Flask server did not terminate in time, killing...")
                self.flask_server_process.kill()
                self.flask_server_process.wait()
                print("Flask server killed.")

        if hasattr(self, 'server_thread') and self.server_thread.is_alive():
            print("Joining server thread...")
            self.server_thread.join(timeout=5)
            if self.server_thread.is_alive(): print("Server thread did not join in time.")
            else: print("Server thread joined.")

        if self.db_session:
            self.db_session.close()
            print("Database session closed.")

        event.accept()

def main():
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts) # For WebEngine
    app = QApplication(sys.argv)

    # Set app name for better OS integration (e.g., file paths)
    QApplication.setApplicationName("OfflineCompiler")
    QApplication.setOrganizationName("MyCompany") # Optional

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
