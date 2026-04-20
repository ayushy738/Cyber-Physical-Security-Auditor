import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtCore import QThread, pyqtSignal
from utils import run_analyzer


# 🔥 Worker Thread (prevents UI freeze)
class AnalyzerWorker(QThread):
    finished = pyqtSignal(dict, str)

    def __init__(self, file):
        super().__init__()
        self.file = file

    def run(self):
        data = run_analyzer(self.file)
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

        self.worker = AnalyzerWorker(file)
        self.worker.finished.connect(self.on_analysis_done)
        self.worker.start()

    def on_analysis_done(self, data, content):
        self.text.setText(content)
        self.show_threats(data, content)

    # 🔥 Risk Score Function
    def calculate_score(self, threats):
        score_map = {
            "CRITICAL": 40,
            "HIGH": 25,
            "MEDIUM": 10,
            "LOW": 5
        }

        score = sum(score_map[t["severity"]] for t in threats)
        return min(score, 100)

    def show_threats(self, data, content):
        self.result.clear()
        cursor = self.text.textCursor()

        for t in data["threats"]:
            line = t["line"]
            typ = t["type"]
            severity = t["severity"]

            self.result.append(f"[{severity}] {typ} at line {line}")

            # 🔥 Highlight line
            block = self.text.document().findBlockByLineNumber(line - 1)
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

            # 🎨 Color mapping
            if severity == "CRITICAL":
                color = QColor("#ff0000")
            elif severity == "HIGH":
                color = QColor("#ff6666")
            elif severity == "MEDIUM":
                color = QColor("#ffcc00")
            else:
                color = QColor("#ccffcc")

            fmt = cursor.charFormat()
            fmt.setBackground(color)
            cursor.setCharFormat(fmt)

        # 🔥 Show Risk Score
        score = self.calculate_score(data["threats"])
        self.result.append(f"\n🔥 Risk Score: {score}/100")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ThreatApp()
    win.resize(800, 600)
    win.show()
    sys.exit(app.exec_())