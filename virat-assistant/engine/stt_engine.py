import numpy as np
from faster_whisper import WhisperModel


class STTEngine:
    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        """Initializes Faster-Whisper with INT8 quantization for optimal CPU inference."""
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe_array(self, audio: np.ndarray) -> str:
        # RMS Energy check to ignore pure room noise / dead silence
        rms_energy = np.sqrt(np.mean(audio**2))
        if rms_energy < 0.012:
            return ""

        segments, _ = self.model.transcribe(
            audio,
            beam_size=3,
            language="en",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=400)
        )
        return " ".join([segment.text for segment in segments]).strip()