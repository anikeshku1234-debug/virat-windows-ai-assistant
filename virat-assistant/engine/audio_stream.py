import sounddevice as sd
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from engine.stt_engine import STTEngine


class AudioListenerThread(QThread):
    transcription_received = pyqtSignal(str)

    def __init__(self, stt_engine: STTEngine, sample_rate: int = 16000, chunk_seconds: int = 4):
        super().__init__()
        self.stt = stt_engine
        self.sample_rate = sample_rate
        self.chunk_seconds = chunk_seconds
        self.is_running = True

    def run(self):
        while self.is_running:
            try:
                # Capture uncompressed mono audio
                recording = sd.rec(
                    int(self.chunk_seconds * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype="float32"
                )
                sd.wait()
                audio_mono = np.squeeze(recording)

                # Process buffer through faster-whisper
                text = self.stt.transcribe_array(audio_mono)
                if text and len(text.strip()) > 1:
                    self.transcription_received.emit(text.strip())
            except Exception as e:
                print(f"[Audio Stream Warning]: {e}")

    def stop(self):
        self.is_running = False