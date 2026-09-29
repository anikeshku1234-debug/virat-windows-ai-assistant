import os
import re
import json
from typing import Callable
from google import genai
from engine.security_guard import SecurityGuard
from tools.system_tools import WindowsTools
from tools.browser_tools import BrowserAgent
from tools.email_tools import EmailAgent


SYSTEM_PROMPT = """
Aapka naam Virat hai - ek behad smart, dostana aur helpful Windows desktop AI assistant.
Aap insaan ki tarah natural baatcheet karte hain.

Guidelines:
1. User jis bhasha me bole (Hindi, Hinglish, ya English), aapko usi bhasha me naturally jawab dena hai.
2. Agar user ne koi computer task diya hai (jaise koi app kholna, folder kholna, YouTube pe kuch chalana, file dhoondhna, shutdown ya email), toh aapko JSON format me response dena hoga:
{
  "action": "open_app" | "open_folder" | "search_youtube" | "search_file" | "power" | "email" | "chat",
  "target": "target string (e.g. notepad, chrome, downloads, song name)",
  "reply": "Aapki boli hui aawaz me insaan jaisa chhota reply (1-2 sentences)"
}
3. Agar normal baatcheet hai, toh "action": "chat" rakhein aur "reply" me badhiya jawab dein.
Hamesha valid JSON format me hi jawab dein.
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
            return "Emergency stop activate kar diya gaya hai. Saare actions freeze hain."

        if not self.client:
            # Fallback if API key is not yet set
            return self._fallback_rule_engine(lower_q, ui_confirm)

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
            reply = data.get("reply", "Ji, samajh gaya.")

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
                    subject="Update",
                    body=target or "Automated mail by Virat"
                )
                if self.security.authorize("send_email", draft, ui_confirm):
                    self.email_agent.dispatch(draft)

            return reply

        except Exception as e:
            print(f"[Brain Gemini Error]: {e}")
            return self._fallback_rule_engine(lower_q, ui_confirm)

    def _fallback_rule_engine(self, q: str, ui_confirm: Callable[[str], bool]) -> str:
        if "notepad" in q:
            WindowsTools.launch_application("notepad")
            return "Notepad open kar diya hai."
        if "downloads" in q:
            WindowsTools.open_known_path("downloads")
            return "Downloads folder khol diya hai."
        if "youtube" in q or "chalao" in q or "play" in q:
            m = re.search(r"(?:play|search|chalao)\s+(.+)", q)
            target = m.group(1).replace("on youtube", "") if m else "music"
            self.browser.search_youtube(target)
            return f"YouTube par {target} chala raha hoon."
        return "Maine aapki baat suni, par Gemini API key .env me add karenge toh main insaan ki tarah sab baatein samajh kar execute karunga."
