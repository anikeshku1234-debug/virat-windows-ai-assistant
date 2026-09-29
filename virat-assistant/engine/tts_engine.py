import os
import asyncio
import tempfile
import edge_tts
import winsound

class TTSEngine:
    def __init__(self, voice: str = "en-IN-PrabhatNeural"):
        self.voice = voice

    async def _render_audio(self, text: str, output_path: str):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)

    def speak(self, text: str):
        if not text.strip():
            return
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            asyncio.run(self._render_audio(text, tmp_path))
            winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
        except Exception as e:
            print(f"[TTS Error]: {e}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)