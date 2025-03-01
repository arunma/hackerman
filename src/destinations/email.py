import os
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .base import Destination

class EmailDestination(Destination):
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str,
                 from_email: str, to_email: str, subject_template: str = None):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_email = to_email
        self.subject_template = subject_template or "Hackerman Update: {title}"

    def send(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Send content via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            
            # Create subject from template and metadata
            subject = self.subject_template.format(**(metadata or {}))
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'html' if '<html>' in content else 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
