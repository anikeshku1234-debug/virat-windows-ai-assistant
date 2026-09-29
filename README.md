# Virat: Autonomous Windows AI Voice Assistant

Virat is a local, voice-activated desktop assistant engineered specifically for Windows. Built with asynchronous audio streams, local speech recognition via `faster-whisper`, neural text-to-speech with `edge-tts`, Playwright browser automation, and a zero-trust Human-In-The-Loop (HITL) security governor.

---

## Key Features

- **Local Speech Processing:** Fast speech-to-text inference powered by `faster-whisper` running locally with `int8` quantization.
- **Neural Voice Playback:** Native-sounding text-to-speech using Microsoft Edge Neural Voices (`en-IN-PrabhatNeural`).
- **Zero-Trust Security Supervisor:** Enforces UI confirmation prompts before executing critical actions (system shutdown, restart, sending emails, deleting files).
- **Browser Automation:** Dynamic web control using Playwright for YouTube search, playback, like, and subscribe workflows.
- **Windows Integration:** Direct Win32 API and shell calls to launch apps, open system folders, navigate directories, and locate files.
- **Fail-Safe Operation:** Software emergency stop triggerable via voice command or a one-click dashboard button.

---

## Installation & Setup

### 1. Prerequisites
- **Python:** 3.10 to 3.12 (Make sure *Add Python to PATH* is checked during installation).
- **FFmpeg:** Required for audio processing. Open PowerShell as Administrator and run:
  ```powershell
  winget install "Gyan.FFmpeg"
