import os
import json
import re
from typing import Callable
from google import genai
from engine.security_guard import SecurityGuard
from tools.system_tools import WindowsTools
from tools.browser_tools import BrowserAgent
from tools.email_tools import EmailAgent

SYSTEM_PROMPT = """
Aapka naam Virat hai - ek behad smart, dostana aur energetic Windows desktop AI voice assistant.
Aap insaan ki tarah natural baatcheet karte hain.

Rules:
1. User jis bhasha me bole (Hindi, Hinglish, ya English), aapko usi bhasha me naturally aawaz me bolne jaisa chhota reply (1-2 lines) dena hai.
2. Agar user ne koi computer task karne ko bola hai, toh action JSON me format karein:
{
  "action": "open_app" | "open_folder" | "search_youtube" | "search_file" | "power" | "email" | "chat",
  "target": "target string jaise notepad, chrome, downloads, song name, etc.",
  "reply": "User ko aawaz me bolne wala natural insaan jaisa reply"
}
3. Agar aam baatcheet ya sawal hai, toh "action": "chat" rakhein aur "reply" me badhiya jawab dein.
Hamesha valid JSON reply hi karein.
"""

class ViratBrain:
    def __init__(self, security: SecurityGuard):
        self.security = security
        self.browser = BrowserAgent()
        self.email_agent = EmailAgent()
        api_key = os.getenv("GEMINI_API_KEY", "")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def process_command(self, raw_text: str, ui_confirm: Callable[[str], bool]) -> str:
        q = raw_text.strip()
        lower_q = q.lower()

        # Emergency Stop
        if any(w in lower_q for w in ["emergency stop", "halt all", "stop virat", "ruk jao", "sab band karo"]):
            self.security.trip_emergency_stop()
            return "Emergency stop activate kar diya hai. Saare kaam rok diye gaye hain."

        # Safety Fallback
        if not self.client:
            if "notepad" in lower_q:
                WindowsTools.launch_application("notepad")
                return "Notepad open kar diya hai."
            if "downloads" in lower_q:
                WindowsTools.open_known_path("downloads")
                return "Downloads folder khol diya hai."
            return f"Maine suna: '{raw_text}'. Kripya .env me Gemini API key check karein."

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"User command: {q}",
                config=dict(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text)
            action = data.get("action", "chat")
            target = data.get("target", "")
            reply = data.get("reply", "Ji, command execute kar raha hoon.")

            if action == "open_app":
                WindowsTools.launch_application(target)
            elif action == "open_folder":
                WindowsTools.open_known_path(target)
            elif action == "search_youtube":
                self.browser.search_youtube(target)
            elif action == "search_file":
                hits = WindowsTools.deep_file_search(target)
                if hits:
                    return f"{reply} File yahan mili: {hits[0]}"
                return f"Mujhe '{target}' naam ki koi file nahi mili."
            elif action == "power":
                if self.security.authorize("system_shutdown", {}, ui_confirm):
                    WindowsTools.execute_power_routine("shutdown")
            elif action == "email":
                draft = self.email_agent.compose_staged_draft(
                    recipient="contact@example.com",
                    subject="Quick Message",
                    body=target or "Drafted by Virat"
                )
                if self.security.authorize("send_email", draft, ui_confirm):
                    self.email_agent.dispatch(draft)

            return reply

        except Exception as e:
            print(f"[Brain Gemini Error]: {e}")
            return "Mujhe samajhne me thodi dikkat aayi, kripya dobara bolein."
