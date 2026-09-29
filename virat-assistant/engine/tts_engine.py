import os
import asyncio
import tempfile
import edge_tts
import winsound


class TTSEngine:
    def __init__(self, voice: str = "hi-IN-MadhurNeural"):
        self.voice = voice

    async def _generate_audio_file(self, text: str, output_path: str):
        communicate = edge_tts.Communicate(text, self.voice, rate="+5%", pitch="+0Hz")
        await communicate.save(output_path)

    def speak(self, text: str):
        if not text or not text.strip():
            return

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            asyncio.run(self._generate_audio_file(text, tmp_path))
            winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
        except Exception as e:
            print(f"[TTS Error]: {e}")
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
