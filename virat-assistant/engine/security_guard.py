import os
import json
from datetime import datetime, timezone
from enum import IntEnum
from typing import Callable, Dict, Any


class ActionTier(IntEnum):
    READ_ONLY = 0
    LOW_IMPACT = 1
    HIGH_IMPACT = 2
    CRITICAL = 3


class SecurityGuard:
    def __init__(self, audit_file: str = "audit_log.jsonl"):
        self.audit_file = audit_file
        self.emergency_stop_active = False
        self.trusted_mode = os.getenv("TRUSTED_AUTOMATION_MODE", "false").lower() == "true"

        self.risk_table = {
            "system_shutdown": ActionTier.CRITICAL,
            "system_restart": ActionTier.CRITICAL,
            "delete_file": ActionTier.HIGH_IMPACT,
            "send_email": ActionTier.HIGH_IMPACT,
            "browser_interaction": ActionTier.LOW_IMPACT,
            "open_app": ActionTier.LOW_IMPACT,
            "open_folder": ActionTier.LOW_IMPACT,
            "deep_search": ActionTier.READ_ONLY
        }

    def trip_emergency_stop(self):
        self.emergency_stop_active = True
        self._record("EMERGENCY_STOP", {"status": "ACTIVE"})

    def reset_emergency_stop(self):
        self.emergency_stop_active = False
        self._record("EMERGENCY_STOP_CLEARED", {"status": "INACTIVE"})

    def _record(self, event_name: str, payload: Dict[str, Any]):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_name,
            "details": payload
        }
        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def authorize(self, action_name: str, payload: Dict[str, Any], ui_prompt: Callable[[str], bool]) -> bool:
        if self.emergency_stop_active:
            self._record("ACTION_BLOCKED_EMERGENCY", {"action": action_name})
            return False

        tier = self.risk_table.get(action_name, ActionTier.HIGH_IMPACT)
        self._record("EVALUATE_ACTION", {"action": action_name, "tier": tier.name, "payload": payload})

        if tier >= ActionTier.HIGH_IMPACT and not self.trusted_mode:
            dialog_text = self._build_prompt(action_name, payload)
            decision = ui_prompt(dialog_text)
            self._record("HITL_DECISION", {"action": action_name, "approved": decision})
            return decision

        return True

    def _build_prompt(self, action: str, p: Dict[str, Any]) -> str:
        if action == "system_shutdown":
            return "Virat is requesting authorization to shut down your computer. Proceed?"
        elif action == "system_restart":
            return "Virat is requesting authorization to restart your computer. Proceed?"
        elif action == "send_email":
            return (
                f"Review Outgoing Email:\n\n"
                f"Recipient: {p.get('recipient')}\n"
                f"Subject: {p.get('subject')}\n"
                f"Body:\n{p.get('body')}\n\n"
                f"Confirm sending?"
            )
        elif action == "delete_file":
            return f"Authorize permanent deletion of file: {p.get('target')}?"
        return f"Authorize high-privilege execution of: {action}?"