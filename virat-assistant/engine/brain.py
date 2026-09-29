import os
import re
from typing import Callable, Tuple
from tools.system_tools import WindowsTools
from tools.browser_tools import BrowserAgent
from tools.email_tools import EmailAgent
from engine.security_guard import SecurityGuard

class ViratBrain:
    def __init__(self, guard: SecurityGuard):
        self.guard = guard
        self.browser = BrowserAgent()
        self.email_system = EmailAgent()

    def handle(self, raw_input: str, ui_confirm: Callable[[str], bool]) -> str:
        cmd = raw_input.strip().lower()

        # 1. Emergency Overrides
        if any(w in cmd for w in ["emergency stop", "abort all", "halt execution", "freeze"]):
            self.guard.trip_emergency_stop()
            return "Emergency stop activated. All system actions are suspended."

        if "resume operations" in cmd or "reset emergency stop" in cmd:
            self.guard.reset_emergency_stop()
            return "Safety override lifted. Virat is fully operational."

        # 2. Power Systems (Critical Tier)
        if any(p in cmd for p in ["shut down", "turn off my pc", "shutdown"]):
            if self.guard.authorize("system_shutdown", {}, ui_confirm):
                return WindowsTools.execute_power_routine("shutdown")
            return "Shutdown sequence denied by user."

        if "restart" in cmd:
            if self.guard.authorize("system_restart", {}, ui_confirm):
                return WindowsTools.execute_power_routine("restart")
            return "Restart sequence denied by user."

        # 3. Web & Media Automation
        if "youtube" in cmd and "search" in cmd:
            query = re.sub(r".*search\s+", "", cmd).replace("on youtube", "").strip()
            return self.browser.search_youtube(query)

        if cmd in ["like this video", "like the video", "thumbs up"]:
            if self.guard.authorize("browser_mutate", {"action": "like"}, ui_confirm):
                return self.browser.interact("like")
            return "Action blocked by safety policy."

        if cmd in ["subscribe to channel", "subscribe"]:
            if self.guard.authorize("browser_mutate", {"action": "subscribe"}, ui_confirm):
                return self.browser.interact("subscribe")
            return "Action blocked by safety policy."

        # 4. Email Pipeline (Staged High-Impact)
        if "write an email" in cmd or "send an email" in cmd:
            # Staged template - parse real params from transcript
            draft = {
                "recipient": "recipient@example.com",
                "subject": "Status Update",
                "body": "Hello, I will attend the scheduled meeting as requested."
            }
            if self.guard.authorize("send_email", draft, ui_confirm):
                success, note = self.email_system.dispatch_staged(draft)
                return note
            return "Email dispatch rejected by user."

        # 5. Native Filesystem Operations
        for folder in ["downloads", "documents", "desktop", "music", "videos"]:
            if folder in cmd and ("open" in cmd or "show" in cmd):
                _, msg = WindowsTools.open_known_path(folder)
                return msg

        if any(token in cmd for token in ["find my", "locate", "where is"]):
            target_term = re.sub(r".*(?:find my|locate|where is)\s+", "", cmd).strip()
            hits = WindowsTools.deep_file_search(target_term)
            if hits:
                return f"Located {len(hits)} match: {hits[0]}"
            return f"Could not find any file named '{target_term}' within your user directory."

        # 6. Default App Launch
        if cmd.startswith("open "):
            target_app = cmd.replace("open ", "").strip()
            _, status = WindowsTools.launch(target_app)
            return status

        return f"Understood: '{raw_input}'. No automation handler was mapped to this input."