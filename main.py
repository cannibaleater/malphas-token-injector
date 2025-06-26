import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QPoint, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.parent = parent
        self.setStyleSheet("background-color: #11111A;")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.title = QPushButton("  DISCORD TOKEN TOOL")
        self.title.setEnabled(False)
        self.title.setStyleSheet("color: #8888cc; background: transparent; border: none; text-align: left;")
        layout.addWidget(self.title)

        layout.addStretch()

        self.min_btn = QPushButton("—")
        self.max_btn = QPushButton("🗖")
        self.close_btn = QPushButton("×")

        for btn in [self.min_btn, self.max_btn, self.close_btn]:
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("""
                QPushButton {
                    color: #b0b0ff;
                    background-color: #1a1a28;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #333355;
                }
            """)

        self.min_btn.clicked.connect(self.parent.showMinimized)
        self.max_btn.clicked.connect(self.toggle_max_restore)
        self.close_btn.clicked.connect(self.parent.close)

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        self.old_pos = None

    def toggle_max_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.parent.move(self.parent.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()


class DiscordGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(1300, 600)
        self.setStyleSheet(open("style.qss").read())

        # Navegador embutido
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://discord.com/login"))

        # Token input
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("token")

        # Botão de login
        self.login_button = QPushButton("inject")
        self.login_button.clicked.connect(self.inject_token)

        # Logs
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setPlaceholderText("logs")

        # Layout direito
        right_layout = QVBoxLayout()
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.token_input)
        top_bar.addWidget(self.login_button)
        right_layout.addLayout(top_bar)
        right_layout.addWidget(self.logs)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # Splitter entre navegador e painel
        splitter = QSplitter()
        splitter.addWidget(self.browser)
        splitter.addWidget(right_widget)
        splitter.setSizes([1000, 400])
        splitter.setHandleWidth(0)

        # Layout principal com barra personalizada
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(splitter)
        content_widget.setLayout(content_layout)

        main_layout.addWidget(content_widget)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def inject_token(self):
        token = self.token_input.text().strip()
        if not token:
            self.logs.append("⚠️ Empty Token!")
            return

        js_code = f"""
            function login(token) {{
                setInterval(() => {{
                    document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage.token = `"${{token}}"`;
                }}, 50);
                setTimeout(() => {{
                    location.href = "https://discord.com/app";
                }}, 2500);
            }}
            login("{token}");
        """
        self.browser.page().runJavaScript(js_code)
        self.logs.append("✅ Token injected, wait for redirect...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DiscordGUI()
    window.show()
    sys.exit(app.exec())
