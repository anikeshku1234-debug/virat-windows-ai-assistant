import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Tuple


class EmailAgent:
    def __init__(self):
        self.server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.sender = os.getenv("SENDER_EMAIL", "")
        self.password = os.getenv("SENDER_APP_PASSWORD", "")

    def compose_staged_draft(self, recipient: str, subject: str, body: str) -> Dict[str, str]:
        """Creates an in-memory draft ready for user validation."""
        return {
            "recipient": recipient,
            "subject": subject,
            "body": body
        }

    def dispatch(self, draft: Dict[str, str]) -> Tuple[bool, str]:
        """Dispatches email through secure TLS connection."""
        if not self.sender or not self.password:
            return False, "SMTP configuration missing in .env file."

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = draft["recipient"]
            msg['Subject'] = draft["subject"]
            msg.attach(MIMEText(draft["body"], 'plain'))

            with smtplib.SMTP(self.server, self.port) as session:
                session.starttls()
                session.login(self.sender, self.password)
                session.send_message(msg)

            return True, f"Email successfully delivered to {draft['recipient']}."
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"