import sys
import os
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QSizePolicy, QScrollBar, QStackedWidget, QMainWindow
)
from dotenv import dotenv_values

# Environment Setup
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

# Utility Functions
def AnswerModifier(answer):
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

def QueryModifier(query):
    query = query.lower().strip()
    query_words = query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you",
                      "what's", "where's", "how's"]
    if not any(word in query for word in question_words):
        if query and query[-1] not in ['.', '?']:
            query += "?"
    return query.capitalize()

def SetMicrophoneStatus(command):
    with open(rf"{TempDirPath}\Mic.data", "w", encoding='utf-8') as file:
        file.write(command)

def GetMicrophoneStatus():
    with open(rf"{TempDirPath}\Mic.data", "r", encoding='utf-8') as file:
        return file.read()

def SetAssistantStatus(status):
    with open(rf"{TempDirPath}\Status.data", "w", encoding='utf-8') as file:
        file.write(status)
SetAssistantStatus("Initializing...")
def GetAssistantStatus():
    with open(rf"{TempDirPath}\Status.data", "r", encoding='utf-8') as file:
        return file.read()

def MicButtonInitialized():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(filename):
    return rf"{GraphicsDirPath}\{filename}"

def TempDirectoryPath(filename):
    return rf"{TempDirPath}\{filename}"

def ShowTextToScreen(text):
    with open(rf"{TempDirPath}\Responses.data", "w", encoding='utf-8') as file:
        file.write(text)

# ChatSection Class
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        text_color = QColor(Qt.blue)
        text_color_format = QTextCharFormat()
        text_color_format.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_format)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        movie.setScaledSize(QSize(480, 270))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel()
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

        self.chat_text_edit.viewport().installEventFilter(self)
        self.setScrollBarStyle()

    def setScrollBarStyle(self):
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def loadMessages(self):
    # Use a global variable to track previous messages
        global old_chat_message

        # Initialize old_chat_message if it doesn't exist
        if "old_chat_message" not in globals():
            old_chat_message = ""

        try:
            # Read the contents of the message file
            with open(TempDirectoryPath('Responses.data'), "r", encoding="utf-8") as file:
                messages = file.read()

            # If the file is empty or the same as the last message, do nothing
            if not messages or len(messages.strip()) <= 1 or messages == old_chat_message:
                return

            # Otherwise, show the message and update the old message tracker
            self.addMessage(message=messages, color="white")
            old_chat_message = messages

        except Exception as e:
            print(f"[ERROR] Failed to load messages: {e}")


    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
        self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
            MicButtonInitialized()
        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled

    def addMessage(self, message, color):
            cursor = self.chat_text_edit.textCursor()
            format = QTextCharFormat()
            formatm = QTextBlockFormat()

            formatm.setTopMargin(10)
            formatm.setLeftMargin(10)

            format.setForeground(QColor(color))

            cursor.setCharFormat(format)
            cursor.setBlockFormat(formatm)
            cursor.insertText(message + "\n")

            self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_label.setMovie(movie)

        max_gif_size_H = int(screen_width / 16*9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))

        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()

        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('Mic_on.png'))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")

        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath("Mic_on.png"), 60, 60)
            MicButtonInitialized()
        else:
            self.load_icon(GraphicsDirectoryPath("Mic_off.png"), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)

        chat_section = ChatSection()
        layout.addWidget(chat_section)

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)

        self.stacked_widget = stacked_widget
        self.initUI()
        self.current_screen = None

    def initUI(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignRight)

        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black")

        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black")

        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath("Minimize2.png"))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath("Maximize.png"))
        self.restore_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        self.maximize_button.setFlat(True)

        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath('Close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        line_frame = QFrame()
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setFixedHeight(1)
        line_frame.setStyleSheet("border-color: black;")

        title_label = QLabel(f"{str(Assistantname).capitalize()} AI")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white")

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)

        self.setLayout(layout)
        self.offset = None
        self.draggable = True

    def paintEvent(self, event):
            painter = QPainter(self)
            painter.fillRect(self.rect(), Qt.white)

    def minimizeWindow(self):
            self.parent().showMinimized()    

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)    

    def closeWindow(self):
            self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()    

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen

class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.initUI()

        def initUI(self):
            desktop = QApplication.desktop()
            screen_width = desktop.screenGeometry().width()
            screen_height = desktop.screenGeometry().height()

            stacked_widget = QStackedWidget(self)

            initial_screen = InitialScreen()
            message_screen = MessageScreen()

            stacked_widget.addWidget(initial_screen)
            stacked_widget.addWidget(message_screen)

            self.setGeometry(0, 0, screen_width, screen_height)
            self.setStyleSheet("background-color: black;")

            top_bar = CustomTopBar(self, stacked_widget)
            self.setMenuWidget(top_bar)
            self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
       
if __name__ == "__main__":
    GraphicalUserInterface()

