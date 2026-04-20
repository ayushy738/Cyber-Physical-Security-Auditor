import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor, QTextCursor
from utils import run_analyzer
from PyQt5.QtCore import QThread, pyqtSignal

class AnalyzerWorker(QThread):
    finished = pyqtSignal(dict, str)

    def __init__(self, file):
        super().__init__()
        self.file = file

    def run(self):
        from utils import run_analyzer
        data = run_analyzer(self.file)

        # also return file content
        with open(self.file, "r", errors="ignore") as f:
            content = f.read()

        self.finished.emit(data, content)

class ThreatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Threat Analyzer")

        layout = QVBoxLayout()

        self.btn = QPushButton("Select File")
        self.btn.clicked.connect(self.open_file)

        self.text = QTextEdit()
        self.text.setReadOnly(False)

        self.result = QTextEdit()
        self.result.setReadOnly(True)

        layout.addWidget(self.btn)
        layout.addWidget(self.text)
        layout.addWidget(QLabel("Threats:"))
        layout.addWidget(self.result)

        self.setLayout(layout)

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName()
        if not file:
            return

        self.result.setText("⏳ Running analysis...")

        # 🔥 start worker thread
        self.worker = AnalyzerWorker(file)
        self.worker.finished.connect(self.on_analysis_done)
        self.worker.start()

    def show_threats(self, data, content):
        self.result.clear()
        cursor = self.text.textCursor()

        for t in data["threats"]:
            line = t["line"]
            typ = t["type"]

            self.result.append(f"[{typ}] at line {line}")

            # Highlight line
            block = self.text.document().findBlockByLineNumber(line-1)
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

            color = QColor("red") if "danger" in typ else QColor("yellow")
            fmt = cursor.charFormat()
            fmt.setBackground(color)
            cursor.setCharFormat(fmt)
    
    def on_analysis_done(self, data, content):
        self.text.setText(content)
        self.show_threats(data, content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ThreatApp()
    win.resize(800, 600)
    win.show()
    sys.exit(app.exec_())