# assistant_gui.py (Fixed mic size inside circle + medium/black theme)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel
)
from PyQt5.QtGui import (
    QPainter, QMovie, QFont, QPixmap, QCursor
)
from PyQt5.QtCore import Qt, QSize, QTimer

from dotenv import dotenv_values
import sys
import os

# ---------- Configuration ----------
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")

FILES_DIR = r"C:\pthiin code\Frontend\Files"
GRAPHICS_DIR = r"C:\pthiin code\Frontend\Graphics"

os.makedirs(FILES_DIR, exist_ok=True)
os.makedirs(GRAPHICS_DIR, exist_ok=True)

MIC_FILE = os.path.join(FILES_DIR, "mic.data")
STATUS_FILE = os.path.join(FILES_DIR, "status.data")
RESPONSE_FILE = os.path.join(FILES_DIR, "response.data")

for p in (MIC_FILE, STATUS_FILE, RESPONSE_FILE):
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            f.write("")


# ---------- Helper Functions ----------
def get_graphics_path(filename: str) -> str:
    return os.path.join(GRAPHICS_DIR, filename)

def set_microphone_status(status: str):
    with open(MIC_FILE, "w", encoding="utf-8") as f:
        f.write(status)

def get_microphone_status() -> str:
    try:
        with open(MIC_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return "False"


# ---------- Mic Button Widget ----------
class MicButton(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(100, 100)   # Circle size reduced
        self.toggled = False

        self.icon_on = get_graphics_path("mic_on.png")
        self.icon_off = get_graphics_path("mic_off.png")

        # Default mic off
        self.load_icon(self.icon_off)
        set_microphone_status("False")

        # Click to toggle
        self.mousePressEvent = self.toggle_mic

    def load_icon(self, path):
        if os.path.exists(path):
            # Smaller icon to fit circle properly
            pixmap = QPixmap(path).scaled(55, 55, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(pixmap)

    def toggle_mic(self, event=None):
        self.toggled = not self.toggled
        if self.toggled:
            self.load_icon(self.icon_on)
            self.setStyleSheet("""
                QLabel {
                    border: 4px solid #00ffcc;
                    border-radius: 50px;
                    background-color: black;
                    box-shadow: 0 0 20px #00ffcc;
                }
            """)
            set_microphone_status("True")
        else:
            self.load_icon(self.icon_off)
            self.setStyleSheet("""
                QLabel {
                    border: 4px solid red;
                    border-radius: 50px;
                    background-color: black;
                }
            """)
            set_microphone_status("False")


# ---------- Chat Section (small GIF, bottom-right) ----------
class ChatSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Chat box
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setFont(QFont("Segoe UI", 13))
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: black;
                color: white;
                border: none;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_text_edit)

        # Small GIF in bottom-right corner
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("background-color: black; padding: 5px;")
        gif_path = get_graphics_path("jarvis.gif.gif")

        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(260, 160))  # small GIF size
            self.gif_label.setMovie(movie)
            movie.start()

        gif_container = QHBoxLayout()
        gif_container.addStretch(1)
        gif_container.addWidget(self.gif_label, alignment=Qt.AlignBottom | Qt.AlignRight)
        layout.addLayout(gif_container)

        # Mic + Status
        mic_layout = QHBoxLayout()
        self.mic_button = MicButton()
        mic_layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        layout.addLayout(mic_layout)

        self.label = QLabel("Listening status will appear here...")
        self.label.setStyleSheet("color: cyan; font-size: 18px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # Timer updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(400)

    def update_status(self):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                status = f.read().strip()
        except Exception:
            status = ""
        self.label.setText(status)


# ---------- Initial Screen (medium GIF centered) ----------
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 80, 0, 80)
        layout.setSpacing(25)

        # Medium GIF (centered)
        gif_label = QLabel()
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setStyleSheet("background-color: black; padding: 10px;")

        gif_path = get_graphics_path("jarvis.gif.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(520, 320))
            gif_label.setMovie(movie)
            movie.start()
        layout.addWidget(gif_label, alignment=Qt.AlignCenter)

        # Mic Button Below GIF
        self.mic_button = MicButton()
        layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)

        # Label
        self.label = QLabel(f"{Assistantname} is ready to assist you.")
        self.label.setStyleSheet("color:white;font-size:20px;font-weight:bold;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.setLayout(layout)
        self.setStyleSheet("background-color:black;")


# ---------- Message Screen ----------
class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color:black;")


# ---------- Custom Top Bar ----------
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget: QStackedWidget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(55)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel(f"🎙️ {Assistantname} AI")
        title_label.setStyleSheet("color:black;font-size:19px;font-weight:bold;background-color:white;")

        home_button = QPushButton("🏠 Home")
        home_button.setStyleSheet("background:white;color:black;font-weight:bold;padding:5px 15px;")

        chat_button = QPushButton("💬 Chat")
        chat_button.setStyleSheet("background:white;color:black;font-weight:bold;padding:5px 15px;")

        close_button = QPushButton("❌")
        close_button.setStyleSheet("background:white;color:red;font-weight:bold;padding:5px 15px;")
        close_button.clicked.connect(lambda: self.window().close())

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        chat_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(chat_button)
        layout.addWidget(close_button)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)


# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        self.setStyleSheet("background-color:black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)
        self.showMaximized()


# ---------- Entry Point ----------
def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()

