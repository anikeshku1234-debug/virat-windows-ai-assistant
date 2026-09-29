import sys
import os
from dotenv import load_dotenv

# Environment variables load karein (.env file se)
load_dotenv()

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QLabel, QPushButton, QMessageBox
)
from PyQt6.QtGui import QFont

from engine.security_guard import SecurityGuard
from engine.stt_engine import STTEngine
from engine.tts_engine import TTSEngine
from engine.audio_stream import AudioListenerThread
from engine.brain import ViratBrain


class ViratDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virat - Autonomous Windows Voice Assistant")
        self.resize(750, 520)

        # Core subsystems initialize karein
        self.security = SecurityGuard()
        self.stt = STTEngine(
            model_size=os.getenv("WHISPER_MODEL_SIZE", "base"),
            device=os.getenv("WHISPER_DEVICE", "cpu"),
            compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        )
        self.tts = TTSEngine(voice=os.getenv("TTS_VOICE", "en-IN-PrabhatNeural"))
        self.brain = ViratBrain(self.security)

        self._build_interface()

        # Background microphone listener thread start karein
        self.audio_thread = AudioListenerThread(self.stt)
        self.audio_thread.transcription_received.connect(self.handle_voice_input)
        self.audio_thread.start()

    def _build_interface(self):
        root_widget = QWidget()
        layout = QVBoxLayout()

        # Top Status Bar
        status_bar = QHBoxLayout()
        self.status_label = QLabel("● SYSTEM ACTIVE & LISTENING")
        self.status_label.setStyleSheet("color: #00E676; font-weight: bold; font-size: 13px;")
        status_bar.addWidget(self.status_label)
        layout.addLayout(status_bar)

        # Activity Terminal (Logs & Transcription)
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Consolas", 10))
        self.terminal.setStyleSheet(
            "background-color: #0f141c; color: #58a6ff; border: 1px solid #30363d; border-radius: 6px; padding: 8px;"
        )
        layout.addWidget(self.terminal)

        # Emergency Stop Button
        self.stop_button = QPushButton("EMERGENCY STOP (HALT ALL ACTIONS)")
        self.stop_button.setFixedHeight(45)
        self.stop_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.stop_button.setStyleSheet(
            "background-color: #d32f2f; color: white; border: none; border-radius: 5px; cursor: pointer;"
        )
        self.stop_button.clicked.connect(self.trigger_manual_stop)
        layout.addWidget(self.stop_button)

        root_widget.setLayout(layout)
        self.setCentralWidget(root_widget)

    def ask_ui_confirmation(self, message: str) -> bool:
        """High-impact actions ke liye user authorization popup."""
        reply = QMessageBox.warning(
            self,
            "Security Policy Enforcement",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def handle_voice_input(self, user_text: str):
        """Audio thread se text aane par trigger hota hai."""
        self.terminal.append(f"\n[USER AUDIO]: {user_text}")

        # Brain se action route aur execute karein
        response = self.brain.process_command(user_text, self.ask_ui_confirmation)

        self.terminal.append(f"[VIRAT]: {response}")
        self.tts.speak(response)

    def trigger_manual_stop(self):
        """Emergency stop action."""
        self.security.trip_emergency_stop()
        self.status_label.setText("● SYSTEM HALTED - SAFETY OVERRIDE")
        self.status_label.setStyleSheet("color: #d32f2f; font-weight: bold; font-size: 13px;")
        self.terminal.append("\n[ALERT]: Emergency stop manually triggered. All automations blocked.")

    def closeEvent(self, event):
        """Window close hone par cleanly thread stop karein."""
        self.audio_thread.stop()
        self.audio_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ViratDashboard()
    window.show()
    sys.exit(app.exec())