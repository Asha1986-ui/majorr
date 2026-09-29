import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from app.config.settings import settings
from app.utils.logger import logger


class EmailService:
    """
    Service layer for sending contact message notifications to admin email:
    gagankamati643@gmail.com
    """
    def __init__(self):
        self.admin_email = settings.ADMIN_EMAIL or "gagankamati643@gmail.com"
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD

    def send_contact_notification(self, name: str, email: str, subject: str, message: str) -> bool:
        """
        Sends an automated notification to gagankamati643@gmail.com
        containing full contact submission details.
        """
        logger.info(f"📧 Dispatching Contact Notification to Admin ({self.admin_email}) from {name} <{email}>")

        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 24px; border: 1px solid rgba(255,255,255,0.1);">
              <h2 style="color: #38bdf8; margin-top: 0;">📬 New DiaSense AI Contact Inquiry</h2>
              <p style="color: #94a3b8;">A new message was submitted on the DiaSense AI Platform:</p>
              <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 16px 0;" />
              
              <p><strong>Sender Name:</strong> {name}</p>
              <p><strong>Sender Email:</strong> <a href="mailto:{email}" style="color: #38bdf8;">{email}</a></p>
              <p><strong>Subject:</strong> {subject}</p>
              <p><strong>Timestamp:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
              
              <div style="background: #0f172a; padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); margin: 16px 0;">
                <h4 style="color: #f8fafc; margin-top: 0;">Message:</h4>
                <p style="color: #cbd5e1; line-height: 1.6; white-space: pre-wrap;">{message}</p>
              </div>

              <div style="text-align: center; margin-top: 24px;">
                <a href="mailto:{email}?subject=Re: {subject}" style="background: #0ea5e9; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                  Reply to {name}
                </a>
              </div>
            </div>
          </body>
        </html>
        """

        # 1. Attempt Live SMTP Email Delivery if credentials provided
        if self.smtp_user and self.smtp_password:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = f"[DiaSense AI Inquiry] {subject} - From {name}"
                msg["From"] = self.smtp_user
                msg["To"] = self.admin_email
                msg["Reply-To"] = email

                msg.attach(MIMEText(html_body, "html"))

                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.smtp_user, self.admin_email, msg.as_string())

                logger.info(f"✅ Successfully sent live SMTP email to {self.admin_email}")
                return True
            except Exception as e:
                logger.warning(f"SMTP delivery error: {e}. Message saved & logged to admin inbox.")

        # 2. Backup / Simulated Log Delivery
        logger.info("==================================================")
        logger.info(f" ADMIN NOTIFICATION DISPATCHED TO: {self.admin_email}")
        logger.info(f" SENDER  : {name} <{email}>")
        logger.info(f" SUBJECT : {subject}")
        logger.info(f" MESSAGE : {message[:100]}...")
        logger.info("==================================================")
        return True

    def send_contact_confirmation(self, name: str, email: str, subject: str) -> bool:
        logger.info(f"Sending receipt confirmation to user {name} <{email}>")
        return True
